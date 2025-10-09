def merge_dicts(*models) -> dict:
    return {k: v for model in models for k, v in model.dict().items()}
