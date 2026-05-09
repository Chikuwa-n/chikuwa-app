import streamlit as st

# --- (前略：以前の計算ロジック部分は維持) ---

# --- ④ 設立プロセス・ナビゲーター ---
st.divider()
if "show_setup" not in st.session_state:
    st.session_state.show_setup = False

# 推奨結果が「法人成り」の場合に、より強くプッシュする
btn_label = f"🚀 最短で「{data['best']}」を実現するロードマップを見る"
if st.button(btn_label):
    st.session_state.show_setup = True

if st.session_state.show_setup:
    st.header("④ 法人設立・完全ナビゲーション")
    st.write("代表（私）も実際に通った道です。迷いやすいポイントを整理しました。")

    # --- STEP 1: 形態の選択 ---
    st.subheader("STEP 1: 会社の形態を選ぶ")
    corp_type = st.radio("どちらの形態を検討していますか？", ["合同会社（LLC）", "株式会社"])
    
    if corp_type == "合同会社（LLC）":
        st.success("✅ **資産管理会社ならこちらが主流！** 設立費用が安く（登録免許税6万）、決算公告の義務もありません。")
    else:
        st.info("✅ **対外的な信用・上場を狙うならこちら。** 設立費用は約20万〜。役員の任期更新などの手間も発生します。")

    # --- STEP 2: 準備物リスト（ここで広告・紹介の導線） ---
    st.subheader("STEP 2: 必要なものリスト")
    st.write("これがないと始まりません。早めに準備しましょう。")
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("""
        *   **個人の実印:** 役員になる方のもの（印鑑証明書も必要）
        *   **法人用の印鑑3点セット:** 代表印・銀行印・角印
        *   **資本金:** 1円から可能（通帳のコピーが必要）
        """)
    with col_h2:
        st.info("💡 **代表の経験談**")
        st.write("法人印はネットで頼むのが最速で安いです。私はここで作りました。")
        st.markdown("[👉 おすすめの印鑑作成サービス（広告リンク想定）](https://example.com)")

    # --- STEP 3: 定款と申請方法（柔軟な分岐） ---
    st.subheader("STEP 3: 定款作成と登記申請")
    has_mynumber = st.radio("マイナンバーカードを持っていますか？", ["持っている", "持っていない"])
    apply_method = st.radio("申請はどうしたいですか？", ["なるべく安く、自分でやりたい", "プロに丸投げしたい"])

    if apply_method == "なるべく安く、自分でやりたい":
        if has_mynumber == "持っている":
            st.success("🎯 **「マイナポータル」での電子申請がおすすめ！**")
            st.write("定款の収入印紙代（4万円）を浮かせられます。ただし、電子署名の設定などPCスキルが少し必要です。")
        else:
            st.warning("⚠️ **紙の定款だと4万円損します。**")
            st.write("マイナンバーカードがない場合、電子定款作成サービス（5,000円程度）だけ利用して、紙で登記するのが現実的です。")
        st.markdown("[👉 自分で安く登記するならこのサービス（広告リンク）](https://example.com)")
    else:
        st.success("🎯 **「司法書士」または「会社設立Freee/マネーフォワード」の活用**")
        st.write("手数料を払ってプロに頼むか、クラウドサービスを使って書類を自動生成しましょう。")
        st.markdown("[👉 登記お任せパックの詳細を見る（広告リンク）](https://example.com)")

    # --- STEP 4: 税理士の判定ロジック ---
    st.divider()
    st.subheader("STEP 4: 顧問税理士は必要か？")
    
    # 判定ロジック：売上が多い or 経費管理が複雑 or 投資を加速させたいなら推奨
    needs_tax_accountant = False
    if salary + investment > 10000000 or expense > 2000000:
        needs_tax_accountant = True
        
    if needs_tax_accountant:
        st.error("💡 **あなたは「税理士をつけるべき」判定です**")
        st.write(f"現在の収支規模では、自力での決算はリスクが高いです。{pref}（{data['params']['pref']}）周辺で、資産管理会社に強い税理士を紹介できます。")
        st.markdown(f"[🔍 {pref}で評判の良い税理士事務所を探す（広告リンク）](https://example.com/search?pref={pref})")
    else:
        st.success("💡 **まずは自力（またはスポット相談）でもOK**")
        st.write("規模が小さいうちはクラウド会計ソフトを駆使して自力で乗り切ることも可能です。")

st.divider()
st.caption(f"現在の設定：{pref} / {'40歳以上' if is_over_40 else '40歳未満'} / 役員報酬4.5万円設定")
