import streamlit as st
import pandas as pd

# --- 設定 ---
st.set_page_config(page_title="合同会社竹輪 | 3択比較シミュレーター", layout="wide")

# --- ロジック関数 ---
def get_report(salary, investment, expense, board_fee_monthly):
    total_income = salary + investment
    taxable_income = total_income - expense
    
    # 1. 現状維持（給与+雑所得/分離課税を簡易化）
    # 社会保険料は給与から天引き（変わらず）、投資分に住民税・所得税
    stay_tax = taxable_income * 0.20 # 概算
    stay_profit = taxable_income - stay_tax

    # 2. 個人事業主（青色申告）
    # 青色控除65万、国民健康保険（上限あり）が発生
    solo_taxable = max(0, taxable_income - 650000)
    solo_tax = solo_taxable * 0.20
    solo_hoken = min(1000000, solo_taxable * 0.10) # 国保概算（上限考慮）
    solo_profit = taxable_income - solo_tax - solo_hoken

    # 3. 法人（資産管理会社）
    annual_board = board_fee_monthly * 12
    # 社会保険料（京都・最低ランク4.5万想定なら年間約15.5万）
    corp_shaho = 155000 if board_fee_monthly <= 50000 else (board_fee_monthly * 0.30 * 12)
    corp_tax_fixed = 70000 # 均等割
    corp_setup = 100000    # 設立費用
    
    corp_dobukin_1st = corp_shaho + corp_tax_fixed + corp_setup
    corp_dobukin_2nd = corp_shaho + corp_tax_fixed
    corp_profit_2nd = taxable_income - corp_dobukin_2nd

    return {
        "stay": {"profit": stay_profit, "tax": stay_tax, "hoken": 0},
        "solo": {"profit": solo_profit, "tax": solo_solo_tax if 'solo_tax' in locals() else solo_tax, "hoken": solo_hoken},
        "corp": {"profit": corp_profit_2nd, "dobukin_1st": corp_dobukin_1st, "dobukin_2nd": corp_dobukin_2nd}
    }

# --- UI ---
st.title("⚖️ 戦略的・手残り最大化判定")
st.caption("現状維持・個人・法人の3ルートから、最適な資産形成パスを導き出します。")

# 入力
st.header("① 基本データ")
c1, c2, c3 = st.columns(3)
with c1: salary = st.number_input("給与年収", value=5000000, step=100000)
with c2: investment = st.number_input("投資/副業収入", value=3000000, step=100000)
with c3: expense = st.number_input("関連経費", value=500000, step=50000)

# 判定
data = get_report(salary, investment, expense, 45000)
best = "法人成り" if data["corp"]["profit"] > data["stay"]["profit"] else "現状維持"

st.divider()
st.header(f"② 判定結果：推奨は「{best}」")

# 詳細シミュレーション（ここが代表のこだわりポイント）
st.divider()
st.header("③ 各シナリオの詳細比較")
st.write("なぜその判定になったのか、それぞれの内訳を確認してください。")

# 3択のタブを作成
tab_stay, tab_solo, tab_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])

with tab_stay:
    st.subheader("現状維持（給与＋特定口座/雑所得）")
    st.info("💡 特徴：面倒な手続きが一切なく、最も手軽です。")
    st.write(f"・想定される所得税/住民税: 約 {data['stay']['tax']:,}円")
    st.write(f"・社会保険料: 給与天引きのみ（追加なし）")
    st.metric("最終的な年間手残り", f"{int(data['stay']['profit']):,}円")
    st.warning("⚠️ 懸念：投資利益が増えるほど、累進課税や分離課税のメリットが薄れる可能性があります。")

with tab_solo:
    st.subheader("個人事業主（青色申告）")
    st.info("💡 特徴：65万円の控除が受けられますが、国民健康保険が所得に連動して重くなります。")
    st.write(f"・節税効果（青色控除）: -650,000円分")
    st.write(f"・国民健康保険料（ドブ金）: 約 {int(data['solo']['hoken']):,}円")
    st.metric("最終的な年間手残り", f"{int(data['solo']['profit']):,}円")
    st.error("❌ 懸念：この収入規模では、国民健康保険料の増加分が節税額を上回る「社保負け」のリスクがあります。")

with tab_corp:
    st.subheader("法人成り（資産管理会社）")
    st.info("💡 特徴：社会保険料を固定（最低ランク）に抑え、手残りを最大化する戦略です。")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write("**【初年度】**")
        st.write(f"・設立費用: 100,000円")
        st.write(f"・維持コスト(社保等): {data['corp']['dobukin_2nd']:,}円")
        st.write(f"・合計ドブ金: {data['corp']['dobukin_1st']:,}円")
    with col_c2:
        st.write("**【2年目以降】**")
        st.write(f"・維持コスト(社保等): {data['corp']['dobukin_2nd']:,}円")
        st.write(f"・合計ドブ金: {data['corp']['dobukin_2nd']:,}円")
    
    st.metric("2年目以降の年間手残り", f"{int(data['corp']['profit']):,}円", delta=f"+{int(data['corp']['profit'] - data['stay']['profit']):,}円（現状維持比）")
    st.success("✅ メリット：社保削減により、中長期的に最もキャッシュが残ります。")

st.divider()
st.caption("Produced by 合同会社竹輪 | 京都から資産形成を自動化する")
