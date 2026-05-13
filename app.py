import streamlit as st

# --- 1. SEO & メタデータ設定（検索エンジンに「何についてのサイトか」を伝える） ---
st.set_page_config(
    page_title="マイクロ法人・資産管理会社の社会保険料削減シミュレーター | 合同会社竹輪",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. データ定義（2026年度 協会けんぽ料率 概算） ---
PREF_RATES = {
    "東京都": 0.0998, "神奈川県": 0.1002, "埼玉県": 0.1027, "千葉県": 0.1024,
    "愛知県": 0.0995, "京都府": 0.1032, "大阪府": 0.1034, "兵庫県": 0.1030,
    "福岡県": 0.1035, "北海道": 0.1044,
}

# --- 3. 計算ロジック ---
def get_detailed_report(salary, investment, expense, board_fee_monthly, pref, is_over_40):
    total_income = salary + investment
    taxable_income = total_income - expense
    
    # 現状維持（概算）
    stay_profit = taxable_income - (taxable_income * 0.20)
    
    # 個人事業主（青色控除考慮・国保上限考慮）
    solo_taxable = max(0, taxable_income - 650000)
    solo_hoken = min(1000000, solo_taxable * 0.10)
    solo_profit = taxable_income - (solo_taxable * 0.20) - solo_hoken
    
    # 法人（社会保険料適正化スキーム）
    h_rate = PREF_RATES.get(pref, 0.10) + (0.016 if is_over_40 else 0)
    annual_shaho = (board_fee_monthly * (h_rate + 0.183)) * 12
    corp_profit_2nd = taxable_income - (annual_shaho + 70000) # 均等割含む

    res = {"現状維持": stay_profit, "個人事業主": solo_profit, "法人成り": corp_profit_2nd}
    return {"best": max(res, key=res.get), "stay_profit": stay_profit, "solo_profit": solo_profit, "corp_profit": corp_profit_2nd}

# --- 4. ヘッダー：コアキーワード・セクション ---
st.title("⚖️ 資産管理会社・マイクロ法人設立シミュレーター")
st.caption("京都の現役学生が開発 | 実体験に基づく「役員報酬4.5万円」最適化検証")

st.markdown("""
### ターゲットとなる具体的な悩み
*   **本業年収500万〜1500万**のサラリーマンで、副業収益の税・社保を最適化したい。
*   **役員報酬を月額4.5万円**（厚生年金下限）に設定し、社会保険料を全国最低水準に固定したい。
*   **京都**をはじめとする各都道府県の料率に基づき、法人成りの損益分岐点を正確に知りたい。
*   **匿名性を維持**しつつ、自分一人で合同会社を最短・最安で立ち上げたい。
""")

# --- 5. 入力エリア ---
st.header("1. シミュレーション条件の入力")
c1, c2 = st.columns(2)
with c1:
    salary = st.number_input("現在の本業年収（額面） [円]", value=5000000, step=100000)
    investment = st.number_input("副業利益・投資収益 [円]", value=3000000, step=100000)
with c2:
    pref = st.selectbox("法人の所在地（都道府県）", list(PREF_RATES.keys()))
    is_over_40 = st.checkbox("40歳以上ですか？（介護保険料の算入）", value=False)
    expense = st.number_input("法人化で経費化する予定額 [円]", value=500000, step=50000)

data = get_detailed_report(salary, investment, expense, 45000, pref, is_over_40)

# --- 6. 判定・比較結果 ---
st.divider()
st.header(f"2. 判定結果：推奨は「{data['best']}」")

t1, t2, t3 = st.tabs(["🏠 現状維持", "👤 個人事業主", "🏢 法人成り（推奨）"])
with t1: st.metric("年間最終手残り", f"{int(data['stay_profit']):,}円")
with t2: st.metric("年間最終手残り", f"{int(data['solo_profit']):,}円")
with t3: 
    st.metric("2年目以降の手残り", f"{int(data['corp_profit']):,}円", 
              delta=f"現状比 +{int(data['corp_profit'] - data['stay_profit']):,}円")
    st.success("社会保険料削減スキームを適用することで、手残りを最大化できます。")
# ここから会計ソフトの動線
    st.markdown("---")
    st.subheader("🏢 法人化をスムーズに進めるための推奨ツール")
    st.write("法人登記から日々の経理まで自動化できるクラウドサービスです。")

    col_freee, col_mf = st.columns(2)
    
    with col_freee:
        st.write("**freee**")
        st.caption("初めての法人設立に特化。知識がなくても簡単に書類が作成できます。")
        st.link_button("まずは無料で使ってみる", "https://px.a8.net/svt/ejp?a8mat=4B3PIX+62I3SI+3SPO+9FL80Y") # ここにコピーしたURL

    with col_mf:
        # マネーフォワード等も提携済みならここに配置
        st.write("**マネーフォワード クラウド**")
        st.caption("仕訳の自動化が強力。銀行口座やカードとの連携が非常にスムーズです。")
        st.link_button("法人用アカウントを作成する", "https://px.a8.net/svt/ejp?a8mat=YYYYY") # ここにコピーしたURL

    st.info("💡 **リテラシー重視のアドバイス**\n\n"
            "マイクロ法人の運営は「いかに事務作業を減らすか」が鍵です。会計ソフトを導入することで、"
            "税理士に丸投げせずとも自分で決算まで完結できる体制が整います。")
# --- 7. 法人設立ナビ（はんこ森連携） ---
st.divider()
if "show_setup" not in st.session_state: st.session_state.show_setup = False
if st.button(f"🚀 「{data['best']}」の具体的なコストと設立手順を表示"):
    st.session_state.show_setup = True

if st.session_state.show_setup:
    st.header("3. マイクロ法人・最短設立ガイド")
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🛠️ 準備すべきもの")
        st.write("・個人の実印と印鑑証明（各1通）")
        st.write("・法人印3点セット（代表印・銀行印・角印）")
        st.write("・資本金（1円〜）が振り込まれた通帳のコピー")
    with col_r:
        st.info("💡 **リコメンド(広告ではありません)**")
        st.write("アフィリエイト提携はありませんが、私は『はんこ森』で買いました。印鑑は「実印・銀行印・角印」の3点が必要です。3点セットで3,750円と、他社より圧倒的に安かったです。無理に高い店で買う必要はありません。")
        st.link_button("はんこ森：会社設立印鑑3点セット ↗️", "https://hankomori.com/SHOP/COP-3SET-AKNJ.html?gad_source=1&gad_campaignid=20522573694&gbraid=0AAAAADHGPQYBxVIogTuZ1qiGPADQHCy-V&gclid=CjwKCAjwn4vQBhBsEiwAq3hhN5jUxsp-VkYJ9CYvF6SiCO31EQaat1zItZWHjSR-98QDZdi8Lkr4WRoCwtoQAvD_BwE")

    st.subheader("📝 定款作成と法務局申請")
    st.write("電子申請を利用することで、定款印紙代（4万円）を確実に0円にします。")
    st.link_button("会社設立クラウドサービス一覧 ↗️", "https://px.a8.net/svt/ejp?a8mat=4B3PIX+6BFLV6+4JGQ+HV7V6")

# --- 8. 検索エンジン向けFAQ（SEO強化） ---
st.divider()
st.header("📋 マイクロ法人設立に関するFAQ")
f1, f2 = st.columns(2)
with f1:
    st.markdown("**Q. 役員報酬4.5万円のメリットは何ですか？**")
    st.caption("A. 厚生年金の標準報酬月額を最低等級に抑えることで、健康保険料と厚生年金保険料の合計額を月額約2.5万円〜（労使折半後）に固定できます。")
    st.markdown("**Q. 学生でも法人化できますか？**")
    st.caption("A. はい、20歳以上であれば実印が登録できるため可能です。代表も京都で学生の身分で合同会社を設立・運営しています。")
with f2:
    st.markdown("**Q. 設立費用は総額でいくら必要ですか？**")
    st.caption("A. 合同会社なら、登録免許税（6万円）＋印鑑代＋クラウドサービス代の約7〜8万円で設立可能です。")
    st.markdown("**Q. 住所を公開せずに設立できますか？**")
    st.caption("A. バーチャルオフィス等を利用すれば、自宅住所を登記簿に載せず、プライバシーを守ることが可能です。")

st.divider()
st.caption(f"Produced by 合同会社竹輪 | 京都府京都市 | 2026年最新シミュレーション")
