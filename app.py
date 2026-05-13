import streamlit as st
import pandas as pd

# --- ページ設定 ---
st.set_page_config(page_title="合同会社竹輪 | 法人設立ナビ", layout="wide")

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

# --- UIセクション ---
st.title("⚖️ 戦略的・手残り最大化判定（全国対応版）")
st.caption("Produced by 合同会社竹輪")

# ① 入力
st.header("① 基本データ入力")
c1, c2 = st.columns(2)
with c1:
    salary = st.number_input("現在の給与年収 [円]", value=5000000, step=100000)
    investment = st.number_input("投資・副業収入 [円]", value=3000000, step=100000)
with c2:
    pref = st.selectbox("事業所の所在地", list(PREF_RATES.keys()))
    is_over_40 = st.checkbox("40歳以上ですか？", value=False)
    expense = st.number_input("関連経費 [円]", value=500000, step=50000)

# ここで計算を実行（変数 data を作成）
data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

# ② 判定結果
st.divider()
st.header(f"② 判定結果：推奨は「{data['best']}」")

# ③ 詳細タブ
tab_stay, tab_solo, tab_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])
with tab_stay: st.metric("年間手残り", f"{int(data['stay_profit']):,}円")
with tab_solo: st.metric("年間手残り", f"{int(data['solo_profit']):,}円")
with tab_corp: st.metric("2年目以降手残り", f"{int(data['corp_profit']):,}円", delta=f"現状比 +{int(data['corp_profit'] - data['stay_profit']):,}円")

# --- ④ 法人設立ナビ（今回のメイン） ---
st.divider()
if "show_setup" not in st.session_state:
    st.session_state.show_setup = False

# data['best'] が定義された後にボタンを置く
if st.button(f"🚀 {data['best']} を実現するための最短ロードマップを見る"):
    st.session_state.show_setup = True

if st.session_state.show_setup:
    st.header("④ 法人設立・完全ナビゲーション")
    
    # STEP 1: 形態
    corp_type = st.radio("会社の形態を選んでください", ["合同会社（LLC）", "株式会社"], help="資産管理なら合同会社がコスパ最強です。")
    
    # STEP 2: 必要なもの
    st.subheader("🛠️ 準備するものリスト")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("- **個人の実印と印鑑証明**\n- **法人印3点セット** (実印・銀行印・角印)\n- **資本金用の通帳**")
    with col_r:
        st.info("💡 **代表のアドバイス**")
        st.write("法人印はネット注文が最安です。私は1週間かからず揃えました。")
        st.markdown("[👉 法人印のおすすめショップはこちら](https://example.com)")

    # STEP 3: 申請方法の分岐
    st.subheader("📝 申請・定款作成")
    has_card = st.radio("マイナンバーカードを持っていますか？", ["持っている", "持っていない"])
    user_intent = st.radio("申請のスタンスは？", ["なるべく安く、自分でやりたい", "時間は買いたい、プロに任せる"])

    if user_intent == "なるべく安く、自分でやりたい":
        if has_card == "持っている":
            st.success("✅ **「マネーフォワード会社設立」等で電子申請！**")
            st.write("定款の印紙代4万円が0円になります。マイナンバーカードがあれば自宅で完結可能です。")
        else:
            st.warning("⚠️ **定款の電子化だけは外部委託がお得！**")
            st.write("自分で紙の定款を作ると印紙代4万円かかります。5,000円程度の電子定款作成代行サービスを使いましょう。")
    else:
        st.success("✅ **「司法書士」へ丸投げプラン**")
        st.write("書類作成から法務局への提出まで代行。手間を最小化して本業に集中できます。")
        st.markdown("[👉 信頼できる登記代行サービスはこちら](https://example.com)")

    # STEP 4: 税理士判定
    st.divider()
    st.subheader("👨‍💼 顧問税理士の必要性判定")
    if salary + investment > 10000000:
        st.error(f"判定：**税理士を付けるべきです**")
        st.write(f"{pref}周辺で、資産管理会社に詳しい先生への相談を推奨します。")
        st.markdown(f"[👉 {pref}の税理士紹介サービスへ](https://example.com/tax?pref={pref})")
    else:
        st.success(f"判定：**まずは自力でOK！**")
        st.write("まずはクラウド会計ソフトを導入して、自分で管理を始めてみましょう。")
