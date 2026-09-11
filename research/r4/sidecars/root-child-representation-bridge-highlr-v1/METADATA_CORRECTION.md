# Additive correction to one descriptive READY field

Original frozen source/READY remain unchanged. The free-text `only_scientific_change`
field accidentally retains “boundedhighLR SFT8 2286be” from a mechanical description
rewrite. The correct description is **fixed higher-rate SFT8 adapter0ba42364183a311a8f5b67e4bac4e9294924c1dfb73f152a209811df09b78773**,
not RL4/2286be. The executable NEW_SHA, checkpoint path, config SHA, SPEC binding,
selection check, actual role-routing tests and weight/source closure all use the correct
highLR SFT8 checkpoint. No executable, scientific input or weight correction is needed.
This factual note is outside the original source closure; bind it separately at acceptance.
