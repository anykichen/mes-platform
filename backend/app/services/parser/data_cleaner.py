"""
数据清洗
- 去除空行、小计行、合计行
- 数值类型转换
- 良率格式标准化（% → 小数）
"""
import pandas as pd
import numpy as np

# 需要过滤的行关键字
SKIP_KEYWORDS = ["合计", "总计", "小计", "Total", "Sum", "Grand Total"]


def clean_station_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    # 过滤空行
    df = df.dropna(subset=["station_name"])
    df = df[df["station_name"].astype(str).str.strip() != ""]

    # 过滤合计行
    df = df[~df["station_name"].astype(str).str.contains(
        "|".join(SKIP_KEYWORDS), case=False, na=False
    )]

    # 数值列清洗
    int_cols = ["input_qty", "output_qty", "ng_qty"]
    float_cols = ["yield_rate", "material_yield", "process_yield"]

    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace("%", "").str.strip(),
                errors="coerce"
            ).fillna(0)
            # 如果是百分比形式（> 1），转为小数
            mask = df[col] > 1
            df.loc[mask, col] = df.loc[mask, col] / 100

    # 工站名称标准化
    df["station_name"] = df["station_name"].astype(str).str.strip()

    return df.reset_index(drop=True)
