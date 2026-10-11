import base64

import streamlit as st

from src.npvt_decrypter.link_builder import extract_links_from_json
from src.npvt_decrypter.whitebox_aes import NPVTDecrypter


def process_npvt(content, tables_data):
    if tables_data is None:
        st.error(":x: !موجود نیست. لطفا آن را از منوی کناری آپلود کنید `npv_tables.json` فایل")
        return

    try:
        with st.spinner("...در حال پردازش و استخراج کانفیگ"):
            decrypter = NPVTDecrypter(tables_data)
            results = decrypter.decrypt_text(content)

        if not results:
            st.session_state["generated_links"] = []
            st.session_state["raw_blocks"] = []
            st.error(":x: !دیتای رمز گذاری شده قابل استخراج نیست")
            return

        generated_links = []
        raw_blocks = []
        for idx, pt in enumerate(results):
            decoded_str = pt.decode("utf-8", errors="replace")
            links = extract_links_from_json(decoded_str)
            if links:
                generated_links.extend(links)
            else:
                raw_blocks.append((idx, decoded_str))

        st.session_state["generated_links"] = generated_links
        st.session_state["raw_blocks"] = raw_blocks

    except (KeyError, IndexError, ValueError, TypeError) as e:
        st.error(f":x: خطا در پردازش:\n {e}")


def process_plain_base64(content):
    try:
        s = "".join(content.split())
        s += "=" * ((-len(s)) % 4)
        decoded_text = base64.b64decode(s).decode("utf-8", errors="replace")
        st.session_state["plain_decoded"] = decoded_text
    except (ValueError, TypeError) as e:
        st.error(f":x: خطا:\n {e}")
