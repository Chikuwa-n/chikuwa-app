import streamlit as st

# --- SEO対策：検索エンジンに拾わせるための設定 ---
st.set_page_config(
    page_title="法人成り・個人事業主の社会保険料計算比較ツール | 合同会社竹輪",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 計算ロジック ---
def get_detailed_report(salary, investment, expense, board_fee_monthly, pref, is_over_40):
    total_income = salary + investment
    taxable_income = total_income - expense
    
    # 1. 現状維持（所得税・住民税 合計約20%想定）
    stay_profit = taxable_income - (taxable_income * 0.20)
    
    # 2. 個人事業主（青色申告特別控除65万円適用）
    solo_taxable = max(0, taxable_income - 650000)
    solo_tax = solo_taxable * 0.20
    # 国民健康保険料（所得の約10%・上限考慮の概算）
    solo_hoken = min(1000000, solo_taxable * 0.10)
    solo_profit = taxable_income - solo_tax - solo_hoken
    
    # 3. 法人（協会けんぽ都道府県別料率 + 厚生年金 18.3%）
    h_rate = PREF_RATES.get(pref, 0.10) + (0.016 if is_over_40 else 0)
    total_shaho_rate = h_rate + 0.183
    # 役員報酬に対する社会保険料（労使折半合計）
    annual_shaho = (board_fee_monthly * total_shaho_rate) * 12
    # 法人住民税 均等割（約7万円）
    corp_profit_2nd = taxable_income - (annual_shaho + 70000)

    res = {"現状維持": stay_profit, "個人事業主": solo_profit, "法人成り": corp_profit_2nd}
    return {
        "best": max(res, key=res.get), 
        "stay_profit": stay_profit, 
        "solo_profit": solo_profit, 
        "corp_profit": corp_profit_2nd,
        "shaho": annual_shaho
    }

# --- データ定義 ---
PREF_RATES = {
    "東京都": 0.0998, "神奈川県": 0.1002, "埼玉県": 0.1027, "千葉県": 0.1024,
    "愛知県": 0.0995, "京都府": 0.1032, "大阪府": 0.1034, "兵庫県": 0.1030,
    "福岡県": 0.1035, "北海道": 0.1044,
}

# --- ヘッダー：SEOキーワードセクション ---
st.title("⚖️ 法人成り・個人事業主シミュレーター")
st.subheader("社会保険料・所得税・法人税を考慮した「手残り最大化」判定")

st.markdown("""
**副業の法人化**や**資産管理会社の設立**、**マイクロ法人**での社会保険料適正化を検討中の方へ。  
本ツールは、全国の協会けんぽ料率に基づき、**役員報酬の最適化**による手残り金額の変化を瞬時に算出します。
""")

# --- ① 入力エリア ---
st.header("1. 収支データの入力")
with st.expander("💡 入力項目のヒントを見る", expanded=True):
    st.caption("給与所得と副業・投資収益を合算し、青色申告や法人化による節税効果を測定します。")

c1, c2 = st.columns(2)
with c1:
    salary = st.number_input("現在の本業給与（年収） [円]", value=5000000, step=100000, help="源泉徴収票の額面を入力してください。")
    investment = st.number_input("投資・副業・事業収益 [円]", value=3000000, step=100000, help="売上から直接経費を引いた利益ベースです。")
with c2:
    pref = st.selectbox("事業所の所在地（都道府県）", list(PREF_RATES.keys()), help="法人所在地の健康保険料率を適用します。")
    is_over_40 = st.checkbox("40歳以上（介護保険料 加算対象）", value=False)
    expense = st.number_input("法人化後に経費化できる金額 [円]", value=500000, step=50000, help="自宅按分や旅費交通費など。")

data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

# --- ② 判定結果 ---
st.divider()
st.header(f"2. 判定：あなたに最適な形態は「{data['best']}」")
st.write(f"現在の収支では、**{data['best']}** を選択することで、税金と社会保険料の「ドブ金」を最小化し、効率的な資産形成が可能です。")

# --- ③ 詳細タブ ---
st.header("3. 形態別シミュレーション詳細")
t_stay, t_solo, t_corp = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り"])

with t_stay:
    st.metric("年間最終手残り（概算）", f"{int(data['stay_profit']):,}円")
    st.write("・メリット：事務手続きが一切不要。")
    st.write("・デメリット：節税の選択肢がなく、収入増がそのまま税負担増に。")

with t_solo:
    st.metric("年間最終手残り（概算）", f"{int(data['solo_profit']):,}円")
    st.write("・メリット：青色申告特別控除（65万円）が利用可能。")
    st.error("・デメリット：利益増に伴い「国民健康保険料」が激増するリスク。")

with t_corp:
    st.metric("2年目以降の手残り", f"{int(data['corp_profit']):,}円", 
              delta=f"現状比 +{int(data['corp_profit'] - data['stay_profit']):,}円")
    st.success("・メリット：役員報酬を低額（月4.5万等）に設定し、社会保険料を全国最低水準に固定可能。")

# --- ④ 法人設立ロードマップ（集客・広告導線） ---
st.divider()
if "show_setup" not in st.session_state: st.session_state.show_setup = False

if st.button(f"🚀 「{data['best']}」の具体的な設立費用と手順を確認する"):
    st.session_state.show_setup = True

if st.session_state.show_setup:
    st.header("4. 法人設立・完全ロードマップ")
    
    # STEP 1: 会社形態
    st.subheader("STEP 1: 会社形態の選択（合同会社 vs 株式会社）")
    st.write("資産管理会社や自分一人の「マイクロ法人」なら、設立費用が安い**合同会社（LLC）**がおすすめです。")
    st.radio("検討中の形態", ["合同会社", "株式会社"], horizontal=True, label_visibility="collapsed")

    # STEP 2: 準備物（印鑑）
    st.subheader("STEP 2: 設立に必要な準備物")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""
        - **実印・印鑑証明**: 役員全員分が必要
        - **法人印3点セット**: 代表印・銀行印・角印
        - **資本金**: 1円から設定可能
        """)
    with col_r:
        st.info("💡 **法人印について**")
        st.write("法務局への登記には法人実印が必須です。品質とコストを両立するなら、こちらが便利です。")
        st.link_button("はんこ森：会社設立印鑑3点セット ↗️", "https://your-affiliate-link-hankomori.com")

    # STEP 3: 登記申請（会社設立サービス）
    st.subheader("STEP 3: 定款作成と法務局への申請")
    st.write("電子署名を利用すれば、定款に貼る**印紙代（4万円）が0円**になります。")
    st.link_button("【最短0円】会社設立クラウドサービス ↗️", "https://your-link-setup.com")

    # STEP 4: 税理士判定
    st.divider()
    st.subheader("STEP 4: 顧問税理士の必要性")
    if salary + investment > 10000000:
        st.error(f"💡 判定：**税理士の関与を推奨します**")
        st.write(f"{pref}周辺で資産管理会社に強い先生を見つけることで、税務リスクを回避できます。")
        st.link_button(f"{pref}の税理士無料紹介 ↗️", f"https://your-link-tax.com?pref={pref}")
    else:
        st.success("💡 判定：**まずは自力での運用が可能です**")
        st.write("「マネーフォワード」や「Freee」などの会計ソフトで日々の記帳を始めましょう。")

st.divider()
st.caption(f"Produced by 合同会社竹輪 | 京都から全国の資産形成を支援 | 2026年最新料率対応")
