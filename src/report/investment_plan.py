from __future__ import annotations

from typing import Any


class InvestmentPlan:
    """Generate investment recommendations and action plans."""

    def __init__(self, backtest_result: dict[str, Any], watchlist_config: dict[str, Any]):
        self.result = backtest_result
        self.config = watchlist_config

    def generate_recommendation(self) -> dict[str, Any]:
        """Generate investment recommendation based on backtest results."""
        profit_pct = self.result.get("profit_pct", 0.0)
        sharpe = self.result.get("sharpe_ratio", 0.0)
        max_dd = self.result.get("max_drawdown", 0.0)
        volatility = self.result.get("volatility", 0.0)
        trade_count = self.result.get("trade_count", 0)

        # Decision logic
        if profit_pct > 0.15 and sharpe > 1.0 and max_dd > -0.2:
            rating = "STRONG BUY"
            reason = "Strategy demonstrated excellent returns with acceptable risk."
        elif profit_pct > 0.05 and sharpe > 0.5 and max_dd > -0.25:
            rating = "BUY"
            reason = "Strategy showed positive returns with moderate risk profile."
        elif profit_pct >= 0 and max_dd > -0.3:
            rating = "HOLD"
            reason = "Strategy is breakeven but has reasonable risk control."
        elif max_dd < -0.3 or sharpe < -0.5:
            rating = "SELL"
            reason = "Strategy exhibits high drawdown or poor risk-adjusted returns."
        else:
            rating = "NEUTRAL"
            reason = "Strategy performance is inconclusive; needs further analysis."

        return {
            "rating": rating,
            "reason": reason,
            "profit_pct": profit_pct,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "volatility": volatility,
            "trade_count": trade_count,
        }

    def generate_action_plan(self) -> dict[str, Any]:
        """Generate actionable investment plan."""
        trades = self.result.get("trades", [])
        positions = self.result.get("portfolio_positions", {})
        profit_pct = self.result.get("profit_pct", 0.0)
        sharpe = self.result.get("sharpe_ratio", 0.0)
        max_dd = self.result.get("max_drawdown", 0.0)

        actions = []

        # Recent trading actions
        if trades:
            recent_trades = sorted(trades, key=lambda t: t["date"])[-5:]
            for trade in recent_trades:
                action = {
                    "date": trade["date"],
                    "symbol": trade["symbol"],
                    "type": "BUY" if trade["action"] == "buy" else "SELL",
                    "qty": round(trade["qty"], 2),
                    "price": round(trade["price"], 2),
                }
                actions.append(action)

        # Risk management suggestions
        suggestions = []
        if max_dd < -0.25:
            suggestions.append("Consider tightening stop-loss levels (current max drawdown > 25%)")
        if sharpe < 0.5:
            suggestions.append("Risk-adjusted returns are low; review strategy parameters")
        if profit_pct < 0 and len(trades) > 10:
            suggestions.append("Strategy is losing money with high trading frequency; reduce trade count")
        if positions:
            suggestions.append(f"Current positions: {', '.join(positions.keys())}")

        return {
            "recent_trades": actions,
            "suggestions": suggestions,
            "next_review_date": "1 month",
        }

    def generate_summary(self) -> str:
        """Generate summary text report."""
        rec = self.generate_recommendation()
        plan = self.generate_action_plan()

        summary = f"""
投资分析报告
{'='*60}

评级: {rec['rating']}
原因: {rec['reason']}

关键指标:
- 收益率: {rec['profit_pct']*100:.2f}%
- 夏普比率: {rec['sharpe_ratio']:.2f}
- 最大回撤: {rec['max_drawdown']*100:.2f}%
- 波动率: {rec['volatility']*100:.2f}%
- 交易次数: {rec['trade_count']}

行动建议:
{chr(10).join(f"- {s}" for s in plan['suggestions'])}

近期交易记录:
{chr(10).join(f"  {t['date']} {t['type']} {t['symbol']} {t['qty']:.2f}股@{t['price']:.2f}元" for t in plan['recent_trades'][-5:])}

下次审查: {plan['next_review_date']}
{'='*60}
        """
        return summary
