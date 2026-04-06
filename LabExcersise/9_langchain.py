# Topic: langchain

from langchain_openai import ChatOpenAI

# i) LLM-based prompting
# **********************

# i) create the model
llm = ChatOpenAI()
# use the api_key parameter to create the model

# system: role (set the persona/role to the LLM)
# human: user (user will write the prompts eg: 0-shot/1-shot etc..)

# write a generic function that will run a prompt and retrieve the results from the LLM
def run(prompt):
    try:

        messages = [("system", "You are a helpful assistant good in giving information",),
                    ("human", prompt)]

        response = llm.invoke(messages)
        print(response.content)
        return(1)

    except Exception as e:
        print("Exception from run()." + "\n" + str(e))
        return(-1)

user_p = "give 3 characteristics of a good dataset" # 0-shot
ret = run(user_p)
print(ret)


# --------------------------------------------------------
# 2) Parameterized templates / Placeholder-based templates
# --------------------------------------------------------

# *************************************************
#   2.1) Component: Prompt Templates
#   Build templates to optimize LLM queries / prompts
# *************************************************

from langchain_core.prompts import PromptTemplate

# i)
pt = PromptTemplate(input_variables=["topic"],
                        template="what are the top 5 destinations for people who love {topic}?" )

print(pt)

# ii) format the prompt template
prompt = pt.format(topic="arts and literature")
print(prompt)
ret = run(prompt)
print(ret)


temp = "tell me a {p1} fact about {p2}"
pt = PromptTemplate.from_template(temp)
prompt = pt.format(p1="medical",p2="carbon")
prompt

ret = run(prompt)
print(ret)

# ====================================================
# 3) Component: Chains
# Combine LLMs and Prompt templates to build workflows
# ====================================================

# **************************************************************************************************
# example 3.1
# simple chain without any input parameter and output parser
# # A basic single-step chain that takes a user query, formats it using a prompt, and gets an answer from the LLM.
# **************************************************************************************************

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# i) Create the LLM
llm = ChatOpenAI()

# ii) Create the Prompt
qry = ''' 
    A company is planning to conduct a training program on AI to its leaders.
    Suggest a suitable program name in about 5 words.
    '''
prompt = PromptTemplate.from_template(qry)

# iii) set up the chain to execute the prompt
# a single chain that executes 1 prompt
chain = prompt | llm

# iv) Run it
result = chain.invoke({})
# since the prompt does not take any input values, give a blank {} as parameter
print(result.content)


# *********************************************************************************************
# example 3.2
# simple chain with input parameter and an output parser
# A basic single-step chain that takes a user query, formats it using a prompt,
# gets an answer from the LLM, formats the response
# ***********************************************************************************************

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# i) Create the LLM
llm = ChatOpenAI()

# ii) Create the Prompt
prompt = PromptTemplate(input_variables=["topic"],
                        template="Explain in simple terms the concept of {topic}" )

topic = "Quantum Computing"

# iii) Create the LLM Chain
chain = prompt | llm | StrOutputParser()

# iv) Run it
result = chain.invoke({"topic":topic})
print(result)

# -------------------------
# --- 28/03/2026: Saturday
# -------------------------
# ********************************************
# example 3.3
# Example of ChatPromptTemplate with Parser
# ********************************************


from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Step 1: Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful customer support assistant."),
    ("human", "Customer issue: {issue}")
])

# Step 2: Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Step 3: Create chain (new style)
chain = prompt | llm | StrOutputParser()

# Step 4: Invoke with input
response = chain.invoke({
    "issue": "My internet connection keeps disconnecting every 10 minutes."
})

# Step 5: analyse the response
print(response)

# **************************
# example 3.4 : JSON Parser
# **************************
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

# Step 1: Define parser with expected schema
parser = JsonOutputParser()
format_instructions = parser.get_format_instructions()
print(format_instructions)

# Step 2: Create prompt template
prompt = ChatPromptTemplate.from_template("""
You are an AI assistant that classifies support tickets.

Extract the following fields:
- category
- priority
- suggested_action

{format_instructions}

User Query:
{query}
""")

# Step 3: Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Step 4: Create chain
chain = prompt | llm | parser

# Step 5: Invoke
response = chain.invoke({
    "query": "My laptop is overheating and shutting down frequently.",
    "format_instructions": format_instructions
})

print(response)
response['category']
response['priority']
response['suggested_action']


# *****************************
# example 3.5: Sequential Chain
# Sequential chains allow you to connect multiple chains and compose them into pipelines
# that execute some specific scenario.
# *****************************

# ********* Returns only the final response ******************

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# step 1: create model
llm = ChatOpenAI()

# step 2: create the prompts
# Step 2.1: Content
content_prompt = PromptTemplate(
    input_variables=["title"],
    template="""You are an expert content writer.
                    Given a title, create a professional and high quality content with a suitable heading.
                    The content should not exceed 1000 words. 

                    Title: {title}

                    Content:"""
)

# Step 2.2: Summary
summary_prompt = PromptTemplate(
    input_variables=["contents"],
    template="""You are an expert editor of text documents.
                    Given the content on a topic, write a crisp 75-word summary. Retain the same heading.

                    Topic Content:
                    {contents}

                    Summary:"""
)

# step 3: output parser
parser = StrOutputParser()

# step 4: create the individual chains
content_chain = content_prompt | llm | parser
summary_chain = summary_prompt | llm | parser

# step 5: full pipeline
chain = content_chain | (lambda contents: {"contents": contents}) | summary_chain

# step 6: run the chain
result = chain.invoke({"title":"Benefits of Green Energy to the Society"})
print("Final Summary")
print(result)

# ************* 3.5 To return intermediate results *****************

from langchain_core.runnables import RunnableLambda

content_chain = content_prompt | llm | parser
summary_chain = summary_prompt | llm | parser


def workflow(inputs):
    contents = content_chain.invoke({"title": inputs["title"]})
    summary = summary_chain.invoke({"contents": contents})

    return {
        "title": inputs["title"],
        "contents": contents,
        "summary": summary
    }


chain = RunnableLambda(workflow)

response = chain.invoke({"title": "Benefits of Green energy to the society"})

print("CONTENT:\n", response["contents"])
print("\nSUMMARY:\n", response["summary"])


# =========================================================
# 4) Component: Tools and Agents
# Agent: Use LLMs to choose a specific activity to perform
# Tool: Used by agents to perform a specific task
# ========================================================

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langsmith import Client
from langchain.agents import create_agent

# step 1: Tool initialization
wiki = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000))

# step 2: create the tool object
tools = [wiki]

# step 3: create agent
agent = create_agent(model=llm, tools=tools, system_prompt="you are a helpful assistant")

content_msg = "What is climate change"

# step 4: execution
msg = {"messages": [{"role": "user", "content": content_msg}]}
response = agent.invoke(input=msg)

# check the response
print(response)

# Example 2: # LLM + python functions as Tools

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain.agents import create_agent
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk

@tool # always include this line to create a function as a tool
def extract_entities(text: str) -> dict:
    """Extract named entities and their types from the given input text."""
    entities = []

    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    tree = ne_chunk(tagged)

    for subtree in tree:
        if hasattr(subtree, "label"):
            for token, pos in subtree:
                entities.append(f"{subtree.label()}:{token}")

    return {"entities": entities}

# create the tools
search = DuckDuckGoSearchRun()
tools = [search, extract_entities] # sequence is important

system_prompt = """
You are a helpful AI assistant.

When the user asks for a summary:
1. First provide the summary under the heading 'Text'.
2. Then extract named entities from that summary using the extract_entities tool.
3. Return the final answer under exactly these headings:
   Text
   Entities
"""

user_content = ''' Give a 50 word summary on Operation Sindoor, then extract entities from that summary'''

agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

resp = agent.invoke({ "messages":[{"role": "user", "content": user_content }]  } )
print(resp["messages"][-1].content)
print(resp)

# =====================================
# 5) Component: Memory
# State management of tools / agent
# =====================================

# **************************
# (example 1) simple history
# **************************

import os
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

llm = ChatOpenAI()

history = ChatMessageHistory()

history.add_user_message("hello")
history.add_ai_message("Greetings. How are you ?")
history.add_user_message("i am fine. today i want to talk about some interesting topics")
history.add_ai_message("Nice. Looking forward to this.")
print(history)
history.messages


# *******************************************
# (example 2) : Simulation of a real-life chat
# ********************************************
history = ChatMessageHistory()

# Start the chat loop
msg = ''' Hi. I am your AI Doctor. How can i help you?
        To end this conversation, type exit/bye/quit/close
        '''
flag = True
exit_val = ["exit","quit","bye","close"]

while flag:
    user_input = input("You: ")
    if any(ev for ev in exit_val if ev in user_input):
        flag = False

    # Add user message to history
    history.add_user_message(user_input)

    # Generate AI response using chat history
    ai_response = llm.invoke(history.messages)

    # Display and store AI response
    print(f"AI: {ai_response.content}")
    history.add_ai_message(ai_response.content)

# total messages
print(f"There are {len(history.messages)} messages")

# display the full chat history
print("\n--- Chat History ---")
for msg in history.messages:
    role = "User" if isinstance(msg, HumanMessage) else "AI"
    print(f"{role}: {msg.content}")

# get the 2nd question and answer
q = 2
print(f"Question Number: {q}")
print(f"Q:" + history.messages[q].content)
print()
print(f"A:" + history.messages[q+1].content)

# =========================================================
# 6) Component: Document Loader
# Read a document
# ========================================================
from langchain_community.document_loaders import TextLoader, PyPDFLoader

f1 = "D:/stackroute/2_AI-assisted-programming/learning_requirements/parkar/2025/1/dataset/ai.txt"
f2 = "D:/stackroute/2_AI-assisted-programming/learning_requirements/parkar/2025/1/dataset/indian_classical_music.pdf"

# pdf_files = ['f1.pdf','f2.pdf']
# loop every file in files:
#     open file;
#     for every page:
#         get data;
#         append data
#

# -------------------------------
# read a text file for processing
# -------------------------------
loader = TextLoader(f1)
data = loader.load()

# read the full contents
data = data[0].page_content
print(data)
print(f"Document length = {len(data)} characters")

# -------------------------
# read a PDF for processing
# -------------------------
loader = PyPDFLoader(f2)
data = loader.load()
print(data)
print(f"Total pages = {len(data)}")

# get the data from all the pages
pdf_data = ""
for i in range(len(data)):
    pdf_data+= data[i].page_content
    pdf_data+= "\n"
print(pdf_data)

# =========================================================
# 7) Component: Vector Store
# Create embeddings on input data and perform Q/A
# ========================================================

import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Step 1: Load text from file
loader = TextLoader(f1)
documents = loader.load()

chunksize=150
overlap = int(0.1*chunksize)

# Step 2: Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunksize, chunk_overlap=overlap)
docs = text_splitter.split_documents(documents)
print(f"There are {len(docs)} chunks")

# print the chunks
chunks = [doc.page_content for doc in docs]

# print(len(chunks))
# chunks[0]
# chunks[10]

# Step 3: Convert to vector store using OpenAI
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_texts(chunks,embedding=embeddings)
print(vectorstore)

# Step 4: Perform similarity search
query = "Give 3 examples of real world AI"
results = vectorstore.similarity_search(query, k=2)

# Step 5: Display results
for i, doc in enumerate(results, 1):
    print(f"\n--- Result {i} ---\n{doc.page_content}")












