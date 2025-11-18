from langchain.chat_models import init_chat_model
from langgraph.graph import START, MessagesState, StateGraph

# Define the nodes
model = init_chat_model(
    "qwen3-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
)

# Define the chat node
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# Build and compile graph
builder = StateGraph(MessagesState)
builder.add_node("chat", call_model)
builder.add_edge(START, "chat")
rec_agent = builder.compile()