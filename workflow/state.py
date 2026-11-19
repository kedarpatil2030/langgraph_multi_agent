
from typing import Optional
from typing_extensions import TypedDict, NotRequired

from langgraph.graph import MessagesState


class State(MessagesState):

    customer_id: NotRequired[Optional[int]]

    phone_number: NotRequired[Optional[str]]

    verified: NotRequired[bool]

    loaded_memory: NotRequired[str]


class InputState(MessagesState):
    pass
