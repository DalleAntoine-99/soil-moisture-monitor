import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# ========= CONFIG =========
DATA_DIR = "ml/data/processed"
MODEL_DIR = "ml/models"
MODEL_PATH = os.path.join(MODEL_DIR, "ridge_regressor.joblib")

TEST_SIZE = 0.2
RANDOM_STATE = 42
RIDGE_ALPHA = 1.0  # régularisation (peut être ajustée plus tard)

os.makedirs(MODEL_DIR, exist_ok=True)

# ========= LOAD DATA =========
print("Loading features and labels...")
X = np.load(os.path.join(DATA_DIR, "features.npy"))
y = np.load(os.path.join(DATA_DIR, "labels.npy"))

print(f"Features shape: {X.shape}")
print(f"Labels shape: {y.shape}")

# ========= TRAIN / TEST SPLIT =========
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y  # important car labels issues de classes
)

print(f"Train size: {X_train.shape[0]}")
print(f"Test size: {X_test.shape[0]}")

# ========= TRAIN MODEL =========
print("Training Ridge Regressor...")
model = Ridge(alpha=RIDGE_ALPHA)
model.fit(X_train, y_train)

# ========= EVALUATION =========
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Evaluation results:")
print(f"MAE: {mae:.4f}")
print(f"R²:  {r2:.4f}")

# ========= SAVE MODEL =========
joblib.dump(model, MODEL_PATH)
print(f"Model saved to: {MODEL_PATH}")
