from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough

def create_db(docs):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embedding=embeddings)
    return vectorstore

def get_documents_from_loader(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_docs = splitter.split_documents(docs)
    print(len(split_docs))
    return split_docs

def create_chain(vectorstore):
    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template("Answer the following question using context provided.\nContext: {context}\nQuestion: {input}")
    parser = StrOutputParser()
    #chain = prompt | model | parser
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    chain = create_stuff_documents_chain(llm=model, output_parser=parser, prompt=prompt)
    retrieval_chain = create_retrieval_chain(retriever, chain)
    return retrieval_chain

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_chain2(vectorstore):
    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template("Answer the following question using context provided.\nContext: {context}\nQuestion: {question}")
    parser = StrOutputParser()
    #chain = prompt | model | parser
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    chain = {"context": retriever, "question": RunnablePassthrough() } | prompt | model | parser

    return chain

url = "https://python.langchain.com/v0.2/docs/concepts/"

#docA = Document(page_content="LCEL is a funky music machine", metadata={})



docs = get_documents_from_loader(url)
vectorstore = create_db(docs)
chain = create_chain2(vectorstore)
response = chain.invoke("What is LCEL?")
print(response)