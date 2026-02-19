"""
Query Clarifier - Detects ambiguous queries and asks for clarification
NEW component to handle vague queries intelligently
"""
from typing import Dict, List, Optional

class QueryClarifier:
    """Detects ambiguous queries and suggests clarifications"""
    
    def __init__(self):
        self.ambiguous_patterns = {
            'loan': ['gold loan', 'home loan', 'personal loan'],
            'deposit': ['FD deposits', 'CASA balance'],
            'transaction': ['UPI', 'card', 'wallet'],
            'customer': ['new customers', 'active customers'],
            'rate': ['NPA rate', 'fraud rate', 'churn rate', 'default rate']
        }
    
    def is_ambiguous(self, query: str) -> bool:
        """Check if query is too vague"""
        q = query.lower()
        
        # Very short queries
        if len(q.split()) <= 2:
            return True
        
        # Contains ambiguous terms without specifics
        ambiguous_terms = ['show', 'give', 'tell', 'display', 'present', 'what', 'how', 'the']
        if any(term in q for term in ambiguous_terms) and not self._has_specific_metric(q):
            return True
        
        return False
    
    def _has_specific_metric(self, query: str) -> bool:
        """Check if query mentions a specific metric"""
        specific_metrics = [
            'gold loan', 'home loan', 'personal loan',
            'upi', 'card', 'wallet',
            'new customer', 'active customer',
            'npa', 'fraud', 'churn', 'credit score',
            'casa', 'fd', 'deposit'
        ]
        return any(metric in query for metric in specific_metrics)
    
    def get_suggestions(self, query: str) -> Dict[str, List[str]]:
        """Get clarification suggestions for ambiguous query"""
        q = query.lower()
        suggestions = {}
        
        # Check for vague terms
        if 'loan' in q and not any(x in q for x in ['gold', 'home', 'personal']):
            suggestions['Which type of loan?'] = [
                'Gold loan',
                'Home loan', 
                'Personal loan',
                'All loans combined'
            ]
        
        if any(word in q for word in ['transaction', 'payment']) and not any(x in q for x in ['upi', 'card', 'wallet']):
            suggestions['Which payment type?'] = [
                'UPI transactions',
                'Card transactions',
                'Wallet transactions',
                'All payment types'
            ]
        
        if 'customer' in q and not any(x in q for x in ['new', 'active']):
            suggestions['Which customer metric?'] = [
                'New customers',
                'Active customers',
                'Customer churn',
                'Credit score'
            ]
        
        if 'deposit' in q and not any(x in q for x in ['fd', 'casa', 'fixed']):
            suggestions['Which deposit type?'] = [
                'FD deposits',
                'CASA balance',
                'All deposits'
            ]
        
        # Check if action is vague
        if not any(word in q for word in ['highest', 'lowest', 'trend', 'growth', 'compare', 'total', 'average']):
            suggestions['What would you like to see?'] = [
                'Total amount',
                'Highest branch',
                'Trend over time',
                'Growth rate',
                'Compare all branches'
            ]
        
        return suggestions
    
    def auto_clarify(self, query: str) -> Optional[str]:
        """Attempt to auto-clarify vague query with defaults"""
        q = query.lower()
        clarified = query
        
        # Add defaults for vague terms
        if 'loan' in q and not any(x in q for x in ['gold', 'home', 'personal']):
            clarified = q.replace('loan', 'gold loan')
        
        if 'transaction' in q and not any(x in q for x in ['upi', 'card', 'wallet']):
            clarified = q.replace('transaction', 'upi transaction')
        
        if 'customer' in q and not any(x in q for x in ['new', 'active']):
            clarified = q.replace('customer', 'active customer')
        
        # Add action if missing
        if not any(word in q for word in ['highest', 'lowest', 'trend', 'total', 'compare']):
            clarified = 'total ' + clarified
        
        return clarified if clarified != query else None
    
    def format_clarification_prompt(self, suggestions: Dict[str, List[str]]) -> str:
        """Format suggestions as a user-friendly prompt"""
        lines = ["🤔 Your query seems ambiguous. Please clarify:\n"]
        
        for question, options in suggestions.items():
            lines.append(f"\n{question}")
            for i, option in enumerate(options, 1):
                lines.append(f"  {i}. {option}")
        
        lines.append("\n💡 Or rephrase your query with more details!")
        return "\n".join(lines)