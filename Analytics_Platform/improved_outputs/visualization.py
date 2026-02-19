"""
Visualization Engine
Creates Plotly charts for all result types.
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, Any, Optional, List

PALETTE = ["#667eea", "#f6ad55", "#68d391", "#fc8181", "#76e4f7", "#b794f4"]


class VisualizationEngine:

    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def create_visualization(self, result: Dict[str, Any], plan: Dict[str, Any]) -> Optional[str]:
        try:
            if result.get("cross_growth_data") is not None:
                return self._cross_growth_chart(result, plan)
            if result.get("multi_metric_comparison") is not None:
                return self._multi_metric_chart(result, plan)
            if result.get("comparison_data") is not None:
                return self._comparison_chart(result, plan)
            if result.get("trend_data") is not None:
                return self._trend_chart(result, plan)
            if "value" in result:
                return self._metric_card(result, plan)
        except Exception as e:
            print(f"⚠️  Visualization error: {e}")
        return None

    # ── Chart types ────────────────────────────────────────────────

    def _cross_growth_chart(self, result: Dict, plan: Dict) -> str:
        df      = result["cross_growth_data"]
        metrics = result.get("metrics", [])
        if len(metrics) < 2:
            return self._comparison_chart(result, plan)

        ma, mb = metrics[0], metrics[1]
        qualifying = set(result.get("qualifying_branches", pd.DataFrame()).index.tolist())

        colors_a = [PALETTE[0] if b in qualifying else "#a0aec0" for b in df.index]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=f"{ma.replace('_',' ').title()} Growth %",
            x=df.index.tolist(),
            y=df[f"{ma}_growth"].tolist(),
            marker_color=colors_a,
            text=[f"{v:.1f}%" for v in df[f"{ma}_growth"]],
            textposition="outside",
        ))
        fig.add_trace(go.Bar(
            name=f"{mb.replace('_',' ').title()} Growth %",
            x=df.index.tolist(),
            y=df[f"{mb}_growth"].tolist(),
            marker_color=PALETTE[1],
            text=[f"{v:.1f}%" for v in df[f"{mb}_growth"]],
            textposition="outside",
        ))

        summary = result.get("summary", "")
        fig.update_layout(
            title={"text": f"{ma.replace('_',' ').title()} vs {mb.replace('_',' ').title()} Growth<br><sub>{summary}</sub>",
                   "x": 0.5, "xanchor": "center"},
            barmode="group",
            xaxis_title="Branch",
            yaxis_title="Growth (%)",
            template="plotly_white",
            height=520,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.4)
        return self._save(fig, f"cross_growth_{ma}_vs_{mb}")

    def _multi_metric_chart(self, result: Dict, plan: Dict) -> str:
        df      = result["multi_metric_comparison"]
        metrics: List[str] = result.get("metrics", [c for c in df.columns if c != "total"])
        winner  = result.get("winner", "")

        fig = go.Figure()
        for i, metric in enumerate(metrics):
            if metric not in df.columns:
                continue
            fig.add_trace(go.Bar(
                name=metric.replace("_", " ").title(),
                x=df.index.tolist(),
                y=df[metric].tolist(),
                marker_color=PALETTE[i % len(PALETTE)],
                text=df[metric].tolist(),
                texttemplate="%{text:,.0f}",
                textposition="outside",
            ))

        title = " & ".join(m.replace("_"," ").title() for m in metrics) + " by Branch"
        if winner:
            title += f"<br><sub>Winner: {winner}</sub>"

        fig.update_layout(
            title={"text": title, "x": 0.5, "xanchor": "center"},
            barmode="group",
            xaxis_title="Branch",
            yaxis_title="Value",
            template="plotly_white",
            height=520,
        )
        return self._save(fig, "multi_metric_" + "_".join(metrics))

    def _comparison_chart(self, result: Dict, plan: Dict) -> str:
        data = result["comparison_data"]
        if isinstance(data, pd.Series):
            df = data.reset_index()
            df.columns = ["Category", "Value"]
        else:
            df = pd.DataFrame(list(data.items()), columns=["Category", "Value"])

        metric_label = (plan.get("metric") or "Value").replace("_", " ").title()
        winner = str(result.get("winner", ""))
        colors = [PALETTE[0] if str(row["Category"]) == winner else "#a0aec0"
                  for _, row in df.iterrows()]

        fig = go.Figure(go.Bar(
            x=df["Category"],
            y=df["Value"],
            marker_color=colors,
            text=df["Value"],
            texttemplate="%{text:,.0f}",
            textposition="outside",
        ))
        fig.update_layout(
            title={"text": f"{metric_label} by Branch" + (f"<br><sub>Winner: {winner}</sub>" if winner else ""),
                   "x": 0.5, "xanchor": "center"},
            xaxis_title="Branch",
            yaxis_title=metric_label,
            template="plotly_white",
            height=500,
            showlegend=False,
        )
        return self._save(fig, f"comparison_{plan.get('metric','value')}")

    def _trend_chart(self, result: Dict, plan: Dict) -> str:
        data = result["trend_data"]
        if isinstance(data, pd.Series):
            df = data.reset_index()
            df.columns = ["Date", "Value"]
        else:
            df = pd.DataFrame(data)

        metric_label = (plan.get("metric") or "Value").replace("_", " ").title()

        fig = go.Figure(go.Scatter(
            x=df.iloc[:, 0],
            y=df.iloc[:, 1],
            mode="lines+markers",
            name=metric_label,
            line=dict(color=PALETTE[0], width=3),
            marker=dict(size=6),
        ))
        fig.update_layout(
            title={"text": f"{metric_label} Trend", "x": 0.5, "xanchor": "center"},
            xaxis_title="Date",
            yaxis_title=metric_label,
            template="plotly_white",
            height=500,
            hovermode="x unified",
        )
        fig.update_xaxes(rangeslider_visible=True)
        return self._save(fig, f"trend_{plan.get('metric','value')}")

    def _metric_card(self, result: Dict, plan: Dict) -> str:
        metric_label = (plan.get("metric") or "Value").replace("_", " ").title()
        fig = go.Figure(go.Indicator(
            mode="number",
            value=result.get("value", 0),
            title={"text": metric_label},
            number={"valueformat": ",.0f"},
        ))
        fig.update_layout(height=400, template="plotly_white")
        return self._save(fig, f"metric_{plan.get('metric','value')}")

    def _save(self, fig: go.Figure, prefix: str) -> str:
        ts   = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"{prefix}_{ts}.html"
        fig.write_html(str(path))
        return str(path)