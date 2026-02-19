"""
MCP Analytics Platform
Main entry point — used by app.py (Streamlit) and CLI.
"""

import json
import os
from typing import Dict, Any, Optional

from improved_outputs.data_loader import DataLoader
from improved_outputs.analytics_engine import AnalyticsEngine
from improved_outputs.visualization import VisualizationEngine
from improved_outputs.insight_generator import InsightGenerator
from improved_outputs.llm_query_parser import LLMQueryParser


class MCPAnalyticsPlatform:

    def __init__(self, use_local_llm: bool = True):
        print("🚀 Initialising MCP Analytics Platform...")

        self.use_local_llm    = use_local_llm
        self.data_loader      = DataLoader()
        self.analytics_engine = AnalyticsEngine()
        self.viz_engine       = VisualizationEngine()
        self.insight_gen      = InsightGenerator()

        # Primary query parser — Ollama/Mistral (local, free) or fallback to remote
        provider = "ollama" if use_local_llm else "openai"
        self.parser = LLMQueryParser(provider=provider, ollama_model="mistral")

        # Load datasets
        self.datasets = self.data_loader.load_all_datasets()
        if not self.datasets:
            print("⚠️  No datasets loaded!")
        else:
            print(f"✅ Loaded datasets: {list(self.datasets.keys())}\n")

    # ── Public API ────────────────────────────────────────────

    def process_query(self, user_query: str) -> Dict[str, Any]:
        print(f"\n📝 Query: '{user_query}'")
        try:
            # 1. Parse natural language → execution plan
            plan = self.parser.parse(user_query)

            # 2. Resolve dataset
            dataset_name = plan.get("dataset", "loan")
            df = self.datasets.get(dataset_name)
            if df is None:
                return {
                    "success": False,
                    "error": f"Dataset '{dataset_name}' not found. Available: {list(self.datasets.keys())}",
                    "query": user_query,
                }

            print(f"📋 Plan: {json.dumps(plan, indent=2, default=str)}")

            # 3. Execute analytics
            print("⚙️  Executing...")
            result = self.analytics_engine.execute_plan(df, plan)
            if not result.get("success", True):
                return {"success": False, "error": result.get("error", "Analytics failed"), "query": user_query}

            # 4. Visualise
            print("📊 Creating chart...")
            viz_path = self.viz_engine.create_visualization(result, plan)

            # 5. Insights
            print("💡 Generating insights...")
            insights = self.insight_gen.generate_insights(result, plan, user_query)

            return {
                "success":       True,
                "query":         user_query,
                "plan":          plan,
                "result":        result,
                "visualization": viz_path,
                "insights":      insights,
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "query": user_query}

    # ── Interactive CLI mode ──────────────────────────────────

    def interactive_mode(self):
        print("=" * 60)
        print("🎯  MCP Analytics Platform — Interactive Mode")
        print("=" * 60)
        print("\nDatasets loaded:")
        for name, df in self.datasets.items():
            print(f"  • {name}: {len(df):,} rows")
        print("\nType any question. Type 'exit' to quit.\n")

        while True:
            try:
                query = input("💬  Your query: ").strip()
                if not query:
                    continue
                if query.lower() in ("exit", "quit", "q"):
                    print("👋 Goodbye!")
                    break
                response = self.process_query(query)
                print("\n" + "=" * 60)
                if response["success"]:
                    r = response["result"]
                    if "value" in r:
                        print(f"📈 Result : {r['value']:,.2f}")
                    if response.get("insights"):
                        print(f"\n{response['insights']}")
                    if response.get("visualization"):
                        print(f"\n📊 Chart  : {response['visualization']}")
                else:
                    print(f"❌ Error: {response['error']}")
                print("=" * 60 + "\n")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ {e}\n")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="MCP Analytics Platform")
    ap.add_argument("--query", type=str, help="Run a single query and exit")
    args = ap.parse_args()

    platform = MCPAnalyticsPlatform()
    if args.query:
        resp = platform.process_query(args.query)
        print(json.dumps(resp, indent=2, default=str))
    else:
        platform.interactive_mode()


if __name__ == "__main__":
    main()