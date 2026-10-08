from abc import ABC, abstractmethod

class AIModule(ABC):

    @abstractmethod
    def _extract_ml_feature(self):
        pass

    @abstractmethod
    def _predict_with_lgb(self, feature_vector):
        pass