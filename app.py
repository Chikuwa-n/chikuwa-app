import streamlit as st

# --- ページ設定 ---
st.set_page_config(page_title="合同会社竹輪 | 資産形成最大化シミュレーター", layout="wide")

# --- データ定義（令和6年度 協会けんぽ料率 概算） ---
PREF_RATES = {
    "東京都": 0.0998, "神奈川県": 0.1002, "埼玉県": 0.1027, "千葉県": 0.1024,
    "愛知県": 0.0995, "京都府": 0.1032, "大阪府": 0.1034, "兵庫県": 0.1030,
    "福岡県": 0.1035, "北海道": 0.1044,
}
PENSION_RATE = 0.183
KAIGO_RATE = 0.016

# --- 計算ロジック ---
def get_detailed_report(salary, investment, expense, board_fee_monthly, pref, is_over_40):
    total_income = salary + investment
    taxable_income = total_income - expense
    stay_profit = taxable_income - (taxable_income * 0.20)
    solo_taxable = max(0, taxable_income - 650000)
    solo_profit = taxable_income - (solo_taxable * 0.20) - min(1000000, solo_taxable * 0.10)
    h_rate = PREF_RATES.get(pref, 0.10) + (KAIGO_RATE if is_over_40 else 0)
    annual_shaho = (board_fee_monthly * (h_rate + PENSION_RATE)) * 12
    corp_profit_2nd = taxable_income - (annual_shaho + 70000)
    res = {"現状維持": stay_profit, "個人事業主": solo_profit, "法人成り": corp_profit_2nd}
    return {"best": max(res, key=res.get), "stay_profit": stay_profit, "solo_profit": solo_profit, "corp_profit": corp_profit_2nd}

# --- UIセクション ---
st.title("⚖️ 戦略的・手残り最大化判定ツール")
st.caption("Produced by 合同会社竹輪")

st.header("1. 基本データの入力")
c1, c2 = st.columns(2)
with c1:
    salary = st.number_input("現在の給与年収 [円]", value=5000000, step=100000)
    investment = st.number_input("投資・副業収入 [円]", value=3000000, step=100000)
with c2:
    pref = st.selectbox("事業所の所在地", list(PREF_RATES.keys()))
    is_over_40 = st.checkbox("40歳以上ですか？（介護保険料の加算）", value=False)
    expense = st.number_input("関連経費 [円]", value=500000, step=50000)

data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

st.divider()
st.header(f"2. 判定結果：推奨は「{data['best']}」")

st.header("3. 詳細シミュレーション比較")
tab_stay, tab_solo, tab_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])
with tab_stay: st.metric("年間最終手残り", f"{int(data['stay_profit']):,}円")
with tab_solo: st.metric("年間最終手残り", f"{int(data['solo_profit']):,}円")
with tab_corp: 
    st.metric("2年目以降の手残り", f"{int(data['corp_profit']):,}円", delta=f"現状比 +{int(data['corp_profit'] - data['stay_profit']):,}円")

# --- 設立ナビゲーション ---
st.divider()
if "show_setup" not in st.session_state: st.session_state.show_setup = False

if st.button(f"🚀 「{data['best']}」の具体的手続きに進む"):
    st.session_state.show_setup = True

if st.session_state.show_setup:
    st.header("4. 法人設立ロードマップ")
    
    # STEP 1: 形態
    st.subheader("STEP 1: 形態の選択")
    corp_type = st.radio("設立する会社の形態", ["合同会社（LLC）", "株式会社"], horizontal=True)
    st.caption("※資産管理・節税目的であれば、設立費用が安い「合同会社」が合理的です。")

    # STEP 2: 準備物（はんこ森リンク）
    st.subheader("STEP 2: 必要な準備物")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("- **個人の実印・印鑑証明**\n- **法人印3点セット** (代表印・銀行印・角印)\n- **資本金** (1円〜)")
    with col_r:
        st.info("💡 **推奨リソース**")
        st.write("法人印は「実印・銀行印・角印」の3点が必要です。品質と価格のバランスから、私はこちらを推奨しています。")
        # はんこ森への導線（さりげなく）
        st.link_button("はんこ森：会社設立3点セット ↗️", "https://your-affiliate-link-hankomori.com")

    # STEP 3: 申請方法
    st.subheader("STEP 3: 定款作成と登記申請")
    has_card = st.radio("マイナンバーカードの有無", ["持っている", "持っていない"], horizontal=True)
    user_intent = st.radio("申請のスタイル", ["コスト優先（自分で行う）", "タイパ優先（プロに任せる）"], horizontal=True)

    if user_intent == "コスト優先（自分で行う）":
        st.success("🎯 **クラウド設立サービスの活用**")
        st.write("電子署名を利用することで、定款の印紙代（4万円）を節約可能です。")
        st.link_button("会社設立クラウドサービスを確認 ↗️", "https://your-link-setup.com")
    else:
        st.success("🎯 **司法書士・代行サービスの活用**")
        st.write("書類作成から法務局への提出まで一任し、時間を節約する選択です。")
        st.link_button("登記代行パックの詳細 ↗️", "https://your-link-pro.com")

    # STEP 4: 税理士
    st.divider()
    st.subheader("STEP 4: 顧問税理士の検討")
    if salary + investment > 10000000:
        st.error(f"💡 **税理士の関与をおすすめします**")
        st.write(f"現在の収支規模では、正確な決算と節税のために専門家が必要です。{pref}周辺で資産管理会社に強い先生をご案内できます。")
        st.link_button(f"{pref}の税理士無料紹介 ↗️", f"https://your-link-tax.com?pref={pref}")
    else:
        st.success("💡 **まずはご自身での運用が可能です**")
        st.write("クラウド会計ソフトを導入し、まずは自力で日々の管理を始めてみましょう。")

st.divider()
st.caption(f"試算条件: {pref} / {'40歳以上' if is_over_40 else '40歳未満'} / 役員報酬4.5万円")
