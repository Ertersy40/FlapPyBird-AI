from random import uniform, seed, randint
from math import exp

def activationFunc(inp):
    try:
        return 1/(1 +  exp(-inp))
    except:
        return 0
    
def get_copies(original_network, num_copies, mutation_rate):
    seed()
    copies = [original_network]
    
    for _ in range(num_copies - 1):
        current_copy = Network(original_network.layerMap)
        
        # Mutate Connections
        mutate_connections(original_network, current_copy, mutation_rate)

        # Mutate Nodes
        mutate_nodes(original_network, current_copy, mutation_rate)

        copies.append(current_copy)

    return copies

def mutate_connections(original, copy, mutation_rate):
    for layer_idx, connection_layer in enumerate(copy.connections):
        for conn_idx, connection in enumerate(connection_layer):
            weight_offset = get_random_offset(mutation_rate)
            copy.connections[layer_idx][conn_idx].weight = original.connections[layer_idx][conn_idx].weight + weight_offset

def mutate_nodes(original, copy, mutation_rate):
    for layer_idx, node_layer in enumerate(copy.nodes):
        for node_idx, node in enumerate(node_layer):
            bias_offset = get_random_offset(mutation_rate)
            copy.nodes[layer_idx][node_idx].bias = original.nodes[layer_idx][node_idx].bias + bias_offset
            copy.nodes[layer_idx][node_idx].value = 0  # Resetting value

def get_random_offset(mutation_rate):
    if randint(1, 3) == 3:
        return 0
    else:
        return round(uniform(-1 * mutation_rate, mutation_rate), 5)
    
class Node:
    def __init__(self):
        self.bias = 0
        self.value = None

        self.inConnections = []
    
    def calc(self):
        self.value = 0
        for x in self.inConnections:
            self.value += x.weight * x.inNode.value
        self.value += self.bias
        self.value = activationFunc(self.value)

class Connection:
    def __init__(self, inNode, outNode, weight):
        self.weight = weight
        self.inNode = inNode
        self.outNode = outNode


class Network:
    def __init__(self, layers=[3, 3, 3], lower=-5, upper=5, decimalPlaces=5):
        self.layerMap = layers
        self.nodes = []
        self.connections = []
        
        if len(layers) <= 1:
            print("A network with only one layer is very pointless my dude...")
            return
        
        # Initialize node layers with random biases
        self._initialize_nodes(lower, upper, decimalPlaces)
        
        # Create connections between nodes in adjacent layers
        self._initialize_connections(lower, upper, decimalPlaces)
    
    def _initialize_nodes(self, lower, upper, decimalPlaces):
        for layer_size in self.layerMap:
            node_layer = []
            for _ in range(layer_size):
                node = Node()
                node.bias = round(uniform(lower, upper), decimalPlaces)
                node_layer.append(node)
            self.nodes.append(node_layer)

    def _initialize_connections(self, lower, upper, decimalPlaces):
        for layer_idx in range(len(self.nodes) - 1):
            connection_layer = []
            for in_node in self.nodes[layer_idx]:
                for out_node in self.nodes[layer_idx + 1]:
                    connection = Connection(in_node, out_node, weight=round(uniform(lower, upper), decimalPlaces))
                    connection_layer.append(connection)
                    
                    # Update node objects with their incoming and outgoing connections
                    out_node.inConnections.append(connection)
            
            self.connections.append(connection_layer)

    def forward_propagate(self, inputs):
        # Validate the number of inputs
        if len(inputs) != self.layerMap[0]:
            print("Enter the right amount of inputs you donkey!!!")
            print(f"Inputs entered: {len(inputs)}")
            print(f"Inputs required: {self.layerMap[0]}")
            return
        
        # Assign inputs to the first layer of nodes
        for idx, input_value in enumerate(inputs):
            self.nodes[0][idx].value = input_value
        
        # Calculate node values for hidden and output layers
        for node_layer in self.nodes[1:]:  # Skip the input layer
            for node in node_layer:
                node.calc()

        # Collect and return output values
        return [node.value for node in self.nodes[-1]]



