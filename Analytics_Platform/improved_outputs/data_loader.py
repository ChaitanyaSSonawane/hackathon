
"""
Data Loader - Handles loading data from various sources
Supports CSV with caching for better performance
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import hashlib
import pickle

class DataLoader:
    """Loads and caches datasets"""
    
    def __init__(self, data_dir: str = "data", cache_dir: str = ".cache"):
        """Initialize data loader"""
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = {}
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all available datasets"""
        datasets = {}
        
        dataset_files = {
            'loan': 'loan_deposit_performance.csv',
            'payment': 'digital_payments_data.csv',
            'customer': 'customer_credit_data.csv'
        }
        
        for name, filename in dataset_files.items():
            try:
                df = self.load_csv(filename)
                if df is not None:
                    datasets[name] = df
                    print(f"✅ Loaded {name}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"⚠️ Failed to load {name}: {e}")
        
        return datasets
    
    def load_csv(self, filename: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Load CSV file with caching"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"⚠️ File not found: {filepath}")
            return None
        
        if use_cache:
            cache_key = self._get_cache_key(filepath)
            cached_df = self._load_from_cache(cache_key)
            if cached_df is not None:
                return cached_df
        
        try:
            df = pd.read_csv(filepath)
            df = self._preprocess_dataframe(df)
            
            if use_cache:
                self._save_to_cache(cache_key, df)
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return None
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic preprocessing"""
        # Convert date columns
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
        
        # Handle missing values in numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        return df
    
    def _get_cache_key(self, filepath: Path) -> str:
        """Generate cache key"""
        stat = filepath.stat()
        key_str = f"{filepath}_{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Load from cache"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, df: pd.DataFrame):
        """Save to cache"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")