import streamlit as st
import pandas as pd

# --- 設定 ---
st.set_page_config(page_title="合同会社竹輪 | 全国対応版シミュレーター", layout="wide")

# --- 全国料率データ（令和6年度 協会けんぽ 概算） ---
# 本来は47都道府県分をリスト化しますが、ここでは主要な所をピックアップ
PREF_RATES = {
    "東京都": 0.0998,
    "大阪府": 0.1034,
    "京都府": 0.1032,
    "神奈川県": 0.1002,
    "愛知県": 0.0995,
    "福岡県": 0.1035,
    "北海道": 0.1044,
}
PENSION_RATE = 0.183  # 厚生年金（全国一律）
KAIGO_RATE = 0.016    # 介護保険（40歳以上一律）

# --- ロジック関数 ---
def get_detailed_report(salary, investment, expense, board_fee_monthly, pref, is_over_40):
    total_income = salary + investment
    taxable_income = total_income - expense
    
    # --- 1. 現状維持 ---
    stay_tax = taxable_income * 0.20 
    stay_profit = taxable_income - stay_tax

    # --- 2. 個人事業主 ---
    solo_taxable = max(0, taxable_income - 650000)
    solo_tax = solo_taxable * 0.20
    solo_hoken = min(1000000, solo_taxable * 0.10) # 国保概算
    solo_profit = taxable_income - solo_tax - solo_hoken

    # --- 3. 法人（全国対応計算） ---
    h_rate = PREF_RATES.get(pref, 0.10) # 選択された県の料率（なければ10%）
    if is_over_40:
        h_rate += KAIGO_RATE
    
    total_shaho_rate = h_rate + PENSION_RATE
    
    # 役員報酬に対する社会保険料（労使合計）
    # ※最低ランク4.5万〜上限まで、より精密な計算（簡易版）
    annual_shaho = (board_fee_monthly * total_shaho_rate) * 12
    
    corp_tax_fixed = 70000 
    corp_setup = 100000    
    
    corp_dobukin_1st = annual_shaho + corp_tax_fixed + corp_setup
    corp_dobukin_2nd = annual_shaho + corp_tax_fixed
    corp_profit_2nd = taxable_income - corp_dobukin_2nd

    return {
        "stay": {"profit": stay_profit, "tax": stay_tax},
        "solo": {"profit": solo_profit, "tax": solo_tax, "hoken": solo_hoken},
        "corp": {"profit": corp_profit_2nd, "dobukin_1st": corp_dobukin_1st, "dobukin_2nd": corp_dobukin_2nd, "h_rate": h_rate}
    }

# --- UIセクション ---
st.title("⚖️ 戦略的・手残り最大化判定（全国対応版）")

# ① 入力エリア
st.header("① 基本データ")
col_a, col_b = st.columns(2)
with col_a:
    salary = st.number_input("現在の給与年収", value=5000000, step=100000)
    investment = st.number_input("投資・副業収入", value=3000000, step=100000)
with col_b:
    pref = st.selectbox("事業所の所在地（都道府県）", list(PREF_RATES.keys()))
    is_over_40 = st.checkbox("40歳以上ですか？（介護保険料の計算）", value=False)
    expense = st.number_input("経費", value=500000, step=50000)

# 計算
data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

# ② 結果表示
st.divider()
results_map = {"現状維持": data["stay"]["profit"], "個人事業主": data["solo"]["profit"], "法人成り": data["corp"]["profit"]}
best_option = max(results_map, key=results_map.get)

st.header(f"② 推奨：{best_option}")
st.info(f"選択された **{pref}** の料率（{data['corp']['h_rate']*100:.2f}%）に基づき計算しました。")

# ③ 詳細（タブ）
tab1, tab2, tab3 = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])
# （※ 各タブ内は前回のロジックと同様）
with tab3:
    st.write(f"**{pref}での法人経営コスト**")
    st.write(f"・社会保険料（労使合計）: 年間 約 {int(data['corp']['dobukin_2nd'] - 70000):,}円")
    st.metric("2年目以降の手残り", f"{int(data['corp']['profit']):,}", delta=f"現状比 +{int(data['corp']['profit'] - data['stay']['profit']):,}円")
