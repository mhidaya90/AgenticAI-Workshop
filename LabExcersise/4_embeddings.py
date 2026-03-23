# Embeddings:
# converting text into matrix of numbers with meanings

from gensim.models import Word2Vec

doc = ["delivery was fast and packaging was good",
       "shipping was quick and box was safe",
       "return process was slow and refund delayed",
       "customer support helped me quickly",
       "the product quality exceeded my expectations and feels premium",
       "received a damaged item and the replacement took too long",
       "checkout process was smooth and payment options were easy",
       "size chart was inaccurate so the shoes did not fit properly",
       "app interface is confusing and hard to navigate",
       "great discounts but the website loads very slowly",
       "customer service resolved my complaint within minutes",
       "tracking information was not updated regularly",
       "the fabric feels cheap compared to the pictures online",
       "installation guide was clear and helped me set up quickly"
       ]

# get the unique words from the doc
reviews = []

for d in doc:
    words = d.split()
    reviews.append(words)
print(reviews)

# build the model
model = Word2Vec(reviews,vector_size=250,window=4,min_count=1)
print(model)

# unique words in the reviews
unique_words = list(model.wv.index_to_key)
print(unique_words)

# get the vector of a word
# numerical representation of the word/term
model.wv["customer"]
model.wv["customer"].shape

model.wv["delivery"]
model.wv["delivery"].shape

# find similarities between 2 words
from sklearn.metrics.pairwise import cosine_similarity

A = model.wv['product']
B = model.wv['fabric']

sim = cosine_similarity([A], [B])
print(f"Similarity between delayed and slowly is {sim}")

# increase vector size to 200.

# Sentence comparison
# Sentence Transformation

# Sentence transformation is the process of converting a sentence into another representation or form (
# textual or # numerical) while preserving its meaning

from sentence_transformers import SentenceTransformer, util

# name of the embedding model "all-MinLM-L6-v2"
model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = ['lion is the king of jungle', 'lion king is a good movie']

embeddings = model.encode(sentences)

print(embeddings)
len(embeddings)

# get the shape of the embeddings
embeddings[0].shape

# create the 2 embeddings top find the similarities
e1 = embeddings[0]
e2 = embeddings[1]
sim = util.cos_sim(e1,e2)
print(f"Similarities between the 2 strings = {sim}")

sentences = [
    "healthy food contains all the necessary elements for our body like protein, vitamin, fats, "
    "and carbohydrates, etc.",
"healthy food is the requirement of our body.",
"it does not let us feel lazy and dull.",
"any food closest to its natural form is healthier than those one cooked.",
"fried and oily food can never be healthy food.",
"to get healthy food, we should stay away from junk food.",
"protein in our food helps our body in repairing its dead or broken cells.",
"carbohydrates help us in getting energy to be ready for our daily work.",
"vitamins strengthen our bones and keep us away from diseases.",
"healthy food is essential for a healthy body, soul, and life."
]

comment = ["stale food is not nutritious"]

# use case: find which sentences from the corpus match the comment

# -------------------------------------------------------------------
# the embedding size for the corpus and the prompt should be the same
# --------------------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

# create the sentence and query embeddings
sentence_emb = model.encode(sentences)
comment_emb = model.encode(comment)

# verify the embedding size
print(f"Sentence: {(sentence_emb[0].shape)}, Comment: {comment_emb[0].shape}")

results = {}

for i in range(len(sentence_emb)):
    sent_emb = sentence_emb[i]
    results[i] = round(float(util.cos_sim(sent_emb, comment_emb)),5)

print(results)

# sort the results in a decreasing order
sorted_results = sorted(results.items(),key=lambda x:x[1], reverse=True)
print(sorted_results)

# print the actual results
top_k = 1
print(f"The Closest matching texts for the given input '{comment[0]}' : \n")

for i in range(top_k):
    ndx = sorted_results[i][0]
    print(f"** {sentences[ndx]}")

# --------------------------------------------------------------------------

# Embeddings with OpenAI

# openAI library
# openAI key

# how to configure the Apikey in the environment
# i) Create a new Env variable OPENAI_API_KEY and set the value of the key
# or .env file

# step 2
# import os
# os.getenv("OPENAI_API_KEY")

from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

apikey = ""
client = OpenAI(api_key = apikey)

texts = [
    "Delivery was late and packaging was damaged",
    "Amazing quality and worth the price",
    "Refund process was slow"
]

print(texts)

# create the embeddings
response = client.embeddings.create(model="text-embedding-3-small",   # fast + affordable
                input=texts )
# embeddings
embeddings = [item.embedding for item in response.data]
len(embeddings)

# view the embeddings
embeddings[0]

# embedding size
len(embeddings[0])

# Step 2: Embed query
query = "Late shipping issue"

query_embedding = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding

sim_score = []

# Step 3: Compute similarity
for i in range(len(texts)):
    similarities = cosine_similarity([query_embedding], [embeddings[i]])
    sim_score.append(similarities)

print(sim_score)
