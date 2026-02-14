"""
Test rapide MAPIE avec données synthétiques
"""
import numpy as np
from sklearn.linear_model import Ridge
from mapie.regression import MapieRegressor

print("🧪 Testing MAPIE configuration...")

# Données synthétiques
np.random.seed(42)
X_train = np.random.randn(100, 10)
y_train = np.random.randn(100) * 20 + 50

X_test = np.random.randn(10, 10)

print(f"✓ Train: {X_train.shape}")
print(f"✓ Test:  {X_test.shape}")

# Test 1: MAPIE avec cv=5 (cross-validation interne)
print("\n🔮 Test 1: MAPIE with cv=5...")
try:
    mapie1 = MapieRegressor(
        estimator=Ridge(alpha=1.0, random_state=42),
        method="base",
        cv=5,
        random_state=42
    )
    mapie1.fit(X_train, y_train)
    print("✓ MAPIE fit OK")
    
    y_pred1, y_intervals1 = mapie1.predict(X_test, alpha=0.05)
    print(f"✓ Predictions shape: {y_pred1.shape}")
    print(f"✓ Intervals shape: {y_intervals1.shape}")
    print("✅ SUCCESS: cv=5 works!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 2: MAPIE avec cv=None (split simple)
print("\n🔮 Test 2: MAPIE with cv=None...")
try:
    mapie2 = MapieRegressor(
        estimator=Ridge(alpha=1.0, random_state=42),
        method="base",
        cv=None,
        random_state=42
    )
    mapie2.fit(X_train, y_train)
    print("✓ MAPIE fit OK")
    
    y_pred2, y_intervals2 = mapie2.predict(X_test, alpha=0.05)
    print(f"✓ Predictions shape: {y_pred2.shape}")
    print(f"✓ Intervals shape: {y_intervals2.shape}")
    print("✅ SUCCESS: cv=None works!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 3: MAPIE naive avec cv=5
print("\n🔮 Test 3: MAPIE naive with cv=5...")
try:
    mapie3 = MapieRegressor(
        estimator=Ridge(alpha=1.0, random_state=42),
        method="naive",
        cv=5,
        random_state=42
    )
    mapie3.fit(X_train, y_train)
    print("✓ MAPIE fit OK")
    
    y_pred3, y_intervals3 = mapie3.predict(X_test, alpha=0.05)
    print(f"✓ Predictions shape: {y_pred3.shape}")
    print(f"✓ Intervals shape: {y_intervals3.shape}")
    print("✅ SUCCESS: naive + cv=5 works!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "="*60)
print("RECOMMENDATION: Use the first working method above")
print("="*60)
