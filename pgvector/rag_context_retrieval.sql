create or replace function rag_context_retrieval (
    query_embedding vector(1536),
    file_names text[]
) returns table (
    chunk_text text
) as $$
begin
    return query
    select
        t.chunk_text
    from
        file_chunks as t
    where
        t.file_name = any(file_names)
    order by
        t.embedding <-> query_embedding
    limit 1;
end;
$$ language plpgsql;