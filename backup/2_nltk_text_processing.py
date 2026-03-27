# Tokenization:
# split the text into
# a) words
# b) sentences

# NLTK: natural language toolkit library.
# used for data processing

import nltk

text = "this is a sentence with some words"
print(text)

# work token
words = nltk.word_tokenize(text)
print(words)
# similar to the split() of python

# sentence tokenization

# eg1:
text = "Today is Friday. The weekend starts today. There are 2 more days for the week to end"
nltk.sent_tokenize(text)

# other sentence delimiters
text = "The meeting is at 10. Are you coming? Please confirm!"
nltk.sent_tokenize(text)

# dealing with abbreviations
text = "Dr.Rao is a scientist with ISRO. his colleague is Ms.Priya."
nltk.sent_tokenize(text)

# scientific notations
text = "take the value of pi as 3.14. Use this in all calculations"
nltk.sent_tokenize(text)

text = "take the value of pi as 3.14 only. use this in all calculations"
nltk.sent_tokenize(text)

text = "take the value of pi as 3. 14. Use this in all calculations"
nltk.sent_tokenize(text)

# read a file and do a sentence tokenization

path=r"D:\stackroute\2_AI-assisted-programming\learning_requirements\cognizant\2025\1\code\1_PreRequisite\dataset\rbi.pdf"

# path = r"d:\new\text\t1.pdf"
# path = "d:\\new\\text\\t1.pdf"
# path="d:/new/text/t1.pdf"

from pypdf import PdfReader

data = {}

reader = PdfReader(path)
print(f"Total pages = {len(reader.pages)}")

for ndx,page in enumerate(reader.pages):
        data[ndx] = page.extract_text()

print(data)

# page wise document text
# exercise: take 1 page. Convert it to a sentence vector

pagedata = data[10]
pagedata_sentences = nltk.sent_tokenize(pagedata)
print(f"Total sentences in pagedata = {len(pagedata_sentences)}")

# print the first 2 sentences
pagedata_sentences[:3]

data5 = nltk.sent_tokenize(data[5])
print(f"Total sentences = {len(data5)}")

for d in data5:
        print(d)
        print(" ------ ")


# apostrphe
# couldn't', didn't'

text = "i can't do this. it cdn't be done. if it hadn't been noticed, it wd've caused a big problem"
nltk.word_tokenize(text)
nltk.sent_tokenize(text)

# i) apostrophe
from nltk.tokenize import RegexpTokenizer

ap_tokens = RegexpTokenizer("[\\w']+") # find all the words that has or does not contain '
ap_tokens.tokenize(text)

# password validation
# number
# special char
# uppercase
# lowercase

tokenizer = RegexpTokenizer(r'.')
# validate this password
password = "Chin@123<"
# password = "abdef"

# convert the password into individual characters using the tokenizer
chars = tokenizer.tokenize(password)
print(chars)

has_digit = any(c.isdigit() for c in chars)
print(has_digit)

has_upper = any(c.isupper() for c in chars) # upper case
has_special = any(not c.isalnum() for c in chars) # alphanumeric
print(has_special)

# for special character validations, you can try this library
import string
print(string.punctuation)

# validation of IP addresses
ip_token = RegexpTokenizer(r"\d+.\d+.\d+.\d+")
text = "User login failed from IP 114.45.1.874 at 10:32 PM"
ip_token.tokenize(text)
# apply the validation rules to check if the IP is valid or suspect

# --------------------------------------------------------------------------
# advance tokenization: to be discussed later
# --------------------------------------------------------------------------

# 2) stop words

text = '''the movie was excellent with a nice storyline. the characters did a good job. overall it was a fun movie'''

print(text)

from nltk.corpus import stopwords

# convert the list of words into a set
stop_words = set(stopwords.words("english"))
print(stop_words)

# stopwords allows to add custom words as "stop words"
stop_words.update(["paisa", "rupya"])
print(stop_words)

# check if the words are added
"paisa" in stop_words
"rupya" in stop_words

# split the text into words
words = nltk.word_tokenize(text);
print(words)

new_words = [w for w in words if w not in stop_words]
new_text = ' '.join(new_words)

print(text)
print(new_text)

# read the rbi file
# do a stop word removal on any 1 page of the document
# compare the actual and stopword version.

# 14-March-2026
import nltk

# POS tag: Parts of Speech
text = ''' reliance industries has a global presence. it started as a small refinery and now it has turned into a big business organization '''

words = nltk.word_tokenize(text)
pos = nltk.pos_tag(words)
print(pos)

# extract only the nouns
noun_forms = ['NN','NNS','NNP']
noun_words = []

for k, v in pos:
        if v in noun_forms:
                noun_words.append(k)
print(noun_words)

# lemma and stemming
'''
Stemming means cutting a word down to its basic root by removing endings — even if the result is not a real word.
*** running → run, studies → studi, easily → easili
*** Faster & Less Accurate
*** Uses simple rules to cut words

Lemmatization means converting a word into its dictionary base form (lemma) using language rules and meaning.
*** running → run, better → good, studies → study
*** Slower & More Accurate
*** Uses POS information
'''

from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet

words = ["running", "studies", "better", "flies", "cats", "easily"]

# ---- initialize stemmer and lemmatizer ----
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

print("Word\t\tStem\t\tLemma")

for w in words:
    stem = stemmer.stem(w)
    lemma = lemmatizer.lemmatize(w)   # default POS = noun
    print(f"{w}\t\t{stem}\t\t{lemma}")

# n-Grams: technique to group words into 1 or more combinations
from textblob import TextBlob

text = "artificial intelligence is going to play a big role in automation"
blob = TextBlob(text)
print(blob)

# convert the blob text into grams
blob.ngrams(1) # similar to split function (single words)
blob.ngrams(2)
blob.ngrams(3)
blob.ngrams(4)
blob.ngrams(5)

# Word Association
# Edit Distance
import difflib

text = "the return policy for any product is 15 days with a bill and 7 days without a valid bill"

words = text.split();
print(words)

difflib.get_close_matches("plcy", words)
difflib.get_close_matches("prodt", words)
difflib.get_close_matches("daze",words)

# NER (Named Entity Recognition)

import spacy

nlp = spacy.load("en_core_web_sm")

text = "the founder of Reliance industries is Dhirubhai Ambani. it was started in 1981"

# convert the text into nlp format
doc = nlp(text)

# extract all the entities from the given text
for ent in doc.ents:
    print(f"Entity = {ent.text}, Entity Type = {ent.label_}")


# for entities not present in the default corpus
text = "the role of xenophycular in the body is to release new tissues"
doc = nlp(text)

for ent in doc.ents:
    print(f"Entity = {ent.text}, Entity Type = {ent.label_}")
# this will not return any entities since the words/entities are not present.

# the entity list will have to be customized to include the new words/entites and its type.

from spacy.pipeline import EntityRuler
nlp = spacy.load("en_core_web_sm")

ruler = nlp.add_pipe("entity_ruler", before="ner")

# exact match
patterns = [ {"label": "DRUG", "pattern": "xenophycular"},
             {"label": "DRUG", "pattern": "ibuprofin"}]

ruler.add_patterns(patterns)

text = "the role of Xenophycular in the body is to release new tissues. earlier it was ibuprofin"
doc = nlp(text)

for ent in doc.ents:
    print(f"Entity = {ent.text}, Entity Type = {ent.label_}")


# for .. in text:
#     match = regex(pattern)
#     if match:
#         pattern = ["label": "PHONE", "pattern":matchvalue]