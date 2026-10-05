from abc import ABC, abstractmethod

class LifeCycleBehavior(ABC):

    @abstractmethod
    def update_twf(self):
        self.is_machine_failure()

    @abstractmethod
    def update_hdf(self):
        self.is_machine_failure()

    @abstractmethod
    def update_pwf(self):
        self.is_machine_failure()

    @abstractmethod
    def update_osf(self):
        self.is_machine_failure()

    @abstractmethod
    def update_rnf(self):
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