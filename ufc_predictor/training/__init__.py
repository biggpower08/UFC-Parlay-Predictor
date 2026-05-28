__all__ = ["train", "retrain_model"]


def __getattr__(name):
    if name == "train":
        from ufc_predictor.training.train import train

        return train
    if name == "retrain_model":
        from ufc_predictor.training.retrain import retrain_model

        return retrain_model
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
