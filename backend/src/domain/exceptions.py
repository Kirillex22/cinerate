from typing import Optional


class ModelException(Exception):
    pass


class TransformToSeasonException(ModelException):
    code = "NOT_FOUND"

    def __init__(self, season: Optional[int]):
        super().__init__(f"Cannot transform season to film cause of season={season}")
