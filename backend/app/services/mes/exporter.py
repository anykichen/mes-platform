"""
MES 报表导出服务
路径: Login → Production KPI → Daily Summary → MFG Daily → 导出 Excel
"""
import os
import asyncio
from datetime import date
from playwright.async_api import Page, Download
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.mes.session_manager import get_active_page

logger = setup_logging()


class NoDataFoundError(Exception):
    """专案无生产数据异常（正常情况，非系统错误）"""
    pass


async def export_daily_report(
    project: str,
    report_date: date,
    shift: str = "summary",  # summary / day / night
    page: Page = None,
) -> str:
    """
    导出指定专案、日期、班次的 Excel 报表
    返回本地文件路径
    若 page 参数提供则使用指定页面（用于并发采集）
    """
    if page is None:
        page = await get_active_page()

    shift_map = {
        "summary": {"start": "00:00", "end": "23:59"},
        "day":     {"start": settings.MES_DAY_SHIFT_START,   "end": settings.MES_DAY_SHIFT_END},
        "night":   {"start": settings.MES_NIGHT_SHIFT_START, "end": settings.MES_NIGHT_SHIFT_END},
    }
    time_range = shift_map.get(shift, shift_map["summary"])

    try:
        # 1. 导航到 MFG Daily 报表页面（每次都刷新，确保状态干净）
        logger.info(f"正在导出 [{project}] {report_date} {shift} 报表")
        mfg_daily_url = f"{settings.MES_BASE_URL}/func/tmirpt/mfgdaily.aspx?recounttype=t&fk=0123911"

        # 使用 force=True 确保强制刷新页面，清除旧的JavaScript状态
        await page.goto(mfg_daily_url, wait_until="networkidle", timeout=120000)

        # 等待页面JavaScript渲染完成（ExtJS/EasyUI组件需要时间初始化）
        await page.wait_for_timeout(3000)

        # 再次等待确保页面完全加载
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)

        # 2. 设置查询条件 - 使用JavaScript操作EasyUI/ExtJS组件

        # 设置厂区 (EasyUI combogrid)
        await page.evaluate(f'''
            $("#dllFactory").combogrid("setValue", "{settings.MES_FACTORY}");
        ''')

        # 设置专案 - EasyUI searchbox，ID为searchboxprodSerial
        project_set_result = await page.evaluate(f'''
            (function() {{
                var projectValue = "{project}";
                var success = false;
                var finalValue = "";
                var foundField = "";

                // 方法1: 优先使用原来的jQuery方式！这个是能正常工作的！
                if (typeof $ !== 'undefined') {{
                    console.log("优先使用jQuery方式");
                    var searchbox = $("#searchboxprodSerial");
                    if (searchbox.length > 0) {{
                        var input = searchbox.find("input").first();
                        if (input.length > 0) {{
                            input.val(projectValue);
                            input.trigger("change");
                            input.trigger("input");
                            input.trigger("keyup");
                            console.log("jQuery设置值: " + projectValue);
                            success = true;
                            finalValue = input.val();
                            foundField = "jquery-searchbox";
                        }}
                    }}
                }}

                // 如果jQuery失败，尝试原生方法
                if (!success) {{
                    console.log("jQuery方式失败，尝试原生方式");
                    var selectors = ["#searchboxprodSerial", "#prodSerial", "#txtprodSerial", "input[name='prodSerial']", "input[id*='prodSerial']"];
                    for (var s = 0; s < selectors.length; s++) {{
                        var field = document.querySelector(selectors[s]);
                        if (field) {{
                            field.value = projectValue;
                            field.dispatchEvent(new Event("input", {{ bubbles: true }}));
                            field.dispatchEvent(new Event("change", {{ bubbles: true }}));
                            field.dispatchEvent(new Event("blur", {{ bubbles: true }}));
                            success = true;
                            finalValue = field.value;
                            foundField = selectors[s];
                            console.log("原生设置成功: " + selectors[s]);
                            break;
                        }}
                    }}
                }}

                return {{
                    success: success,
                    value: finalValue,
                    field: foundField
                }};
            }})()
        ''')

        logger.info(f"专案设置结果: success={project_set_result.get('success')}, value='{project_set_result.get('value')}', field='{project_set_result.get('field')}'")

        # 设置日期
        date_str = report_date.strftime("%Y/%m/%d")
        await page.evaluate(f'''
            $("#dllDate").datebox("setValue", "{date_str}");
        ''')

        # 设置时间范围（班次）
        await page.evaluate(f'''
            $("#dllTimeStart").timespinner("setValue", "{time_range['start']}");
            $("#dllTimeEnd").timespinner("setValue", "{time_range['end']}");
        ''')

        # 3. 点击查询按钮
        await page.evaluate('''
            document.getElementById("ctl00_btnQuery").click();
        ''')

        # 等待数据加载完成（等待表格出现或错误提示）
        await page.wait_for_timeout(8000)

        # 检查是否有数据
        has_data = await page.evaluate('''
            (function() {
                // 检查常见的无数据提示
                var bodyText = document.body.innerText || "";
                if (bodyText.includes("没有查询到") || bodyText.includes("无数据") || bodyText.includes("No data found")) {
                    return false;
                }

                // 检查表格是否有数据行
                var table = document.querySelector("table.datagrid-btable, table[class*='datagrid']");
                if (table) {
                    var rows = table.querySelectorAll("tr");
                    if (rows.length <= 1) {
                        console.log("表格行数少于等于1，可能无数据");
                    }
                }

                // 检查是否有红色警告标签
                var redElements = document.querySelectorAll("[style*='color:red'], [style*='color:#ff'], .red, [style*='background-color:red']");
                for (var i = 0; i < redElements.length; i++) {
                    var el = redElements[i];
                    var color = window.getComputedStyle(el).color;
                    var bgColor = window.getComputedStyle(el).backgroundColor;
                    if ((color && color.includes("rgb(255") || bgColor && bgColor.includes("rgb(255"))) {
                        var text = el.textContent || "";
                        if (text.includes("没有查询到") || text.includes("No data") || text.includes("无数据")) {
                            console.log("发现红色警告标签提示无数据");
                            return false;
                        }
                    }
                }

                console.log("没有发现无数据提示，认为有数据");
                return true;
            })()
        ''')

        if not has_data:
            logger.warning(f"专案 [{project}] 在 {report_date} {shift} 时间段没有生产数据，跳过")
            raise NoDataFoundError(f"No data found for project {project}")

        # 4. 等待导出按钮变为可用（最多等待30秒）
        try:
            await page.wait_for_selector('#ctl00_btnExport:not([disabled])', timeout=30000)
            await page.wait_for_timeout(1000)
        except Exception:
            logger.warning("导出按钮等待超时，直接使用JavaScript调用")

        # 5. 导出 Excel（监听下载事件）
        async with page.expect_download(timeout=60000) as download_info:
            await page.evaluate('document.getElementById("ctl00_btnExport").click()')
        download: Download = await download_info.value

        # 保存到本地
        filename = f"{project}_{report_date.strftime('%Y%m%d')}_{shift}.xlsx"
        save_path = os.path.join(settings.DOWNLOAD_DIR, filename)
        await download.save_as(save_path)

        # 验证文件是否正确保存
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            logger.info(f"Excel 已下载: {save_path} (大小: {file_size} bytes)")

            if file_size < 1000:
                logger.warning(f"Excel文件过小 ({file_size} bytes)，可能没有数据")
                os.remove(save_path)
                raise NoDataFoundError(f"Excel file too small, likely no data for project {project}")
        else:
            logger.error(f"Excel文件未保存: {save_path}")
            raise ValueError(f"Failed to save Excel file for project {project}")

        return save_path

    except NoDataFoundError:
        raise
    except Exception as e:
        logger.error(f"导出失败 [{project}] {report_date} {shift}: {e}")
        raise


async def export_daily_report_with_retry(
    project: str,
    report_date: date,
    shift: str = "summary",
    page: Page = None,
    max_retries: int = 2,
    retry_delay: int = 10,
) -> str:
    """
    带重试的导出函数
    - NoDataFoundError: 不重试（无数据是正常情况）
    - 其他异常: 自动重试 max_retries 次
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await export_daily_report(project, report_date, shift, page=page)
        except NoDataFoundError:
            raise
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                logger.warning(
                    f"导出失败 [{project}]，第 {attempt+1}/{max_retries} 次重试，等待 {retry_delay}s: {e}"
                )
                await asyncio.sleep(retry_delay)
    raise last_error
