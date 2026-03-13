#nltk token processing

#tokenization
#split the text into
#words
#sentence

import nltk


#word Tokenization

text = "this is some text"
words= nltk.word_tokenize(text)
print(words)

#similar to python split function


#snetence Tokenization

text1 = "Today is Friday. The weekend starts today. There are 2 more days for the week to end"
nltk.sent_tokenize(text1)

#other sentence with delimiters
text = "The meeting is at 10. Are you coming? Please confirm!"
nltk.sent_tokenize(text)

#Dealing with abbreviations
text="Dr.Suresh is scientist in ISRO. his colleague Ms.priya. her husband is Mr.kamal"
nltk.sent_tokenize(text)

text = "Dr.Rao is a scientist with ISRO. his colleague is Ms.Priya."
nltk.sent_tokenize(text)

#Scientific notations
text="the value of pi is 3.14. used the value in calsutions"
nltk.sent_tokenize(text)

#read a file and do sentence tokenization
from pypdf import PdfReader

path=r"C:\Users\c04-labuser992564\Downloads\rbi.pdf"

data = {}

reader = PdfReader(path)
print(f"Total pages = {len(reader.pages)}")

for ndx,page in enumerate(reader.pages):
        data[ndx] = page.extract_text()

print(data)

data[5]
data[10]

pagedata = data[5]
pagedata_sentence=nltk.sent_tokenize(pagedata)
print("Total sentence in the page is={len(pagedata_sentence)}")

for d in data[5]:
    print(d)
    print("------")

# i) apostrophe

from nltk.tokenize import RegexpTokenizer


ap_tokens = RegexpTokenizer("[\\w']+")  # find all the words that has or does not contain '
text="i can't do it. i wouldn't go for it."
ap_tokens.tokenize(text)


tokenizer = RegexpTokenizer(r'.')
password = "Chian@123"
chars = tokenizer.tokenize(password)
print(chars)

has_digit = any(c.isdigit() for c in chars)
print(has_digit)

has_upper = any(c.isupper() for c in chars)  # upper case
print(has_upper)
has_special = any(not c.isalnum() for c in chars)  # alphanumeric
print(has_special)


import string
print(string.ascii_lowercase)
print(string.ascii_uppercase)
print(string.punctuation)

# validation of IP addresses
ip_token = RegexpTokenizer(r"\d+.\d+.\d+.\d+")
text = "User login failed from IP 114.45.1.874 at 10:32 PM"
ip_token.tokenize(text)
# apply the validation rules to check if the IP is valid or suspect


#Stop Words

from nltk.corpus import stopwords

text='''the movie was excellent with nice storyline. 
the charcters did the good job. 
overall it was nice movie'''

stop_words = set(stopwords.words("english"))
print(stop_words)

stop_words.update(["paisa","rupya"])

print(stop_words)

"paisa" in stop_words
"rupaya" in stop_words

# split the text into words
words = nltk.word_tokenize(text);
print(words)

new_words = [w for w in words if w not in stop_words]
new_text= ' '.join(new_words)

print(text)
print(new_text)

words = nltk.word_tokenize(data[5])
print(words)
new_words = [w for w in words if w not in stop_words]
new_text= ' '.join(new_words)

print(data[5])
print(new_text)

# POS tag: Parts of Speech
text = ''' reliance industries has a global presence. it started as a small refinery and not it has turned into a big business organization '''

words = nltk.word_tokenize(text)
pos = nltk.pos_tag(words)
print(pos)

import spacy
nlp = spacy.load("en_core_web_sm")