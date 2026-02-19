"""
Query Detector — Keyword-based fallback parser.
Used when Ollama is not running.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


VALID_BRANCHES = [
    "mumbai", "delhi", "pune", "bangalore", "chennai",
    "kolkata", "hyderabad", "ahmedabad", "jaipur", "surat",
]

# (keyword, column, dataset) — longest first to avoid partial matches
METRIC_MAP: List[Tuple[str, str, str]] = sorted([
    # loan
    ("gold loan",       "gold_loan_amt",               "loan"),
    ("gold loans",      "gold_loan_amt",               "loan"),
    ("gold lending",    "gold_loan_amt",               "loan"),
    ("home loan",       "home_loan_amt",               "loan"),
    ("home loans",      "home_loan_amt",               "loan"),
    ("housing loan",    "home_loan_amt",               "loan"),
    ("mortgage",        "home_loan_amt",               "loan"),
    ("personal loan",   "personal_loan_amt",           "loan"),
    ("personal loans",  "personal_loan_amt",           "loan"),
    ("fixed deposit",   "fd_deposit_amt",              "loan"),
    ("fixed deposits",  "fd_deposit_amt",              "loan"),
    ("fd",              "fd_deposit_amt",              "loan"),
    ("deposits",        "fd_deposit_amt",              "loan"),
    ("deposit",         "fd_deposit_amt",              "loan"),
    ("casa",            "casa_balance",                "loan"),
    ("current account", "casa_balance",                "loan"),
    ("savings account", "casa_balance",                "loan"),
    ("npa",             "npa_percent",                 "loan"),
    ("non performing",  "npa_percent",                 "loan"),
    ("bad loan",        "npa_percent",                 "loan"),
    ("bad loans",       "npa_percent",                 "loan"),
    # NOTE: generic "loan"/"loans" removed — now a fallback in extract_metrics()
    # to prevent shadowing "home loan", "personal loan" etc.
    # payment
    ("upi",             "upi_volume",                  "payment"),
    ("unified payment", "upi_volume",                  "payment"),
    ("credit card",     "card_txn_volume",             "payment"),
    ("debit card",      "card_txn_volume",             "payment"),
    ("card",            "card_txn_volume",             "payment"),
    ("digital wallet",  "wallet_txn_volume",           "payment"),
    ("e-wallet",        "wallet_txn_volume",           "payment"),
    ("wallet",          "wallet_txn_volume",           "payment"),
    ("fraud rate",      "fraud_rate_percent",          "payment"),
    ("fraud",           "fraud_rate_percent",          "payment"),
    # customer
    ("new customer",    "new_customers",               "customer"),
    ("active customer", "active_customers",            "customer"),
    ("credit score",    "avg_credit_score",            "customer"),
    ("default rate",    "loan_default_rate_percent",   "customer"),
    ("loan default",    "loan_default_rate_percent",   "customer"),
    ("churn",           "customer_churn_rate_percent", "customer"),
    ("attrition",       "customer_churn_rate_percent", "customer"),
    ("customer",        "active_customers",            "customer"),
], key=lambda x: len(x[0]), reverse=True)

VALUE_UPGRADES = {
    "upi_volume":        "upi_value",
    "card_txn_volume":   "card_txn_value",
    "wallet_txn_volume": "wallet_txn_value",
}

MULTI_METRIC_CONNECTORS = [
    "compared to", "vs", "versus", "against",
    "and", "or", "plus", "&", "also", "with", ",",
]

COMPARISON_KEYWORDS = [
    "compare", "versus", "vs", "between", "against",
    "which branch", "what branch", "which location",
    "highest", "lowest", "best", "worst", "top", "bottom",
    "all branches", "each branch", "by branch", "across branches",
    "ranking", "rank", "growing faster", "outperform",
    "find branches", "branches where", "faster than",
]

CROSS_GROWTH_PATTERNS = [
    r"growing faster than",
    r"grows? faster than",
    r"growth.*faster.*than",
    r"faster.*growth.*than",
    r"faster than",
    r"outpac(ing|e)",
    r"higher growth than",
]

GROWTH_KEYWORDS = [
    "growth", "trend", "increase", "decrease", "rise", "fall",
    "growing", "declining", "over time", "timeline", "progression",
]

DEFAULT_METRICS = {
    "loan":     "gold_loan_amt",
    "payment":  "upi_volume",
    "customer": "active_customers",
}

QUARTER_MONTHS = {
    "1": [1,2,3], "2": [4,5,6], "3": [7,8,9], "4": [10,11,12],
}

MONTH_MAP = {
    "january":1,"february":2,"march":3,"april":4,
    "may":5,"june":6,"july":7,"august":8,
    "september":9,"october":10,"november":11,"december":12,
}


class QueryDetector:

    # ── Public API ─────────────────────────────────────────────────

    def is_comparison_query(self, query: str) -> bool:
        q = query.lower()
        return any(kw in q for kw in COMPARISON_KEYWORDS)

    def is_cross_growth_query(self, query: str) -> bool:
        q = query.lower()
        return any(re.search(p, q) for p in CROSS_GROWTH_PATTERNS)

    def is_multi_metric_query(self, query: str) -> bool:
        metrics, _ = self.extract_metrics(query)
        if len(metrics) < 2:
            return False
        q = query.lower()
        return any(kw in q for kw in MULTI_METRIC_CONNECTORS)

    def extract_branches(self, query: str) -> List[str]:
        q = query.lower()
        if any(p in q for p in ["all branches", "all branch", "every branch", "each branch"]):
            return []
        return [b.capitalize() for b in VALID_BRANCHES if re.search(r"\b" + b + r"\b", q)]

    def extract_metrics(self, query: str) -> Tuple[List[str], str]:
        q = query.lower()
        wants_value = any(w in q for w in ["value", "amount", "rupee", "inr"])
        found_cols, found_ds, consumed = [], [], []

        for kw, col, ds in METRIC_MAP:
            for m in re.finditer(r"\b" + re.escape(kw) + r"\b", q):
                s, e = m.start(), m.end()
                if any(cs <= s and e <= ce for cs, ce in consumed):
                    continue
                actual = VALUE_UPGRADES.get(col, col) if wants_value else col
                if actual not in found_cols:
                    found_cols.append(actual)
                    found_ds.append(ds)
                consumed.append((s, e))
                break

        # Fallback: if no specific loan metric found but "loan" is in query → default to gold_loan_amt
        if not found_cols and re.search(r"\bloan\b", q):
            found_cols = ["gold_loan_amt"]
            found_ds   = ["loan"]

        dataset = max(set(found_ds), key=found_ds.count) if found_ds else self._infer_dataset(q)
        return found_cols, dataset

    def extract_date_range(self, query: str) -> Dict[str, Any]:
        q = query.lower()

        m = re.search(r"last\s+(\d+)\s+(day|week|month|year)s?", q, re.IGNORECASE)
        if m:
            n, unit = int(m.group(1)), m.group(2).lower()
            r: Dict[str, Any] = {"type": "relative", "n": n, "unit": unit}
            if unit == "month": r["months"] = n
            elif unit == "day":   r["days"]   = n
            elif unit == "week":  r["days"]   = n * 7
            elif unit == "year":  r["years"]  = n
            return r

        m = re.search(r"\bq([1-4])\b.*?(\d{4})", q, re.IGNORECASE)
        if m:
            return {"type":"quarter","quarter":m.group(1),"year":int(m.group(2)),"months":QUARTER_MONTHS[m.group(1)]}

        month_pat = "|".join(MONTH_MAP)
        m = re.search(rf"({month_pat})\s+(\d{{4}})", q, re.IGNORECASE)
        if m:
            return {"type":"month","month":MONTH_MAP[m.group(1).lower()],"year":int(m.group(2))}

        m = re.search(r"\b(20\d{2})\b", q)
        if m:
            return {"type":"year","year":int(m.group(1))}

        return {}

    def build_comparison_plan(self, query: str) -> Dict[str, Any]:
        if self.is_cross_growth_query(query):
            return self.build_cross_growth_plan(query)

        q          = query.lower()
        metrics, dataset = self.extract_metrics(query)
        branches   = self.extract_branches(query)
        date_range = self.extract_date_range(query)

        # limit / sort
        limit, sort_order = None, "descending"
        tm = re.search(r"\btop\s+(\d+)\b", q)
        bm = re.search(r"\bbottom\s+(\d+)\b", q)
        if tm:   limit, sort_order = int(tm.group(1)), "descending"
        elif bm: limit, sort_order = int(bm.group(1)), "ascending"
        # NOTE: "highest"/"lowest" without explicit "top N" means sort only — no limit=1
        # so that multi-metric queries still rank ALL branches side by side.
        elif any(w in q for w in ["lowest","worst","least","minimum"]): sort_order = "ascending"

        agg = self._aggregation(q, metrics[0] if metrics else "")
        filters = {"branch": branches} if branches else {}

        plan: Dict[str, Any] = {
            "comparison_column": "branch",
            "dataset":           dataset,
            "aggregation":       agg,
            "filters":           filters,
            "group_by":          None,
            "sort_order":        sort_order,
            "limit":             limit,
        }
        if date_range:
            plan["date_filter"] = date_range

        if len(metrics) >= 2 and any(kw in q for kw in MULTI_METRIC_CONNECTORS):
            plan["comparison_type"] = "multi_metric_branch_comparison"
            plan["metrics"]         = metrics
            plan["metric"]          = metrics[0]
            plan["limit"]           = limit  # apply limit AFTER type is determined
            return plan

        # Single-metric path: "highest" means show top 1 branch
        if any(w in q for w in ["highest","best","most","maximum"]) and not tm:
            limit = 1
        elif any(w in q for w in ["lowest","worst","least","minimum"]) and not bm:
            limit = 1
        plan["limit"]           = limit
        plan["comparison_type"] = "branch_comparison"
        plan["metric"]          = metrics[0] if metrics else DEFAULT_METRICS.get(dataset, "gold_loan_amt")
        return plan

    def build_cross_growth_plan(self, query: str) -> Dict[str, Any]:
        metrics, dataset = self.extract_metrics(query)
        branches         = self.extract_branches(query)
        date_range       = self.extract_date_range(query)

        if len(metrics) < 2:
            other = "gold_loan_amt" if (not metrics or metrics[0] != "gold_loan_amt") else "fd_deposit_amt"
            metrics = (metrics or []) + [other]
            metrics = metrics[:2]

        plan: Dict[str, Any] = {
            "comparison_type":   "cross_metric_growth_comparison",
            "comparison_column": "branch",
            "dataset":           dataset,
            "metric_a":          metrics[0],
            "metric_b":          metrics[1],
            "metrics":           metrics,
            "metric":            metrics[0],
            "aggregation":       "growth",
            "filters":           {"branch": branches} if branches else {},
            "group_by":          None,
            "sort_order":        "descending",
            "limit":             None,
        }
        if date_range:
            plan["date_filter"] = date_range
        return plan

    # ── Private helpers ────────────────────────────────────────────

    def _aggregation(self, q: str, metric: str) -> str:
        if any(w in q for w in GROWTH_KEYWORDS):       return "growth"
        if any(w in q for w in ["average","mean","avg"]): return "mean"
        if "count" in q or "how many" in q:            return "count"
        if any(x in metric for x in ["percent","rate","score"]): return "mean"
        return "sum"

    def _infer_dataset(self, q: str) -> str:
        scores = {
            "payment":  sum(1 for s in ["payment","transaction","digital","transfer"] if s in q),
            "customer": sum(1 for s in ["customer","user","client","member","performance"] if s in q),
            "loan":     sum(1 for s in ["loan","lending","credit","borrow","disburse"] if s in q),
        }
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "loan"