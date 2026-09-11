"""Pure bounded support decision; candidate cursor is not Adam's cursor."""
def needs_group(mixed):
    if not 0<=len(mixed)<=4 or any(type(x)is not bool for x in mixed):raise ValueError('invalid group support flags')
    return len(mixed)<2 or (len(mixed)<4 and sum(mixed)<2)

def validate_prefix(mixed):
    if not 2<=len(mixed)<=4 or needs_group(mixed):raise ValueError('not a completed legal stopping prefix')
    for length in range(2,len(mixed)):
        if not needs_group(mixed[:length]):raise ValueError('groups sampled after stopping rule')
    return 'update' if any(mixed) else 'noop'

def transition(completed_windows,old_policy,window,mixed,new_policy):
    if window!=completed_windows+1 or not 1<=window<=4:raise ValueError('stale or skipped candidate window')
    decision=validate_prefix(mixed)
    if decision=='noop':
        if new_policy is not None:raise ValueError('no-op cannot mutate policy or optimizer')
        policy=old_policy
    else:
        if new_policy is None or new_policy['step']!=old_policy['step']+1 or new_policy['adapter_sha256']==old_policy['adapter_sha256']:raise ValueError('exactly one real fresh update required')
        policy=new_policy
    return {'completed_windows':window,'next_window':window+1,'optimizer_steps':policy['step'],'policy':policy,'decision':decision}
