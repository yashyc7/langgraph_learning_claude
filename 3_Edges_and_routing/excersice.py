"""
Build a score-based router graph:

One grader node sets a score: int in state
Routing logic:

score >= 90 → excellent node
score >= 60 → pass node
score < 60 → fail node


Each outcome node prints a message and appends it to history
Test with 3 different scores: 95, 72, 45
"""
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from operator import add 
# 1 create the StateSchema 
class State(TypedDict):
    score : int
    output_node:str
    message:Annotated[list[str],add]


## defining the functions 

def grader_node(state:State)->State:
    """ Returns the node name that needs to be executed
    """
    if state['score'] >= 90:
        return {"output_node":"excellent","score":state['score'],"message":["Great you have excellent Score"]}
    elif state['score']>=60 and state['score'] <90:
        return {"output_node":"pass","score":state['score'],"message":["Hi you have Average Score"]}
    else : 
        return {"output_node":"fail","score":state['score'],"message":["Alas you have Poor Score"]}


def excellent_node(state:State)->State:
    print("Wow you have Outstanding Results")
    return {}

def pass_node(state:State)->State:
    print("uhmm You have average score")
    return {}

# ✅ correct
def fail_node(state: State) -> State:
    print("Alas you have failed")
    return {}      # nothing new to add — grader already added the message

## routing function 

def decide_node(state:State)->State:
    return state['output_node']


def build_graph()->StateGraph:
    graph = StateGraph(State)

    graph.add_node("grader",grader_node)
    graph.add_node("excellent",excellent_node)
    graph.add_node("pass",pass_node)
    graph.add_node("fail",fail_node)
    

    # adding edges now
    # entry point with grader 
    graph.add_edge(START,"grader")
    graph.add_conditional_edges(
        "grader",
        decide_node,
        {
            "excellent":"excellent",
            "pass":"pass",
            "fail":"fail",
        }
    )

    graph.add_edge("excellent",END)
    graph.add_edge("pass",END)
    graph.add_edge("fail",END)

    return graph.compile()


def main():
    app = build_graph()

    scores = [23,65,91]

    for score in scores:
        result = app.invoke({"score":score})
        print(result)

main()



# Alas you have failed
# {'score': 23, 'output_node': 'fail', 'message': ['Alas you have Poor Score']}
# uhmm You have average score
# {'score': 65, 'output_node': 'pass', 'message': ['Hi you have Average Score']}
# Wow you have Outstanding Results
# {'score': 91, 'output_node': 'excellent', 'message': ['Great you have excellent Score']}