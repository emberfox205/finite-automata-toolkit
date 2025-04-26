from graphviz import Digraph

# Encompass properties and interactions with a DFA
class DFA():
    def __init__(self, alphabet: tuple, states: tuple, initial_state: str, final_states: tuple, rules: dict):
        self.alphabet = alphabet
        self.states = states
        self.initial_state: str = initial_state
        self.final_states: list = final_states
        self.rules: dict = rules
        # Internal attrs to mark traced nodes and edges on graph
        self.__traced_states__: list = []
        self.__traced_rules__: dict = {}
        self.__input_str__: str = ""
        
        self.default_state_attrs = {
            'shape': 'circle',
            'fontname': 'Times-Roman',
            'fontsize': '12',
            'style': 'filled',
            'fillcolor': 'white',
            'fontcolor': 'red',
            'color':'black'
        }
        self.traced_default_state_attrs = {
            'shape': 'circle',
            'fontname': 'Times-Roman',
            'fontsize': '12',
            'style': 'filled',
            'fillcolor': 'white',
            'fontcolor': 'red',
            'color':'red'
        }
        self.final_state_attrs = {
            'shape': 'doublecircle',
            'fontname': 'Times-Roman',
            'fontsize': '10',
            'style': 'filled',
            'fillcolor': 'white',
            'fontcolor': 'red',
            'color':'black'
        }
        self.traced_final_state_attrs = {
            'shape': 'doublecircle',
            'fontname': 'Times-Roman',
            'fontsize': '10',
            'style': 'filled',
            'fillcolor': 'white',
            'fontcolor': 'red',
            'color':'red'
        }
        self.edge_attrs = {
            'fontname': 'Times-Roman',
            'fontsize': '16',
            'fontcolor': 'blue',
            'color':'black',
            'penwidth': '1.0'
        }
        self.traced_edge_attrs = {
            'fontname': 'Times-Roman',
            'fontsize': '16',
            'fontcolor': 'blue',
            'color':'red',
            'penwidth': '1.0'
        }

    # Create a graph object render-able by st.graphviz()
    def create_dfa(self, validation_trace=False):
        dfa = Digraph('DFA')
        dfa.attr(rankdir='LR',size='8.5')
        
        # Start node (invisible) to create an initial state's input edge 
        dfa.attr('node', shape='none', height='0', width='0')
        dfa.node('', label='')
        
        # Add states 
        for state in self.states:
            # Unpack attribute dict 
            # Choose color based on mode (normal/tracing)
            if state in self.final_states:
                if validation_trace and state in self.__traced_states__:
                    dfa.attr('node', **self.traced_final_state_attrs)
                else:
                    dfa.attr('node', **self.final_state_attrs)
            else:
                if validation_trace and state in self.__traced_states__:
                    dfa.attr('node', **self.traced_default_state_attrs)
                else:
                    dfa.attr('node', **self.default_state_attrs)
            dfa.node(str(state))
        
        # Apply color based on mode (normal/tracing)
        if validation_trace:
            dfa.attr("edge", **self.traced_edge_attrs)
        else:
            dfa.attr("edge", **self.edge_attrs)
        # Add start arrow
        dfa.edge('', str(self.initial_state), arrowsize='1')
        
        # Group transitions 
        grouped_transitions = {}
        for (state, symbol), next_state in self.rules.items():
                    key = (state, next_state)
                    if key not in grouped_transitions:
                        grouped_transitions[key] = []
                    grouped_transitions[key].append(symbol)
                    
        # Add edges
        dfa.attr("edge", **self.edge_attrs)
        for (src, dst), symbols in grouped_transitions.items():
            # Sort and join symbols
            if len(symbols) == 1:
                label = symbols[0]
            else:
                label = ', '.join(sorted(symbols))
            
            # Apply color based on mode (normal/tracing)
            if validation_trace and any((src, symbol) in self.__traced_rules__ for symbol in symbols):
                dfa.attr("edge", **self.traced_edge_attrs)
            else:
                dfa.attr("edge", **self.edge_attrs)
            
            # Style self-loops differently 
            if src == dst:
                dfa.edge(str(src), str(dst), label=label, constraint='false')
            else:
                dfa.edge(str(src), str(dst), label=label)

        return dfa  

    # Check if input string is syntactically correct
    # Does not check whether string is accepted / rejected
    def check_syntax(self, raw_input: str) -> bool:
        input_str = raw_input.strip()
        for symbol in input_str:
            if symbol not in self.alphabet:
                return False 
        return True
    
    # Validate string against DFA 
    def validate(self, input: str) -> bool:
        # Reset internal attrs
        self.__traced_states__ = [self.initial_state,]
        self.__traced_rules__ = {}
        self.__input_str__ = input
        # Check syntax
        if not self.check_syntax(input):
            return False
        # Process input 
        current_state = self.initial_state
        input_str = input.strip()
        
        if input_str:
            for symbol in input_str:
                # Update on valid transition
                if (current_state, symbol) in self.rules:
                    
                    # Add states and rules to traced collections
                    if current_state not in self.__traced_states__:
                        self.__traced_states__.append(current_state)
                    if self.rules[(current_state, symbol)] not in self.__traced_states__:
                        self.__traced_states__.append(self.rules[(current_state, symbol)])
                    if (current_state, symbol) not in self.__traced_rules__:
                        self.__traced_rules__[(current_state, symbol)] = self.rules[(current_state, symbol)]
                        
                    current_state = self.rules[(current_state, symbol)]
                # Reject otherwise
                else:
                    return False 
          
        # Check if the resulting state is one of the final states 
        return current_state in self.final_states 
    
