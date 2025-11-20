from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, MessagesState, StateGraph
from typing import TypedDict, Literal
from langgraph.types import interrupt, Command, RetryPolicy

# Define the nodes
llm = init_chat_model(
    "qwen3-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
)

class UserIntent(TypedDict):
    intent: Literal["产品推荐", "产品问答", "其他"]

class UserProfile:
    age: int
    risk_grd: str

class UserBehavior:
    buy_lc_list: list[str]
    buy_jj_list: list[str]

class RetailAgentState(MessagesState):
    # 用户信息
    user_id: str
    user_profile: UserProfile
    query: str

    # 意图分类
    user_intent: UserIntent | None

    # 推荐产品
    rec_list: str

    # 对话消息
    messages: list[str] | None

def classify_intent(state: RetailAgentState):
    """使用LLM识别用户意图，并路由到不同下游节点"""

    # 创建带结构化输出的LLM
    structured_llm = llm.with_structured_output(UserIntent)

    # 意图识别prompt
    classify_intent_prompt = f"""
    请分析用户输入的Query，并对其做意图分类:
    Query: {state["messages"][-1].content}
    请提供用户的意图分类.
    """
    # Get structured response directly as dict
    user_intent = structured_llm.invoke(classify_intent_prompt)

    return {"user_intent": user_intent}

# 根据意图路由
def route_intent(state: RetailAgentState):
    return state["user_intent"].intent

# Define the chat node
def qa(state: RetailAgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Define the chat node
def rec(state: RetailAgentState):
    return {"rec_list": "产品列表\n1.product1\n2.product2\n3.product3"}

# Build and compile graph
builder = StateGraph(RetailAgentState)
builder.add_node("classify_intent", classify_intent)
builder.add_node("qa", qa)
builder.add_node("rec", rec)
builder.add_edge(START, "classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {  # Name returned by route_decision : Name of next node to visit
        "产品推荐": "rec",
        "产品问答": "qa",
        "其他": "qa",
    },
)
builder.add_edge("rec", END)
builder.add_edge("qa", END)
retail_agent = builder.compile()