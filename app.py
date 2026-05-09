import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(page_title="合同会社竹輪 | 法人成り診断ツール", layout="wide")

# --- 京都府の料率（2026年想定・概算） ---
# 協会けんぽ京都府（介護保険第2号含む）
HEALTH_RATE = 0.1165 / 2  
PENSION_RATE = 0.183 / 2  

# --- タイトル表示 ---
st.title("🚀 個人事業主 vs 法人成り 損益分岐シミュレーター")
st.markdown("""
資産管理会社（合同会社）の設立を検討している投資家・個人事業主向けの精密診断ツールです。
**「ドブ金（社会保険料・税金）」**の差を可視化します。
""")

# --- サイドバー：ユーザー入力 ---
st.sidebar.header("📊 収支シミュレーション設定")
income = st.sidebar.number_input("年間売上（運用益含む） [円]", value=8000000, step=100000)
expense = st.sidebar.number_input("年間経費 [円]", value=1000000, step=100000)

st.sidebar.subheader("法人化後の設定")
board_fee_monthly = st.sidebar.slider("役員報酬（月額） [円]", 45000, 500000, 45000)
is_first_year = st.sidebar.checkbox("初年度のシミュレーション", value=True)

# --- 計算ロジック ---
def calculate_results(income, expense, board_fee_monthly, first_year):
    # 1. 法人のドブ金計算
    # 社会保険料（労使合計）
    annual_shaho = (board_fee_monthly * (HEALTH_RATE + PENSION_RATE) * 2) * 12
    # 法人住民税均等割（赤字でもかかる）
    fixed_tax = 70000
    # 設立費用
    setup_cost = 100000 if first_year else 0
    
    total_dobukin = annual_shaho + fixed_tax + setup_cost
    
    # 法人の手残り（簡易：法人税等は一旦考慮外）
    net_profit = income - expense - (board_fee_monthly * 12) - total_dobukin
    
    return total_dobukin, net_profit

# 実行
dobukin, profit = calculate_results(income, expense, board_fee_monthly, is_first_year)

# --- メイン画面表示 ---
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("📉 かえってこないお金（ドブ金）")
    st.subheader(f"{int(dobukin):,} 円 / 年")
    st.caption("※設立費用・社保合計・均等割の合算")

with col2:
    st.header("💰 法人の純手残り")
    st.subheader(f"{int(profit):,} 円 / 年")
    st.caption("※売上から経費・報酬・ドブ金を引いた残金")

# --- 視覚化グラフ ---
st.divider()
st.subheader("年度別・構成比の確認")

# 棒グラフ（初年度 vs 2年目）
first_year_cost, _ = calculate_results(income, expense, board_fee_monthly, True)
second_year_cost, _ = calculate_results(income, expense, board_fee_monthly, False)

fig = go.Figure(data=[
    go.Bar(name='初年度', x=['ドブ金'], y=[first_year_cost], marker_color='#eb4034'),
    go.Bar(name='2年目以降', x=['ドブ金'], y=[second_year_cost], marker_color='#34eb89')
])
fig.update_layout(barmode='group', title="年度別のドブ金コスト比較")
st.plotly_chart(fig, use_container_width=True)

# 代表へのアドバイス
st.info(f"💡 **代表へのヒント:** 役員報酬を **{board_fee_monthly:,}円** に設定すると、年間の社会保険料（法人＋個人）は約 **{int(dobukin - 70000 - (100000 if is_first_year else 0)):,}円** です。")
