import time
from epyt import epanet

class Epanet(epanet):
    """This class extends the existing epanet class with additional functionality.
    """    
    def get_node_values(self):
        node_values = {
            name_id: {
                'type': self.getNodeType(self.getNodeIndex(name_id)),
                'pressure': round(self.getNodePressure(self.getNodeIndex(name_id)), 5),
                'head': round(self.getNodeHydraulicHead(self.getNodeIndex(name_id)), 5),
                **({
                    'min_level': float(self.getNodeTankMinimumWaterLevel(self.getNodeIndex(name_id))),
                    'max_level': float(self.getNodeTankMaximumWaterLevel(self.getNodeIndex(name_id)))
                } if self.getNodeType(self.getNodeIndex(name_id)) == 'TANK' else {})
            }
            for name_id in self.getNodeNameID()
        }
        return node_values

    def get_link_values(self):
        link_values = {
            name_id: {
                'type': self.getLinkType(self.getLinkIndex(name_id)),
                **({
                    'status': int(self.getLinkStatus(self.getLinkIndex(name_id)))
                } if self.getLinkType(self.getLinkIndex(name_id)) == 'PIPE' else {}),
                **({
                    'power': self.getLinkPumpPower(self.getLinkIndex(name_id))
                } if self.getLinkType(self.getLinkIndex(name_id)) == 'PUMP' else {}),
                **({
                    'setting': self.getLinkSettings(self.getLinkIndex(name_id))
                } if self.getLinkType(self.getLinkIndex(name_id)) == 'VALVE' else {})
            }
            for name_id in self.getLinkNameID()
        }
        return link_values

def main():
    """Runs a hydraulic simulation.
    """
    d = Epanet('test.inp')
    d.setTimeSimulationDuration(60 * 20)
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

            # LOGIC HERE ####################################################################################

            

            # END ###########################################################################################

            d.nextHydraulicAnalysisStep()

            time.sleep(1)  

    except KeyboardInterrupt:
        print('>--- Program interrupted by user ---')
    
    finally:
        d.closeHydraulicAnalysis()         
        d.unload()

if __name__ == '__main__':
    main()
