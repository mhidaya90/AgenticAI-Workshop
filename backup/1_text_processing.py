# tokenization
# sentence into individual words

# import the library "regular expression"

# CTRL + ENTER -> execute the current line

import re

# string
# regular string
s1 = "this is a string \n\n this has a new line"
print(s1)

# raw string
s2 = r"this is a string \n\n this has a new line"
print(s2)

# tokens
# 1) using the split()
s1.split() # here, the default delimiter is the "white space"
s2.split()

# $ ~ , |

# splitting data based on custom delimiters
rec = "17719~Sriraman~Pune~Plan A~577.50"
print(rec)
rec.split("~")

# 2) pattern matching in a string
# -------------------------------
text = "India is my Country. The capital is New Delhi. It is in Asia. Bias and Variance are part of any data"

# extract all the words that have "ia" in the text

# p1: pattern to extract
# p2: input data

# method 1
re.findall(r"\b\w*ia\w*\b", text)
# \b: starting of the word
# \w: any character
# * : 0 or more occurances of characters
# \b: ending of the word

# method 2
# []: range of characters
# consider the string as a regular text; not a raw text
# in this case, use \\ for pattern matching
re.findall("[\\w]*ia[\\w]*", text)

# gives a syntax warning
re.findall("[\w]*ia[\w]*", text)

# ii) extract email IDs from a given text
text = '''
    these are the primary email IDs of employees arun@cts.co.in sriram@cts.co.in priya@gmail.com 
    anu@yahoo.com abc@mail.com newemp@ctsxyz.com 
     '''
print(text)

pattern = r"[\w.]*@[\w.]*" # create the pattern
re.findall(pattern, text) # use the pattern

# extract email IDs of only cts employees
pattern = r"[\w.]*@cts[\w.]*" # create the pattern
re.findall(pattern, text) # use the pattern

# extract only those names that has the pattern cts.
pattern = r"[\w.]*@cts\.[\w.]*" # create the pattern
re.findall(pattern, text) # use the pattern

# iii) extract digits from a text
# \d -> digits

text =  '''
            the project is over 13 years old. There are 95 people working on this with over 30 releases. 
            The expected revenue is about 102 million. There are close to 3750 files spanning over 55745 lines of code 
        '''

# get all the digits
num = re.findall(r"\d+", text)
print(num)
type(num)
type(num[0])

# list comprehension
num = [int(n) for n in num]

# extract all the 2 digit numbers
# method 1
num2 = [int(n) for n in num if len(n) == 3]
num2

# method 2 : re method
# extract all the 5-digits from text
re.findall(r"\d{5}", text)

re.findall(r"\d{4}", text)
re.findall(r"\d{3}", text)
re.findall(r"\d{2}", text)

# look ahead / look behind
# + -         + -

pattern = r"(?<!\w)(\d{2})(?!\w)"
re.findall(pattern,text)

# \w: alpha characters -->
# \d: numbers -->

# iv) extract mobile phone numbers from a text
text = "emp id 16590 phone 8955019641"
re.findall(r"\d{10}",text)


# v)
text = "the client numbers are 123-456-8976 and (457)-457-8911"
# OR condition : matching multiple patterns (using the | symbol)
pattern = r"\d{3}-\d{3}-\d{4}|\(\d{3}\)-\d{3}-\d{4}"
re.findall(pattern,text)

# vi) text cleansing
text = ''' there are a lot of \n\n\n unwanted characters in this text...
    [] [] reading becomes difficult %%^. This contains A MIX Of cASES.
    Thre are some numbers here 1159 5959
'''
print(text)

# sub: substitution
# removing all the spl characters from

re.sub("[\W]"," ",text).lower().strip()

newtext = ' '.join(re.sub("[\W]"," ",text).split()).lower().strip()

print(text)
print(newtext)
