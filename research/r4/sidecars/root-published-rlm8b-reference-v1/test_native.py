"""Catch native text/usage mismatch and falsely promoted worker terminals."""
import pytest
import collect as c
import rv_study as s
def raw(text='FINAL(Answer: 2)'):
    return dict(model='qwen3-8b',prompt_token_ids=[1,2],choices=[dict(index=0,finish_reason='stop',token_ids=[3],message=dict(role='assistant',content=text))],usage=dict(prompt_tokens=2,completion_tokens=1,total_tokens=3))
class Tok:
    def decode(self,ids,**kw):return 'FINAL(Answer: 2)'
def test_native_mismatch_not_available():
    assert c.authenticate(raw(),[1,2],Tok())['content']=='FINAL(Answer: 2)'
    with pytest.raises(ValueError):c.authenticate(raw('FINAL(Answer: 3)'),[1,2],Tok())
    with pytest.raises(ValueError):c.authenticate(raw(),[1],Tok())
def test_terminal_requires_actual_native_root_branch():
    result=dict(terminal=dict(final='Answer: 2',error=None),events=[dict(kind='iteration',value=dict(final='Answer: 2',response='FINAL(Answer: 2)'))])
    call=dict(role='root',native_verified=True,content='FINAL(Answer: 2)')
    assert c.final_capture(result,[call],0)
    assert not c.final_capture(result,[dict(call,native_verified=False)],0)
    assert not c.final_capture(result,[call],1)

def test_real_tokenizer_prefix_flat_ids():
    tok=s.tokenizer();messages=[dict(role='system',content='Use the REPL.'),dict(role='user',content='Count records.')]
    ids=c.prompt_ids(tok,messages)
    assert isinstance(ids,list) and len(ids)>10 and all(type(i)==int for i in ids)
    assert tok.decode(ids,skip_special_tokens=False).endswith('<|im_start|>assistant\n')
