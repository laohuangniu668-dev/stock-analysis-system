from __future__ import annotations

import pandas as pd
from typing import Any


class RiskAnalyzer:
    """Risk analysis and monitoring."""

    @staticmethod
    def calculate_concentration_risk(weights: dict[str, float]) -> dict[str, Any]:
        """Calculate portfolio concentration risk."""
        if not weights:
            return {"herfindahl_index": 0.0, "max_weight": 0.0, "top3_weight": 0.0, "diversified": True}
        values = list(weights.values())
        herfindahl = sum(w ** 2 for w in values)
        max_w = max(values) if values else 0.0
        sorted_weights = sorted(values, reverse=True)
        top3 = sum(sorted_weights[:3])
        diversified = herfindahl < 0.25 and max_w < 0.5
        return {"herfindahl_index": herfindahl, "max_weight": max_w, "top3_weight": top3, "diversified": diversified}

    @staticmethod
    def calculate_position_sizing(account_value: float, risk_per_trade: float, stop_loss_pct: float) -> dict[str, Any]:
        """Calculate position sizing based on risk parameters."""
        if stop_loss_pct <= 0:
            return {"position_size": 0.0, "units": 0.0, "risk_amount": 0.0}
        risk_amount = account_value * risk_per_trade
        position_size = risk_amount / (stop_loss_pct * account_value) if stop_loss_pct > 0 else 0.0
        return {"position_size": position_size, "risk_amount": risk_amount, "risk_per_trade_pct": risk_per_trade * 100}

    @staticmethod
    def calculate_portfolio_volatility(individual_vols: dict[str, float], weights: dict[str, float], correlation_matrix: dict[str, dict[str, float]] | None = None) -> float:
        """Calculate portfolio volatility."""
        if not weights or not individual_vols:
            return 0.0
        weighted_vol = sum(weights.get(symbol, 0) * individual_vols.get(symbol, 0) for symbol in individual_vols.keys())
        return weighted_vol

    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Value at Risk."""
        if returns.empty:
            return 0.0
        return returns.quantile(1 - confidence)

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk."""
        if returns.empty:
            return 0.0
        var_threshold = returns.quantile(1 - confidence)
        return returns[returns <= var_threshold].mean()
