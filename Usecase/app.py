from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
from dotenv import load_dotenv
import os
from openai import OpenAI
import psycopg2 as psy




app = Flask(__name__)

load_dotenv()
apikey= os.getenv('OPENAI_API_KEY')
print(apikey)
client =OpenAI(api_key=apikey)

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

#natural language execute function
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

        # cols = [c[0] for c in cursor.description]
        cols = [c[0] for c in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        return df.to_dict(orient="records")
        # return pd.DataFrame(rows, columns=cols)



    except Exception as e:
        # err = str(e)
        # err = re.sub("\\n", " ", err).strip()
        # err = ' '.join(err.split())
        # return err
        err = str(e)
        err = re.sub("\\n", " ", err).strip()
        err = ' '.join(err.split())
        return {"error": err}


# REST API endpoint
@app.route("/api/execute", methods=["POST"])
def execute_prompt():
    data = request.get_json()
    user_query = data.get("prompt")
    results = ExecuteNLPrompt(cursor, user_query)
    return jsonify({"results": results})

# Frontend route
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)