from src.simulation.state.FailureMode import FailureMode
from src.simulation.lifecyle.Lifecycle import Lifecycle

class ProductionAsset(Lifecycle):

    def __init__(self,
                 udi: int,
                 product_id: str,
                 type: str,
                 air_temp: float,
                 process_temp: float,
                 rotational_speed: int,
                 torque: float,
                 tool_wear: int,
                 machine_failure: int,
                 twf: int,
                 hdf: int,
                 pwf: int,
                 osf: int,
                 rnf: int):
        super().__init__(type=type, 
                         tool_wear=tool_wear,
                        failure_modes={
                            FailureMode.TWF: twf,
                            FailureMode.HDF: hdf,
                            FailureMode.PWF: pwf,
                            FailureMode.OSF: osf,
                            FailureMode.RNF: rnf
                        })
        self.__udi = udi
        self.__product_id = product_id
        self.__air_temp = air_temp
        self.__process_temp = process_temp
        self.___rotational_speed = rotational_speed
        self.___torque = torque
        self.___machine_failure = machine_failure
        self.log = "設備初始化成功"
        