import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from ml_pipeline import train_model

def test_train_model():
    assert train_model() is not None