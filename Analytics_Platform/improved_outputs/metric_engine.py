
"""
Metric Engine - Complete catalog matching YOUR actual data columns
All 3 datasets with all metrics
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, Optional

class MetricEngine:
    """Manages metric catalog and semantic matching"""
    
    def __init__(self):
        print("🔧 Loading embedding model...")
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.metrics_catalog = self._build_metrics_catalog()
            self.metric_embeddings = self._compute_embeddings()
            print(f"✅ Loaded {len(self.metrics_catalog)} metrics")
        except Exception as e:
            print(f"⚠️ Error loading embedding model: {e}")
            self.model = None
            self.metrics_catalog = {}
            self.metric_embeddings = {}
    
    def _build_metrics_catalog(self) -> Dict[str, Dict]:
        """Build complete catalog with ALL your columns"""
        return {
            # ===== LOAN DATASET =====
            # Gold Loan
            "loan_gold_total": {
                "dataset": "loan",
                "column": "gold_loan_amt",
                "aggregation": "sum",
                "description": "total gold loan amount disbursement volume lending"
            },
            "loan_gold_growth": {
                "dataset": "loan",
                "column": "gold_loan_amt",
                "aggregation": "growth",
                "description": "gold loan growth rate increase trend"
            },
            
            # Home Loan
            "loan_home_total": {
                "dataset": "loan",
                "column": "home_loan_amt",
                "aggregation": "sum",
                "description": "total home loan amount housing mortgage property"
            },
            "loan_home_growth": {
                "dataset": "loan",
                "column": "home_loan_amt",
                "aggregation": "growth",
                "description": "home loan growth rate housing mortgage increase"
            },
            
            # Personal Loan
            "loan_personal_total": {
                "dataset": "loan",
                "column": "personal_loan_amt",
                "aggregation": "sum",
                "description": "total personal loan amount unsecured lending"
            },
            "loan_personal_growth": {
                "dataset": "loan",
                "column": "personal_loan_amt",
                "aggregation": "growth",
                "description": "personal loan growth rate increase"
            },
            
            # FD Deposits
            "deposit_fd_total": {
                "dataset": "loan",
                "column": "fd_deposit_amt",
                "aggregation": "sum",
                "description": "total fixed deposit amount fd savings"
            },
            "deposit_fd_growth": {
                "dataset": "loan",
                "column": "fd_deposit_amt",
                "aggregation": "growth",
                "description": "fd deposit growth rate increase"
            },
            
            # CASA Balance
            "casa_balance_total": {
                "dataset": "loan",
                "column": "casa_balance",
                "aggregation": "sum",
                "description": "total casa balance current savings account"
            },
            "casa_balance_growth": {
                "dataset": "loan",
                "column": "casa_balance",
                "aggregation": "growth",
                "description": "casa balance growth rate increase"
            },
            
            # NPA Percent
            "npa_percent_avg": {
                "dataset": "loan",
                "column": "npa_percent",
                "aggregation": "mean",
                "description": "average npa percentage non performing assets bad loans"
            },
            
            # ===== PAYMENT DATASET =====
            # UPI Volume
            "payment_upi_volume": {
                "dataset": "payment",
                "column": "upi_volume",
                "aggregation": "sum",
                "description": "total upi transaction volume count digital payment"
            },
            "payment_upi_value": {
                "dataset": "payment",
                "column": "upi_value",
                "aggregation": "sum",
                "description": "total upi transaction value amount digital payment"
            },
            "payment_upi_growth": {
                "dataset": "payment",
                "column": "upi_volume",
                "aggregation": "growth",
                "description": "upi transaction growth rate increase"
            },
            
            # Card Transactions
            "payment_card_volume": {
                "dataset": "payment",
                "column": "card_txn_volume",
                "aggregation": "sum",
                "description": "total card transaction volume count credit debit"
            },
            "payment_card_value": {
                "dataset": "payment",
                "column": "card_txn_value",
                "aggregation": "sum",
                "description": "total card transaction value amount credit debit"
            },
            "payment_card_growth": {
                "dataset": "payment",
                "column": "card_txn_volume",
                "aggregation": "growth",
                "description": "card transaction growth rate increase"
            },
            
            # Wallet Transactions
            "payment_wallet_volume": {
                "dataset": "payment",
                "column": "wallet_txn_volume",
                "aggregation": "sum",
                "description": "total wallet transaction volume count digital wallet"
            },
            "payment_wallet_value": {
                "dataset": "payment",
                "column": "wallet_txn_value",
                "aggregation": "sum",
                "description": "total wallet transaction value amount digital wallet"
            },
            "payment_wallet_growth": {
                "dataset": "payment",
                "column": "wallet_txn_volume",
                "aggregation": "growth",
                "description": "wallet transaction growth rate increase"
            },
            
            # Fraud Rate
            "payment_fraud_rate": {
                "dataset": "payment",
                "column": "fraud_rate_percent",
                "aggregation": "mean",
                "description": "average fraud rate percentage suspicious transactions"
            },
            
            # ===== CUSTOMER DATASET =====
            # New Customers
            "customer_new_total": {
                "dataset": "customer",
                "column": "new_customers",
                "aggregation": "sum",
                "description": "total new customers acquisition onboarding"
            },
            "customer_new_growth": {
                "dataset": "customer",
                "column": "new_customers",
                "aggregation": "growth",
                "description": "new customer growth rate acquisition increase"
            },
            
            # Active Customers
            "customer_active_count": {
                "dataset": "customer",
                "column": "active_customers",
                "aggregation": "sum",
                "description": "total active customers user base count"
            },
            "customer_active_growth": {
                "dataset": "customer",
                "column": "active_customers",
                "aggregation": "growth",
                "description": "active customer growth rate user base expansion"
            },
            
            # Credit Score
            "customer_credit_avg": {
                "dataset": "customer",
                "column": "avg_credit_score",
                "aggregation": "mean",
                "description": "average credit score customer creditworthiness"
            },
            
            # Loan Default Rate
            "customer_default_rate": {
                "dataset": "customer",
                "column": "loan_default_rate_percent",
                "aggregation": "mean",
                "description": "average loan default rate percentage bad debt"
            },
            
            # Churn Rate
            "customer_churn_rate": {
                "dataset": "customer",
                "column": "customer_churn_rate_percent",
                "aggregation": "mean",
                "description": "average customer churn rate percentage attrition loss"
            }
        }
    
    def _compute_embeddings(self) -> Dict[str, np.ndarray]:
        """Precompute embeddings"""
        if self.model is None:
            return {}
        
        embeddings = {}
        for metric_name, metric_info in self.metrics_catalog.items():
            description = metric_info['description']
            embeddings[metric_name] = self.model.encode(description)
        return embeddings
    
    def find_best_metric(self, query: str, threshold: float = 0.4) -> Dict:
        """Find best matching metric"""
        if self.model is None or not self.metric_embeddings:
            return {
                'metric_name': None,
                'metric_info': None,
                'confidence': 0.0,
                'all_scores': {}
            }
        
        query_embedding = self.model.encode(query)
        
        similarities = {}
        for metric_name, metric_embedding in self.metric_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, metric_embedding)
            similarities[metric_name] = similarity
        
        best_metric = max(similarities, key=similarities.get)
        best_score = similarities[best_metric]
        
        if best_score < threshold:
            return {
                'metric_name': None,
                'metric_info': None,
                'confidence': best_score,
                'all_scores': similarities
            }
        
        return {
            'metric_name': best_metric,
            'metric_info': self.metrics_catalog[best_metric],
            'confidence': best_score,
            'all_scores': similarities
        }
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))