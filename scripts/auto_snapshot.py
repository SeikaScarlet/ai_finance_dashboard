#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键自动报数：抓汇率 + 抓股价 + 生成 snapshot 模板。
Fetch exchange rates and stock prices, generate snapshot template.

用法 / Usage:
    python3 scripts/auto_snapshot.py
    python3 scripts/auto_snapshot.py --dry-run  # 只打印，不写文件

依赖 / Dependencies:
    纯 Python 标准库，无需额外安装
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

# 项目目录
SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR.parent
DATA = BASE / "data"


def fetch_exchange_rates() -> dict:
    """
    Fetch USD/HKD exchange rates from open.er-api.com.
    抓取 USD/HKD 汇率（open.er-api.com）
    
    Returns
    -------
    dict
        {"USD": float, "HKD": float, "_source": str}
    """
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        rates = data["rates"]
        usd_rmb = round(rates["CNY"], 4)
        hkd_rmb = round(rates["CNY"] / rates["HKD"], 4)
        source = data.get("time_last_update_utc", "")
        return {"USD": usd_rmb, "HKD": hkd_rmb, "_source": source}
    except urllib.error.URLError as e:
        print(f"⚠️  汇率 API 失败: {e}", file=sys.stderr)
        print("   使用备用汇率 USD=7.0, HKD=0.9", file=sys.stderr)
        return {"USD": 7.0, "HKD": 0.9, "_source": "offline-fallback"}


def fetch_stock_price_yahoo(symbol: str) -> dict | None:
    """
    Fetch stock price from Yahoo Finance (unofficial API).
    抓取股价（Yahoo Finance 非官方 API）
    
    Parameters
    ----------
    symbol : str
        Stock symbol, e.g. "VOO", "0700.HK"
    
    Returns
    -------
    dict | None
        {"symbol": str, "price": float, "currency": str} or None if failed
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        result = data["chart"]["result"][0]
        meta = result["meta"]
        return {
            "symbol": symbol,
            "price": round(meta["regularMarketPrice"], 2),
            "currency": meta["currency"]
        }
    except (urllib.error.URLError, KeyError, IndexError) as e:
        print(f"⚠️  {symbol} 股价抓取失败: {e}", file=sys.stderr)
        return None


def fetch_stock_price_sina(code: str) -> dict | None:
    """
    Fetch A-share or HK stock price from Sina Finance.
    抓取 A股/港股股价（新浪财经）
    
    Parameters
    ----------
    code : str
        Sina stock code, e.g. "sh600000" (A-share), "hk00700" (HK)
    
    Returns
    -------
    dict | None
        {"code": str, "name": str, "price": float} or None if failed
    """
    url = f"http://hq.sinajs.cn/list={code}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            text = resp.read().decode("gbk")
        import re
        match = re.search(r'"([^"]+)"', text)
        if not match:
            return None
        fields = match.group(1).split(",")
        return {
            "code": code,
            "name": fields[0],
            "price": round(float(fields[3]), 2)
        }
    except (urllib.error.URLError, ValueError, IndexError) as e:
        print(f"⚠️  {code} 股价抓取失败: {e}", file=sys.stderr)
        return None


def load_last_snapshot() -> dict | None:
    """
    Load the last snapshot from history.json.
    读取最后一次快照（history.json）
    
    Returns
    -------
    dict | None
        Last snapshot or None if not found
    """
    history_file = DATA / "history.json"
    if not history_file.exists():
        return None
    with open(history_file, encoding="utf-8") as f:
        data = json.load(f)
    snaps = data.get("snapshots", [])
    if not snaps:
        return None
    snaps.sort(key=lambda s: s["date"])
    return snaps[-1]


def build_snapshot(rates: dict, stock_prices: dict, last_snap: dict | None) -> dict:
    """
    Build a new snapshot with fetched data and last snapshot as fallback.
    构建新快照（在线数据 + 上次快照作为后备）
    
    Parameters
    ----------
    rates : dict
        Exchange rates from fetch_exchange_rates()
    stock_prices : dict
        Dict of {key: price_dict} from fetch_stock_price_*()
    last_snap : dict | None
        Last snapshot from load_last_snapshot()
    
    Returns
    -------
    dict
        New snapshot ready to append to history.json
    """
    last_prices = (last_snap or {}).get("prices", {})
    last_holdings = (last_snap or {}).get("holdings", {})
    
    snap = {
        "date": str(date.today()),
        "rates": {"USD": rates["USD"], "HKD": rates["HKD"]},
        "ratesSource": f"open.er-api.com ({rates['_source']})",
        "comment": "TODO 写一句备注",
        "cashFlow": {
            "deposits": 0,
            "withdrawals": 0,
            "note": ""
        },
        "prices": {},
        "holdings": {}
    }
    
    # 合并股价：优先用在线抓取，没抓到用上次
    for key, price_info in stock_prices.items():
        if price_info:
            snap["prices"][key] = {
                "ccy": price_info.get("currency", "USD"),
                "price": price_info["price"]
            }
    
    # 上次价格作为后备
    for key, p in last_prices.items():
        if key not in snap["prices"]:
            snap["prices"][key] = p
    
    # holdings 完全沿用上次（需要手动更新）
    snap["holdings"] = last_holdings
    
    return snap


def main():
    dry_run = "--dry-run" in sys.argv
    
    print("🚀 开始自动报数...\n")
    
    # 1. 抓汇率
    print("📡 正在抓取汇率...")
    rates = fetch_exchange_rates()
    print(f"   USD → RMB : {rates['USD']}")
    print(f"   HKD → RMB : {rates['HKD']}")
    print(f"   源 : {rates['_source']}\n")
    
    # 2. 抓股价（示例：美股 ETF）
    print("📈 正在抓取股价...")
    stock_prices = {}
    
    symbols = [
        ("voo", "VOO"),           # 标普 500
        ("qqqm", "QQQM"),         # 纳指
        ("brk_b", "BRK-B"),       # 伯克希尔
        ("iau_gold", "IAU"),      # 黄金
        ("tencent_futu", "0700.HK"),  # 腾讯（港股）
    ]
    
    for key, symbol in symbols:
        price = fetch_stock_price_yahoo(symbol)
        if price:
            stock_prices[key] = price
            print(f"   ✅ {symbol:12s} = {price['price']:8.2f} {price['currency']}")
        else:
            print(f"   ❌ {symbol:12s} 抓取失败，将沿用上次价格")
    
    # 腾讯港股通账户共享价格
    if "tencent_futu" in stock_prices:
        stock_prices["tencent_zhongyin"] = stock_prices["tencent_futu"]
        stock_prices["tencent_zhaoshang"] = stock_prices["tencent_futu"]
    
    print()
    
    # 3. 加载上次快照
    last_snap = load_last_snapshot()
    if last_snap:
        print(f"📂 上次快照日期: {last_snap['date']}\n")
    else:
        print("📂 未找到上次快照，这是首次报数\n")
    
    # 4. 构建新快照
    snap = build_snapshot(rates, stock_prices, last_snap)
    
    # 5. 输出
    print("========== 复制以下 JSON，append 到 history.json 的 snapshots 数组末尾 ==========\n")
    print(json.dumps(snap, ensure_ascii=False, indent=2))
    print("\n========== END ==========\n")
    
    if dry_run:
        print("🏁 --dry-run 模式：未写入文件")
    else:
        print("💡 提示：")
        print("   1. 检查 prices 是否都抓到了")
        print("   2. 手动更新 holdings（持仓变动）")
        print("   3. 填写 comment 备注")
        print("   4. 填写 cashFlow（净注入/赎回）")
        print("   5. append 到 data/history.json 后运行 `python3 -m http.server 8765` 验证")


if __name__ == "__main__":
    main()
