"""
数据转换器
将解析好的 DataFrame 转换为 StationSummary ORM 对象列表
"""
import pandas as pd
from datetime import date
from app.models.station import StationSummary
from app.services.parser.sheet_detector import detect_sheets
from app.services.parser.excel_reader import read_sheet
from app.services.parser.data_cleaner import clean_station_df
from app.core.logging import setup_logging

logger = setup_logging()


async def excel_to_station_records(
    filepath: str,
    project: str,
    report_date: date,
) -> list[StationSummary]:
    """
    完整解析流程：检测 Sheet → 读取 → 清洗 → 转换为 ORM 对象
    """
    records = []

    # 1. 检测 Sheet
    sheets = detect_sheets(filepath)
    logger.info(f"Sheet 检测结果: {sheets}")

    for shift, sheet_name in sheets.items():
        if sheet_name is None:
            logger.debug(f"[{shift}] Sheet 未找到，跳过")
            continue

        # 2. 读取
        df = read_sheet(filepath, sheet_name)
        if df is None or df.empty:
            continue

        # 3. 清洗
        df = clean_station_df(df)
        if df.empty:
            continue

        # 4. 转换
        for _, row in df.iterrows():
            record = StationSummary(
                report_date=report_date,
                shift=shift,
                project=project,
                station_name=row["station_name"],
                input_qty=int(row.get("input_qty", 0)),
                output_qty=int(row.get("output_qty", 0)),
                ng_qty=int(row.get("ng_qty", 0)),
                yield_rate=float(row.get("yield_rate", 0)),
                material_yield=float(row.get("material_yield", 0)),
                process_yield=float(row.get("process_yield", 0)),
            )
            records.append(record)

        logger.info(f"[{project}] [{shift}] 解析完成，{len(records)} 条记录")

    return records
