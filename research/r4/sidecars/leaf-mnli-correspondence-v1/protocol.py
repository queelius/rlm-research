"""MNLI public-text identity, matched schemas and immutable 80-coordinate plan."""
import collections
import itertools
import random
import statistics
import unicodedata
import study as s

MASTER=981431001
LABELS=('entailment','neutral','contradiction')
GENRES=('government','slate','telephone','travel')
ARMS=('matching','constant')
DECODERS=('free','shape')
SYSTEM=('You are a text classification assistant. Classify every supplied input record and return '
        'only the requested final answer in the requested format. Do not write code, use tools, '
        'provide explanations, or reason aloud.')


def normalize(text):return ' '.join(unicodedata.normalize('NFKC',text).casefold().split())
def pair_group(row):return s.digest([normalize(row['premise']),normalize(row['hypothesis'])])
def public_id(row):return 'm'+pair_group(row)[:12]


def choose_constant(ids,tokenizer):
    def length(tag):return len(tokenizer.encode(s.serialize({'tag':tag}),add_special_tokens=False))
    lengths=[length(tag) for tag in ids];hist=collections.Counter(lengths);median=statistics.median(lengths)
    target=min(hist,key=lambda x:(-hist[x],abs(x-median),x))
    candidates=[]
    for index in range(256):
        tag='m'+s.digest([MASTER,'constant-candidate',index])[:12]
        if tag not in ids:candidates.append(dict(index=index,tag=tag,tokens=length(tag)))
    chosen=min(candidates,key=lambda x:(abs(x['tokens']-target),x['index']))
    return chosen['tag'],dict(chosen=chosen,modal_target=target,median=median,
        source_field_token_lengths=dict(zip(ids,lengths,strict=True)),histogram=dict(hist),candidates=candidates,
        matching_field_tokens=sum(lengths),control_field_tokens=len(ids)*chosen['tokens'],
        residual_control_minus_matching=len(ids)*chosen['tokens']-sum(lengths),
        field_definition='compact JSON one-field object {"tag":ID}, no special tokens',
        selection_uses_labels_or_performance=False,source_ids_resampled=False)


def plan(contexts):
    cells=list(itertools.product(ARMS,DECODERS));orders=list(itertools.permutations(cells))
    rng=random.Random(MASTER);rng.shuffle(orders);blocks=list(range(16));rng.shuffle(blocks)
    result=[]
    for block in blocks:
        ci,repeat=divmod(block,2)
        ordered=list(orders[ci%len(orders)])
        if repeat:ordered.reverse()
        for position,(arm,decoder) in enumerate(ordered):
            row=dict(context_index=ci,repeat=repeat,seed=981431101+block,arm=arm,decoder=decoder,
                     kind='batch',size=48,block=block,pair_position=position,dispatch_order=len(result))
            row['id']=s.digest(['mnli80',row]);result.append(row)
        # Fixed reference is part of every block, not selected after batch outcomes.
        row=dict(context_index=ci,repeat=repeat,seed=981431101+block,arm='matching',decoder='free',
                 kind='singleton',size=1,block=block,pair_position=4,dispatch_order=len(result))
        row['id']=s.digest(['mnli80',row]);result.append(row)
    return result


def selected_context(context,row):
    if row['kind']=='batch':return context
    record=min(context['records'],key=pair_group)
    return {**context,'records':[record]}


def schema(size):
    return {'json':{'type':'array','minItems':size,'maxItems':size,'items':{
        'type':'object','properties':{'tag':{'type':'string','pattern':'^m[0-9a-f]{12}$'},
        'label':{'type':'string','enum':list(LABELS)}},'required':['tag','label'],'additionalProperties':False}}}


def request(context,row,constant):
    records=[{k:r[k] for k in ('id','premise','hypothesis')} for r in context['records']]
    tag=('copy that record\'s displayed id exactly' if row['arm']=='matching'
         else 'write the constant '+constant+' for every record, not its displayed id')
    prompt=('For every supplied record, classify the relation of its hypothesis to its premise. '
        'entailment means the hypothesis must be true given the premise; contradiction means the hypothesis '
        'must be false given the premise; neutral means neither conclusion follows. '
        'Do not infer the relation label from a record’s position in the batch or from its ID.\n'
        f'Return exactly {len(records)} JSON objects in one array, in the displayed record order. '
        'Each object must have exactly the string fields tag then label. For tag, '+tag+'. '
        'For label, use exactly entailment, neutral, or contradiction. No additional text.\n'
        'Input records (id, premise, hypothesis):\n'+s.serialize(records))
    body=dict(model=s.MODEL['alias'],messages=[dict(role='system',content=SYSTEM),dict(role='user',content=prompt)],
        temperature=.5,top_p=1,top_k=-1,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,
        seed=row['seed'],max_tokens=3072,return_token_ids=True,chat_template_kwargs={'enable_thinking':False},cache_salt=s.ROOT.name)
    if row['decoder']=='shape':body['structured_outputs']=schema(len(records))
    return body


def null_row(row,reason):
    return dict(coordinate=row,available=False,strict_correct=None,strict_bounds=[0,row['size']],reason=reason)
