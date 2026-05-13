import streamlit as st

# --- ページ設定 ---
st.set_page_config(page_title="合同会社竹輪 | 資産形成最大化シミュレーター", layout="wide")

# --- データ定義 ---
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
    
    # 1. 現状維持
    stay_profit = taxable_income - (taxable_income * 0.20)
    # 2. 個人事業主
    solo_taxable = max(0, taxable_income - 650000)
    solo_profit = taxable_income - (solo_taxable * 0.20) - min(1000000, solo_taxable * 0.10)
    # 3. 法人
    h_rate = PREF_RATES.get(pref, 0.10) + (KAIGO_RATE if is_over_40 else 0)
    annual_shaho = (board_fee_monthly * (h_rate + PENSION_RATE)) * 12
    corp_profit_2nd = taxable_income - (annual_shaho + 70000)

    res = {"現状維持": stay_profit, "個人事業主": solo_profit, "法人成り": corp_profit_2nd}
    best = max(res, key=res.get)
    
    return {"best": best, "stay_profit": stay_profit, "solo_profit": solo_profit, "corp_profit": corp_profit_2nd, "shaho": annual_shaho}

# --- ① 入力エリア ---
st.title("⚖️ 戦略的・手残り最大化判定ツール")
st.caption("Produced by 合同会社竹輪")

st.header("1. 基本データの入力")
c1, c2 = st.columns(2)
with c1:
    salary = st.number_input("現在の給与年収 [円]", value=5000000, step=100000)
    investment = st.number_input("投資・副業収入 [円]", value=3000000, step=100000)
with c2:
    pref = st.selectbox("事業所の所在地", list(PREF_RATES.keys()))
    is_over_40 = st.checkbox("40歳以上ですか？", value=False)
    expense = st.number_input("関連経費 [円]", value=500000, step=50000)

data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

# --- ② 判定結果 ---
st.divider()
st.header(f"2. 判定結果：推奨は「{data['best']}」")
st.info(f"💡 {pref}の料率を適用。最も手残りが多くなる形態を算出しました。")

# --- ③ 詳細タブ ---
st.header("3. 詳細シミュレーション比較")
tab_stay, tab_solo, tab_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])
with tab_stay:
    st.metric("年間最終手残り", f"{int(data['stay_profit']):,}円")
    st.write("面倒な手間はありませんが、節税・社保削減の恩恵もありません。")
with tab_solo:
    st.metric("年間最終手残り", f"{int(data['solo_profit']):,}円")
    if data['solo_profit'] < data['stay_profit']:
        st.error("国民健康保険の負担により、現状維持より手残りが減る計算です。")
with tab_corp:
    st.metric("2年目以降の手残り", f"{int(data['corp_profit']):,}円", 
              delta=f"現状比 +{int(data['corp_profit'] - data['stay_profit']):,}円")
    st.success("社会保険料を最適化することで、中長期的な資産形成スピードが最大化します。")

# --- ④ 法人設立ナビ（広告・アフィリエイト導線） ---
st.divider()
if "show_setup" not in st.session_state:
    st.session_state.show_setup = False

if st.button(f"🚀 「{data['best']}」に向けた具体的な手続きを確認する"):
    st.session_state.show_setup = True

if st.session_state.show_setup:
    st.header("4. 法人設立・完全ロードマップ")
    st.write("代表の経験に基づき、迷いやすいポイントを最短ルートで案内します。")

    # STEP 1: 形態
    st.subheader("STEP 1: 会社の形態を選択")
    corp_type = st.radio("どちらの形態で設立しますか？", ["合同会社（LLC）", "株式会社"])
    if corp_type == "合同会社（LLC）":
        st.success("✅ **資産管理・副業法人ならこちら！** 設立費用が安く、維持コストも最小限です。")
    else:
        st.info("✅ **信頼性重視ならこちら。** 外部からの出資や、将来的な上場を視野に入れる場合に適しています。")

    # STEP 2: 準備物（印鑑広告）
    st.subheader("STEP 2: 必要な準備物")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("- **個人の実印・印鑑証明**\n- **法人印3点セット**\n- **資本金（1円〜）**")
    with col_r:
        st.info("💡 **代表のアドバイス：印鑑について**")
        st.write("店舗で作ると高いですが、ネットなら数千円〜で即日発送可能です。")
        # 【広告A：印鑑】
        st.markdown("### [👉 代表も利用したおすすめ印鑑セット](https://your-affiliate-link-hanko.com)")

    # STEP 3: 申請（登記サービス広告）
    st.subheader("STEP 3: 定款作成と法務局への申請")
    has_card = st.radio("マイナンバーカードを持っていますか？", ["持っている", "持っていない"])
    user_intent = st.radio("申請のスタンスを選択してください", ["コスト優先（自分でやる）", "タイパ優先（プロに任せる）"])

    if user_intent == "コスト優先（自分でやる）":
        if has_card == "持っている":
            st.success("🎯 **クラウド設立サービスの電子申請が最適！**")
            st.write("定款印紙代4万円が不要。マイナンバーカードがあればスマホで登記可能です。")
        else:
            st.warning("⚠️ **電子定款作成サービスを使いましょう**")
            st.write("自分ですべて紙でやると4万円損します。代行サービスで安く済ませるのが鉄則です。")
        # 【広告B：登記サービス】
        st.markdown("### [👉 【最短0円】会社設立 Freee / マネーフォワード](https://your-link-setup.com)")
    else:
        st.success("🎯 **司法書士・代行サービスを活用**")
        st.write("書類作成から提出までプロが代行。本業や投資に集中したい方におすすめです。")
        st.markdown("### [👉 登記お任せパックの詳細を見る](https://your-link-pro.com)")

    # STEP 4: 税理士（税理士紹介広告）
    st.divider()
    st.subheader("STEP 4: 顧問税理士の判定")
    # 判定条件：売上+投資が1000万超、または経費が200万超
    if salary + investment > 10000000 or expense > 2000000:
        st.error(f"判定：**税理士を付けることを強く推奨します**")
        st.write(f"規模的に自力での決算は危険です。{pref}周辺で、資産管理会社に強い先生を紹介します。")
        # 【広告C：税理士紹介】
        st.markdown(f"### [🔍 {pref}で評判の良い税理士を無料で見つける](https://your-link-tax.com?pref={pref})")
    else:
        st.success("判定：**まずはクラウド会計で自力運用が可能**")
        st.write("まずは「マネーフォワード」や「Freee」で日々の帳簿付けを始めましょう。")

st.divider()
st.caption(f"現在の試算条件：{pref} / {'40歳以上' if is_over_40 else '40歳未満'} / 役員報酬4.5万円")
