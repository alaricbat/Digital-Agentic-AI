from abc import ABC, abstractmethod

class LifeCycleBehavior(ABC):

    @abstractmethod
    def update_twf(self):
        self.is_machine_failure(self)

    @abstractmethod
    def is_machine_failure(self) -> bool:
        pass