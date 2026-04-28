from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
import os
from openai import OpenAI
warnings.filterwarnings('ignore')

st.set_page_config(page_title="金融数据挖掘及其综合应用平台", layout='wide', initial_sidebar_state="expanded")

# ========== 默认API密钥 ==========
DEFAULT_API_KEY = "sk-49914cb00a544da7a13674e98a4a0310"
if 'api_key' not in st.session_state:
    env_key = os.environ.get("OPENAI_API_KEY", "")
    st.session_state['api_key'] = env_key if env_key else DEFAULT_API_KEY

# ========== 全局CSS样式（增强文字清晰度） ==========
st.markdown("""
<style>
    /* 全局背景与遮罩（提高文字对比度） */
    .stApp {
        background: linear-gradient(135deg, #f0f4fa 0%, #d9e2ef 100%);
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255,255,255,0.88);
        backdrop-filter: blur(2px);
        z-index: -1;
    }
    /* 主标题样式 */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    /* 卡片样式 */
    .metric-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(4px);
        padding: 1.2rem;
        border-radius: 20px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    /* AI分析区域 */
    .ai-analysis {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 28px;
        color: #f8fafc;
        margin: 1.5rem 0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);
    }
    /* 聊天窗口 */
    .chat-message {
        padding: 0.8rem;
        border-radius: 1rem;
        margin-bottom: 0.8rem;
        background-color: rgba(255,255,255,0.85);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(59,130,246,0.3);
        color: #1e293b;
    }
    .chat-user {
        background-color: #e0f2fe;
        border-left: 4px solid #3B82F6;
    }
    .chat-assistant {
        background-color: #f1f5f9;
        border-left: 4px solid #10B981;
    }
    /* 按钮 */
    .stButton > button {
        border-radius: 40px;
        background: linear-gradient(90deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        font-weight: 500;
    }
    /* 表格和数据框 */
    .dataframe, .stDataFrame {
        background-color: rgba(255,255,255,0.9);
        border-radius: 16px;
    }
    /* 输入框、滑块标签 */
    label, .stMarkdown, .stSelectbox label, .stSlider label {
        color: #1e293b !important;
        font-weight: 500;
    }
    /* 侧边栏背景加强 */
    .css-1d391kg, .css-163ttbj {
        background-color: rgba(255,255,255,0.95);
        backdrop-filter: blur(8px);
    }
    /* 脚注 */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #475569;
        border-top: 1px solid rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ========== 数据加载（缓存） ==========
@st.cache_data
def load_data():
    data_dict = {}
    try:
        with st.spinner('加载交易数据...'):
            trade_data_2024 = pd.read_csv('交易数据2024.csv')
            trade_data_2025 = pd.read_csv('交易数据2025.csv')
            adj_trade_2023 = pd.read_csv('复权交易数据2023.csv')
            adj_trade_2024 = pd.read_csv('复权交易数据2024.csv')
            adj_trade_2025 = pd.read_csv('复权交易数据2025.csv')
            trade_data = pd.concat([trade_data_2024, trade_data_2025], ignore_index=True)
            adj_trade_data = pd.concat([adj_trade_2023, adj_trade_2024, adj_trade_2025], ignore_index=True)
            for df in [trade_data, adj_trade_data]:
                df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            data_dict['trade_data'] = trade_data
            data_dict['adj_trade_data'] = adj_trade_data
        with st.spinner('加载指数数据...'):
            hs300_data = pd.read_excel('沪深300指数交易数据.xlsx')
            hs300_data['trade_date'] = pd.to_datetime(hs300_data['trade_date'], format='%Y%m%d')
            data_dict['hs300_data'] = hs300_data
            index_data = pd.read_csv('index_trdata.csv')
            index_data['trade_date'] = pd.to_datetime(index_data['trade_date'], format='%Y%m%d')
            data_dict['index_data'] = index_data
        with st.spinner('加载股票基本信息...'):
            stock_basic = pd.read_excel('股票基本信息表.xlsx')
            company_info = pd.read_excel('上市公司基本信息.xlsx')
            data_dict['stock_basic'] = stock_basic
            data_dict['company_info'] = company_info
        with st.spinner('加载行业分类...'):
            industry_info = pd.read_excel('最新个股申万行业分类(完整版-截至7月末).xlsx')
            industry_info = industry_info.dropna(subset=['新版一级行业', '股票代码'])
            industry_info['股票代码'] = industry_info['股票代码'].astype(str).str.strip()
            data_dict['industry_info'] = industry_info
        with st.spinner('加载财务数据...'):
            years = [2018,2019,2020,2021,2022,2023,2024]
            fin_list = []
            for y in years:
                try:
                    df = pd.read_excel(f'Data{y}.xlsx')
                    df['年度'] = y
                    fin_list.append(df)
                except: pass
            if fin_list:
                financial_data = pd.concat(fin_list, ignore_index=True)
                financial_data['ts_code'] = financial_data['ts_code'].astype(str).str.strip()
                data_dict['financial_data'] = financial_data
            try:
                fin_data = pd.read_csv('fin_data.csv')
                fin_data['股票代码'] = fin_data['股票代码'].astype(str).str.strip()
                data_dict['fin_data'] = fin_data
            except: pass
        with st.spinner('加载股票日线数据...'):
            try:
                stk_trdata = pd.read_csv('stk_trdata.csv')
                stk_trdata['trade_date'] = pd.to_datetime(stk_trdata['trade_date'], format='%Y%m%d')
                stk_trdata['ts_code'] = stk_trdata['ts_code'].astype(str).str.strip()
                data_dict['stk_trdata'] = stk_trdata
            except: pass
        st.success("数据加载完成！")
    except Exception as e:
        st.error(f"加载失败: {e}")
    return data_dict

# ========== 技术指标、模型训练等辅助函数 ==========
def calculate_technical_indicators(df, period=20):
    if df.empty or len(df) < 30: return df
    df = df.sort_values('trade_date').copy()
    df['MA5'] = df['close'].rolling(5,1).mean()
    df['MA10'] = df['close'].rolling(10,1).mean()
    df['MA20'] = df['close'].rolling(20,1).mean()
    df['MA60'] = df['close'].rolling(60,1).mean()
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14,1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14,1).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1+rs))
    low_min = df['low'].rolling(9,1).min()
    high_max = df['high'].rolling(9,1).max()
    df['K'] = 100 * (df['close'] - low_min) / (high_max - low_min)
    df['D'] = df['K'].rolling(3,1).mean()
    df['J'] = 3*df['K'] - 2*df['D']
    df['OBV'] = (np.sign(df['close'].diff()) * df['vol']).fillna(0).cumsum()
    df['Return'] = df['close'].pct_change()
    df['Volume_Ratio'] = df['vol'] / df['vol'].rolling(5,1).mean()
    df['Momentum'] = df['close'] - df['close'].shift(5)
    return df

def calculate_cumulative_returns(df, start_date, end_date):
    if df.empty: return 0
    mask = (df['trade_date'] >= pd.Timestamp(start_date)) & (df['trade_date'] <= pd.Timestamp(end_date))
    filtered = df[mask]
    if len(filtered) < 2: return 0
    return (filtered.iloc[-1]['close'] / filtered.iloc[0]['close'] - 1) * 100

def build_trading_strategy(predictions, prices, initial_capital=1000000):
    positions, cash, holdings = [], initial_capital, 0
    portfolio_values = []
    for i, signal in enumerate(predictions):
        price = prices[i]
        if signal == 1 and cash > 0:
            shares = cash // price
            if shares > 0:
                cash -= shares * price
                holdings += shares
        elif signal == -1 and holdings > 0:
            cash += holdings * price
            holdings = 0
        portfolio_values.append(cash + holdings * price)
        positions.append(holdings)
    total_return = (portfolio_values[-1]/initial_capital -1)*100 if portfolio_values else 0
    return {'total_return': total_return, 'portfolio_values': portfolio_values, 'positions': positions, 'final_portfolio_value': portfolio_values[-1] if portfolio_values else initial_capital}

def prepare_model_data(stock_data, target_days=5):
    if stock_data.empty or len(stock_data) < 30: return None
    stock_data = calculate_technical_indicators(stock_data)
    feature_cols = ['MA5','MA10','MA20','MA60','MACD','RSI','K','D','J','OBV','Volume_Ratio','Momentum']
    available = [c for c in feature_cols if c in stock_data.columns]
    if len(available) < 5: return None
    stock_data['Future_Return'] = stock_data['close'].shift(-target_days) / stock_data['close'] - 1
    stock_data['Target'] = np.where(stock_data['Future_Return'] > 0.02, 1, np.where(stock_data['Future_Return'] < -0.02, -1, 0))
    stock_data = stock_data.dropna(subset=available+['Target'])
    if len(stock_data) < 50: return None
    X = stock_data[available]
    y = stock_data['Target']
    train_size = int(0.7*len(X))
    val_size = int(0.15*len(X))
    X_train, X_val, X_test = X[:train_size], X[train_size:train_size+val_size], X[train_size+val_size:]
    y_train, y_val, y_test = y[:train_size], y[train_size:train_size+val_size], y[train_size+val_size:]
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    return (X_train_scaled, y_train, X_val_scaled, y_val, X_test_scaled, y_test, scaler, available)

def train_model(model_type, X_train, y_train, X_val, y_val):
    if model_type == '逻辑回归': model = LogisticRegression(max_iter=1000, random_state=42)
    elif model_type == '支持向量机': model = SVC(kernel='rbf', probability=True, random_state=42)
    elif model_type == '神经网络': model = MLPClassifier(hidden_layer_sizes=(100,50), max_iter=1000, random_state=42)
    elif model_type == '随机森林': model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == '梯度提升树': model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    else: model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    val_acc = accuracy_score(y_val, model.predict(X_val))
    return model, val_acc

def generate_ai_analysis(stock_data, industry_name, stock_code, analysis_year, api_key):
    if not api_key: return "请输入API密钥"
    try:
        latest = stock_data.tail(50)
        current_price = latest['close'].iloc[-1] if len(latest)>0 else 0
        price_change = latest['pct_chg'].iloc[-1] if len(latest)>0 else 0
        avg_volume = latest['vol'].mean() if len(latest)>0 else 0
        tech = calculate_technical_indicators(stock_data.copy())
        if not tech.empty:
            rsi = tech.iloc[-1].get('RSI',50)
            macd = tech.iloc[-1].get('MACD',0)
            macd_signal = tech.iloc[-1].get('MACD_Signal',0)
        else: rsi,macd,macd_signal = 50,0,0
        prompt = f"""你是一位资深金融分析师，请对{industry_name}行业的股票{stock_code}（年份：{analysis_year}）进行分析。
数据：价格{current_price:.2f}，涨跌幅{price_change:.2f}%，成交量{avg_volume:.0f}；RSI={rsi:.1f}，MACD={macd:.3f}，信号线={macd_signal:.3f}。
请给出技术分析、市场环境、投资建议和风险提示。"""
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"你是专业金融分析师。"},{"role":"user","content":prompt}], temperature=0.7, max_tokens=1500)
        return response.choices[0].message.content
    except Exception as e: return f"AI分析失败: {e}"

# ========== AI对话上下文（全局） ==========
def get_current_context(data, module, industry_name=None, stock_code=None):
    if module == "市场总览":
        trade = data.get('trade_data', pd.DataFrame())
        hs = data.get('hs300_data', pd.DataFrame())
        ind = data.get('industry_info', pd.DataFrame())
        ctx = ""
        if not trade.empty:
            ctx += f"最新交易日平均涨跌幅：{trade.groupby('trade_date')['pct_chg'].mean().iloc[-1]:.2f}% "
        if not hs.empty:
            ctx += f"沪深300收盘{hs['close'].iloc[-1]:.2f} "
        if not ind.empty:
            ctx += f"共{len(ind)}只个股，{ind['新版一级行业'].nunique()}个行业。"
        return ctx
    elif module == "行业分析" and industry_name:
        info = data.get('industry_info', pd.DataFrame())
        stocks = info[info['新版一级行业']==industry_name]['股票代码'].tolist()
        adj = data.get('adj_trade_data', pd.DataFrame())
        ctx = f"行业：{industry_name}，共{len(stocks)}只股票。"
        if not adj.empty:
            latest = adj[adj['ts_code'].isin(stocks) & (adj['trade_date']==adj['trade_date'].max())]
            if not latest.empty:
                ctx += f"最近交易日平均涨跌幅：{latest['pct_chg'].mean():.2f}%。"
        return ctx
    elif module == "个股分析":
        return f"个股分析，当前查看股票：{stock_code if stock_code else '未选择'}。"
    elif module == "投资组合回测":
        return "投资组合回测，可构建等权组合并计算净值。"
    return "金融数据平台。"

def call_chat_api(messages, api_key):
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.7, max_tokens=2000)
        return response.choices[0].message.content
    except Exception as e: return f"调用失败: {e}"

def render_global_chat(data, module, industry_name=None, stock_code=None):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 智能金融助手")
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    for msg in st.session_state.chat_messages:
        role_class = "chat-user" if msg["role"]=="user" else "chat-assistant"
        icon = "👤" if msg["role"]=="user" else "🤖"
        st.sidebar.markdown(f'<div class="chat-message {role_class}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
    user_input = st.sidebar.chat_input("提问金融问题...")
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        context = get_current_context(data, module, industry_name, stock_code)
        system = f"你是金融分析师，当前上下文：{context}。请基于此回答，超出使用通用知识。"
        messages = [{"role": "system", "content": system}] + st.session_state.chat_messages
        with st.spinner("思考中..."):
            reply = call_chat_api(messages, st.session_state.get('api_key', ''))
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ========== 功能模块 ==========
def display_market_overview(data):
    st.markdown('<h1 class="main-header">📊 市场总览</h1>', unsafe_allow_html=True)
    trade = data.get('trade_data', pd.DataFrame())
    hs300 = data.get('hs300_data', pd.DataFrame())
    index_data = data.get('index_data', pd.DataFrame())
    stock_basic = data.get('stock_basic', pd.DataFrame())
    industry_info = data.get('industry_info', pd.DataFrame())
    fin = data.get('financial_data', pd.DataFrame())
    col1, col2 = st.columns([1,2])
    with col1:
        start = st.date_input("开始日期", date(2024,1,1), key="mark_start")
        end = st.date_input("结束日期", date(2024,12,31), key="mark_end")
        if not trade.empty:
            latest = trade['trade_date'].max()
            recent = trade[trade['trade_date']==latest]
            st.metric("交易股票数", len(recent))
            st.metric("平均涨跌幅", f"{recent['pct_chg'].mean():.2f}%")
            st.metric("总成交量(亿)", f"{recent['vol'].sum()/1e8:.1f}")
    with col2:
        if not hs300.empty:
            filtered = hs300[(hs300['trade_date']>=pd.Timestamp(start)) & (hs300['trade_date']<=pd.Timestamp(end))]
            fig = px.line(filtered, x='trade_date', y='close', title="沪深300指数走势")
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("### 行业统计分析")
    if not fin.empty and not industry_info.empty:
        merged = pd.merge(fin, industry_info[['股票代码','新版一级行业']], left_on='ts_code', right_on='股票代码', how='inner')
        if not merged.empty:
            stats = merged.groupby(['新版一级行业','年度']).agg({'营业收入':'sum','营业利润':'sum'}).reset_index()
            stats['营收增长率'] = stats.groupby('新版一级行业')['营业收入'].pct_change()*100
            st.dataframe(stats[stats['年度']==stats['年度'].max()])

def display_industry_analysis(data, industry_name):
    st.markdown(f'<h1 class="main-header">🏭 {industry_name}行业分析</h1>', unsafe_allow_html=True)
    industry_info = data.get('industry_info', pd.DataFrame())
    adj_trade = data.get('adj_trade_data', pd.DataFrame())
    hs300 = data.get('hs300_data', pd.DataFrame())
    company_info = data.get('company_info', pd.DataFrame())
    fin_data = data.get('fin_data', pd.DataFrame())
    industry_info['股票代码'] = industry_info['股票代码'].astype(str).str.strip()
    stocks = industry_info[industry_info['新版一级行业']==industry_name]['股票代码'].tolist()
    if not stocks:
        st.warning("无股票数据")
        return
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("股票数量", len(stocks))
    if not adj_trade.empty:
        latest = adj_trade['trade_date'].max()
        recent = adj_trade[(adj_trade['ts_code'].isin(stocks)) & (adj_trade['trade_date']==latest)]
        avg = recent['pct_chg'].mean() if not recent.empty else 0
        col2.metric("近期平均涨跌", f"{avg:.2f}%")
    if not adj_trade.empty:
        ind_data = adj_trade[adj_trade['ts_code'].isin(stocks)]
        if not ind_data.empty:
            idx = ind_data.groupby('trade_date').apply(lambda x: (x['close']*x['vol']).sum()/x['vol'].sum()).reset_index()
            idx.columns=['trade_date','price']
            fig = px.line(idx, x='trade_date', y='price', title=f'{industry_name}行业指数')
            st.plotly_chart(fig, use_container_width=True)
    tab_names = ["📊 行业指数交易数据", "🏢 上市公司信息", "💹 股票交易数据", "💰 财务数据", "⭐ 综合评价分析", "📈 股票价格涨跌趋势分析"]
    tab_objs = st.tabs(tab_names)
    for idx, tab in enumerate(tab_objs):
        with tab:
            if tab_names[idx] == "📊 行业指数交易数据":
                if not hs300.empty:
                    st.dataframe(hs300.sort_values('trade_date', ascending=False).head(100))
            elif tab_names[idx] == "🏢 上市公司信息":
                if not company_info.empty:
                    ind_com = company_info[company_info['ts_code'].isin(stocks)]
                    st.dataframe(ind_com)
            elif tab_names[idx] == "💹 股票交易数据":
                if not adj_trade.empty:
                    latest_trade = adj_trade[adj_trade['ts_code'].isin(stocks) & (adj_trade['trade_date']==adj_trade['trade_date'].max())]
                    latest_trade = pd.merge(latest_trade, industry_info[['股票代码','公司简称']], left_on='ts_code', right_on='股票代码')
                    st.dataframe(latest_trade[['公司简称','close','pct_chg','vol']])
            elif tab_names[idx] == "💰 财务数据":
                if not fin_data.empty:
                    fin = fin_data[fin_data['股票代码'].isin(stocks)]
                    if not fin.empty:
                        st.dataframe(fin[fin['年度']==fin['年度'].max()])
            elif tab_names[idx] == "⭐ 综合评价分析":
                display_comprehensive_evaluation(data, industry_name, stocks)
            elif tab_names[idx] == "📈 股票价格涨跌趋势分析":
                display_trend_analysis(data, industry_name, stocks)

def display_comprehensive_evaluation(data, industry_name, industry_stocks):
    st.markdown("#### 综合评价分析")
    fin_data = data.get('fin_data', pd.DataFrame())
    adj_trade = data.get('adj_trade_data', pd.DataFrame())
    hs300 = data.get('hs300_data', pd.DataFrame())
    if fin_data.empty: return
    year = st.selectbox("评价年度", [2024,2023,2022], key="comp_year")
    rank = st.selectbox("排名数量", [5,10,15], key="comp_rank")
    fin = fin_data[fin_data['股票代码'].isin(industry_stocks) & (fin_data['年度']==year)].copy()
    if not fin.empty and '净资产收益率' in fin.columns and '营业收入' in fin.columns:
        fin['综合得分'] = fin['净资产收益率'].fillna(0)*0.5 + (fin['净利润']/fin['营业收入']).fillna(0)*0.5
        top = fin.nlargest(rank, '综合得分')
        st.dataframe(top[['股票代码','净资产收益率','营业收入','净利润','综合得分']])
        start = st.date_input("回测开始", date(2024,1,1), key="comp_start")
        end = st.date_input("回测结束", date(2024,6,30), key="comp_end")
        if not adj_trade.empty:
            rets = []
            for _, row in top.iterrows():
                code = row['股票代码']
                stock_data = adj_trade[adj_trade['ts_code']==code]
                rets.append(calculate_cumulative_returns(stock_data, start, end))
            avg_ret = np.mean(rets) if rets else 0
            hs_ret = calculate_cumulative_returns(hs300, start, end) if not hs300.empty else 0
            st.metric("组合收益率", f"{avg_ret:.2f}%")
            st.metric("沪深300收益率", f"{hs_ret:.2f}%")

def display_trend_analysis(data, industry_name, industry_stocks):
    st.markdown("#### 股票价格涨跌趋势分析")
    adj_trade = data.get('adj_trade_data', pd.DataFrame())
    if adj_trade.empty: 
        st.warning("交易数据缺失")
        return
    
    # ========== 模型训练参数（放在主界面内部） ==========
    st.markdown("##### 🤖 模型参数配置")
    col1, col2, col3 = st.columns(3)
    with col1:
        model_type = st.selectbox("选择预测模型", ['逻辑回归', '支持向量机', '随机森林', '梯度提升树', '神经网络'], key="trend_model")
    with col2:
        target_days = st.slider("预测未来天数", 3, 10, 5, key="trend_days")
    with col3:
        test_ratio = st.slider("测试集比例%", 10, 40, 20, key="trend_test") / 100
    
    year = st.selectbox("分析年度", [2024,2023,2022], key="trend_year")
    stock = st.selectbox("选择股票", industry_stocks[:20], key="trend_stock")
    stock_data = adj_trade[(adj_trade['ts_code']==stock) & (adj_trade['trade_date'].dt.year==year)]
    if stock_data.empty:
        st.warning("无数据")
        return
    tech = calculate_technical_indicators(stock_data)
    st.line_chart(tech.set_index('trade_date')[['close','MA5','MA20']])
    
    if st.button("启动模型训练", key="train_btn"):
        with st.spinner("训练中..."):
            res = prepare_model_data(stock_data, target_days=target_days)
            if res:
                X_train,y_train,X_val,y_val,X_test,y_test,scaler,feats = res
                model,val_acc = train_model(model_type, X_train, y_train, X_val, y_val)
                st.success(f"验证集准确率：{val_acc:.2%}")
                y_pred = model.predict(X_test)
                test_acc = accuracy_score(y_test, y_pred)
                st.metric("测试集准确率", f"{test_acc:.2%}")
                # 混淆矩阵
                cm = confusion_matrix(y_test, y_pred)
                fig_cm = px.imshow(cm, text_auto=True, labels=dict(x="预测", y="实际"), x=['下跌','震荡','上涨'], y=['下跌','震荡','上涨'])
                st.plotly_chart(fig_cm, use_container_width=True)
                # 量化策略回测
                all_pred = model.predict(scaler.transform(tech[feats].dropna()))
                valid_idx = tech[feats].dropna().index
                prices = tech.loc[valid_idx, 'close'].values
                if len(all_pred) > 0:
                    strat = build_trading_strategy(all_pred, prices)
                    st.metric("策略总收益", f"{strat['total_return']:.2f}%")
                    fig_strat = go.Figure()
                    fig_strat.add_trace(go.Scatter(y=strat['portfolio_values'], mode='lines', name='策略净值'))
                    fig_strat.update_layout(title='策略净值曲线')
                    st.plotly_chart(fig_strat, use_container_width=True)
            else:
                st.warning("数据不足，无法训练")
    
    # AI分析报告按钮
    st.markdown("##### 🧠 AI大模型解读与分析")
    api_key = st.session_state.get('api_key', '')
    if not api_key:
        st.warning("⚠️ 请在侧边栏输入API密钥以使用AI分析功能")
    if st.button("生成AI分析报告", type="secondary", disabled=not api_key):
        with st.spinner("AI正在分析..."):
            report = generate_ai_analysis(stock_data, industry_name, stock, year, api_key)
            st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
            st.markdown("### 🤖 AI智能分析报告")
            st.markdown(report)
            st.markdown("</div>", unsafe_allow_html=True)

def display_stock_analysis(data):
    st.markdown('<h1 class="main-header">📈 个股分析</h1>', unsafe_allow_html=True)
    stock_basic = data.get('stock_basic', pd.DataFrame())
    adj_trade = data.get('adj_trade_data', pd.DataFrame())
    fin_data = data.get('fin_data', pd.DataFrame())
    if stock_basic.empty:
        st.warning("股票基础数据缺失")
        return
    stock_list = stock_basic['ts_code'].astype(str).tolist()
    stock_code = st.selectbox("选择股票代码", stock_list)
    st.session_state["current_stock"] = stock_code
    if stock_code:
        info = stock_basic[stock_basic['ts_code']==stock_code]
        name = info['name'].iloc[0] if not info.empty else stock_code
        st.subheader(f"{name} ({stock_code})")
        trade = adj_trade[adj_trade['ts_code']==stock_code].sort_values('trade_date')
        if not trade.empty:
            fig = px.line(trade, x='trade_date', y='close', title="收盘价走势")
            st.plotly_chart(fig, use_container_width=True)
            tech = calculate_technical_indicators(trade)
            col1,col2 = st.columns(2)
            with col1:
                st.line_chart(tech.set_index('trade_date')[['RSI']])
            with col2:
                st.line_chart(tech.set_index('trade_date')[['MACD','MACD_Signal']])
        if not fin_data.empty:
            fin = fin_data[fin_data['股票代码']==stock_code].sort_values('年度', ascending=False)
            if not fin.empty:
                st.subheader("历年财务指标")
                st.dataframe(fin[['年度','营业收入','净利润','净资产收益率']])

def display_portfolio_backtest(data):
    st.markdown('<h1 class="main-header">💰 投资组合回测</h1>', unsafe_allow_html=True)
    adj_trade = data.get('adj_trade_data', pd.DataFrame())
    stock_basic = data.get('stock_basic', pd.DataFrame())
    if adj_trade.empty or stock_basic.empty:
        st.warning("数据缺失")
        return
    stocks = st.multiselect("选择股票（最多5只）", stock_basic['ts_code'].astype(str).tolist(), max_selections=5)
    start = st.date_input("开始日期", date(2024,1,1))
    end = st.date_input("结束日期", date(2024,6,30))
    if stocks and st.button("开始回测"):
        prices = {}
        for code in stocks:
            df = adj_trade[(adj_trade['ts_code']==code) & (adj_trade['trade_date']>=pd.Timestamp(start)) & (adj_trade['trade_date']<=pd.Timestamp(end))]
            if not df.empty:
                df = df.set_index('trade_date')['close']
                prices[code] = df
        if prices:
            all_dates = pd.concat(prices.values(), axis=1).dropna().index
            equal_weights = 1/len(stocks)
            port_val = pd.Series(1.0, index=all_dates)
            for code in stocks:
                ret = prices[code].pct_change().fillna(0)
                port_val = port_val * (1 + equal_weights * ret).fillna(1)
            port_val = port_val.cumprod()
            fig = px.line(x=port_val.index, y=port_val, title="等权组合净值")
            st.plotly_chart(fig, use_container_width=True)
            st.metric("累计收益率", f"{(port_val.iloc[-1]-1)*100:.2f}%")

# ========== 主函数 ==========
def main():
    data = load_data()
    st.markdown('<h1 class="main-header">金融数据挖掘及其综合应用平台</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-header">—— 智能投研分析平台 ——</h3>', unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/stock.png", width=80)
        st.markdown("### 📋 功能导航")
        module = st.radio("选择模块", ["市场总览", "行业分析", "个股分析", "投资组合回测"], index=0)
        industry_name = None
        if module == "行业分析":
            ind_info = data.get('industry_info', pd.DataFrame())
            if not ind_info.empty:
                industries = sorted(ind_info['新版一级行业'].dropna().unique())
                industry_name = st.selectbox("选择行业", industries)
            else:
                st.warning("行业数据缺失")
                module = "市场总览"
        
        # API设置
        st.markdown("---")
        st.markdown("### 🔑 API密钥")
        api_key_input = st.text_input("DeepSeek API Key", type="password", value=st.session_state.get('api_key', DEFAULT_API_KEY))
        if api_key_input:
            st.session_state['api_key'] = api_key_input

    # 显示对应模块
    if module == "市场总览":
        display_market_overview(data)
    elif module == "行业分析" and industry_name:
        display_industry_analysis(data, industry_name)
    elif module == "个股分析":
        display_stock_analysis(data)
    elif module == "投资组合回测":
        display_portfolio_backtest(data)

    # 全局AI对话（侧边栏底部）
    render_global_chat(data, module, industry_name, st.session_state.get("current_stock", None))

    st.markdown("---")
    st.markdown("<div class='footer'>数据仅供参考，AI分析不构成投资建议。</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()