import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.0.0";
import { OpenAI } from "https://esm.sh/openai@4.0.0";
import { corsHeaders } from "../_shared/cors.ts";

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const { query, files, project_id } = await req.json();

  // Generate embedding for the query
  const openai = new OpenAI({
    apiKey: Deno.env.get("OPENAI_API_KEY"),
  });

  const embeddingResponse = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input: query,
  });

  const queryEmbedding = embeddingResponse.data[0].embedding;

  const supabaseClient = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_ANON_KEY") ?? "",
    {
      global: {
        headers: { Authorization: `Bearer ${Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")}` },
      },
    }
  );

  const { data, error } = await supabaseClient.rpc("rag_context_retrieval", {
    query_embedding: queryEmbedding,
    file_names: files,
    project_id: project_id,
  });

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 500,
    });
  }

  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    status: 200,
  });
});