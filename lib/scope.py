"""DISSILEX symmetric-relation dedup helper (public app subset).

Extracted from the DISSILEX build library. Only the edge-count dedup rule the
Streamlit landing page needs is included here. The dev repo holds the full
module; keep symmetric_dedup_sql() byte-identical to it (a drift test guards
this).
"""

# Symmetric relation types whose bidirectional pairs are the SAME fact and so
# are deduplicated when counting edges (X->Y and Y->X counted once). Self-loops
# (src==tgt) are reciprocal-verb facts and are kept (counted once).
SYMMETRIC_DEDUP_RELATIONS = (
    'HAS_SYNONYM',
    'HAS_SUBJ_A1_RECIPROCAL',
    'HAS_ANTONYM',
)


def symmetric_dedup_sql():
    """SQL WHERE predicate that keeps each symmetric-pair edge once.

    Assumes the counted relations table is aliased `r1` (correlated subquery
    uses `r2`). Non-symmetric types always kept; symmetric types keep the
    src<tgt copy, a single-direction edge with no reverse, or a self-loop.
    """
    sql_list = ",".join(f"'{r}'" for r in SYMMETRIC_DEDUP_RELATIONS)
    return (
        f"r1.relation_type NOT IN ({sql_list})\n"
        "            OR r1.source_uuid < r1.target_uuid\n"
        "            OR r1.source_uuid = r1.target_uuid\n"
        "            OR NOT EXISTS (\n"
        "              SELECT 1 FROM relations r2\n"
        "              WHERE r2.relation_type = r1.relation_type\n"
        "                AND r2.source_uuid = r1.target_uuid\n"
        "                AND r2.target_uuid = r1.source_uuid\n"
        "            )"
    )
