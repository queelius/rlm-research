"""Mechanical exact-text reconstruction from preserved paper v2 TeX."""
import difflib,re,tarfile
import rv_study as s
def extract():
    with tarfile.open(s.PAPER) as archive:tex=archive.extractfile('appendix/sec3-methods.tex').read().decode()
    listings=re.findall(r'\\begin\{lstlisting\}\[style=customstyle\]\n(.*?)\\end\{lstlisting\}',tex,re.S)
    base,diff=listings[0],listings[2];result=base
    # Misaligned printed hunk indices are not executable patch coordinates.
    lines=diff.splitlines();i=0;changes=[]
    while i<len(lines):
        if lines[i].startswith('-') and not lines[i].startswith('---'):
            before=lines[i][1:];i+=1;after=[]
            while i<len(lines) and lines[i].startswith('+') and not lines[i].startswith('+++'):after.append(lines[i][1:]);i+=1
            replacement='\n'.join(after)
            if result.count(before)!=1:raise ValueError('paper replacement must occur once')
            result=result.replace(before,replacement);changes.append(dict(before=before,after=replacement));continue
        i+=1
    context_warning=next(l[1:] for l in lines if l.startswith('+IMPORTANT: You have a total'))
    result=result.replace('\n\nYour context is', '\n\n'+context_warning+'\n\nYour context is',1)
    marker='```\nIn the next step, we can return FINAL_VAR(final_answer).'
    if result.count(marker)!=1:raise ValueError('closed final example boundary changed')
    result=result.replace(marker,'```\nFINAL_VAR(final_answer)\n\nIn the next step, we can return FINAL_VAR(final_answer).')
    return dict(tex=tex,base=base,published_diff=diff,reconstructed=result,actual_diff=''.join(difflib.unified_diff(base.splitlines(True),result.splitlines(True),fromfile='paper-v2-base',tofile='paper-v2-Qwen8B-reconstruction')),replacements=changes)
def render(template,context):
    # One format pass resolves the three metadata fields and doubled example braces.
    return template.format(context_type='str',context_total_length=len(context),context_lengths=[len(context)])
