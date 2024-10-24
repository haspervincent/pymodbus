import time
from epyt import epanet

def main():
    """Runs a hydraulic simulation."""
    d = epanet('net1.inp')
    d.setTimeSimulationDuration(64 * 20) # 24 * 60 * 60
    d.setTimeHydraulicStep(64 * 10)
    
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

            # NODES : (JUNCTIONS, RESERVOIRS, TANKS)
            tank_values = {i: d.getNodeHydraulicHead(d.getNodeIndex(i)) for i in d.getNodeTankNameID()}
            print(tank_values)

            # LINKS : (PIPES, PUMPS, VALVES)


            d.nextHydraulicAnalysisStep()

            time.sleep(1)  

    except KeyboardInterrupt:
        print('>--- Program interrupted by user ---')
    
    finally:
        d.closeHydraulicAnalysis()         
        d.unload()

if __name__ == '__main__':
    main()
