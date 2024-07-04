import datetime
import inspect
import json
import operator
from collections import defaultdict

from langchain import hub
from langchain.agents import create_openai_functions_agent, create_react_agent, AgentExecutor
from langchain.chains.openai_functions import create_structured_output_runnable
from langchain.chains.structured_output import create_openai_fn_runnable
from langchain.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser
)
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AIMessage, BaseMessage, FunctionMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai.chat_models import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# State
from langchain_core.pydantic_v1 import BaseModel, Field, ValidationError, validator

# Tools
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langsmith import traceable
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation

# for agent state, pattern matching
from typing import Annotated, Dict, List, Optional, TypedDict, Tuple, Sequence, Union, Literal
import re

from langgraph.graph import END, StateGraph, MessageGraph
from langgraph.graph.message import AnyMessage, add_messages

# for going direct to openai without involving langchain
from openai import OpenAI