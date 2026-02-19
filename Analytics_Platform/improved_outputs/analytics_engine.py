"""
Analytics Engine
Executes execution plans against DataFrames.
Filters are always applied first, before any analytics.
"""

import pandas as pd
from typing import Dict, Any, List, Optional


class AnalyticsEngine:

    def execute_plan(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        # Always filter first
        working = df.copy()
        working = self._apply_filters(working, plan.get("filters", {}))
        working = self._apply_date_filter(working, plan.get("date_filter", {}))

        if working.empty:
            return {
                "success": False,
                "error": "No data matches the filters. Check branch names or date range.",
                "value": 0,
            }

        ctype = plan.get("comparison_type")
        if ctype == "multi_metric_branch_comparison":
            return self._multi_metric(working, plan)
        if ctype == "cross_metric_growth_comparison":
            return self._cross_growth(working, plan)
        if ctype:
            return self._single_metric_comparison(working, plan)
        return self._standard(working, plan)

    # ── Comparison handlers ────────────────────────────────────────

    def _multi_metric(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        col    = plan.get("comparison_column", "branch")
        metrics: List[str] = plan.get("metrics", [])
        agg    = plan.get("aggregation", "sum")

        if not metrics:
            return {"success": False, "error": "No metrics specified"}

        missing = [m for m in metrics if m not in df.columns]
        if missing:
            return {"success": False, "error": f"Columns not found: {missing}. Available: {list(df.columns)}"}
        if col not in df.columns:
            return {"success": False, "error": f"Column '{col}' not in data"}

        data = {m: self._agg(df.groupby(col)[m], agg) for m in metrics}
        result_df = pd.DataFrame(data)
        result_df["total"] = result_df.sum(axis=1)

        asc = plan.get("sort_order") == "ascending"
        result_df = result_df.sort_values("total", ascending=asc)
        if plan.get("limit"):
            result_df = result_df.head(plan["limit"])

        winner = result_df.index[0] if len(result_df) else "N/A"
        return {
            "success":              True,
            "multi_metric_comparison": result_df,
            "comparison_data":      result_df["total"],
            "grouped_data":         result_df,
            "value":                float(result_df["total"].iloc[0]) if len(result_df) else 0,
            "winner":               winner,
            "metrics":              metrics,
            "metric_breakdown":     {m: result_df[m].to_dict() for m in metrics},
            "comparison_type":      col,
            "count":                len(result_df),
        }

    def _single_metric_comparison(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        col    = plan.get("comparison_column", "branch")
        metric = plan.get("metric")
        agg    = plan.get("aggregation", "sum")

        if not metric:
            return {"success": False, "error": "No metric in plan"}
        if col not in df.columns:
            return {"success": False, "error": f"Column '{col}' not in data"}
        if metric not in df.columns:
            return {"success": False, "error": f"Metric '{metric}' not found. Available: {list(df.columns)}"}

        data = self._agg(df.groupby(col)[metric], agg)
        asc  = plan.get("sort_order") == "ascending"
        data = data.sort_values(ascending=asc)
        if plan.get("limit"):
            data = data.head(plan["limit"])

        winner = data.index[0] if len(data) else "N/A"
        return {
            "success":         True,
            "comparison_data": data,
            "grouped_data":    data,
            "value":           float(data.iloc[0]) if len(data) else 0,
            "winner":          winner,
            "comparison_type": col,
            "count":           len(data),
        }

    def _cross_growth(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        col      = plan.get("comparison_column", "branch")
        metric_a = plan.get("metric_a")
        metric_b = plan.get("metric_b")

        if not metric_a or not metric_b:
            return {"success": False, "error": "cross_metric_growth needs metric_a and metric_b"}

        missing = [m for m in [metric_a, metric_b] if m not in df.columns]
        if missing:
            return {"success": False, "error": f"Columns not found: {missing}"}

        def growth(series: pd.Series) -> float:
            s = series.dropna()
            if len(s) < 2 or s.iloc[0] == 0:
                return 0.0
            return float((s.iloc[-1] - s.iloc[0]) / s.iloc[0] * 100)

        rows = []
        for branch, grp in df.groupby(col):
            grp = grp.sort_values("date") if "date" in grp.columns else grp
            ga, gb = growth(grp[metric_a]), growth(grp[metric_b])
            rows.append({
                "branch":               branch,
                f"{metric_a}_growth":   round(ga, 2),
                f"{metric_b}_growth":   round(gb, 2),
                "growth_diff":          round(ga - gb, 2),
                "faster":               ga > gb,
            })

        result_df   = pd.DataFrame(rows).set_index("branch")
        qualifying  = result_df[result_df["faster"]].sort_values("growth_diff", ascending=False)
        comp_data   = result_df[f"{metric_a}_growth"].sort_values(ascending=False)

        return {
            "success":            True,
            "cross_growth_data":  result_df,
            "qualifying_branches":qualifying,
            "comparison_data":    comp_data,
            "value":              len(qualifying),
            "winner":             qualifying.index[0] if len(qualifying) else "N/A",
            "metrics":            [metric_a, metric_b],
            "metric_breakdown": {
                metric_a: result_df[f"{metric_a}_growth"].to_dict(),
                metric_b: result_df[f"{metric_b}_growth"].to_dict(),
            },
            "count":   len(result_df),
            "summary": (
                f"{len(qualifying)} branch(es) where {metric_a.replace('_',' ')} grows faster "
                f"than {metric_b.replace('_',' ')}: {', '.join(qualifying.index.tolist())}"
                if len(qualifying) else
                f"No branches where {metric_a.replace('_',' ')} grows faster than {metric_b.replace('_',' ')}"
            ),
        }

    def _standard(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        metric = plan.get("metric")
        if not metric:
            return {"success": False, "error": "No metric in plan", "value": 0}
        if metric not in df.columns:
            return {"success": False, "error": f"'{metric}' not found. Available: {list(df.columns)}", "value": 0}

        group_by = plan.get("group_by")
        agg      = plan.get("aggregation", "sum")

        if group_by and group_by in df.columns:
            trend = self._agg(df.groupby(group_by)[metric], agg).sort_index()
            total = float(df[metric].sum()) if agg == "growth" else float(trend.sum())
            return {"success": True, "value": total, "trend_data": trend, "grouped_data": trend, "count": len(trend)}

        value = self._scalar(df[metric], agg)
        return {"success": True, "value": value, "count": len(df)}

    # ── Filters ────────────────────────────────────────────────────

    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        for col, val in filters.items():
            if col not in df.columns:
                print(f"⚠️  Filter column '{col}' not found, skipping")
                continue
            if isinstance(val, (list, tuple)):
                df = df[df[col].isin(val)]
            elif isinstance(val, dict):
                if "min" in val: df = df[df[col] >= val["min"]]
                if "max" in val: df = df[df[col] <= val["max"]]
            else:
                df = df[df[col] == val]
        return df

    def _apply_date_filter(self, df: pd.DataFrame, date_filter: Dict[str, Any]) -> pd.DataFrame:
        if not date_filter:
            return df
        date_col = next((c for c in df.columns if any(k in c.lower() for k in ["date","month","period","time"])), None)
        if not date_col:
            return df

        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

        t = date_filter.get("type")

        if t == "relative":
            end   = df[date_col].max()
            n     = date_filter.get("n", 1)
            unit  = date_filter.get("unit", "month")
            if unit == "month" or "months" in date_filter:
                start = end - pd.DateOffset(months=date_filter.get("months", n))
            elif unit == "day" or "days" in date_filter:
                start = end - pd.Timedelta(days=date_filter.get("days", n))
            elif unit == "week":
                start = end - pd.Timedelta(days=n * 7)
            elif unit == "year" or "years" in date_filter:
                start = end - pd.DateOffset(years=date_filter.get("years", n))
            else:
                return df
            print(f"📅 Date filter: {start.date()} → {end.date()}")
            df = df[(df[date_col] >= start) & (df[date_col] <= end)]

        elif t == "quarter":
            yr, months = date_filter.get("year"), date_filter.get("months", [])
            if yr and months:
                df = df[(df[date_col].dt.year == yr) & (df[date_col].dt.month.isin(months))]

        elif t == "month":
            yr, mo = date_filter.get("year"), date_filter.get("month")
            if yr and mo:
                df = df[(df[date_col].dt.year == yr) & (df[date_col].dt.month == mo)]
            elif yr:
                df = df[df[date_col].dt.year == yr]

        elif t == "year":
            yr = date_filter.get("year")
            if yr:
                df = df[df[date_col].dt.year == yr]

        return df

    # ── Aggregation helpers ────────────────────────────────────────

    def _agg(self, grouped, agg: str) -> pd.Series:
        if agg == "sum":    return grouped.sum()
        if agg in ("mean","avg"): return grouped.mean()
        if agg == "count":  return grouped.count()
        if agg == "min":    return grouped.min()
        if agg == "max":    return grouped.max()
        if agg == "median": return grouped.median()
        if agg == "growth":
            s = grouped.sum()
            return s.pct_change().fillna(0) * 100 if len(s) > 1 else s
        return grouped.sum()

    def _scalar(self, series: pd.Series, agg: str) -> float:
        if agg == "sum":    return float(series.sum())
        if agg in ("mean","avg"): return float(series.mean())
        if agg == "count":  return float(series.count())
        if agg == "min":    return float(series.min())
        if agg == "max":    return float(series.max())
        if agg == "median": return float(series.median())
        if agg == "growth":
            if len(series) > 1:
                f, l = series.iloc[0], series.iloc[-1]
                return float((l - f) / f * 100) if f != 0 else 0.0
            return 0.0
        return float(series.sum())