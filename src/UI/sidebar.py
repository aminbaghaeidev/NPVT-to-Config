import os

import streamlit as st

from src.utils.streamlit_cache import (
    _cached_tables_from_bytes,
    _cached_tables_from_path,
)


def load_tables(tables_path):
    if os.path.exists(tables_path):
        st.sidebar.success(":white_check_mark: شناسایی شد npv_tabels.json فایل")
        try:
            return _cached_tables_from_path(tables_path)
        except (OSError, ValueError) as e:
            st.sidebar.error(f"خطا در بارگذاری جدول‌ها:\n {e}")
            return None

    st.sidebar.warning(":warning: !یافت نشد npv_tables.json فایل")
    uploaded = st.sidebar.file_uploader("آپلود npv_tables.json", type=["json"])
    if uploaded is not None:
        try:
            tables = _cached_tables_from_bytes(uploaded.getvalue())
            st.sidebar.success(":white_check_mark: !جدول‌ها بارگذاری شدند")
            return tables
        except (ValueError, UnicodeDecodeError) as e:
            st.sidebar.error(f"خطا:\n {e}")
    return None
