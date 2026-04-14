from typing import TypedDict,Annotated
from operator import add
from langgraph.graph import StateGraph,START,END


## state

class State(TypedDict):
    text : str
    sentiment:str # set by the classifier node
    messages : Annotated[list[str],add] # accumulates accross nodes


# nodes


def classifier_node(state:State)->State:
    """Decides sentiment based on the keywords
    """

    text = state['text'].lower()

    if any(w in text for w in ["happy", "great", "love", "awesome", "good"]):
        sentiment = "positive sentiment"
    elif any(w in text for w in ["sad", "bad", "hate", "terrible", "awful"]):
        sentiment = "negative sentiment"
    else:
        sentiment = "neutral sentiment"

    print(f"[CLASSIFIER] text='{state['text']}' → sentiment={sentiment}")
    return {"sentiment": sentiment, "messages": [f"Classified as: {sentiment}"]}


def positive_node(state:State)->State:
    print("[POSTIVE NODE]")
    return {"messages":["Thats awesome ! keep up the pace"]}


def negative_node(state:State)->State:
    print("[NEGATIVE NODE]")
    return {"messages":["That sounds tough. Things will get better!"]}


def neutral_node(state: State) -> State:
    print("[NEUTRAL NODE] 📢 Informing...")
    return {"messages": ["Thanks for sharing. Here's what I know about that."]}


# 3 ROUTING FUNCTION 
def route_by_sentiment(state:State)->str:
    return state["sentiment"]


#4 build the graph now 
def build_graph()->StateGraph:
    graph = StateGraph(State)

    # register nodes now 

    graph.add_node("classifier",classifier_node)
    graph.add_node("positive",positive_node)
    graph.add_node("negative",negative_node)
    graph.add_node("neutral",neutral_node)

    # entry point 
    graph.add_edge(START,"classifier")

    # conditional routing from classifier 
    graph.add_conditional_edges(
        "classifier" , # starting node 
        route_by_sentiment,
        {
            "positive sentiment":"positive", #return value -> node
            "negative sentiment":"negative",
            "neutral sentiment":"neutral" 
        }

    )

    # all three outcomes meet to an end 

    graph.add_edge("positive",END)
    graph.add_edge("negative",END)
    graph.add_edge("neutral",END)

    return graph.compile()

# ── 5. RUN ────────────────────────────────
def main():
    app = build_graph()

    test_inputs = [
        "I love this! It's awesome!",
        "This is terrible and I hate it",
        "The weather is cloudy today",
    ]

    for text in test_inputs:
        print(f"\n── Input: '{text}' ──")
        result = app.invoke({"text": text, "sentiment": "", "messages": []})
        print(f"Messages: {result['messages']}")


main()


# ── Input: 'I love this! It's awesome!' ──
# [CLASSIFIER] text='I love this! It's awesome!' → sentiment=positive sentiment
# [POSTIVE NODE]
# Messages: ['Classified as: positive sentiment', 'Thats awesome ! keep up the pace']

# ── Input: 'This is terrible and I hate it' ──
# [CLASSIFIER] text='This is terrible and I hate it' → sentiment=negative sentiment
# [NEGATIVE NODE]
# Messages: ['Classified as: negative sentiment', 'That sounds tough. Things will get better!']

# ── Input: 'The weather is cloudy today' ──
# [CLASSIFIER] text='The weather is cloudy today' → sentiment=neutral sentiment
# [NEUTRAL NODE] 📢 Informing...
# Messages: ['Classified as: neutral sentiment', "Thanks for sharing. Here's what I know about that."]