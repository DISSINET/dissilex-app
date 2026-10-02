"""Shared footer rendered at the bottom of every page.

Also injects sidebar nav styling so the auto-generated page labels
(derived from script filenames by Streamlit) render in upper case, and
provides ``render_sidebar_links()`` — the external-link block every page
puts under the sidebar nav.
"""
import streamlit as st

#: External destinations shown in both the sidebar and the footer.
EXTERNAL_LINKS = (
    ("GitHub", "https://github.com/DISSINET/dissilex-app"),
    ("Zenodo", "https://doi.org/10.5281/zenodo.20600887"),  # concept DOI: latest version
    ("DISSINET", "https://dissinet.cz"),
)


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


def render_sidebar_links():
    """Render the external links in the sidebar, continuing the page nav list.

    Uses ``st.page_link`` rather than markdown anchors: it accepts external
    URLs (rendering with ``target="_blank"``) and is built from the same theme
    tokens as Streamlit's auto-generated nav links — no underline, body-text
    colour, ``lineHeights.menuItem``, ``darkenedBgMix15`` hover — so the
    external links read as list entries rather than blue hyperlinks.

    Streamlit's own divider under the nav (``stSidebarNavSeparator``) is kept
    deliberately: it marks internal pages off from external destinations. The
    CSS below only closes the remaining gaps between the two groups' styling:

    * **Label size.** The nav renders its label with ``inheritFont``, wrapped
      in a span at ``fontSizes.sm`` (0.875rem); ``st.page_link`` passes
      ``largerLabel``, which resolves to ``fontSizes.md`` (1rem). Same family
      (``Source Sans``) — only the size differed.
    * **Vertical rhythm.** Nav items are ``<li>`` whose margins collapse with
      the anchor's; our links are flex items, where margins do not collapse.
      The anchor margins are therefore zeroed and the block ``gap`` alone
      controls the spacing — its value (and the padding below) is **tuned by
      eye against the rendered nav**, not derived from a theme token.
    * **Text colour.** Inactive nav links fade ``bodyText`` to alpha .8 (.75
      in dark); ``st.page_link`` uses it at full strength.
    * **Padding above.** Streamlit pads sidebar user content by
      ``spacing.twoXL`` (1.5rem) when a nav sits above; the override sets the
      gap between the divider and the first external link, also by eye.

    Called explicitly by each page (not from ``render_footer()``) so the
    sidebar is written while the page body is still being built.
    """
    st.markdown(
        """
        <style>
          [data-testid="stSidebarUserContent"] { padding-top: 1.525rem; }
          [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .stPageLink) {
            gap: 0.925rem;
          }
          [data-testid="stSidebarUserContent"] [data-testid="stPageLink-NavLink"] {
            margin-top: 0;
            margin-bottom: 0;
            opacity: 0.8;
          }
          [data-testid="stSidebarUserContent"] [data-testid="stPageLink-NavLink"] [data-testid="stMarkdownContainer"],
          [data-testid="stSidebarUserContent"] [data-testid="stPageLink-NavLink"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.875rem;
            line-height: inherit;
          }
          @media (prefers-color-scheme: dark) {
            [data-testid="stSidebarUserContent"] [data-testid="stPageLink-NavLink"] { opacity: 0.75; }
          }
          [data-testid="stSidebarUserContent"] [data-testid="stPageLink-NavLink"]:hover { opacity: 1; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    for label, url in EXTERNAL_LINKS:
        st.sidebar.page_link(url, label=label)


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
    external = " · ".join(
        f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'
        for label, url in EXTERNAL_LINKS
    )
    st.markdown(
        '<div style="text-align:center;color:#888;font-size:10pt;">'
        f'<a href="{base}" target="_self">Home</a> · '
        f'<a href="{base}Funding" target="_self">Funding</a> · '
        f'<a href="{base}Attribution" target="_self">Attribution</a> · '
        f'{external}'
        '</div>',
        unsafe_allow_html=True,
    )
