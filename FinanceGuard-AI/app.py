import streamlit as st
import tabulate  # ensure this is installed
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from voice_assistant import VoiceAssistant, create_voice_enabled_interface

# Import original modules
from data_processor import (
    load_and_process_data,
    get_key_metrics,
    get_branch_analytics,
    get_time_patterns,
    detect_anomalies
)
from ai_agent import FinancialAnalysisAgent
from visualizations import (
    create_failure_heatmap,
    create_daily_trends,
    create_branch_performance,
    create_financial_impact,
    create_time_analysis,
    create_risk_matrix
)

# Import advanced modules
from enhanced_ai_agent import SuperFinancialAgent
from advanced_features import PredictiveFailurePreventor, SmartTransactionRouter, AnomalyDNASystem
from advanced_visualizations import (
    create_real_time_risk_radar,
    create_predictive_timeline,
    create_anomaly_dna_visualization,
    create_branch_risk_heatmap,
    create_financial_impact_gauge
)
from gamification import BranchGamification

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FinanceGuard AI - Retail Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "FinanceGuard AI - Advanced Hackathon Solution"}
)

# Enhanced CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3d59 0%, #2e5266 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 0.5rem 0; }
    .insight-box { background-color: #e8f5e9; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 5px solid #4caf50; }
    .achievement-card { background: linear-gradient(45deg, #FFD700 0%, #FFA500 100%); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; color: #fff; font-weight: bold; }
    .risk-high { background-color: #ffebee; border-left: 5px solid #f44336; }
    .risk-medium { background-color: #fff3e0; border-left: 5px solid #ff9800; }
    .risk-low { background-color: #e8f5e9; border-left: 5px solid #4caf50; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 24px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
for key in ('chat_history', 'alerts', 'achievements'):
    if key not in st.session_state:
        st.session_state[key] = []

# Load data with fallback options
@st.cache_data
def load_data():
    primary = r'C:\Users\abdal\Downloads\jordan_transactions.csv'
    fallbacks = [
        'jordan_transactions.csv',
        'data/jordan_transactions.csv',
        os.path.join(os.path.expanduser('~'), 'Downloads', 'jordan_transactions.csv')
    ]
    for path in [primary] + fallbacks:
        if os.path.exists(path):
            try:
                return load_and_process_data(path)
            except Exception as e:
                st.error(f"Error loading from {path}: {e}")
    st.warning("jordan_transactions.csv not found.")
    if st.button("Generate Sample Data"):
        import generate_sample_data
        df = generate_sample_data.generate_sample_transactions("jordan_transactions.csv", 5000)
        st.success("Sample data generated—refresh!")
        return load_and_process_data("jordan_transactions.csv")
    st.info("Place your file in one of these paths:")
    st.code(primary)
    for p in fallbacks:
        st.code(p)
    st.stop()

df = load_data()
metrics = get_key_metrics(df)
anomalies = detect_anomalies(df)

# Check OpenAI key
if not os.getenv("OPENAI_API_KEY"):
    st.warning("\u26a0\ufe0f OPENAI_API_KEY not set—AI features disabled.")

# Initialize AI agents and advanced features
@st.cache_resource
def get_agents(df):
    try:
        return {
            'standard': FinancialAnalysisAgent(df),
            'super': SuperFinancialAgent(df)
        }
    except Exception as e:
        st.error(f"Error initializing AI agents: {e}")
        return None

agents = get_agents(df) if os.getenv("OPENAI_API_KEY") else None
agent = agents['standard'] if agents else None
super_agent = agents.get('super') if agents else None

@st.cache_resource
def init_features(df):
    return {
        'pfp': PredictiveFailurePreventor(df),
        'router': SmartTransactionRouter(df),
        'dna': AnomalyDNASystem(df),
        'gamification': BranchGamification(df)
    }

features = init_features(df)

# Header
st.markdown('<h1 class="main-header">FinanceGuard AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;font-size:1.3rem;color:#5a6c7d;">Advanced Retail Financial Intelligence & Automation Platform</p>', unsafe_allow_html=True)

# The rest of the app code continues unchanged...
# (tabs, dashboards, assistants, charts, etc.)

# Top metrics bar
cols = st.columns(5)
with cols[0]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Transactions", f"{metrics['total_transactions']:,}", f"{metrics['failed_transactions']} failed")
    st.markdown('</div>', unsafe_allow_html=True)
with cols[1]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    rate = metrics['failure_rate']
    st.metric("Failure Rate", f"{rate:.1f}%", "Above threshold" if rate > 10 else "Normal",
              delta_color="inverse" if rate > 10 else "normal")
    st.markdown('</div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Revenue Impact", f"${metrics['failed_amount']:,.2f}",
              f"-{metrics['failed_amount'] / metrics['total_amount'] * 100:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)
with cols[3]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Active Alerts", len(anomalies),
              "Critical" if any(a['severity'] == 'high' for a in anomalies) else "Normal",
              delta_color="inverse" if anomalies else "normal")
    st.markdown('</div>', unsafe_allow_html=True)
with cols[4]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    curr = features['pfp'].calculate_pfp_score({
        'hour': datetime.now().hour,
        'branch': df['branch_name'].iloc[0],
        'amount': metrics['avg_transaction']
    })
    st.metric("Real-time Risk Score", f"{curr['score']:.2f}", curr['risk_level'])
    st.markdown('</div>', unsafe_allow_html=True)

# Tabs (without Workflow or Voice)
tabs = st.tabs([
    "🤖 AI Assistant",
    "📊 Analytics Dashboard",
    "⚡ Real-time Monitoring",
    "💡 Smart Insights",
    "🚀 Advanced AI",
    "🏆 Gamification",
    "🎤 Voice Assistant"  # New tab
])
# Tab 1: AI Assistant
# Tab 1: AI Assistant
with tabs[0]:
    st.header("AI-Powered Financial Assistant / المساعد المالي المدعوم بالذكاء الاصطناعي")
    
    if not agent:
        st.warning("AI features disabled. / ميزات الذكاء الاصطناعي معطلة")
    else:
        # Language selection
        input_language = st.radio(
            "Choose input language / اختر لغة الإدخال",
            options=['English', 'العربية'],
            horizontal=True
        )
        
        c1, c2 = st.columns([3, 1])
        with c1:
            if input_language == 'العربية':
                user_q = st.text_input(
                    "اسأل عن بياناتك:", 
                    placeholder="مثال: لماذا يفشل فرع المركز؟", 
                    key="q1_ar"
                )
            else:
                user_q = st.text_input(
                    "Ask about your data:", 
                    placeholder="e.g. Why is Mall C failing?", 
                    key="q1_en"
                )
            
            adv = st.checkbox("Use Advanced AI / استخدم الذكاء الاصطناعي المتقدم", value=False)
        
        with c2:
            if input_language == 'العربية':
                st.write("**أسئلة سريعة:**")
                if st.button("🔍 تحليل الفشل", key="qa1_ar"):
                    user_q = "حلل نمط المعاملات الفاشلة"
                if st.button("📊 أداء الفروع", key="qa2_ar"):
                    user_q = "قارن الأداء عبر جميع الفروع"
                if st.button("💰 تأثير الإيرادات", key="qa3_ar"):
                    user_q = "ما هو تأثير المعاملات الفاشلة على الإيرادات"
                if st.button("🔮 توقع المخاطر", key="qa4_ar"):
                    user_q = "توقع مخاطر الفروع خلال 24 ساعة القادمة"
            else:
                st.write("**Quick Questions:**")
                if st.button("🔍 Failure Analysis", key="qa1_en"):
                    user_q = "Analyze failed transactions pattern"
                if st.button("📊 Branch Performance", key="qa2_en"):
                    user_q = "Compare performance across branches"
                if st.button("💰 Revenue Impact", key="qa3_en"):
                    user_q = "Revenue impact of failed transactions"
                if st.button("🔮 Predict Risks", key="qa4_en"):
                    user_q = "Predict branch risk next 24h"
        
        if user_q:
            with st.spinner("🧠 Working... / جاري العمل..."):
                # If input is in Arabic, translate to English for processing
                if input_language == 'العربية':
                    try:
                        # Import translator
                        from deep_translator import GoogleTranslator
                        translator = GoogleTranslator(source='ar', target='en')
                        english_query = translator.translate(user_q)
                        st.info(f"Translated query / الاستعلام المترجم: {english_query}")
                    except Exception as e:
                        st.error(f"Translation error / خطأ في الترجمة: {e}")
                        english_query = user_q
                else:
                    english_query = user_q
                
                # Process the query
                res = super_agent.analyze_with_prediction(english_query) if adv and super_agent else agent.query(english_query)
                
                if res.get('success'):
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    
                    # If Arabic input, translate response back to Arabic
                    if input_language == 'العربية':
                        try:
                            translator = GoogleTranslator(source='en', target='ar')
                            arabic_response = translator.translate(res['response'])
                            st.write("**الإجابة:**")
                            st.write(arabic_response)
                            st.write("**English Response:**")
                            st.write(res['response'])
                        except Exception as e:
                            st.error(f"Translation error / خطأ في الترجمة: {e}")
                            st.write(res['response'])
                    else:
                        st.write(res['response'])
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Update chat history
                    st.session_state.chat_history.append({
                        'q': user_q,
                        'a': res['response'],
                        't': datetime.now().strftime("%H:%M:%S"),
                        'lang': input_language
                    })
                else:
                    st.error(res.get('error', 'Unknown error / خطأ غير معروف'))
    
    if st.session_state.chat_history:
        st.subheader("Conversation History / سجل المحادثة")
        for item in reversed(st.session_state.chat_history[-5:]):
            lang_emoji = "🇸🇦" if item.get('lang') == 'العربية' else "🇺🇸"
            with st.expander(f"[{item['t']}] {lang_emoji} {item['q'][:50]}..."):
                st.write(f"**Q:** {item['q']}")
                st.write(f"**A:** {item['a']}")

# Tab 2: Analytics Dashboard
with tabs[1]:
    st.header("Analytics Dashboard")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.plotly_chart(create_failure_heatmap(df), use_container_width=True)
    with r1c2:
        st.plotly_chart(create_branch_performance(df), use_container_width=True)
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.plotly_chart(create_daily_trends(df), use_container_width=True)
    with r2c2:
        st.plotly_chart(create_financial_impact(df), use_container_width=True)
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        st.plotly_chart(create_time_analysis(df), use_container_width=True)
    with r3c2:
        st.plotly_chart(create_risk_matrix(df), use_container_width=True)

# Tab 3: Real-time Monitoring
with tabs[2]:
    st.header("Real-time Monitoring")
    if st.button("🔄 Refresh"):
        st.experimental_rerun()
    if st.checkbox("Auto-refresh every 30 seconds"):
        time.sleep(30)
        st.experimental_rerun()
    st.subheader("🎯 Real-time Risk Radar")
    st.plotly_chart(create_real_time_risk_radar(df), use_container_width=True)
    cols_rt = st.columns(4)
    hr = datetime.now().hour
    hr_df = df[df['hour'] == hr]
    prev_df = df[df['hour'] == (hr - 1) % 24]
    with cols_rt[0]:
        st.metric("Transactions", len(hr_df), f"{len(hr_df) - len(prev_df)} vs last")
    with cols_rt[1]:
        failures = hr_df['is_failed'].sum()
        st.metric("Failures", failures, f"{failures - prev_df['is_failed'].sum()} vs last")
    with cols_rt[2]:
        rate = hr_df['is_failed'].mean() * 100 if len(hr_df) else 0
        prev_rate = prev_df['is_failed'].mean() * 100 if len(prev_df) else 0
        st.metric("Fail Rate", f"{rate:.1f}%", f"{rate - prev_rate:.1f}% vs last")
    with cols_rt[3]:
        sc = features['pfp'].calculate_pfp_score({
            'hour': hr,
            'branch': df['branch_name'].mode()[0],
            'amount': df['transaction_amount'].mean()
        })
        st.metric("Risk Score", f"{sc['score']:.2f}", sc['risk_level'])
    st.subheader("📡 Live Activity Feed")
    feed = []
    for i in range(10):
        t = df.sample(1).iloc[0]
        feed.append({
            'Time': (datetime.now() - timedelta(minutes=i)).strftime("%H:%M:%S"),
            'Branch': t['branch_name'],
            'Amount': f"${t['transaction_amount']:.2f}",
            'Status': '✅' if not t['is_failed'] else '❌',
            'Risk': np.random.choice(['Low', 'Med', 'High'])
        })
    st.dataframe(pd.DataFrame(feed), use_container_width=True)
    st.subheader("🚨 Active Alerts & Anomalies")
    a1, a2 = st.columns(2)
    with a1:
        if anomalies:
            for an in anomalies[:5]:
                icon = "🔴" if an['severity'] == 'high' else "🟡"
                with st.expander(f"{icon} {an['type'].upper()}"):
                    st.write(an['message'])
                    if 'data' in an:
                        st.json(an['data'])
                    if st.button("Acknowledge", key=an['type']):
                        st.success("Acknowledged")
        else:
            st.success("✅ No active alerts")
    with a2:
        st.write("**System Health**")
        health = {
            'Payment Gateway': '🟢 Operational' if metrics['failure_rate'] < 15 else '🔴 Issues Detected',
            'Database': '🟢 Healthy',
            'API Response': '🟢 < 200ms',
            'CPU Usage': '🟡 65%',
            'Memory': '🟢 4.2GB / 8GB'
        }
        for component, status in health.items():
            st.write(f"{component}: {status}")
    st.subheader("🏢 Branch Performance Monitor")
    sel = st.selectbox("Select Branch", df['branch_name'].unique())
    bd = df[df['branch_name'] == sel]
    b1, b2, b3 = st.columns(3)
    with b1:
        st.metric("Transactions", len(bd), f"{len(bd)/len(df)*100:.1f}% of total")
    with b2:
        fr = bd['is_failed'].mean() * 100
        st.metric("Fail Rate", f"{fr:.1f}%", f"{fr - metrics['failure_rate']:.1f}% vs avg")
    with b3:
        rs = features['pfp'].calculate_pfp_score({
            'branch': sel,
            'hour': hr,
            'amount': bd['transaction_amount'].mean()
        })
        st.metric("Risk Score", f"{rs['score']:.2f}", rs['risk_level'])
    hbd = bd.groupby('hour').agg({'is_failed': ['count', 'sum', 'mean']})
    hbd.columns = ['total', 'failed', 'failure_rate']
    hbd['failure_rate'] *= 100
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hbd.index, y=hbd['total'], name='Transactions'))
    fig.add_trace(go.Scatter(x=hbd.index, y=hbd['failure_rate'], name='% Fail', yaxis='y2', mode='lines+markers'))
    fig.update_layout(
        title=f"{sel} - Hourly Performance",
        xaxis_title="Hour",
        yaxis_title="Count",
        yaxis2=dict(title="% Fail", overlaying='y', side='right')
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Smart Insights & Intelligence
with tabs[3]:
    st.header("Smart Insights & Intelligence")
    insight_col1, insight_col2 = st.columns([2, 1])
    with insight_col1:
        st.subheader("🧠 AI-Generated Insights")
        insights = agent.get_smart_insights(df) if agent else []
        if insights:
            for i, ins in enumerate(insights):
                icon = "⚠️" if ins['type'] == 'warning' else "💡" if ins['type'] == 'insight' else "📊"
                with st.expander(f"{icon} {ins['title']}", expanded=(i == 0)):
                    st.write(ins['content'])
                    if ins.get('recommendation'):
                        st.info(f"**Recommendation:** {ins['recommendation']}")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("📊 Analyze Further", key=f"analyze_{i}"):
                        st.write("Launching deep analysis...")
                    if c2.button("📧 Share Insight", key=f"share_{i}"):
                        st.success("Insight shared")
                    if c3.button("🔄 Create Workflow", key=f"workflow_{i}"):
                        st.info("Workflow creation started")
        else:
            st.info("No insights available. Configure AI to get smart insights.")
    with insight_col2:
        st.subheader("📈 Trend Analysis")
        trends = {
            'Daily Trend': '📈 Improving' if df.groupby('date')['is_failed'].mean().iloc[-1] < df.groupby('date')['is_failed'].mean().iloc[-7] else '📉 Declining',
            'Weekly Pattern': '🔄 Cyclical',
            'Monthly Outlook': '⚡ Volatile'
        }
        for trend, status in trends.items():
            st.metric(trend, status)
    st.subheader("🔍 Pattern Recognition & Anomalies")
    p1, p2 = st.columns(2)
    with p1:
        sigs = features['dna'].dna_signatures
        st.plotly_chart(create_anomaly_dna_visualization(sigs), use_container_width=True)
    with p2:
        patterns = [
            {'pattern': 'Peak Hour Failures', 'description': 'Failures spike during 12-2 PM and 5-7 PM', 'impact': 'High', 'frequency': 'Daily'},
            {'pattern': 'Weekend Anomaly', 'description': 'Lower failure rates on weekends', 'impact': 'Medium', 'frequency': 'Weekly'},
            {'pattern': 'Branch Clustering', 'description': 'Similar branches show similar failure patterns', 'impact': 'Medium', 'frequency': 'Continuous'}
        ]
        for pat in patterns:
            with st.expander(f"🔍 {pat['pattern']}"):
                st.write(f"**Description:** {pat['description']}")
                st.write(f"**Impact:** {pat['impact']}")
                st.write(f"**Frequency:** {pat['frequency']}")
                if st.button(f"Investigate", key=f"investigate_{pat['pattern']}"):
                    st.write("Launching detailed investigation...")
    st.subheader("🔮 Predictive Analytics")
    pr1, pr2 = st.columns(2)
    preds = [metrics['failure_rate'] * (1 + np.sin(i / 3) / 5) for i in range(7)]
    with pr1:
        st.plotly_chart(create_predictive_timeline(df, preds), use_container_width=True)
    with pr2:
        st.write("**7-Day Forecast**")
        fc = pd.DataFrame({
            'Day': [f"Day {i+1}" for i in range(7)],
            'Predicted Rate': [f"{r:.1f}%" for r in preds],
            'Risk Level': ['High' if r > 20 else 'Medium' if r > 15 else 'Low' for r in preds]
        })
        st.dataframe(fc, use_container_width=True)
        st.metric("Prediction Confidence", "87%", "+2% from last week")
    st.subheader("💰 Business Impact Analysis")
    i1, i2, i3 = st.columns(3)
    with i1:
        imp = {
            'current': (metrics['failed_amount'] / metrics['total_amount']) * 100,
            'target': 5.0,
            'critical': 15.0
        }
        st.plotly_chart(create_financial_impact_gauge(imp), use_container_width=True)
    with i2:
        st.metric("Revenue at Risk", f"${metrics['failed_amount']:,.2f}", f"{imp['current']:.1f}% of total")
        st.metric("Monthly Projection", f"${metrics['failed_amount'] * 30:,.2f}", "Potential loss if unchanged")
    with i3:
        st.metric("Customer Impact", f"{metrics['failed_transactions']:,}", "Failed transactions")
        st.metric("Reputation Risk", "Medium", "Based on failure patterns")
    st.subheader("🎯 Smart Recommendations")
    recs = [
        {'priority': 'High', 'title': 'Implement Retry Mechanism', 'description': 'Add automatic retry for failed transactions during peak hours', 'impact': 'Could reduce failures by 30%', 'effort': 'Medium', 'roi': '$50,000/month'},
        {'priority': 'High', 'title': 'Scale Infrastructure', 'description': 'Increase server capacity during peak hours', 'impact': 'Reduce timeout failures by 40%', 'effort': 'High', 'roi': '$75,000/month'},
        {'priority': 'Medium', 'title': 'Optimize Database Queries', 'description': 'Improve query performance for high-volume branches', 'impact': 'Reduce latency by 25%', 'effort': 'Medium', 'roi': '$30,000/month'}
    ]
    for rec in recs:
        color_icon = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
        with st.expander(f"{color_icon} {rec['title']} - Priority: {rec['priority']}"):
            col_desc, col_action = st.columns([2, 1])
            with col_desc:
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Expected Impact:** {rec['impact']}")
                st.write(f"**Estimated ROI:** {rec['roi']}")
            with col_action:
                st.write(f"**Effort Required:** {rec['effort']}")
                if st.button("Implement", key=f"impl_{rec['title']}"):
                    st.success("Implementation task created")
                if st.button("Learn More", key=f"learn_{rec['title']}"):
                    st.info("Detailed analysis loading...")

# Tab 5: Advanced AI Features
# Tab 5: Advanced AI Features
with tabs[4]:
    st.header("🚀 Advanced AI Features")
    
    # Advanced AI Models
    st.subheader("🧩 Advanced AI Models")
    
    model_col1, model_col2 = st.columns(2)
    
    with model_col1:
        st.write("**Predictive Failure Prevention (PFP)**")
        
        # Test transaction for prediction
        test_transaction = {
            'branch': st.selectbox("Test Branch", df['branch_name'].unique()),
            'hour': st.slider("Hour of Day", 0, 23, 12),
            'amount': st.number_input("Transaction Amount", min_value=0.0, value=float(df['transaction_amount'].mean()))
        }
        
        if st.button("Predict Risk"):
            prediction = features['pfp'].calculate_pfp_score(test_transaction)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{prediction['score']:.2f}")
            with col2:
                st.metric("Risk Level", prediction['risk_level'])
            with col3:
                st.metric("Failure Probability", f"{prediction['failure_probability']*100:.1f}%")
            
            if prediction['recommendation']:
                st.info(f"**Recommendation:** {prediction['recommendation']}")
    
    with model_col2:
        st.write("**Smart Transaction Router**")
        
        active_routes = features['router'].smart_route(df.groupby('branch_name').agg({'is_failed': 'mean'}).to_dict()['is_failed'])
        
        st.write("Current Active Routes:")
        for branch, route_info in active_routes.items():
            status_color = "🟢" if route_info['status'] == "Normal" else "🟡"
            st.write(f"{status_color} **{branch}**: {route_info['status']}")
            if route_info['status'] != "Normal":
                st.write(f"   ↳ {route_info['recommendation']}")
    
    st.divider()
    
    # AI Insights
    st.subheader("🔍 Deep AI Insights")
    st.subheader("🔍 Deep AI Insights")

ai_insight_type = st.selectbox(
    "Select Analysis Type",
    ["Pattern Recognition", "Causal Analysis", "Impact Prediction", "Optimization Strategy"]
)

if ai_insight_type == "Pattern Recognition":
    if super_agent:
        patterns = super_agent.find_patterns(df)
        for pattern in patterns:
            with st.expander(f"📊 {pattern['name']}"):
                st.write(pattern['description'])
                if 'visual' in pattern and pattern['visual'] is not None:
                    st.plotly_chart(pattern['visual'], use_container_width=True)
    else:
        st.info("Configure AI to enable pattern recognition")

elif ai_insight_type == "Causal Analysis":
    if super_agent:
        causes = super_agent.analyze_root_causes(df)
        st.write("**Root Cause Analysis:**")
        for cause in causes:
            st.write(f"• {cause['factor']}: {cause['impact']}")
    else:
        st.info("Configure AI to enable causal analysis")

elif ai_insight_type == "Impact Prediction":
    future_days = st.slider("Predict for next (days):", 1, 30, 7)
    predictions = features['pfp'].predict_future_failures(df, days=future_days)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(future_days)), y=predictions,
                            mode='lines+markers', name='Predicted Failures'))
    fig.update_layout(title="Failure Rate Prediction",
                     xaxis_title="Days", yaxis_title="Failure Rate %")
    st.plotly_chart(fig, use_container_width=True)

elif ai_insight_type == "Optimization Strategy":
    if super_agent:
        strategy = super_agent.generate_optimization_strategy(df)
        st.write("**Recommended Optimization Strategy:**")
        for step in strategy:
            with st.expander(f"Step {step['priority']}: {step['action']}"):
                st.write(f"**Expected Outcome:** {step['expected_outcome']}")
                st.write(f"**Implementation Difficulty:** {step['difficulty']}")
    else:
        st.info("Configure AI to enable optimization strategies")
    st.divider()
    
    # Automation Controls
    st.subheader("⚡ Automation Controls")
    
    auto_col1, auto_col2 = st.columns(2)
    
    with auto_col1:
        st.write("**Automated Actions**")
        auto_retry = st.checkbox("Enable Auto-Retry for Failed Transactions", value=True)
        auto_route = st.checkbox("Enable Smart Transaction Routing", value=True)
        auto_alert = st.checkbox("Enable Smart Alert System", value=True)
        
        if st.button("Apply Automation Settings"):
            st.success("Automation settings updated!")
    
    with auto_col2:
        st.write("**Threshold Settings**")
        failure_threshold = st.slider("Failure Rate Alert Threshold (%)", 5, 25, 15)
        risk_threshold = st.slider("Risk Score Alert Threshold", 0.0, 10.0, 7.0)
        
        if st.button("Update Thresholds"):
            st.success("Thresholds updated!")
    
    st.divider()
    
    # Advanced Visualizations
    st.subheader("📊 Advanced Visualizations")
    
    viz_type = st.selectbox(
        "Select Visualization",
        ["Risk Radar", "Branch Risk Heatmap", "Anomaly DNA Map", "Financial Impact Gauge"]
    )
    
    if viz_type == "Risk Radar":
        st.plotly_chart(create_real_time_risk_radar(df), use_container_width=True)
    elif viz_type == "Branch Risk Heatmap":
        st.plotly_chart(create_branch_risk_heatmap(df), use_container_width=True)
    elif viz_type == "Anomaly DNA Map":
        sigs = features['dna'].dna_signatures
        st.plotly_chart(create_anomaly_dna_visualization(sigs), use_container_width=True)
    elif viz_type == "Financial Impact Gauge":
        impact_data = {
            'current': (metrics['failed_amount'] / metrics['total_amount']) * 100,
            'target': 5.0,
            'critical': 15.0
        }
        st.plotly_chart(create_financial_impact_gauge(impact_data), use_container_width=True)

# Tab 6: Branch Gamification System
with tabs[5]:
    st.header("🏆 Branch Gamification System")
    
    # Main leaderboard
    leaderboard = features['gamification'].get_leaderboard()
    
    st.subheader("🏅 Current Leaderboard")
    
    # Create leaderboard visualization
    fig = go.Figure(data=[
        go.Bar(
            y=leaderboard['branch_name'],
            x=leaderboard['total_points'],
            orientation='h',
            marker_color=['gold', 'silver', '#CD7F32', '#4A90E2', '#4A90E2']
        )
    ])
    
    fig.update_layout(
        title="Branch Performance Points",
        xaxis_title="Points",
        yaxis_title="Branch",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Branch details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_branch = st.selectbox("Select Branch Details", df['branch_name'].unique())
    
    with col2:
        branch_details = features['gamification'].get_branch_details(selected_branch)
        
        st.write(f"**{selected_branch} Performance**")
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("Current Level", f"Level {branch_details['level']}")
        with metric_cols[1]:
            st.metric("Total Points", f"{branch_details['total_points']:,}")
        with metric_cols[2]:
            st.metric("Current Streak", f"{branch_details['current_streak']} days")
        with metric_cols[3]:
            st.metric("Achievement Count", branch_details['achievement_count'])
    
    st.divider()
    
    # Achievements Section
    st.subheader("🎖️ Achievements & Badges")
    
    achievements = features['gamification'].check_achievements(selected_branch)
    
    if achievements:
        ach_cols = st.columns(3)
        for idx, achievement in enumerate(achievements):
            with ach_cols[idx % 3]:
                st.markdown(f"""
                <div class="achievement-card">
                    <h4>{achievement['badge']} {achievement['name']}</h4>
                    <p>{achievement['description']}</p>
                    <small>+{achievement['points']} points</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Performance Challenges
    st.subheader("🎯 Active Challenges")
    
    challenges = [
        {
            'name': 'Zero Failure Champion',
            'description': 'Achieve 0% failure rate for 24 hours',
            'reward': '500 points + Legendary Badge',
            'progress': 75,
            'deadline': '48 hours'
        },
        {
            'name': 'Peak Performance',
            'description': 'Maintain < 5% failure rate during peak hours',
            'reward': '300 points',
            'progress': 60,
            'deadline': '7 days'
        },
        {
            'name': 'Customer Satisfaction Hero',
            'description': 'Process 1000 successful transactions in a row',
            'reward': '400 points + Super Badge',
            'progress': 85,
            'deadline': '3 days'
        }
    ]
    
    for challenge in challenges:
        with st.expander(f"🎯 {challenge['name']} - {challenge['progress']}% Complete"):
            st.write(f"**Description:** {challenge['description']}")
            st.write(f"**Reward:** {challenge['reward']}")
            st.write(f"**Deadline:** {challenge['deadline']}")
            st.progress(challenge['progress'] / 100)
            
            if st.button(f"View Details", key=f"challenge_{challenge['name']}"):
                st.info("Detailed challenge metrics would appear here")
    
    st.divider()
    
    # Team Performance
    st.subheader("👥 Team Performance & Collaboration")
    
    team_col1, team_col2 = st.columns(2)
    
    with team_col1:
        st.write("**Top Performing Teams**")
        team_data = {
            'Team': ['North Region', 'South Region', 'Central Region', 'East Region'],
            'Points': [4500, 4200, 3800, 3600],
            'Average Failure Rate': ['8.2%', '9.1%', '10.5%', '11.3%']
        }
        st.dataframe(pd.DataFrame(team_data), use_container_width=True)
    
    with team_col2:
        st.write("**Collaboration Bonuses**")
        collab_bonuses = {
            'Cross-Branch Support': '+100 points',
            'Knowledge Sharing': '+50 points',
            'Best Practice Implementation': '+200 points',
            'Mentoring New Staff': '+150 points'
        }
        
        for bonus, points in collab_bonuses.items():
            st.write(f"• {bonus}: {points}")
    
    st.divider()
    
    # Rewards & Incentives
    st.subheader("🎁 Rewards & Incentives")
    
    reward_col1, reward_col2, reward_col3 = st.columns(3)
    
    with reward_col1:
        st.write("**Monthly Rewards**")
        monthly_rewards = {
            '1st Place': 'Employee of the Month + $500',
            '2nd Place': 'Gift Card + $300',
            '3rd Place': 'Extra Day Off + $200'
        }
        for place, reward in monthly_rewards.items():
            st.write(f"🏆 {place}: {reward}")
    
    with reward_col2:
        st.write("**Achievement Unlocks**")
        unlocks = {
            'Level 5': 'Premium Parking Spot',
            'Level 10': 'Executive Lunch Privileges',
            'Level 15': 'Work from Home Flexibility',
            'Level 20': 'Training Budget Increase'
        }
        for level, unlock in unlocks.items():
            st.write(f"🔓 {level}: {unlock}")
    
    with reward_col3:
        st.write("**Special Recognition**")
        special = {
            'Consistency Star': '30-day perfect record',
            'Innovation Award': 'Process improvement',
            'Customer Champion': 'Highest satisfaction',
            'Team Player': 'Best collaboration'
        }
        for award, criteria in special.items():
            st.write(f"⭐ {award}: {criteria}")
    
    st.divider()
    
    # Personal Dashboard
    st.subheader("📊 Personal Performance Dashboard")
    
    # Simulate personal metrics for demo
    personal_metrics = {
        'Your Points': 1250,
        'Your Level': 8,
        'Next Level': '250 points',
        'Global Rank': '#42 of 150',
        'Team Rank': '#5 of 25'
    }
    
    personal_cols = st.columns(5)
    for idx, (metric, value) in enumerate(personal_metrics.items()):
        with personal_cols[idx]:
            st.metric(metric, value)
    
    # Progress to next level
    st.write("**Progress to Next Level**")
    progress = (personal_metrics['Your Points'] % 500) / 500  # Assume 500 points per level
    st.progress(progress)
    st.write(f"{int(progress * 100)}% to Level {personal_metrics['Your Level'] + 1}")
    
    # Recent achievements
    st.write("**Your Recent Achievements**")
    recent_achievements = [
        {'name': 'Quick Resolver', 'date': 'Today', 'points': '+50'},
        {'name': '100 Streak', 'date': 'Yesterday', 'points': '+100'},
        {'name': 'Peak Performer', 'date': '2 days ago', 'points': '+75'}
    ]
    
    for ach in recent_achievements:
        st.write(f"🏅 {ach['name']} - {ach['date']} ({ach['points']} points)")
with tabs[6]:
    try:
        create_voice_enabled_interface(df)
    except ImportError as e:
        st.warning("Voice Assistant requires additional dependencies:")
        st.code("""
        pip install SpeechRecognition
        pip install pyttsx3
        pip install googletrans==4.0.0-rc1
        pip install pyaudio
        """)
        st.error(f"Import error: {e}")
        st.info("Please install the required packages and restart the application.")
    except Exception as e:
        st.error(f"Error initializing Voice Assistant: {e}")
        st.info("Voice Assistant may not be available on this system.")
# Sidebar
with st.sidebar:
    st.header("System Status")
    st.subheader("Data Source")
    st.info(f"Loaded {len(df):,} transactions")
    st.text(f"Date range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
    st.divider()
    st.header("Quick Actions")
    if st.button("🔄 Refresh Data"):
        st.experimental_rerun()
    st.divider()
    st.header("Settings")
    st.checkbox("Enable Notifications", value=True)
    st.checkbox("Auto-refresh Data", value=False)
    st.checkbox("Advanced Mode", value=True)
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888;'>"
        "FinanceGuard AI - Advanced Retail Intelligence Platform | © 2025"
        "</div>",
        unsafe_allow_html=True
    )
