from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


class ReportGenerator:
    """Generate comprehensive backtest reports."""

    def __init__(self, backtest_result: dict[str, Any], watchlist_path: str, output_dir: str = "reports"):
        self.result = backtest_result
        self.watchlist_path = watchlist_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _generate_timestamp_filename(self, ext: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"backtest_report_{timestamp}.{ext}"

    def to_dict(self) -> dict[str, Any]:
        """Export result as dictionary."""
        return self.result

    def to_json(self, path: str | None = None) -> str:
        """Export to JSON file."""
        if path is None:
            path = self._generate_timestamp_filename("json")
        else:
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        result_copy = self.result.copy()
        if "trades" in result_copy:
            result_copy["trades"] = [t.copy() if isinstance(t, dict) else t.__dict__ for t in result_copy["trades"]]
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result_copy, f, indent=2, ensure_ascii=False)
        return str(path)

    def to_csv(self, path: str | None = None) -> str:
        """Export trades to CSV."""
        if path is None:
            path = self._generate_timestamp_filename("csv")
        else:
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        trades = self.result.get("trades", [])
        if trades:
            df = pd.DataFrame(trades)
            df.to_csv(path, index=False, encoding="utf-8")
        return str(path)

    def to_excel(self, path: str | None = None) -> str:
        """Export to Excel with multiple sheets."""
        if path is None:
            path = self._generate_timestamp_filename("xlsx")
        else:
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            # Summary sheet
            summary_data = {
                "Metric": [
                    "Initial Cash",
                    "Final Value",
                    "Profit/Loss",
                    "Profit %",
                    "Trade Count",
                    "Sharpe Ratio",
                    "Max Drawdown %",
                    "Volatility %",
                    "Annualized Return %",
                ],
                "Value": [
                    f"{self.result.get('initial_cash', 0):,.2f}",
                    f"{self.result.get('final_value', 0):,.2f}",
                    f"{self.result.get('profit', 0):,.2f}",
                    f"{self.result.get('profit_pct', 0)*100:.2f}%",
                    str(self.result.get("trade_count", 0)),
                    f"{self.result.get('sharpe_ratio', 0):.2f}",
                    f"{self.result.get('max_drawdown', 0)*100:.2f}%",
                    f"{self.result.get('volatility', 0)*100:.2f}%",
                    f"{self.result.get('annualized_return', 0)*100:.2f}%",
                ],
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name="Summary", index=False)

            # Trades sheet
            trades = self.result.get("trades", [])
            if trades:
                df_trades = pd.DataFrame(trades)
                df_trades.to_excel(writer, sheet_name="Trades", index=False)

            # Positions sheet
            positions = self.result.get("portfolio_positions", {})
            if positions:
                positions_data = [{"Symbol": k, "Qty": v.get("qty", 0), "Cost Basis": v.get("cost_basis", 0)} for k, v in positions.items()]
                df_positions = pd.DataFrame(positions_data)
                df_positions.to_excel(writer, sheet_name="Positions", index=False)
        
        return str(path)

    def to_text(self, path: str | None = None) -> str:
        """Export to text report."""
        if path is None:
            path = self._generate_timestamp_filename("txt")
        else:
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self._generate_text_report()
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        return str(path)

    def _generate_text_report(self) -> str:
        """Generate formatted text report."""
        trades = self.result.get("trades", [])
        positions = self.result.get("portfolio_positions", {})
        
        report = f"""
{'='*70}
股票投资组合回测报告
{'='*70}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据源文件: {self.watchlist_path}

{'─'*70}
【投资绩效指标】
{'─'*70}
初始资金:        {self.result.get('initial_cash', 0):>15,.2f} 元
最终资产:        {self.result.get('final_value', 0):>15,.2f} 元
盈利/亏损:       {self.result.get('profit', 0):>15,.2f} 元
收益率:          {self.result.get('profit_pct', 0)*100:>15.2f}%

{'─'*70}
【风险指标】
{'─'*70}
年化收益率:      {self.result.get('annualized_return', 0)*100:>15.2f}%
波动率(年化):    {self.result.get('volatility', 0)*100:>15.2f}%
夏普比率:        {self.result.get('sharpe_ratio', 0):>15.2f}
最大回撤:        {self.result.get('max_drawdown', 0)*100:>15.2f}%

{'─'*70}
【交易统计】
{'─'*70}
总交易次数:      {self.result.get('trade_count', 0):>15}
交易详情:
"""
        
        if trades:
            report += "\n日期           操作    代码      数量       价格    理由\n"
            report += "─" * 70 + "\n"
            for trade in trades[-20:]:
                reason = trade.get("reason", "")
                report += f"{trade.get('date', ''):<12} {trade.get('action', ''):<6} {trade.get('symbol', ''):<8} {trade.get('qty', 0):>8.2f} {trade.get('price', 0):>8.2f} {reason}\n"
        
        if positions:
            report += f"\n{'─'*70}\n【当前持仓】\n{'─'*70}\n"
            for symbol, pos in positions.items():
                report += f"\n代码: {symbol}\n"
                report += f"  数量: {pos.get('qty', 0):.2f}\n"
                report += f"  成本: {pos.get('cost_basis', 0):,.2f}\n"
                report += f"  买入价: {pos.get('buy_price', 0):.2f}\n"
        
        report += f"\n{'='*70}\n【投资建议】\n{'='*70}\n"
        report += self._generate_recommendations() + "\n"
        report += f"{'='*70}\n"
        
        return report

    def _generate_recommendations(self) -> str:
        """Generate investment recommendations."""
        profit_pct = self.result.get("profit_pct", 0.0)
        sharpe = self.result.get("sharpe_ratio", 0.0)
        max_dd = self.result.get("max_drawdown", 0.0)
        volatility = self.result.get("volatility", 0.0)
        
        recommendations = []
        
        if profit_pct > 0.15 and sharpe > 1.0:
            recommendations.append("✓ 策略表现优异，建议继续使用")
        elif profit_pct > 0.05:
            recommendations.append("✓ 策略表现良好，收益正向")
        elif profit_pct < 0:
            recommendations.append("✗ 策略亏损，建议优化参数或更换策略")
        
        if max_dd > -0.15:
            recommendations.append("✓ 最大回撤控制良好")
        elif max_dd > -0.25:
            recommendations.append("⚠ 最大回撤较大，建议调整止损水平")
        else:
            recommendations.append("✗ 最大回撤过大，风险过高")
        
        if sharpe > 1.0:
            recommendations.append("✓ 风险调整收益较好")
        elif sharpe > 0.5:
            recommendations.append("⚠ 风险调整收益一般")
        else:
            recommendations.append("✗ 风险调整收益不理想")
        
        if volatility > 0.3:
            recommendations.append("⚠ 组合波动率较高，建议分散持仓")
        
        return "\n".join(recommendations)
