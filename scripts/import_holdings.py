#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从券商 CSV 账单导入持仓数据。
Import holdings from broker CSV exports.

支持的格式 / Supported formats:
    - 富途牛牛导出（Futu）
    - 雪盈证券导出（Snowball）
    - 通用 CSV（Generic）

用法 / Usage:
    python3 scripts/import_holdings.py broker_export.csv --broker futu
    python3 scripts/import_holdings.py broker_export.csv --broker generic

CSV 格式要求 / CSV Format:
    通用格式必须包含以下列（Generic format requires these columns）:
    - symbol 或 code: 股票代码
    - shares 或 qty 或 quantity: 持股数
    - cost 或 cost_price: 成本价
    - currency 或 ccy: 币种（可选）
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR.parent


def normalize_symbol(symbol: str) -> str:
    """
    Normalize stock symbol to asset_dashboard key format.
    规范化股票代码为资产看板 key 格式
    
    Examples
    --------
    HK.00700 → tencent_futu
    00700.HK → tencent_hk
    VOO → voo
    """
    s = symbol.lower().replace(".", "_").replace("-", "_")
    
    # 特殊映射
    mapping = {
        "hk_00700": "tencent_futu",
        "00700_hk": "tencent_hk",
        "sh600000": "etf_515450",  # 示例，根据实际调整
    }
    
    return mapping.get(s, s)


def parse_futu_csv(filepath: str) -> list[dict]:
    """
    Parse Futu broker CSV export.
    解析富途牛牛导出的 CSV
    
    Expected columns:
    - 股票代码 (symbol)
    - 持股数量 (qty)
    - 成本价 (cost_price)
    - 币种 (currency)
    """
    holdings = []
    
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get("股票代码") or row.get("symbol")
            qty = row.get("持股数量") or row.get("qty")
            cost = row.get("成本价") or row.get("cost_price")
            ccy = row.get("币种") or row.get("currency") or "USD"
            
            if not symbol or not qty or not cost:
                continue
            
            key = normalize_symbol(symbol)
            holdings.append({
                "key": key,
                "shares": float(qty),
                "cost": float(cost),
                "ccy": ccy.upper()
            })
    
    return holdings


def parse_generic_csv(filepath: str) -> list[dict]:
    """
    Parse generic CSV export.
    解析通用格式 CSV
    
    Required columns (at least one of each):
    - symbol / code / ticker
    - shares / qty / quantity
    - cost / cost_price / avg_cost
    - currency / ccy (optional, defaults to USD)
    """
    holdings = []
    
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 智能匹配列名
            symbol = (row.get("symbol") or row.get("code") or 
                     row.get("ticker") or row.get("股票代码"))
            qty = (row.get("shares") or row.get("qty") or 
                   row.get("quantity") or row.get("持股数量"))
            cost = (row.get("cost") or row.get("cost_price") or 
                    row.get("avg_cost") or row.get("成本价"))
            ccy = (row.get("currency") or row.get("ccy") or 
                   row.get("币种") or "USD")
            
            if not symbol or not qty or not cost:
                continue
            
            key = normalize_symbol(symbol)
            holdings.append({
                "key": key,
                "shares": float(qty),
                "cost": float(cost),
                "ccy": ccy.upper()
            })
    
    return holdings


def convert_to_snapshot_format(holdings: list[dict]) -> dict:
    """
    Convert holdings list to snapshot format.
    转换为 snapshot 格式
    
    Parameters
    ----------
    holdings : list[dict]
        List of {"key": str, "shares": float, "cost": float, "ccy": str}
    
    Returns
    -------
    dict
        Holdings dict ready for snapshot
    """
    result = {}
    for h in holdings:
        key = h["key"]
        result[key] = {
            "shares": h["shares"],
            "cost": h["cost"],
            "ccy": h["ccy"]
        }
    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/import_holdings.py <csv文件> [--broker futu|generic]")
        print()
        print("示例:")
        print("  python3 scripts/import_holdings.py futu_export.csv --broker futu")
        print("  python3 scripts/import_holdings.py my_holdings.csv --broker generic")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    broker = "generic"
    
    if "--broker" in sys.argv:
        idx = sys.argv.index("--broker")
        if idx + 1 < len(sys.argv):
            broker = sys.argv[idx + 1].lower()
    
    if not Path(csv_file).exists():
        print(f"❌ 文件不存在: {csv_file}")
        sys.exit(1)
    
    print(f"📂 正在读取: {csv_file}")
    print(f"📊 券商格式: {broker}\n")
    
    # 解析 CSV
    if broker == "futu":
        holdings = parse_futu_csv(csv_file)
    else:
        holdings = parse_generic_csv(csv_file)
    
    if not holdings:
        print("❌ 未解析到任何持仓数据")
        print("   请检查 CSV 格式是否正确")
        sys.exit(1)
    
    print(f"✅ 成功解析 {len(holdings)} 条持仓\n")
    
    # 显示预览
    print("=" * 80)
    print("持仓预览:")
    print("=" * 80)
    for h in holdings:
        print(f"  {h['key']:20s}  {h['shares']:>10,.0f} 股  @ {h['cost']:>10.2f} {h['ccy']}")
    
    # 转换格式
    snapshot_holdings = convert_to_snapshot_format(holdings)
    
    print("\n" + "=" * 80)
    print("JSON 输出（复制到 snapshot 的 holdings 字段）:")
    print("=" * 80)
    print(json.dumps(snapshot_holdings, ensure_ascii=False, indent=2))
    
    print("\n💡 下一步:")
    print("   1. 复制上面的 JSON")
    print("   2. 粘贴到新 snapshot 的 holdings 字段")
    print("   3. 或合并到 `python3 scripts/new_snapshot.py` 的输出中")


if __name__ == "__main__":
    main()
