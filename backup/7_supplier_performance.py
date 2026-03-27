import psycopg2 as psy
import pandas as pd
import re
import random
from openai import OpenAI
import numpy as np

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

def SearchData(cursor, cond, qtype, limit=5):
    try:
        qtype = qtype.lower().strip()

        if qtype not in ['meta', 'lex', 'emb', 'reg']:
            data = "Invalid Query Type. Valid values are 'lex','meta','emb','reg'"
        else:
            if qtype == "lex":
                query = f'''
                    select * from supplier_data where supplier_id in ( 
                    select supplier_id from supplier where content_tsv @@ websearch_to_tsquery('english', 
                    '{cond}'))
                    limit {limit} ; '''
            elif qtype == "meta":
                query = f'''
                        select * from supplier_data where supplier_id in ( 
                            select supplier_id from supplier where metadata @> '{cond}') limit {limit} ; '''
            elif qtype == "emb":
                response = client.embeddings.create(model='text-embedding-3-small', input=cond)
                txt_embed = response.data[0].embedding
                query = f''' select * from supplier_data where supplier_id in (
                            select supplier_id from supplier order by embedding <=> '{txt_embed}'::vector 
                            limit {limit} ) '''
            else:
                query = cond

            query = re.sub('[\\n]', ' ', query).strip()
            # print(query)

            cursor.execute(query)
            data = cursor.fetchall()

            cols = [c[0] for c in cursor.description]
            data = pd.DataFrame(data,columns=cols)

    except Exception as e:
        data = str(e)
        data = re.sub("\\n"," ",data).strip()
        data = ' '.join(data.split())

    # return(data,cursor)
    return(data)

# -----------------------------------------------------------------------------------------------

# import os
# print(os.getcwd())

# Connect to the pgVector database using the credentials
ret = ConnectDB("pgvector.txt")
if ret[0] == "SUCCESS":
    conn = ret[1]
    cursor = ret[2]
else:
    print("Error / Exception during ConnectDB")

print(conn)
print(cursor)


# to create the embeddings, we will use OpenAI embeddings (size 1536)
client = OpenAI()

# Convert every Content into an embedding; and update table against each supplier ID
# -----------------------------------------------------------------------------------
for i in range(len(data)):
    supplierid,content = data.loc[i, "supplier_id"], data.loc[i,"content"]
    # print(supplierid)
    # print(content)

    response = client.embeddings.create(model="text-embedding-3-small", input=content)
    embedding = response.data[0].embedding  # get the embeddings for the selected review text

    # Convert to PostgreSQL vector format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    # Update database
    cursor.execute("UPDATE supplier SET embedding = %s WHERE supplier_id = %s;", (embedding_str,supplierid))

conn.commit()

# 25/3/2026

# write a prompt to fetch data from the table using embedding search
prompt = "fast delivery"
response = client.embeddings.create(model='text-embedding-3-small', input=prompt)
print(response)
# extract only the embeddings
prompt_embed = response.data[0].embedding

# form the query to run the embedding search
qry = f''' select sd.*
        from supplier s
        join supplier_data sd
        on sd.supplier_id = s.supplier_id
        order by s.embedding <=> '{prompt_embed}'::vector
        limit 10;
        '''
print(qry)

# execute the query
def executeQuery(query):
    try:
        data = ''

        cursor.execute(query)
        data = cursor.fetchall()

        cols = [c[0] for c in cursor.description]
        data = pd.DataFrame(data, columns=cols)

    except Exception as e:
        data = "Exception." + str(e)

    return(data)

data = executeQuery(qry)
print(data)

# evaluation
# "fast delivery"

data.columns
data[['supplier_id','on_time_delivery_pct','late_deliveries']].sort_values('on_time_delivery_pct', ascending=False)









