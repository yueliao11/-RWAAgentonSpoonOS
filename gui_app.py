#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA Yield Optimizer - Streamlit GUI Application
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import asyncio
from datetime import datetime, timedelta
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import RWADataService

# Page configuration
st.set_page_config(
    page_title="RWA Yield Optimizer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        border-color: #2ca02c;
    }
    .warning-card {
        background-color: #fff3cd;
        border-color: #ff7f0e;
    }
    .danger-card {
        background-color: #f8d7da;
        border-color: #d62728;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data service
@st.cache_resource
def get_data_service():
    return RWADataService()

# Initialize session state
def init_session_state():
    if 'data_service' not in st.session_state:
        st.session_state.data_service = get_data_service()
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None

# Async wrapper for Streamlit
def run_async(coro):
    """Run async function in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Dashboard Page
def show_dashboard():
    st.markdown('<h1 class="main-header">🏦 RWA Yield Optimizer Dashboard</h1>', unsafe_allow_html=True)
    
    data_service = st.session_state.data_service
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh All Data", type="primary", use_container_width=True):
            with st.spinner("Refreshing protocol data..."):
                results = run_async(data_service.refresh_protocol_data())
                if "error" not in results:
                    st.success("✅ Data refreshed successfully!")
                    st.session_state.last_refresh = datetime.now()
                else:
                    st.error(f"❌ Error refreshing data: {results['error']}")
    
    # Dashboard summary
    summary = data_service.get_dashboard_summary()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Protocols</h3>
            <h2>{summary['total_protocols']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card success-card">
            <h3>Average APY</h3>
            <h2>{summary['avg_apy']:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total TVL</h3>
            <h2>${summary['total_tvl']:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        last_update = summary.get('last_updated', 'Never')
        if last_update != 'Never':
            last_update = datetime.fromisoformat(last_update).strftime('%H:%M:%S')
        st.markdown(f"""
        <div class="metric-card">
            <h3>Last Updated</h3>
            <h2>{last_update}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    if summary['protocols']:
        # Protocol overview table
        st.subheader("📊 Protocol Overview")
        
        df = pd.DataFrame([{
            'Protocol': p.protocol.title(),
            'APY (%)': f"{p.current_apy:.1f}%",
            'Risk Score': f"{p.risk_score:.1f}",
            'Asset Type': p.asset_type,
            'TVL ($)': f"${p.tvl:,.0f}",
            'Min Investment': f"${p.min_investment:,.0f}",
            'Lock Period': p.lock_period
        } for p in summary['protocols']])
        
        st.dataframe(df, use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 APY Comparison")
            fig_apy = px.bar(
                x=[p.protocol.title() for p in summary['protocols']],
                y=[p.current_apy for p in summary['protocols']],
                title="Current APY by Protocol",
                labels={'x': 'Protocol', 'y': 'APY (%)'}
            )
            fig_apy.update_layout(showlegend=False)
            st.plotly_chart(fig_apy, use_container_width=True)
        
        with col2:
            st.subheader("⚖️ Risk vs Return")
            fig_risk = px.scatter(
                x=[p.risk_score for p in summary['protocols']],
                y=[p.current_apy for p in summary['protocols']],
                text=[p.protocol.title() for p in summary['protocols']],
                title="Risk Score vs APY",
                labels={'x': 'Risk Score', 'y': 'APY (%)'}
            )
            fig_risk.update_traces(textposition="top center")
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.warning("⚠️ No protocol data available. Please refresh data first.")

# Protocol Analysis Page
def show_protocol_analysis():
    st.header("🔍 Protocol Analysis")
    
    data_service = st.session_state.data_service
    protocols = data_service.get_all_protocols_data()
    
    if not protocols:
        st.warning("⚠️ No protocol data available. Please refresh data from Dashboard first.")
        return
    
    # Protocol selector
    protocol_names = [p.protocol for p in protocols]
    selected_protocol = st.selectbox(
        "Select Protocol for Analysis",
        protocol_names,
        format_func=lambda x: x.title()
    )
    
    if selected_protocol:
        protocol_data = data_service.get_protocol_data(selected_protocol)
        
        if protocol_data:
            # Protocol details
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📊 {selected_protocol.title()} Details")
                
                # Risk gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = protocol_data.risk_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Risk Score"},
                    delta = {'reference': 0.5},
                    gauge = {
                        'axis': {'range': [None, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.3], 'color': "lightgreen"},
                            {'range': [0.3, 0.7], 'color': "yellow"},
                            {'range': [0.7, 1], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.8
                        }
                    }
                ))
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.subheader("📈 Key Metrics")
                
                metrics_data = {
                    "Current APY": f"{protocol_data.current_apy:.1f}%",
                    "Risk Score": f"{protocol_data.risk_score:.2f}/1.0",
                    "Asset Type": protocol_data.asset_type,
                    "Total Value Locked": f"${protocol_data.tvl:,.0f}",
                    "Active Pools": str(protocol_data.active_pools),
                    "Min Investment": f"${protocol_data.min_investment:,.0f}",
                    "Lock Period": protocol_data.lock_period
                }
                
                for key, value in metrics_data.items():
                    st.metric(key, value)
            
            # Historical data (if available)
            st.subheader("📊 Historical Analysis")
            history = data_service.get_protocol_history(selected_protocol, days=30)
            
            if len(history) > 1:
                df_history = pd.DataFrame([{
                    'Date': datetime.fromisoformat(h.timestamp).date(),
                    'APY': h.current_apy,
                    'Risk Score': h.risk_score,
                    'TVL': h.tvl
                } for h in history])
                
                fig_history = px.line(df_history, x='Date', y='APY', title='APY Trend (30 days)')
                st.plotly_chart(fig_history, use_container_width=True)
            else:
                st.info("📝 Historical data will be available after multiple data refreshes.")

# AI Predictions Page
def show_ai_predictions():
    st.header("🤖 AI Yield Predictions")
    
    data_service = st.session_state.data_service
    protocols = data_service.get_all_protocols_data()
    
    if not protocols:
        st.warning("⚠️ No protocol data available. Please refresh data from Dashboard first.")
        return
    
    # Protocol and timeframe selection
    col1, col2 = st.columns(2)
    
    with col1:
        protocol_names = [p.protocol for p in protocols]
        selected_protocol = st.selectbox(
            "Select Protocol",
            protocol_names,
            format_func=lambda x: x.title()
        )
    
    with col2:
        timeframe = st.selectbox(
            "Prediction Timeframe",
            ["30d", "90d", "180d"],
            index=1
        )
    
    # Get prediction button
    if st.button("🔮 Get AI Prediction", type="primary"):
        with st.spinner("Getting AI prediction..."):
            prediction = run_async(data_service.get_ai_prediction(selected_protocol, timeframe))
            
            if prediction["success"]:
                st.success("✅ AI prediction completed!")
                
                # Display prediction results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Predicted APY",
                        f"{prediction['predicted_apy']:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Confidence Score",
                        f"{prediction['confidence']:.1f}/10"
                    )
                
                with col3:
                    current_data = data_service.get_protocol_data(selected_protocol)
                    if current_data:
                        change = prediction['predicted_apy'] - current_data.current_apy
                        st.metric(
                            "Expected Change",
                            f"{change:+.1f}%"
                        )
                
                # Reasoning and risk factors
                st.subheader("🧠 AI Analysis")
                st.write(prediction['reasoning'])
                
                st.subheader("⚠️ Risk Factors")
                for factor in prediction['risk_factors']:
                    st.write(f"• {factor}")
                
                # Full report
                with st.expander("📄 Full AI Report"):
                    st.text(prediction['full_report'])
            else:
                st.error(f"❌ Prediction failed: {prediction['error']}")
    
    # Prediction history
    st.subheader("📊 Prediction History")
    if selected_protocol:
        history = data_service.get_ai_predictions_history(selected_protocol)
        
        if history:
            df_predictions = pd.DataFrame([{
                'Date': datetime.fromisoformat(h.timestamp).strftime('%Y-%m-%d %H:%M'),
                'Timeframe': h.timeframe,
                'Predicted APY': f"{h.predicted_apy:.1f}%",
                'Confidence': f"{h.confidence:.1f}/10",
                'Model': h.model_name.title()
            } for h in history])
            
            st.dataframe(df_predictions, use_container_width=True)
        else:
            st.info("📝 No prediction history available yet.")

# Portfolio Optimizer Page
def show_portfolio_optimizer():
    st.header("💼 Portfolio Optimizer")
    
    data_service = st.session_state.data_service
    protocols = data_service.get_all_protocols_data()
    
    if not protocols:
        st.warning("⚠️ No protocol data available. Please refresh data from Dashboard first.")
        return
    
    # Investment parameters
    col1, col2 = st.columns(2)
    
    with col1:
        investment_amount = st.number_input(
            "Investment Amount ($)",
            min_value=1000,
            max_value=10000000,
            value=50000,
            step=1000
        )
    
    with col2:
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["low", "medium", "high"],
            index=1
        )
    
    # Optimize button
    if st.button("🎯 Optimize Portfolio", type="primary"):
        with st.spinner("Optimizing portfolio..."):
            optimization = run_async(data_service.optimize_portfolio(investment_amount, risk_tolerance))
            
            if optimization["success"]:
                st.success("✅ Portfolio optimization completed!")
                
                allocations = optimization["allocations"]
                metrics = optimization["portfolio_metrics"]
                
                # Portfolio metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Expected APY", f"{metrics['weighted_apy']:.1f}%")
                
                with col2:
                    st.metric("Expected Return", f"${metrics['expected_return']:,.0f}")
                
                with col3:
                    st.metric("Risk Score", f"{metrics['weighted_risk']:.2f}")
                
                with col4:
                    st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
                
                # Allocation charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Allocation Distribution")
                    
                    fig_pie = px.pie(
                        values=[a.allocation_percentage for a in allocations],
                        names=[a.protocol.title() for a in allocations],
                        title="Portfolio Allocation"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.subheader("💰 Allocation Amounts")
                    
                    fig_bar = px.bar(
                        x=[a.protocol.title() for a in allocations],
                        y=[a.allocation_amount for a in allocations],
                        title="Investment Amount by Protocol"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Detailed allocation table
                st.subheader("📋 Detailed Allocation")
                
                df_allocation = pd.DataFrame([{
                    'Protocol': a.protocol.title(),
                    'Amount ($)': f"${a.allocation_amount:,.0f}",
                    'Percentage (%)': f"{a.allocation_percentage:.1f}%",
                    'Expected APY (%)': f"{a.expected_apy:.1f}%",
                    'Risk Score': f"{a.risk_score:.2f}"
                } for a in allocations])
                
                st.dataframe(df_allocation, use_container_width=True)
                
                # Full report
                with st.expander("📄 Full Optimization Report"):
                    st.text(optimization['full_report'])
            else:
                st.error(f"❌ Optimization failed: {optimization['error']}")

# Settings Page
def show_settings():
    st.header("⚙️ Settings")
    
    data_service = st.session_state.data_service
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    with st.form("api_settings"):
        openai_key = st.text_input(
            "OpenRouter API Key",
            value=data_service.get_user_setting("openai_api_key", ""),
            type="password",
            help="Your OpenRouter API key for AI predictions"
        )
        
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=data_service.get_user_setting("anthropic_api_key", ""),
            type="password",
            help="Your Anthropic API key (optional)"
        )
        
        if st.form_submit_button("💾 Save API Keys"):
            if openai_key:
                data_service.save_user_setting("openai_api_key", openai_key)
                os.environ['OPENAI_API_KEY'] = openai_key
            if anthropic_key:
                data_service.save_user_setting("anthropic_api_key", anthropic_key)
                os.environ['ANTHROPIC_API_KEY'] = anthropic_key
            
            st.success("✅ API keys saved successfully!")
    
    # Application Settings
    st.subheader("🎛️ Application Settings")
    
    with st.form("app_settings"):
        auto_refresh = st.checkbox(
            "Auto-refresh data",
            value=data_service.get_user_setting("auto_refresh", "false") == "true"
        )
        
        refresh_interval = st.selectbox(
            "Refresh interval (minutes)",
            [5, 10, 15, 30, 60],
            index=1
        )
        
        theme = st.selectbox(
            "Theme",
            ["light", "dark"],
            index=0
        )
        
        if st.form_submit_button("💾 Save Settings"):
            data_service.save_user_setting("auto_refresh", str(auto_refresh).lower())
            data_service.save_user_setting("refresh_interval", str(refresh_interval))
            data_service.save_user_setting("theme", theme)
            st.success("✅ Settings saved successfully!")
    
    # Data Management
    st.subheader("🗄️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Clean Old Data", help="Remove data older than 90 days"):
            data_service.cleanup_old_data()
            st.success("✅ Old data cleaned successfully!")
    
    with col2:
        if st.button("📊 Database Stats", help="Show database statistics"):
            # Simple database stats
            protocols = data_service.get_all_protocols_data()
            st.info(f"📈 {len(protocols)} protocols in database")

# Main Application
def main():
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🏦 RWA Yield Optimizer")
    st.sidebar.markdown("---")
    
    pages = {
        "📊 Dashboard": show_dashboard,
        "🔍 Protocol Analysis": show_protocol_analysis,
        "🤖 AI Predictions": show_ai_predictions,
        "💼 Portfolio Optimizer": show_portfolio_optimizer,
        "⚙️ Settings": show_settings
    }
    
    selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))
    
    # Status information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📡 Status")
    
    if st.session_state.last_refresh:
        st.sidebar.success(f"✅ Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    else:
        st.sidebar.warning("⚠️ No data refresh yet")
    
    # Quick actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    if st.sidebar.button("🔄 Quick Refresh"):
        with st.spinner("Refreshing..."):
            data_service = st.session_state.data_service
            results = run_async(data_service.refresh_protocol_data())
            if "error" not in results:
                st.sidebar.success("✅ Refreshed!")
                st.session_state.last_refresh = datetime.now()
                st.rerun()
    
    # Display selected page
    pages[selected_page]()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🏦 RWA Yield Optimizer | Built with Streamlit | "
        f"Session: {st.session_state.data_service.session_id[:8]}..."
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()