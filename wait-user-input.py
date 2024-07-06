#!/usr/bin/env python
# coding: utf-8

# In[1]:


from graph_gen.gen_graph import gen_graph


# # How to wait for user input
# 
# One of the main human-in-the-loop interaction patterns is waiting for human input. A key use case involves asking the user clarifying questions. One way to accomplish this is simply go to the END node and exit the graph. Then, any user response comes back in as fresh invocation of the graph. This is basically just creating a chatbot architecture.
# 
# The issue with this is it is tough to resume back in a particular point in the graph. Often times the agent is halfway through some process, and just needs a bit of a user input. Although it is possible to design your graph in such a way where you have a `conditional_entry_point` to route user messages back to the right place, that is not super scalable (as it essentially involves having a routing function that can end up almost anywhere).
# 
# A separate way to do this is to have a node explicitly for getting user input. This is easy to implement in a notebook setting - you just put an `input()` call in the node. But that isn't exactly production ready.
# 
# Luckily, LangGraph makes it possible to do similar things in a production way. The basic idea is:
# 
# - Set up a node that represents human input. This can have specific incoming/outgoing edges (as you desire). There shouldn't actually be any logic inside this node.
# - Add a breakpoint before the node. This will stop the graph before this node executes (which is good, because there's no real logic in it anyways)
# - Use `.update_state` to update the state of the graph. Pass in whatever human response you get. The key here is to use the `as_node` parameter to apply this update **as if you were that node**. This will have the effect of making it so that when you resume execution next it resumes as if that node just acted, and not from the beginning.
# 
# **Note:** this requires passing in a checkpointer.
# 
# Below is a quick example.

# ## Setup
# 
# First we need to install the packages required

# In[1]:


get_ipython().run_cell_magic('capture', '--no-stderr', '%pip install --quiet -U langgraph langchain_anthropic\n')


# Next, we need to set API keys for Anthropic (the LLM we will use)

# In[2]:


import getpass
import os


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("ANTHROPIC_API_KEY")


# Optionally, we can set API key for [LangSmith tracing](https://smith.langchain.com/), which will give us best-in-class observability.

# In[3]:


os.environ["LANGCHAIN_TRACING_V2"] = "true"
_set_env("LANGCHAIN_API_KEY")


# ## Build the agent
# 
# We can now build the agent. We will build a relatively simple ReAct-style agent that does tool calling. We will use Anthropic's models and a fake tool (just for demo purposes).

# In[4]:


# Set up the state
from langgraph.graph import MessagesState, START

# Set up the tool
# We will have one real tool - a search tool
# We'll also have one "fake" tool - a "ask_human" tool
# Here we define any ACTUAL tools
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode


@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder for the actual implementation
    # Don't let the LLM know this though 😊
    return [
        f"I looked up: {query}. Result: It's sunny in San Francisco, but you better look out if you're a Gemini 😈."
    ]


tools = [search]
tool_node = ToolNode(tools)

# Set up the model
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-3-5-sonnet-20240620")


# We are going "bind" all tools to the model
# We have the ACTUAL tools from above, but we also need a mock tool to ask a human
# Since `bind_tools` takes in tools but also just tool definitions,
# We can define a tool definition for `ask_human`

from langchain_core.pydantic_v1 import BaseModel


class AskHuman(BaseModel):
    """Ask the human a question"""

    question: str


model = model.bind_tools(tools + [AskHuman])

# Define nodes and conditional edges

from langchain_core.messages import ToolMessage

from langgraph.prebuilt import ToolInvocation


# Define the function that calls the model
def call_model(state):
    messages = state["messages"]
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Build the graph
from langgraph.graph import END, StateGraph


# In[5]:


def no_tools(state):
    return not state["messages"][-1].tool_calls

def human_needed(state):
    return state["messages"][-1].tool_calls[0]["name"] == "AskHuman"

# the human node
def get_human_input(state):
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    tool_message = last_message.tool_calls[0]
    question = tool_message['args']['question']
    weather_place = input(question)
    tool_message = [
        {"tool_call_id": tool_call_id, "type": "tool", "content": weather_place}
    ]
    return { "messages": tool_message }

graph_spec = """

call_model(MessagesState)
   no_tools => END
   human_needed => get_human_input
   => tool_node

tool_node
   => call_model
   
get_human_input
   => call_model
   
"""

graph_code = gen_graph("wait_user_input", graph_spec)
print(graph_code)
exec(graph_code)


# In[6]:


from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "2"}}
input_message = HumanMessage(
    content="Use the search tool to ask the user where they are, then look up the weather there"
)
for event in wait_user_input.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()


# In[ ]:




