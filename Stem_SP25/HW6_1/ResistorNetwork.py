#region imports
from scipy.optimize import fsolve
from Resistor import Resistor
from VoltageSource import VoltageSource
from Loop import Loop
#endregion

#region class definitions
class ResistorNetwork():
    #region constructor
    def __init__(self):
        """
        The resistor network consists of Loops, Resistors and Voltage Sources.
        This is the constructor for the network and it defines fields for Loops, Resistors and Voltage Sources.
        You can populate these lists manually or read them in from a file.
        """
        #region attributes
        self.Loops = []  # initialize an empty list of loop objects in the network
        self.Resistors = []  # initialize an empty a list of resistor objects in the network
        self.VSources = []  # initialize an empty a list of source objects in the network
        #endregion
    #endregion

    #region methods
    def BuildNetworkFromFile(self, filename):
        """
        This function reads the lines from a file and processes the file to populate the fields
        for Loops, Resistors and Voltage Sources
        :param filename: string for file to process
        :return: nothing
        """
        FileTxt = open(filename,"r").read().split('\n')  # reads from file and then splits the string at the new line characters

        LineNum = 0  # a counting variable to point to the line of text to be processed from FileTxt
        lineTxt = ""  # Variable to store the current line being processed

        # erase any previous
        self.Resistors = []
        self.VSources = []
        self.Loops = []

        # Process each line in the file
        FileLength = len(FileTxt)
        while LineNum < FileLength:
            lineTxt = FileTxt[LineNum].lower().strip()

            if len(lineTxt) <1:
                pass # skip
            elif lineTxt[0] == '#':
                pass  # skips comment lines
            elif "resistor" in lineTxt:
                LineNum = self.MakeResistor(LineNum, FileTxt)
            elif "source" in lineTxt:
                LineNum = self.MakeVSource(LineNum, FileTxt)
            elif "loop" in lineTxt:
                LineNum = self.MakeLoop(LineNum, FileTxt)
            else:
                LineNum+=1  # Move to the next line if no relevant tag is found
            # Ensure LineNum increments to avoid infinite loop
            LineNum += 1
            if LineNum >= FileLength:
                break  # Stop if we exceed the file length

        pass

    # region element creation

    def MakeResistor(self, N, Txt):
        """
        Make a resistor object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        R = Resistor()  # instantiate a new resistor object
        N += 1  # <Resistor> was detected, so move to next line in Txt
        while N < len(Txt):  # Ensure we don't go out of bounds
            txt = Txt[N].lower().strip()  # Retrieve and lowercase the line

            if "name" in txt:
                R.Name = txt.split('=')[1].strip()  # Extract resistor name
            elif "resistance" in txt:
                R.Resistance = float(txt.split('=')[1].strip())  # Extract resistance value
            elif "</resistor>" in txt:
                break  # Exit the loop when the closing tag is found

            N += 1  # Move to the next line

        self.Resistors.append(R)  # Store resistors properly

        return N + 1  # Move past </Resistor> tag
    # endregion

    # region element creation
    def MakeVSource (self, N, Txt):
        """
        Make a voltage source object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a voltage source object
        """
        VS=VoltageSource()  # Instantiate a new voltage source object
        N+=1  # Move to next line
        txt = Txt[N].lower().strip()  # Retrieve and lowercase the line

        while "source" not in txt:
            if "name" in txt:
                VS.Name = txt.split('=')[1].strip()
            if "value" in txt:
                VS.Voltage = float(txt.split('=')[1].strip())
            if "type" in txt:
                VS.Type = txt.split('=')[1].strip()
            N+=1
            txt = Txt[N].lower().strip()   # Update txt to next line

        self.VSources.append(VS)

        return N
    # endregion

    def MakeLoop(self, N, Txt):
        """
        Make a Loop object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        loop_name = ""  # Initialize loop name
        loop_nodes = []  # Initialize loop nodes

        N+=1  # Move to next line
        txt = Txt[N].lower().strip() # Retrieve and lowercase the line
        while "loop" not in txt:
            if "name" in txt:
                loop_name = txt.split('=')[1].strip()
            if "nodes" in txt:
                txt=txt.replace(" ","")  # Remove any spaces
                loop_nodes = txt.split('=')[1].strip().split(',')
            N+=1
            txt = Txt[N].lower().strip()  # Update txt to next line

        # Instantiate the Loop object correctly
        L = Loop(loop_name, loop_nodes)

        self.Loops.append(L)   # Append loop object to the list
        return N

    def AnalyzeCircuit(self):
        """
        Use fsolve to find currents in the resistor network.
        :return:
        """
        # need to set the currents to that Kirchoff's laws are satisfied
        i0 = [0.1, 0.1, 0.1, 0.1]    #define an initial guess for the currents in the circuit
        i = fsolve(self.GetKirchoffVals,i0)
        # print output to the screen
        print("I1 = {:0.1f}".format(i[0]))
        print("I2 = {:0.1f}".format(i[1]))
        print("I3 = {:0.1f}".format(i[2]))
        return i

    def GetKirchoffVals(self,i):
        """
        This function uses Kirchoff Voltage and Current laws to analyze this specific circuitw
        KVL:  The net voltage drop for a closed loop in a circuit should be zero
        KCL:  The net current flow into a node in a circuit should be zero
        :param i: a list of currents relevant to the circuit
        :return: a list of loop voltage drops and node currents
        """
        # set current in resistors in the top loop.
        self.GetResistorByName('ad').Current = i[0]  # I_1 in diagram
        self.GetResistorByName('bc').Current = i[0]  # I_1 in diagram
        self.GetResistorByName('cd').Current = i[2]  # I_3 in diagram
        # set current in resistor in bottom loop.
        self.GetResistorByName('ce').Current = i[1]  # I_2 in diagram
        self.GetResistorByName('de_parallel').Current = i[3]  # Resistor from ResistorNetwork_2.txt
        #calculate net current into node c
        Node_c_Current = sum([i[0],i[1],-i[2]])

        KVL = self.GetLoopVoltageDrops()  # two equations here
        KVL.append(Node_c_Current)  # one equation here

        # Additional KCL equation for new node (e or f) in the second circuit
        Node_f_Current = sum([i[1], -i[2], -i[3]])  # Adjust based on circuit
        KVL.append(Node_f_Current)  # Adding the extra KCL equation

        return KVL

    def GetElementDeltaV(self, name):
        """
        Need to retrieve either a resistor or a voltage source by name.
        :param name:Name of the element
        :return:Voltage drop or voltage value
        """
        # Check for resistors
        for r in self.Resistors:
            if name == r.Name:
                return -r.DeltaV()
            if name[::-1] == r.Name:  # Reverse name for opposite traversal
                return -r.DeltaV()

        # Check for voltage sources
        for v in self.VSources:
            if name == v.Name:
                return v.Voltage
            if name[::-1] == v.Name:
                return -v.Voltage

    def GetLoopVoltageDrops(self):
        """
        This calculates the net voltage drop around a closed loop in a circuit based on the
        current flowing through resistors (cause a drop in voltage regardless of direction of traversal) or
        the value of the voltage source that have been set up as positive based on the direction of traversal.
        :return: net voltage drop for all loops in the network.
        """
        loopVoltages=[]
        for L in self.Loops:
            # Traverse loops in order of nodes and add up voltage drops between nodes
            loopDeltaV=0
            for n in range(len(L.nodes)):
                if n == len(L.nodes)-1:
                    name = L.nodes[0] + L.nodes[n]
                else:
                    name = L.nodes[n]+L.nodes[n+1]
                loopDeltaV += self.GetElementDeltaV(name)
            loopVoltages.append(loopDeltaV)
        return loopVoltages

    def GetResistorByName(self, name):
        """
        A way to retrieve a resistor object from self.Resistors based on resistor name
        :param name: (str) The name of the resistor to retrieve
        :return: The resistor object matching the given name.
        """
        for r in self.Resistors:
            if r.Name == name:
                return r

        return None

    #endregion

class ResistorNetwork_2(ResistorNetwork):
    #region constructor
    def __init__(self):
        super().__init__()  # runs the constructor of the parent class
        #region attributes
        #endregion
    #endregion

    #region methods
    def AnalyzeCircuit(self):
        """
        Modifies circuit analysis for the second network.
        """
        i0 = [0.1, 0.1, 0.1, 0.1]  # Initial guess for four unknown currents
        i = fsolve(self.GetKirchoffVals, i0)

        # Print output to the screen
        print("I1 = {:.1f}".format(i[0]))
        print("I2 = {:.1f}".format(i[1]))
        print("I3 = {:.1f}".format(i[2]))
        print("I4 = {:.1f}".format(i[3]))

        return i

    def GetKirchoffVals(self,i):
        """
        Applies Kirchhoff’s Laws for the modified circuit.
        """
        # Set currents in resistors
        self.GetResistorByName('ad').Current = i[0]
        self.GetResistorByName('bc').Current = i[0]
        self.GetResistorByName('cd').Current = i[2]
        self.GetResistorByName('ce').Current = i[1]
        self.GetResistorByName('de_parallel').Current = i[3]

        # Node equation for Kirchhoff’s Current Law (sum of currents into node = 0)
        Node_c_Current = sum([i[0], i[1], -i[2]])  # KCL at node c
        Node_e_Current = sum([i[1], -i[2], -i[3]])  # KCL at node e

        # Kirchhoff's Voltage Law equations
        KVL = self.GetLoopVoltageDrops()
        KVL.append(Node_c_Current)  # Adding the first KCL equation
        KVL.append(Node_e_Current)  # Adding the second KCL equation

        return KVL
    #endregion
#endregion
