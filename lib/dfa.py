import pandas as pd
import numpy as np
from graphviz import Digraph


# Encompass properties and interactions with a DFA
class DFA:
    def __init__(
        self,
        alphabet: tuple,
        states: tuple,
        initial_state: str,
        final_states: tuple,
        rules: dict,
    ):
        self.alphabet: tuple = alphabet
        self.states: tuple = states
        self.initial_state: str = initial_state
        self.final_states: tuple = final_states
        self.rules: dict = rules

        # Internal attributes
        self.__reduced_states__: list = list()
        self.__reduced_initial_state__: str = str()
        self.__reduced_final_states__: list = list()
        self.__reduced_rules__: dict = dict()

        self.__traced_states__: list = []
        self.__traced_rules__: dict = {}
        self.__input_str__: str = ""
        self.__reduction_df__: pd.DataFrame = pd.DataFrame()

        # Graphviz elements' style attributes
        # Stylistic choices mimic what's shown on lecturer's slides
        self.default_state_attrs = {
            "shape": "circle",
            "fontname": "Times-Roman",
            "fontsize": "12",
            "style": "filled",
            "fillcolor": "white",
            "fontcolor": "red",
            "color": "black",
        }
        self.traced_default_state_attrs = {
            "shape": "circle",
            "fontname": "Times-Roman",
            "fontsize": "12",
            "style": "filled",
            "fillcolor": "white",
            "fontcolor": "red",
            "color": "red",
        }
        self.final_state_attrs = {
            "shape": "doublecircle",
            "fontname": "Times-Roman",
            "fontsize": "10",
            "style": "filled",
            "fillcolor": "white",
            "fontcolor": "red",
            "color": "black",
        }
        self.traced_final_state_attrs = {
            "shape": "doublecircle",
            "fontname": "Times-Roman",
            "fontsize": "10",
            "style": "filled",
            "fillcolor": "white",
            "fontcolor": "red",
            "color": "red",
        }
        self.edge_attrs = {
            "fontname": "Times-Roman",
            "fontsize": "16",
            "fontcolor": "blue",
            "color": "black",
            "penwidth": "1.0",
        }
        self.traced_edge_attrs = {
            "fontname": "Times-Roman",
            "fontsize": "16",
            "fontcolor": "blue",
            "color": "red",
            "penwidth": "1.0",
        }

    # Create a graph object render-able by st.graphviz()
    def create_dfa(self, validation_trace=False) -> Digraph:
        dfa = Digraph("DFA")
        dfa.attr(rankdir="LR", size="8.5")

        # Start node (invisible) to create an initial state's input edge
        dfa.attr("node", shape="none", height="0", width="0")
        dfa.node("", label="")

        # Add states
        for state in self.states:
            # Unpack attribute dict
            # Choose color based on mode (normal/tracing)
            if state in self.final_states:
                if validation_trace and state in self.__traced_states__:
                    dfa.attr("node", **self.traced_final_state_attrs)
                else:
                    dfa.attr("node", **self.final_state_attrs)
            else:
                if validation_trace and state in self.__traced_states__:
                    dfa.attr("node", **self.traced_default_state_attrs)
                else:
                    dfa.attr("node", **self.default_state_attrs)
            dfa.node(str(state))

        # Apply color based on mode (normal/tracing)
        if validation_trace:
            dfa.attr("edge", **self.traced_edge_attrs)
        else:
            dfa.attr("edge", **self.edge_attrs)
        # Add start arrow
        dfa.edge("", str(self.initial_state), arrowsize="1")

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
                label = ", ".join(sorted(symbols))

            # Apply color based on mode (normal/tracing)
            if validation_trace and any(
                (src, symbol) in self.__traced_rules__ for symbol in symbols
            ):
                dfa.attr("edge", **self.traced_edge_attrs)
            else:
                dfa.attr("edge", **self.edge_attrs)

            # Style self-loops differently
            if src == dst:
                dfa.edge(str(src), str(dst), label=label, constraint="false")
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
        self.__traced_states__ = [
            self.initial_state,
        ]
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
                    if (
                        self.rules[(current_state, symbol)]
                        not in self.__traced_states__
                    ):
                        self.__traced_states__.append(
                            self.rules[(current_state, symbol)]
                        )
                    if (current_state, symbol) not in self.__traced_rules__:
                        self.__traced_rules__[(current_state, symbol)] = self.rules[
                            (current_state, symbol)
                        ]

                    current_state = self.rules[(current_state, symbol)]

                # Reject otherwise
                else:
                    return False

        # Check if the resulting state is one of the final states
        return current_state in self.final_states

    # Get all unmarked cells
    # Return form: [(row_0, col_0), (row_1, label_1), ...]
    def __fetch_zero_cells__(self) -> list:
        # Get row and column labels of all unmarked cells
        zero_positions = np.where(self.__reduction_df__ == 0)
        row_indices = zero_positions[0]
        col_indices = zero_positions[1]
        row_labels = [self.__reduction_df__.index[i] for i in row_indices]
        col_labels = [self.__reduction_df__.columns[i] for i in col_indices]
        zero_cells = list(zip(row_labels, col_labels))
        return zero_cells

    # Set up all (p,q) pairs before mark()
    def __construct_df__(self) -> None:
        self.__reduction_df__ = pd.DataFrame(
            pd.NA, index=self.states, columns=self.states
        )

        # Set up half-matrix for Myhill-Nerode algorithm / mark()
        for i, col in enumerate(self.__reduction_df__.columns):
            self.__reduction_df__.iloc[i, :i] = 0

        # Set up initial marked cells from F and !F sets
        zero_cells = self.__fetch_zero_cells__()

        for cell in zero_cells:
            # Both labels should return different statuses
            if (cell[0] in self.final_states) != (cell[1] in self.final_states):
                if self.__reduction_df__.loc[cell[0], cell[1]] == None:
                    self.__reduction_df__.loc[cell[1], cell[0]] = 1
                else:
                    self.__reduction_df__.loc[cell[0], cell[1]] = 1
        return self.__reduction_df__

    # Myhill-Nerode algorithm, first part
    def mark(self) -> None:
        self.__construct_df__()

        changed = True
        while changed:
            changed = False
            zero_cells = self.__fetch_zero_cells__()

            for cell in zero_cells:
                for symbol in self.alphabet:
                    move_0 = self.rules[(cell[0], symbol)]
                    move_1 = self.rules[(cell[1], symbol)]

                    # Get the value for the destination pair
                    dest_value = None
                    if not pd.isna(self.__reduction_df__.loc[move_0, move_1]):
                        dest_value = self.__reduction_df__.loc[move_0, move_1]
                    elif not pd.isna(self.__reduction_df__.loc[move_1, move_0]):
                        dest_value = self.__reduction_df__.loc[move_1, move_0]

                    # If destination pair is distinguishable, mark current pair
                    if dest_value == 1:
                        self.__reduction_df__.loc[cell[0], cell[1]] = 1
                        changed = True
                        break  # No need to check other symbols

    # Myhill-Nerode algorithm, second part
    # Consecutive and explicit calls to mark() and reduce() are required
    # This is to comply with the expectation of the exercise
    def reduce(self) -> None:
        zero_cells = self.__fetch_zero_cells__()

        equi_classes = {state: {state} for state in self.states}

        # Merge classes based on unmarked pairs
        for s1, s2 in zero_cells:
            # Find the representatives of each class
            rep1 = None
            rep2 = None
            for rep, cls in equi_classes.items():
                if s1 in cls:
                    rep1 = rep
                if s2 in cls:
                    rep2 = rep
                if rep1 and rep2:
                    break

            # If states are in different classes, merge them
            if rep1 != rep2:
                equi_classes[rep1].update(equi_classes[rep2])
                del equi_classes[rep2]

        state_mapping = {}
        new_states = []

        for rep, states_set in equi_classes.items():
            states_list = sorted(list(states_set))
            if len(states_list) > 1:
                new_state_name = ", ".join(states_list)
            else:
                new_state_name = states_list[0]
            new_states.append(new_state_name)
            for old_state in states_list:
                state_mapping[old_state] = new_state_name

        # Generate reduced DFA components
        self.__reduced_states__ = new_states
        self.__reduced_initial_state__ = state_mapping[self.initial_state]
        self.__reduced_final_states__ = []

        # Map final states to their new names
        for final_state in self.final_states:
            if state_mapping[final_state] not in self.__reduced_final_states__:
                self.__reduced_final_states__.append(state_mapping[final_state])

        # Generate reduced transition rules
        self.__reduced_rules__ = {}
        for (state, symbol), next_state in self.rules.items():
            # Only add one transition per new state-symbol pair
            new_key = (state_mapping[state], symbol)
            if new_key not in self.__reduced_rules__:
                self.__reduced_rules__[new_key] = state_mapping[next_state]

    # Get a new object updated with new params
    def get_reduced_dfa(self) -> "DFA":
        reduced_dfa = DFA(
            alphabet=self.alphabet,
            states=tuple(self.__reduced_states__),
            initial_state=self.__reduced_initial_state__,
            final_states=tuple(self.__reduced_final_states__),
            rules=self.__reduced_rules__,
        )
        return reduced_dfa

    def remove_inaccessible_states(self) -> None:
        # Find accessible states with BFS
        accessible = set()
        queue = [self.initial_state]

        while queue:
            current = queue.pop(0)
            if current not in accessible:
                accessible.add(current)
                # Add all states reachable from current state
                for symbol in self.alphabet:
                    if (current, symbol) in self.rules:
                        next_state = self.rules[(current, symbol)]
                        if next_state not in accessible:
                            queue.append(next_state)

        # Identify inaccessible states
        inaccessible = set()
        for state in self.states:
            if state not in accessible:
                inaccessible.add(state)

        if not inaccessible:
            return

        # Create new components without inaccessible states
        self.__reduced_states__ = list(accessible)
        self.__reduced_initial_state__ = self.initial_state
        self.__reduced_final_states__ = []
        for state in self.final_states:
            if state in accessible:
                self.__reduced_final_states__.append(state)

        # Keep only transitions between accessible states
        self.__reduced_rules__ = {}
        for key, next_state in self.rules.items():
            state, symbol = key
            if state in accessible and next_state in accessible:
                self.__reduced_rules__[(state, symbol)] = next_state

# Minor testing
if __name__ == "__main__":
    test_obj = DFA(
        alphabet=("a", "b"),
        states=tuple([f"q{x}" for x in range(8)]),
        initial_state="q0",
        final_states=("q5",),
        rules={
            ("q0", "a"): "q1",
            ("q0", "b"): "q2",
            ("q1", "a"): "q2",
            ("q1", "b"): "q3",
            ("q2", "a"): "q2",
            ("q2", "b"): "q3",
            ("q3", "a"): "q5",
            ("q3", "b"): "q4",
            ("q4", "a"): "q5",
            ("q4", "b"): "q3",
            ("q5", "a"): "q5",
            ("q5", "b"): "q5",
            ("q6", "a"): "q1",
            ("q6", "b"): "q7",
            ("q7", "a"): "q6",
            ("q7", "b"): "q4",
        },
    )
    # Procedure for reduction of number of states
    test_obj.remove_inaccessible_states()
    test_obj = test_obj.get_reduced_dfa()
    test_obj.mark()
    test_obj.reduce()
    reduced_test_obj = test_obj.get_reduced_dfa()
