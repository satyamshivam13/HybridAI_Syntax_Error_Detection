"""
Model Optimization Script
Goal: Push accuracy from 83% → 90%+
Strategy: Better feature engineering + hyperparameter tuning
"""
import pandas as pd
import numpy as np
import random

# Set random seeds for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

def create_enhanced_features(df):
    """Create enhanced features beyond just code text"""
    
    # Ensure buggy_code column exists (handle both 'code' and 'buggy_code' columns)
    if 'code' in df.columns and 'buggy_code' not in df.columns:
        df['buggy_code'] = df['code']
    elif 'buggy_code' not in df.columns:
        raise ValueError("Dataset must have either 'code' or 'buggy_code' column")
    
    # Clean buggy_code column
    df['buggy_code'] = df['buggy_code'].fillna('').astype(str)
    
    # Feature 1: Code length
    df['code_length'] = df['buggy_code'].apply(len)
    
    # Feature 2: Number of lines
    df['num_lines'] = df['buggy_code'].apply(lambda x: x.count('\n') + 1)
    
    # Feature 3: Has division operator
    df['has_division'] = df['buggy_code'].apply(lambda x: '/' in x or '%' in x).astype(int)
    
    # Feature 4: Has type conversion
    df['has_type_conv'] = df['buggy_code'].apply(
        lambda x: any(kw in x for kw in ['int(', 'float(', 'str(', 'stoi', 'static_cast'])
    ).astype(int)
    
    # Feature 5: Missing colon (Python)
    df['missing_colon'] = df.apply(
        lambda row: 1 if row['language'] == 'Python' and any(kw in row['buggy_code'] 
                        for kw in ['def ', 'class ', 'if ', 'for ', 'while ']) 
                        and row['buggy_code'].count(':') < row['buggy_code'].count('\n') 
        else 0, axis=1
    )
    
    # Feature 6: Missing semicolon (Java/C/C++)
    df['missing_semicolon'] = df.apply(
        lambda row: 1 if row['language'] in ['Java', 'C', 'C++'] 
                        and row['buggy_code'].count(';') < (row['buggy_code'].count('\n') - 1)
        else 0, axis=1
    )
    
    # Feature 7: Has comparison with zero
    df['compares_zero'] = df['buggy_code'].apply(
        lambda x: any(pattern in x for pattern in ['== 0', '!= 0', '> 0', '< 0', '>= 0', '<= 0'])
    ).astype(int)
    
    # Feature 8: Has string operations
    df['has_string_ops'] = df['buggy_code'].apply(
        lambda x: '"' in x or "'" in x
    ).astype(int)
    
    # Feature 9: Has type declaration
    df['has_type_decl'] = df['buggy_code'].apply(
        lambda x: any(t in x for t in ['int ', 'float ', 'double ', 'char ', 'String ', 'bool'])
    ).astype(int)
    
    # Feature 10: Bracket count difference
    df['bracket_diff'] = df['buggy_code'].apply(
        lambda x: abs(x.count('(') - x.count(')')) + 
                  abs(x.count('[') - x.count(']')) + 
                  abs(x.count('{') - x.count('}'))
    )
    
    return df


def train_optimized_model(X_train, y_train, X_test, y_test):
    """Try multiple algorithms and find the best one"""
    
    print("Testing multiple algorithms...")
    print("="*60)
    
    models = {
        'Logistic Regression (Default)': LogisticRegression(max_iter=1000, random_state=42),
        'Logistic Regression (Tuned)': LogisticRegression(
            max_iter=2000, 
            C=0.5,  # Regularization
            solver='saga',
            class_weight='balanced',
            random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=200,
            max_depth=50,
            min_samples_split=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=7,
            random_state=42
        )
    }
    
    best_model = None
    best_accuracy = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy*100:.2f}%")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
    
    print(f"\n{'='*60}")
    print(f"🏆 Best Model: {best_name}")
    print(f"🎯 Best Accuracy: {best_accuracy*100:.2f}%")
    print("="*60)
    
    return best_model, best_name


def main():
    print("="*60)
    print("MODEL OPTIMIZATION PIPELINE")
    print("="*60)
    
    # Load dataset
    df = pd.read_csv("dataset/merged/all_errors.csv")
    print(f"\n✅ Dataset loaded: {len(df)} samples")
    
    # Create enhanced features
    print("\n📊 Creating enhanced features...")
    df = create_enhanced_features(df)
    
    # Prepare features
    X_text = df['buggy_code']
    X_lang = df['language']
    X_numerical = df[['code_length', 'num_lines', 'has_division', 'has_type_conv',
                      'missing_colon', 'missing_semicolon', 'compares_zero',
                      'has_string_ops', 'has_type_decl', 'bracket_diff']]
    y = df['error_type']
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data
    X_text_train, X_text_test, X_lang_train, X_lang_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
        X_text, X_lang, X_numerical, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training samples: {len(X_text_train)}")
    print(f"Testing samples: {len(X_text_test)}")
    
    # Enhanced TF-IDF with better parameters
    print("\n🔧 Vectorizing with enhanced TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=8000,  # Increased from 5000
        ngram_range=(1, 3),  # Include trigrams
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,  # Use logarithmic scaling
        analyzer='char',  # Character-level for better syntax pattern capture
        strip_accents='unicode'
    )
    
    X_text_train_vec = vectorizer.fit_transform(X_text_train)
    X_text_test_vec = vectorizer.transform(X_text_test)
    
    # Combine text features with numerical features
    from scipy.sparse import hstack
    X_train_combined = hstack([X_text_train_vec, X_num_train.values])
    X_test_combined = hstack([X_text_test_vec, X_num_test.values])
    
    print(f"Feature dimensions: {X_train_combined.shape[1]}")
    
    # Train optimized model
    best_model, best_name = train_optimized_model(X_train_combined, y_train, X_test_combined, y_test)
    
    # Generate detailed report
    print("\n" + "="*60)
    print("DETAILED PERFORMANCE REPORT")
    print("="*60)
    
    y_pred = best_model.predict(X_test_combined)
    
    print("\n📊 Classification Report:\n")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0))
    
    # Per-language accuracy
    print("\n🌍 Per-Language Accuracy:")
    print("-"*60)
    for lang in df['language'].unique():
        lang_mask = X_lang_test == lang
        if lang_mask.sum() > 0:
            lang_accuracy = accuracy_score(y_test[lang_mask], y_pred[lang_mask])
            print(f"{lang}: {lang_accuracy*100:.2f}%")
    
    # Calculate final accuracy
    final_accuracy = accuracy_score(y_test, y_pred)
    
    # Validate model quality before saving
    ACCURACY_THRESHOLD = 0.95
    print(f"\n🔍 Model Validation:")
    print(f"   Accuracy: {final_accuracy*100:.2f}%")
    print(f"   Threshold: {ACCURACY_THRESHOLD*100:.2f}%")
    
    if final_accuracy < ACCURACY_THRESHOLD:
        print(f"\n⚠️  WARNING: Accuracy {final_accuracy*100:.2f}% below threshold!")
        print(f"   Saving as FAILED model for debugging...")
        joblib.dump(best_model, 'models/FAILED_model_debug.pkl')
        joblib.dump(vectorizer, 'models/FAILED_vectorizer_debug.pkl')
        print(f"   Debug models saved. Review training data and hyperparameters.")
    else:
        # Save models
        print(f"\n✅ Model meets quality threshold - saving...")
        joblib.dump(best_model, 'models/syntax_error_model.pkl')
        joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
        joblib.dump(label_encoder, 'models/label_encoder.pkl')
        
        # Save numerical feature names for future use
        joblib.dump(X_numerical.columns.tolist(), 'models/numerical_features.pkl')
        
        print(f"💾 Models saved to /models directory")
    
    print(f"\n✅ Optimization complete!")
    print(f"🎯 Final Accuracy: {final_accuracy*100:.2f}%")
    print(f"🏆 Model: {best_name}")
    
    # Save results
    results_df = pd.DataFrame({
        'language': X_lang_test,
        'actual': label_encoder.inverse_transform(y_test),
        'predicted': label_encoder.inverse_transform(y_pred)
    })
    results_df.to_csv('results/optimized_results.csv', index=False)
    print(f"📊 Results saved to results/optimized_results.csv")


if __name__ == "__main__":
    main()
