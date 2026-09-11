"""Authenticated wrong-route output is observed invalid0, never executed or repaired."""
import json
import re
import study as s

def verified_response(raw,body,source,tokenizer):
    if raw.get('model')!=s.MODEL['alias'] or len(raw.get('choices',[]))!=1:raise ValueError('actual model/single branch differs')
    choice=raw['choices'][0];message=choice.get('message') or {};incoming=raw.get('prompt_token_ids');outgoing=choice.get('token_ids');usage=raw.get('usage') or {}
    if incoming!=source['actual_native_prompt_token_ids'] or not isinstance(outgoing,list) or any(type(v)!=int for v in outgoing):raise ValueError('actual native token identity unavailable/different')
    if usage.get('prompt_tokens')!=len(incoming) or usage.get('completion_tokens')!=len(outgoing):raise ValueError('native token usage disagrees')
    finish=choice.get('finish_reason')
    if message.get('role')!='assistant' or finish not in ('stop','length','tool_calls'):raise ValueError('unverified returned assistant branch')
    tools=message.get('tool_calls') or []
    if tools:
        # Authenticate parsed function envelopes against exact generated native bytes, not tool text alone.
        content_ids=outgoing[:-1] if outgoing and outgoing[-1] in (151645,151643) else outgoing
        decoded=tokenizer.decode(content_ids,skip_special_tokens=False,clean_up_tokenization_spaces=False)
        spans=list(re.finditer(r'<tool_call>\s*(.*?)\s*</tool_call>',decoded,re.S))
        if len(spans)!=len(tools):raise ValueError('native tool-envelope count differs')
        remaining=[];cursor=0
        for match,tool in zip(spans,tools):
            envelope=json.loads(match[1]);function=tool.get('function') or {}
            args=function.get('arguments');args=json.loads(args) if isinstance(args,str) else args
            if envelope!={'name':function.get('name'),'arguments':args}:raise ValueError('native tool-envelope function/arguments differ')
            remaining.append(decoded[cursor:match.start()]);cursor=match.end()
        remaining.append(decoded[cursor:])
        if ''.join(remaining).strip()!=(message.get('content') or '').strip():raise ValueError('native tool-envelope surrounding text differs')
        # Returning no scalar content makes the unchanged strict parser assign observed invalid0.
        return None,finish,usage
    decoded=tokenizer.decode(outgoing,skip_special_tokens=True,clean_up_tokenization_spaces=False)
    if not isinstance(message.get('content'),str) or decoded!=message['content']:raise ValueError('native completion text differs')
    if finish=='tool_calls':return None,finish,usage # Authenticated raw wrong-route text without parsed functions.
    return message['content'],finish,usage
