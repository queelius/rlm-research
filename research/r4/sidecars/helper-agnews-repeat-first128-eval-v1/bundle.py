"""Same512 collector and exact8-step gate, with the actual repeated-data manifest."""
import reuse_eval

reuse_eval.execute("bundle.py",globals(),[
    ("seed2_eval_","repeat128_eval_",14),
    ("agnews-same512-training-seed-replica-eval-v1","agnews-same512-repeat128-versus-broader-eval-v1",1),
    ("helper-agnews-native-hf-eightstep-seed2-v1","helper-agnews-repeat-first128-eightstep-v1",1),
    ("abafc45c35a038aee97ccb7a4dce4dee8c2ce03b111a9430bd2c17022ac20853",
     "1ebe94d3339e1e742c4f984ffa3f00f9cb9813e239747b7a390f70c70e5b7119",1),
    ('ARM = "rl_seed2_step8"','ARM = "rl_repeat128_step8"',1),
    ('\'"arm": "rl_seed2_step8"\'','\'"arm": "rl_repeat128_step8"\'',1),
    ("APPROVE_TRAINING_SEED_REPLICATION","APPROVE_BREADTH_VERSUS_REPEAT_FIRST128",1),
    ("training_seed_replication_not_new_dataset=True,",
     "training_seed_replication_not_new_dataset=False,mechanism_repeat128_vs_broader=True,",1),
    ('study.ROOT,study.RL,study.rl,study.ARMS = ROOT,TRAIN,core,(ARM,)',
     '''study.ROOT,study.RL,study.rl,study.ARMS = ROOT,TRAIN,core,(ARM,)
# State qualification must authenticate the actual repeat128 training manifest.
# Endpoint prompts/gold remain the SAME original broad heldout512 functions.
study.DATA=TRAIN
study.gold=old_study.gold
study.schedule=old_study.schedule''',1),
])
