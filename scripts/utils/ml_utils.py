"""
ML Utilities
Shared routines for loading ML models and vectors.
"""

import os
import joblib

def load_model_bundle(models_dir: str):
    """
    Load the trained model, vectorizer, and label encoder from the given directory.
    Returns:
        tuple: (model, vectorizer, label_encoder, error_message)
    """
    try:
        model = joblib.load(os.path.join(models_dir, "syntax_error_model.pkl"))
        vectorizer = joblib.load(os.path.join(models_dir, "tfidf_vectorizer.pkl"))
        label_encoder = joblib.load(os.path.join(models_dir, "label_encoder.pkl"))
        return model, vectorizer, label_encoder, None
    except Exception as exc:  # noqa: BLE001
        return None, None, None, f"Model bundle unavailable: {exc}"
