import os
import pickle
from typing import List, Tuple

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB


def get_training_data() -> Tuple[np.ndarray, np.ndarray]:
    X_train = np.array([
        [95, 95, 95],
        [90, 95, 90],
        [95, 90, 95],
        [85, 90, 85],
        [80, 85, 80],
        [85, 80, 85],
        [75, 80, 75],
        [75, 80, 75],
        [70, 75, 70],
        [75, 70, 75],
        [65, 70, 65],
        [60, 65, 60],
        [70, 60, 70],
        [55, 60, 55],
        [50, 55, 50],
        [45, 50, 45],
        [40, 45, 40],
        [35, 40, 35],
        [30, 35, 30],
        [25, 30, 25],
        [20, 25, 20],
        [15, 20, 15],
        [10, 15, 10],
        [5, 10, 5],
        [1, 5, 1],
    ])
    y_train = np.array([
        95, 92, 93,
        87, 82, 83,
        77, 75,
        72, 73, 67,
        62, 67,
        57, 52, 47,
        42, 37, 32,
        27, 22, 17,
        12, 7, 2,
    ])
    return X_train, y_train


def evaluate_current_numeric_model(X: np.ndarray, y_numeric: np.ndarray) -> float:
    """Load the saved GaussianNB model (trained with numeric targets as classes)
    and compute training accuracy on X against the original numeric labels.
    """
    model_path = os.path.join("output", "naive_bayes_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please run build_model.py first.")

    with open(model_path, "rb") as f:
        model: GaussianNB = pickle.load(f)

    y_pred = model.predict(X)
    acc = accuracy_score(y_numeric, y_pred)
    return acc


def evaluate_pass_fail_classification(X: np.ndarray, y_numeric: np.ndarray) -> Tuple[float, float]:
    """Train a GaussianNB on pass/fail labels (>=75 pass) and return
    (train_accuracy, test_accuracy) using a 70/30 split.
    """
    y_class = np.where(y_numeric >= 75, "Lulus", "Tidak Lulus")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_class, test_size=0.3, random_state=42, stratify=y_class
    )

    clf = GaussianNB()
    clf.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, clf.predict(X_train))
    test_acc = accuracy_score(y_test, clf.predict(X_test))
    return train_acc, test_acc


if __name__ == "__main__":
    X, y = get_training_data()

    try:
        acc_numeric = evaluate_current_numeric_model(X, y)
        print(f"Akurasi (model saat ini, target numerik sebagai kelas) - data latih: {acc_numeric:.4f}")
    except FileNotFoundError as e:
        print(str(e))

    train_acc, test_acc = evaluate_pass_fail_classification(X, y)
    print(f"Akurasi klasifikasi Lulus/Tidak Lulus - train: {train_acc:.4f}, test: {test_acc:.4f}")


