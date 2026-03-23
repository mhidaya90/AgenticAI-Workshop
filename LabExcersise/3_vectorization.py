# Vectorization: representing string/text in a number form

from sklearn.preprocessing import OneHotEncoder
import pandas as pd

file = r"d:\stackroute\2_AI-assisted-programming\learning_requirements\cognizant\2025\1\code\1_PreRequisite\dataset\emp.csv"

data = pd.read_csv(file)
print(data)

# identify the category features/columns
data.dtypes

# method 1
col = "gender"
onehot = OneHotEncoder(sparse_output=False)
gender_onehot_encoding = onehot.fit_transform(data[[col]])
print(gender_onehot_encoding)

print(data.head(3))

# method 2: one-hot encoding using dummy values
cols = ['gender','dept','education'] # convert these columns into dummy values

# pd.get_dummies(data['gender'],drop_first=True).astype(int)
# pd.get_dummies(data['dept'],drop_first=True)
# data[['name','dept']].head(6)

# convert all the categorical columns into a dummy value representation

data_new = data.copy()

for c in cols:
    dummy = pd.get_dummies(data[c], drop_first=True,prefix=c).astype(int)
    data_new = data_new.join(dummy) # add the new set of columns to the dataset

print(data_new)
print(data_new.columns)

# final format
# remove the old categorical columns
data_new.drop(columns=cols,inplace=True)
print(data_new.columns)

# display new set of data
data_new[['name','dept_Prodcom','dept_Purchase','dept_R&D','dept_Sales']].head(20)

data['dept'].head(20)


# Count Vectorizer
# -----------------
# A CountVectorizer converts a collection of text documents into a matrix of word-frequency counts
# (bag-of-words representation) that machine-learning models can use.

from sklearn.feature_extraction.text import CountVectorizer

corpus = ['this is an ai event. all ai related news, ai models will be here',
          'ai is the future. future of ai is automation']
print(corpus)

cv = CountVectorizer()
cv1 = cv.fit(corpus) # gives only the word and its position
voc1 = cv1.vocabulary_
print(voc1)

# document matrix representation
cv2 = cv.fit_transform(corpus)
arr2 = cv2.toarray()
voc2 = cv.get_feature_names_out()

# transpose form
pd.DataFrame(arr2,columns=voc2).T
pd.DataFrame(arr2,columns=voc2)

# 3 PDF documents
# retail, healthcare, finance

from pypdf import PdfReader

files = [
r"d:\stackroute\2_AI-assisted-programming\learning_requirements\cognizant\2025\1\code\1_PreRequisite\dataset\finance.pdf",
r"d:\stackroute\2_AI-assisted-programming\learning_requirements\cognizant\2025\1\code\1_PreRequisite\dataset\healthcare.pdf",
r"d:\stackroute\2_AI-assisted-programming\learning_requirements\cognizant\2025\1\code\1_PreRequisite\dataset\retail.pdf"
]

docs = []

# read each PDF and store the data in a list
for f in files:
    data = ""
    reader = PdfReader(f)

    for page in reader.pages:
        data += page.extract_text()

    docs.append(data)

print(docs)

# there are 3 documents. 1 for each domain
len(docs)

# without stopwords removal
cv1 = CountVectorizer()
wc1 = cv1.fit_transform(docs)
arr1 = wc1.toarray()

arr1[0]
arr1[1]
arr1[2]

# unique set of words in all the documents
print( len(arr1[0]), len(arr1[1]), len(arr1[2]) )

# get the list of vocabulary
f1 = cv1.get_feature_names_out()
print(f"CV1. There are {len(f1)} features across {len(docs)} documents")
print(f1)

docs[0] # finance documents
docs[1] # healthcare
docs[2] # retail

# ndx = ['CTS', 'TATAMOTORS', 'RAMCO']
# cp = [1904.2, 785.4, 218.5]
# vol = [3.1e3, 4.1e3, 1.04e3]
# list(zip(ndx,cp,vol))

# combine all the features of cv1 into a single dataframe
# count the words in each of the documents
df_count = pd.concat([
    pd.DataFrame(zip(f1,arr1[0],["finance"]*len(f1)),columns=['word','count','domain']),
    pd.DataFrame(zip(f1,arr1[1],["healthcare"]*len(f1)),columns=['word','count','domain']),
    pd.DataFrame(zip(f1,arr1[2],["retail"]*len(f1)),columns=['word','count','domain'])
], ignore_index=True)

print(df_count)

# get the count of the word to check its occurance
word = "activity"
word = "loan"

df_count[df_count["word"]==word].sort_values("count",ascending=False)

# exercise: use the flag stop_words=True in the countvectorizer()

# -----------------
# TF-IDF vectorizer
# -----------------
# Term Frequency / Inverse Document Frequency
# tells the significance of a word in a given corpus

from sklearn.feature_extraction.text import TfidfVectorizer

corpus = ['meeting went off well',
          'meeting her after a long time',
          'we are meeting the client today',
          'the stakeholder meeting was cancelled today',
          'the meeting is a way to discus progress']

# remove stop words
vect = TfidfVectorizer()
tfidf = vect.fit_transform(corpus).toarray()
features = vect.get_feature_names_out()

# store in a dataframe
df_tfidf = pd.DataFrame(tfidf,columns=features)
print(df_tfidf)

df_tfidf.T

# ---------------------------------
v2 = TfidfVectorizer(stop_words="english")
tfidf2 = v2.fit_transform(corpus).toarray()
features = v2.get_feature_names_out()

# store in a dataframe
df_tfidf2 = pd.DataFrame(tfidf2,columns=features)
print(df_tfidf2.T)



































































































