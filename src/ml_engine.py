
import joblib
import numpy as np
import pandas as pd
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load optimized models
MODEL_DIR = "models"

# Flags for model state
model = None
vectorizer = None
label_encoder = None
use_enhanced_features = False
model_loaded = False

# Try loading models with robust error handling
try:
    vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
    model = joblib.load(os.path.join(MODEL_DIR, "syntax_error_model.pkl"))
    label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
    model_loaded = True
    
    try:
        numerical_features = joblib.load(os.path.join(MODEL_DIR, "numerical_features.pkl"))
        use_enhanced_features = True
    except (FileNotFoundError, ImportError, Exception) as e:
        logger.warning(f"Could not load numerical features: {e}")
        use_enhanced_features = False
        
except (FileNotFoundError, ModuleNotFoundError, ImportError) as e:
    # Try fallback to old model files
    try:
        vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf.pkl"))
        model = joblib.load(os.path.join(MODEL_DIR, "error_classifier.pkl"))
        label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
        model_loaded = True
        use_enhanced_features = False
    except Exception as fallback_e:
        logger.warning(f"⚠️  Warning: Could not load ML models. Error: {e}")
        model_loaded = False


def extract_numerical_features(code: str):
    """Extract numerical features for enhanced model"""
    features = []
    
    # Feature 1: Code length
    features.append(len(code))
    
    # Feature 2: Number of lines
    features.append(code.count('\n') + 1)
    
    # Feature 3: Has division operator
    features.append(1 if ('/' in code or '%' in code) else 0)
    
    # Feature 4: Has type conversion
    has_conv = any(kw in code for kw in ['int(', 'float(', 'str(', 'stoi', 'static_cast'])
    features.append(1 if has_conv else 0)
    
    # Feature 5: Missing colon (estimate)
    has_keywords = any(kw in code for kw in ['def ', 'class ', 'if ', 'for ', 'while '])
    colon_count = code.count(':')
    newline_count = code.count('\n')
    features.append(1 if (has_keywords and colon_count < newline_count) else 0)
    
    # Feature 6: Missing semicolon (estimate)
    semicolon_count = code.count(';')
    features.append(1 if (semicolon_count < newline_count - 1) else 0)
    
    # Feature 7: Has comparison with zero
    has_zero_comp = any(pattern in code for pattern in ['== 0', '!= 0', '> 0', '< 0', '>= 0', '<= 0'])
    features.append(1 if has_zero_comp else 0)
    
    # Feature 8: Has string operations
    features.append(1 if ('"' in code or "'" in code) else 0)
    
    # Feature 9: Has type declaration
    has_type = any(t in code for t in ['int ', 'float ', 'double ', 'char ', 'String ', 'bool'])
    features.append(1 if has_type else 0)
    
    # Feature 10: Bracket count difference
    bracket_diff = abs(code.count('(') - code.count(')')) + \
                   abs(code.count('[') - code.count(']')) + \
                   abs(code.count('{') - code.count('}'))
    features.append(bracket_diff)
    
    return features


def detect_error_ml(code: str):
    # Return default if model not available
    if not model_loaded:
        return "NoError", 0.0
    
    try:
        # TF-IDF vectorization
        vec = vectorizer.transform([code])
        
        # Add numerical features if using enhanced model
        if use_enhanced_features:
            try:
                from scipy.sparse import hstack
                numerical = extract_numerical_features(code)
                numerical_array = np.array(numerical).reshape(1, -1)
                vec = hstack([vec, numerical_array])
            except Exception as e:
                logger.warning(f"Feature extraction warning: {e}")
                pass
        
        # Prediction
        probs = model.predict_proba(vec)[0]
        max_prob = float(np.max(probs))
        pred_index = int(np.argmax(probs))
        pred_label = label_encoder.inverse_transform([pred_index])[0]

        return pred_label, max_prob
    
    except Exception as e:
        return "NoError", 0.0

