"""
生成一份和天池 UserBehavior.csv 格式完全相同的【模拟数据】，只用来测试代码能否跑通。

注意：模拟数据跑出来的结果不是真实结论，不能写进简历。
正式分析前请删除 data/raw/UserBehavior.csv，换成从天池下载的真实数据。

用法：
    python make_sample_data.py            # 默认 10,000 个用户
    python make_sample_data.py 30000      # 指定用户数
"""
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

import config

N_USERS = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
N_ITEMS = 80_000
N_CATEGORIES = 600
rng = np.random.default_rng(config.RANDOM_STATE)

BJ = timezone(timedelta(hours=8))
day0 = datetime(2017, 11, 25, tzinfo=BJ)
days = [day0 + timedelta(days=i) for i in range(9)]
weekend = np.array([d.weekday() >= 5 for d in days])

# 一天中各小时的活跃权重：凌晨低，晚上 20–22 点最高
hour_w = np.array([3, 2, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 7, 7, 8, 10, 11, 10, 6], float)
hour_w /= hour_w.sum()
hour_cdf = np.cumsum(hour_w)
hour_cdf[-1] = 1.0

item_cat = rng.integers(0, N_CATEGORIES, N_ITEMS)
item_pop = rng.zipf(1.6, N_ITEMS).astype(float)
item_pop /= item_pop.sum()
item_cdf = np.cumsum(item_pop)

rows = []
for u in range(1, N_USERS + 1):
    activity = rng.lognormal(mean=3.9, sigma=0.9)          # 用户活跃度
    intent = rng.beta(1.2, 12)                              # 用户购买意向
    p_active_day = np.clip(rng.beta(3, 2), 0.15, 1.0)
    active = rng.random(9) < p_active_day
    active[rng.integers(0, 9)] = True
    carted = []
    for d in np.where(active)[0]:
        n = max(1, int(rng.poisson(activity / 6 * (1.15 if weekend[d] else 1.0))))
        hours = np.searchsorted(hour_cdf, rng.random(n))
        secs = rng.integers(0, 3600, n)
        items = np.minimum(np.searchsorted(item_cdf, rng.random(n)), N_ITEMS - 1)
        r = rng.random(n)
        p_cart = 0.04 + 0.25 * intent
        p_fav = 0.03
        p_buy = 0.004 + 0.12 * intent + (0.04 if carted else 0)
        for k in range(n):
            ts = int((days[d] + timedelta(hours=int(hours[k]), seconds=int(secs[k]))).timestamp())
            it = int(items[k])
            if r[k] < p_buy:
                if carted and rng.random() < 0.6:
                    it = carted[rng.integers(0, len(carted))]
                beh = "buy"
            elif r[k] < p_buy + p_cart:
                beh = "cart"
                carted.append(it)
            elif r[k] < p_buy + p_cart + p_fav:
                beh = "fav"
            else:
                beh = "pv"
            if beh != "pv":   # 收藏、加购、购买之前通常先浏览
                rows.append((u, it, int(item_cat[it]), "pv", ts - int(rng.integers(5, 600))))
            rows.append((u, it, int(item_cat[it]), beh, ts))

# 人为加入少量脏数据，用来测试清洗步骤
n_dirty = 200
for i in range(n_dirty):
    u, it, c, b, ts = rows[rng.integers(0, len(rows))]
    rows.append((u, it, c, b, ts))                                    # 完全重复的记录
    rows.append((u, it, c, b, ts - 86400 * int(rng.integers(30, 400))))   # 超出时间范围的记录

rows.sort(key=lambda x: (x[0], x[4]))
config.RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
with open(config.RAW_CSV, "w") as f:
    for row in rows:
        f.write(",".join(map(str, row)) + "\n")

print(f"已生成模拟数据：{len(rows):,} 行，{N_USERS:,} 个用户 -> {config.RAW_CSV}")
print("提醒：这是模拟数据，只用于测试代码，结果不能写进简历。")
