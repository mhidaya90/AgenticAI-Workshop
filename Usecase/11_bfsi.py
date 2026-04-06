from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import psycopg2 as psy
import pandas as pd
import re
import random
from openai import OpenAI
import numpy as np

load_dotenv()
apikey= os.getenv('OPENAI_API_KEY')
print(apikey)
client =OpenAI(api_key=apikey)


#create model
llm = ChatOpenAI(api_key=apikey)

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

ret = ConnectDB("pgvector.txt")
if ret[0] == "SUCCESS":
    conn = ret[1]
    cursor = ret[2]
else:
    print("Error / Exception during ConnectDB")

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

    return (data)

def SearchBFSIData(cursor, cond, qtype, limit=5):
    """
    BFSI RAG Search Function
    qtype options:
        - 'lex'  : keyword search in case_summary / resolution_notes
        - 'meta' : metadata filter (JSON-like conditions on categorical fields)
        - 'emb'  : semantic similarity search using embeddings
        - 'reg'  : raw SQL query passed directly
    """
    try:
        qtype = qtype.lower().strip()

        if qtype not in ['meta', 'lex', 'emb', 'reg']:
            data = "Invalid Query Type. Valid values are 'lex','meta','emb','reg'"
        else:
            if qtype == "lex":
                # Keyword search in text fields
                query = f"""
                    SELECT * FROM bfsicases
                    WHERE case_summary ILIKE '%{cond}%'
                       OR resolution_notes ILIKE '%{cond}%'
                    LIMIT {limit};
                """

            elif qtype == "meta":
                # Metadata filter (example: region='West' AND product_type='Home Loan')
                query = f"""
                    SELECT * FROM bfsicases
                    WHERE {cond}
                    LIMIT {limit};
                """

            elif qtype == "emb":
                # Semantic similarity search using pgvector
                response = client.embeddings.create(model='text-embedding-3-small', input=cond)
                txt_embed = response.data[0].embedding
                query = f"""
                    SELECT * FROM bfsicases
                    ORDER BY summary_embedding <-> '{txt_embed}'::vector
                    LIMIT {limit};
                """

            else:  # 'reg'
                query = cond

            query = re.sub('[\\n]', ' ', query).strip()
            cursor.execute(query)
            rows = cursor.fetchall()

            cols = [c[0] for c in cursor.description]
            data = pd.DataFrame(rows, columns=cols)

    except Exception as e:
        data = str(e)
        data = re.sub("\\n", " ", data).strip()
        data = ' '.join(data.split())

    return data

#embedding search
qry = "select case_id,case_summary,summary_embedding from bfsicases where summary_embedding IS NULL";
data = SearchBFSIData(cursor, qry, qtype="reg")
print(data.head())

print(data.columns)
print(data['case_id'].tail(20))
print(len(data))

#create embeddings

for i in range(len(data)):
    caseid, summary = data.loc[i, "case_id"], data.loc[i, "case_summary"]
    # print(supplierid)
    # print(content)

    response = client.embeddings.create(model="text-embedding-3-small", input=summary)
    embedding = response.data[0].embedding  # get the embeddings for the selected review text

    # Convert to PostgreSQL vector format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    # Update database
    cursor.execute("UPDATE bfsicases SET summary_embedding = %s WHERE case_id = %s;", (embedding_str, caseid))

conn.commit()

#search by embeddings
def search_by_embedding(cursor, query_text, limit=5):
    # Step 1: Generate embedding for the query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    query_embed = response.data[0].embedding

    # Step 2: Run similarity search in Postgres
    sql = f"""
        SELECT case_id, case_summary, policy_reference
        FROM bfsicases
        ORDER BY summary_embedding <-> '{query_embed}'::vector
        LIMIT {limit};
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

search_by_embedding(cursor,
    "borrower asked for release of funds but insurance document is pending",
    limit=5)

search_by_embedding(cursor,
    "customer disputes EMI amount after rate revision and requests servicing support",
    limit=5)

search_by_embedding(cursor,
    "name mismatch in income proof",
    limit=10)

# qry="SELECT case_id, case_summary, channel FROM bfsicases WHERE knowledge_article_tag='Disbursement Hold' ORDER BY summary_embedding <-> embedding('release funds blocked due to missing document') LIMIT 10;"
#
# #data= executeQuery(qry)
# data = SearchBFSIData(cursor, qry, qtype="reg")
# # print(data.head())
# print(data)

conn.close()

#NLQ
def ExecuteNLPrompt(cursor, user_query, limit=10):
    """
    Execute BFSI queries from natural language.
    Strategy:
      1. Try SQL filters
      2. Fallback to ILIKE keyword search
      3. Fallback to embedding similarity
    """

    try:
        uq = user_query.lower()
        rows = []
        query = None

        # --- Structured filters ---
        if "high" in uq and "home loan" in uq and "west" in uq:
            query = """
                SELECT case_id, product_type, region, case_status, priority
                FROM bfsicases
                WHERE LOWER(priority)='high'
                  AND LOWER(product_type)='home loan'
                  AND LOWER(region)='west'
                  AND LOWER(case_status) IN ('open','pending documents')
                LIMIT {limit};
            """.format(limit=limit)

        elif "average actual tat" in uq and "q3 2025" in uq:
            query = """
                SELECT process_name, risk_band, AVG(actual_tat_hours) AS avg_tat
                FROM bfsicases
                WHERE EXTRACT(QUARTER FROM created_date)=3
                  AND EXTRACT(YEAR FROM created_date)=2025
                GROUP BY process_name, risk_band;
            """

        elif "closed cases" in uq and "csat" in uq:
            query = """
                SELECT product_type, region, COUNT(*) AS closed_count
                FROM bfsicases
                WHERE case_status='Closed'
                  AND csat_score < 3.0
                GROUP BY product_type, region;
            """

        elif "exception" in uq and "highest transaction" in uq:
            query = """
                SELECT case_id, transaction_amount_inr
                FROM bfsicases
                WHERE exception_flag='Yes'
                ORDER BY transaction_amount_inr DESC
                LIMIT 10;
            """

        elif "fraud review" in uq and "severe-risk" in uq and "north" in uq:
            response = client.embeddings.create(model="text-embedding-3-small",
                                                input="suspicious duplicate documentation")
            txt_embed = response.data[0].embedding
            query = f"""
                SELECT case_id, case_summary, risk_band, region, process_name
                FROM bfsicases
                WHERE LOWER(risk_band)='severe'
                  AND LOWER(process_name)='fraud review'
                  AND LOWER(region)='north'
                ORDER BY summary_embedding <-> '{txt_embed}'::vector
                LIMIT {limit};
            """

        elif "collateral valuation gap" in uq or "manual review" in uq:
            query = f"""
                SELECT case_id, case_summary, policy_reference
                FROM bfsicases
                WHERE case_summary ILIKE '%collateral%'
                   OR case_summary ILIKE '%manual%'
                LIMIT {limit};
            """

        # --- Embedding fallback for "similar" queries ---
        elif "similar" in uq or "semantically" in uq or "close to" in uq:
            response = client.embeddings.create(model="text-embedding-3-small", input=user_query)
            txt_embed = response.data[0].embedding
            query = f"""
                SELECT case_id, case_summary
                FROM bfsicases
                ORDER BY summary_embedding <-> '{txt_embed}'::vector
                LIMIT {limit};
            """

        # --- Default: keyword search ---
        else:
            query = f"""
                SELECT case_id, case_summary
                FROM bfsicases
                WHERE case_summary ILIKE '%{user_query}%'
                   OR resolution_notes ILIKE '%{user_query}%'
                LIMIT {limit};
            """

        # Execute query
        query = re.sub('[\\n]', ' ', query).strip()
        cursor.execute(query)
        rows = cursor.fetchall()

        # Fallback: if still empty, use embeddings
        if not rows:
            response = client.embeddings.create(model="text-embedding-3-small", input=user_query)
            txt_embed = response.data[0].embedding
            fallback_query = f"""
                SELECT case_id, case_summary
                FROM bfsicases
                ORDER BY summary_embedding <-> '{txt_embed}'::vector
                LIMIT {limit};
            """
            cursor.execute(fallback_query)
            rows = cursor.fetchall()

        cols = [c[0] for c in cursor.description]
        return pd.DataFrame(rows, columns=cols)

    except Exception as e:
        err = str(e)
        err = re.sub("\\n", " ", err).strip()
        err = ' '.join(err.split())
        return err


df = ExecuteNLPrompt(cursor, "Find cases mentioning collateral valuation gap", limit=5)
print(df)

df = ExecuteNLPrompt(cursor,"Find severe-risk cases related to fraud review in the North region similar to suspicious duplicate documentation",limit=5)
print(df)

df = ExecuteNLPrompt(cursor,"What is the average actual TAT by process_name and risk_band for cases created in Q3 2025?")
print(df)

prompts = [
    "Find cases mentioning collateral valuation gap",
    "List all cases where the notes mention duplicate request and the resolution was closed as duplicate",
    "Show only high-priority Home Loan cases from the West region that are still open or pending documents",
    "Retrieve escalated cases handled by Disbursement Control with SLA breach = Yes",
    "Find cases semantically similar to: borrower asked for release of funds but insurance document is pending",
    "Surface cases similar to customer disputes EMI amount after rate revision and requests servicing support",
    "What is the average actual TAT by process_name and risk_band for cases created in Q3 2025?",
    "Count the number of closed cases by product_type and region where CSAT score is below 3.0",
    "Which 10 cases have the highest transaction_amount_inr among cases flagged with exception_flag = Yes?",
    "Find severe-risk cases related to fraud review in the North region similar to suspicious duplicate documentation",
    "Search for complaints about sanction delays for SME Working Capital and include only cases with actual_tat_hours > sla_hours",
    "For KYC verification cases, retrieve records similar to name mismatch in income proof and return the most common root causes",
    "List policy references most frequently associated with escalated cases that mention AML alerts in the summary or notes",
    "Show cases tagged with Disbursement Hold where the summary is semantically close to release funds blocked due to missing document and group them by channel"
]

for i, p in enumerate(prompts, start=1):
    print(f"\n--- Prompt {i}: {p} ---")
    df = ExecuteNLPrompt(cursor, p, limit=5)
    print(df)




