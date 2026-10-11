from abc import ABC, abstractmethod

from src.simulation.state.OperationState import OperationState

class LifeCycleBehavior(ABC):

    @abstractmethod
    def update_twf(self) -> OperationState:
        self.is_machine_failure()

    @abstractmethod
    def update_hdf(self) -> OperationState:
        self.is_machine_failure()

    @abstractmethod
    def update_pwf(self) -> OperationState:
        self.is_machine_failure()

    @abstractmethod
    def update_osf(self) -> OperationState:
        self.is_machine_failure()

    @abstractmethod
    def update_rnf(self) -> OperationState:
        self.is_machine_failure()

    @abstractmethod
    def is_machine_failure(self) -> bool:
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass