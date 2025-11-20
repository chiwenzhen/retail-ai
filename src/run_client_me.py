import asyncio

from client import AgentClient
from core import settings
from schema import ChatMessage


# async def amain() -> None:
#     #### ASYNC ####
#     client = AgentClient('http://127.0.0.1:8080', agent='retail_agent')
#
#     print("Agent info:")
#     print(client.info)
#
#     print("Chat example:")
#     response = await client.ainvoke("中国第一个皇帝是谁?")
#     response.pretty_print()
#
#     print("\nStream example:")
#     async for message in client.astream("中国第一个皇帝是谁?"):
#         if isinstance(message, str):
#             print(message, flush=True, end="")
#         elif isinstance(message, ChatMessage):
#             print("\n", flush=True)
#             message.pretty_print()
#         else:
#             print(f"ERROR: Unknown type - {type(message)}")
#

def main() -> None:
    #### SYNC ####
    client = AgentClient('http://127.0.0.1:8080', agent='retail_agent')

    # print("Agent info:")
    # print(client.info)

    # print("Chat example:")
    # response = client.invoke("中国第一个皇帝是谁?", thread_id='user-123')
    # response.pretty_print()
    # response = client.invoke("他的父亲是谁?", thread_id='user-123')
    # response.pretty_print()

    print("\nStream example:")
    for message in client.stream("中国第一个皇帝是谁?", thread_id='user-123'):
        if isinstance(message, str):
            print(message, flush=True, end="")
        elif isinstance(message, ChatMessage):
            print("\n", flush=True)
            message.pretty_print()
        else:
            print(f"ERROR: Unknown type - {type(message)}")
    for message in client.stream("他的父亲是谁?", thread_id='user-123'):
        if isinstance(message, str):
            print(message, flush=True, end="")
        elif isinstance(message, ChatMessage):
            print("\n", flush=True)
            message.pretty_print()
        else:
            print(f"ERROR: Unknown type - {type(message)}")


if __name__ == "__main__":
    print("Running in sync mode")
    main()
    print("\n\n\n\n\n")
    # print("Running in async mode")
    # asyncio.run(amain())
