
from langchain.agents import create_agent

from utils.models import model

from workflow.state import State

from database.tools import invoice_tools

from langgraph.checkpoint.memory import MemorySaver


invoice_checkpointer = MemorySaver()


INVOICE_PROMPT = """
You are an Invoice Information Specialist.

You are responsible for customer invoice-related questions.

You can:

1. Retrieve customer invoices.
2. Find recent purchases.
3. Find invoice amounts.
4. Find invoice line items.
5. Identify employees associated with invoices.

You have access to invoice database tools.

The customer ID is available in the shared agent state.

Always use tools to retrieve invoice information.

Never invent invoice amounts or purchase details.

If no information is found, explain that clearly.

You are a sub-agent. Return a clear response to the supervisor.
"""


invoice_information_subagent = create_agent(
    model=model,

    tools=invoice_tools,

    name="invoice_information_subagent",

    system_prompt=INVOICE_PROMPT,

    state_schema=State,

    checkpointer=invoice_checkpointer
)
