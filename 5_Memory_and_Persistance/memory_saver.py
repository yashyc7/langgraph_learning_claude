from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig


# ─────────────────────────────────────────
# 1. TOOL DEFINITION
# ─────────────────────────────────────────

@tool
def get_user_data(username: str) -> str:
    """Fetch sensitive user data. Requires human approval before running."""
    return f"[SENSITIVE] Data for '{username}': email=user@example.com, balance=$5000"


tools = [get_user_data]


# ─────────────────────────────────────────
# 2. LLM SETUP
# ─────────────────────────────────────────

llm = ChatOllama( model="qwen3.5:0.8b", temperature=0.2,)

llm_with_tools = llm.bind_tools(tools)


# ─────────────────────────────────────────
# 3. AGENT NODE
# ─────────────────────────────────────────

def agent_node(state: MessagesState) -> MessagesState:
    print(f"\n[AGENT] ({len(state['messages'])} messages in thread)")

    system_prompt = """You are a security-critical assistant.

RULES:
- If the user asks for ANY sensitive data, you MUST call the tool `get_user_data`.
- NEVER respond with sensitive data directly.
- NEVER skip tool usage.
- ONLY respond via tool call when sensitive data is requested.
"""

    response = llm_with_tools.invoke(
        [SystemMessage(content=system_prompt)] + state["messages"]
    )

    # Debug logs (observability)
    print("[DEBUG] LLM Response:", response)
    print("[DEBUG] Tool Calls:", getattr(response, "tool_calls", None))

    return {"messages": [response]}


# ─────────────────────────────────────────
# 4. TOOL NODE
# ─────────────────────────────────────────

tool_node = ToolNode(tools)


# ─────────────────────────────────────────
# 5. ROUTING LOGIC
# ─────────────────────────────────────────

def should_continue(state: MessagesState) -> str:
    last_msg = state["messages"][-1]

    if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
        return "tools"

    return "end"


# ─────────────────────────────────────────
# 6. GRAPH BUILDER
# ─────────────────────────────────────────

def build_graph(interrupt: bool = False) -> CompiledStateGraph:
    memory = MemorySaver()
    graph = StateGraph(MessagesState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    graph.add_edge("tools", "agent")

    if interrupt:
        return graph.compile(
            checkpointer=memory,
            interrupt_before=["tools"],  # pause before tool execution
        )

    return graph.compile(checkpointer=memory)


# ─────────────────────────────────────────
# 7. HUMAN-IN-THE-LOOP FLOW
# ─────────────────────────────────────────

def demo_interrupt():
    print("\n" + "=" * 50)
    print("DEMO: Human Approval (interrupt)")
    print("=" * 50)

    app = build_graph(interrupt=True)

    config: RunnableConfig = {
        "configurable": {"thread_id": "interrupt-thread"}
    }

    query = "Get sensitive data for username 'yash123'"
    print(f"\nUser: {query}")

    # Step 1: Run until interrupt
    app.invoke({"messages": [HumanMessage(content=query)]}, config=config)

    # Step 2: Inspect state
    state = app.get_state(config)
    pending_node = state.next

    print(f"\n[PAUSED] At node: {pending_node}")

    last_msg = state.values["messages"][-1]

    # 🛑 SAFETY CHECK (critical)
    if not getattr(last_msg, "tool_calls", None):
        raise RuntimeError(
            "LLM did not generate a tool call. Try a better model or stronger prompt."
        )

    tool_call = last_msg.tool_calls[0]

    print(f"[PAUSED] Tool: {tool_call['name']}")
    print(f"[PAUSED] Args: {tool_call['args']}")

    # Step 3: Human approval
    approval = input("\nApprove? (yes/no): ").strip().lower()

    if approval == "yes":
        print("[APPROVED] Resuming execution...")
        result = app.invoke(None, config=config)  # resume execution
        print(f"\nAgent: {result['messages'][-1].content}")
    else:
        print("[DENIED] Tool execution blocked.")


# ─────────────────────────────────────────
# 8. MAIN
# ─────────────────────────────────────────

def main():
    demo_interrupt()


if __name__ == "__main__":
    main()



    
# ==================================================
# DEMO: Human Approval (interrupt)
# ==================================================

# User: Get sensitive data for username 'yash123'

# [AGENT] (1 messages in thread)
# [DEBUG] LLM Response: content='' additional_kwargs={} response_metadata={'model': 'qwen3.5:0.8b', 'created_at': '2026-04-16T17:42:54.9098008Z', 'done': True, 'done_reason': 'stop', 'total_duration': 30313051500, 'load_duration': 362402200, 'prompt_eval_count': 348, 'prompt_eval_duration': 8061956600, 'eval_count': 118, 'eval_duration': 21630030700, 'logprobs': None, 'model_name': 'qwen3.5:0.8b', 'model_provider': 'ollama'} id='lc_run--019d9763-0e4e-7810-a615-0c94c6d62416-0' tool_calls=[{'name': 'get_user_data', 'args': {'username': 'yash123'}, 'id': '0b0c958d-92b2-4624-99c9-c2e82e1df776', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 348, 'output_tokens': 118, 'total_tokens': 466}
# [DEBUG] Tool Calls: [{'name': 'get_user_data', 'args': {'username': 'yash123'}, 'id': '0b0c958d-92b2-4624-99c9-c2e82e1df776', 'type': 'tool_call'}]

# [PAUSED] At node: ('tools',)
# [PAUSED] Tool: get_user_data
# [PAUSED] Args: {'username': 'yash123'}

# Approve? (yes/no): yes
# [APPROVED] Resuming execution...

# [AGENT] (3 messages in thread)
# [DEBUG] LLM Response: content="Here is the sensitive data for 'yash123':\n- Email: user@example.com\n- Balance: $5000" additional_kwargs={} response_metadata={'model': 'qwen3.5:0.8b', 'created_at': '2026-04-16T17:47:59.1459484Z', 'done': True, 'done_reason': 'stop', 'total_duration': 17092844900, 'load_duration': 1215917000, 'prompt_eval_count': 419, 'prompt_eval_duration': 10397696900, 'eval_count': 32, 'eval_duration': 5387374500, 'logprobs': None, 'model_name': 'qwen3.5:0.8b', 'model_provider': 'ollama'} id='lc_run--019d9767-e660-7512-99ec-1d73a657e5b9-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 419, 'output_tokens': 32, 'total_tokens': 451}
# [DEBUG] Tool Calls: []

# Agent: Here is the sensitive data for 'yash123':
# - Email: user@example.com
# - Balance: $5000