from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage,HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph,START,END,MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
# defining the tools 

@tool
def get_user_data(username:str)->str:
    """Fetch sensitive user data. Requires human approval before running."""
    return f"[SENSITIVE] Data for '{username}': email=user@example.com, balance=$5000"


tools = [get_user_data]


# ── 2. LLM + TOOLS SETUP ──────────────────

llm = ChatOllama(
    model="qwen3.5:0.8b",
    temperature=0.2,)

llm_with_tools = llm.bind_tools(tools)


# 3 Nodes agent node 

def agent_node(state: MessagesState) -> MessagesState:
    print(f"[AGENT] ({len(state['messages'])} messages in thread)")

    system_prompt = """You are a helpful assistant.
You MUST use the conversation history to answer questions about the user.
If the user asks what you know about them, summarize from previous messages.
"""

    response = llm_with_tools.invoke(
        [HumanMessage(content=system_prompt)] + state["messages"]
    )

    return {"messages": [response]}

tool_node = ToolNode(tools)

# 4 Routing 

def should_continue(state: MessagesState) -> str:
    last_msg = state["messages"][-1]

    if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
        return "tools"

    return "end"


#5 build graph
def build_graph(interrupt:bool = False)->CompiledStateGraph:
    memory = MemorySaver()
    graph=StateGraph(MessagesState)

    graph.add_node("agent",agent_node)
    graph.add_node("tools",tool_node)

    graph.add_edge(START,"agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools":"tools",
            "end":END
        }
    )
    # LOOPING AGAIN TO AGENT IN CASE RE CALLING OF TOOLS
    graph.add_edge("tools","agent")

    if interrupt:
        # Compile graph with checkpointing + pre-tool execution interrupt.
        # This pauses execution right before the "tools" node runs,
        # allowing an external system (e.g., human approval layer / audit / policy engine)
        # to inspect, approve, modify, or reject the tool call.
        # State is persisted via SqliteSaver, so execution can be safely resumed.
        return graph.compile(
            checkpointer=memory,
            interrupt_before=["tools"]
        )

    # Standard compilation with persistent state.
    # No interruption: agent → tools → agent loop runs autonomously.
    return graph.compile(checkpointer=memory)


def demo_memory():
    print("\n" + "="*50)
    print("DEMO A: Multi-turn Memory")
    print("="*50)
    app=build_graph()
    config:RunnableConfig = {"configurable":{"thread_id":"yash-thread"}}
    turns = [
        "Hi! My name is Yash and I am learning LangGraph.",
        "I am from India and I love building AI apps.",
        "What do you know about me so far?",   # agent should recall both facts
    ]
    for turn in turns:
        print(f"\nUser: {turn}")
        result = app.invoke({"messages": [HumanMessage(turn)]}, config=config)
        print(f"Agent: {result['messages'][-1].content}")

    # Different thread — completely isolated
    print("\n── Different thread (no memory) ──")
    other:RunnableConfig = {"configurable": {"thread_id": "stranger-thread"}}
    result = app.invoke({"messages": [HumanMessage("What do you know about me?")]}, config=other)
    print(f"Agent: {result['messages'][-1].content}")




# ── 7. MAIN ───────────────────────────────

def main():
    demo_memory()

main()