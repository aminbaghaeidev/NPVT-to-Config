import streamlit as st


def get_input_content():
    tab_file, tab_text = st.tabs([":file_folder: آپلود فایل", ":page_facing_up: متن کدگذاری شده"])
    content = ""

    with tab_file:
        uploaded_files = st.file_uploader(
            "(.npvt | .txt) فایل کانفیگ",
            type=["npvt", "txt"],
            accept_multiple_files=True
        )
        if uploaded_files:
            content = "\n".join(
                f.getvalue().decode("utf-8", errors="ignore") for f in uploaded_files
            )

    with tab_text:
        text_input = st.text_area(":را وارد کنید NPVT محتوای متنی فایل", height=150)
        if text_input:
            content = text_input

    return content
