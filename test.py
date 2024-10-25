import time
from epyt import epanet
import json

def main():
    """Runs a hydraulic simulation.
    """
    d = epanet('test.inp')
    d.setTimeSimulationDuration(60 * 20) # 24 * 60 * 60 (24 hours in seconds)
    d.setTimeHydraulicStep(60 * 10)
    
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

            # hydraulic_heads = [d.getNodeHydraulicHead(d.getNodeIndex(name_id)) for name_id in d.getNodeTankNameID()]




            node_values = {
                'total': d.getNodeCount(),
                'reservoirs': d.getNodeReservoirCount(),
                'tanks': d.getNodeTankCount(),
                'junctions': d.getNodeJunctionCount()
            }
            # print(node_values)
            json_node_values = json.dumps(node_values, indent=4)
            print(json_node_values)

            junction_values = {
                i: {
                    'elev': round(float(d.getNodeElevations(d.getNodeIndex(i))), 2),
                }
                for i in d.getNodeJunctionNameID()
            }
            # print(junction_values)
            json_junction_values = json.dumps(junction_values, indent=4)
            print(json_junction_values)

            reservoir_values = {
                i: {
                    'head': int(d.getNodeHydraulicHead(d.getNodeIndex(i)))
                }
                for i in d.getNodeReservoirNameID()
            }
            # print(reservoir_values)
            json_reservoir_values = json.dumps(reservoir_values, indent=4)
            print(json_reservoir_values)

            tank_values = {
                i: {
                    'elevation': round(float(d.getNodeElevations(d.getNodeIndex(i))), 1),
                    'init_level': round(float(d.getNodeTankInitialLevel(d.getNodeIndex(i))), 1),
                    'min_level': round(float(d.getNodeTankMinimumWaterLevel(d.getNodeIndex(i))), 1),
                    'max_level': round(float(d.getNodeTankMaximumWaterLevel(d.getNodeIndex(i))), 1),
                    'head': round(float(d.getNodeHydraulicHead(d.getNodeIndex(i))), 8)
                }
                for i in d.getNodeTankNameID()
            }
            # print(tank_values)
            json_tank_values = json.dumps(tank_values, indent=4)
            print(json_tank_values)

            link_values = {
                'total': d.getLinkCount(),
                'pipes': d.getLinkPipeCount(),
                'pumps': d.getLinkPumpCount(),
                'valves': d.getLinkValveCount()
            }
            # print(link_values)
            json_link_values = json.dumps(link_values, indent=4)
            print(json_link_values)

            pipe_values = {
                i: {
                    'roughness': round(float(d.getLinkRoughnessCoeff(d.getLinkIndex(i))), 8),
                    'status': int(d.getLinkStatus(d.getLinkIndex(i))),
                    'flow': round(float(d.getLinkFlows(d.getLinkIndex(i))), 8)
                }
                for i in d.getLinkPipeNameID()
            }
            # print(pipe_values)
            json_pipe_values = json.dumps(pipe_values, indent=4)
            print(json_pipe_values)

            pump_values = {
                i: {
                    'power': int(d.getLinkPumpPower(d.getLinkIndex(i))),
                    'flow': round(float(d.getLinkFlows(d.getLinkIndex(i))), 8)
                }
                for i in d.getLinkPumpNameID()
            }
            # print(pump_values)
            json_pump_values = json.dumps(pump_values, indent=4)
            print(json_pump_values)

            valve_values = {
                i: {
                    'type': str(d.getLinkType(d.getLinkIndex(i))),
                    'setting': int(d.getLinkSettings(d.getLinkIndex(i))),
                    'flow': round(float(d.getLinkFlows(d.getLinkIndex(i))), 8)
                } 
                for i in d.getLinkValveNameID() 
            }
            # print(valve_values)
            json_valve_values = json.dumps(valve_values, indent=4)
            print(json_valve_values)

     


            d.nextHydraulicAnalysisStep()

            time.sleep(1)  

    except KeyboardInterrupt:
        print('>--- Program interrupted by user ---')
    
    finally:
        d.closeHydraulicAnalysis()         
        d.unload()

if __name__ == '__main__':
    main()
