from __future__ import annotations

import pandas as pd
from typing import Any

from src.risk.risk_analyzer import RiskAnalyzer


class PortfolioRiskController:
    """Portfolio-level risk control and management."""

    def __init__(self, portfolio_value: float, watchlist_config: list[dict[str, Any]]):
        self.portfolio_value = portfolio_value
        self.watchlist = watchlist_config

    def validate_portfolio_weights(self, positions: dict[str, dict[str, float]]) -> dict[str, Any]:
        """Validate current portfolio weight against limits."""
        total_value = sum(pos["qty"] * pos.get("buy_price", 1.0) for pos in positions.values())
        if total_value == 0:
            return {"status": "empty", "alerts": []}

        weights = {}
        for symbol, pos in positions.items():
            w = (pos["qty"] * pos.get("buy_price", 1.0)) / total_value if total_value else 0.0
            weights[symbol] = w

        alerts = []
        for symbol, weight in weights.items():
            item = next((x for x in self.watchlist if x["code"] == symbol), None)
            if not item:
                continue
            max_pos = item.get("max_position", 0.3)
            if weight > max_pos:
                alerts.append(f"Warning: {symbol} position ({weight*100:.1f}%) exceeds limit ({max_pos*100:.1f}%)")

        concentration = RiskAnalyzer.calculate_concentration_risk(weights)
        if not concentration["diversified"]:
            alerts.append(f"Warning: Portfolio concentration risk high (Herfindahl: {concentration['herfindahl_index']:.3f})")

        return {"status": "ok", "weights": weights, "concentration": concentration, "alerts": alerts}

    def calculate_rebalance_actions(self, positions: dict[str, dict[str, float]], target_prices: dict[str, float]) -> dict[str, Any]:
        """Calculate rebalancing actions based on target weights."""
        current_value = sum(pos["qty"] * target_prices.get(pos["symbol"], pos.get("buy_price", 1.0)) for pos in positions.values())
        if current_value == 0:
            return {"actions": []}

        actions = []
        for item in self.watchlist:
            symbol = item["code"]
            target_weight = item.get("target_weight", 0.0)
            if target_weight == 0:
                continue

            target_value = current_value * target_weight
            current_pos = positions.get(symbol, {})
            current_value_pos = current_pos.get("qty", 0) * target_prices.get(symbol, current_pos.get("buy_price", 1.0))
            
            if current_value_pos == 0 and target_value > 0:
                qty_to_buy = target_value / target_prices.get(symbol, 1.0) if target_prices.get(symbol) else 0
                actions.append({"symbol": symbol, "action": "BUY", "qty": qty_to_buy, "price": target_prices.get(symbol, 0)})
            elif abs(current_value_pos - target_value) / target_value > 0.1:
                delta = target_value - current_value_pos
                if delta > 0:
                    qty_to_buy = delta / target_prices.get(symbol, 1.0) if target_prices.get(symbol) else 0
                    actions.append({"symbol": symbol, "action": "BUY", "qty": qty_to_buy, "price": target_prices.get(symbol, 0)})
                else:
                    qty_to_sell = abs(delta) / target_prices.get(symbol, 1.0) if target_prices.get(symbol) else 0
                    actions.append({"symbol": symbol, "action": "SELL", "qty": qty_to_sell, "price": target_prices.get(symbol, 0)})

        return {"actions": actions, "current_value": current_value}

    def check_stop_loss_conditions(self, positions: dict[str, dict[str, float]], current_prices: dict[str, float]) -> list[dict[str, Any]]:
        """Check which positions should be stopped out."""
        stop_signals = []
        for item in self.watchlist:
            symbol = item["code"]
            pos = positions.get(symbol)
            if not pos:
                continue
            
            stop_loss = item.get("stop_loss", 0.08)
            buy_price = pos.get("buy_price", 1.0)
            current_price = current_prices.get(symbol, buy_price)
            
            loss_pct = (buy_price - current_price) / buy_price
            if loss_pct > stop_loss:
                stop_signals.append({
                    "symbol": symbol,
                    "action": "STOP_LOSS",
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "loss_pct": loss_pct,
                    "qty": pos.get("qty", 0),
                })

        return stop_signals

    def check_take_profit_conditions(self, positions: dict[str, dict[str, float]], current_prices: dict[str, float]) -> list[dict[str, Any]]:
        """Check which positions should take profit."""
        profit_signals = []
        for item in self.watchlist:
            symbol = item["code"]
            pos = positions.get(symbol)
            if not pos:
                continue
            
            take_profit = item.get("take_profit")
            if not take_profit:
                continue
            
            buy_price = pos.get("buy_price", 1.0)
            current_price = current_prices.get(symbol, buy_price)
            
            profit_pct = (current_price - buy_price) / buy_price
            if profit_pct > take_profit:
                profit_signals.append({
                    "symbol": symbol,
                    "action": "TAKE_PROFIT",
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "profit_pct": profit_pct,
                    "qty": pos.get("qty", 0),
                })

        return profit_signals
