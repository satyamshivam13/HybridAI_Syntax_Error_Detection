"""
Data Utilities for Model Training and Evaluation
Shared functions to eliminate code duplication across scripts
"""

import pandas as pd
import os


def load_dataset(path='dataset/merged/all_errors.csv'):
    """
    Load dataset with validation and automatic column handling
    
    Args:
        path: Path to the CSV dataset
        
    Returns:
        pd.DataFrame: Validated dataset with standardized columns
        
    Raises:
        FileNotFoundError: If dataset doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")
    
    df = pd.read_csv(path)
    
    # Handle column name flexibility (code vs buggy_code)
    if 'code' in df.columns and 'buggy_code' not in df.columns:
        df['buggy_code'] = df['code']
    
    # Validate required columns
    required = ['buggy_code', 'error_type', 'language']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Clean data
    df['buggy_code'] = df['buggy_code'].fillna('').astype(str)
    df['error_type'] = df['error_type'].fillna('Unknown').astype(str)
    df['language'] = df['language'].fillna('Unknown').astype(str)
    
    print(f"✅ Dataset loaded: {len(df)} samples")
    print(f"   Languages: {df['language'].unique().tolist()}")
    print(f"   Error types: {df['error_type'].nunique()}")
    
    return df



