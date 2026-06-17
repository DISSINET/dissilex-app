"""Attribution page — renders app/content/attribution.md."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from footer import render_footer  # noqa: E402

st.set_page_config(page_title="DISSILEX — Attribution", page_icon="\N{OPEN BOOK}", layout="wide")

md_path = Path(__file__).resolve().parents[1] / "content" / "attribution.md"
st.markdown(md_path.read_text(encoding="utf-8"))

render_footer()
