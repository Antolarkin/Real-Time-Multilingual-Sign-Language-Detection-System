import numpy as np

class GestureFeatureExtractor:
    """
    Simplified feature extractor (Reverted).
    Legacy models now use internal landmark processing.
    """
    def __init__(self):
        pass

    def extract_features(self, landmarks):
        return None

    def reset(self):
        pass

LOCAL_FEATURE_DIM = 40
GLOBAL_FEATURE_DIM = 4
GES_FEATURE_DIM = 1
