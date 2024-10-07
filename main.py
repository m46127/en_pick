import streamlit as st

# メニューの選択肢を定義
menu_options = ["トップページ", "pdf_pick"]

# サイドバーでメニューを表示
selected_option = st.sidebar.radio("メインメニュー", menu_options)

# 選択肢に応じて表示するページを変更
if selected_option == "トップページ":
    st.title("トップページ")
    st.write("ようこそ！")

elif selected_option == "pdf_pick":
    # pick.py の内容をインポートして実行
    from pdfpick import pdfpick_page
    pdfpick_page()
