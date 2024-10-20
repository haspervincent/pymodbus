from pyModbusTCP.server import ModbusServer
import time

def main():

    try:
        server = ModbusServer(host='127.0.0.1', port=502, no_block=True)
        server.start()
        if server.is_run:
            print("=== Modbus server started successfully ===")
            print("Status: \033[92mRunning\033[0m")

            server.data_bank.set_discrete_inputs(0, [False]*100)
            server.data_bank.set_coils(0, [False]*100)
            server.data_bank.set_input_registers(0, [0]*100)
            server.data_bank.set_holding_registers(0, [0]*100)

            while 1:
                # di = server.data_bank.get_discrete_inputs(0, 100)
                # co = server.data_bank.get_coils(0, 100)
                # ir = server.data_bank.get_input_registers(0, 100)
                hr = server.data_bank.get_holding_registers(0, 100)

                # print(f"di: {di[:10]}")
                # print(f"co: {co[:10]}")
                # print(f"ir: {ir[:10]}")
                print(f"hr: {hr[:10]}")

                time.sleep(5)

    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")

    finally:
        server.stop()
        print("Status: \033[91mStopped\033[0m")
    
if __name__ == '__main__':
    main()
