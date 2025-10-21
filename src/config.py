import streamlit as st


def set_page_config():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://docs.streamlit.io",
            "Report a bug": None,
            "About": "Dashboard v1.0"
        }
    )


def apply_custom_css():
    custom_css = """
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
            color: #E0E0E0;
        }
        
        [data-testid="stSidebar"] {
            background-color: #0E1117;
            border-right: 1px solid #30363D;
        }
        
        [data-testid="stSidebarNav"] {
            background-color: #0E1117;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #F0F6FC;
            margin-bottom: 1rem;
        }
        
        .stMetric {
            background-color: #161B22;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #30363D;
        }
        
        .stMetric-label {
            color: #8B949E;
        }
        
        .stMetric-value {
            color: #58A6FF;
        }
        
        .stCard {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1.5rem;
        }
        
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
            background-color: #161B22;
        }
        
        .stDataFrame {
            background-color: #161B22;
        }
        
        .stDataFrame thead {
            background-color: #0E1117;
        }
        
        .stDataFrame tbody tr:hover {
            background-color: #262730;
        }
        
        .stButton > button {
            background-color: #1F77B4;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        
        .stButton > button:hover {
            background-color: #3498DB;
        }
        
        .stButton > button:active {
            background-color: #1560A0;
        }
        
        .stTextInput > div > div > input,
        .stPasswordInput > div > div > input,
        .stSelectbox > div > div > select,
        .stMultiSelect > div > div > select {
            background-color: #161B22;
            color: #E0E0E0;
            border: 1px solid #30363D;
            border-radius: 4px;
            padding: 0.5rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stPasswordInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stMultiSelect > div > div > select:focus {
            border-color: #1F77B4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
        }
        
        .stAlert {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 4px;
        }
        
        .stAlert-warning {
            background-color: #332701;
            border-color: #6F4E37;
        }
        
        .stAlert-error {
            background-color: #3D0F0F;
            border-color: #6F3737;
        }
        
        .stAlert-success {
            background-color: #0F3D1F;
            border-color: #376F3D;
        }
        
        .stAlert-info {
            background-color: #0F1F3D;
            border-color: #3D5F6F;
        }
        
        .container {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .section-header {
            border-bottom: 2px solid #1F77B4;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        [data-testid="stForm"] {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 2rem;
        }
        
        .plotly-graph-div {
            background-color: #161B22;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #161B22;
            border: 1px solid #30363D;
            color: #8B949E;
            border-radius: 4px 4px 0 0;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1F77B4;
            color: #FFFFFF;
            border-color: #1F77B4;
        }
        
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            margin-top: 2rem;
        }
        
        .auth-title {
            text-align: center;
            margin-bottom: 1.5rem;
            color: #F0F6FC;
        }
        
        .auth-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .metric-container {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #58A6FF;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #8B949E;
            margin-top: 0.5rem;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)