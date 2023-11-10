from abc import ABC, abstractmethod
from fs_lite.feature import Feature
from typing import Generic, TypeVar

T = TypeVar('T')

class FeatureStore(ABC, Generic[T]):

    @abstractmethod
    def compute(self, input: T, features: list[Feature[T]]) -> T:
        pass
