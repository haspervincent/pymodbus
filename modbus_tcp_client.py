from pyModbusTCP.client import ModbusClient
import time
import random

def main():

    try:
        client = ModbusClient(host='127.0.0.1', port=502, unit_id=1, auto_open=True)
        client.open()
        if client.is_open:
            print("=== Successfully connected to Modbus server ===")
            print("Status: \033[92mConnected\033[0m")

            while 1:
                # r_int = random.randint(0, 9)
                # r_bool = True if random.randint(0, 1) == 1 else False
                # client.write_single_coil(r_int, r_bool)

                r_int1 = random.randint(0, 9)
                r_int2 = random.randint(0, 9) # up to 16-bit (0-65535)
                client.write_single_register(r_int1, r_int2)
                
                # di = client.read_discrete_inputs(0, 100)
                # co = client.read_coils(0, 100) 
                # ir = client.read_input_registers(0, 100)
                hr = client.read_holding_registers(0, 100)
                
                # print(f"di: {di[:10]}")
                # print(f"co: {co[:10]}")
                # print(f"ir: {ir[:10]}")
                print(f"hr: {hr[:10]}")
                
                time.sleep(5)

    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")

    finally:
        client.close()
        print("Status: \033[91mDisconnected\033[0m")
    
if __name__ == '__main__':
    main()
