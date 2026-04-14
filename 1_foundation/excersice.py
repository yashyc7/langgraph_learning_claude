"""Build a 3-node linear graph:
Input → Process → Output
The Process node must:

Uppercase the input string
Count its characters

Final state should have both — the uppercased string AND the character count.
Hint: you'll need to add a char_count: int field to your State.
    """


from typing import TypedDict
from langgraph.graph import StateGraph,START,END


class State(TypedDict):
    text : str 
    count : int

# adding nodes here 

def input_node(state:State)->State:
    print(f"[INPUT NODE] received data {state['text']}")
    return {"text":state['text'],'count':state['count']}

def process_node(state:State)->State:
    uppercased = state['text'].upper()
    total_chars = 0 
    for i in range(len(state['text'])):
        total_chars = total_chars + 1
    
    print(f"[PROCESS NODE] processed  data {state['text']} and count {state['count']}")
    return {"text":uppercased,"count":total_chars}

def output_node(state:State)->State:
    print(f"[OUTPUT NODE] received  data {state['text']} and count {state['count']}")
    return {"text":state['text'],'count':state['count']}


def build_graph()->StateGraph:
    graph = StateGraph(State)

    # adding the nodes now 

    graph.add_node("input",input_node)
    graph.add_node("process",process_node)
    graph.add_node("output",output_node)

    # add edges 
    graph.add_edge(START,"input")
    graph.add_edge("input","process")
    graph.add_edge("process","output")
    graph.add_edge("output",END)

    return graph.compile()


def main ():
    app = build_graph()

    result = app.invoke({"text":"Yash Chauhan","count":0})

    print(result)

main()