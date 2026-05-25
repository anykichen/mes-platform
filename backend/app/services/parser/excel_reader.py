"""
Excel 数据读取器
将原始宽表（站点为列）读取为 DataFrame
支持 MES MFG Daily 导出的格式
"""
import pandas as pd
from typing import Optional
from app.core.logging import setup_logging

logger = setup_logging()

# 字段名映射（MES 导出列名 → 标准字段名）
COLUMN_MAP = {
    "工站": "station_name", "Station": "station_name", "站点": "station_name",
    "投入": "input_qty",    "Input": "input_qty",    "Input Qty": "input_qty",
    "产出": "output_qty",   "Output": "output_qty",  "Output Qty": "output_qty",
    "NG": "ng_qty",         "NG数": "ng_qty",         "不良数": "ng_qty",
    "良率": "yield_rate",   "Yield": "yield_rate",   "Yield Rate": "yield_rate",
    "物料良率": "material_yield", "Material Yield": "material_yield",
    "工程良率": "process_yield",  "Process Yield": "process_yield",
}


def read_sheet(filepath: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    读取指定 Sheet，返回标准化 DataFrame
    列: station_name, input_qty, output_qty, ng_qty, yield_rate, material_yield, process_yield
    """
    try:
        # MES MFG Daily 导出的格式:
        # - 第4行(索引3)是工站名称
        # - 第5行(索引4)是投入数量
        # - 第6行(索引5)是产出数量
        # - 第7行(索引6)是不良数量
        # - 第8行(索引7)是良率
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=None, engine="openpyxl")
        
        # 检查是否是 MES 导出格式（通过检查特定行的内容）
        if df.shape[0] >= 8 and df.shape[1] > 5:
            # 检查第4行是否包含工站关键字
            first_row = df.iloc[3].astype(str)
            if first_row.str.contains('CGM|VI|OQC|PACK|LAM', case=False, na=False).any():
                logger.info(f"检测到 MES MFG Daily 导出格式")
                
                # 提取工站名称（第4行，索引3）
                stations = df.iloc[3].tolist()
                
                # 提取各行数据
                input_qty = df.iloc[4].tolist() if df.shape[0] > 4 else []
                output_qty = df.iloc[5].tolist() if df.shape[0] > 5 else []
                ng_qty = df.iloc[6].tolist() if df.shape[0] > 6 else []
                yield_rate = df.iloc[7].tolist() if df.shape[0] > 7 else []
                
                # 构建 DataFrame
                data = []
                for i, station in enumerate(stations):
                    if station and str(station).strip() and i > 1:  # 跳过前两列和空列
                        data.append({
                            "station_name": str(station).strip(),
                            "input_qty": _parse_number(input_qty[i]) if i < len(input_qty) else None,
                            "output_qty": _parse_number(output_qty[i]) if i < len(output_qty) else None,
                            "ng_qty": _parse_number(ng_qty[i]) if i < len(ng_qty) else None,
                            "yield_rate": _parse_number(yield_rate[i]) if i < len(yield_rate) else None,
                        })
                
                result_df = pd.DataFrame(data)
                if len(result_df) > 0:
                    logger.info(f"从 [{sheet_name}] 解析到 {len(result_df)} 个工站")
                    return result_df
        
        # 标准格式处理
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0, engine="openpyxl")

        # 重命名列
        df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})

        # 必须有 station_name
        if "station_name" not in df.columns:
            logger.warning(f"Sheet [{sheet_name}] 未找到工站列，跳过")
            return None

        # 只保留有效列
        valid_cols = [c for c in [
            "station_name", "input_qty", "output_qty", "ng_qty",
            "yield_rate", "material_yield", "process_yield"
        ] if c in df.columns]
        df = df[valid_cols].copy()

        return df

    except Exception as e:
        logger.error(f"读取 Sheet [{sheet_name}] 失败: {e}")
        return None


def _parse_number(value) -> Optional[float]:
    """解析数值，支持字符串和数字类型"""
    if value is None or pd.isna(value):
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        value = str(value).strip()
        if not value:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None
