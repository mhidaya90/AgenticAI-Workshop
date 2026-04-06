# RAG evaluation techniques

# -----------------------------
# 1) Structured data evaluation
# -----------------------------

import psycopg2 as psy
import pandas as pd
from openai import OpenAI
import re, numpy as np

# ---------------------------------------------------------
# read the connection file and connect to postgres database
# ---------------------------------------------------------
def ConnectDB(file):
    try:
        ret = []
        data = ''
        fp = open(file, "r")

        while True:
            next_line = fp.readline()
            if not next_line:
                break
            data += next_line.strip()
        fp.close()

        if len(data) <= 0:
            ret.extend(["ERROR", "Unable to read the Input data properly. Filename:" + file])
        else:
            parameters = data.split(";")
            keys = [];
            values = []

            for p in parameters:
                if len(p) > 0:
                    sp = p.split(":")
                    keys.append(sp[0])
                    values.append(sp[1])
            conn_values = dict(zip(keys, values))

            # Establish connection to PostgreSQL
            conn = psy.connect(dbname=conn_values['dbname'], user=conn_values['user'],
                               password=conn_values['password'],
                               host=conn_values['host'], port=conn_values['port'])

            cursor = conn.cursor()

            ret.extend(["SUCCESS", conn, cursor])

    except Exception as e:
        ret.extend(["EXCEPTION", "ConnetDB(). " + str(e)])

    return (ret)

# Connect to the pgVector database using the credentials
ret = ConnectDB("pgvector.txt")
if ret[0] == "SUCCESS":
    conn = ret[1]
    cursor = ret[2]
else:
    print("Error / Exception during ConnectDB")

# for the embeddings
client = OpenAI()

def executeQuery(query):
    try:
        data = ''

        cursor.execute(query)
        data = cursor.fetchall()

        cols = [c[0] for c in cursor.description]
        data = pd.DataFrame(data, columns=cols)
        data = data.reset_index(drop=True)


    except Exception as e:
        data = "Exception." + str(e)

    return(data)

def GetSimilarRecords(txt,limit=5):
    response = client.embeddings.create(model='text-embedding-3-small',input=txt)
    txt_embed = response.data[0].embedding

    query = f''' select * from supplier_data where supplier_id in (
                   select supplier_id from supplier order by embedding <=> '{txt_embed}'::vector 
                   limit {limit} ) '''

    data = executeQuery(query)


    return(data)


# Evaluations
# ***********

txt = 'excellent compliance score'
res = GetSimilarRecords(txt,limit=30)
print(res)

# ------------------------------------------
# 1) Precision@k (retrieved / retrieved_ids)
# Meaning: Relevance/Quality of the top K results
# formula:  relevant results in top K/ K
# ---------------------------------------

res[['supplier_id','compliance_score']]

# assume: Excellent Compliance score > 90
comp_score = 90
cs_k = len(res[res.compliance_score >= comp_score])
k = 30

prec_at_k = cs_k / k
print(f"Precision @{k} = {prec_at_k *100} %")

# ------------------------------------------
# 2) Recall@k (retrieved / relevant_ids)
# focus area: Coverage
# Out of all relevant records, how many did we successfully retrieve in top K?
# ------------------------------------------
qry = "select count(1) from supplier_data where compliance_score >= 90;"
ct_all_rec = executeQuery(qry)
ct_all_rec = ct_all_rec["count"].tolist()[0]
print(f"Total rows that match the condition > 90 is: {ct_all_rec}")

rec_at_k = cs_k / ct_all_rec
print(f"Recall @{k} = {rec_at_k * 100}%")

# -------------------------------
# 3) MAP (Mean Average Precision)
# focus area: ranking of ALL hits
# -------------------------------
# for every retrieved ID, check if it exists in the Relevant ID
# check relevant items only
# (sum of precisions@k at relevant hits) / total relevant items (count of all relevant record)

small_df1 = res[['supplier_id','compliance_score']]
small_df1['relevant'] = np.where(small_df1['compliance_score']>=90, "yes", "no")
small_df1 = small_df1.sort_values("relevant",ascending=False).reset_index(drop=True)
print(small_df1)

# ----------------------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str):
    return normalize_text(text).split()

# 1) Exact match
def exact_match_score(reference: str, prediction: str) -> int:
    return int(normalize_text(reference) == normalize_text(prediction))


# 2) F1: Harmonic Mean of Precision & Recall
# ((2PR) / (P+R)
def f1_score(reference: str, prediction: str) -> float:
    ref_tokens = tokenize(reference)
    pred_tokens = tokenize(prediction)

    if len(ref_tokens) == 0 and len(pred_tokens) == 0:
        return 1.0
    if len(ref_tokens) == 0 or len(pred_tokens) == 0:
        return 0.0

    A = set(ref_tokens)
    B = set(pred_tokens)
    common = len(A.intersection(B))

    if common == 0:
        return 0.0

    precision = common / len(pred_tokens)
    recall = common / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)

# --------------------------------------
# 3) BLEU: Bi-Lingual Evaluation Understudy
# to find the quality of generated text
# checks n-grams overlap

# 1.0:      perfect match
# 0.5–0.7:  decent similarity
# < 0.1:    very weak
# ≈ 0:      no meaningful overlap
# --------------------------------------
# import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def bleu_score_single(reference: str, prediction: str) -> float:
    ref_tokens = tokenize(reference)
    pred_tokens = tokenize(prediction)

    if not pred_tokens:
        return 0.0

    smoothie = SmoothingFunction().method1
    return sentence_bleu([ref_tokens], pred_tokens, smoothing_function=smoothie)

# -------------------------------------------------------------
# 4) ROUGE : Recall Oriented Understudy for Gisting Evaluation
# to find the quality of a summarized text generated by machines
# --------------------------------------------------------------
# rouge1:	    Overlap of unigrams between prediction and reference
# rouge2:	    Overlap of bigrams
# rougeL:	    Longest common subsequence
# rougeLsum:    Summarization-based version (sentence-level LCS)

from rouge_score import rouge_scorer

rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

def rouge_scores(reference: str, prediction: str) -> dict:
    scores = rouge.score(reference, prediction)
    return {
        "rouge1_f1": scores["rouge1"].fmeasure,
        "rouge2_f1": scores["rouge2"].fmeasure,
        "rougeL_f1": scores["rougeL"].fmeasure,}

# -----------------------------------------------------------------------

# supplier evaluation data
supp_eval_df = executeQuery("select * from supplier_eval")
print(supp_eval_df)

# Pick a random question - answer for evaluation
import random

ndx = random.randint(0,len(supp_eval_df)-1)
print(f"Random number : {ndx}")
supp_eval_df.columns
ref_answer = supp_eval_df.loc[ndx,"ref_answer"]
gen_answer = supp_eval_df.loc[ndx,"gen_answer"]

print(ref_answer)
print(gen_answer)

# 1)
em = exact_match_score(ref_answer, gen_answer)
print(em)

# 2)
f1 = f1_score(ref_answer, gen_answer)
print(f1)

# 3)
bleu_sc = bleu_score_single(ref_answer, gen_answer)
print(bleu_sc)

# 4)
rogue_sc = rouge_scores(ref_answer, gen_answer)
print(rogue_sc)

# These measure do not take the Semantic meanings into consideration
# So, a high score does not necessarily mean "Greater similarity"

# 5) LLM-as-a-judge
# Judge LLM Evaluates on:
# ----------------------
#   semantic correctness
#   completeness
#   faithfulness
#   helpfulness

JUDGE_PROMPT_RAG = """
You are evaluating a RAG system answer.

Score the generated answer from 0.0 to 1.0 using:
1. Correctness against the reference answer
2. Faithfulness to the retrieved context
3. Completeness
4. Clarity

Return STRICT JSON only:
{
  "score": <float>,
  "reason": "<short explanation>"
}
"""
import json

def llm_judge_rag(ref_answer, gen_answer) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, response_format={"type": "json_object"},
        messages=[  {"role": "system", "content": JUDGE_PROMPT_RAG},
                    { "role": "user", "content": json.dumps({
                        "reference_answer": ref_answer, "generated_answer": gen_answer},
                    ensure_ascii=False)
            }
        ]
    )
    return json.loads(response.choices[0].message.content)

llm_judge = llm_judge_rag(ref_answer, gen_answer)
print(llm_judge)
























