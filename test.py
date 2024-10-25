from epyt import epanet

from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian

class Epanet(epanet):
    """This class extends the existing 'epanet' class with additional functionality
    to get the relevant node and link values.
    """    
    def get_node_values(self):
        node_values = {}

        for name_id in self.getNodeNameID():
            node_index = self.getNodeIndex(name_id)
            node_type = self.getNodeType(node_index)

            node_values[name_id] = {
                'type': node_type,
                'pressure': round(self.getNodePressure(node_index), 5),
                'head': round(self.getNodeHydraulicHead(node_index), 5),
                **({
                    'min_level': float(self.getNodeTankMinimumWaterLevel(node_index)),
                    'max_level': float(self.getNodeTankMaximumWaterLevel(node_index))
                } if node_type == 'TANK' else {})
            }

        return node_values

    def get_link_values(self):
        link_values = {}

        for name_id in self.getLinkNameID():
            link_index = self.getLinkIndex(name_id)
            link_type = self.getLinkType(link_index)

            link_values[name_id] = {
                'type': link_type,
                **({'status': self.getLinkStatus(link_index)} if link_type == 'PIPE' else {}),
                **({'power': self.getLinkPumpPower(link_index)} if link_type == 'PUMP' else {}),
                **({'setting': self.getLinkSettings(link_index)} if link_type == 'VALVE' else {})
            }

        return link_values
    
    def get_node_values_modbus(self):
        node_values_modbus = []

        for name_id in self.getNodeNameID():
            node_index = self.getNodeIndex(name_id)
            node_type = self.getNodeType(node_index)

            node_values_modbus.extend([
                round(self.getNodePressure(node_index), 5),
                round(self.getNodeHydraulicHead(node_index), 5)
            ])

            match node_type:
                case 'TANK':
                    node_values_modbus.extend([
                        float(self.getNodeTankMinimumWaterLevel(node_index)),
                        float(self.getNodeTankMaximumWaterLevel(node_index))
                    ])
                case _:
                    pass

        return node_values_modbus

    def get_link_values_modbus(self):
        link_values_modbus = []

        for name_id in self.getLinkNameID():
            link_index = self.getLinkIndex(name_id)
            link_type = self.getLinkType(link_index)

            match link_type:
                case 'PIPE':
                    link_values_modbus.extend(int(self.getLinkStatus(link_index)))
                case 'PUMP':
                    link_values_modbus.extend(self.getLinkPumpPower(link_index))
                case 'VALVE':
                    link_values_modbus.extend(self.getLinkSettings(link_index))
                case _:
                    pass

        return link_values_modbus

class ModbusClient(ModbusTcpClient):
    """This class extends the existing 'ModbusTcpClient' class with additional functionality
    for reading and writing float values.
    """
    class ModbusFloatResponse:
        def __init__(self, floats: list[float]):
            self.floats = floats
        
        def __getitem__(self, index: int):
            return self.floats[index]

        def __len__(self):
            return len(self.floats)

    def read_floats(self, address: int, count: int = 1, slave: int = 1):
        """Read float values from the specified address."""
        result = self.read_holding_registers(address, count * 2, slave=slave)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        return self.ModbusFloatResponse([decoder.decode_32bit_float() for _ in range(count)])

    def write_float(self, address: int, value: float, slave: int = 1):
        """Write a single float value to the specified address."""
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_32bit_float(value)
        registers = builder.to_registers()
        self.write_registers(address, registers, slave=slave)

    def write_floats(self, address: int, values: list[float], slave: int = 1):
        """Write multiple float values starting from the specified address."""
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        for value in values:
            builder.add_32bit_float(value)
        registers = builder.to_registers()
        self.write_registers(address, registers, slave=slave)
