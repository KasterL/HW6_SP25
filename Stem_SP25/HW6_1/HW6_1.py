#region imports
from ResistorNetwork import ResistorNetwork, ResistorNetwork_2
#endregion

# region Function Definitions
def main():
    """
    This program solves for the unknown currents in the circuit of the homework assignment.
    :return: nothing
    """
    print("Network 1:")
    Net= ResistorNetwork()  #Instantiate a ResistorNetwork object
    ResistorNetwork() #call the function from Net that builds the resistor network from a text file
    IVals=Net.AnalyzeCircuit()  # Solve for unknown currents

    print("\nNetwork 2:")
    Net_2 = ResistorNetwork_2() #Instantiate a ResistorNetwork_2 object
    Net_2.BuildNetworkFromFile("ResistorNetwork.txt") #call the function from Net that builds the resistor network from a text file
    IVals_2=Net_2.AnalyzeCircuit()   # Solve for unknown currents
# endregion

# region function calls
if __name__=="__main__":
    main()
# endregion