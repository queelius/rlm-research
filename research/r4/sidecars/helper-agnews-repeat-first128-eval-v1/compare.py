"""Exact saved raw scorer; fixed repeated128 versus broader and c32."""
import reuse_eval
reuse_eval.execute("compare.py",globals(),[
    ("same512-training-seed-replica-source-to-raw-v1","same512-repeat128-versus-broader-source-to-raw-v1",1),
    ('primary="c32 versus fixed replica step8"','primary="broader seed1 versus fixed repeat128 step8"',1),
    ('secondary="seed1 versus seed2 descriptive paired contrast"','secondary="c32 versus fixed repeat128 endpoint"',1),
    ("same research-exposed512; training-seed replication, not new data or independent trainer implementation",
     "same research-exposed512; repeated-first128 mechanism comparison, not new data, independent items, or universal breadth effect",1),
    ("replica_new_physical_calls=128","repeat128_new_physical_calls=128,broader_reference_physical_calls_reused=128",1),
])
