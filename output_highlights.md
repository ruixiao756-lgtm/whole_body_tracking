# Training Highlights for output.log

Selected 12 representative iterations from the full log.

| Iteration | Timesteps | Composite | Mean reward | Episode length | Anchor pos reward | Anchor ori reward | Anchor lin vel error | Anchor ang vel error | Reasons |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 1966080 | 0.1828 | -0.7000 | 8.0000 | 0.0065 | 0.0046 | 0.8884 | 3.6198 | start; timeline 0% |
| 333 | 656670720 | 0.8455 | 31.1600 | 500.0000 | 0.1409 | 0.4578 | 0.4427 | 1.1841 | best Mean episode length |
| 528 | 1040056320 | 0.9298 | 36.2700 | 481.8900 | 0.2728 | 0.4678 | 0.3095 | 0.9030 | timeline 25% |
| 1054 | 2074214400 | 0.9603 | 39.0300 | 495.0300 | 0.2953 | 0.4713 | 0.3087 | 0.9037 | timeline 50% |
| 1160 | 2282618880 | 0.9723 | 39.2800 | 490.4900 | 0.3135 | 0.4743 | 0.2915 | 0.8391 | best Episode_Reward/motion_global_anchor_pos |
| 1279 | 2516582400 | 0.9717 | 40.8100 | 500.0000 | 0.3090 | 0.4724 | 0.2968 | 0.8514 | best Mean reward |
| 1442 | 2837053440 | 0.9741 | 39.8000 | 495.0400 | 0.3063 | 0.4754 | 0.2761 | 0.8108 | best Metrics/motion/error_anchor_lin_vel (lowest) |
| 1455 | 2862612480 | 0.9731 | 39.7700 | 495.0300 | 0.3050 | 0.4761 | 0.2848 | 0.8010 | best Metrics/motion/error_anchor_ang_vel (lowest) |
| 1461 | 2874408960 | 0.9760 | 40.0300 | 500.0000 | 0.3076 | 0.4757 | 0.2846 | 0.8122 | best composite score |
| 1584 | 3116236800 | 0.9503 | 38.5000 | 500.0000 | 0.2550 | 0.4757 | 0.3250 | 0.8770 | timeline 75% |
| 1983 | 3900702720 | 0.9424 | 37.4600 | 495.1200 | 0.2290 | 0.4794 | 0.3638 | 0.9065 | best Episode_Reward/motion_global_anchor_ori |
| 2101 | 4132700160 | 0.9384 | 37.1200 | 490.4300 | 0.2288 | 0.4777 | 0.3627 | 0.8982 | end; timeline 100% |
