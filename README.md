### langgraph_gen
Slightly modified examples from langgraph, all graph code for nodes/edges generated.

Nodes mostly unchanged, take 'state' parameter.

Conditional edges simplified, edge traversal determined by boolean function that takes 'state' as parameter.

### human-in-loop.ipynb
  
```python
  graph_spec = """
   
call_model(AgentState)
    should_call_tool => ask_human_approval
    
ask_human_approval
    human_allows_tool_call => call_tool
    
call_tool
    => call_model

"""
```

![Human-in-the-loop](human-in-loop.png)