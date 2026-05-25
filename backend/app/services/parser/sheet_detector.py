"""
Sheet 识别器
自动判断 Excel 中哪个 Sheet 是汇总/白班/夜班
"""
import openpyxl
from typing import Optional

SHEET_PATTERNS = {
    "summary": ["汇总", "Summary", "All", "Total", "合计"],
    "day":     ["白班", "Day", "D班", "白", "08:00"],
    "night":   ["夜班", "Night", "N班", "夜", "20:00"],
}


def detect_sheets(filepath: str) -> dict[str, Optional[str]]:
    """
    返回: {"summary": "Sheet1", "day": "Sheet2", "night": "Sheet3"}
    未找到的类型值为 None
    """
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    sheet_names = wb.sheetnames
    wb.close()

    result = {"summary": None, "day": None, "night": None}

    for sheet_type, patterns in SHEET_PATTERNS.items():
        for name in sheet_names:
            if any(p.lower() in name.lower() for p in patterns):
                result[sheet_type] = name
                break

    # 如果只有一个 Sheet，视为汇总
    if len(sheet_names) == 1 and result["summary"] is None:
        result["summary"] = sheet_names[0]

    return result
