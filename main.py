# This is the file you execute to start your application.

# It will:
# Initialize the database.
# Build the multi-agent graph.
# Generate a unique thread ID.
# Accept a customer question.
# Execute the graph.
# Handle human verification interruptions.
# Print the final response.

from uuid import uuid4

from langchain_core.messages import HumanMessage

from langgraph.types import Command

from database.chinook import initialize_database

from workflow.graph import multi_agent_graph


def run_application():

    # Initialize database
    initialize_database()

    # Create conversation thread
    thread_id = str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("\n===================================")
    print(" LANGGRAPH MULTI-AGENT CUSTOMER SUPPORT")
    print("===================================")

    print("\nType 'exit' to stop.\n")

    while True:

        question = input("\nCustomer: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        # Start graph
        result = multi_agent_graph.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            },
            config=config
        )

        # Handle human verification
        while "__interrupt__" in result:

            interrupt_data = result["__interrupt__"]

            for item in interrupt_data:
                print(
                    "\nVerification required:",
                    item.value
                )

            answer = input("\nCustomer: ").strip()

            result = multi_agent_graph.invoke(
                Command(resume=answer),
                config=config
            )

        # Display final response
        print("\nAssistant:")

        for message in result["messages"]:

            if message.type == "ai" and message.content:

                print(message.content)


if __name__ == "__main__":

    run_application()
