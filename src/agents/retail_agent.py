import logging
from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, MessagesState, StateGraph
from typing import TypedDict, Literal
from langgraph.types import interrupt, Command, RetryPolicy
logger = logging.getLogger(__name__)

# Define the nodes
llm = init_chat_model(
    "qwen3-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
)

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
    user_intent: str

    # 推荐产品
    rec_list: str

def classify_intent(state: RetailAgentState) -> Command[Literal["qa", "rec"]]:
    print(f"running classify_intent")

    # 意图识别prompt
    classify_intent_prompt = f"""
    请分析用户输入的Query，将其意图分类到这三类：产品推荐、产品问答、其他。只需要输出这三个类别之一，不得输出其他内容。
    Query: {state["messages"][-1].content}
    """
    logger.info(f"classify_intent_prompt= {classify_intent_prompt}")
    # Get structured response directly as dict
    user_intent = llm.invoke(classify_intent_prompt)
    logger.info(f"user_intent= {user_intent}")
    if user_intent == "产品推荐":
        goto = "rec"
    elif user_intent == "产品问答":
        goto = "qa"
    elif user_intent == "其他":
        goto = "qa"
    else:
        goto = "qa"
    return Command(
        update={"user_intent": user_intent},
        goto=goto
    )

# 根据意图路由
def route_intent(state: RetailAgentState):
    print(f"running route_intent")
    return state["user_intent"]

# Define the chat node
def qa(state: RetailAgentState):
    print(f"running qa")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Define the chat node
def rec(state: RetailAgentState):
    print(f"running rec")
    response = "产品列表\n1.product1\n2.product2\n3.product3"
    return {"rec_list": response, "messages": [response]}

# Build and compile graph
builder = StateGraph(RetailAgentState)
builder.add_node("classify_intent", classify_intent)
builder.add_node("qa", qa)
builder.add_node("rec", rec)
builder.add_edge(START, "classify_intent")
builder.add_edge("rec", END)
builder.add_edge("qa", END)
retail_agent = builder.compile()