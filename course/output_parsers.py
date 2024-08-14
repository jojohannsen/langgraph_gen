from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser, CommaSeparatedListOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


model = ChatOpenAI(model="gpt-4o-mini")

def call_string_output_parser(s):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tell me a joke about the following subject"),
        ("human", "{subject}")
    ])

    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    return chain.invoke(s)

def call_list_output_parser(s):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Give me a list of 3 synonyms for the following word as a comma separated list"),
        ("human", "{word}")
    ])
    output_parser = CommaSeparatedListOutputParser()
    chain = prompt | model | output_parser
    return chain.invoke(s)

def call_json_output_parser(s):
    class Person(BaseModel):
        name: str = Field(description="The name of the person")
        age: int = Field(description="The age of the person")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract information from the following text.  Use the following formatting instructions: {formatting_instructions}"),
        ("human", "{text}")
    ])
    output_parser = JsonOutputParser(pydantic_object=Person)
    chain = prompt | model | output_parser
    return chain.invoke({"text": s, "formatting_instructions": output_parser.get_format_instructions()})

# result = call_list_output_parser("happy")
# print(result)

result = call_json_output_parser("Bobby is 27 years old")
print(result)