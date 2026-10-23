/** Run actual pinned GBrain storage + search with shared real cached embeddings.
 * This is a component adapter, not hosted GBrain or raw-document ingestion.
 * Upstream is MIT, copyright 2026 Garry Tan; see README.md and upstream pin.
 */
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const upstream = process.env.RESEARCH_GBRAIN_SOURCE;
if (!upstream || !process.env.GBRAIN_HOME) throw new Error('Explicit isolated upstream/config paths required');
const root = resolve(upstream);
const mod = (p: string) => import(pathToFileURL(resolve(root, p)).href);
const { configureGateway } = await mod('src/core/ai/gateway.ts');
const { PGLiteEngine } = await mod('src/core/pglite-engine.ts');
const { hybridSearch } = await mod('src/core/search/hybrid.ts');
const { readProjectionSnapshot, installPageProjection } = await mod('src/core/page-state/projections.ts');

// No credentials/fallback providers: supplied vectors were actually produced by
// the recorded OpenAI embedding API. The upstream injectable query-vector seam
// skips only the external embedding request, not the upstream search algorithm.
configureGateway({ embedding_model: 'openai:text-embedding-3-small',
  embedding_dimensions: 1024, env: {} });

const input = JSON.parse(await Bun.stdin.text());
const engine = new PGLiteEngine();
const clock = () => performance.now();
const start = clock();
try {
  await engine.connect({});
  await engine.initSchema();
  await engine.setConfig('search.reranker.enabled', 'false');
  const initialized = clock();
  for (const event of input.events) {
    if (!/^e[0-9a-f]+$/.test(event.id) || event.embedding.length !== 1024) throw new Error('Invalid public event/vector');
    const slug = 'evidence/' + event.id;
    await engine.putPage(slug, { type: 'note', title: event.text,
      compiled_truth: event.text, frontmatter: { research_source_id: event.id } });
    const snapshot = await readProjectionSnapshot(engine, slug, 'default', {allowUnsealed:true});
    if (!snapshot) throw new Error('Written page missing');
    await installPageProjection(engine, snapshot, [{chunk_index:0,
      chunk_text:event.text, chunk_source:'compiled_truth',
      embedding:new Float32Array(event.embedding), model:'openai:text-embedding-3-small'}], {seal:true});
  }
  const indexed = clock();
  let observedEmbedding = false;
  let metadata: unknown = null;
  const options: any = {
    mode:'balanced', limit:input.events.length, expansion:false,
    queryEmbedFn: () => new Float32Array(input.query.embedding),
    onQueryEmbedding: () => {observedEmbedding = true;},
    onMeta: (m:unknown) => {metadata = m;},
  };
  const result = await hybridSearch(engine, input.query.text, options);
  const searched = clock();
  const ranks = result.map((r:any) => ({id:r.slug.slice('evidence/'.length), score:r.score,
    source:r.chunk_source, cosine:r.cosine ?? null}));
  if (!observedEmbedding) throw new Error('Semantic arm did not execute; refusing to call keyword fallback hybrid');
  console.log(JSON.stringify({status:'completed',case_id:input.query.id,rankings:ranks,
    semantic_embedding_used:observedEmbedding,metadata,
    seconds:{initialization:(initialized-start)/1000,indexing:(indexed-initialized)/1000,
      search:(searched-indexed)/1000},
    scope:'actual upstream PGLite/hybrid component; shared prefiltered records and cached OpenAI vectors; no graph extraction, reranker, synthesis or provider generation'}));
} finally { await engine.disconnect(); }
