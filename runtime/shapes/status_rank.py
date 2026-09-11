"""STATUS_RANK — the ONLY place the epistemic-status total order appears in source.

Plan v0.1.2 §5; runtime spec §4 (~ KL-11; v1.8 may reorder or flatten).
Every VALUES table and rank expression in the library is generated from here.
"""

STATUS_RANK = {"confirmed": 3, "time-sensitive": 2, "inferred": 1, "unverified": 0}

STATUSES = tuple(STATUS_RANK)


def rank(status):
    """Rank of a status value, or None if outside the vocabulary (never a default)."""
    return STATUS_RANK.get(status)


def values_table(status_var="?status", rank_var="?rank"):
    """Spec §7.2 VALUES form — valid in plain SPARQL (§7.3 CONSTRUCT)."""
    rows = " ".join(f'("{s}" {r})' for s, r in STATUS_RANK.items())
    return f"VALUES ({status_var} {rank_var}) {{ {rows} }}"


def rank_expr(var):
    """SHACL-SPARQL-safe rank lookup (BF-2, D-5a).

    W3C SHACL §5.3.2 forbids VALUES inside sh:select; this nested IF() is the
    equivalent: an unmatched value leaves the result unbound, so FILTER fails,
    exactly as an unmatched VALUES row would.
    """
    expr = "?__unbound"
    for status, r in reversed(list(STATUS_RANK.items())):
        expr = f'IF({var}="{status}",{r},{expr})'
    return expr


def sh_in_list():
    """Turtle list of the four values, for sh:in in Family B."""
    return "( " + " ".join(f'"{s}"' for s in STATUS_RANK) + " )"


# §7.4 register lattice (inverted: most restrictive wins). (c), non-enforcing (KL-4).
# Distinct order from STATUS_RANK; kept in this module so every ordering in the
# runtime is declared in one file.
REGISTER_RANK = {"governed-internal": 2, "contextual": 1, "plain": 0}


def register_rank(register):
    return REGISTER_RANK.get(register)
