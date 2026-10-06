from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Any

from src.engine.watchlist_backtest import WatchlistBacktest
from src.report.report_generator import ReportGenerator
from src.report.investment_plan import InvestmentPlan
from src.risk.portfolio_controller import PortfolioRiskController
from src.utils.watchlist_loader import WatchlistLoader


class InvestmentResearchPlatform:
    """Complete investment research and analysis platform."""

    def __init__(self, watchlist_path: str, initial_cash: float = 100000.0):
        self.watchlist_path = watchlist_path
        self.initial_cash = initial_cash
        self.watchlist_loader = WatchlistLoader(watchlist_path)

    def run_full_analysis(self, start_date: str, end_date: str, output_dir: str = "reports") -> dict[str, Any]:
        """Run complete investment analysis pipeline."""
        # Step 1: Backtest
        print(f"[1/4] Running backtest from {start_date} to {end_date}...")
        engine = WatchlistBacktest(self.initial_cash)
        backtest_result = engine.run_watchlist(self.watchlist_path, start_date, end_date)

        # Step 2: Portfolio Risk Analysis
        print("[2/4] Analyzing portfolio risk...")
        risk_controller = PortfolioRiskController(self.initial_cash, self.watchlist_loader.enabled_rows())
        positions = backtest_result.get("portfolio_positions", {})
        weight_analysis = risk_controller.validate_portfolio_weights(positions)

        # Step 3: Investment Plan
        print("[3/4] Generating investment plan...")
        plan_generator = InvestmentPlan(backtest_result, self.watchlist_loader.enabled_rows())
        recommendation = plan_generator.generate_recommendation()
        action_plan = plan_generator.generate_action_plan()

        # Step 4: Report Generation
        print("[4/4] Generating reports...")
        report_gen = ReportGenerator(backtest_result, self.watchlist_path, output_dir)
        
        reports = {}
        reports["json"] = report_gen.to_json()
        reports["csv"] = report_gen.to_csv()
        reports["excel"] = report_gen.to_excel()
        reports["text"] = report_gen.to_text()

        # Summary
        summary = {
            "backtest_result": backtest_result,
            "weight_analysis": weight_analysis,
            "recommendation": recommendation,
            "action_plan": action_plan,
            "reports": reports,
            "summary_text": plan_generator.generate_summary(),
        }

        print(f"\n✓ Analysis complete!")
        print(f"\nReports generated in: {output_dir}/")
        print(f"  - {Path(reports['json']).name}")
        print(f"  - {Path(reports['excel']).name}")
        print(f"  - {Path(reports['text']).name}")
        print(f"  - {Path(reports['csv']).name}")

        return summary

    def print_summary(self, summary: dict[str, Any]) -> None:
        """Print analysis summary to console."""
        print("\n" + "="*70)
        print("投资分析总结")
        print("="*70)
        
        result = summary["backtest_result"]
        rec = summary["recommendation"]
        
        print(f"\n【回测结果】")
        print(f"初始资金:     {result['initial_cash']:>15,.2f} 元")
        print(f"最终资产:     {result['final_value']:>15,.2f} 元")
        print(f"收益率:       {result['profit_pct']*100:>15.2f}%")
        print(f"交易次数:     {result['trade_count']:>15}")
        
        print(f"\n【风险指标】")
        print(f"夏普比率:     {rec['sharpe_ratio']:>15.2f}")
        print(f"最大回撤:     {rec['max_drawdown']*100:>15.2f}%")
        print(f"波动率:       {rec['volatility']*100:>15.2f}%")
        print(f"年化收益:     {result['annualized_return']*100:>15.2f}%")
        
        print(f"\n【投资评级】")
        print(f"评级:         {rec['rating']:>20}")
        print(f"理由:         {rec['reason']}")
        
        print(f"\n【风险提示】")
        alerts = summary["weight_analysis"].get("alerts", [])
        if alerts:
            for alert in alerts:
                print(f"  ⚠ {alert}")
        else:
            print("  ✓ 无风险提示")
        
        print(f"\n【行动建议】")
        for action in summary["action_plan"].get("suggestions", []):
            print(f"  • {action}")
        
        print("\n" + "="*70)
