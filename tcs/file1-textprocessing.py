#tokenization
#breaks words into pieces
#import regular expression

import re
print('hello')

s1 = "this is a string \n\n this has a new line"
#print(s1)

# raw string
s2 = r"this is a string \n\n this has a new line"
#print(s2)

s1.split()

s2.split()

rec = "790417~hidayathullah~chennai~Plan A~550.5"
print(rec)
print(rec.split("~"))

text= "India is my country, the captial is new delhi, it is in asia. Bias and Variance are part of any data"
print(re.findall(r"\b\w*ia\w*\b",text))

re.findall("[\\w]*ia[\\w]*",text)
print(re.findall("[\w]*ia[\w]*",text))

text= "these are the primary email id of employee anu@cts.co.in sriram@cts.co.in priya@gmail.com someli@gmail.com joseph@ctsxyz.com"
print(text)
pattern=r"[\w.]*@[\w.]*"
re.findall(pattern,text)
pattern=r"[\w.]*@cts[\w.]*"
re.findall(pattern,text)
pattern=r"[\w.]*@cts\.[\w.]*"
re.findall(pattern,text)

#extract digits from a text
#\d represent digits
text = '''
        The forefeet have 4 functional digits, and the hindfeet 50
        Enter only 300 digits for 36.5-digit verification
       '''
num= re.findall(r"\d+",text)
print(num)
#list comprehension
[int(n) for n in num]
[int(n) for n in num if len(n)==3]

re.findall(r"\d{3}",text)

pattern=r"(?<!\w)(\d{2})(?!\w)"
print(re.findall(pattern,text))

text="this is my phone number 9566740274"
re.findall(r"\d{10}",text)

text= "the client numbers are 123-456-7890 and external connect and (456)-457-2345"
re.findall(r"\d{3}-\d{3}-\d{4}",text)
pattern = r"\d{3}-\d{3}-\d{4}|\(\d{3}\)-\d{3}-\d{4}"

re.findall(pattern,text)

text = "the client numbers are 123-456-8976 and (457)-457-8911"
pattern = r"\d{3}-\d{3}-\d{4}|\(\d{3}\)-\d{3}-\d{4}"
re.findall(pattern, text)


#text cleanising
text='''
this is the line have \n\n\n\n for ths word and simpele oit will be
'''

# sub: substitution
# removing all the spl characters from

re.sub("[\W]", " ", text).lower().strip()

newtext = ' '.join(re.sub("[\W]", " ", text).split()).lower().strip()

print(text)
print(newtext)















