create or replace function rag_context_retrieval (
    query_embedding vector(1536),
    file_names text[],
    project_id text
) returns table (
    chunk_text text,
    similarity float
) as $$
begin
    return query
    select
        t.chunk_text,
        t.embedding <-> query_embedding as similarity
    from
        file_chunks as t
    where
        t.file_name = any(file_names)
        and t.project_id = project_id
    order by
        t.embedding <-> query_embedding
    limit 3;
end;
$$ language plpgsql;