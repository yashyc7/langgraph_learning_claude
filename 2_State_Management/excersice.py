"""
Build a graph that maintains a running message history across 3 nodes.
Requirements:

Each node appends its own message to the history
No node overwrites the previous messages
Add a step_count that increments by 1 in each node
Final state must show all 3 messages and step_count: 3

Hint: step_count is a plain field — each node reads current value and returns +1
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from operator import add


class State(TypedDict):
    message: Annotated[list[str], add]
    step_count: int


# add the nodes here


def start_node(state: State) -> State:
    print("[START NODE] start with count and increment it ")
    return {
        "message": ["Added 1 to step count final step count is 1 "],
        "step_count": state['step_count']+1,
    }

def middle_node(state:State)->State:
    print("[MIDDLE NODE] increment the count with one more")
    return {
        "message": ["Added 1 more to step count final step count is 2 "],
        "step_count": state['step_count']+1,
    }

def final_node(state:State)->State:
    print("[FINAL NODE] increment the count with one more")
    return {
        "message": ["Added 1 more to step count final step count is 3"],
        "step_count": state['step_count']+1,
    }


## 3 build graph function 
def build_graph()->StateGraph:
    graph = StateGraph(State)

    graph.add_node("start",start_node)
    graph.add_node("middle",middle_node)
    graph.add_node("final",final_node)
    
    
    graph.add_edge(START,"start")
    graph.add_edge("start","middle")
    graph.add_edge("middle","final")
    graph.add_edge("final",END)

    return graph.compile()



def main():

    app = build_graph()

    result = app.invoke({"message":[],"step_count":0})

    print(result)

    print(f"message->{result['message']}")
    print(f"step count ->{result['step_count']}")

main()

# [START NODE] start with count and increment it 
# [MIDDLE NODE] increment the count with one more
# [FINAL NODE] increment the count with one more
# {'message': ['Added 1 to step count final step count is 1 ', 'Added 1 more to step count final step count is 2 ', 'Added 1 more to step count final step count is 3'], 'step_count': 3}
# message->['Added 1 to step count final step count is 1 ', 'Added 1 more to step count final step count is 2 ', 'Added 1 more to step count final step count is 3']
# step count ->3