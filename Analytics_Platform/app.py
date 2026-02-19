# """
# MCP Analytics Platform - Production-Ready Web UI
# Enterprise-grade interface with advanced features
# """
# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from improved_main import MCPAnalyticsPlatform
# import time
# from datetime import datetime
# import json

# # ==================== PAGE CONFIGURATION ====================
# st.set_page_config(
#     page_title="MCP Analytics - Banking Intelligence",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get Help': 'https://github.com/yourusername/mcp-analytics',
#         'Report a bug': 'https://github.com/yourusername/mcp-analytics/issues',
#         'About': '# MCP Analytics Platform\nAI-Powered Banking Analytics v1.0'
#     }
# )

# # ==================== CUSTOM CSS (PRODUCTION STYLING) ====================
# st.markdown("""
# <style>
#     /* Import Google Fonts */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
#     /* Global Styles */
#     * {
#         font-family: 'Inter', sans-serif;
#     }
    
#     /* Hide Streamlit Branding */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
    
#     /* Main Background */
#     .main {
#         background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
#     }
    
#     .block-container {
#         padding-top: 2rem;
#         padding-bottom: 2rem;
#     }
    
#     /* Header Card */
#     .header-card {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 2rem;
#         border-radius: 20px;
#         box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
#         margin-bottom: 2rem;
#         text-align: center;
#         animation: fadeInDown 0.8s ease-out;
#     }
    
#     .header-title {
#         color: white;
#         font-size: 3rem;
#         font-weight: 800;
#         margin: 0;
#         text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
#     }
    
#     .header-subtitle {
#         color: rgba(255,255,255,0.9);
#         font-size: 1.2rem;
#         margin-top: 0.5rem;
#         font-weight: 400;
#     }
    
#     /* Input Container */
#     .input-container {
#         background: white;
#         padding: 2rem;
#         border-radius: 20px;
#         box-shadow: 0 10px 40px rgba(0,0,0,0.1);
#         margin-bottom: 2rem;
#         animation: fadeInUp 0.8s ease-out;
#     }
    
#     /* UPDATED: Input Text - BLACK COLOR */
#     .stTextInput > div > div > input {
#         border-radius: 50px;
#         border: 2px solid #e0e0e0;
#         padding: 18px 25px;
#         font-size: 16px;
#         transition: all 0.3s;
#         background: #f8f9fa;
#         color: #000000 !important;
#         font-weight: 500;
#     }
    
#     .stTextInput > div > div > input::placeholder {
#         color: #999999 !important;
#         font-weight: 400;
#     }
    
#     .stTextInput > div > div > input:focus {
#         border-color: #667eea;
#         box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
#         background: white;
#         color: #000000 !important;
#     }
    
#     /* Buttons */
#     .stButton > button {
#         border-radius: 50px;
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         border: none;
#         padding: 15px 35px;
#         font-weight: 600;
#         font-size: 16px;
#         transition: all 0.3s;
#         box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
#     }
    
#     .stButton > button:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
#     }
    
#     .stButton > button:active {
#         transform: translateY(-1px);
#     }
    
#     /* Result Card */
#     .result-card {
#         background: white;
#         padding: 2.5rem;
#         border-radius: 20px;
#         box-shadow: 0 10px 40px rgba(0,0,0,0.1);
#         margin: 1.5rem 0;
#         animation: fadeInUp 0.6s ease-out;
#         border-left: 5px solid #667eea;
#     }
    
#     .result-value {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 3rem;
#         border-radius: 15px;
#         text-align: center;
#         margin: 1.5rem 0;
#         box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
#     }
    
#     .result-number {
#         font-size: 4rem;
#         font-weight: 800;
#         color: white;
#         text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
#         margin: 0;
#     }
    
#     .result-label {
#         color: rgba(255,255,255,0.9);
#         font-size: 1.1rem;
#         margin-top: 0.5rem;
#         font-weight: 500;
#     }
    
#     /* Metric Cards */
#     .metric-card {
#         background: white;
#         border-radius: 15px;
#         padding: 1.5rem;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.08);
#         transition: all 0.3s;
#         border-left: 4px solid #667eea;
#         margin: 0.5rem 0;
#     }
    
#     .metric-card:hover {
#         transform: translateY(-5px);
#         box-shadow: 0 8px 25px rgba(0,0,0,0.15);
#     }
    
#     .metric-value {
#         font-size: 2.5rem;
#         font-weight: 800;
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         margin: 0;
#     }
    
#     .metric-label {
#         color: #666;
#         font-size: 0.9rem;
#         margin-top: 0.5rem;
#         font-weight: 500;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#     }
    
#     /* Chat Messages */
#     .user-message {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         padding: 1.2rem 1.8rem;
#         border-radius: 20px 20px 5px 20px;
#         margin: 1rem 0;
#         box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
#         max-width: 80%;
#         animation: slideInRight 0.5s ease-out;
#     }
    
#     .bot-message {
#         background: white;
#         padding: 1.5rem 2rem;
#         border-radius: 20px 20px 20px 5px;
#         margin: 1rem 0;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.1);
#         border-left: 4px solid #667eea;
#         animation: slideInLeft 0.5s ease-out;
#     }
    
#     /* Sidebar */
#     .css-1d391kg, .css-1lcbmhc {
#         background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
#     }
    
#     .sidebar-card {
#         background: rgba(255,255,255,0.1);
#         backdrop-filter: blur(10px);
#         padding: 1.2rem;
#         border-radius: 15px;
#         margin: 1rem 0;
#         border: 1px solid rgba(255,255,255,0.2);
#         transition: all 0.3s;
#     }
    
#     .sidebar-card:hover {
#         background: rgba(255,255,255,0.15);
#         transform: translateX(5px);
#     }
    
#     .sidebar-title {
#         color: white;
#         font-weight: 600;
#         font-size: 1.1rem;
#         margin: 0;
#     }
    
#     .sidebar-text {
#         color: rgba(255,255,255,0.8);
#         font-size: 0.9rem;
#         margin: 0.5rem 0 0 0;
#     }
    
#     /* Example Queries */
#     .example-query {
#         background: rgba(255,255,255,0.95);
#         border-radius: 12px;
#         padding: 1rem 1.2rem;
#         margin: 0.6rem 0;
#         cursor: pointer;
#         transition: all 0.3s;
#         border-left: 3px solid #667eea;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#     }
    
#     .example-query:hover {
#         background: white;
#         transform: translateX(8px);
#         box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
#     }
    
#     /* Loading Animation */
#     .loading-container {
#         text-align: center;
#         padding: 3rem;
#     }
    
#     .loading-spinner {
#         border: 6px solid rgba(102, 126, 234, 0.1);
#         border-top: 6px solid #667eea;
#         border-radius: 50%;
#         width: 60px;
#         height: 60px;
#         animation: spin 1s linear infinite;
#         margin: 0 auto 1rem auto;
#     }
    
#     .loading-text {
#         color: #667eea;
#         font-weight: 600;
#         font-size: 1.1rem;
#         animation: pulse 1.5s ease-in-out infinite;
#     }
    
#     /* Animations */
#     @keyframes spin {
#         0% { transform: rotate(0deg); }
#         100% { transform: rotate(360deg); }
#     }
    
#     @keyframes pulse {
#         0%, 100% { opacity: 1; }
#         50% { opacity: 0.5; }
#     }
    
#     @keyframes fadeInDown {
#         from {
#             opacity: 0;
#             transform: translateY(-30px);
#         }
#         to {
#             opacity: 1;
#             transform: translateY(0);
#         }
#     }
    
#     @keyframes fadeInUp {
#         from {
#             opacity: 0;
#             transform: translateY(30px);
#         }
#         to {
#             opacity: 1;
#             transform: translateY(0);
#         }
#     }
    
#     @keyframes slideInRight {
#         from {
#             opacity: 0;
#             transform: translateX(50px);
#         }
#         to {
#             opacity: 1;
#             transform: translateX(0);
#         }
#     }
    
#     @keyframes slideInLeft {
#         from {
#             opacity: 0;
#             transform: translateX(-50px);
#         }
#         to {
#             opacity: 1;
#             transform: translateX(0);
#         }
#     }
    
#     /* Success/Error Alerts */
#     .success-alert {
#         background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
#         color: white;
#         padding: 1rem 1.5rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
#     }
    
#     .error-alert {
#         background: linear-gradient(135deg, #eb3941 0%, #f15e64 100%);
#         color: white;
#         padding: 1rem 1.5rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         box-shadow: 0 4px 15px rgba(235, 57, 65, 0.3);
#     }
    
#     /* Info Box */
#     .info-box {
#         background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
#         color: white;
#         padding: 1.2rem 1.5rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
#     }
    
#     /* Chart Container */
#     .chart-container {
#         background: white;
#         padding: 2rem;
#         border-radius: 15px;
#         box-shadow: 0 8px 30px rgba(0,0,0,0.1);
#         margin: 1.5rem 0;
#     }
    
#     /* Expander */
#     .streamlit-expanderHeader {
#         background: #f8f9fa;
#         border-radius: 10px;
#         font-weight: 600;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 1rem;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         background: rgba(255,255,255,0.1);
#         border-radius: 10px;
#         padding: 1rem 2rem;
#         color: white;
#         font-weight: 600;
#     }
    
#     .stTabs [aria-selected="true"] {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#     }
    
#     /* Download Button */
#     .stDownloadButton > button {
#         border-radius: 50px;
#         background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
#         color: white;
#         border: none;
#         padding: 12px 30px;
#         font-weight: 600;
#         box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
#     }
    
#     /* Footer */
#     .footer {
#         text-align: center;
#         padding: 2rem;
#         color: rgba(255,255,255,0.6);
#         margin-top: 3rem;
#         border-top: 1px solid rgba(255,255,255,0.1);
#     }
# </style>
# """, unsafe_allow_html=True)

# # ==================== INITIALIZE SESSION STATE ====================
# if 'platform' not in st.session_state:
#     with st.spinner('🚀 Initializing Analytics Platform...'):
#         try:
#             st.session_state.platform = MCPAnalyticsPlatform(use_local_llm=True)
#             st.session_state.chat_history = []
#             st.session_state.initialized = True
#         except Exception as e:
#             st.error(f"Failed to initialize platform: {str(e)}")
#             st.stop()

# # ==================== HEADER ====================
# st.markdown("""
# <div class='header-card'>
#     <h1 class='header-title'>📊 MCP Analytics Platform</h1>
#     <p class='header-subtitle'>Enterprise-Grade Banking Intelligence | AI-Powered Insights</p>
# </div>
# """, unsafe_allow_html=True)

# # ==================== SIDEBAR ====================
# with st.sidebar:
#     st.markdown("""
#     <div style='text-align: center; padding: 1.5rem 0;'>
#         <h2 style='color: white; font-weight: 800; margin: 0;'>⚡ Control Panel</h2>
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Dataset Info
#     st.markdown("<h3 style='color: white; margin-top: 1.5rem;'>📂 Datasets</h3>", unsafe_allow_html=True)
    
#     for name, df in st.session_state.platform.datasets.items():
#         st.markdown(f"""
#         <div class='sidebar-card'>
#             <h4 class='sidebar-title'>{name.upper()}</h4>
#             <p class='sidebar-text'>📊 {len(df):,} rows • {len(df.columns)} columns</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # Example Queries
#     st.markdown("<h3 style='color: white;'>💡 Quick Queries</h3>", unsafe_allow_html=True)
    
#     example_queries = {
#         "🏆 Top Performers": [
#             "Which branch has highest gold loan?",
#             "Which branch has highest NPA percent?",
#             "Which branch has lowest fraud rate?",
#         ],
#         "📈 Trends & Growth": [
#             "UPI volume trend over time",
#             "Customer growth over time",
#             "Gold loan growth rate",
#         ],
#         "🔍 Comparisons": [
#             "Compare all branches for gold loan",
#             "Gold loan and home loan comparison",
#             "Compare Mumbai Delhi Pune for UPI",
#         ],
#         "📊 Deep Insights": [
#             "Total gold loan in Mumbai",
#             "Which branch has highest gold loan and home loan?",
#             "Average credit score by branch",
#         ]
#     }
    
#     selected_category = st.selectbox(
#         "Select Category",
#         list(example_queries.keys()),
#         label_visibility="collapsed"
#     )
    
#     for query in example_queries[selected_category]:
#         if st.button(query, key=query, use_container_width=True):
#             st.session_state.current_query = query
#             st.rerun()
    
#     st.markdown("---")
    
#     # Stats
#     st.markdown("<h3 style='color: white;'>📊 Session Stats</h3>", unsafe_allow_html=True)
    
#     total_queries = len(st.session_state.chat_history)
#     successful_queries = sum(1 for chat in st.session_state.chat_history 
#                             if chat.get('response') and chat['response'].get('success'))
    
#     st.markdown(f"""
#     <div class='sidebar-card'>
#         <h4 class='sidebar-title'>{total_queries}</h4>
#         <p class='sidebar-text'>Total Queries</p>
#     </div>
#     <div class='sidebar-card'>
#         <h4 class='sidebar-title'>{successful_queries}</h4>
#         <p class='sidebar-text'>Successful</p>
#     </div>
#     <div class='sidebar-card'>
#         <h4 class='sidebar-title'>{total_queries - successful_queries}</h4>
#         <p class='sidebar-text'>Failed</p>
#     </div>
#     """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # Actions
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("🗑️ Clear", use_container_width=True):
#             st.session_state.chat_history = []
#             st.rerun()
#     with col2:
#         if st.button("💾 Export", use_container_width=True):
#             # Export chat history as JSON
#             if st.session_state.chat_history:
#                 export_data = [{
#                     'timestamp': chat['timestamp'].isoformat(),
#                     'query': chat['query'],
#                     'success': chat['response'].get('success') if chat.get('response') else False
#                 } for chat in st.session_state.chat_history]
                
#                 st.download_button(
#                     "📥 Download History",
#                     data=json.dumps(export_data, indent=2),
#                     file_name=f"analytics_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                     mime="application/json"
#                 )

# # ==================== MAIN CONTENT ====================

# # Quick Stats Dashboard
# col1, col2, col3, col4 = st.columns(4)

# total_rows = sum(len(df) for df in st.session_state.platform.datasets.values())
# total_datasets = len(st.session_state.platform.datasets)

# with col1:
#     st.markdown(f"""
#     <div class='metric-card'>
#         <div class='metric-value'>{total_datasets}</div>
#         <div class='metric-label'>Active Datasets</div>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown(f"""
#     <div class='metric-card'>
#         <div class='metric-value'>{total_rows:,}</div>
#         <div class='metric-label'>Total Records</div>
#     </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown(f"""
#     <div class='metric-card'>
#         <div class='metric-value'>{len(st.session_state.chat_history)}</div>
#         <div class='metric-label'>Queries Processed</div>
#     </div>
#     """, unsafe_allow_html=True)

# with col4:
#     success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 100
#     st.markdown(f"""
#     <div class='metric-card'>
#         <div class='metric-value'>{success_rate:.0f}%</div>
#         <div class='metric-label'>Success Rate</div>
#     </div>
#     """, unsafe_allow_html=True)

# st.markdown("<br>", unsafe_allow_html=True)

# # Query Input
# st.markdown("<div class='input-container'>", unsafe_allow_html=True)
# st.markdown("### 💬 Ask Your Question")

# query = st.text_input(
#     "",
#     placeholder="e.g., Which branch has highest gold loan and home loan?",
#     key="query_input",
#     value=st.session_state.get('current_query', ''),
#     label_visibility="collapsed"
# )

# if 'current_query' in st.session_state:
#     del st.session_state.current_query

# col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns([1.5, 1, 1, 1, 4])

# with col_btn1:
#     submit = st.button("🚀 Analyze Query", use_container_width=True, type="primary")
# with col_btn2:
#     clear_input = st.button("🔄 Clear", use_container_width=True)
# with col_btn3:
#     voice_input = st.button("🎤 Voice", use_container_width=True, disabled=True)
# with col_btn4:
#     help_btn = st.button("❓ Help", use_container_width=True)

# st.markdown("</div>", unsafe_allow_html=True)

# if help_btn:
#     st.markdown("""
#     <div class='info-box'>
#         <strong>💡 How to use:</strong><br>
#         • Type your question naturally (e.g., "Which branch has highest gold loan?")<br>
#         • Click example queries from sidebar for inspiration<br>
#         • Use specific branch names: Mumbai, Delhi, Pune, etc.<br>
#         • Ask about trends: "over time", "growth", "trend"<br>
#         • Compare metrics: "gold loan and home loan"
#     </div>
#     """, unsafe_allow_html=True)

# if clear_input:
#     st.rerun()

# # Process Query
# if submit and query:
#     st.session_state.chat_history.append({
#         'timestamp': datetime.now(),
#         'query': query,
#         'response': None
#     })
    
#     # Loading Animation
#     loading_placeholder = st.empty()
#     with loading_placeholder.container():
#         st.markdown("""
#         <div class='loading-container'>
#             <div class='loading-spinner'></div>
#             <p class='loading-text'>🤖 Analyzing your query...</p>
#             <p style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>This may take a few seconds</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     # Process
#     response = st.session_state.platform.process_query(query)
#     st.session_state.chat_history[-1]['response'] = response
    
#     loading_placeholder.empty()
#     time.sleep(0.3)
#     st.rerun()

# # ==================== CHAT HISTORY ====================

# st.markdown("---")
# st.markdown("### 💬 Conversation History")

# if not st.session_state.chat_history:
#     st.markdown("""
#     <div style='text-align: center; padding: 4rem 2rem; background: white; border-radius: 20px; 
#                 box-shadow: 0 10px 40px rgba(0,0,0,0.1);'>
#         <h2 style='color: #667eea; margin-bottom: 1rem;'>👋 Welcome to MCP Analytics!</h2>
#         <p style='color: #666; font-size: 1.1rem; margin-bottom: 1.5rem;'>
#             Start exploring your data with AI-powered insights
#         </p>
#         <p style='color: #999;'>
#             💡 Try asking: "Which branch has highest gold loan?" or click an example from the sidebar
#         </p>
#     </div>
#     """, unsafe_allow_html=True)
# else:
#     for i, chat in enumerate(reversed(st.session_state.chat_history)):
#         # User Query
#         st.markdown(f"""
#         <div class='user-message'>
#             <strong>🙋 You</strong>
#             <p style='margin: 0.5rem 0 0 0; font-size: 1.05rem;'>{chat['query']}</p>
#             <small style='opacity: 0.8;'>{chat['timestamp'].strftime('%I:%M:%S %p')}</small>
#         </div>
#         """, unsafe_allow_html=True)
        
#         # Bot Response
#         if chat['response']:
#             response = chat['response']
            
#             st.markdown("<div class='bot-message'>", unsafe_allow_html=True)
#             st.markdown("**🤖 MCP Analytics**")
            
#             if response['success']:
#                 # Result Value
#                 if 'value' in response['result']:
#                     value = response['result']['value']
#                     st.markdown(f"""
#                     <div class='result-value'>
#                         <h1 class='result-number'>{value:,.2f}</h1>
#                         <p class='result-label'>Query Result</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Insights
#                 if response.get('insights'):
#                     st.markdown("**📊 Key Insights:**")
#                     st.info(response['insights'])
                
#                 # Visualization
#                 if response.get('visualization'):
#                     with st.expander("📈 View Interactive Chart", expanded=True):
#                         try:
#                             import plotly.io as pio
#                             with open(response['visualization'], 'r', encoding='utf-8') as f:
#                                 html_content = f.read()
#                             st.components.v1.html(html_content, height=500, scrolling=True)
#                         except Exception as e:
#                             st.warning(f"Chart preview not available. Download to view.")
#                             with open(response['visualization'], 'r', encoding='utf-8') as f:
#                                 chart_html = f.read()
#                             st.download_button(
#                                 "📥 Download Chart",
#                                 chart_html,
#                                 file_name=f"chart_{i}.html",
#                                 mime="text/html",
#                                 key=f"download_{i}"
#                             )
                
#                 # Execution Details
#                 with st.expander("🔍 Execution Details"):
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.json({
#                             "Dataset": response['plan'].get('dataset'),
#                             "Metric": response['plan'].get('metric'),
#                             "Aggregation": response['plan'].get('aggregation')
#                         })
#                     with col2:
#                         st.json({
#                             "Comparison Type": response['plan'].get('comparison_type', 'None'),
#                             "Filters": response['plan'].get('filters', {}),
#                             "Group By": response['plan'].get('group_by', 'None')
#                         })
                
#             else:
#                 st.markdown(f"""
#                 <div class='error-alert'>
#                     <strong>❌ Error:</strong> {response.get('error', 'Unknown error occurred')}
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             st.markdown("</div>", unsafe_allow_html=True)

# # ==================== FOOTER ====================
# st.markdown("""
# <div class='footer'>
#     <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
#         🚀 Powered by MCP Analytics Platform
#     </p>
#     <p style='font-size: 0.9rem;'>
#         Built with ❤️ using Streamlit • Version 1.0.0 Production
#     </p>
#     <p style='font-size: 0.8rem; margin-top: 1rem;'>
#         © 2024 MCP Analytics. All rights reserved.
#     </p>
# </div>
# """, unsafe_allow_html=True)


"""
Nexus Analytics Platform - Production-Ready Web UI
Enterprise-grade interface with advanced features
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from improved_main import MCPAnalyticsPlatform
import time
from datetime import datetime
import json

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Nexus Analytics - Banking Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/nexus-analytics',
        'Report a bug': 'https://github.com/yourusername/nexus-analytics/issues',
        'About': '# Nexus Analytics Platform\nAI-Powered Banking Analytics v1.0'
    }
)

# ==================== CUSTOM CSS (PRODUCTION STYLING) ====================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Background */
    .main {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        margin-bottom: 2rem;
        text-align: center;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Input Container */
    .input-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* UPDATED: Input Text - BLACK COLOR */
    .stTextInput > div > div > input {
        border-radius: 50px;
        border: 2px solid #e0e0e0;
        padding: 18px 25px;
        font-size: 16px;
        transition: all 0.3s;
        background: #f8f9fa;
        color: #000000 !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999999 !important;
        font-weight: 400;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
        color: #000000 !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 35px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Result Card */
    .result-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        animation: fadeInUp 0.6s ease-out;
        border-left: 5px solid #667eea;
    }
    
    .result-value {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 15px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .result-number {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin: 0;
    }
    
    .result-label {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Chat Messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        max-width: 80%;
        animation: slideInRight 0.5s ease-out;
    }
    
    .bot-message {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        animation: slideInLeft 0.5s ease-out;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    .sidebar-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s;
    }
    
    .sidebar-card:hover {
        background: rgba(255,255,255,0.15);
        transform: translateX(5px);
    }
    
    .sidebar-title {
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0;
    }
    
    .sidebar-text {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Loading Animation */
    .loading-container {
        text-align: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        border: 6px solid rgba(102, 126, 234, 0.1);
        border-top: 6px solid #667eea;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem auto;
    }
    
    .loading-text {
        color: #667eea;
        font-weight: 600;
        font-size: 1.1rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Animations */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Success/Error Alerts */
    .success-alert {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    
    .error-alert {
        background: linear-gradient(135deg, #eb3941 0%, #f15e64 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(235, 57, 65, 0.3);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        border-radius: 50px;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255,255,255,0.6);
        margin-top: 3rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZE SESSION STATE ====================
if 'platform' not in st.session_state:
    with st.spinner('🚀 Initializing Analytics Platform...'):
        try:
            st.session_state.platform = MCPAnalyticsPlatform(use_local_llm=True)
            st.session_state.chat_history = []
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize platform: {str(e)}")
            st.stop()

# ==================== HEADER ====================
st.markdown("""
<div class='header-card'>
    <h1 class='header-title'>📊 Nexus Analytics Platform</h1>
    <p class='header-subtitle'>Enterprise-Grade Banking Intelligence | AI-Powered Insights</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <h2 style='color: white; font-weight: 800; margin: 0;'>⚡ Control Panel</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Dataset Info
    st.markdown("<h3 style='color: white; margin-top: 1.5rem;'>📂 Datasets</h3>", unsafe_allow_html=True)
    
    for name, df in st.session_state.platform.datasets.items():
        st.markdown(f"""
        <div class='sidebar-card'>
            <h4 class='sidebar-title'>{name.upper()}</h4>
            <p class='sidebar-text'>📊 {len(df):,} rows • {len(df.columns)} columns</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Example Queries
    st.markdown("<h3 style='color: white;'>💡 Quick Queries</h3>", unsafe_allow_html=True)
    
    example_queries = {
        "🏆 Top Performers": [
            "Which branch has highest gold loan?",
            "Which branch has highest NPA percent?",
            "Which branch has lowest fraud rate?",
        ],
        "📈 Trends & Growth": [
            "UPI volume trend over time",
            "Customer growth over time",
            "Gold loan growth rate",
        ],
        "🔍 Comparisons": [
            "Compare all branches for gold loan",
            "Gold loan and home loan comparison",
            "Compare Mumbai Delhi Pune for UPI",
        ],
        "📊 Deep Insights": [
            "Total gold loan in Mumbai",
            "Which branch has highest gold loan and home loan?",
            "Average credit score by branch",
        ]
    }
    
    selected_category = st.selectbox(
        "Select Category",
        list(example_queries.keys()),
        label_visibility="collapsed"
    )
    
    for query in example_queries[selected_category]:
        if st.button(query, key=query, use_container_width=True):
            st.session_state.current_query = query
            st.rerun()
    
    st.markdown("---")
    
    # Stats
    st.markdown("<h3 style='color: white;'>📊 Session Stats</h3>", unsafe_allow_html=True)
    
    total_queries = len(st.session_state.chat_history)
    successful_queries = sum(1 for chat in st.session_state.chat_history 
                            if chat.get('response') and chat['response'].get('success'))
    
    st.markdown(f"""
    <div class='sidebar-card'>
        <h4 class='sidebar-title'>{total_queries}</h4>
        <p class='sidebar-text'>Total Queries</p>
    </div>
    <div class='sidebar-card'>
        <h4 class='sidebar-title'>{successful_queries}</h4>
        <p class='sidebar-text'>Successful</p>
    </div>
    <div class='sidebar-card'>
        <h4 class='sidebar-title'>{total_queries - successful_queries}</h4>
        <p class='sidebar-text'>Failed</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions - Only Export button
    if st.button("💾 Export History", use_container_width=True):
        # Export chat history as JSON
        if st.session_state.chat_history:
            export_data = [{
                'timestamp': chat['timestamp'].isoformat(),
                'query': chat['query'],
                'success': chat['response'].get('success') if chat.get('response') else False
            } for chat in st.session_state.chat_history]
            
            st.download_button(
                "📥 Download History",
                data=json.dumps(export_data, indent=2),
                file_name=f"analytics_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ==================== MAIN CONTENT ====================

# Quick Stats Dashboard (REMOVED SUCCESS RATE)
col1, col2, col3 = st.columns(3)

total_rows = sum(len(df) for df in st.session_state.platform.datasets.values())
total_datasets = len(st.session_state.platform.datasets)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{total_datasets}</div>
        <div class='metric-label'>Active Datasets</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{total_rows:,}</div>
        <div class='metric-label'>Total Records</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{len(st.session_state.chat_history)}</div>
        <div class='metric-label'>Queries Processed</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Query Input
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
st.markdown("### 💬 Ask Your Question")

query = st.text_input(
    "",
    placeholder="e.g., Which branch has highest gold loan and home loan?",
    key="query_input",
    value=st.session_state.get('current_query', ''),
    label_visibility="collapsed"
)

if 'current_query' in st.session_state:
    del st.session_state.current_query

# REMOVED: Clear, Voice, Help buttons - Only Analyze button remains
submit = st.button("🚀 Analyze Query", use_container_width=False, type="primary")

st.markdown("</div>", unsafe_allow_html=True)

# Process Query
if submit and query:
    st.session_state.chat_history.append({
        'timestamp': datetime.now(),
        'query': query,
        'response': None
    })
    
    # Loading Animation
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.markdown("""
        <div class='loading-container'>
            <div class='loading-spinner'></div>
            <p class='loading-text'>🤖 Analyzing your query...</p>
            <p style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>This may take a few seconds</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Process
    response = st.session_state.platform.process_query(query)
    st.session_state.chat_history[-1]['response'] = response
    
    loading_placeholder.empty()
    time.sleep(0.3)
    st.rerun()

# ==================== CHAT HISTORY ====================

st.markdown("---")
st.markdown("### 💬 Conversation History")

if not st.session_state.chat_history:
    st.markdown("""
    <div style='text-align: center; padding: 4rem 2rem; background: white; border-radius: 20px; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);'>
        <h2 style='color: #667eea; margin-bottom: 1rem;'>👋 Welcome to Nexus Analytics!</h2>
        <p style='color: #666; font-size: 1.1rem; margin-bottom: 1.5rem;'>
            Start exploring your data with AI-powered insights
        </p>
        <p style='color: #999;'>
            💡 Try asking: "Which branch has highest gold loan?" or click an example from the sidebar
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        # User Query
        st.markdown(f"""
        <div class='user-message'>
            <strong>🙋 You</strong>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.05rem;'>{chat['query']}</p>
            <small style='opacity: 0.8;'>{chat['timestamp'].strftime('%I:%M:%S %p')}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Bot Response
        if chat['response']:
            response = chat['response']
            
            st.markdown("<div class='bot-message'>", unsafe_allow_html=True)
            st.markdown("**🤖 Nexus Analytics**")
            
            if response['success']:
                # Result Value
                if 'value' in response['result']:
                    value = response['result']['value']
                    st.markdown(f"""
                    <div class='result-value'>
                        <h1 class='result-number'>{value:,.2f}</h1>
                        <p class='result-label'>Query Result</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Insights
                if response.get('insights'):
                    st.markdown("**📊 Key Insights:**")
                    st.info(response['insights'])
                
                # Visualization
                if response.get('visualization'):
                    with st.expander("📈 View Interactive Chart", expanded=True):
                        try:
                            import plotly.io as pio
                            with open(response['visualization'], 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            st.components.v1.html(html_content, height=500, scrolling=True)
                        except Exception as e:
                            st.warning(f"Chart preview not available. Download to view.")
                            with open(response['visualization'], 'r', encoding='utf-8') as f:
                                chart_html = f.read()
                            st.download_button(
                                "📥 Download Chart",
                                chart_html,
                                file_name=f"chart_{i}.html",
                                mime="text/html",
                                key=f"download_{i}"
                            )
                
                # Execution Details
                with st.expander("🔍 Execution Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.json({
                            "Dataset": response['plan'].get('dataset'),
                            "Metric": response['plan'].get('metric'),
                            "Aggregation": response['plan'].get('aggregation')
                        })
                    with col2:
                        st.json({
                            "Comparison Type": response['plan'].get('comparison_type', 'None'),
                            "Filters": response['plan'].get('filters', {}),
                            "Group By": response['plan'].get('group_by', 'None')
                        })
                
            else:
                st.markdown(f"""
                <div class='error-alert'>
                    <strong>❌ Error:</strong> {response.get('error', 'Unknown error occurred')}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("""
<div class='footer'>
    <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
        🚀 Powered by Nexus Analytics Platform
    </p>
    <p style='font-size: 0.9rem;'>
        Built with ❤️ using Streamlit • Version 1.0.0 Production
    </p>
    <p style='font-size: 0.8rem; margin-top: 1rem;'>
        © 2024 Nexus Analytics. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)