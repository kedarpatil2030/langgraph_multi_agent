
from pydantic import BaseModel, Field

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from langgraph.store.base import BaseStore

from utils.models import model


# ==========================================
# MEMORY DATA MODEL
# ==========================================

class UserProfile(BaseModel):

    customer_id: str = Field(
        description="Customer identifier"
    )

    music_preferences: list[str] = Field(
        default_factory=list,
        description="Customer music preferences"
    )


# ==========================================
# LOAD MEMORY
# ==========================================

def load_memory(state, store: BaseStore):

    customer_id = str(state["customer_id"])

    namespace = (
        "memory_profile",
        customer_id
    )

    existing_memory = store.get(
        namespace,
        "user_memory"
    )

    formatted_memory = "No saved preferences."

    if existing_memory:

        profile = existing_memory.value["memory"]

        preferences = profile.get(
            "music_preferences",
            []
        )

        if preferences:
            formatted_memory = (
                "Music Preferences: "
                + ", ".join(preferences)
            )

    return {
        "loaded_memory": formatted_memory
    }


# ==========================================
# CREATE MEMORY
# ==========================================

MEMORY_PROMPT = """
You are a customer preference extraction agent.

Analyze the conversation.

Identify music preferences explicitly shared
by the customer.

Update the existing customer profile.

Do not invent preferences.

Preserve existing preferences unless new
information is provided.

Return a structured UserProfile.
"""


def create_memory(state, store: BaseStore):

    customer_id = str(state["customer_id"])

    namespace = (
        "memory_profile",
        customer_id
    )

    existing = store.get(
        namespace,
        "user_memory"
    )

    old_preferences = []

    if existing:

        old_preferences = existing.value[
            "memory"
        ].get("music_preferences", [])

    messages = state["messages"]

    structured_model = model.with_structured_output(
        UserProfile
    )

    updated_profile = structured_model.invoke(
        [
            SystemMessage(content=MEMORY_PROMPT),

            HumanMessage(
                content=(
                    f"Customer ID: {customer_id}\n"
                    f"Existing preferences: {old_preferences}\n"
                    f"Conversation: {messages}"
                )
            )
        ]
    )

    preferences = list(
        dict.fromkeys(
            old_preferences +
            updated_profile.music_preferences
        )
    )

    profile = UserProfile(
        customer_id=customer_id,
        music_preferences=preferences
    )

    store.put(
        namespace,
        "user_memory",
        {
            "memory": profile.model_dump()
        }
    )

    return {
        "loaded_memory": (
            "Music Preferences: "
            + ", ".join(preferences)
        )
    }
