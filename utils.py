"""各个笔记本共用的小工具：数据库连接、画图设置、结果汇总。"""
import json
import warnings

import duckdb
import matplotlib.pyplot as plt

import config


def connect():
    """连接 DuckDB，并把清洗后的数据注册成一张名为 ub 的视图。"""
    con = duckdb.connect()
    con.execute(f"SET memory_limit = '{config.DUCKDB_MEMORY_LIMIT}'")
    if config.CLEAN_PARQUET.exists():
        con.execute(
            f"CREATE OR REPLACE VIEW ub AS SELECT * FROM read_parquet('{config.CLEAN_PARQUET.as_posix()}')"
        )
    return con


def setup_plot():
    """设置中文字体。按顺序尝试 Mac、Windows、Linux 上常见的中文字体。"""
    warnings.filterwarnings("ignore", message="Glyph .* missing from font")
    warnings.filterwarnings("ignore", message="findfont")
    plt.rcParams["font.sans-serif"] = [
        "PingFang SC", "Heiti TC", "Arial Unicode MS",      # Mac
        "Microsoft YaHei", "SimHei",                         # Windows
        "Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Micro Hei",   # Linux 和 Colab
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 110
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False


def save_fig(fig, name):
    """把图保存到 figures/ 目录，方便放进 GitHub 的 README 或面试材料。"""
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    return path


def update_summary(section, values):
    """把关键结论数字写进 results/summary.json，最后统一拿来写简历。"""
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    data = {}
    if config.SUMMARY_JSON.exists():
        data = json.loads(config.SUMMARY_JSON.read_text(encoding="utf-8"))
    data[section] = values
    config.SUMMARY_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=float), encoding="utf-8"
    )
    return data


def pct(x, digits=2):
    """小数转百分比字符串。"""
    return f"{x * 100:.{digits}f}%"
