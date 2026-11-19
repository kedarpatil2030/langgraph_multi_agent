
from langgraph.graph import StateGraph, START, END

from langgraph.checkpoint.memory import MemorySaver

from langgraph.store.memory import InMemoryStore

from workflow.state import State, InputState

from workflow.verification import (
    verify_info,
    human_input,
    should_interrupt
)

from workflow.memory import (
    load_memory,
    create_memory
)

from agents.supervisor import supervisor


# ==========================================
# MEMORY AND CHECKPOINT STORAGE
# ==========================================

checkpointer = MemorySaver()

in_memory_store = InMemoryStore()


# ==========================================
# BUILD MAIN GRAPH
# ==========================================

def build_multi_agent_graph():

    workflow = StateGraph(
        State,
        input_schema=InputState
    )

    # Add nodes

    workflow.add_node(
        "verify_info",
        verify_info
    )

    workflow.add_node(
        "human_input",
        human_input
    )

    workflow.add_node(
        "load_memory",
        load_memory
    )

    workflow.add_node(
        "supervisor",
        supervisor
    )

    workflow.add_node(
        "create_memory",
        create_memory
    )

    # Start

    workflow.add_edge(
        START,
        "verify_info"
    )

    # Verification routing

    workflow.add_conditional_edges(
        "verify_info",
        should_interrupt,
        {
            "continue": "load_memory",
            "interrupt": "human_input"
        }
    )

    # Human input loop

    workflow.add_edge(
        "human_input",
        "verify_info"
    )

    # Load preferences

    workflow.add_edge(
        "load_memory",
        "supervisor"
    )

    # Supervisor execution

    workflow.add_edge(
        "supervisor",
        "create_memory"
    )

    # Final response

    workflow.add_edge(
        "create_memory",
        END
    )

    return workflow.compile(
        checkpointer=checkpointer,
        store=in_memory_store
    )


multi_agent_graph = build_multi_agent_graph()
