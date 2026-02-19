
"""
Insight Generator - Complete with multi-metric breakdown
Generates rich insights for all query types
"""
import pandas as pd
from typing import Dict, Any

class InsightGenerator:
    """Generates insights from results"""
    
    def __init__(self):
        pass
    
    def generate_insights(self, result: Dict[str, Any], plan: Dict[str, Any], query: str) -> str:
        """Generate insights from analysis results"""
        insights = []
        
        # Multi-metric comparison
        if 'multi_metric_comparison' in result and result['multi_metric_comparison'] is not None:
            return self._generate_multi_metric_insights(result, plan)
        
        # Regular insights
        metric_name = (plan.get('metric') or 'Value').replace('_', ' ').title()
        
        # Main value
        if 'value' in result:
            value = result['value']
            insights.append(f"📊 **{metric_name}**: {self._format_number(value)}")
        
        # Comparison insights
        if 'comparison_data' in result and result['comparison_data'] is not None:
            comp_insight = self._analyze_comparison(result, metric_name, plan)
            if comp_insight:
                insights.append(comp_insight)
        
        # Trend insights
        elif 'trend_data' in result and result['trend_data'] is not None:
            trend_insight = self._analyze_trend(result['trend_data'], metric_name)
            if trend_insight:
                insights.append(trend_insight)
        
        # Filters
        if plan.get('filters'):
            filter_desc = self._describe_filters(plan['filters'])
            insights.append(f"🔍 **Filters**: {filter_desc}")
        
        # Records analyzed
        if 'count' in result:
            insights.append(f"📈 **Records Analyzed**: {result['count']}")
        
        return "\n".join(insights)
    
    def _generate_multi_metric_insights(self, result: Dict, plan: Dict) -> str:
        """Generate insights for multi-metric comparison"""
        insights = []
        comparison_df = result['multi_metric_comparison']
        metrics = result.get('metrics', [])
        
        # Winner announcement
        if 'winner' in result and result['winner'] != 'N/A':
            winner = result['winner']
            total_value = result['value']
            metric_labels = ' + '.join(m.replace('_',' ').title() for m in metrics)
            insights.append(f"🏆 **Winner**: {winner} with {self._format_number(total_value)} combined ({metric_labels})")
        
        # Breakdown by metric
        if 'metric_breakdown' in result:
            insights.append("\n📊 **Metric Breakdown**:")
            breakdown = result['metric_breakdown']
            winner = result.get('winner', 'N/A')
            
            for metric in metrics:
                metric_name = metric.replace('_', ' ').title()
                if winner in breakdown[metric]:
                    value = breakdown[metric][winner]
                    insights.append(f"   • {metric_name}: {self._format_number(value)}")
        
        # Top 3 branches
        if len(comparison_df) >= 3:
            insights.append("\n📊 **Top 3 Branches**:")
            for i, (branch, row) in enumerate(comparison_df.head(3).iterrows(), 1):
                total = row['total']
                metric_vals = [f"{m.replace('_', ' ').title()[:15]}: {self._format_number(row[m])}" 
                              for m in metrics]
                insights.append(f"   {i}. {branch}: {self._format_number(total)} total")
                for mv in metric_vals:
                    insights.append(f"      - {mv}")
        elif len(comparison_df) > 0:
            # Show all if less than 3
            insights.append("\n📊 **All Branches**:")
            for branch, row in comparison_df.iterrows():
                total = row['total']
                insights.append(f"   • {branch}: {self._format_number(total)} total")
        
        # Calculate range
        if len(comparison_df) >= 2:
            highest = comparison_df['total'].max()
            lowest = comparison_df['total'].min()
            diff_pct = ((highest - lowest) / lowest * 100) if lowest != 0 else 0
            insights.append(f"\n📉 **Range**: {diff_pct:.1f}% difference between highest and lowest")
        
        return "\n".join(insights)
    
    def _analyze_comparison(self, result: Dict, metric_name: str, plan: Dict = None) -> str:
        """Analyze comparison results"""
        comparison_data = result['comparison_data']
        
        if len(comparison_data) == 0:
            return ""
        
        insights = []
        
        # Winner
        if 'winner' in result and result['winner'] != 'N/A':
            winner_value = result['value']
            insights.append(f"🏆 **Winner**: {result['winner']} with {self._format_number(winner_value)}")
        
        # Show results based on how many were requested
        # limit=1 → user asked for the single winner only; do NOT show other branches
        limit = plan.get("limit") if plan else None
        if limit == 1:
            # Only the winner — no secondary info
            pass
        elif len(comparison_data) > 3:
            top3 = comparison_data.head(3)
            top3_str = ", ".join([f"{idx} ({self._format_number(val)})" for idx, val in top3.items()])
            insights.append(f"📊 **Top 3**: {top3_str}")
        else:
            all_str = ", ".join([f"{idx} ({self._format_number(val)})" for idx, val in comparison_data.items()])
            insights.append(f"📊 **Results**: {all_str}")

        # Range only meaningful when showing multiple branches
        if limit != 1 and len(comparison_data) >= 2:
            highest = comparison_data.max()
            lowest = comparison_data.min()
            diff_pct = ((highest - lowest) / lowest * 100) if lowest != 0 else 0
            insights.append(f"📉 **Range**: {diff_pct:.1f}% difference between highest and lowest")
        
        return "\n".join(insights)
    
    def _analyze_trend(self, trend_data: pd.Series, metric_name: str) -> str:
        """Analyze trend"""
        if len(trend_data) < 2:
            return ""
        
        values = trend_data.values
        first_val = values[0]
        last_val = values[-1]
        
        if last_val > first_val:
            change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            direction = "📈 **Trending Up**"
            insight = f"{direction}: {metric_name} increased by {abs(change_pct):.1f}% over the period"
        elif last_val < first_val:
            change_pct = ((first_val - last_val) / first_val * 100) if first_val != 0 else 0
            direction = "📉 **Trending Down**"
            insight = f"{direction}: {metric_name} decreased by {abs(change_pct):.1f}% over the period"
        else:
            direction = "➡️ **Stable**"
            insight = f"{direction}: {metric_name} remained relatively stable"
        
        # Peak and trough
        if len(trend_data) > 5:
            max_val = values.max()
            min_val = values.min()
            max_idx = values.argmax()
            min_idx = values.argmin()
            
            peak_date = trend_data.index[max_idx]
            trough_date = trend_data.index[min_idx]
            
            insight += f"\n   • Peak: {self._format_number(max_val)} at {peak_date}"
            insight += f"\n   • Lowest: {self._format_number(min_val)} at {trough_date}"
        
        return insight
    
    def _describe_filters(self, filters: Dict[str, Any]) -> str:
        """Describe filters"""
        descriptions = []
        for column, value in filters.items():
            col_name = column.replace('_', ' ').title()
            if isinstance(value, (list, tuple)):
                descriptions.append(f"{col_name} in {', '.join(map(str, value))}")
            else:
                descriptions.append(f"{col_name} = {value}")
        return ", ".join(descriptions) if descriptions else "None"
    
    def _format_number(self, num: float) -> str:
        """Format number with units"""
        if abs(num) >= 1_000_000_000:
            return f"{num/1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"{num/1_000:.2f}K"
        else:
            return f"{num:.2f}"