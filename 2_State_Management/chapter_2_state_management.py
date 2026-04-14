from typing import Annotated,TypedDict
from langgraph.graph import START,END,StateGraph
from operator import add 

###### 2 Custom reducer function 
# keep only unique items no duplicats

def keep_unique(existing:list,new:list)->list:
    return list(set(existing+new))



#### 1 state schema

class State(TypedDict):
    user:str
    score : int
    messages:Annotated[list[str],add] # reducer function is add here to append messages at the last 
    tags : Annotated[list[str],keep_unique] # custom reducer 



### defining nodes

def node_start(state:State)->State:
    print(f"[START NODE] user = {state['user']}")
    return {
        "messages":[f'Welcome {state['user']} !'],
        "tags":['started'],
        "score":0
    }

def node_action(state:State)->State:
    print(f"[ACTION NODE] score = {state['score']}")
    return {
        "messages":["Action Completed!"], # appended — not overwritten
        "tags":["started","action_done"], # started wouldn't be  duplicate it woule be overwritten due to the keep_unique reducer function 
        "score":state['score']+10
    }

def node_finish(state:State)->State:
    print(f"[FINISH_NODE final_score ={state['score']}]")
    return {
        "messages":[f"Done! Final Score: {state['score']}"],
        "tags":["finished"]
    }
    

# 4. build graph now 

def build_graph()->StateGraph:

    graph = StateGraph(State)

    graph.add_node("start",node_start)
    graph.add_node("action",node_action)
    graph.add_node("finish",node_finish)


    graph.add_edge(START,"start")
    graph.add_edge("start","action")
    graph.add_edge("action","finish")
    graph.add_edge("finish",END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({"user":"Yash","score":0,"messages":[],"tags":[]})
    print("\n── Final State ──")
    print(f"User:     {result['user']}")
    print(f"Score:    {result['score']}")
    print(f"Messages: {result['messages']}")
    print(f"Tags:     {result['tags']}")


main()


# [START NODE]  user=Yash
# [ACTION NODE] score=0, messages so far=['Welcome Yash!']
# [FINISH NODE] final score=10

# ── Final State ──
# User:     Yash
# Score:    10
# Messages: ['Welcome Yash!', 'Action completed.', 'Done! Final score: 10']
# Tags:     ['started', 'action_done', 'finished']   # no duplicates