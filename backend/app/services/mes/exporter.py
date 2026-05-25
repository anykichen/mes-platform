"""
MES 报表导出服务
路径: Login → Production KPI → Daily Summary → MFG Daily → 导出 Excel

重构后的流程:
  ① setup_mfg_daily_page()  — 导航到页面 + 设置厂区/日期/时间（只执行一次）
  ② query_and_export_project() — 设置专案 → 查询 → 导出 Excel（每个专案执行一次）
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


# ─── 班次时间映射 ───────────────────────────────────────────
SHIFT_MAP = {
    "summary": {"start": "00:00", "end": "23:59"},
    "day":     {"start": settings.MES_DAY_SHIFT_START,   "end": settings.MES_DAY_SHIFT_END},
    "night":   {"start": settings.MES_NIGHT_SHIFT_START, "end": settings.MES_NIGHT_SHIFT_END},
}


async def setup_mfg_daily_page(
    page: Page,
    report_date: date,
    shift: str = "summary",
) -> None:
    """
    ① 初始化 MFG Daily 报表页面（只执行一次）
    - 导航到 MFG Daily 页面
    - 设置厂区、日期、时间范围
    - 后续只需改专案名称即可重复查询导出
    """
    time_range = SHIFT_MAP.get(shift, SHIFT_MAP["summary"])
    date_str = report_date.strftime("%Y/%m/%d")

    mfg_daily_url = f"{settings.MES_BASE_URL}/func/tmirpt/mfgdaily.aspx?recounttype=t&fk=0123911"

    logger.info(f"正在初始化 MFG Daily 页面: {report_date} {shift}")

    # 1. 导航到 MFG Daily 报表页面
    await page.goto(mfg_daily_url, wait_until="networkidle", timeout=120000)

    # 等待 ExtJS/EasyUI 组件初始化
    await page.wait_for_timeout(3000)
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(2000)

    # 2. 设置厂区
    await page.evaluate(f'''
        $("#dllFactory").combogrid("setValue", "{settings.MES_FACTORY}");
    ''')
    logger.info(f"厂区已设置: {settings.MES_FACTORY}")

    # 3. 设置日期
    await page.evaluate(f'''
        $("#dllDate").datebox("setValue", "{date_str}");
    ''')
    logger.info(f"日期已设置: {date_str}")

    # 4. 设置时间范围（班次）
    await page.evaluate(f'''
        $("#dllTimeStart").timespinner("setValue", "{time_range['start']}");
        $("#dllTimeEnd").timespinner("setValue", "{time_range['end']}");
    ''')
    logger.info(f"时间范围已设置: {time_range['start']} ~ {time_range['end']}")

    logger.info("MFG Daily 页面初始化完成，准备逐专案采集")


async def _set_project_name(page: Page, project: str) -> bool:
    """在已初始化的页面中设置专案名称"""
    result = await page.evaluate(f'''
        (function() {{
            var projectValue = "{project}";
            var success = false;
            var finalValue = "";
            var foundField = "";

            if (typeof $ !== 'undefined') {{
                var searchbox = $("#searchboxprodSerial");
                if (searchbox.length > 0) {{
                    var input = searchbox.find("input").first();
                    if (input.length > 0) {{
                        input.val(projectValue);
                        input.trigger("change");
                        input.trigger("input");
                        input.trigger("keyup");
                        success = true;
                        finalValue = input.val();
                        foundField = "jquery-searchbox";
                    }}
                }}
            }}

            if (!success) {{
                var selectors = ["#searchboxprodSerial", "#prodSerial", "#txtprodSerial",
                                 "input[name='prodSerial']", "input[id*='prodSerial']"];
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
    return result.get("success", False)


async def _click_query_and_wait(page: Page) -> None:
    """点击查询按钮并等待数据加载"""
    await page.evaluate('''
        document.getElementById("ctl00_btnQuery").click();
    ''')
    await page.wait_for_timeout(8000)


async def _check_has_data(page: Page) -> bool:
    """检查查询结果中是否有数据"""
    return await page.evaluate('''
        (function() {
            var bodyText = document.body.innerText || "";
            if (bodyText.includes("没有查询到") || bodyText.includes("无数据") ||
                bodyText.includes("No data found")) {
                return false;
            }

            var table = document.querySelector("table.datagrid-btable, table[class*='datagrid']");
            if (table) {
                var rows = table.querySelectorAll("tr");
                if (rows.length <= 1) {
                    console.log("表格行数少于等于1，可能无数据");
                }
            }

            var redElements = document.querySelectorAll(
                "[style*='color:red'], [style*='color:#ff'], .red, [style*='background-color:red']");
            for (var i = 0; i < redElements.length; i++) {
                var el = redElements[i];
                var color = window.getComputedStyle(el).color;
                var bgColor = window.getComputedStyle(el).backgroundColor;
                if ((color && color.includes("rgb(255") || bgColor && bgColor.includes("rgb(255"))) {
                    var text = el.textContent || "";
                    if (text.includes("没有查询到") || text.includes("No data") ||
                        text.includes("无数据")) {
                        return false;
                    }
                }
            }

            return true;
        })()
    ''')


async def _wait_and_export(page: Page, project: str, report_date: date, shift: str) -> str:
    """等待导出按钮可用 → 触发导出 → 保存文件"""
    try:
        await page.wait_for_selector('#ctl00_btnExport:not([disabled])', timeout=30000)
        await page.wait_for_timeout(1000)
    except Exception:
        logger.warning("导出按钮等待超时，直接使用JavaScript调用")

    async with page.expect_download(timeout=60000) as download_info:
        await page.evaluate('document.getElementById("ctl00_btnExport").click()')
    download: Download = await download_info.value

    filename = f"{project}_{report_date.strftime('%Y%m%d')}_{shift}.xlsx"
    save_path = os.path.join(settings.DOWNLOAD_DIR, filename)
    await download.save_as(save_path)

    if os.path.exists(save_path):
        file_size = os.path.getsize(save_path)
        logger.info(f"Excel 已下载: {save_path} (大小: {file_size} bytes)")
        if file_size < 1000:
            logger.warning(f"Excel文件过小 ({file_size} bytes)，可能没有数据")
            os.remove(save_path)
            raise NoDataFoundError(f"Excel file too small, likely no data for project {project}")
    else:
        raise ValueError(f"Failed to save Excel file for project {project}")

    return save_path


async def query_and_export_project(
    page: Page,
    project: str,
    report_date: date,
    shift: str = "summary",
) -> str:
    """
    ② 在已初始化的页面上，切专案 → 查询 → 导出
    前提: 已经调用过 setup_mfg_daily_page() 设置了厂区/日期/时间
    返回: Excel 文件本地路径
    抛出: NoDataFoundError（该专案无数据）
    """
    logger.info(f"正在采集专案: [{project}]")

    # 1. 设置专案名称
    success = await _set_project_name(page, project)
    logger.info(f"专案设置结果: {'成功' if success else '失败'}")

    # 2. 点击查询
    await _click_query_and_wait(page)

    # 3. 检查数据
    has_data = await _check_has_data(page)
    if not has_data:
        logger.warning(f"专案 [{project}] 在 {report_date} {shift} 时间段没有生产数据，跳过")
        raise NoDataFoundError(f"No data found for project {project}")

    # 4. 导出 Excel
    return await _wait_and_export(page, project, report_date, shift)


# ─── 向后兼容：保留旧版单次导出接口 ───────────────────────────
async def export_daily_report(
    project: str,
    report_date: date,
    shift: str = "summary",
    page: Page = None,
) -> str:
    """
    [兼容旧接口] 单次完整导出（导航+设置+查询+下载）
    新代码请使用: setup_mfg_daily_page() + query_and_export_project()
    """
    if page is None:
        page = await get_active_page()

    try:
        await setup_mfg_daily_page(page, report_date, shift)
        return await query_and_export_project(page, project, report_date, shift)
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
