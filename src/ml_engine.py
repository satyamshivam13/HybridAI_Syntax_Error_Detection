
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


from .feature_utils import extract_numerical_features



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

