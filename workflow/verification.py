
from langchain_core.messages import AIMessage

from langgraph.types import interrupt

from database.chinook import execute_query


def verify_info(state):

    # Already verified
    if state.get("customer_id") is not None:
        return {
            "verified": True
        }

    phone_number = state.get("phone_number")

    if not phone_number:
        return {
            "verified": False
        }

    query = """
        SELECT CustomerId
        FROM Customer
        WHERE Phone = ?
    """

    result = execute_query(
        query,
        (phone_number,)
    )

    if result:

        customer_id = result[0]["CustomerId"]

        return {
            "customer_id": customer_id,
            "verified": True,
            "messages": [
                AIMessage(
                    content="Your account has been verified successfully."
                )
            ]
        }

    return {
        "phone_number": None,
        "verified": False,
        "messages": [
            AIMessage(
                content="I could not verify that phone number. Please try again."
            )
        ]
    }


def human_input(state):

    user_phone = interrupt(
        {
            "message": "Please enter your registered phone number."
        }
    )

    return {
        "phone_number": user_phone
    }


def should_interrupt(state):

    if state.get("customer_id") is not None:
        return "continue"

    if state.get("verified"):
        return "continue"

    return "interrupt"
