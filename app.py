import streamlit as st
import pandas as pd

# --- ページ設定 ---
st.set_page_config(page_title="合同会社竹輪 | 3択・全国対応判定ツール", layout="wide")

# --- 全国料率データ（令和6年度 協会けんぽ 概算） ---
PREF_RATES = {
    "東京都": 0.0998,
    "神奈川県": 0.1002,
    "埼玉県": 0.1027,
    "千葉県": 0.1024,
    "愛知県": 0.0995,
    "京都府": 0.1032,
    "大阪府": 0.1034,
    "兵庫県": 0.1030,
    "福岡県": 0.1035,
    "北海道": 0.1044,
}
PENSION_RATE = 0.183  # 厚生年金（全国一律）
KAIGO_RATE = 0.016    # 介護保険（40歳以上）

# --- ロジック関数 ---
def get_detailed_report(salary, investment, expense, board_fee_monthly, pref, is_over_40):
    total_income = salary + investment
    taxable_income = total_income - expense
    
    # 1. 現状維持（給与 + 分離課税等）
    stay_tax = taxable_income * 0.20 
    stay_profit = taxable_income - stay_tax

    # 2. 個人事業主（青色申告）
    solo_taxable = max(0, taxable_income - 650000)
    solo_tax = solo_taxable * 0.20
    solo_hoken = min(1000000, solo_taxable * 0.10) 
    solo_profit = taxable_income - solo_tax - solo_hoken

    # 3. 法人（全国対応計算）
    h_rate = PREF_RATES.get(pref, 0.10) 
    if is_over_40:
        h_rate += KAIGO_RATE
    
    total_shaho_rate = h_rate + PENSION_RATE
    # 労使折半合計の社保負担
    annual_shaho = (board_fee_monthly * total_shaho_rate) * 12
    
    corp_tax_fixed = 70000 
    corp_setup = 100000    
    
    corp_dobukin_1st = annual_shaho + corp_tax_fixed + corp_setup
    corp_dobukin_2nd = annual_shaho + corp_tax_fixed
    corp_profit_2nd = taxable_income - corp_dobukin_2nd

    return {
        "stay": {"profit": stay_profit, "tax": stay_tax},
        "solo": {"profit": solo_profit, "tax": solo_tax, "hoken": solo_hoken},
        "corp": {"profit": corp_profit_2nd, "dobukin_1st": corp_dobukin_1st, "dobukin_2nd": corp_dobukin_2nd, "h_rate": h_rate},
        "params": {"pref": pref, "is_over_40": is_over_40}
    }

# --- UIセクション ---
st.title("⚖️ 戦略的・手残り最大化判定（全国対応版）")
st.caption("Produced by 合同会社竹輪")

# ① 入力エリア
st.header("① 基本データ入力")
col_in1, col_in2 = st.columns(2)
with col_in1:
    salary = st.number_input("現在の給与年収 [円]", value=5000000, step=100000)
    investment = st.number_input("投資・副業収入 [円]", value=3000000, step=100000)
with col_in2:
    pref = st.selectbox("事業所の所在地（都道府県）", list(PREF_RATES.keys()))
    is_over_40 = st.checkbox("40歳以上ですか？（介護保険料の加算）", value=False)
    expense = st.number_input("関連経費 [円]", value=500000, step=50000)

# 計算実行
data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

# ② 判定結果
st.divider()
results_map = {"現状維持": data["stay"]["profit"], "個人事業主": data["solo"]["profit"], "法人成り": data["corp"]["profit"]}
best_option = max(results_map, key=results_map.get)

st.header(f"② 判定結果：推奨は「{best_option}」")
st.info(f"💡 {pref}の健康保険料率（{'40歳以上' if is_over_40 else '40歳未満'}）を適用してシミュレーションしました。")

# ③ 詳細シミュレーション（切り替えタブ）
st.divider()
st.header("③ 詳細シミュレーション比較")
st.write("それぞれのプランを選択して、内訳と「なぜ損か・得か」を確認してください。")

tab_stay, tab_solo, tab_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])

with tab_stay:
    st.subheader("現状維持プランの内訳")
    st.info("💡 手間はないが、効率的な手残りの最大化は難しい状態です。")
    st.write(f"・想定される税負担（所得・住民税）: 約 {int(data['stay']['tax']):,}円")
    st.write(f"・社会保険料: 給与天引きのみ（追加なし）")
    st.metric("最終的な年間手残り", f"{int(data['stay']['profit']):,}円")
    st.warning("これ以上の節税や社保削減の余地がありません。")

with tab_solo:
    st.subheader("個人事業主プラン（青色申告）の内訳")
    st.info("💡 65万円の控除を使えますが、健康保険料の跳ね上がりに注意。")
    st.write(f"・青色申告特別控除: 650,000円 適用済み")
    st.write(f"・国民健康保険料（ドブ金）: 約 {int(data['solo']['hoken']):,}円")
    st.write(f"・想定される税負担: 約 {int(data['solo']['tax']):,}円")
    st.metric("最終的な年間手残り", f"{int(data['solo']['profit']):,}円")
    if data['solo']['profit'] < data['stay']['profit']:
        st.error("❌ 現在の収支では、国民健康保険料の負担が重すぎて「現状維持」より損をしています。")

with tab_corp:
    st.subheader(f"法人成りプラン（{pref}・資産管理会社）の内訳")
    st.success("✅ 社会保険料を最低ランクに固定することで、投資効率を最大化します。")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write("**【初年度（設立コストあり）】**")
        st.write(f"・設立費用等: 100,000円")
        st.write(f"・維持コスト(社保・均等割): {int(data['corp']['dobukin_2nd']):,}円")
        st.write(f"・合計ドブ金: {int(data['corp']['dobukin_1st']):,}円")
    with col_c2:
        st.write("**【2年目以降（安定期）】**")
        st.write(f"・法人住民税（均等割）: 70,000円")
        st.write(f"・社会保険料（労使合計）: {int(data['corp']['dobukin_2nd'] - 70000):,}円")
        st.write(f"・合計ドブ金: {int(data['corp']['dobukin_2nd']):,}円")
    
    st.metric("2年目以降の年間手残り", f"{int(data['corp']['profit']):,}円", 
              delta=f"現状維持比 +{int(data['corp']['profit'] - data['stay']['profit']):,}円")

st.divider()
st.caption("Produced by 合同会社竹輪 | ※本ツールは概算です。正確な情報は専門家にご確認ください。")
