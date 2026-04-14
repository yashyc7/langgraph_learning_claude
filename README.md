## LangGraph Learning Curriculum

### Chapter 1 — Foundations
- What is LangGraph & why it exists (vs LangChain)
- Graphs, Nodes, Edges — the mental model
- State — the backbone of everything
- Your first graph: Hello World
- **Exercise:** Build a 3-node linear graph: Input → Process → Output that uppercases a string and counts its characters

---

### Chapter 2 — State Management
- TypedDict state schema
- State reducers (how state updates work)
- Passing state between nodes
- Annotated state & custom reducers
- **Exercise:** Build a graph that maintains a running message history list — each node appends to it without overwriting previous messages

---

### Chapter 3 — Edges & Routing
- Normal edges
- Conditional edges
- Entry & finish points
- Building a decision-making graph
- **Exercise:** Build a sentiment router — if input is positive route to a "celebrate" node, if negative route to a "console" node, if neutral route to a "inform" node

---

### Chapter 4 — Tool Calling & ReAct Agent
- Binding tools to LLM
- ToolNode
- Building a ReAct loop from scratch
- Handling tool errors
- **Exercise:** Build a ReAct agent with 2 tools: a calculator and a weather faker — agent should decide which tool to call based on the user query

---

### Chapter 5 — Memory & Persistence
- Checkpointers (in-memory & SQLite)
- Short-term memory (thread-level)
- Long-term memory (cross-thread)
- Human-in-the-loop with interrupts
- **Exercise:** Build a chat agent that remembers conversation across multiple turns using a checkpointer, and pauses for human approval before answering sensitive questions

---

### Chapter 6 — Multi-Agent Systems
- Subgraphs
- Supervisor pattern
- Handoffs between agents
- Shared vs isolated state
- **Exercise:** Build a supervisor agent that routes tasks to two specialized sub-agents: a "researcher" and a "writer" — supervisor decides who handles the user request

---

### Chapter 7 — Production Patterns
- Streaming (tokens, events, state)
- Error handling & retries
- Async graphs
- LangGraph with FastAPI
- **Exercise:** Wrap your ReAct agent from Chapter 4 in a FastAPI endpoint that streams the response token by token to the client

---

### Chapter 8 — Advanced
- Dynamic graph modification
- Map-reduce patterns
- LangGraph Platform / Studio
- Real-world project end-to-end
- **Exercise:** Build an end-to-end research assistant — takes a topic, fans out to 3 parallel researcher nodes, collects results, and a writer node produces a final report

---

