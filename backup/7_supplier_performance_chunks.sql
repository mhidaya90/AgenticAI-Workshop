-- drop table document_chunks;
-- 1) table creation

CREATE TABLE document_chunks (
	document_id	TEXT PRIMARY KEY,
    supplier_id TEXT,
	chunk_id BIGSERIAL,
    chunk_type TEXT,        -- e.g. delivery, risk, compliance
    chunk_content TEXT,
    content_tsv TSVECTOR GENERATED ALWAYS AS ( to_tsvector('english', coalesce(chunk_content,''))) STORED,
    chunk_metadata JSONB,
    chunk_embedding VECTOR(1536),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- 2) check table creation
select * from document_chunks;

-- 3) index creation
-- 1) Lexical Search
CREATE INDEX IF NOT EXISTS idx_docchunk_content_tsv ON document_chunks USING GIN (content_tsv);

-- 2) Fast metadata filtering (optional but useful): GIN: Generalized Inverted Index
CREATE INDEX IF NOT EXISTS idx_docchunk_metadata ON document_chunks USING GIN (chunk_metadata);

-- 3) Vector index for similarity search (choose one)
CREATE INDEX IF NOT EXISTS idx_docchunk_embedding ON document_chunks USING hnsw (chunk_embedding vector_cosine_ops);


select count(1) from document_chunks;

select * from document_chunks;

-- 4) populate the table with the chunks



