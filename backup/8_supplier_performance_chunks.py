# chunking strategies
# -------------------
import psycopg2 as psy
import pandas as pd
import json # used in the metadata creation
import re
from openai import OpenAI

# read the connection file and connect to postgres database
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
        ret.extend(["EXCEPTION", "ConnetDB(). " + str(e),""])

    return (ret)


def supplier_record_to_chunks(row: dict):
    try:
        supplier_id = row["supplier_id"]

        chunks = [
            {
                "supplier_id": supplier_id, "chunk_type": "delivery",
                "content": (
                    f"Supplier {supplier_id}. Delivery details. "
                    f"On-time delivery: {row['on_time_delivery_pct']}%. "
                    f"Average lead time: {row['avg_lead_time_days']} days. "
                    f"Late deliveries: {row['late_deliveries']}. "),
                "metadata": {"category": row["category"], "region": row["region"]}
            },
            {
                "supplier_id": supplier_id, "chunk_type": "quality",
                "content": (
                    f"Supplier {supplier_id}. Quality details. "
                    f"Quality score: {row['quality_score']}/100. "
                    f"Defect rate: {row['defect_rate_pct']}%. "
                    f"Supplier performance score: {row['supplier_performance_score']}."),
                "metadata": {"category": row["category"], "region": row["region"]}
            },
            {
                "supplier_id": supplier_id, "chunk_type": "compliance",
                "content": (
                    f"Supplier {supplier_id}. Compliance details. "
                    f"Compliance score: {row['compliance_score']}/100. "
                    f"Contract breach count: {row['contract_breach_count']}. "),
                "metadata": {"category": row["category"], "region": row["region"]}
            },
            {
                "supplier_id": supplier_id, "chunk_type": "risk",
                "content": (
                    f"Supplier {supplier_id}. Risk details. "
                    f"Risk score: {row['risk_score']}. "
                    f"Category: {row['category']}. "
                    f"Region: {row['region']}."),
                "metadata": {"category": row["category"], "region": row["region"]}
            }
        ]
    except Exception as e:
        chunks = [{"status":"Exception." + str(e)}]

    return chunks

# create the OpenAI client to create chunk embeddings
client = OpenAI()

# 3) insert the chunks into the table
def insert_chunks(cursor, chunks):
    try:
        ret = -1
        document_id = ''

        insert_sql = """
            INSERT INTO document_chunks
            (document_id, supplier_id, chunk_id, chunk_type, chunk_content, chunk_metadata, chunk_embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

        for chunk_id, chunk in enumerate(chunks):
            chunkid = str(chunk_id + 1)
            ctype = chunk["chunk_type"]

            document_id = "/".join(["DOC", chunk["supplier_id"], chunkid, ctype.upper()])

            response = client.embeddings.create(model="text-embedding-3-small", input=chunk['content'])
            embedding = response.data[0].embedding  # get the embeddings for the selected review text
            # Convert to PostgreSQL vector format
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"

            cursor.execute(insert_sql, (document_id, chunk["supplier_id"], chunkid, ctype,
                                        chunk["content"], json.dumps(chunk["metadata"]),
                                        embedding_str ))
        ret = 1

    except Exception as e:
        print("Exception in insert_chunks()." + str(e))
        ret = -1

    return (ret)

# 4) general queries
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

# 5) Connect to the pgVector database using the credentials
ret,conn,cursor = ConnectDB("pgvector.txt")
print(ret)

# Get all the supplier data from the database
qry = "select * from supplier_data;"
supplier_data = executeQuery(qry)
print(supplier_data)

# 7) create the Chunks
supplier_chunks = []

for i in range(len(supplier_data)):
    row = supplier_data.loc[i]
    row = dict(row)
    chunk = supplier_record_to_chunks(row)
    supplier_chunks.append(chunk)


print(f"Number of chunks for each supplier = {len(chunk)}")
print(f"Total chunks created = {len(supplier_chunks)}")
supplier_chunks[0]

# 8) Insert all the chunks into the table
for chunk in supplier_chunks:
    ret = insert_chunks(cursor,chunk)
    if ret == -1:
        break

conn.commit()

# 9) Verify chunks
qry = "select * from document_chunks;"
document_chunk_data = executeQuery(qry)
print(len(document_chunk_data))
document_chunk_data.columns

document_chunk_data[['chunk_type','chunk_content']]

conn.close()



