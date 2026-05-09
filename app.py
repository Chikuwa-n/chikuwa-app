import streamlit as st
import pandas as pd

# --- ページ設定 ---
st.set_page_config(page_title="合同会社竹輪 | 3択判定ツール", layout="wide")

# --- 計算ロジック ---
def get_report(salary, investment, expense, board_fee_monthly):
    total_income = salary + investment
    taxable_income = total_income - expense
    
    # 1. 現状維持（分離課税・総合課税の簡易計算）
    stay_tax = taxable_income * 0.20 
    stay_profit = taxable_income - stay_tax

    # 2. 個人事業主（青色申告）
    solo_taxable = max(0, taxable_income - 650000)
    solo_tax = solo_taxable * 0.20
    # 国民健康保険：所得の約10%（上限約100万と想定）
    solo_hoken = min(1000000, solo_taxable * 0.10) 
    solo_profit = taxable_income - solo_tax - solo_hoken

    # 3. 法人（資産管理会社）
    # 社会保険料：役員報酬4.5万なら年間約15.5万（京都・労使合計）
    corp_shaho = 155000 if board_fee_monthly <= 50000 else (board_fee_monthly * 0.30 * 12)
    corp_tax_fixed = 70000 
    corp_setup = 100000    
    
    corp_dobukin_1st = corp_shaho + corp_tax_fixed + corp_setup
    corp_dobukin_2nd = corp_shaho + corp_tax_fixed
    corp_profit_2nd = taxable_income - corp_dobukin_2nd

    return {
        "stay": {"profit": stay_profit, "tax": stay_tax, "hoken": 0},
        "solo": {"profit": solo_profit, "tax": solo_tax, "hoken": solo_hoken},
        "corp": {"profit": corp_profit_2nd, "dobukin_1st": corp_dobukin_1st, "dobukin_2nd": corp_dobukin_2nd}
    }

# --- UIセクション ---
st.title("⚖️ 戦略的・手残り最大化判定シミュレーター")
st.caption("Produced by 合同会社竹輪")

# ① 入力エリア
st.header("① 現在の収支を入力")
c1, c2, c3 = st.columns(3)
with c1: salary = st.number_input("給与年収 [円]", value=5000000, step=100000)
with c2: investment = st.number_input("投資・副業収入 [円]", value=3000000, step=100000)
with c3: expense = st.number_input("経費 [円]", value=500000, step=50000)

# 計算実行
data = get_report(salary, investment, expense, 45000)

# ② 判定結果
st.divider()
# 簡易的な判定ロジック：最も手残りが多いものを抽出
results_map = {
    "現状維持": data["stay"]["profit"],
    "個人事業主": data["solo"]["profit"],
    "法人成り": data["corp"]["profit"]
}
best_option = max(results_map, key=results_map.get)

st.header(f"② 判定結果：推奨は「{best_option}」")
st.write(f"あなたの収支状況では、**{best_option}** が最も効率的に資産を残せる可能性が高いです。")

# ③ 詳細シミュレーション（切り替えタブ）
st.divider()
st.header("③ 詳細シミュレーション比較")
st.write("各ボタンを押すと、それぞれのシナリオでの「なぜ？」がわかります。")

tab_stay, tab_solo, tab_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])

with tab_stay:
    st.subheader("現状維持プラン")
    st.info("💡 **メリット:** 事務手間がゼロ。確定申告も特定口座なら不要。")
    st.warning("⚠️ **デメリット:** 節税手段が限られ、収入増がそのまま税負担増に直結。")
    
    st.write(f"・想定税金（所得・住民税）: 約 {int(data['stay']['tax']):,}円")
    st.write(f"・社会保険料: 給与天引きのみ（追加なし）")
    st.metric("年間最終手残り", f"{int(data['stay']['profit']):,}")

with tab_solo:
    st.subheader("個人事業主プラン（青色申告）")
    st.info("💡 **メリット:** 65万円の控除や経費計上が可能。")
    st.error("❌ **デメリット:** 利益が増えると「国民健康保険料」が激増し、節税分を食い潰す。")
    
    st.write(f"・青色申告による税軽減: 適用済み")
    st.write(f"・国民健康保険料（ドブ金）: 約 {int(data['solo']['hoken']):,}円")
    st.metric("年間最終手残り", f"{int(data['solo']['profit']):,}")
    if data['solo']['profit'] < data['stay']['profit']:
        st.write("※現在は「社会保険料」の負担が重く、現状維持より手残りが少なくなっています。")

with tab_corp:
    st.subheader("法人成りプラン（資産管理会社）")
    st.success("✅ **メリット:** 社会保険料を一定額に固定。最も「ドブ金」を抑えられる。")
    st.warning("⚠️ **デメリット:** 設立費用や法人住民税（均等割）などの固定費が発生。")
    
    col_corp1, col_corp2 = st.columns(2)
    with col_corp1:
        st.write("**【初年度（設立時）】**")
        st.write(f"・設立費用等: 100,000円")
        st.write(f"・維持コスト(社保等): {int(data['corp']['dobukin_2nd']):,}円")
        st.write(f"・初年度ドブ金計: {int(data['corp']['dobukin_1st']):,}円")
    with col_corp2:
        st.write("**【2年目以降】**")
        st.write(f"・固定コスト: 70,000円")
        st.write(f"・社会保険料: {int(data['corp']['dobukin_2nd']-70000):,}円")
        st.write(f"・2年目ドブ金計: {int(data['corp']['dobukin_2nd']):,}円")
    
    st.metric("2年目以降の手残り", f"{int(data['corp']['profit']):,}", 
              delta=f"現状維持比 +{int(data['corp']['profit'] - data['stay']['profit']):,}円")

st.divider()
st.caption("※本ツールは概算です。実際の設立・申告に際しては税理士等の専門家にご相談ください。")
