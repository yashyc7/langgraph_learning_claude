# ─────────────────────────────────────────
# Chapter 4: Tool Calling & ReAct Agent
# ─────────────────────────────────────────

import os
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.state import CompiledStateGraph

# ── 1. DEFINE TOOLS ───────────────────────
# Docstring is critical — LLM uses it to decide when to call the tool

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression. Input must be a valid Python math expression.
    Examples: '2 + 2', '10 * 5', '100 / 4'
    """
    try:
        result = eval(expression)  # safe enough for learning purposes
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city.
    Examples: 'London', 'New York', 'Tokyo'
    """
    # Fake weather data — no API needed
    weather_db = {
        "london":   "Cloudy, 15°C, light rain",
        "new york": "Sunny, 22°C, clear skies",
        "tokyo":    "Humid, 28°C, partly cloudy",
        "paris":    "Sunny, 19°C, light breeze",
    }
    result = weather_db.get(city.lower(), f"No weather data for '{city}'")
    return f"Weather in {city}: {result}"


# ── 2. LLM + TOOLS SETUP ──────────────────
tools = [calculator, get_weather]

llm = ChatOllama(
    model="qwen3.5:0.8b",
    temperature=0.2,)

llm_with_tools = llm.bind_tools(tools)


# ── 3. NODES ──────────────────────────────

def agent_node(state: MessagesState) -> MessagesState:
    """LLM decides: call a tool OR give final answer."""
    print(f"[AGENT] thinking... ({len(state['messages'])} messages in history)")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ToolNode handles tool execution automatically
tool_node = ToolNode(tools)


# ── 4. ROUTING FUNCTION ───────────────────

def should_continue(state: MessagesState) -> str:
    last_msg = state["messages"][-1]

    if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
        return "tools"

    return "end"             # LLM gave final answer


# ── 5. BUILD GRAPH ────────────────────────

def build_graph() -> CompiledStateGraph:
    graph = StateGraph(MessagesState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    # Conditional: after agent → either call tools or end
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end":   END,
        }
    )

    # After tools → always go back to agent (the loop)
    graph.add_edge("tools", "agent")

    return graph.compile()


# ── 6. RUN ────────────────────────────────

def run_query(app, query: str):
    print(f"\n── Query: '{query}' ──")
    result = app.invoke({"messages": [HumanMessage(content=query)]})
    final = result["messages"][-1].content
    print(f"Answer: {final}")


def main():
    app = build_graph()

    run_query(app, "What is 1234 multiplied by 56?")
    run_query(app, "What is the weather in Tokyo?")
    run_query(app, "What is 100 divided by 4, and what's the weather in London?")


main()