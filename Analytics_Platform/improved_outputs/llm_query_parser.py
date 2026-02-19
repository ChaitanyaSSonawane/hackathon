"""
LLM Query Parser
================
Uses Ollama (local, free) to parse any natural language query into a
structured execution plan. Falls back to keyword detector if Ollama
is not running.
"""

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List


# ── Schema sent to the LLM with every request ──────────────────────────────

DATA_SCHEMA = """
DATASETS AND COLUMNS:
- "loan"    : date, branch, gold_loan_amt, home_loan_amt, personal_loan_amt,
              fd_deposit_amt, casa_balance, npa_percent
- "payment" : date, branch, upi_volume, upi_value, card_txn_volume,
              card_txn_value, wallet_txn_volume, wallet_txn_value, fraud_rate_percent
- "customer": date, branch, new_customers, active_customers, avg_credit_score,
              loan_default_rate_percent, customer_churn_rate_percent

Branches : Mumbai, Delhi, Pune, Bangalore, Chennai,
           Kolkata, Hyderabad, Ahmedabad, Jaipur, Surat
Date range: 2024-01-01 to 2024-12-30
"""

SYSTEM_PROMPT = f"""You are a banking analytics query planner.
Convert the user query into a JSON execution plan using the schema below.

{DATA_SCHEMA}

PLAN TYPES — set "type" to one of:
  "branch_comparison"              one metric ranked across branches
  "multi_metric_branch_comparison" multiple metrics side-by-side across branches
  "cross_metric_growth_comparison" branches where metric_a grows faster than metric_b
  "trend"                          metric over time (group_by = "date")
  "simple"                         single aggregated number

FIELDS:
  type, dataset, metric (single), metrics (list), metric_a, metric_b,
  aggregation, group_by, sort_order ("ascending"/"descending"), limit (int or null),
  filters: {{ branch: ["Mumbai","Pune"] }},
  date_filter: one of:
    {{ "type":"relative", "n":6, "unit":"month" }}
    {{ "type":"quarter",  "quarter":"3", "year":2024, "months":[7,8,9] }}
    {{ "type":"month",    "month":6, "year":2024 }}
    {{ "type":"year",     "year":2024 }}

AGGREGATIONS: sum, mean, growth, count, min, max, median
  - percent/rate columns  → mean
  - amounts/volumes       → sum
  - trend/growing         → growth

NATURAL LANGUAGE → COLUMN:
  deposit/fd/fixed deposit/savings → fd_deposit_amt
  gold loan / gl                   → gold_loan_amt
  home loan / housing / mortgage   → home_loan_amt
  personal loan / pl               → personal_loan_amt
  casa / current account           → casa_balance
  npa / non performing / bad loan  → npa_percent
  upi (default volume)             → upi_volume   ; if "value/amount" → upi_value
  card (default volume)            → card_txn_volume ; if "value/amount" → card_txn_value
  wallet                           → wallet_txn_volume ; if "value/amount" → wallet_txn_value
  fraud                            → fraud_rate_percent
  new customer / acquisition       → new_customers
  active customer                  → active_customers
  credit score                     → avg_credit_score
  default rate / loan default      → loan_default_rate_percent
  churn / attrition                → customer_churn_rate_percent
  generic "loan" (only if no specific loan type mentioned) → gold_loan_amt
  generic "performance"/"stats"    → active_customers (customer dataset)

RULES:
  - "top N"    → sort_order=descending, limit=N
  - "bottom N" → sort_order=ascending,  limit=N
  - "vs/and/both" with 2+ metrics     → multi_metric_branch_comparison, set metrics list
  - "highest X and Y"               → multi_metric_branch_comparison (NOT branch_comparison)
  - "growing faster than/outpacing"  → cross_metric_growth_comparison
  - "trend/over time/monthly"        → trend
  - For relative dates, data ends 2024-12-30 (use data max, not today)
  - Vague query → pick most sensible default

OUTPUT: valid JSON only — no markdown, no explanation."""


# ── HTTP helper ─────────────────────────────────────────────────────────────

def _post(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


# ── JSON extractor ───────────────────────────────────────────────────────────

def _extract_json(text: str) -> Optional[dict]:
    """
    Pull the first valid JSON object out of an LLM response.
    Handles markdown fences, preamble text, trailing explanation.
    """
    if not text:
        return None

    # Strip markdown fences
    text = re.sub(r"^```(?:json)?[ \t]*\n?", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\n?```[ \t]*$", "", text, flags=re.MULTILINE)
    text = text.strip()

    # Try direct parse
    try:
        r = json.loads(text)
        if isinstance(r, dict):
            return r
    except json.JSONDecodeError:
        pass

    # Find richest balanced JSON object in text
    best = None
    for m in re.finditer(r"\{", text):
        start, depth = m.start(), 0
        for i, ch in enumerate(text[start:]):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        candidate = json.loads(text[start: start + i + 1])
                        if isinstance(candidate, dict) and len(candidate) > best_len(best):
                            best = candidate
                    except Exception:
                        pass
                    break
    return best


def best_len(d: Optional[dict]) -> int:
    return len(d) if d else 0


# ── Ollama call ──────────────────────────────────────────────────────────────

def _call_ollama(query: str, model: str = "mistral") -> Optional[dict]:
    data = _post(
        "http://localhost:11434/api/chat",
        headers={"Content-Type": "application/json"},
        body={
            "model": model,
            "stream": False,
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Convert this query:\n\n{query}"},
            ],
        },
    )
    return _extract_json(data["message"]["content"])


# ── Plan normaliser ──────────────────────────────────────────────────────────

def _normalise(plan: dict) -> dict:
    """
    Map whatever the LLM returned → the exact format analytics_engine expects.
    """
    plan_type = (
        plan.get("type")
        or plan.get("comparison_type")
        or plan.get("plan_type")
        or "simple"
    )

    # filters
    raw = plan.get("filters") or {}
    branches = raw.get("branch") or plan.get("branch_filter") or plan.get("branches") or []
    if isinstance(branches, str):
        branches = [branches]
    filters = {}
    if branches:
        filters["branch"] = [b.capitalize() for b in branches]

    # date_filter
    date_filter = (
        raw.get("date_filter")
        or plan.get("date_filter")
        or plan.get("time_filter")
        or {}
    )

    # metrics
    metrics: List[str] = plan.get("metrics") or []
    metric: Optional[str] = plan.get("metric") or (metrics[0] if metrics else None)

    out: Dict[str, Any] = {
        "dataset":     plan.get("dataset", "loan"),
        "metric":      metric,
        "aggregation": plan.get("aggregation", "sum"),
        "filters":     filters,
        "group_by":    plan.get("group_by"),
        "sort_order":  plan.get("sort_order", "descending"),
        "limit":       plan.get("limit"),
    }

    if date_filter:
        out["date_filter"] = date_filter

    COMPARISON_TYPES = {
        "branch_comparison",
        "multi_metric_branch_comparison",
        "cross_metric_growth_comparison",
    }

    if plan_type in COMPARISON_TYPES:
        out["comparison_type"]   = plan_type
        out["comparison_column"] = plan.get("comparison_column", "branch")

    if plan_type == "multi_metric_branch_comparison" and metrics:
        out["metrics"] = metrics

    # Safety net: if 2+ metrics present but wrong type was inferred, auto-upgrade
    elif len(metrics) >= 2 and plan_type == "branch_comparison":
        out["comparison_type"] = "multi_metric_branch_comparison"
        out["metrics"] = metrics
        print("  ⚠ Auto-upgraded branch_comparison → multi_metric_branch_comparison")

    if plan_type == "cross_metric_growth_comparison":
        out["metric_a"] = plan.get("metric_a") or (metrics[0] if len(metrics) > 0 else metric)
        out["metric_b"] = plan.get("metric_b") or (metrics[1] if len(metrics) > 1 else None)
        out["metrics"]  = [out["metric_a"], out["metric_b"]]

    if plan_type == "trend":
        out["group_by"] = plan.get("group_by", "date")

    return out


# ── Keyword fallback ─────────────────────────────────────────────────────────

def _keyword_fallback(query: str) -> Dict[str, Any]:
    """Simple rule-based fallback used when Ollama is not running."""
    from improved_outputs.query_detector import QueryDetector
    qd = QueryDetector()

    if qd.is_cross_growth_query(query):
        return qd.build_cross_growth_plan(query)
    if qd.is_comparison_query(query):
        return qd.build_comparison_plan(query)

    metrics, dataset = qd.extract_metrics(query)
    branches         = qd.extract_branches(query)
    date_range       = qd.extract_date_range(query)

    defaults = {"loan": "gold_loan_amt", "payment": "upi_volume", "customer": "active_customers"}
    plan = {
        "dataset":    dataset,
        "metric":     metrics[0] if metrics else defaults.get(dataset, "gold_loan_amt"),
        "aggregation":"sum",
        "filters":    {"branch": branches} if branches else {},
        "group_by":   None,
        "sort_order": "descending",
        "limit":      None,
    }
    if date_range:
        plan["date_filter"] = date_range
    return plan


# ── Main class ───────────────────────────────────────────────────────────────

class LLMQueryParser:
    """
    Parse any natural language query into an execution plan.

    Usage:
        parser = LLMQueryParser()                          # auto (Ollama default)
        parser = LLMQueryParser(provider="ollama",
                                ollama_model="mistral")    # explicit
    """

    def __init__(self, provider: str = "ollama", ollama_model: str = "mistral"):
        self.provider      = provider
        self.ollama_model  = ollama_model
        print(f" LLMQueryParser ready — provider: {provider}, model: {ollama_model}")

    def parse(self, user_query: str) -> Dict[str, Any]:
        print(f"  → Parsing with Ollama ({self.ollama_model})...")
        try:
            result = _call_ollama(user_query, self.ollama_model)
            if result:
                plan = _normalise(result)
                print(f"  Plan: {plan}")
                return plan
        except urllib.error.URLError:
            print("  Ollama not reachable — is it running? (`ollama serve`)")
        except Exception as e:
            print(f"  Ollama error: {e}")

        print("  → Using keyword fallback...")
        return _keyword_fallback(user_query)