"""Funding page — renders app/content/funding.md."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from footer import render_footer  # noqa: E402

st.set_page_config(
    page_title="DISSILEX — Funding",
    page_icon="\N{OPEN BOOK}",
    layout="wide",
    initial_sidebar_state="collapsed",
)

md_path = Path(__file__).resolve().parents[1] / "content" / "funding.md"
st.markdown(md_path.read_text(encoding="utf-8"))

render_footer()
