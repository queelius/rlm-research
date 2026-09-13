"""Native boolean spans and G4 reward contrasts only, never a loss or output repair."""
import re
import study as s


def native_spans(record,order):
    try:
        parsed=s.interface.parse(record['text'],'vector',order);tokens=record['completion_ids'];tok=s.tokenizer()
        text=tok.decode(tokens,skip_special_tokens=True);assert text==record['text']
        start=re.search(r'"eligible"\s*:\s*\[',text);assert start,'literal unescaped eligible key required for span qualification'
        end=text.index(']',start.end());matches=list(re.finditer(r'\b(?:true|false)\b',text[start.end():end]))
        spans=[(start.end()+m.start(),start.end()+m.end()) for m in matches]
        assert len(spans)==len(order) and [text[lo:hi]=='true' for lo,hi in spans]==parsed['vector']
        offsets=[];previous=''
        for i in range(len(tokens)):
            prefix=tok.decode(tokens[:i+1],skip_special_tokens=True)
            assert prefix.startswith(previous) and text.startswith(prefix),'nonmonotone native prefix decode'
            offsets.append((len(previous),len(prefix)));previous=prefix
        decisions=[];used=set();joint=[]
        for position,(lo,hi) in enumerate(spans):
            indices=[i for i,(a,b) in enumerate(offsets) if b>a and b>lo and a<hi]
            assert indices and offsets[indices[0]][0]<=lo and offsets[indices[-1]][1]>=hi
            assert not used.intersection(indices),'one token intersects multiple candidate values';used.update(indices)
            overlap=[i for i in indices if offsets[i][0]<lo or offsets[i][1]>hi];joint.extend(overlap)
            decisions.append(dict(position=position,implementation_id=order[position],raw_boolean=text[lo:hi],character_span=[lo,hi],
                token_indices=indices,boundary_overlap_token_indices=overlap,token_ids=[tokens[i] for i in indices]))
        return dict(qualified=True,decisions=decisions,exclusive_boolean_token_feasible=not joint,boundary_overlap_token_indices=joint,
            completion_ids_sha256=s.digest(tokens),text_sha256=s.digest(text),text_hash_semantics='canonical JSON string digest',native_token_character_offsets=offsets,
            no_mask_or_loss_created=True)
    except (ValueError,TypeError,KeyError,AssertionError) as error:return {'qualified':False,'reason':f'{type(error).__name__}: {error}','no_repair':True}


def group_contrast(rows,order,gold):
    valid=[r for r in rows if r['semantic_valid']]
    result=dict(planned_samples=4,observed_rows=len(rows),valid_samples=len(valid),full_G4_valid=len(rows)==4 and len(valid)==4)
    if not result['full_G4_valid']:return {**result,'candidate_contrasts':None,'invalid_group_retained':True}
    correct=[[int((key in set(r['ids']))==(key in gold)) for key in order] for r in rows]
    advantages=[[correct[i][j]-sum(correct[k][j] for k in range(4) if k!=i)/3 for j in range(len(order))] for i in range(4)]
    variable=[j for j in range(len(order)) if len({r[j] for r in correct})>1]
    def rloo(values):return [v-sum(values[k] for k in range(4) if k!=i)/3 for i,v in enumerate(values)]
    return {**result,'correctness_by_sample':correct,'candidate_RLOO_advantages':advantages,'variable_candidate_positions':variable,
        'joint_BA_RLOO_advantages':rloo([r['balanced_accuracy'] for r in rows]),'joint_exact_RLOO_advantages':rloo([int(r['exact']) for r in rows]),
        'no_optimizer_or_loss':True,'unweighted_candidate_correctness_diagnostic_not_a_chosen_training_objective':True}
