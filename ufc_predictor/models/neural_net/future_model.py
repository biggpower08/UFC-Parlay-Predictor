"""
Placeholder for future neural network predictor.
Architecture scaffold only — no training implementation yet.
"""


class FutureFightModel:
    """Neural net predictor (to be implemented)."""

    def __init__(self):
        self.model = None

    def train(self, X, y, **kwargs):
        """Train on feature matrix X and labels y."""
        raise NotImplementedError("Neural net training not implemented yet.")

    def predict(self, X):
        """Return win probabilities for fighter A."""
        raise NotImplementedError("Neural net predict not implemented yet.")

    def save(self, path):
        """Persist model weights to disk."""
        raise NotImplementedError("Neural net save not implemented yet.")

    def load(self, path):
        """Load model weights from disk."""
        raise NotImplementedError("Neural net load not implemented yet.")
