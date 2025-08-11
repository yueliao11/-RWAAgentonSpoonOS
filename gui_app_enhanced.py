#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA Yield Optimizer - Enhanced Streamlit GUI Application
Professional, elegant, user-friendly and powerful interface design
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
import json
import os
import sys
from streamlit_option_menu import option_menu
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import RWADataService
from utils.i18n import get_i18n, t, create_language_selector

# Color conversion utility function
def hex_to_rgba(hex_color, alpha=0.2):
    """Convert hexadecimal color to rgba format"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

# Page configuration - Dark theme
st.set_page_config(
    page_title="RWA Yield Optimizer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/XSpoonAi/spoon-core',
        'Report a bug': "https://github.com/XSpoonAi/spoon-core/issues",
        'About': "# RWA Yield Optimizer Pro\nProfessional RWA Investment Analysis Platform"
    }
)

# Professional dark theme CSS styles - Reference design
DARK_THEME_CSS = """
<style>
    /* Global dark theme - Reference design color scheme */
    .stApp {
        background: linear-gradient(135deg, #1a1d29 0%, #252a3a 50%, #2d3748 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main title style - Clean and professional */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: left;
        margin: 1rem 0 2rem 0;
        letter-spacing: -0.02em;
    }
    
    /* Professional card styles - Reference design */
    .metric-card {
        background: rgba(37, 42, 58, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* Protocol card styles - Reference design protocol display */
    .protocol-card {
        background: linear-gradient(135deg, rgba(37, 42, 58, 0.9), rgba(45, 55, 72, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .protocol-card:hover {
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
    }
    
    /* Protocol icon style */
    .protocol-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto 1rem auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* APY value style */
    .apy-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #3b82f6;
        margin: 0.5rem 0;
        text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    }
    
    /* Protocol name style */
    .protocol-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    /* Statistics card style */
    .stats-card {
        background: rgba(37, 42, 58, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        color: #3b82f6;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    /* Heatmap style */
    .heatmap-container {
        background: rgba(37, 42, 58, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Button styles - Reference design */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        background: linear-gradient(135deg, #2563eb, #1e40af);
    }
    
    /* Sidebar style */
    .css-1d391kg {
        background: rgba(26, 29, 41, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Navigation link style */
    .nav-link {
        background: rgba(37, 42, 58, 0.6) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        margin: 4px 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .nav-link:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        transform: translateX(4px) !important;
    }
    
    .nav-link-selected {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(29, 78, 216, 0.3)) !important;
        border-color: rgba(59, 130, 246, 0.6) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Status indicator */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online {
        background: #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    
    .status-warning {
        background: #f59e0b;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Table style optimization */
    .stDataFrame {
        background: rgba(37, 42, 58, 0.8);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input box style */
    .stTextInput > div > div > input {
        background: rgba(37, 42, 58, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stSelectbox > div > div > select {
        background: rgba(37, 42, 58, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* Warning card */
    .warning-card {
        background: linear-gradient(145deg, rgba(255, 193, 7, 0.2), rgba(255, 193, 7, 0.1));
        border-color: rgba(255, 193, 7, 0.5);
    }
    
    /* Danger card */
    .danger-card {
        background: linear-gradient(145deg, rgba(244, 67, 54, 0.2), rgba(244, 67, 54, 0.1));
        border-color: rgba(244, 67, 54, 0.5);
    }
    
    /* Sidebar style */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Button style */
    .stButton > button {
        background: linear-gradient(45deg, #00d4ff, #4ecdc4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5);
    }
    
    /* Metric value style */
    .big-metric {
        font-size: 3rem;
        font-weight: 900;
        color: #00d4ff;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    .metric-label {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 0.5rem;
    }
    
    /* Animation effects */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Chart container */
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #4caf50; box-shadow: 0 0 10px #4caf50; }
    .status-warning { background-color: #ff9800; box-shadow: 0 0 10px #ff9800; }
    .status-offline { background-color: #f44336; box-shadow: 0 0 10px #f44336; }
    
    /* Sidebar dark theme fix */
    .css-1d391kg, .css-1lcbmhc, .css-17eq0hr, .css-1cypcdb {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    /* Streamlit sidebar text color */
    .css-1d391kg .stMarkdown, .css-1lcbmhc .stMarkdown, .css-1cypcdb .stMarkdown {
        color: white !important;
    }
    
    /* Sidebar title */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3,
    .css-1lcbmhc h1, .css-1lcbmhc h2, .css-1lcbmhc h3,
    .css-1cypcdb h1, .css-1cypcdb h2, .css-1cypcdb h3 {
        color: #00d4ff !important;
    }
    
    /* Option Menu dark theme enhancement */
    .nav-link {
        background-color: rgba(26, 26, 46, 0.8) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        margin: 5px 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .nav-link:hover {
        background-color: rgba(0, 212, 255, 0.3) !important;
        transform: translateX(5px) !important;
    }
    
    .nav-link-selected {
        background: linear-gradient(45deg, rgba(0, 212, 255, 0.4), rgba(78, 205, 196, 0.4)) !important;
        border-left: 4px solid #00d4ff !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* Fix sidebar input and select boxes */
    .css-1d391kg .stSelectbox > div > div,
    .css-1lcbmhc .stSelectbox > div > div,
    .css-1cypcdb .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .css-1d391kg .stTextInput > div > div > input,
    .css-1lcbmhc .stTextInput > div > div > input,
    .css-1cypcdb .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Fix sidebar divider */
    .css-1d391kg hr, .css-1lcbmhc hr, .css-1cypcdb hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

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
    if 'selected_protocols' not in st.session_state:
        st.session_state.selected_protocols = ['centrifuge', 'goldfinch']
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'

# Async wrapper
def run_async(coro):
    """Run async function in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Create cool dashboard charts
def create_gauge_chart(value, title, max_value=100, color_scheme="blues"):
    """Create gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20, 'color': 'white'}},
        delta = {'reference': max_value * 0.7},
        gauge = {
            'axis': {'range': [None, max_value], 'tickcolor': 'white'},
            'bar': {'color': "#00d4ff"},
            'steps': [
                {'range': [0, max_value * 0.3], 'color': "rgba(255, 107, 107, 0.3)"},
                {'range': [max_value * 0.3, max_value * 0.7], 'color': "rgba(255, 193, 7, 0.3)"},
                {'range': [max_value * 0.7, max_value], 'color': "rgba(76, 175, 80, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "#ff6b6b", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    return fig

# Create professional line chart - Reference design style
def create_dynamic_line_chart(data, title="Protocol Performance"):
    """Create professional style dynamic line chart"""
    fig = go.Figure()
    
    # Professional color scheme - Reference design
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    for i, protocol in enumerate(data.keys()):
        fig.add_trace(go.Scatter(
            x=list(range(len(data[protocol]))),
            y=data[protocol],
            mode='lines',
            name=protocol.title(),
            line=dict(
                color=colors[i % len(colors)], 
                width=2,
                shape='spline'  # Smooth curve
            ),
            fill='tonexty' if i > 0 else 'tozeroy',
            fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.1)',
            hovertemplate=f'<b>{protocol.title()}</b><br>Day: %{{x}}<br>APY: %{{y:.2f}}%<extra></extra>'
        ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(37, 42, 58, 0.8)",
        font={'color': "#e2e8f0", 'family': "Inter"},
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
            tickcolor='#94a3b8',
            title=dict(text="", font=dict(color='#94a3b8')),
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
            tickcolor='#94a3b8',
            title=dict(text="", font=dict(color='#94a3b8')),
            showgrid=True,
            gridwidth=1,
            ticksuffix='%'
        ),
        legend=dict(
            bgcolor="rgba(37, 42, 58, 0.9)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(color='#e2e8f0')
        ),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode='x unified'
    )
    
    return fig

# Create 3D scatter plot for multi-model prediction comparison
def create_3d_prediction_chart(predictions_data):
    """Create 3D scatter plot for multi-model predictions"""
    fig = go.Figure()
    
    models = ['GPT-4', 'Claude-3.5', 'Gemini-Pro']
    colors = ['#00d4ff', '#ff6b6b', '#4ecdc4']
    
    for i, model in enumerate(models):
        if model.lower().replace('-', '').replace('.', '') in predictions_data:
            data = predictions_data[model.lower().replace('-', '').replace('.', '')]
            fig.add_trace(go.Scatter3d(
                x=data.get('apy', []),
                y=data.get('confidence', []),
                z=data.get('risk', []),
                mode='markers',
                name=model,
                marker=dict(
                    size=12,
                    color=colors[i],
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                hovertemplate=f'<b>{model}</b><br>APY: %{{x:.2f}}%<br>Confidence: %{{y:.1f}}<br>Risk: %{{z:.2f}}<extra></extra>'
            ))
    
    fig.update_layout(
        title={
            'text': "Multi-Model AI Predictions Comparison",
            'x': 0.5,
            'font': {'size': 24, 'color': 'white'}
        },
        scene=dict(
            xaxis_title="Predicted APY (%)",
            yaxis_title="Confidence Score",
            zaxis_title="Risk Score",
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white'),
            zaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white')
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=500
    )
    
    return fig

# Create heatmap for protocol comparison
def create_heatmap_comparison(protocols_data):
    """Create heatmap for protocol comparison"""
    if not protocols_data:
        return go.Figure()
    
    protocols = list(protocols_data.keys())
    metrics = ['APY', 'Risk Score', 'TVL (M)', 'Pools', 'Min Investment (K)']
    
    # Build data matrix
    z_data = []
    for metric in metrics:
        row = []
        for protocol in protocols:
            protocol_data = protocols_data[protocol]
            if metric == 'APY':
                row.append(getattr(protocol_data, 'current_apy', 0))
            elif metric == 'Risk Score':
                row.append(getattr(protocol_data, 'risk_score', 0) * 10)  # Scale for display
            elif metric == 'TVL (M)':
                row.append(getattr(protocol_data, 'tvl', 0) / 1000000)  # Convert to millions
            elif metric == 'Pools':
                row.append(getattr(protocol_data, 'active_pools', 0))
            elif metric == 'Min Investment (K)':
                row.append(getattr(protocol_data, 'min_investment', 0) / 1000)  # Convert to thousands
        z_data.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=[p.title() for p in protocols],
        y=metrics,
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Protocol Comparison Heatmap",
            'x': 0.5,
            'font': {'size': 24, 'color': 'white'}
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=400
    )
    
    return fig# Real-time data panel

def show_realtime_dashboard():
    """Real-time data dashboard - Professional dashboard display"""
    st.markdown(f'<h1 class="main-title">🏠 {t("dashboard.title")}</h1>', unsafe_allow_html=True)
    
    # 添加功能介绍
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #3b82f6;">
        <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
        📊 <strong>{t("dashboard.description")}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    data_service = st.session_state.data_service
    
    # Top control panel
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        if st.button(f"🔄 {t('dashboard.controls.refresh_data')}", key="refresh_main"):
            with st.spinner(f"🌐 {t('dashboard.messages.fetching_data')}"):
                results = run_async(data_service.refresh_protocol_data())
                if "error" not in results:
                    st.success(f"✅ {t('dashboard.messages.data_updated')}")
                    st.session_state.last_refresh = datetime.now()
                    time.sleep(1)
                    st.rerun()
    
    with col2:
        auto_refresh = st.checkbox(f"🔄 {t('dashboard.controls.auto_refresh')}", value=False)
        if auto_refresh:
            time.sleep(5)
            st.rerun()
    
    with col3:
        time_range = st.selectbox(f"📅 {t('dashboard.controls.time_range')}", ["24H", "7D", "30D", "90D"], index=1)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="status-indicator status-online"></div>
            <span style="color: white;">{t('dashboard.controls.system_online')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Get protocol data
    summary = data_service.get_dashboard_summary()
    protocols = summary.get('protocols', [])
    
    if not protocols:
        st.warning(f"⚠️ {t('dashboard.messages.no_data')}")
        return
    
    # Key metrics cards
    st.markdown(f"### 📊 {t('dashboard.kpi.title', default='Key Performance Indicators')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card success-card">
            <div class="metric-label">Total Protocols</div>
            <div class="big-metric">{len(protocols)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_apy = sum(p.current_apy for p in protocols) / len(protocols)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average APY</div>
            <div class="big-metric">{avg_apy:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_tvl = sum(p.tvl for p in protocols)
        st.markdown(f"""
        <div class="metric-card warning-card">
            <div class="metric-label">Total TVL</div>
            <div class="big-metric">${total_tvl/1000000:.1f}M</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.last_refresh:
            last_update = st.session_state.last_refresh.strftime('%H:%M:%S')
        else:
            last_update = "Never"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Last Update</div>
            <div class="big-metric" style="font-size: 1.5rem;">{last_update}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Protocol APY Metrics - Reference design style
    st.markdown("### Protocol APY Metrics")
    
    # Create protocol card grid
    cols = st.columns(5)  # 5 protocols, 5 per row
    
    # Protocol icon mapping
    protocol_icons = {
        'centrifuge': '🏠',
        'goldfinch': '💰', 
        'maple': '🏦',
        'credix': '🌍',
        'truefi': '⚡'
    }
    
    protocol_names = {
        'centrifuge': 'ETH Staking',
        'goldfinch': 'Stablecoin Lending',
        'maple': 'Tokenized Real Estate',
        'credix': 'Fixed Income Bonds',
        'truefi': 'Quantitative Strategy Fund'
    }
    
    for i, protocol in enumerate(protocols):
        with cols[i]:
            icon = protocol_icons.get(protocol.protocol, '📊')
            name = protocol_names.get(protocol.protocol, protocol.protocol.title())
            
            st.markdown(f"""
            <div class="protocol-card">
                <div class="protocol-icon">
                    {icon}
                </div>
                <div class="protocol-name">{name}</div>
                <div class="apy-value">{protocol.current_apy:.2f}%</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">
                    Max APY {protocol.current_apy + 2:.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 30-Day APY Trends - Reference design
    st.markdown("### 30-Day APY Trends")
    st.markdown('<p style="color: #94a3b8; margin-bottom: 2rem;">Overall performance of RWA yields over the past 30 days</p>', unsafe_allow_html=True)
    
    # Simulate historical data (in real application, get from database)
    historical_data = {}
    for protocol in protocols:
        base_apy = protocol.current_apy
        # Generate simulated historical data
        historical_data[protocol.protocol] = [
            base_apy + np.random.normal(0, 0.5) for _ in range(30)
        ]
    
    line_fig = create_dynamic_line_chart(historical_data, "Protocol APY Trends (30 Days)")
    st.plotly_chart(line_fig, use_container_width=True)
    
    # Protocol details table
    st.markdown("### 📋 Protocol Details")
    
    # Create detailed data table
    df_data = []
    for protocol in protocols:
        df_data.append({
            'Protocol': protocol.protocol.title(),
            'APY (%)': f"{protocol.current_apy:.1f}%",
            'Risk Score': f"{protocol.risk_score:.2f}",
            'Asset Type': protocol.asset_type,
            'TVL': f"${protocol.tvl:,.0f}",
            'Active Pools': protocol.active_pools,
            'Min Investment': f"${protocol.min_investment:,.0f}",
            'Lock Period': protocol.lock_period,
            'Status': '🟢 Active' if protocol.tvl > 0 else '🔴 Inactive'
        })
    
    df = pd.DataFrame(df_data)
    
    # Use streamlit-aggrid for enhanced table display
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
        
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_selection('multiple', use_checkbox=True)
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, 
                                   aggFunc='sum', editable=False)
        
        grid_options = gb.build()
        
        AgGrid(
            df,
            gridOptions=grid_options,
            data_return_mode='AS_INPUT',
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            theme='streamlit',
            enable_enterprise_modules=True,
            height=400,
            width='100%'
        )
    except ImportError:
        # If st_aggrid is not installed, use standard table
        st.dataframe(df, use_container_width=True, height=400)

# Multi-model prediction page
def show_ai_predictions():
    """Multi-model AI prediction page"""
    st.markdown(f'<h1 class="main-title">🤖 {t("predictions.title")}</h1>', unsafe_allow_html=True)
    
    # 添加功能介绍
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #10b981;">
        <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
        🧠 <strong>{t("predictions.description")}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    data_service = st.session_state.data_service
    protocols = data_service.get_all_protocols_data()
    
    if not protocols:
        st.warning(f"⚠️ {t('dashboard.messages.no_data_from_dashboard')}")
        return
    
    # Prediction parameter control panel
    st.markdown(f"### 🎛️ {t('predictions.parameters.title', default='Prediction Parameters')}")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        selected_protocol = st.selectbox(
            "🏦 Select Protocol",
            [p.protocol for p in protocols],
            format_func=lambda x: x.title()
        )
    
    with col2:
        timeframe = st.selectbox(
            "⏰ Prediction Timeframe",
            ["30d", "90d", "180d", "365d"],
            index=1
        )
    
    with col3:
        model_selection = st.multiselect(
            "🧠 AI Models",
            ["GPT-4", "Claude-3.5", "Gemini-Pro"],
            default=["GPT-4", "Claude-3.5", "Gemini-Pro"]
        )
    
    # Prediction button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔮 Generate AI Predictions", type="primary", use_container_width=True):
            with st.spinner("🧠 AI models are analyzing..."):
                prediction = run_async(data_service.get_ai_prediction(selected_protocol, timeframe))
                
                if prediction["success"]:
                    st.session_state.current_prediction = prediction
                    st.success("✅ AI prediction completed!")
                else:
                    st.error(f"❌ Prediction failed: {prediction['error']}")
    
    # Display prediction results
    if hasattr(st.session_state, 'current_prediction') and st.session_state.current_prediction:
        prediction = st.session_state.current_prediction
        
        # Prediction result metrics
        st.markdown("### 🎯 Prediction Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card success-card">
                <div class="metric-label">Predicted APY</div>
                <div class="big-metric">{prediction['predicted_apy']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Confidence Score</div>
                <div class="big-metric">{prediction['confidence']:.1f}/10</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            current_data = data_service.get_protocol_data(selected_protocol)
            if current_data:
                change = prediction['predicted_apy'] - current_data.current_apy
                color_class = "success-card" if change > 0 else "danger-card" if change < 0 else "warning-card"
                st.markdown(f"""
                <div class="metric-card {color_class}">
                    <div class="metric-label">Expected Change</div>
                    <div class="big-metric">{change:+.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            risk_level = "Low" if prediction['confidence'] > 7 else "Medium" if prediction['confidence'] > 5 else "High"
            color_class = "success-card" if risk_level == "Low" else "warning-card" if risk_level == "Medium" else "danger-card"
            st.markdown(f"""
            <div class="metric-card {color_class}">
                <div class="metric-label">Risk Level</div>
                <div class="big-metric" style="font-size: 1.5rem;">{risk_level}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 3D scatter plot for multi-model comparison
        st.markdown("### 🎲 Multi-Model Comparison (3D View)")
        
        # Simulate multi-model data
        predictions_data = {
            'gpt4': {
                'apy': [prediction['predicted_apy'] + np.random.normal(0, 0.3) for _ in range(5)],
                'confidence': [prediction['confidence'] + np.random.normal(0, 0.5) for _ in range(5)],
                'risk': [np.random.uniform(0.2, 0.8) for _ in range(5)]
            },
            'claude35': {
                'apy': [prediction['predicted_apy'] + np.random.normal(0, 0.2) for _ in range(5)],
                'confidence': [prediction['confidence'] + np.random.normal(0, 0.3) for _ in range(5)],
                'risk': [np.random.uniform(0.3, 0.7) for _ in range(5)]
            },
            'geminipro': {
                'apy': [prediction['predicted_apy'] + np.random.normal(0, 0.4) for _ in range(5)],
                'confidence': [prediction['confidence'] + np.random.normal(0, 0.4) for _ in range(5)],
                'risk': [np.random.uniform(0.1, 0.9) for _ in range(5)]
            }
        }
        
        scatter_3d_fig = create_3d_prediction_chart(predictions_data)
        st.plotly_chart(scatter_3d_fig, use_container_width=True)
        
        # AI analysis details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧠 AI Analysis")
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #00d4ff;">Reasoning</h4>
                <p>{prediction['reasoning']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚠️ Risk Factors")
            risk_factors_html = ""
            for factor in prediction['risk_factors']:
                risk_factors_html += f"<li style='margin: 0.5rem 0;'>{factor}</li>"
            
            st.markdown(f"""
            <div class="metric-card warning-card">
                <ul style="padding-left: 1.5rem;">
                    {risk_factors_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Portfolio optimization page
def show_portfolio_optimizer():
    """Portfolio optimization page - Professional portfolio analysis"""
    st.markdown(f'<h1 class="main-title">💼 {t("optimizer.title")}</h1>', unsafe_allow_html=True)
    
    # Add feature introduction
    st.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #f59e0b;">
        <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
        🎯 <strong>{t("optimizer.description")}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    data_service = st.session_state.data_service
    protocols = data_service.get_all_protocols_data()
    
    if not protocols:
        st.warning(f"⚠️ {t('dashboard.messages.no_data_from_dashboard')}")
        return
    
    # Investment parameter settings
    st.markdown(f"### 🎛️ {t('optimizer.parameters.title')}")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        investment_amount = st.number_input(
            "💰 Investment Amount ($)",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=5000,
            format="%d"
        )
    
    with col2:
        risk_tolerance = st.select_slider(
            "⚖️ Risk Tolerance",
            options=["Conservative", "Moderate", "Aggressive"],
            value="Moderate"
        )
    
    with col3:
        optimization_goal = st.selectbox(
            "🎯 Optimization Goal",
            ["Max Return", "Min Risk", "Balanced", "Sharpe Ratio"]
        )
    
    # Optimization button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Optimize Portfolio", type="primary", use_container_width=True):
            with st.spinner("🧮 Optimizing your portfolio..."):
                risk_map = {"Conservative": "low", "Moderate": "medium", "Aggressive": "high"}
                optimization = run_async(data_service.optimize_portfolio(
                    investment_amount, 
                    risk_map[risk_tolerance]
                ))
                
                if optimization["success"]:
                    st.session_state.current_optimization = optimization
                    st.success("✅ Portfolio optimization completed!")
                else:
                    st.error(f"❌ Optimization failed: {optimization['error']}")
    
    # Display optimization results
    if hasattr(st.session_state, 'current_optimization') and st.session_state.current_optimization:
        optimization = st.session_state.current_optimization
        allocations = optimization["allocations"]
        metrics = optimization["portfolio_metrics"]
        
        # Portfolio metrics
        st.markdown(f"### 📊 {t('optimizer.results.title')}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card success-card">
                <div class="metric-label">Expected APY</div>
                <div class="big-metric">{metrics['weighted_apy']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Annual Return</div>
                <div class="big-metric">${metrics['expected_return']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            risk_color = "success-card" if metrics['weighted_risk'] < 0.4 else "warning-card" if metrics['weighted_risk'] < 0.7 else "danger-card"
            st.markdown(f"""
            <div class="metric-card {risk_color}">
                <div class="metric-label">Risk Score</div>
                <div class="big-metric">{metrics['weighted_risk']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="big-metric">{metrics['sharpe_ratio']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualization charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🥧 {t('optimizer.visualization.portfolio_allocation')}")
            
            # Create 3D pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=[a.protocol.title() for a in allocations],
                values=[a.allocation_percentage for a in allocations],
                hole=0.4,
                marker=dict(
                    colors=['#00d4ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'],
                    line=dict(color='#FFFFFF', width=2)
                ),
                textinfo='label+percent',
                textfont=dict(size=14, color='white'),
                hovertemplate='<b>%{label}</b><br>Allocation: %{percent}<br>Amount: $%{value:,.0f}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title={
                    'text': "Asset Allocation Distribution",
                    'x': 0.5,
                    'font': {'size': 20, 'color': 'white'}
                },
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "white"},
                showlegend=True,
                legend=dict(
                    bgcolor="rgba(255,255,255,0.1)",
                    bordercolor="rgba(255,255,255,0.2)",
                    borderwidth=1
                ),
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown(f"### 📊 {t('optimizer.visualization.investment_amounts')}")
            
            # Create bar chart
            fig_bar = go.Figure(data=[go.Bar(
                x=[a.protocol.title() for a in allocations],
                y=[a.allocation_amount for a in allocations],
                marker=dict(
                    color=['#00d4ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'],
                    line=dict(color='white', width=2)
                ),
                text=[f'${a.allocation_amount:,.0f}' for a in allocations],
                textposition='auto',
                textfont=dict(color='white', size=12),
                hovertemplate='<b>%{x}</b><br>Amount: $%{y:,.0f}<br>APY: %{customdata:.1f}%<extra></extra>',
                customdata=[a.expected_apy for a in allocations]
            )])
            
            fig_bar.update_layout(
                title={
                    'text': "Investment Amount by Protocol",
                    'x': 0.5,
                    'font': {'size': 20, 'color': 'white'}
                },
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "white"},
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    title=dict(text="Protocol", font=dict(color='white'))
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    title=dict(text="Investment Amount ($)", font=dict(color='white'))
                ),
                height=400
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Detailed allocation table
        st.markdown("### 📋 Detailed Allocation")
        
        df_allocation = pd.DataFrame([{
            'Protocol': a.protocol.title(),
            'Amount ($)': f"${a.allocation_amount:,.0f}",
            'Percentage (%)': f"{a.allocation_percentage:.1f}%",
            'Expected APY (%)': f"{a.expected_apy:.1f}%",
            'Risk Score': f"{a.risk_score:.2f}",
            'Annual Return': f"${a.allocation_amount * a.expected_apy / 100:,.0f}"
        } for a in allocations])
        
        st.dataframe(df_allocation, use_container_width=True, height=300)
        
        # Export functionality
        st.markdown(f"### 📥 {t('optimizer.export.title')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df_allocation.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"portfolio_allocation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_csv_portfolio"
            )
        
        with col2:
            # JSON export
            json_data = {
                'optimization_date': datetime.now().isoformat(),
                'investment_amount': investment_amount,
                'risk_tolerance': risk_tolerance,
                'portfolio_metrics': metrics,
                'allocations': [
                    {
                        'protocol': a.protocol,
                        'amount': a.allocation_amount,
                        'percentage': a.allocation_percentage,
                        'expected_apy': a.expected_apy,
                        'risk_score': a.risk_score
                    } for a in allocations
                ]
            }
            
            st.download_button(
                label="📋 Download JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"portfolio_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_json_portfolio"
            )
        
        with col3:
            # Generate report
            report_text = f"""
RWA Portfolio Optimization Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Investment Parameters:
- Amount: ${investment_amount:,}
- Risk Tolerance: {risk_tolerance}
- Optimization Goal: {optimization_goal}

Portfolio Metrics:
- Expected APY: {metrics['weighted_apy']:.2f}%
- Expected Annual Return: ${metrics['expected_return']:,.0f}
- Risk Score: {metrics['weighted_risk']:.3f}
- Sharpe Ratio: {metrics['sharpe_ratio']:.3f}
- Diversification Score: {metrics['diversification_score']}/10

Allocation Details:
"""
            for a in allocations:
                report_text += f"- {a.protocol.title()}: ${a.allocation_amount:,.0f} ({a.allocation_percentage:.1f}%) - {a.expected_apy:.1f}% APY\n"
            
            st.download_button(
                label="📊 Download Report",
                data=report_text,
                file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_txt_portfolio"
            )

# Protocol comparison page
def show_protocol_comparison():
    """Protocol comparison page - Professional comparative analysis"""
    st.markdown(f'<h1 class="main-title">📊 {t("comparison.title")}</h1>', unsafe_allow_html=True)
    
    # Add feature introduction
    st.markdown(f"""
    <div style="background: rgba(139, 92, 246, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #8b5cf6;">
        <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
        🔥 <strong>{t("comparison.description")}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add description text - Reference design
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;">
    In-depth analysis and comparison of different RWA protocols, evaluating their performance, security, and potential returns to make informed investment decisions.
    </p>
    """, unsafe_allow_html=True)
    
    data_service = st.session_state.data_service
    protocols = data_service.get_all_protocols_data()
    
    if not protocols:
        st.warning(f"⚠️ {t('dashboard.messages.no_data_from_dashboard')}")
        return
    
    # Protocol selection
    st.markdown(f"### 🎯 {t('comparison.selection.title')}")
    
    protocol_names = [p.protocol for p in protocols]
    selected_protocols = st.multiselect(
        "Choose protocols for comparison:",
        protocol_names,
        default=protocol_names[:3] if len(protocol_names) >= 3 else protocol_names,
        format_func=lambda x: x.title()
    )
    
    if len(selected_protocols) < 2:
        st.warning("⚠️ Please select at least 2 protocols for comparison.")
        return
    
    # Get data for selected protocols
    selected_data = {p.protocol: p for p in protocols if p.protocol in selected_protocols}
    
    # Create two-column layout - Reference design
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # AI Smart Investment Recommendations - 使用Streamlit原生组件
        try:
            st.markdown('<div class="metric-card" style="padding: 1.5rem; height: 500px; overflow-y: auto;">', unsafe_allow_html=True)
            
            st.markdown(f"### 💡 {t('comparison.recommendations.title')}")
            st.markdown(t('comparison.recommendations.description'))
            
            # 使用实际的协议数据来生成推荐
            if selected_data and len(selected_data) > 0:
                protocols_list = list(selected_data.keys())
                colors = ["#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]
                
                for i, protocol_name in enumerate(protocols_list[:5]):  # 最多显示5个协议
                    try:
                        protocol_data = selected_data[protocol_name]
                        color = colors[i % len(colors)]
                        
                        # 根据协议数据生成智能推荐
                        if protocol_data.current_apy > 10:
                            recommendation = f"offers high APY of {protocol_data.current_apy:.1f}%, suitable for growth-oriented investors."
                        elif protocol_data.risk_score < 0.3:
                            recommendation = f"has low risk score of {protocol_data.risk_score:.2f}, ideal for conservative investors."
                        elif protocol_data.tvl > 50000000:  # 50M+
                            recommendation = f"has strong TVL of ${protocol_data.tvl/1000000:.1f}M, indicating good market confidence."
                        else:
                            recommendation = f"provides balanced risk-return profile with {protocol_data.current_apy:.1f}% APY."
                        
                        # 使用更简单的HTML结构
                        st.markdown(f"""
                        <div style="margin: 1rem 0; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid {color};">
                            <strong style="color: {color}; font-size: 1.1rem;">{protocol_name.title()}</strong><br>
                            <span style="color: #e2e8f0; margin-top: 0.5rem; display: block;">{recommendation}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying recommendation for {protocol_name}: {str(e)}")
            else:
                st.info("👆 Please select at least 2 protocols above to see AI-powered investment recommendations.")
            
            # 使用Streamlit按钮而不是HTML按钮
            if st.button("📊 View More Details", key="view_details_btn", use_container_width=True):
                st.info("Detailed analysis coming soon!")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error rendering recommendations: {str(e)}")
            st.markdown(f"### 💡 {t('comparison.recommendations.title')}")
            st.info("Recommendations will appear here once protocols are selected.")
    
    with col2:
        # Multi-Dimensional Protocol Scoring Heatmap - Reference design right side
        st.markdown(f"### {t('comparison.heatmap.title')}")
        st.markdown('<p style="color: #94a3b8; margin-bottom: 1rem;">Visualize protocol performance through key indicators.</p>', unsafe_allow_html=True)
    
        # 使用实际选中的协议数据创建热力图
        if selected_data and len(selected_data) > 0:
            protocols_list = [p.title() for p in selected_data.keys()]
            metrics = ['APY Score', 'Safety Score', 'TVL Score', 'Liquidity', 'Risk-Adj Return', 'Market Cap']
            
            # 基于实际数据计算评分 (0-100)
            scores = []
            for protocol_name, protocol_data in selected_data.items():
                # 计算各项评分
                apy_score = min(protocol_data.current_apy * 5, 100)  # APY * 5 作为评分
                safety_score = (1 - protocol_data.risk_score) * 100  # 风险越低安全性越高
                tvl_score = min(protocol_data.tvl / 1000000, 100)  # TVL/1M 作为评分
                liquidity_score = 80 if protocol_data.lock_period == "flexible" else 50
                risk_adj_score = min(protocol_data.current_apy / (1 + protocol_data.risk_score) * 8, 100)
                market_cap_score = min(protocol_data.tvl / 500000, 100)  # TVL/500K 作为市值评分
                
                scores.append([
                    round(apy_score), 
                    round(safety_score), 
                    round(tvl_score), 
                    round(liquidity_score), 
                    round(risk_adj_score), 
                    round(market_cap_score)
                ])
        else:
            # 如果没有选中协议，显示示例数据
            protocols_list = ['Select Protocols', 'To View', 'Heatmap Data']
            metrics = ['APY', 'Safety', 'TVL', 'Liquidity', 'Risk-Adj', 'Market Cap']
            scores = [[50, 50, 50, 50, 50, 50] for _ in protocols_list]
        
        # Create heatmap
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=scores,
            x=metrics,
            y=protocols_list,
            colorscale=[
                [0, '#ef4444'],      # Red - Low score
                [0.3, '#f59e0b'],    # Orange - Medium-low score
                [0.5, '#eab308'],    # Yellow - Medium score
                [0.7, '#22c55e'],    # Green - Medium-high score
                [1, '#10b981']       # Dark green - High score
            ],
            text=[[f'{score}' for score in row] for row in scores],
            texttemplate="%{text}",
            textfont={"size": 12, "color": "white"},
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>%{x}: %{z}<extra></extra>'
        ))
        
        fig_heatmap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(37, 42, 58, 0.8)",
            font={'color': "#e2e8f0", 'family': "Inter"},
            height=400,
            margin=dict(l=100, r=40, t=40, b=80),
            xaxis=dict(
                tickangle=0,
                tickfont=dict(color='#e2e8f0', size=12)
            ),
            yaxis=dict(
                tickfont=dict(color='#e2e8f0', size=12)
            )
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Key Performance Indicators Radar Chart - Reference design bottom
    st.markdown(f"### {t('comparison.radar.title')}")
    st.markdown('<p style="color: #94a3b8; margin-bottom: 1rem;">Compare comprehensive performance indicators of selected protocols.</p>', unsafe_allow_html=True)
    
    # Create radar chart
    categories = ['APY Score', 'Safety Score', 'Liquidity Score', 'Yield Stability', 'Market Cap Score']
    
    fig_radar = go.Figure()
    
    colors = ['#00d4ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    
    for i, protocol_name in enumerate(selected_protocols):
        protocol_data = selected_data[protocol_name]
        
        # Calculate various scores (0-10 scale)
        apy_score = min(protocol_data.current_apy / 2, 10)  # APY/2 as score
        safety_score = (1 - protocol_data.risk_score) * 10  # Lower risk = higher safety
        liquidity_score = 8 if protocol_data.lock_period == "flexible" else 5
        stability_score = 7 + np.random.normal(0, 1)  # Simulate stability score
        market_cap_score = min(protocol_data.tvl / 10000000, 10)  # TVL/10M as market cap score
        
        values = [apy_score, safety_score, liquidity_score, stability_score, market_cap_score]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=protocol_name.title(),
            line=dict(color=colors[i % len(colors)], width=3),
            fillcolor=hex_to_rgba(colors[i % len(colors)], 0.2)
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                gridcolor='rgba(255,255,255,0.2)',
                tickcolor='white'
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',
                tickcolor='white'
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        title={
            'text': "Protocol Performance Radar",
            'x': 0.5,
            'font': {'size': 24, 'color': 'white'}
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        legend=dict(
            bgcolor="rgba(255,255,255,0.1)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1
        ),
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed comparison table
    st.markdown(f"### 📊 {t('comparison.table.title')}")
    
    comparison_data = []
    for protocol_name in selected_protocols:
        protocol_data = selected_data[protocol_name]
        comparison_data.append({
            t('comparison.table.protocol'): protocol_name.title(),
            t('comparison.table.apy'): f"{protocol_data.current_apy:.2f}%",
            t('comparison.table.risk_score'): f"{protocol_data.risk_score:.3f}",
            'Risk Level': 'Low' if protocol_data.risk_score < 0.4 else 'Medium' if protocol_data.risk_score < 0.7 else 'High',
            t('comparison.table.asset_type'): protocol_data.asset_type,
            t('comparison.table.tvl'): f"${protocol_data.tvl/1000000:.1f}M",
            t('comparison.table.active_pools'): protocol_data.active_pools,
            t('comparison.table.min_investment'): f"${protocol_data.min_investment:,.0f}",
            t('comparison.table.lock_period'): protocol_data.lock_period,
            'Risk-Adj APY': f"{protocol_data.current_apy/(1+protocol_data.risk_score):.2f}%"
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, height=400)
    
    # Investment recommendations
    st.markdown(f"### 💡 {t('comparison.recommendations_section.title')}")
    
    # Find best protocols
    best_apy = max(selected_data.values(), key=lambda x: x.current_apy)
    safest = min(selected_data.values(), key=lambda x: x.risk_score)
    highest_tvl = max(selected_data.values(), key=lambda x: x.tvl)
    best_risk_adj = max(selected_data.values(), key=lambda x: x.current_apy/(1+x.risk_score))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card success-card">
            <h4 style="color: #4caf50;">🏆 Best Performers</h4>
            <p><strong>Highest APY:</strong> {best_apy.protocol.title()} ({best_apy.current_apy:.1f}%)</p>
            <p><strong>Safest Option:</strong> {safest.protocol.title()} (Risk: {safest.risk_score:.2f})</p>
            <p><strong>Largest TVL:</strong> {highest_tvl.protocol.title()} (${highest_tvl.tvl/1000000:.1f}M)</p>
            <p><strong>Best Risk-Adjusted:</strong> {best_risk_adj.protocol.title()} ({best_risk_adj.current_apy/(1+best_risk_adj.risk_score):.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #00d4ff;">📈 Portfolio Suggestions</h4>
            <p><strong>Conservative:</strong> Focus on {safest.protocol.title()} (60-70%)</p>
            <p><strong>Balanced:</strong> Mix {best_risk_adj.protocol.title()} (40%) + {safest.protocol.title()} (30%)</p>
            <p><strong>Aggressive:</strong> Emphasize {best_apy.protocol.title()} (50-60%)</p>
            <p><strong>Diversified:</strong> Equal weights across all selected protocols</p>
        </div>
        """, unsafe_allow_html=True)

# Settings page
def show_settings():
    """Settings page"""
    st.markdown(f'<h1 class="main-title">⚙️ {t("settings.title")}</h1>', unsafe_allow_html=True)
    
    # 添加功能介绍
    st.markdown(f"""
    <div style="background: rgba(107, 114, 128, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #6b7280;">
        <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">
        🔑 <strong>{t("settings.description")}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    data_service = st.session_state.data_service
    
    # API configuration
    st.markdown(f"### 🔑 {t('settings.api.title')}")
    
    with st.form("api_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            openai_key = st.text_input(
                t('settings.api.openrouter_key'),
                value=data_service.get_user_setting("openai_api_key", ""),
                type="password",
                help="Your OpenRouter API key for AI predictions"
            )
        
        with col2:
            anthropic_key = st.text_input(
                t('settings.api.anthropic_key'),
                value=data_service.get_user_setting("anthropic_api_key", ""),
                type="password",
                help="Your Anthropic API key (optional)"
            )
        
        if st.form_submit_button(f"💾 {t('settings.api.save_keys')}", type="primary"):
            if openai_key:
                data_service.save_user_setting("openai_api_key", openai_key)
                os.environ['OPENAI_API_KEY'] = openai_key
            if anthropic_key:
                data_service.save_user_setting("anthropic_api_key", anthropic_key)
                os.environ['ANTHROPIC_API_KEY'] = anthropic_key
            
            st.success(f"✅ {t('settings.messages.keys_saved')}")
    
    # Application settings
    st.markdown(f"### 🎛️ {t('settings.application.title')}")
    
    with st.form("app_settings"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            auto_refresh = st.checkbox(
                f"🔄 {t('settings.application.auto_refresh')}",
                value=data_service.get_user_setting("auto_refresh", "false") == "true"
            )
            
            refresh_interval = st.selectbox(
                f"⏰ {t('settings.application.refresh_interval')}",
                [1, 5, 10, 15, 30, 60],
                index=2
            )
        
        with col2:
            theme = st.selectbox(
                f"🎨 {t('settings.application.theme')}",
                ["Dark (Recommended)", "Light"],
                index=0
            )
            
            chart_style = st.selectbox(
                "📊 Chart Style",
                ["Modern", "Classic", "Minimal"],
                index=0
            )
        
        with col3:
            # Language selector
            i18n = get_i18n()
            st.markdown(f"**🌐 {t('settings.application.language')}**")
            i18n.create_language_selector("settings_language")
        
        if st.form_submit_button(f"💾 {t('settings.application.save_settings')}", type="primary"):
            data_service.save_user_setting("auto_refresh", str(auto_refresh).lower())
            data_service.save_user_setting("refresh_interval", str(refresh_interval))
            data_service.save_user_setting("theme", theme)
            data_service.save_user_setting("chart_style", chart_style)
            st.success(f"✅ {t('settings.messages.settings_saved')}")
    
    # Data management
    st.markdown("### 🗄️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clean Old Data", help="Remove data older than 90 days"):
            data_service.cleanup_old_data()
            st.success("✅ Old data cleaned successfully!")
    
    with col2:
        if st.button("📊 Database Stats", help="Show database statistics"):
            protocols = data_service.get_all_protocols_data()
            st.info(f"📈 {len(protocols)} protocols in database")
    
    with col3:
        if st.button("🔄 Reset All Data", help="Reset all data (cannot be undone)"):
            st.warning("⚠️ This action cannot be undone!")

# Main application
def main():
    """Main application"""
    init_session_state()
    
    # Sidebar navigation - using streamlit-option-menu
    with st.sidebar:
        st.markdown('<h2 style="color: #00d4ff; text-align: center;">🚀 RWA Optimizer Pro</h2>', unsafe_allow_html=True)
        
        # Get navigation options based on current language
        nav_options = [
            t('navigation.dashboard'),
            t('navigation.predictions'), 
            t('navigation.optimizer'),
            t('navigation.comparison'),
            t('navigation.settings')
        ]
        
        selected = option_menu(
            menu_title=None,
            options=nav_options,
            icons=["speedometer2", "robot", "pie-chart", "bar-chart", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "transparent",
                    "border-radius": "10px"
                },
                "icon": {
                    "color": "#00d4ff", 
                    "font-size": "18px"
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px 0",
                    "padding": "12px 15px",
                    "background-color": "rgba(26, 26, 46, 0.8)",
                    "color": "#ffffff",
                    "border-radius": "10px",
                    "border": "1px solid rgba(255, 255, 255, 0.1)",
                    "transition": "all 0.3s ease"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(45deg, rgba(0, 212, 255, 0.4), rgba(78, 205, 196, 0.4))",
                    "border-left": "4px solid #00d4ff",
                    "color": "#ffffff",
                    "font-weight": "bold",
                    "box-shadow": "0 4px 15px rgba(0, 212, 255, 0.3)"
                },
            }
        )
        
        # Status information
        st.markdown("---")
        st.markdown(f"### 📡 {t('settings.system.title')}")
        
        if st.session_state.last_refresh:
            status_color = "status-online"
            status_text = t('settings.system.status_online')
            last_update = st.session_state.last_refresh.strftime('%H:%M:%S')
        else:
            status_color = "status-warning"
            status_text = t('settings.system.status_waiting')
            last_update = t('dashboard.messages.never_updated')
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div class="status-indicator {status_color}"></div>
            <span style="color: white;">{status_text}</span>
        </div>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{t('settings.system.last_update')}: {last_update}</p>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown(f"### ⚡ {t('settings.system.quick_actions')}")
        if st.button(f"🔄 {t('settings.system.quick_refresh')}", use_container_width=True):
            with st.spinner("Refreshing..."):
                data_service = st.session_state.data_service
                results = run_async(data_service.refresh_protocol_data())
                if "error" not in results:
                    st.success("✅ Refreshed!")
                    st.session_state.last_refresh = datetime.now()
                    time.sleep(1)
                    st.rerun()
    
    # Display page based on selection
    if selected == t('navigation.dashboard'):
        show_realtime_dashboard()
    elif selected == t('navigation.predictions'):
        show_ai_predictions()
    elif selected == t('navigation.optimizer'):
        show_portfolio_optimizer()
    elif selected == t('navigation.comparison'):
        show_protocol_comparison()
    elif selected == t('navigation.settings'):
        show_settings()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: rgba(255,255,255,0.6); padding: 20px;'>
            <p>🚀 RWA Yield Optimizer Pro | Built with Streamlit & ❤️</p>
            <p>Session: {st.session_state.data_service.session_id[:8]}... | 
            Version: 2.0 Enhanced | 
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()