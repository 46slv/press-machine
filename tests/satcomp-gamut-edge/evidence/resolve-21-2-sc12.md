# SatComp SC-12: Resolve 21.2 constant probe

Resolve Studio 21.2.0.6 on Windows/CUDA reproduced the built-in DCTL ResolveFX failure observed on 21.1.0.14. This is not acceptance of the eight-control product route.

Candidate: 769a014c22c5d857fd771a659672171340a753b1 (PR #19). Synthetic fixture: same frame zero at 640 x 360, 24 fps, full-range float32 RGBA ZIP EXR, alpha 1. Built-in DCTL ResolveFX Global Blend was 1.000. Captures used Resolve's official in-app Workspace > Console (Python 3) and a disposable project, not MCP or external scripting.

| Route | Independently verified result |
| --- | --- |
| OFF | Decoded RGBA bits match the input in all 230,400 pixels. |
| Direct Color DCTL | Every RGBA pixel equals (8.125, 8.125, 0.375, 1). |
| Built-in DCTL ResolveFX | R and G each contain 54,000 zeros and 7,200 values of 16. Alpha is unchanged; all decoded RGBA bits match 21.1.0.14. |

EXR SHA-256 pins, independently checked before linear float32 decoding:

| Capture | SHA-256 |
| --- | --- |
| Input | 9e2e348fcfa7a9a42f04d9e5f010be57a3067d8c8b82594ee9fa6c1a67fd709a |
| 21.2 OFF | 86b42b2f015ed56b3e9ee55b19c361f8b24955eda87d1e7b77e5f19d9b5d391f |
| 21.2 Direct Color | 2eebb9b62337debf656ea8eab521651d81b455f7f891d9559e80f7936ae9bbbc |
| 21.2 Built-in ResolveFX | 9c8c01a61b9084eb100299890a0616cb2239d427f3d821842453c315fa6ae73d |
| 21.1 Built-in ResolveFX | e8a9bca21bdd38a40a57ade17e61f87d063daf4c3286defbbe1f7bef8a6a6e47 |

No 21.2 LogC4, LogC3, DaVinci Intermediate, blurred-edge, or partial/zero-alpha regression ran after the constant gate failed. The 21.1 reports remain separate. Production assets and preferences were unchanged; capture files are retained in the local acceptance archive.
