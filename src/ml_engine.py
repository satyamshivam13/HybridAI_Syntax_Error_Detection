import logging
import os
from typing import Any

import joblib
import numpy as np

from .feature_utils import extract_numerical_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = "models"
REQUIRED_SKLEARN_MAJOR_MINOR = "1.1"

model: Any = None
vectorizer: Any = None
label_encoder: Any = None
use_enhanced_features = False
model_loaded = False
model_error: str | None = None


class ModelUnavailableError(RuntimeError):
    """Raised when inference is requested but the ML model is unavailable."""


class ModelInferenceError(RuntimeError):
    """Raised when model inference fails after successful model load."""


def _load_model_bundle() -> None:
    global model
    global vectorizer
    global label_encoder
    global use_enhanced_features
    global model_loaded
    global model_error

    candidates = [
        {
            "vectorizer": "tfidf_vectorizer.pkl",
            "model": "syntax_error_model.pkl",
            "label_encoder": "label_encoder.pkl",
            "numerical_features": "numerical_features.pkl",
        },
        {
            "vectorizer": "tfidf.pkl",
            "model": "error_classifier.pkl",
            "label_encoder": "label_encoder.pkl",
            "numerical_features": None,
        },
    ]

    errors: list[str] = []
    for candidate in candidates:
        try:
            vectorizer = joblib.load(os.path.join(MODEL_DIR, candidate["vectorizer"]))
            model = joblib.load(os.path.join(MODEL_DIR, candidate["model"]))
            label_encoder = joblib.load(os.path.join(MODEL_DIR, candidate["label_encoder"]))
            if candidate["numerical_features"]:
                _ = joblib.load(os.path.join(MODEL_DIR, candidate["numerical_features"]))
                use_enhanced_features = True
            else:
                use_enhanced_features = False
            model_loaded = True
            model_error = None
            return
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{candidate['model']}: {exc}")

    model_loaded = False
    model_error = " | ".join(errors) if errors else "Unknown model loading failure"
    logger.error("ML model load failed: %s", model_error)


_load_model_bundle()


def is_model_available() -> bool:
    return model_loaded


def get_model_status() -> dict[str, Any]:
    status: dict[str, Any] = {"loaded": model_loaded, "error": model_error}
    try:
        import sklearn

        status["sklearn_version"] = sklearn.__version__
        status["expected_sklearn_major_minor"] = REQUIRED_SKLEARN_MAJOR_MINOR
        status["sklearn_compatible"] = sklearn.__version__.startswith(REQUIRED_SKLEARN_MAJOR_MINOR)
    except Exception as exc:  # noqa: BLE001
        status["sklearn_version"] = None
        status["expected_sklearn_major_minor"] = REQUIRED_SKLEARN_MAJOR_MINOR
        status["sklearn_compatible"] = False
        status["error"] = status["error"] or f"Unable to read scikit-learn version: {exc}"
    return status


def detect_error_ml(code: str):
    if not model_loaded:
        raise ModelUnavailableError(model_error or "ML model is unavailable")

    try:
        vec = vectorizer.transform([code])
        if use_enhanced_features:
            from scipy.sparse import hstack

            numerical = extract_numerical_features(code)
            numerical_array = np.array(numerical).reshape(1, -1)
            vec = hstack([vec, numerical_array])

        probs = model.predict_proba(vec)[0]
        max_prob = float(np.max(probs))
        pred_index = int(np.argmax(probs))
        pred_label = label_encoder.inverse_transform([pred_index])[0]
        return pred_label, max_prob
    except Exception as exc:  # noqa: BLE001
        raise ModelInferenceError(str(exc)) from exc

