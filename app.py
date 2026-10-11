from pathlib import Path

import streamlit as st

from src.UI.inputs import get_input_content
from src.UI.processing import process_npvt, process_plain_base64
from src.UI.results import render_results
from src.UI.sidebar import load_tables

TABLES_PATH = Path(__file__).resolve().parent / "data" / "npv_tables.json"


def main():
    st.set_page_config(page_title="NPVT Decrypter", page_icon=":closed_lock_with_key:", layout="wide")
    st.title(":unlock: NPVT استخراج کانفیگ از فایل")

    tables_data = load_tables(TABLES_PATH)
    content = get_input_content()

    if st.button(":zap: استخراج", type="primary"):
        if not content.strip():
            st.warning("لطفاً فایل آپلود کنید یا متن را وارد نمایید.")
        elif "NPVT" in content:
            st.session_state.pop("plain_decoded", None)
            process_npvt(content, tables_data)
        else:
            st.session_state.pop("generated_links", None)
            st.session_state.pop("raw_blocks", None)
            process_plain_base64(content)

    render_results()


if __name__ == "__main__":
    main()
