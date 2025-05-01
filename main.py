import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from lib.dfa import DFA

st.title("Deterministic Finite Accepter Simulator")

st.header("I. DFA Configuration", divider="red")

if "dfa_obj" not in st.session_state:
    st.session_state.dfa_obj = 0
if "dfa_graph_obj" not in st.session_state:
    st.session_state.dfa_graph_obj = 0
if "is_str_valid" not in st.session_state:
    st.session_state.is_str_valid = None
if "test_string" not in st.session_state:
    st.session_state.test_string = ""

# Pre-initialize default values to avoid conflict with callback function
for i in range(2):
    if f"symbol_{i}" not in st.session_state:
        st.session_state[f"symbol_{i}"] = str(i)

# Alphabet Configuration
st.markdown('<a id="alphabet_config"></a>', unsafe_allow_html=True)
st.subheader("1. Alphabet (Σ)")
symbol_cols = st.columns(2)


# When input symbol collides with one in the other box, delete the other
def symbol_collision_callback(i: int):
    if st.session_state[f"symbol_{i}"] == st.session_state[f"symbol_{(i+1)%2}"]:
        st.session_state[f"symbol_{(i+1)%2}"] = ""


# Create text inputs for symbols
for i, col in enumerate(symbol_cols):
    # Create text input field on each of the cols
    # Key param automatically adds this box to session state
    col.write(f"Symbol {i+1}")
    symbol = col.text_input(
        f"Symbol {i+1}",
        max_chars=1,
        placeholder=f"Enter symbol {i+1}",
        key=f"symbol_{i}",
        on_change=symbol_collision_callback,
        args=(i,),
        label_visibility="collapsed",
    )

# Raise warning for missing symbols
if any(not st.session_state[f"symbol_{i}"] for i in range(2)):
    st.warning("Incomplete alphabet", icon="⚠️")

# States Configuration
st.markdown('<a id="state_config"></a>', unsafe_allow_html=True)
st.subheader("2. States Configuration")

state_col1, state_col2 = st.columns(2)
state_col1.write(f"Number of States (|Q|)")
num_states = state_col1.number_input(
    "Number of States",
    min_value=1,
    max_value=16,
    value="min",
    step=1,
    key="num_states_input",
    label_visibility="collapsed",
)

state_col2.write(f"Initial State (q0)")
initial_state = state_col2.selectbox(
    "Initial State",
    options=[f"q{x}" for x in range(num_states)],
    key="initial_state_input",
    label_visibility="collapsed",
)

st.write(f"Final States (F)")
final_states = st.pills(
    "Final States",
    options=[f"q{x}" for x in range(num_states)],
    selection_mode="multi",
    default="q0",
    key="accept_states_input",
    label_visibility="collapsed",
)

if not final_states:
    st.warning("Must have at least 1 final state", icon="⚠️")

# Dynamic Transition Table
st.subheader("3. Transition Function (δ)")
st.write("Define where each state goes on each input symbol")

# Create columns with dynamic names
columns = {}
for i in range(2):
    symbol_name = st.session_state.get(f"symbol_{i}", f"Symbol_{i+1}")
    columns[symbol_name] = [f"q0" for _ in range(num_states)]

# Create a pandas DatatFrame for transitions
transition_df = pd.DataFrame(columns, index=[f"q{i}" for i in range(num_states)])

# Allow selection of output state for each transition
edited_df = st.data_editor(
    transition_df,
    column_config={
        symbol_name: st.column_config.SelectboxColumn(
            options=[f"q{i}" for i in range(num_states)],
            required=True,
        )
        for symbol_name in transition_df.columns
    },
    hide_index=False,
    key="transition_table",
)


# Convert the transition rules DataFrame into a Python dict
def df_to_transition_dict(df):
    transition_dict = {}
    # Iterate through all states (index) and symbols (columns)
    for state in df.index:
        for symbol in df.columns:
            next_state = df.at[state, symbol]
            # Skip empty cells if any
            if pd.notna(next_state):
                transition_dict[(state, symbol)] = next_state
    return transition_dict


# Function to be triggered when "Generate Graph" is clicked
def graph_callback(reduction=False):
    # Check if both symbols are provided
    # JS script to jump to anchor point
    # https://discuss.streamlit.io/t/programmatically-jump-to-anchor-on-same-page-after-clicking-button/81466/3
    if not st.session_state["symbol_0"] or not st.session_state["symbol_1"]:
        components.html(
            f"""
        <script>
            var element = window.parent.document.getElementById("alphabet_config");
            element.scrollIntoView({{behavior: 'smooth'}});
        </script>
        """.encode()
        )
        return
    # Check if there is at least a final state
    if not final_states:
        components.html(
            f"""
        <script>
            var element = window.parent.document.getElementById("state_config");
            element.scrollIntoView({{behavior: 'smooth'}});
        </script>
        """.encode()
        )
        return

    # Delete string validation callout if there's any left
    st.session_state.is_str_valid = None
    # Convert transition table into dictionary
    rules_dict = df_to_transition_dict(edited_df)
    dfa_obj = DFA(
        alphabet=(tuple(edited_df)),
        states=tuple([f"q{x}" for x in range(num_states)]),
        initial_state=initial_state,
        final_states=tuple(final_states),
        rules=rules_dict,
    )

    # Reduce DFA states if user clicks on appropriate button
    if reduction:
        dfa_obj.remove_inaccessible_states()
        # Confirm removal
        dfa_obj = dfa_obj.get_reduced_dfa()
        dfa_obj.mark()
        dfa_obj.reduce()
        st.session_state.dfa_obj = dfa_obj.get_reduced_dfa()
        st.session_state.dfa_graph_obj = st.session_state.dfa_obj.create_dfa()
    else:
        st.session_state.dfa_obj = dfa_obj
        st.session_state.dfa_graph_obj = dfa_obj.create_dfa()


graph_gen_col, reduced_graph_gen_col = st.columns([0.20, 0.80])
graph_gen_col.button(
    "Generate Graph", type="primary", on_click=graph_callback, key="submit_config"
)
reduced_graph_gen_col.button(
    "Generate Graph with reduced States",
    type="primary",
    on_click=graph_callback,
    args=(True,),
    key="submit_reduced_config",
)

st.header("II. DFA Visualization and Validation", divider="red")


# Validate and inform user of string validation
def validate(test_input: str):
    st.session_state.is_str_valid = st.session_state.dfa_obj.validate(test_input)
    st.session_state.dfa_graph_obj = st.session_state.dfa_obj.create_dfa(
        validation_trace=True
    )


def del_tracing():
    st.session_state.dfa_graph_obj = st.session_state.dfa_obj.create_dfa()


# Display the graph and validator with conditional layout
if "dfa_obj" in st.session_state and st.session_state.dfa_obj:
    # Get DFA graph and its properties
    graph_str = str(st.session_state.dfa_graph_obj)

    # Check graph's complexity
    # Larger graphs are more likely to be rectangles rather than squares
    num_nodes = len(st.session_state.dfa_obj.states)
    is_complex = num_nodes >= 5  # Arbitrary number tbh

    # Decide on layout based on graph complexity
    if is_complex:
        # For complex graphs, stack validator below graph
        st.subheader("DFA Visualization")
        st.graphviz_chart(graph_str, use_container_width=True)

        st.subheader("String Validation")
        test_string = st.text_input(
            "String validator",
            max_chars=16,
            placeholder="Enter a string to test",
            key="test_input",
            label_visibility="collapsed",
        )
        validate_button_col, reset_col = st.columns([0.13, 0.87])
        validate_button_col.button(
            "Validate",
            type="primary",
            on_click=validate,
            args=(st.session_state.test_input,),
            key="confirm_validation",
        )
        reset_col.button(
            "Remove graph tracing",
            type="secondary",
            on_click=del_tracing,
            key="del_tracing",
        )
    else:
        # For simpler graphs, use side-by-side layout
        validator_col, graph_col = st.columns([0.45, 0.55])

        with graph_col:
            st.subheader("DFA Visualization")
            st.graphviz_chart(graph_str, use_container_width=True)

        with validator_col:
            st.subheader("String Validation")
            test_string = st.text_input(
                "String validator",
                max_chars=16,
                placeholder="Enter a string to test",
                key="test_input",
                label_visibility="collapsed",
            )
            validate_button_col, reset_col = validator_col.columns([0.3, 0.7])
            validate_button_col.button(
                "Validate",
                type="primary",
                on_click=validate,
                args=(st.session_state.test_input,),
                key="confirm_validation",
            )
            reset_col.button(
                "Remove graph tracing",
                type="secondary",
                on_click=del_tracing,
                key="del_tracing",
            )
else:
    st.info(
        "Fill out the DFA configuration and generate a graph to begin testing strings.",
        icon="ℹ️",
    )

# Only show status when a validation attempt has taken place
if "is_str_valid" in st.session_state or st.session_state.is_str_valid is not None:
    # Check for types as well
    if st.session_state.is_str_valid is True:
        st.success("String is accepted", icon="✅")
    elif st.session_state.is_str_valid is False:
        st.error("String is rejected", icon="❌")
# Otherwise, show nothing
