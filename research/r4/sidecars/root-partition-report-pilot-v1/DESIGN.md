# Purchase-join boundary pilot

Question rq:sufficient-interface: when A/B purchase evidence crosses a fixed
recursive boundary, do ordinary advisory child reports omit information needed
for correct composition, and does a hand-designed incidence report improve
exact set correctness at measured cost?

Four synthetic worlds each contain12 customers and48 records. Query: return all
customers who bought both A and B. The four global answer sets contain3/5/7/9
customers. Customer and record IDs and record orders use generator seeds
981409091–094. This is explicitly engineered difficulty, with no rejection
sampling or outcome-conditioned reroll. All records are synthetic purchases
without chronology. No training data, model updates or train/evaluation split
is used in this initial instrument pilot; no held-out training generalization
claim is possible. Future learned interfaces must freeze a disjoint generator
namespace and hold out operation/structure combinations.

Each world has two semantics-preserving3×16 partitions. Co-located chunks
contain four complete customers each. Cross chunks assign a customer's record
slot k to (customer index+k)%3; A and B occupy different slots/chunks. No cross
chunk contains any qualifying A/B pair. Exact local-winner projections therefore
all equal[[],[],[]] across worlds despite distinct answers. That is a deliberate
lossy negative control, not a discovered model deficit. Original input remains
visible to every parent, so the parent can recover from bad reports itself.

At each of8 world/partition coordinates, make3 extraction child calls and3
ordinary child calls. Ordinary reports explicitly serve the global query and
may include partial facts, with unconstrained format. Extraction returns raw
[record_id,customer_id,product] triples. Full evidence and lossy local-winner
projections reuse exactly the same3 actual extraction calls, including any
mistakes. Invalid extraction is null, never silently empty or repaired. These
two projections change the report relation and length together. Each parent
receives all original records,3 advisory reports and the same final JSON-array
answer instruction. Three parents plus two direct calls give11 actual calls
per coordinate,88 total. No report duplication counts as another model call.

Sampling seeds981409101/111 alternate by world, paired over partitions and
parent arms. Child chunk i uses the world's seed+i, paired across extraction
and ordinary calls. There is one realization per world, not two within-world
seed replicates. PLAN freezes coordinate, child and parent order before inference.
Temperature0.6,top_p0.95,top_k0, no grammar,768 child tokens,256 parent/direct-short
tokens,2560 direct-expanded tokens. Expanded direct has the same prompt and a
larger output ceiling equal to3×768+256. This is not equal realized compute;
prefill, repeated calls and actual stopping differ and are reported separately.

Primary readout: full-versus-ordinary exact-set correctness on8 paired
coordinates and number of worlds correct under both partitions (denominator4).
Report cross and co-located cells separately, paired wins/losses/ties, partition
answer flips, malformed/unavailable endpoints and cost. Secondary: lossy control,
direct baselines, extraction triple precision/recall and exactness, report-implied
answers, and final answer agreement with those implications where defined.
Ordinary text has no trusted symbolic implication parser; retain it for audit.
CPU_ORACLE contains exact nonrecursive solution plus exact extraction→projection→
symbolic-composition diagnostics, with no model calls. Valid evidence and
complete extraction are distinct. A correct parent answer alone cannot prove
report use. Four engineered worlds do not support population inference.

Released Qwen3-4B-Instruct-2507 revision cdbee75f17c01a7cc42f958dc650907174af0554
serves every role, no research adapters. Reuse cached checkpoint and qualified
HF BF16 SDPA loading conventions. Save native prompt IDs, generated IDs, actual
generation configuration, sampling, checkpoint pins and every request/response.
Fixed one-level decomposition with ordinary HF calls is an interface diagnostic;
it does not evaluate sampled autonomous RLM planning, learned report selection,
the production Responses transport or an IPython root service.

Single A10040GB estimate,1800s outer cap,1650s work including import/cold load,
120s cleanup allowance. No GPU run occurred in preparation. Every call and
11-call episode is an immutable checkpoint; interrupted results and unrun slots
remain explicit. No automatic retry or outcome-based replacement. If interrupted,
audit retained outputs and prepare an additive continuation with exact missing
requests; do not rerun completed calls under a resume label.

Promote only interface feasibility if ordinary reports lose boundary relations
and incidence improves correctness. Replicate on fresh worlds before training.
If direct/exact methods match, revise any recursion-specific explanation. If all
model arms succeed, increase task complexity in a separately frozen successor;
if extraction fails, improve that stage before asserting synthesis failure.
