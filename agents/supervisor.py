# This is the most important component of the multi-agent architecture.
# The supervisor does not directly retrieve music or invoice data.

# Instead, it delegates tasks to specialist agents.
# Supervisor responsibilities
# Understand customer questions.
# Identify the correct specialist.
# Invoke the appropriate sub-agent.
# Invoke multiple agents when required.
# Combine their responses.
# Return a final answer

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

from langchain_core.messages import HumanMessage

from utils.models import model
from workflow.state import State

from agents.music_agent import music_catalog_subagent

from agents.invoice_agent import (
    invoice_information_subagent
)


# ==========================================
# SUPERVISOR PROMPT
# ==========================================

SUPERVISOR_PROMPT = """
You are the Supervisor Agent of a digital music store.

You manage a team of specialist AI agents.

You have two specialist agents:

1. Music Catalog Agent
   - Handles artists
   - Albums
   - Songs
   - Genres
   - Music recommendations

2. Invoice Information Agent
   - Handles invoices
   - Purchases
   - Billing
   - Customer transaction history

Your responsibilities:

1. Understand the customer request.
2. Identify which specialist is required.
3. Delegate the task to the appropriate agent.
4. You can call multiple specialists for one request.
5. Combine the results into one clear answer.

Do not invent information.

For unrelated questions, politely explain your scope.

Always respond with a summarized final answer.
"""


# ==========================================
# MUSIC SUBAGENT TOOL
# ==========================================

@tool
def call_music_catalog_subagent(query: str):
    """
    Delegate music-related requests to the Music Agent.
    """

    result = music_catalog_subagent.invoke(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        }
    )

    return result["messages"][-1].content


# ==========================================
# INVOICE SUBAGENT TOOL
# ==========================================

@tool
def call_invoice_information_subagent(
    runtime: ToolRuntime,
    query: str
):
    """
    Delegate invoice-related requests to the Invoice Agent.
    """

    customer_id = runtime.state.get("customer_id")

    if customer_id is None:
        return "Customer verification is required."

    result = invoice_information_subagent.invoke(
        {
            "messages": [
                HumanMessage(content=query)
            ],
            "customer_id": customer_id
        }
    )

    return result["messages"][-1].content


# ==========================================
# SUPERVISOR AGENT
# ==========================================

supervisor = create_agent(

    model=model,

    tools=[
        call_music_catalog_subagent,
        call_invoice_information_subagent
    ],

    name="supervisor",

    system_prompt=SUPERVISOR_PROMPT,

    state_schema=State
)
