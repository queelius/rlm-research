"""Accurate CPU reductions for persisted FP32 LoRA gradient vectors."""
import math

def compare(a,b,chunk=1_000_000):
    if a.shape!=b.shape or a.ndim!=1: raise ValueError("paired flat vectors required")
    aa=bb=ab=dd=0.0
    for start in range(0,a.numel(),chunk):
        x=a[start:start+chunk].double();y=b[start:start+chunk].double();d=x-y
        aa+=float(x.dot(x));bb+=float(y.dot(y));ab+=float(x.dot(y));dd+=float(d.dot(d))
    return {"elements":a.numel(),"difference_l2":math.sqrt(dd),"reference_l2":math.sqrt(aa),
            "relative_l2":math.sqrt(dd/aa) if aa else math.inf,
            "cosine":ab/math.sqrt(aa*bb) if aa and bb else math.nan,
            "accumulator":"CPU float64 chunked dot products"}
