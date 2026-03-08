from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.agent.tools import all_tools
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator, os, json

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")
llm_with_tools = llm.bind_tools(all_tools)

SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
You help sales reps log and manage interactions with Healthcare Professionals (HCPs).
Tools available:
1. log_interaction - Log new HCP interaction from natural language
2. edit_interaction - Edit existing interaction by ID
3. get_interaction_history - Get past interactions with an HCP
4. suggest_followup_actions - Suggest next steps after a meeting
5. analyze_sentiment_trend - Analyze sentiment trend for an HCP
Be helpful, concise and professional."""

def agent_node(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

tool_node = ToolNode(all_tools)
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)
graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges("agent", should_continue)
graph_builder.add_edge("tools", "agent")
agent_graph = graph_builder.compile()

def run_agent(message: str, conversation_history: list = []) -> dict:
    messages = []
    for msg in conversation_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    result = agent_graph.invoke({"messages": messages})
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    last_response = ai_messages[-1].content if ai_messages else "Could not process request."

    extracted_data = None
    for msg in result["messages"]:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                data = json.loads(msg.content)
                if "extracted_data" in data:
                    extracted_data = data["extracted_data"]
                    break
            except:
                pass

    return {"message": last_response, "extracted_data": extracted_data}