
-- See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-optimize-performance-pgvector#indexing
-- Set ivfflat.probes to 1/10th the value of lists
-- Set lists to ~ rows / 1000

SET ivfflat.probes = 5;

CREATE INDEX idx_libraries_ivfflat_embedding
ON     libraries
USING  ivfflat (embedding vector_cosine_ops)
WITH  (lists = 50);
