#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式 holdings 更新工具：增量报告持仓变动，自动计算新成本。
Interactive holdings updater: incremental updates with automatic cost basis calculation.

用法 / Usage:
    python3 scripts/update_holdings.py
    python3 scripts/update_holdings.py --reset  # 重置所有持仓（危险）

功能 / Features:
    1. 加载上次快照
    2. 交互式询问每个资产是否有变动
    3. 自动计算加权平均成本（买入）
    4. 自动计算卖出成本（FIFO）
    5. 输出新 snapshot JSON
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR.parent
DATA = BASE / "data"


def load_last_snapshot() -> dict | None:
    """
    Load the last snapshot from history.json.
    读取最后一次快照
    """
    history_file = DATA / "history.json"
    if not history_file.exists():
        print(f"⚠️  未找到 {history_file}，将从零开始")
        return None
    
    with open(history_file, encoding="utf-8") as f:
        data = json.load(f)
    
    snaps = data.get("snapshots", [])
    if not snaps:
        return None
    
    snaps.sort(key=lambda s: s["date"])
    return snaps[-1]


def prompt(label: str, default=None) -> str:
    """
    Prompt user input with optional default value.
    交互式输入（带默认值）
    """
    suffix = f" [{default}]" if default else ""
    val = input(f"{label}{suffix}: ").strip()
    return val or default


def update_cash_holding(key: str, current: dict) -> dict:
    """
    Update a cash-type holding interactively.
    更新现金类持仓（交互式）
    
    Parameters
    ----------
    key : str
        Asset key (e.g. "weizhong_demand")
    current : dict
        Current holding {"raw": float, "ccy": str}
    
    Returns
    -------
    dict
        Updated holding
    """
    current_amount = current.get("raw", 0)
    ccy = current.get("ccy", "RMB")
    
    print(f"\n💰 {key} (现金类)")
    print(f"   当前金额: {current_amount:,.0f} {ccy}")
    
    action = prompt("   操作 (k=保持不变 / n=输入新金额 / d=存入 / w=取出)", "k")
    
    if action == "k":
        return current
    elif action == "n":
        new_amount = float(prompt("   新金额", str(current_amount)))
        return {"raw": new_amount, "ccy": ccy}
    elif action == "d":
        deposit = float(prompt("   存入金额", "0"))
        return {"raw": current_amount + deposit, "ccy": ccy}
    elif action == "w":
        withdraw = float(prompt("   取出金额", "0"))
        return {"raw": current_amount - withdraw, "ccy": ccy}
    else:
        print("   ⚠️  无效操作，保持不变")
        return current


def update_stock_holding(key: str, current: dict, price: float | None = None) -> dict:
    """
    Update a stock-type holding with automatic cost basis calculation.
    更新证券类持仓（自动计算成本）
    
    Parameters
    ----------
    key : str
        Asset key (e.g. "voo")
    current : dict
        Current holding {"shares": float, "cost": float, "ccy": str}
    price : float | None
        Current market price (for reference)
    
    Returns
    -------
    dict
        Updated holding
    """
    current_shares = current.get("shares", 0)
    current_cost = current.get("cost", 0)
    ccy = current.get("ccy", "USD")
    
    print(f"\n📈 {key} (证券类)")
    print(f"   当前持仓: {current_shares:,.0f} 股 @ 成本 {current_cost:.2f} {ccy}")
    if price:
        print(f"   当前市价: {price:.2f} {ccy}")
        pnl = (price - current_cost) * current_shares
        pnl_pct = ((price / current_cost) - 1) * 100 if current_cost > 0 else 0
        print(f"   浮动盈亏: {pnl:+,.0f} {ccy} ({pnl_pct:+.1f}%)")
    
    action = prompt("   操作 (k=保持不变 / b=买入 / s=卖出 / n=直接输入新数据)", "k")
    
    if action == "k":
        return current
    
    elif action == "b":
        buy_shares = float(prompt("   买入股数", "0"))
        buy_price = float(prompt("   成交价", str(price or 0)))
        
        if buy_shares <= 0:
            return current
        
        # 加权平均成本
        total_cost = current_shares * current_cost + buy_shares * buy_price
        total_shares = current_shares + buy_shares
        new_cost = total_cost / total_shares if total_shares > 0 else 0
        
        print(f"   ✅ 新成本: {new_cost:.2f} {ccy}")
        return {"shares": total_shares, "cost": new_cost, "ccy": ccy}
    
    elif action == "s":
        sell_shares = float(prompt("   卖出股数", "0"))
        sell_price = float(prompt("   成交价", str(price or 0)))
        
        if sell_shares <= 0 or sell_shares > current_shares:
            print("   ⚠️  无效卖出量")
            return current
        
        new_shares = current_shares - sell_shares
        realized_pnl = (sell_price - current_cost) * sell_shares
        print(f"   💵 已实现盈亏: {realized_pnl:+,.0f} {ccy}")
        
        # 成本价不变（FIFO）
        return {"shares": new_shares, "cost": current_cost, "ccy": ccy}
    
    elif action == "n":
        new_shares = float(prompt("   新股数", str(current_shares)))
        new_cost = float(prompt("   新成本价", str(current_cost)))
        return {"shares": new_shares, "cost": new_cost, "ccy": ccy}
    
    else:
        print("   ⚠️  无效操作，保持不变")
        return current


def main():
    reset_mode = "--reset" in sys.argv
    
    if reset_mode:
        confirm = prompt("⚠️  --reset 将清空所有持仓，确认？(yes/NO)", "NO")
        if confirm.lower() != "yes":
            print("❌ 已取消")
            return
    
    print("🚀 Holdings 增量更新工具\n")
    
    # 1. 加载上次快照
    last_snap = load_last_snapshot()
    if not last_snap:
        print("📂 未找到上次快照，从头开始\n")
        last_holdings = {}
        last_prices = {}
    else:
        print(f"📂 上次快照日期: {last_snap['date']}\n")
        last_holdings = last_snap.get("holdings", {})
        last_prices = last_snap.get("prices", {})
    
    if reset_mode:
        last_holdings = {}
    
    # 2. 逐项更新
    new_holdings = {}
    
    print("=" * 60)
    print("提示：每项资产会询问是否有变动，直接回车 = 保持不变")
    print("=" * 60)
    
    for key, holding in sorted(last_holdings.items()):
        # 判断类型
        if "raw" in holding:
            # 现金类
            new_holdings[key] = update_cash_holding(key, holding)
        elif "shares" in holding:
            # 证券类
            price = last_prices.get(key, {}).get("price")
            new_holdings[key] = update_stock_holding(key, holding, price)
        else:
            # 未知类型，保持不变
            print(f"\n⚠️  {key} 格式未知，保持不变")
            new_holdings[key] = holding
    
    # 3. 询问是否添加新资产
    print("\n" + "=" * 60)
    add_new = prompt("是否添加新资产？(y/N)", "N")
    
    while add_new.lower() == "y":
        new_key = prompt("新资产 key（例如 binance_btc）")
        asset_type = prompt("类型 (cash / stock)", "cash")
        
        if asset_type == "cash":
            amount = float(prompt("金额"))
            ccy = prompt("币种 (RMB/USD/HKD)", "RMB")
            new_holdings[new_key] = {"raw": amount, "ccy": ccy}
        else:
            shares = float(prompt("股数"))
            cost = float(prompt("成本价"))
            ccy = prompt("币种 (RMB/USD/HKD)", "USD")
            new_holdings[new_key] = {"shares": shares, "cost": cost, "ccy": ccy}
        
        add_new = prompt("继续添加？(y/N)", "N")
    
    # 4. 输出
    print("\n" + "=" * 60)
    print("📊 更新后的 holdings：")
    print("=" * 60)
    print(json.dumps(new_holdings, ensure_ascii=False, indent=2))
    
    print("\n💡 下一步：")
    print("   1. 复制上面的 holdings 到你的新 snapshot")
    print("   2. 或运行 `python3 scripts/new_snapshot.py` 生成完整 snapshot")
    print("   3. Append 到 data/history.json")


if __name__ == "__main__":
    main()
