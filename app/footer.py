"""Shared footer rendered at the bottom of every page.

Also injects sidebar nav styling so the auto-generated page labels
(derived from script filenames by Streamlit) render in upper case.
"""
import streamlit as st


def render_footer():
    st.markdown(
        """
        <style>
          [data-testid="stSidebarNav"] ul li:first-child a,
          [data-testid="stSidebarNav"] ul li:first-child a span {
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;color:#888;font-size:10pt;">'
        '<a href="/" target="_self">Home</a> · '
        '<a href="/Funding" target="_self">Funding</a> · '
        '<a href="/Attribution" target="_self">Attribution</a>'
        '</div>',
        unsafe_allow_html=True,
    )
