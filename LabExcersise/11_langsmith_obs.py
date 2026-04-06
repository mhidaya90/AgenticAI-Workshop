import os
os.getcwd()

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# if the .env file is set up correctly, this will return True; else False
load_dotenv()

def build_documents() -> list[Document]:
    texts = [
        """
        LangSmith is a platform for debugging, tracing, evaluating, and monitoring LLM applications.
        It helps developers inspect application runs, prompts, retrieved documents, and model outputs.
        """,
        """
        FAISS is a vector similarity library commonly used to store embeddings and perform nearest-neighbor search.
        In RAG applications, FAISS can retrieve the most semantically similar chunks for a user query.
        """,
        """
        Retrieval-Augmented Generation (RAG) combines retrieval with generation.
        A retriever fetches relevant context, and the language model answers using that context.
        """,
        """
        LangChain provides abstractions for models, prompts, retrievers, vector stores, and chains.
        A vector store such as FAISS can be converted into a retriever with as_retriever().
        """,
        """
        Good RAG applications rely on clean chunking, useful retrieval, and grounded prompts that instruct the model
        to answer only from the supplied context.
        """,
    ]
    return [Document(page_content=t.strip()) for t in texts]


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def main() -> None:
    # 1) Build sample corpus
    raw_docs = build_documents()

    # 2) Split into chunks
    splitter = RecursiveCharacterTextSplitter( chunk_size=300, chunk_overlap=50,)
    docs = splitter.split_documents(raw_docs)

    # 3) Create embeddings + FAISS index
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(docs, embeddings)

    # 4) Convert FAISS into a retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 5) Create the model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 6) Prompt
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful RAG assistant.
Use only the context below to answer the question.
If the answer is not in the context, say "I don't know based on the provided context."

Context:
{context}

Question:
{question}

Answer:"""
    )

    # 7) Build RAG chain
    chain = ( { "context": retriever | format_docs, "question": RunnablePassthrough(), } | prompt | llm )

    # 8) Ask a question
    question = "What is LangSmith used for?"
    response = chain.invoke(question)

    print("\nQUESTION:")
    print(question)
    print("\nANSWER:")
    print(response.content)

    # 9) Show retrieved chunks separately
    print("\nRETRIEVED CHUNKS:")
    retrieved_docs = retriever.invoke(question)
    for i, d in enumerate(retrieved_docs, start=1):
        print(f"\n--- Chunk {i} ---")
        print(d.page_content)

# run the application
main()
