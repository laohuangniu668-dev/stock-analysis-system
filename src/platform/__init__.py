from __future__ import annotations

import argparse
from pathlib import Path

from src.platform.investment_research_platform import InvestmentResearchPlatform
from src.utils.watchlist_loader import WatchlistLoader


def main():
    parser = argparse.ArgumentParser(description="Personal Investment Research Platform")
    parser.add_argument(
        "--watchlist",
        default="config/watchlist.csv",
        help="Path to watchlist file (CSV or Excel)",
    )
    parser.add_argument(
        "--start",
        default="2023-01-01",
        help="Backtest start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        default="2024-12-31",
        help="Backtest end date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--cash",
        type=float,
        default=100000.0,
        help="Initial portfolio cash (default: 100000)",
    )
    parser.add_argument(
        "--output",
        default="reports",
        help="Output directory for reports",
    )
    args = parser.parse_args()

    watchlist_path = Path(args.watchlist)
    if not watchlist_path.exists():
        print(f"Error: Watchlist file not found: {watchlist_path}")
        return

    # Load watchlist to validate
    try:
        watchlist = WatchlistLoader(str(watchlist_path))
        enabled = watchlist.enabled_rows()
        print(f"Loaded {len(enabled)} enabled stocks from {watchlist_path}")
    except Exception as e:
        print(f"Error loading watchlist: {e}")
        return

    # Run full analysis
    platform = InvestmentResearchPlatform(str(watchlist_path), args.cash)
    try:
        summary = platform.run_full_analysis(args.start, args.end, args.output)
        platform.print_summary(summary)
        print(f"\nSummary report:\n{summary['summary_text']}")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
