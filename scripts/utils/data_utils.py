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


def create_enhanced_features(df):
    """
    Create enhanced features beyond just code text
    
    Args:
        df: DataFrame with 'buggy_code' column
        
    Returns:
        pd.DataFrame: DataFrame with additional feature columns
    """
    # Ensure buggy_code column exists
    if 'buggy_code' not in df.columns:
        if 'code' in df.columns:
            df['buggy_code'] = df['code']
        else:
            raise ValueError("Dataset must have either 'code' or 'buggy_code' column")
    
    # Clean buggy_code column
    df['buggy_code'] = df['buggy_code'].fillna('').astype(str)
    
    # Length features
    df['code_length'] = df['buggy_code'].str.len()
    df['num_lines'] = df['buggy_code'].str.count('\n') + 1
    
    # Character-level features
    df['num_brackets'] = df['buggy_code'].str.count(r'[\[\](){}<>]')
    df['num_quotes'] = df['buggy_code'].str.count(r'["\']')
    df['num_semicolons'] = df['buggy_code'].str.count(';')
    df['num_colons'] = df['buggy_code'].str.count(':')
    
    # Keyword density
    df['num_keywords'] = df['buggy_code'].str.count(
        r'\b(if|else|for|while|return|function|def|class|import|from)\b'
    )
    
    # Indentation consistency (for Python-like languages)
    df['has_tabs'] = df['buggy_code'].str.contains('\t').astype(int)
    df['has_spaces'] = df['buggy_code'].str.contains('    ').astype(int)
    
    return df


def save_augmented_data(new_df, original_path='dataset/merged/all_errors.csv', 
                        output_path=None, check_duplicates=True):
    """
    Save augmented data with optional deduplication
    
    Args:
        new_df: DataFrame with new samples to add
        original_path: Path to original dataset
        output_path: Path to save combined dataset (defaults to original_path)
        check_duplicates: If True, removes duplicate code samples
    """
    if output_path is None:
        output_path = original_path
    
    # Load existing data
    if os.path.exists(original_path):
        existing_df = pd.read_csv(original_path)
    else:
        existing_df = pd.DataFrame()
    
    # Deduplication
    if check_duplicates and not existing_df.empty:
        initial_count = len(new_df)
        existing_codes = set(existing_df['buggy_code'].values)
        new_df = new_df[~new_df['buggy_code'].isin(existing_codes)]
        removed = initial_count - len(new_df)
        if removed > 0:
            print(f"⚠️  Removed {removed} duplicate samples")
        print(f"✅ After deduplication: {len(new_df)} truly new samples")
    
    # Combine
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Save
    combined_df.to_csv(output_path, index=False)
    print(f"💾 Saved to {output_path}")
    print(f"   Total samples: {len(combined_df)}")
    
    return combined_df
