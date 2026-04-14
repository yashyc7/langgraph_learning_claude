from typing import TypedDict
from langgraph.graph import StateGraph,START,END


### creating state this would be the input of the every nod e


class State(TypedDict):
    message:str


#### creating nodes which process data 

def node_input(state:State)->State:
    print(f"[INPUT NODE]   received: {state['message']}")
    return {"message":state["message"]}

def node_process(state:State)->State:
    processed = state['message'].upper()
    print(f"[PROCESSED_NODE] uppercased : {processed}")
    return {"message":processed}

def node_output(state:State)->State:
    print(f"[OUTPUT NODE] final:{state['message']}")
    return {"message":state["message"]}

# now building the graph 

def build_graph()->StateGraph:
    graph=StateGraph(State)

    # registering the nodes
    graph.add_node("input",node_input)
    graph.add_node("process",node_process)
    graph.add_node("output",node_output)

    #connect edges : START - input - > process -> output -> END

    graph.add_edge(START,"input")
    graph.add_edge("input","process")
    graph.add_edge("process","output")
    graph.add_edge("output",END)

    return graph.compile() # compile the state graph and return it 


    ## 4 . run the appliation 

def main():
    app = build_graph()

    # invoke the initial state 
    result = app.invoke({"message":"hello world"})

    print(f"\n Final State :{result}")
    
main()

# [INPUT NODE]   received: hello world
# [PROCESSED_NODE] uppercased : HELLO WORLD
# [OUTPUT NODE] final:HELLO WORLD

#  Final State :{'message': 'HELLO WORLD'}
