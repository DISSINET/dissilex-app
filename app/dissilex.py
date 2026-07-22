#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISSILEX — Interactive lexicographic explorer for DISSINET Actions & Concepts.

Usage:
    streamlit run app/dissilex.py
"""

import html
import os
import re
import sqlite3
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import streamlit.components.v1 as components
from lib.constants import Constants
from lib.scope import symmetric_dedup_sql

from footer import render_footer


def _e(value):
    """HTML-escape a value for safe interpolation into unsafe_allow_html markup."""
    return html.escape(str(value)) if value else ""

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="DISSILEX",
    page_icon="\N{OPEN BOOK}",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
  /* --- Theme-adaptive CSS custom properties --- */
  :root {
    --dl-valency: #1A5276;
    --dl-def-color: #1C1C1C;
    --dl-badge-bg: #F2F3F4;
    --dl-badge-fg: #888;
    --dl-border: #D5D8DC;
    --dl-link: #1A5276;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --dl-valency: #5DADE2;
      --dl-def-color: #6C7A89;
      --dl-badge-bg: #2C3E50;
      --dl-badge-fg: #AEB6BF;
      --dl-border: #4A5568;
      --dl-link: #5DADE2;
    }
  }
  [data-theme="dark"] {
    --dl-valency: #5DADE2;
    --dl-def-color: #6C7A89;
    --dl-badge-bg: #2C3E50;
    --dl-badge-fg: #AEB6BF;
    --dl-border: #4A5568;
    --dl-link: #5DADE2;
  }

  .dissilex-entry { padding: 12px; margin-bottom: 12px;
                    border: 1px solid var(--dl-border); border-radius: 6px; }
  .dl-headword  { font-size: 20pt; font-weight: bold; color: #C0392B; margin-right: 10px; }
  .dl-form      { font-size: 13pt; color: #C0392B; opacity: 0.7; }
  .dl-pos       { font-size: 13pt; color: #888; margin-left: 8px; }
  .dl-def       { font-style: italic; color: var(--dl-def-color); margin-left: 20px; }
  .dl-rel-type  { color: #6C3483; font-size: 11pt; font-variant: small-caps; margin-right: 6px; }
  .dl-badge     { background: var(--dl-badge-bg); color: var(--dl-badge-fg); font-size: 10pt;
                  padding: 1px 6px; border-radius: 3px; margin-left: 4px; }
  .dissilex-entry a.dl-badge { color: var(--dl-link); font-weight: 600; }
  .dl-note      { color: #9B59B6; font-size: 11pt; }
  .dl-source    { color: #888; font-size: 11pt; }
  .dl-status    { color: #888; font-size: 10pt; margin-top: 8px; }
  .dl-val-slot  { color: var(--dl-valency); font-weight: bold; font-size: 13pt;
                  margin-bottom: 2px; }
  .dl-val-line  { color: var(--dl-valency); font-style: italic; font-size: 12pt;
                  margin-left: 20px; line-height: 1.6; }
  .dl-voice     { font-size: 12pt; color: #666; margin: 4px 0 4px 20px; }
  .dl-voice a   { color: #2471A3; text-decoration: underline; }
  .dl-variants  { font-size: 12pt; color: #888; font-style: italic;
                  margin: 2px 0 4px 0; }

  /* Results list grid */
  .dl-results {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 4px 16px;
    align-items: baseline;
    margin-top: 8px;
  }
  .dl-result-head a {
    font-size: 14pt;
    font-weight: bold;
    color: #C0392B;
    text-decoration: none;
  }
  .dl-result-head a:hover { text-decoration: underline; }
  .dl-result-info { padding-bottom: 4px; border-bottom: 1px solid var(--dl-border); }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "dissilex.db"
)


@st.cache_resource
def get_db():
    """Return a shared SQLite connection (read-only)."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def query(sql, params=()):
    """Execute a read query and return a list of sqlite3.Row objects."""
    return get_db().execute(sql, params).fetchall()


@st.cache_data
def _all_uuids():
    """Return the set of all UUIDs present in DISSILEX (actions + concepts)."""
    rows = (
        get_db()
        .execute("SELECT uuid FROM actions UNION SELECT uuid FROM concepts")
        .fetchall()
    )
    return {r[0] for r in rows}


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

STATUS_NAMES = {
    "0": "Pending",
    "1": "Approved",
    "2": "Discouraged",
    "3": "Approved",
    "4": "Unfinished",
}

ENTITY_CLASS_NAMES = Constants.ENTITY_CLASS_NAMES
SLOT_NAMES = Constants.SLOT_NAMES
LANGUAGE_NAMES = Constants.LANGUAGE_NAMES
RELATION_NAMES = Constants.RELATION_NAMES
# Canonical display order for the relations list (T66): the key order of
# RELATION_NAMES. Unknown types sort last.
_REL_ORDER = {rtype: i for i, rtype in enumerate(RELATION_NAMES)}


def _rel_rank(rtype):
    """Sort key for a relation type in the canonical display order."""
    return _REL_ORDER.get(rtype, len(_REL_ORDER))


def _expand_entity_types(raw):
    """Expand entity type abbreviations like 'P, G' to full names."""
    if not raw:
        return None
    codes = [c.strip() for c in raw.split(",")]
    names = [ENTITY_CLASS_NAMES.get(c, c) for c in codes if c and c != "empty"]
    return ", ".join(names) if names else None


# ---------------------------------------------------------------------------
# Navigation state (URL query params as source of truth)
# ---------------------------------------------------------------------------

_SEARCH_TYPES = ["Auto", "Lemma", "UUID", "WordNet ID"]

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)
_WN_NUMERIC = re.compile(r"^\d{5,9}(-[a-z])?$")


def detect_search_type(term):
    """Infer search type from term format: UUID, WordNet ID, or Lemma."""
    t = term.strip()
    if _UUID_RE.match(t):
        return "UUID"
    if _WN_NUMERIC.match(t):
        return "WordNet ID"
    # 'NA' (exact, uppercase) is the WordNet "no equivalent" sentinel stored as
    # an external ID — resolve it as a WordNet ID under Auto. Case-sensitive on
    # purpose: lowercase 'na' is a legitimate lemma substring query (matches
    # narravit, natus, crucesignatus, …) and must stay a Lemma search.
    if t == "NA":
        return "WordNet ID"
    return "Lemma"


def _qp_get(key, default=""):
    return st.query_params.get(key, default)


nav_sel = _qp_get("sel") or None
nav_term = _qp_get("q")
nav_stype = _qp_get("t") if _qp_get("t") in _SEARCH_TYPES else "Auto"

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    # href="?" returns to the app root on ANY base path: it resolves to the
    # current path with an empty query string, dropping all query params.
    # Works under local dev ("/") and a proxied sub-path ("/apps/dissilex/")
    # with no hostname detection or hardcoded paths.
    '<h1><a href="?" target="_self" style="color:inherit;text-decoration:none">DISSILEX</a></h1>',
    unsafe_allow_html=True,
)
st.caption(
    "A lexicographic explorer for the DISSILEX lexico-semantic network "
    "and valency lexicon of medieval Latin actions and concepts."
)

# ---------------------------------------------------------------------------
# Search bar
# ---------------------------------------------------------------------------

col_input, col_type, col_btn = st.columns([5, 2, 1])

with col_input:
    search_term = st.text_input(
        "Search",
        value=nav_term,
        placeholder="Search DISSILEX\u2026",
        label_visibility="collapsed",
    )

with col_type:
    # Keep the dropdown in sync with the URL's `t` param, but only re-sync when
    # the URL actually changes (navigation / new search) — otherwise a manual
    # pick would be clobbered on the next rerun. A keyless selectbox treats
    # `index` as a one-time default and drifts out of sync (would intermittently
    # show a resolved type like "Lemma" instead of "Auto").
    if st.session_state.get("_last_t_url") != nav_stype:
        st.session_state["search_type"] = nav_stype
        st.session_state["_last_t_url"] = nav_stype
    search_type = st.selectbox(
        "Type",
        _SEARCH_TYPES,
        key="search_type",
        label_visibility="collapsed",
    )

with col_btn:
    search_clicked = st.button("Search", use_container_width=True, type="primary")

if search_clicked:
    st.query_params["q"] = search_term.strip()
    st.query_params["t"] = search_type
    if "sel" in st.query_params:
        del st.query_params["sel"]
    st.rerun()

# Also handle Enter key (text input change without button click)
if search_term.strip() != nav_term and not search_clicked:
    st.query_params["q"] = search_term.strip()
    st.query_params["t"] = search_type
    if "sel" in st.query_params:
        del st.query_params["sel"]
    st.rerun()


# ---------------------------------------------------------------------------
# Search execution
# ---------------------------------------------------------------------------

# Active voice first, then passive, reflexive, everything else (T64). Mirrors
# _VOICE_ORDER; the display already re-buckets by voice, so this keeps the flat
# result list correct on its own.
_VOICE_SORT_SQL = (
    "CASE semantic_voice "
    "WHEN 'active semantic voice' THEN 0 "
    "WHEN 'passive semantic voice' THEN 1 "
    "WHEN 'reflexive semantic voice' THEN 2 "
    "ELSE 3 END"
)


def run_search(term, stype):
    """Return (results, effective_stype). Resolves 'Auto' to the detected type."""
    if stype == "Auto":
        stype = detect_search_type(term)
    if stype == "Lemma":
        actions = query(
            "SELECT uuid, 'action' AS kind, "
            "label, pos, detail, lila_canonical, lila_variants, spacy_lemma, "
            "semantic_voice "
            "FROM actions "
            "WHERE label LIKE ? COLLATE NOCASE "
            "   OR lila_canonical LIKE '%' || ? || '%' COLLATE NOCASE "
            "   OR lila_variants LIKE '%' || ? || '%' COLLATE NOCASE "
            "   OR (lila_canonical IS NULL AND spacy_lemma LIKE ? COLLATE NOCASE) "
            f"ORDER BY {_VOICE_SORT_SQL}, label COLLATE NOCASE",
            (f"{term}%", term, term, f"{term}%"),
        )
        concepts = query(
            "SELECT uuid, 'concept' AS kind, label, pos, detail, "
            "lila_canonical, lila_variants, NULL AS spacy_lemma "
            "FROM concepts "
            "WHERE label LIKE ? COLLATE NOCASE "
            "   OR lila_canonical LIKE '%' || ? || '%' COLLATE NOCASE "
            "   OR lila_variants LIKE '%' || ? || '%' COLLATE NOCASE "
            "ORDER BY label COLLATE NOCASE",
            (f"{term}%", term, term),
        )
        return list(actions) + list(concepts), stype

    elif stype == "UUID":
        rows = query(
            "SELECT uuid, 'action' AS kind, "
            "label, pos, detail, lila_canonical, lila_variants, spacy_lemma, "
            "semantic_voice "
            "FROM actions WHERE uuid = ?",
            (term,),
        )
        if not rows:
            rows = query(
                "SELECT uuid, 'concept' AS kind, label, pos, detail, "
                "lila_canonical, lila_variants, NULL AS spacy_lemma "
                "FROM concepts WHERE uuid = ?",
                (term,),
            )
        return list(rows), stype

    elif stype == "WordNet ID":
        # Search all WordNet resources (WN 3.0, WN 3.1).
        # Use LIKE with ESCAPE to handle suffix variations (e.g. "01185006"
        # matches "01185006-v")
        if not term:
            return [], stype
        escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        actions = query(
            "SELECT DISTINCT a.uuid, 'action' AS kind, "
            "a.label, a.pos, a.detail, a.lila_canonical, a.lila_variants, a.spacy_lemma, "
            "a.semantic_voice "
            "FROM external_ids e JOIN actions a ON e.entity_uuid = a.uuid "
            "WHERE e.resource IN ('wordnet30', 'wordnet31') "
            "AND (e.value = ? COLLATE NOCASE "
            "     OR e.value LIKE ? ESCAPE '\\' COLLATE NOCASE) "
            f"ORDER BY {_VOICE_SORT_SQL}, label COLLATE NOCASE",
            (term, f"{escaped}%"),
        )
        concepts = query(
            "SELECT DISTINCT c.uuid, 'concept' AS kind, c.label, c.pos, c.detail, "
            "c.lila_canonical, c.lila_variants, NULL AS spacy_lemma "
            "FROM external_ids e JOIN concepts c ON e.entity_uuid = c.uuid "
            "WHERE e.resource IN ('wordnet30', 'wordnet31') "
            "AND (e.value = ? COLLATE NOCASE "
            "     OR e.value LIKE ? ESCAPE '\\' COLLATE NOCASE) "
            "ORDER BY c.label COLLATE NOCASE",
            (term, f"{escaped}%"),
        )
        return list(actions) + list(concepts), stype

    return [], stype


# ---------------------------------------------------------------------------
# Results list renderer — pure HTML, no buttons
# ---------------------------------------------------------------------------

_VOICE_ORDER = [
    "active semantic voice",
    "passive semantic voice",
    "reflexive semantic voice",
    "deponent",
    None,
]
_VOICE_LABELS = {
    "active semantic voice": "Active meaning",
    "passive semantic voice": "Passive meaning",
    "reflexive semantic voice": "Reflexive meaning",
    "deponent": "Deponent",
    None: "Unclassified",
}


def _voice_sub_buckets(rows):
    """Split action rows into ordered voice buckets. Returns [(voice_key, [rows]), ...]."""
    from collections import OrderedDict

    buckets = OrderedDict()
    for r in rows:
        v = r["semantic_voice"]
        buckets.setdefault(v, []).append(r)
    return [(v, buckets[v]) for v in _VOICE_ORDER if v in buckets]


def _group_results(results):
    """Group results by lemma.  Returns [(group_label, group_kind, [rows]), ...].

    Grouping key priority: lila_canonical > spacy_lemma > ungrouped.
    group_kind is 'lila', 'spacy', 'actions', or 'concepts'.

    Order: LiLa groups (alphabetical), then spaCy-only groups (alphabetical),
    then ungrouped actions, then concepts.
    """
    from collections import OrderedDict

    lila_groups = OrderedDict()  # lila_canonical → [rows]
    spacy_groups = OrderedDict()  # spacy_lemma → [rows]
    ungrouped_actions = []
    concepts = []

    for row in results:
        if row["kind"] == "concept":
            concepts.append(row)
            continue
        lila = row["lila_canonical"]
        if lila:
            lila_groups.setdefault(lila, []).append(row)
        elif row["spacy_lemma"]:
            spacy_groups.setdefault(row["spacy_lemma"], []).append(row)
        else:
            ungrouped_actions.append(row)

    out = []
    # LiLa groups sorted alphabetically by canonical form
    for k, rows in sorted(lila_groups.items(), key=lambda kv: kv[0].lower()):
        out.append((k, "lila", rows))
    # spaCy-only groups sorted alphabetically
    for k, rows in sorted(spacy_groups.items(), key=lambda kv: kv[0].lower()):
        out.append((k, "spacy", rows))
    # Ungrouped actions
    if ungrouped_actions:
        out.append((None, "actions", ungrouped_actions))
    # Concepts in their own section
    if concepts:
        out.append((None, "concepts", concepts))
    return out


def render_results_list(results, term, stype):
    """Render results grouped by LiLa lemma, with clickable headword + View button."""
    if st.button("\u2302 Home", type="secondary"):
        _go_home()
    type_label = {"Lemma": "lemma", "UUID": "UUID", "WordNet ID": "WordNet ID"}.get(
        stype, stype.lower()
    )
    st.markdown(
        f"**{len(results)} result{'s' if len(results) != 1 else ''}** "
        f"for *{_e(term)}* \u00b7 <span style='color:#888;font-size:10pt'>{type_label} search</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    eq = urllib.parse.quote(term, safe="")
    et = urllib.parse.quote(stype, safe="")

    groups = _group_results(results)

    for group_label, group_kind, rows in groups:
        if group_label:
            # LiLa groups in blue; spaCy-only groups in grey-blue with a marker
            if group_kind == "lila":
                color = "#2980B9"
                suffix = ""
            else:
                color = "#7F8C8D"
                suffix = (
                    ' <span style="font-size:9pt;font-weight:normal">· spaCy</span>'
                )
            st.markdown(
                f'<div style="margin:12px 0 4px 0;font-size:12pt;font-weight:bold;'
                f"color:{color};border-bottom:1px solid var(--dl-border);"
                f'padding-bottom:2px">Actions: <em>{_e(group_label)}</em>{suffix}'
                f' <span style="color:#888;font-size:10pt;font-weight:normal">'
                f"({len(rows)})</span></div>",
                unsafe_allow_html=True,
            )
        elif group_kind == "concepts":
            st.markdown(
                f'<div style="margin:16px 0 4px 0;font-size:12pt;font-weight:bold;'
                f"color:#6C3483;border-bottom:1px solid var(--dl-border);"
                f'padding-bottom:2px">Concepts'
                f' <span style="color:#888;font-size:10pt;font-weight:normal">'
                f"({len(rows)})</span></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="margin:12px 0 4px 0;font-size:12pt;'
                f"color:#888;border-bottom:1px solid var(--dl-border);"
                f'padding-bottom:2px">Other actions ({len(rows)})</div>',
                unsafe_allow_html=True,
            )

        if group_kind != "concepts":
            voice_buckets = _voice_sub_buckets(rows)
            show_voice = len(voice_buckets) > 1
        else:
            voice_buckets = [(None, rows)]
            show_voice = False

        for voice_key, bucket_rows in voice_buckets:
            if show_voice:
                vlabel = _VOICE_LABELS[voice_key]
                st.markdown(
                    f'<div style="margin:8px 0 3px 16px;font-size:10pt;font-weight:600;'
                    f'color:#555;border-bottom:1px solid var(--dl-border);">'
                    f'{vlabel} <span style="color:#888;font-weight:normal">({len(bucket_rows)})</span></div>',
                    unsafe_allow_html=True,
                )
            for row in bucket_rows:
                kind_label = "Action" if row["kind"] == "action" else "Concept"
                excerpt = row["detail"] or ""
                if len(excerpt) > 120:
                    excerpt = excerpt[:120] + "\u2026"
                pos_html = (
                    f' <span class="dl-pos">\u00b7 {_e(row["pos"])}</span>'
                    if row["pos"]
                    else ""
                )
                href = f"?q={eq}&t={et}&sel={row['uuid']}"

                c_lemma, c_btn, c_info = st.columns([2, 1, 7], gap="small")
                with c_lemma:
                    st.markdown(
                        f'<a href="{href}" target="_self" '
                        f'style="font-size:14pt;font-weight:bold;color:#C0392B;'
                        f'text-decoration:none">{_e(row["label"])}</a>',
                        unsafe_allow_html=True,
                    )
                with c_btn:
                    if st.button("View", key=f"view_{row['uuid']}", type="primary"):
                        st.query_params["sel"] = row["uuid"]
                        st.rerun()
                with c_info:
                    st.markdown(
                        f'<span class="dl-badge">{kind_label}</span>{pos_html}'
                        f' <span class="dl-source">{_e(excerpt)}</span>',
                        unsafe_allow_html=True,
                    )


# ---------------------------------------------------------------------------
# Entry detail card
# ---------------------------------------------------------------------------


def _go_home():
    """Clear all query params and rerun."""
    for k in list(st.query_params.keys()):
        del st.query_params[k]
    st.rerun()


def _render_back_button():
    has_search = bool(_qp_get("q"))
    if has_search:
        # Check if going back would show a results list (>1 result)
        results, _ = run_search(_qp_get("q"), _qp_get("t") or "Auto")
        if len(results) > 1:
            c1, c2, _ = st.columns([2, 2, 6], gap="small")
            with c1:
                if st.button("\u2190 Back to results", type="primary"):
                    del st.query_params["sel"]
                    st.rerun()
            with c2:
                if st.button("\u2302 Home", type="secondary"):
                    _go_home()
            return
    # Single result or no search — just show Home
    if st.button("\u2302 Home", type="primary"):
        _go_home()


_COPY_BAD_VALUES = {"", "na", "nan", "none"}


def _copy_items(uuid, ext_ids):
    """Build the (display_label, copy_value, tooltip) list for an entity's copy row.

    Order: LiLa, WordNet 3.0, WordNet 3.1, UUID — whichever exist. Labels carry
    no ID (the IDs are already shown in the main card); WordNet buttons carry
    the synset gloss as hover text. 'NA'/empty sentinels are skipped.
    """
    by_res = {}
    for e in ext_ids:
        val = (e["value"] or "")
        if val.strip().lower() in _COPY_BAD_VALUES:
            continue
        by_res[e["resource"]] = (val, e["gloss"] or "")

    items = []
    # LiLa, then WordNet 3.0/3.1, each with no ID in the label
    if "lila" in by_res:
        items.append(("LiLa", by_res["lila"][0], ""))
    for res, label in (("wordnet30", "WordNet 3.0"), ("wordnet31", "WordNet 3.1")):
        if res in by_res:
            val, gloss = by_res[res]
            items.append((label, val, gloss))
    items.append(("UUID", uuid, ""))   # UUID last — least relevant to the public
    return items


def _copy_buttons_html(items):
    """Return a self-contained HTML fragment: one copy-to-clipboard button per
    (label, value). No external requests (CSP-safe); values live in a
    data-attribute (HTML-escaped) and are read by JS, so there is no
    JS-string injection surface. Theme follows the viewer via prefers-color-scheme.
    Returns '' when there is nothing to copy.
    """
    if not items:
        return ""
    parts = []
    for label, val, tip in items:
        title = f' title="{_e(tip)}"' if tip else ""
        parts.append(
            f'<button class="cp" type="button" data-copy="{_e(val)}" '
            f'onclick="cp(this)" aria-label="Copy {_e(label)}"{title}>'
            f'⧉ {_e(label)}</button>'
        )
    buttons = "".join(parts)
    return (
        "<style>"
        "*{box-sizing:border-box;font-family:-apple-system,Segoe UI,Roboto,sans-serif}"
        ".row{display:flex;flex-wrap:wrap;gap:6px;padding:2px 0}"
        ".cp{font-size:10pt;padding:2px 8px;border-radius:3px;cursor:pointer;"
        "border:1px solid #ccc;background:#f0f0f0;color:#333;white-space:nowrap}"
        ".cp:hover{background:#e2e2e2}"
        ".cp.done{background:#2e7d32;color:#fff;border-color:#2e7d32}"
        "@media (prefers-color-scheme:dark){"
        ".cp{background:#2b2b2b;color:#ddd;border-color:#555}"
        ".cp:hover{background:#3a3a3a}"
        ".cp.done{background:#2e7d32;color:#fff;border-color:#2e7d32}}"
        "</style>"
        f'<div class="row">{buttons}</div>'
        "<script>"
        "function cp(b){var t=b.getAttribute('data-copy');"
        "function ok(){var o=b.textContent;b.textContent='\\u2713 Copied!';"
        "b.classList.add('done');setTimeout(function(){b.textContent=o;"
        "b.classList.remove('done')},1200)}"
        "if(navigator.clipboard&&navigator.clipboard.writeText){"
        "navigator.clipboard.writeText(t).then(ok).catch(function(){})}"
        "else{var a=document.createElement('textarea');a.value=t;"
        "document.body.appendChild(a);a.select();"
        "try{document.execCommand('copy');ok()}catch(e){}"
        "document.body.removeChild(a)}}"
        "</script>"
    )


def _render_copy_row(uuid, ext_ids):
    """Render the copy-to-clipboard button row for an entity, if any (T65)."""
    items = _copy_items(uuid, ext_ids)
    if items:
        components.html(_copy_buttons_html(items), height=40, scrolling=False)


def _render_action_card(row):
    """Render the full detail card for an Action entity."""
    uuid = row["uuid"]
    headword = row["label"]
    pos = row["pos"] or ""
    lang = row["language"]
    detail = row["detail"] or ""

    form_html = ""
    pos_html = f' <span class="dl-pos">{_e(pos)}</span>' if pos else ""
    lang_badge = (
        f' <span class="dl-badge" title="{_e(LANGUAGE_NAMES.get(lang, lang))}">{_e(lang)}</span>'
        if lang
        else ""
    )

    ext_ids = query(
        "SELECT resource, value, gloss FROM external_ids WHERE entity_uuid = ?", (uuid,)
    )
    # Badges in the fixed priority order LiLa \u2192 WN 3.0 \u2192 WN 3.1 (mirrors the
    # copy-button row); UUID comes last.
    by_res = {}
    for eid in ext_ids:
        by_res[eid["resource"]] = (eid["value"], eid["gloss"])

    badge_html = ""
    if "lila" in by_res:
        val = by_res["lila"][0]
        if val == "NA":
            badge_html += ' <span class="dl-badge">No equivalent in Lemma Bank</span>'
        else:
            lila_url = urllib.parse.quote(val, safe="")
            badge_html += (
                f' <a href="https://lila-erc.eu/data/id/lemma/{lila_url}" '
                f'target="_blank" class="dl-badge" '
                f'style="text-decoration:none">\u2197 LiLa {_e(val)}</a>'
            )
    for res, ver in (("wordnet30", "3.0"), ("wordnet31", "3.1")):
        if res not in by_res:
            continue
        val, gloss = by_res[res]
        if val == "NA":
            badge_html += f' <span class="dl-badge">No WN {ver} equivalent</span>'
        else:
            title = f' title="{_e(gloss)}"' if gloss else ""
            badge_html += f' <span class="dl-badge"{title}>WN{ver} {_e(val)}</span>'

    uuid_badge = f' <span class="dl-badge">{_e(uuid)}</span>'
    header = (
        f'<span class="dl-headword">{_e(headword)}</span>'
        f"{form_html}{pos_html}{lang_badge}{badge_html}{uuid_badge}"
    )

    variants_html = ""
    variants = row["label_variants"] or ""
    if variants:
        variants_html = f'<div class="dl-variants">{_e(variants)}</div>'

    def_html = ""
    if detail:
        def_html = f'<div class="dl-def">{_e(detail)}</div>'

    voice_html = ""
    sv = row["semantic_voice"] or ""
    if sv:
        voice_html = f'<div class="dl-voice">{_e(_VOICE_LABELS.get(sv, sv))}</div>'

    valency_rows = query(
        "SELECT slot, entity_type, morphosyntactic, morphosyntactic_display, semantic "
        "FROM valency WHERE action_uuid = ? "
        "ORDER BY CASE slot WHEN 's' THEN 0 WHEN 'a1' THEN 1 WHEN 'a2' THEN 2 ELSE 3 END",
        (uuid,),
    )
    valency_html = ""
    if valency_rows:
        blocks = []
        for v in valency_rows:
            slot = v["slot"]
            slot_label = SLOT_NAMES.get(slot, slot)
            entity_names = _expand_entity_types(v["entity_type"])
            morph = v["morphosyntactic_display"] or v["morphosyntactic"]
            if not entity_names and not morph and not v["semantic"]:
                continue
            lines = [
                f'<div class="dl-val-slot">{_e(slot)} \u2014 {_e(slot_label)}</div>'
            ]
            if entity_names:
                lines.append(
                    f'<div class="dl-val-line">Entity types: {_e(entity_names)}</div>'
                )
            if morph:
                lines.append(
                    f'<div class="dl-val-line">Morphosyntactic: {_e(morph)}</div>'
                )
            if v["semantic"]:
                lines.append(
                    f'<div class="dl-val-line">Semantic: {_e(v["semantic"])}</div>'
                )
            blocks.append("".join(lines))
        if blocks:
            valency_html = (
                '<div style="margin: 8px 0 8px 20px">'
                + '<div style="margin-bottom:6px"></div>'.join(blocks)
                + "</div>"
            )

    status_html = _status_html(row)
    card = f'<div class="dissilex-entry">{header}{variants_html}{def_html}{voice_html}{valency_html}{status_html}</div>'
    st.markdown(card, unsafe_allow_html=True)
    _render_copy_row(uuid, ext_ids)


def _render_concept_card(row):
    """Render the full detail card for a Concept entity."""
    uuid = row["uuid"]
    label = row["label"]
    lang = row["language"]
    detail = row["detail"] or ""
    lang_badge = (
        f' <span class="dl-badge" title="{_e(LANGUAGE_NAMES.get(lang, lang))}">{_e(lang)}</span>'
    )
    uuid_badge = f' <span class="dl-badge">{_e(uuid)}</span>'

    ext_ids = query(
        "SELECT resource, value, gloss FROM external_ids WHERE entity_uuid = ?", (uuid,)
    )

    def _ext_badge(e):
        res, val, gloss = e["resource"], e["value"], e["gloss"]
        title = (
            f' title="{_e(gloss)}"'
            if (gloss and res in ("wordnet30", "wordnet31"))
            else ""
        )
        return f' <span class="dl-badge"{title}>{_e(res)} {_e(val)}</span>'

    # Fixed priority order LiLa → WN 3.0 → WN 3.1 (then any other resource);
    # UUID badge comes last.
    _res_rank = {"lila": 0, "wordnet30": 1, "wordnet31": 2}
    ordered = sorted(ext_ids, key=lambda e: _res_rank.get(e["resource"], 3))
    badge_html = "".join(_ext_badge(e) for e in ordered)

    header = (
        f'<span class="dl-headword">{_e(label)}</span>{lang_badge}{badge_html}{uuid_badge}'
    )

    variants_html = ""
    variants = row["label_variants"] or ""
    if variants:
        variants_html = f'<div class="dl-variants">{_e(variants)}</div>'

    def_html = ""
    if detail:
        def_html = f'<div class="dl-def">{_e(detail)}</div>'

    status_html = _status_html(row)
    st.markdown(
        f'<div class="dissilex-entry">{header}{variants_html}{def_html}{status_html}</div>',
        unsafe_allow_html=True,
    )
    _render_copy_row(uuid, ext_ids)


def _render_rel_target(uuid_from, target_uuid, label, direction, rtype):
    """Render a single relation target as a clickable navigation button."""
    display = label or target_uuid[:8]
    arrow = "\u2192" if direction == "fwd" else "\u2190"
    if st.button(
        f"{arrow} {display}",
        type="primary",
        key=f"{direction}_{uuid_from}_{target_uuid}_{rtype}",
    ):
        st.query_params["sel"] = target_uuid
        st.rerun()


def _render_relations(uuid):
    """Render forward and reverse relations with navigation links."""
    fwd = query(
        "SELECT relation_type, target_uuid, target_label FROM relations "
        "WHERE source_uuid = ? ORDER BY relation_type, target_label",
        (uuid,),
    )
    rev = query(
        "SELECT relation_type, source_uuid, source_label FROM relations "
        "WHERE target_uuid = ? ORDER BY relation_type, source_label",
        (uuid,),
    )

    if not fwd and not rev:
        return

    st.markdown("#### Relations")

    if fwd:
        grouped = {}
        for r in fwd:
            grouped.setdefault(r["relation_type"], []).append(r)
        for rtype in sorted(grouped, key=_rel_rank):
            rels = grouped[rtype]
            cols = st.columns([3, 9])
            with cols[0]:
                st.markdown(
                    f'<span class="dl-rel-type" title="{_e(RELATION_NAMES.get(rtype, rtype))}">'
                    f'{_e(rtype)}</span>',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                for r in rels:
                    _render_rel_target(
                        uuid, r["target_uuid"], r["target_label"], "fwd", rtype
                    )

    if rev:
        with st.expander("Referenced by", expanded=True):
            grouped = {}
            for r in rev:
                grouped.setdefault(r["relation_type"], []).append(r)
            for rtype in sorted(grouped, key=_rel_rank):
                rels = grouped[rtype]
                cols = st.columns([3, 9])
                with cols[0]:
                    st.markdown(
                        f'<span class="dl-rel-type" title="{_e(RELATION_NAMES.get(rtype, rtype))}">'
                        f'{_e(rtype)}</span>',
                        unsafe_allow_html=True,
                    )
                with cols[1]:
                    for r in rels:
                        _render_rel_target(
                            uuid, r["source_uuid"], r["source_label"], "rev", rtype
                        )


def _status_html(row):
    """Render the entity status as a small, left-aligned, un-highlighted line at
    the foot of the card (T70). Shows just the status name (e.g. "Approved",
    "Pending"), aligned with the headword — not the "Status:" prefix. Language
    already appears as a badge in the card header, so no language line here."""
    status_label = STATUS_NAMES.get(row["status"], row["status"])
    if not status_label:
        return ""
    return f'<div class="dl-status">{_e(status_label)}</div>'


def render_detail(uuid):
    """Render the full entry detail card for an Action or Concept."""
    _render_back_button()

    rows = query("SELECT * FROM actions WHERE uuid = ?", (uuid,))
    if rows:
        _render_action_card(rows[0])
        _render_relations(uuid)
        return

    rows = query("SELECT * FROM concepts WHERE uuid = ?", (uuid,))
    if rows:
        _render_concept_card(rows[0])
        _render_relations(uuid)
        return

    st.error(f"UUID `{uuid}` not found in actions or concepts.")


# ---------------------------------------------------------------------------
# Results area — routing logic
# ---------------------------------------------------------------------------

if nav_sel:
    render_detail(nav_sel)

elif not nav_term:
    st.markdown("---")
    stats = query(
        "SELECT "
        "(SELECT COUNT(*) FROM actions) AS n_actions, "
        "(SELECT COUNT(*) FROM concepts) AS n_concepts, "
        "(SELECT COUNT(*) FROM relations r1"
        f" WHERE {symmetric_dedup_sql()}) AS n_relations"
    )[0]
    st.markdown(
        f"The database contains **{stats['n_actions']} actions**, "
        f"**{stats['n_concepts']} concepts**, and "
        f"**{stats['n_relations']} relations**.  \n"
        "Enter a search term above to explore."
    )
    st.markdown("**Try:**")
    if st.button("\U0001f3b2 Random search", key="random"):
        import random

        # Exclude the 'NA' sentinel (historian-confirmed "no equivalent") so
        # random search surfaces positive data only. 'NA' stays searchable
        # individually via the WordNet ID / Auto path.
        pool = query(
            "SELECT label AS term FROM actions "
            "UNION ALL "
            "SELECT label AS term FROM concepts "
            "UNION ALL "
            "SELECT e.value AS term "
            "FROM external_ids e WHERE e.resource IN ('wordnet30','wordnet31') "
            "AND e.value != 'NA'"
        )
        pick = random.choice(pool)
        st.query_params["q"] = pick["term"]
        # Leave the type on "Auto" — auto-detect resolves every pick (lemma or
        # WordNet ID); NA is excluded above so no ambiguous pick reaches here.
        st.query_params["t"] = "Auto"
        if "sel" in st.query_params:
            del st.query_params["sel"]
        st.rerun()
    examples = [
        ("dixit", "Lemma", "dixit — action search"),
        ("habuit", "Lemma", "habuit — action search"),
        ("adoravit", "Lemma", "adoravit — action with active meaning"),
        ("adoratus/a", "Lemma", "adoratus/a — action with passive meaning"),
        ("dedit se", "Lemma", "dedit se — action with reflexive meaning"),
        ("confession", "Lemma", "confession — concept search"),
    ]
    for term, stype, label in examples:
        if st.button(label, key=f"ex_{term}"):
            st.query_params["q"] = term
            # Leave the type on "Auto": clicking an example isn't an explicit
            # type choice, and auto-detect resolves every example correctly
            # (lemma / WordNet ID / UUID). The `stype` in the tuple documents
            # the expected resolution only.
            st.query_params["t"] = "Auto"
            if "sel" in st.query_params:
                del st.query_params["sel"]
            st.rerun()

else:
    results, effective_stype = run_search(nav_term, nav_stype)
    if not results:
        st.warning(f"No results found for **{nav_term}**.")
        if effective_stype == "Lemma":
            st.info("Lemma search uses prefix matching. Try a shorter query.")
        elif effective_stype == "UUID":
            st.info(
                "Paste the full UUID (e.g. `123974c0-b1d4-401d-8d9e-15b42b9118b0`)."
            )
        elif effective_stype == "WordNet ID":
            st.info("Enter a WordNet synset ID (e.g. `00014549-v`)")
    elif len(results) == 1:
        st.query_params["sel"] = results[0]["uuid"]
        st.rerun()
    else:
        render_results_list(results, nav_term, effective_stype)

render_footer()
