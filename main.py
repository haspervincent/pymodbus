from watersim.base import Epanet, ModbusClient
import time

def main():
    """Runs a hydraulic simulation.
    """
    d = Epanet('networks/test.inp')
    d.setTimeSimulationDuration(60 * 20)
    d.setTimeHydraulicStep(60 * 10)
    
    client = ModbusClient(host='127.0.0.1', port=502)
    client.connect()

    try:
        d.openHydraulicAnalysis()
        d.initializeHydraulicAnalysis()

        while True:
            # This code sets the simulation duration to run infinitely.
            x = d.getTimeSimulationDuration() + d.getTimeHydraulicStep()
            d.setTimeSimulationDuration(x)
            
            d.runHydraulicAnalysis()

            # tstep = d.runHydraulicAnalysis()
            # print(tstep, end=' ')
            
            # if tstep >= d.getTimeSimulationDuration():
            #     break 

            # LOGIC HERE ############################################################
                
            f = client.read_floats(0, 4)
            print(f)
            print(f.floats)
            hr = client.read_holding_registers(0, 4)
            print(hr)
            print(hr.registers)

            print(d.tank_heads)
            print(d.tank_min_water_levels)
            print(d.tank_max_water_levels)
            print(d.pipe_statuses)
            print(d.pump_powers)

            # END ###################################################################

            d.nextHydraulicAnalysisStep()

            time.sleep(1)  

    except KeyboardInterrupt:
        print('>--- Program interrupted by user ---')
    
    finally:
        d.closeHydraulicAnalysis()         
        d.unload()
        client.close()

if __name__ == '__main__':
    main()
