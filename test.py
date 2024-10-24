import time
from epyt import epanet

def main():
    """Runs a hydraulic simulation."""
    d = epanet('net1.inp')
    d.setTimeSimulationDuration(10)
    d.setTimeHydraulicStep(1)
    
    try:
        d.openHydraulicAnalysis()
        d.initializeHydraulicAnalysis()

        while True:
            # This code sets the simulation duration to run infinitely.
            x = d.getTimeSimulationDuration() + d.getTimeHydraulicStep()
            d.setTimeSimulationDuration(x)
            
            tstep = d.runHydraulicAnalysis()
            
            # if tstep >= d.getTimeSimulationDuration():
            #     break

            print(tstep, [d.getNodeHydraulicHead(i) for i in d.getNodeTankIndex()])

            d.nextHydraulicAnalysisStep()

            time.sleep(1)  

    except KeyboardInterrupt:
        print('>--- Program interrupted by user ---')
    
    finally:
        d.closeHydraulicAnalysis()         
        d.unload()

if __name__ == '__main__':
    main()