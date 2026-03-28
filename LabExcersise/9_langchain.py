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
























