# Independent TREC retention readout

This is a historically evaluated retention panel, not fresh generalization.
Raw native token IDs were re-decoded and matched to the immutable request, endpoint, and host labels.

- c32: 121/128; available 128/128
- rl_step8: 122/128; available 128/128
- sft_step8: 121/128; available 128/128

Paired record changes:
- c32_to_rl_step8: 1 wins, 0 losses, net 1
- c32_to_sft_step8: 0 wins, 0 losses, net 0
- rl_step8_to_sft_step8: 0 wins, 1 losses, net -1
