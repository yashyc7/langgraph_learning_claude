"""
Build a ReAct agent with 2 tools:

get_stock_price(ticker: str) — fake data, return price for AAPL, TSLA, GOOGL
currency_converter(amount: float, from_currency: str, to_currency: str) — fake rates: 1 USD = 0.92 EUR = 83 INR

Test with:

"What is the price of AAPL stock?"
"Convert 100 USD to INR"
"What is TSLA stock price in EUR?"  ← agent must use both toolssummary_
"""
from  langchain_core.tools import tool
import requests
from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langgraph.graph import START,END,MessagesState,StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

load_dotenv()


API_KEY = os.getenv("CURRENCY_EXCHANGE_RATE_API_KEY","")

@tool
def get_stock_price(stock_name:str)->int:
    """This tool / function returns the stock price of the requested stock in USD.

    Args:
        stock_name (str): the stock_name which is sent as an input

    Returns:
        int: returns the value of the stock which is considered as in USD
    """
    stock_db = {
        "AAPL": 178.50,
        "TSLA": 245.30,
        "GOOGL": 140.75
    }

    return stock_db.get(stock_name.upper(),"Ticker not found")

@tool
def currency_converter(amount:float , from_currency : str = "USD" ,to_currency : str = "EUR" )->float:
    """
    This is the currency converter tool/function which is used to convert the currency from one to another . 
    eg amount 2.0 , 4.0 and 6.0 
    from_currency should be like "USD" 
    to_currency should be like "EUR"  

    Args:
        amount (float): amount to be converted 
        from_currency (str): from currency which you wanted to convert 
        to_currency (str): to currency which you wanted 
    Returns:
        float: returns the converted amount of the currency you requested 
    """


    data = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}")

    response = data.json()

    conversion_rate = response["conversion_rates"][f"{to_currency}"]

    return amount * conversion_rate

# 2 tools setup 

tools  = [currency_converter,get_stock_price]

llm = ChatOllama(model="qwen3.5:0.8b",
    temperature=0.2,)

llm_with_tools = llm.bind_tools(tools)


# making the nodes here 
def agent_node(state:MessagesState)->MessagesState:
    """LLM decides to call a tool or give the final answer """
    print(f"[AGENT] thinking...{state["messages"][-1]}")
    print(f"[AGENT] thinking... ({len(state['messages'])} messages in history)")
    response = llm_with_tools.invoke(state['messages'])
    return {"messages":[response]}


## tool node handles the tool executions automatically 

tool_node = ToolNode(tools)


# Routing function \

def should_continue(state:MessagesState)->str:
    """check if the llm wantes to call a tool or is done"""
    last_message = state["messages"][-1]

    if last_message.tool_calls : ##llm requested a tool 
        return "tools"  # name of the edge 
    return "end"


### build graph

def build_graph()->StateGraph:
    graph = StateGraph(MessagesState)

    graph.add_node("agent",agent_node) # is simply an llm 
    graph.add_node("tools",tool_node) # is simply the collection of tool  called tool node 

    # lets create the edges for this graph 
    graph.add_edge(START,"agent")
    graph.add_conditional_edges(

        "agent",
        should_continue,
        {
            "tools":"tools", # RETURN VALUE : NODE NAME 
            "end":END
        }
    )

    # After tools → always go back to agent (the loop)
    graph.add_edge("tools", "agent")

    return graph.compile()


# 6 run the graph

def run_query(app, query: str):
    print(f"\n── Query: '{query}' ──")
    result = app.invoke({"messages": [HumanMessage(content=query)]})
    final = result["messages"][-1].content
    print(f"Answer: {final}")


def main():
    app = build_graph()

    run_query(app, "What is the price of AAPL stock?")
    run_query(app, "Convert 100 USD to INR")
    run_query(app, "What is TSLA stock price in EUR?")


main()




# ── Query: 'What is the price of AAPL stock?' ──
# [AGENT] thinking...content='What is the price of AAPL stock?' additional_kwargs={} response_metadata={} id='a69e1002-1dda-46c9-8559-6d060206862f'
# [AGENT] thinking... (1 messages in history)
# [AGENT] thinking...content='2' name='get_stock_price' id='42632511-f422-4825-9e9b-d4c453aa1674' tool_call_id='4cb6f5e2-9d58-43b2-b356-971ba15d3854'
# [AGENT] thinking... (3 messages in history)
# Answer: The current price of AAPL is $2.

# ── Query: 'Convert 100 USD to INR' ──
# [AGENT] thinking...content='Convert 100 USD to INR' additional_kwargs={} response_metadata={} id='07d33bb7-4305-4137-9243-3892e033095d'
# [AGENT] thinking... (1 messages in history)
# [AGENT] thinking...content='9344.15' name='currency_converter' id='cc27c414-97ba-423e-a6e0-7a71fb0e9661' tool_call_id='7e312166-e96d-439a-b3b1-c8ff7b75f726'
# [AGENT] thinking... (3 messages in history)
# Answer: 100 USD is equivalent to **9344.15 INR**.

# ── Query: 'What is TSLA stock price in EUR?' ──
# [AGENT] thinking...content='What is TSLA stock price in EUR?' additional_kwargs={} response_metadata={} id='eab6e93f-cf8c-40ac-888f-e0aac4c9c628'
# [AGENT] thinking... (1 messages in history)
# [AGENT] thinking...content='4' name='get_stock_price' id='fcc39d4d-bc66-4e6b-b928-b3f12ae89d3d' tool_call_id='edc25cf2-6ccc-48e8-a789-04f95ed8611f'
# [AGENT] thinking... (3 messages in history)
# [AGENT] thinking...content='3.39' name='currency_converter' id='6a476d04-845e-4bf7-950b-21f872e42403' tool_call_id='50352b75-72c9-4e44-a9ce-dfaaf288cc62'
# [AGENT] thinking... (5 messages in history)
# Answer: The current stock price for TSLA (Tesla) in USD is $4. To convert this to EUR, the price is **3.39 EUR**.