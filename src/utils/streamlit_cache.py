import streamlit as st

from src.utils.data_loader import load_tables_from_bytes, load_tables_from_path


@st.cache_data
def _cached_tables_from_path(path):
    return load_tables_from_path(path)


@st.cache_data
def _cached_tables_from_bytes(file_bytes):
    return load_tables_from_bytes(file_bytes)
