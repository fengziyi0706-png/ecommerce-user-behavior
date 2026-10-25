"""项目配置：路径和可调参数都集中在这里。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 原始数据：从阿里天池下载 UserBehavior.csv，解压后放到 data/raw/ 下
RAW_CSV = ROOT / "data" / "raw" / "UserBehavior.csv"

# 清洗后的数据（Parquet 列式存储，读取比 CSV 快很多）
CLEAN_PARQUET = ROOT / "data" / "processed" / "user_behavior_clean.parquet"
USER_FEATURES_PARQUET = ROOT / "data" / "processed" / "user_features.parquet"

RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
SUMMARY_JSON = RESULTS_DIR / "summary.json"

# 按用户抽样的比例。1.0 = 全量（约一亿条、约一百万用户）。
# 如果电脑内存小于 8GB 或运行太慢，改成 0.1（约一千万条、约十万用户）。
SAMPLE_FRACTION = 1.0

# 数据集的有效时间范围（北京时间）
START_DATE = "2017-11-25"
END_DATE = "2017-12-03"          # 含当天
REFERENCE_DATE = "2017-12-04"    # 计算"距今天数"的参照日

# DuckDB 可使用的最大内存，超过会自动写临时文件到硬盘
DUCKDB_MEMORY_LIMIT = "4GB"

RANDOM_STATE = 42
