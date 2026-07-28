"""Shared footer rendered at the bottom of every page.

Also injects sidebar nav styling so the auto-generated page labels
(derived from script filenames by Streamlit) render in upper case.
"""
import streamlit as st


def base_path():
    """URL prefix the app is served under, always leading+trailing slashed.

    The live deploy runs behind Apache with
    ``streamlit run ... --server.baseUrlPath apps/dissilex``, so root-absolute
    hrefs like ``/Funding`` land outside the app. Local dev has no base path
    and returns ``"/"``.
    """
    try:
        raw = st.get_option("server.baseUrlPath") or ""
    except Exception:
        raw = ""
    raw = raw.strip("/")
    return f"/{raw}/" if raw else "/"


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
    base = base_path()
    st.markdown(
        '<div style="text-align:center;color:#888;font-size:10pt;">'
        f'<a href="{base}" target="_self">Home</a> · '
        f'<a href="{base}Funding" target="_self">Funding</a> · '
        f'<a href="{base}Attribution" target="_self">Attribution</a>'
        '</div>',
        unsafe_allow_html=True,
    )
