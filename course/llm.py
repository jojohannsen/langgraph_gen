from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, verbose=True)

response = llm.invoke("Hello, how are you?")
print(response)

response = llm.batch(["What is 3*4", "Who is Johnny Rocket?"])
print(len(response))
for r in response:
    print("RESPONSE: ", r)

from typing import List, Any
from langchain_openai import ChatOpenAI

class DevWrapper:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.invocations = {}

    def invoke(self, input: str) -> Any:
        if input in self.invocations:
            return self.invocations[input]
        
        result = self.llm.invoke(input)
        self.invocations[input] = result
        return result

    def batch(self, inputs: List[str]) -> List[Any]:
        results = []
        for input in inputs:
            if input in self.invocations:
                results.append(self.invocations[input])
            else:
                result = self.llm.invoke(input)
                self.invocations[input] = result
                results.append(result)
        return results
    
dev_llm = DevWrapper(llm)

from contextlib import contextmanager
import time

@contextmanager
def timer(description: str):
    start = time.time()
    yield
    elapsed_time = time.time() - start
    print(f"{description}: {elapsed_time:.4f} seconds")

with timer("First invocation"):
    response = dev_llm.invoke("Hello, how are you?")
    print(response)

with timer("Second invocation"):
    response = dev_llm.invoke("Hello, how are you?")
    print(response)

with timer("Third invocation"):
    response = dev_llm.invoke("Hello, how are you?")
    print(response)

with timer("Batch invocation 1"):
    response = dev_llm.batch(["What is 3*4", "Who is Johnny Rocket?"])
    for r in response:
        print("RESPONSE: ", r)

with timer("Batch invocation 2"):
    response = dev_llm.batch(["What is 3*4", "Who is Johnny Rocket?"])
    for r in response:
        print("RESPONSE: ", r)

with timer("Batch invocation 3"):
    response = dev_llm.batch(["What is 3*4", "Who is Johnny Rocket?"])
    for r in response:
        print("RESPONSE: ", r)