# feature engineering
# create a custom feature to store meanings

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer

reviews = [
    "Delivery was late and the box was damaged",
    "Amazing quality, worth the price!",
    "Refund was delayed and support was unhelpful",
    "Quick delivery, great packaging, happy",
    "Overpriced but the product feels premium"
]

# convert the following reviews into a dataframe
# add a new column "delivery_issue". 0-> no issues; 1 -> has issues

# 1) create a dataframe to store the data
df = pd.DataFrame({"review": reviews})
print(df)

def clean_text(review:str) -> str:
    s = re.sub("[\\W]+", " ", review).lower().strip()
    return(s)

df["clean"] = df["review"].apply(clean_text)
print(df[["review","clean"]])

# create a new column "delivery_issue" and initialize all rows with -1
df["delivery_issue"] = -1
print(df)

# add terms that indicate "issues with deliveries".
delivery_terms = ["late", "delay", "delayed", "shipping", "delivery", "damaged",
                  "package", "packaging", "courier"]

rows = len(df)
print(f"There are {rows} records")

for i in range(rows):
    review = df.loc[i, "clean"]
    review_words = review.split()

    if any(rw for rw in review_words if rw in delivery_terms):
        flag = 1
    else:
        flag = 0

    df.loc[i, "delivery_issue"] = flag

print(df)








