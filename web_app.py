import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import json
from datetime import datetime

from src.platform.investment_research_platform import InvestmentResearchPlatform
from src.utils.watchlist_loader import WatchlistLoader
from src.report.report_generator import ReportGenerator

# Page config
st.set_page_config(
    page_title="个人投研平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #09ab3b;
    }
    .negative {
        color: #ff2b2b;
    }
    .warning {
        color: #ffa421;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📈 个人简化投研平台")
st.markdown("### 以自选股为驱动的策略回测与风险分析工具")

# Sidebar configuration
st.sidebar.header("⚙️ 配置参数")

initial_cash = st.sidebar.number_input(
    "初始资金（元）",
    value=100000,
    min_value=10000,
    step=10000,
    help="回测初始资金"
)

start_date = st.sidebar.date_input(
    "开始日期",
    value=pd.Timestamp("2023-01-01"),
    help="回测开始日期"
)

end_date = st.sidebar.date_input(
    "结束日期",
    value=pd.Timestamp("2024-12-31"),
    help="回测结束日期"
)

st.sidebar.markdown("---")
st.sidebar.info(
    "📝 **使用步骤：**\n"
    "1. 上传自选股 Excel/CSV 文件\n"
    "2. 点击'运行分析'\n"
    "3. 查看报告结果\n"
    "4. 下载完整报告"
)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 上传文件", "📈 分析结果", "⚠️ 风险控制", "📥 下载报告"])

# Session state
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
    st.session_state.summary = None
    st.session_state.reports = None

# Tab 1: Upload
with tab1:
    st.header("自选股文件上传")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 上传文件")
        uploaded_file = st.file_uploader(
            "选择 Excel (xlsx) 或 CSV 文件",
            type=["csv", "xlsx", "xls"],
            help="文件必须包含以下列：代码、名称、市场、启用、策略、参数、权重等"
        )
    
    with col2:
        st.markdown("### 📝 模板下载")
        template_df = pd.DataFrame({
            "代码": ["000001", "600519", "00700"],
            "名称": ["平安银行", "贵州茅台", "腾讯控股"],
            "市场": ["A", "A", "HK"],
            "启用": ["是", "是", "是"],
            "策略": ["dual_ma", "dual_ma", "macd"],
            "参数1": [5, 5, 12],
            "参数2": [20, 20, 26],
            "参数3": ["", "", 9],
            "目标权重": [0.2, 0.15, 0.25],
            "最大仓位": [0.3, 0.25, 0.3],
            "止损": [0.08, 0.08, 0.10],
            "止盈": [0.15, 0.15, 0.20],
            "备注": ["核心持仓", "消费龙头", "港股科技"]
        })
        
        csv_data = template_df.to_csv(index=False, encoding="utf-8")
        st.download_button(
            label="📥 下载模板",
            data=csv_data,
            file_name="watchlist_template.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    if uploaded_file is not None:
        st.success(f"✅ 文件已选择: {uploaded_file.name}")
        
        # Show file preview
        try:
            if uploaded_file.name.endswith(".csv"):
                preview_df = pd.read_csv(uploaded_file, encoding="utf-8")
            else:
                preview_df = pd.read_excel(uploaded_file)
            
            st.markdown("### 📋 文件预览")
            st.dataframe(preview_df, use_container_width=True)
            
            # Validate and analyze
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            
            try:
                watchlist = WatchlistLoader(tmp_path)
                enabled = watchlist.enabled_rows()
                st.info(f"✅ 文件有效！共检测到 {len(enabled)} 只启用的股票")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("启用股票数", len(enabled))
                with col_b:
                    st.metric("A股", len([x for x in enabled if x.get("market", "").lower() == "a"]))
                with col_c:
                    st.metric("港股", len([x for x in enabled if x.get("market", "").lower() == "hk"]))
                
                # Run analysis button
                if st.button("🚀 运行分析", use_container_width=True, type="primary"):
                    with st.spinner("正在进行回测和分析...这可能需要几分钟"):
                        try:
                            platform = InvestmentResearchPlatform(tmp_path, initial_cash)
                            summary = platform.run_full_analysis(
                                start_date.strftime("%Y-%m-%d"),
                                end_date.strftime("%Y-%m-%d"),
                                output_dir="reports"
                            )
                            st.session_state.summary = summary
                            st.session_state.reports = summary["reports"]
                            st.session_state.analysis_complete = True
                            st.success("✅ 分析完成！切换到'分析结果'标签页查看")
                        except Exception as e:
                            st.error(f"❌ 分析出错: {str(e)}")
                            st.write(f"详细错误: {e}")
            
            except Exception as e:
                st.error(f"❌ 文件格式错误: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ 读取文件失败: {str(e)}")
    
    else:
        st.info("👆 请上传自选股文件以开始分析")

# Tab 2: Results
with tab2:
    st.header("📊 分析结果")
    
    if st.session_state.analysis_complete and st.session_state.summary:
        summary = st.session_state.summary
        result = summary["backtest_result"]
        rec = summary["recommendation"]
        
        # Overall rating
        rating_color = {
            "STRONG BUY": "🟢",
            "BUY": "🟢",
            "HOLD": "🟡",
            "SELL": "🔴",
            "NEUTRAL": "⚪"
        }
        
        st.markdown(f"### {rating_color.get(rec['rating'], '')} 投资评级: {rec['rating']}")
        st.markdown(f"**原因**: {rec['reason']}")
        
        st.markdown("---")
        
        # Metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            profit = result["profit"]
            profit_pct = result["profit_pct"]
            color = "🟢" if profit >= 0 else "🔴"
            st.metric(
                "💰 收益",
                f"{profit:,.0f}元",
                f"{profit_pct*100:.2f}%",
                delta_color="normal"
            )
        
        with col2:
            sharpe = rec["sharpe_ratio"]
            color = "🟢" if sharpe > 0.5 else "🟡" if sharpe > 0 else "🔴"
            st.metric(
                "📊 夏普比率",
                f"{sharpe:.2f}",
                help="风险调整后的收益，越高越好，>1.0为优秀"
            )
        
        with col3:
            max_dd = rec["max_drawdown"]
            color = "🟢" if max_dd > -0.15 else "🟡" if max_dd > -0.25 else "🔴"
            st.metric(
                "📉 最大回撤",
                f"{max_dd*100:.2f}%",
                help="最大亏损幅度，越接近0越好"
            )
        
        with col4:
            volatility = rec["volatility"]
            st.metric(
                "📈 波动率",
                f"{volatility*100:.2f}%",
                help="年化波动率，低波动率更稳定"
            )
        
        st.markdown("---")
        
        # Detailed metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💼 账户情况")
            st.markdown(f"""
            - **初始资金**: ¥{result['initial_cash']:,.2f}
            - **最终资产**: ¥{result['final_value']:,.2f}
            - **净利润**: ¥{result['profit']:,.2f}
            - **交易次数**: {result['trade_count']}
            """)
        
        with col2:
            st.subheader("📊 收益指标")
            st.markdown(f"""
            - **年化收益**: {result['annualized_return']*100:.2f}%
            - **收益率**: {result['profit_pct']*100:.2f}%
            - **每笔平均收益**: ¥{result['profit']/max(result['trade_count'], 1):,.2f}
            """)
        
        with col3:
            st.subheader("⚠️ 风险指标")
            st.markdown(f"""
            - **夏普比率**: {rec['sharpe_ratio']:.2f}
            - **最大回撤**: {rec['max_drawdown']*100:.2f}%
            - **波动率**: {rec['volatility']*100:.2f}%
            """)
        
        st.markdown("---")
        
        # Trade history
        if result["trade_count"] > 0:
            st.subheader("📋 交易记录")
            trades_df = pd.DataFrame(result["trades"])
            st.dataframe(
                trades_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Current positions
        if result["portfolio_positions"]:
            st.subheader("📍 当前持仓")
            pos_data = [
                {
                    "代码": symbol,
                    "数量": pos.get("qty", 0),
                    "成本": pos.get("cost_basis", 0),
                    "买入价": pos.get("buy_price", 0)
                }
                for symbol, pos in result["portfolio_positions"].items()
            ]
            pos_df = pd.DataFrame(pos_data)
            st.dataframe(pos_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("👈 请先在'上传文件'标签页上传文件并运行分析")

# Tab 3: Risk Control
with tab3:
    st.header("⚠️ 风险控制与建议")
    
    if st.session_state.analysis_complete and st.session_state.summary:
        summary = st.session_state.summary
        
        # Weight analysis
        st.subheader("💼 持仓权重分析")
        weight_analysis = summary["weight_analysis"]
        
        if weight_analysis.get("alerts"):
            st.warning("⚠️ 风险提示:")
            for alert in weight_analysis["alerts"]:
                st.markdown(f"- {alert}")
        else:
            st.success("✅ 持仓配置合理，无风险提示")
        
        if weight_analysis.get("concentration"):
            conc = weight_analysis["concentration"]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "集中度指数",
                    f"{conc['herfindahl_index']:.3f}",
                    help="接近0表示分散，接近1表示集中"
                )
            
            with col2:
                st.metric(
                    "最大单票权重",
                    f"{conc['max_weight']*100:.1f}%",
                    help="最大的单只股票权重"
                )
            
            with col3:
                st.metric(
                    "前三大持仓比",
                    f"{conc['top3_weight']*100:.1f}%",
                    help="前三大股票总权重"
                )
        
        st.markdown("---")
        
        # Investment plan
        st.subheader("📋 投资计划")
        plan = summary["action_plan"]
        
        if plan.get("suggestions"):
            st.info("💡 **行动建议**:")
            for i, sugg in enumerate(plan["suggestions"], 1):
                st.markdown(f"{i}. {sugg}")
        
        st.markdown("---")
        
        # Recommendation text
        st.subheader("📝 详细建议")
        recommendation_text = summary.get("summary_text", "")
        st.text(recommendation_text)
    
    else:
        st.info("👈 请先在'上传文件'标签页上传文件并运行分析")

# Tab 4: Download
with tab4:
    st.header("📥 下载报告")
    
    if st.session_state.analysis_complete and st.session_state.reports:
        st.success("✅ 分析已完成，可下载以下报告:")
        
        reports = st.session_state.reports
        col1, col2 = st.columns(2)
        
        # JSON report
        if "json" in reports:
            with col1:
                with open(reports["json"], "r", encoding="utf-8") as f:
                    json_data = f.read()
                st.download_button(
                    label="📄 下载 JSON 报告",
                    data=json_data,
                    file_name=Path(reports["json"]).name,
                    mime="application/json",
                    use_container_width=True
                )
        
        # Excel report
        if "excel" in reports:
            with col2:
                with open(reports["excel"], "rb") as f:
                    excel_data = f.read()
                st.download_button(
                    label="📊 下载 Excel 报告",
                    data=excel_data,
                    file_name=Path(reports["excel"]).name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        col3, col4 = st.columns(2)
        
        # CSV report
        if "csv" in reports:
            with col3:
                with open(reports["csv"], "r", encoding="utf-8") as f:
                    csv_data = f.read()
                st.download_button(
                    label="📋 下载 CSV 交易记录",
                    data=csv_data,
                    file_name=Path(reports["csv"]).name,
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Text report
        if "text" in reports:
            with col4:
                with open(reports["text"], "r", encoding="utf-8") as f:
                    text_data = f.read()
                st.download_button(
                    label="📝 下载文本报告",
                    data=text_data,
                    file_name=Path(reports["text"]).name,
                    mime="text/plain",
                    use_container_width=True
                )
        
        st.markdown("---")
        st.info(
            "📦 **报告包含内容**:\n"
            "- **Excel**: 汇总表、交易明细、当前持仓\n"
            "- **CSV**: 交易记录（便于Excel打开）\n"
            "- **JSON**: 完整数据（便于二次处理）\n"
            "- **文本**: 格式化的分析报告"
        )
    
    else:
        st.info("👈 请先在'上传文件'标签页上传文件并运行分析")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    个人简化投研平台 v1.0 | 仅供学习与研究之用 | 不构成投资建议
</div>
""", unsafe_allow_html=True)
