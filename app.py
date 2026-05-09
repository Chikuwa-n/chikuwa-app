import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 設定 ---
st.set_page_config(page_title="合同会社竹輪 | 最適化判定ツール", layout="wide")

# --- ロジック関数 ---
def calculate_all_scenarios(salary_income, investment_income, expense, board_fee_monthly, prefecture):
    # 簡略化した税率・社保率（実際はもっと複雑ですが判定用に定義）
    TAX_RATE = 0.20  # 所得税・住民税合算（概算）
    PREF_RATE = 0.15 # 社会保険料率（労使合計・京都想定）

    # 1. 現状維持（給与 + 株/副業を個人で）
    # 特定口座なら分離課税20.315%だが、ここでは総合課税の個人事業主との比較用に簡易化
    status_stay_tax = (salary_income + investment_income - expense) * TAX_RATE
    status_stay_profit = (salary_income + investment_income - expense) - status_stay_tax

    # 2. 個人事業主（青色申告）
    # 青色申告控除65万を適用
    status_solo_tax = max(0, (salary_income + investment_income - expense - 650000)) * TAX_RATE
    status_solo_profit = (salary_income + investment_income - expense) - status_solo_tax

    # 3. 法人成り（合同会社・資産管理）
    # 役員報酬設定による社保削減を考慮
    annual_board_fee = board_fee_monthly * 12
    corporate_shaho = (board_fee_monthly * PREF_RATE * 2) * 12
    corporate_tax_fixed = 70000 # 均等割
    setup_cost = 100000 # 初年度コスト
    
    status_corp_dobukin = corporate_shaho + corporate_tax_fixed + setup_cost
    status_corp_profit = (salary_income + investment_income - expense) - status_corp_dobukin

    return {
        "現状維持": int(status_stay_profit),
        "個人事業主": int(status_solo_profit),
        "法人成り": int(status_corp_profit),
        "法人ドブ金": int(status_corp_dobukin)
    }

# --- UI部分 ---
st.title("⚖️ 独立・法人成り・現状維持 判定ツール")
st.caption("あなたの今の収入状況から、最も『手残り』が多くなる形態を判定します。")

# ① 入力セクション
st.header("① 現在の収入情報を入力")
col_in1, col_in2, col_in3 = st.columns(3)
with col_in1:
    salary = st.number_input("現在の給与年収 [円]", value=5000000, step=100000)
with col_in2:
    investment = st.number_input("株・副業などの収入 [円]", value=3000000, step=100000)
with col_in3:
    expense = st.number_input("関連する経費 [円]", value=500000, step=50000)

prefecture = st.selectbox("所在都道府県", ["京都府", "東京都", "大阪府"])

# ② 判定セクション
st.divider()
st.header("② あなたに最適なプランは？")

results = calculate_all_scenarios(salary, investment, expense, 45000, prefecture)
best_option = max(results, key=lambda k: results[k] if k != "法人ドブ金" else -1)

st.success(f"🏆 推奨： **{best_option}**")
st.write(f"もっとも手残りが多くなる形態は **{best_option}** です。")

# 比較表
df_res = pd.DataFrame({
    "形態": ["現状維持", "個人事業主", "法人成り"],
    "年間最終手残り": [results["現状維持"], results["個人事業主"], results["法人成り"]]
})
st.table(df_res)

# ③ 詳細セクション
if st.checkbox("③ 詳細な費用・収益シミュレーションを表示"):
    st.header("📊 詳細シミュレーション")
    
    tab1, tab2 = st.tabs(["初年度", "2年目以降"])
    
    with tab1:
        st.subheader("法人化した場合の初年度内訳")
        st.write(f"・設立費用（ドブ金）: 約 100,000円")
        st.write(f"・社会保険料（労使合計）: 約 {results['法人ドブ金'] - 170000:,}円")
        st.write(f"・法人住民税（均等割）: 70,000円")
        st.error(f"初年度のドブ金合計: {results['法人ドブ金']:,}円")

    with tab2:
        st.subheader("法人化 2年目以降")
        st.write(f"・社会保険料（労使合計）: 約 {results['法人ドブ金'] - 170000:,}円")
        st.write(f"・法人住民税（均等割）: 70,000円")
        st.success(f"2年目以降のドブ金合計: {results['法人ドブ金'] - 100000:,}円")

st.divider()
st.caption("Produced by 合同会社竹輪")
