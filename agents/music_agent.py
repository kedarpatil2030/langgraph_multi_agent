# This is the first specialist agent.
# Its responsibility is exclusively music-related requests.
# It uses:
# Music tools.
# System prompt.
# LLM.
# ToolNode.
# Conditional routing.
# LangGraph StateGraph.

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from workflow.state import State
from database.tools import music_tools
from utils.models import model

from langgraph.checkpoint.memory import MemorySaver


music_checkpointer = MemorySaver()

llm_with_tools = model.bind_tools(music_tools)

music_tool_node = ToolNode(music_tools)


MUSIC_PROMPT = """
You are a Music Catalog Specialist.

Your responsibility is to answer music-related questions.

You can help customers with:

1. Artists
2. Albums
3. Songs
4. Music genres
5. Music recommendations

Use the available database tools to retrieve accurate
information.

Do not invent songs, artists or albums.

If the catalog does not contain the requested information,
explain that clearly.

You are a sub-agent. Do not ask the customer follow-up
questions. Return a clear answer to the supervisor.

Previous customer preferences:
{memory}
"""


def music_assistant(state: State):

    memory = state.get("loaded_memory", "None")

    prompt = MUSIC_PROMPT.format(memory=memory)

    response = llm_with_tools.invoke(
        [
            SystemMessage(content=prompt)
        ] + state["messages"]
    )

    return {
        "messages": [response]
    }


def should_continue(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "continue"

    return "end"


def build_music_agent():

    workflow = StateGraph(State)

    workflow.add_node(
        "music_assistant",
        music_assistant
    )

    workflow.add_node(
        "music_tools",
        music_tool_node
    )

    workflow.add_edge(
        START,
        "music_assistant"
    )

    workflow.add_conditional_edges(
        "music_assistant",
        should_continue,
        {
            "continue": "music_tools",
            "end": END
        }
    )

    workflow.add_edge(
        "music_tools",
        "music_assistant"
    )

    return workflow.compile(
        checkpointer=music_checkpointer
    )


music_catalog_subagent = build_music_agent()
