#region class definitions
class Loop():
    #region constructor
    def __init__(self, name, nodes):
        """
        Defines a loop as a list of node names.
        :param name: (str) Name of the loop.
        :param nodes: (list) List of node names that define the loop.
        """
        #region attributes
        self.name = name
        self.nodes = nodes
        #endregion

    # region methods
    def traverse_loop(self):
        """
        Returns a string representation of the loop traversal.
        """
        loop_path = "-".join(self.nodes)  # Construct traversal path
        return f"Traversing loop: {loop_path}"
    #endregion
#endregion