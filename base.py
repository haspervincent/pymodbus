from epyt import epanet
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian

class Epanet(epanet):
    """This class extends the existing 'epanet' class with additional functionality
    to get the relevant node and link values.
    """
    @property
    def tank_heads(self) -> list[float]:
        indices = self.getNodeTankIndex()
        return [float(self.getNodeHydraulicHead(i)) for i in indices]

    @property
    def tank_min_water_levels(self) -> list[float]:
        indices = self.getNodeTankIndex()
        return [float(self.getNodeTankMinimumWaterLevel(i)) for i in indices]
    
    @property
    def tank_max_water_levels(self) -> list[float]:
        indices = self.getNodeTankIndex()
        return [float(self.getNodeTankMaximumWaterLevel(i)) for i in indices]

    @property
    def pipe_statuses(self) -> list[int]:
        indices = self.getLinkPipeIndex()
        return [int(self.getLinkStatus(i)) for i in indices]
   
    @property
    def pump_powers(self) -> list[float]:
        indices = self.getLinkPumpIndex()
        return [float(self.getLinkPumpPower(i)) for i in indices]

class ReadFloatsResponse:
    def __init__(self, floats: list[float]):
        self.floats = floats
    
    def __str__(self):
        return f'ReadFloatsResponse ({len(self.floats)})'

    def __repr__(self):
        return self.__str__()

class ModbusClient(ModbusTcpClient):
    """This class extends the existing 'ModbusTcpClient' class with additional functionality
    for reading and writing float values.
    """
    def read_floats(self, address: int, count: int = 1, slave: int = 1) -> ReadFloatsResponse:
        response = self.read_holding_registers(address, count * 2, slave=slave)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        return ReadFloatsResponse([decoder.decode_32bit_float() for _ in range(count)])
    
    def write_float(self, address: int, value: float, slave: int = 1) -> None:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_32bit_float(value)
        registers = builder.to_registers()
        self.write_registers(address, registers, slave=slave)

    def write_floats(self, address: int, values: list[float], slave: int = 1) -> None:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        for value in values: 
            builder.add_32bit_float(value)
        registers = builder.to_registers()
        self.write_registers(address, registers, slave=slave)
