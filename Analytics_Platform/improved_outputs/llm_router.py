"""
Enhanced LLM Router - Handles VAGUE queries with intelligent prompting
Uses better prompts + fallback strategies
"""
import json
import re
import subprocess
import platform
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

class ExecutionPlan(BaseModel):
    """Validated execution plan"""
    dataset: str
    metric: str
    aggregation: str = "sum"
    filters: Dict[str, Any] = Field(default_factory=dict)
    group_by: Optional[str] = None
    
    @validator('dataset')
    def validate_dataset(cls, v):
        valid = ['loan', 'payment', 'customer']
        if v not in valid:
            raise ValueError(f"Dataset must be one of {valid}")
        return v

class EnhancedLLMRouter:
    """Enhanced router that handles vague/ambiguous queries"""
    
    def __init__(self, use_local: bool = True):
        self.use_local = use_local
        if use_local:
            self._init_local_model()
        
        # Synonym mappings for vague terms
        self.synonyms = {
            'loan': ['lending', 'credit', 'advance', 'borrowing'],
            'deposit': ['savings', 'fixed deposit', 'fd', 'investment'],
            'payment': ['transaction', 'transfer', 'pay'],
            'customer': ['user', 'client', 'account holder', 'member'],
            'gold loan': ['gl', 'gold lending', 'gold credit'],
            'home loan': ['hl', 'housing loan', 'mortgage'],
            'personal loan': ['pl', 'personal credit'],
            'upi': ['unified payment', 'digital payment'],
            'card': ['credit card', 'debit card', 'card transaction'],
            'wallet': ['digital wallet', 'e-wallet', 'mobile wallet'],
            'branch': ['location', 'office', 'city', 'region', 'place', 'area'],
            'highest': ['maximum', 'max', 'top', 'best', 'most', 'largest'],
            'lowest': ['minimum', 'min', 'bottom', 'worst', 'least', 'smallest'],
            'growth': ['increase', 'rise', 'expansion', 'growing'],
            'trend': ['pattern', 'timeline', 'over time', 'progression']
        }
    
    def _init_local_model(self):
        """Initialize local model - Windows compatible"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['where', 'ollama'], capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.backend = 'ollama'
                print("✅ Using Ollama with enhanced prompts")
            else:
                self.backend = 'fallback'
                print("⚠️ Ollama not found, using enhanced fallback")
        except Exception as e:
            self.backend = 'fallback'
            print(f"⚠️ Using enhanced fallback")
    
    def query_to_plan(self, user_query: str) -> Dict[str, Any]:
        """Convert query to plan with enhanced understanding"""
        
        # Step 1: Normalize the query
        normalized_query = self._normalize_query(user_query)
        
        # Step 2: Try LLM with enhanced prompt
        try:
            if self.backend == 'ollama':
                plan = self._query_ollama_enhanced(normalized_query)
                if plan and isinstance(plan, dict):
                    validated = ExecutionPlan(**plan)
                    return validated.dict()
        except Exception as e:
            print(f"⚠️ LLM failed: {e}, using enhanced fallback")
        
        # Step 3: Use enhanced fallback
        return self._enhanced_fallback(normalized_query, user_query)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by expanding synonyms"""
        normalized = query.lower()
        
        # Expand synonyms
        for main_term, synonyms in self.synonyms.items():
            for syn in synonyms:
                if syn in normalized:
                    normalized = normalized.replace(syn, main_term)
        
        return normalized
    
    def _query_ollama_enhanced(self, query: str) -> Optional[Dict]:
        """Query Ollama with MUCH BETTER prompt"""
        
        prompt = f"""You are a banking data analyst. Convert this user query into a structured JSON plan.

USER QUERY: "{query}"

AVAILABLE DATA:
Datasets: loan, payment, customer

Loan metrics: gold_loan_amt, home_loan_amt, personal_loan_amt, fd_deposit_amt, casa_balance, npa_percent
Payment metrics: upi_volume, upi_value, card_txn_volume, card_txn_value, wallet_txn_volume, wallet_txn_value, fraud_rate_percent  
Customer metrics: new_customers, active_customers, avg_credit_score, loan_default_rate_percent, customer_churn_rate_percent

Branches: Mumbai, Delhi, Pune, Bangalore, Chennai, Kolkata, Hyderabad, Ahmedabad, Jaipur, Surat

RULES:
1. If query is vague (e.g., "show me loans"), default to gold_loan_amt
2. If query mentions "total" or "all", use sum aggregation
3. If query mentions "average", use mean aggregation
4. If query mentions "growth", "trend", "increase", use growth aggregation
5. If query mentions "over time", "timeline", "trend", add group_by: "date"
6. If query mentions a city name, add to filters
7. If query is about comparison, focus on most relevant single metric

RESPOND WITH ONLY THIS JSON STRUCTURE:
{{
  "dataset": "loan|payment|customer",
  "metric": "exact_column_name",
  "aggregation": "sum|mean|growth",
  "filters": {{}},
  "group_by": "date|null"
}}

JSON OUTPUT:"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', 'mistral', prompt],
                capture_output=True,
                text=True,
                timeout=30,
                shell=(platform.system() == 'Windows')
            )
            
            if result.returncode == 0:
                return self._extract_json(result.stdout)
        except:
            pass
        
        return None
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text"""
        try:
            return json.loads(text)
        except:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        return None
    
    def _enhanced_fallback(self, normalized_query: str, original_query: str) -> Dict[str, Any]:
        """ENHANCED fallback with intelligent defaults"""
        q = normalized_query
        orig = original_query.lower()
        
        plan = {
            'filters': {},
            'group_by': None,
            'aggregation': 'sum'
        }
        
        # === STEP 1: Determine Dataset ===
        dataset_scores = {'loan': 0, 'payment': 0, 'customer': 0}
        
        # Score based on keywords
        loan_keywords = ['loan', 'lending', 'credit', 'borrow', 'gold', 'home', 'personal', 'deposit', 'fd', 'casa', 'npa']
        payment_keywords = ['payment', 'transaction', 'upi', 'card', 'wallet', 'fraud', 'digital']
        customer_keywords = ['customer', 'user', 'client', 'churn', 'acquisition', 'credit score', 'default']
        
        for keyword in loan_keywords:
            if keyword in q:
                dataset_scores['loan'] += 1
        for keyword in payment_keywords:
            if keyword in q:
                dataset_scores['payment'] += 1
        for keyword in customer_keywords:
            if keyword in q:
                dataset_scores['customer'] += 1
        
        # If vague, default to loan
        if max(dataset_scores.values()) == 0:
            plan['dataset'] = 'loan'
        else:
            plan['dataset'] = max(dataset_scores, key=dataset_scores.get)
        
        # === STEP 2: Determine Metric ===
        metric_mapping = {
            # Loan dataset
            'loan': {
                'gold': 'gold_loan_amt',
                'home': 'home_loan_amt',
                'personal': 'personal_loan_amt',
                'deposit': 'fd_deposit_amt',
                'fd': 'fd_deposit_amt',
                'casa': 'casa_balance',
                'npa': 'npa_percent',
                'default': 'gold_loan_amt'  # Default for vague queries
            },
            # Payment dataset
            'payment': {
                'upi': 'upi_volume',
                'card': 'card_txn_volume',
                'wallet': 'wallet_txn_volume',
                'fraud': 'fraud_rate_percent',
                'default': 'upi_volume'
            },
            # Customer dataset
            'customer': {
                'new': 'new_customers',
                'active': 'active_customers',
                'credit': 'avg_credit_score',
                'default': 'active_customers',
                'churn': 'customer_churn_rate_percent',
                'acquisition': 'new_customers'
            }
        }
        
        dataset = plan['dataset']
        metric_found = False
        
        for keyword, metric in metric_mapping[dataset].items():
            if keyword != 'default' and keyword in q:
                plan['metric'] = metric
                metric_found = True
                break
        
        if not metric_found:
            plan['metric'] = metric_mapping[dataset]['default']
        
        # === STEP 3: Determine Aggregation ===
        if any(word in q for word in ['growth', 'increase', 'rise', 'expansion', 'growing']):
            plan['aggregation'] = 'growth'
        elif any(word in q for word in ['average', 'mean', 'avg']):
            plan['aggregation'] = 'mean'
        elif 'percent' in plan['metric'] or 'rate' in plan['metric'] or 'score' in plan['metric']:
            plan['aggregation'] = 'mean'
        
        # === STEP 4: Detect Grouping ===
        if any(word in q for word in ['trend', 'over time', 'timeline', 'monthly', 'daily', 'time series', 'pattern', 'progression']):
            plan['group_by'] = 'date'
        
        # === STEP 5: Extract Filters ===
        branches = ['mumbai', 'delhi', 'pune', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'ahmedabad', 'jaipur', 'surat']
        for branch in branches:
            if branch in q:
                plan['filters']['branch'] = branch.capitalize()
                break
        
        # Validate
        try:
            validated = ExecutionPlan(**plan)
            return validated.dict()
        except Exception as e:
            print(f"⚠️ Validation failed: {e}, returning safe default")
            return {
                'dataset': 'loan',
                'metric': 'gold_loan_amt',
                'aggregation': 'sum',
                'filters': {},
                'group_by': None
            }