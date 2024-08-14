from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("Tell me a joke about {subject}")

llm = ChatOpenAI(model="gpt-4o-mini")
# response = llm.invoke("Tell me a joke about chickens")
# print(response)

# chain = prompt | llm
# result = chain.invoke("dogs")
# print(result.content)
# result = chain.invoke({"subject": "cats"})
# print(result.content)

another_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a mathematician poet, and when given an input, you make up a mathematical poem about it."),
    ("human", "{input}")
])

chain2 = another_prompt | llm
result = chain2.invoke("giraffe")
print(result.content)