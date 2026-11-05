# Native entry spelling and layout

Read from the installed official DaVinci Resolve Studio 21.1.0.14 SDK on
SHIRO-WS, 2026-11-05. Local SDK directory:
`C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/DaVinciCTL`.

`README.txt` line 73 requires the function definition exactly as-is, including
parameter types and names. Line 77 and `Gain.dctl` line 1 contain this literal:

```c
__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)
{
```

The brace is on its own next line in official `Gain.dctl`. File provenance:

| Installed file | Bytes | SHA256 |
| --- | ---: | --- |
| README.txt | 42073 | `9a227dfc276cea11be2b7ac3d3d080a77e0cd21f6b7d1b4cb09bf0d99bb12efe` |
| Gain.dctl | 248 | `eba494ebf7f8bec6dd9147c6f6d5c3830aa62abc71a92fa09ee2b2cdbb769088` |

At d3964ac, the candidate entry wrapped after p_Y, with the opening brace at
the end of the following argument line. In the preserved R6 evidence the
candidate failed `resolve:ValidateDCTL(source_string)` with a transform-argument
error, while official Gain passed the identical source-string call (nil return).
A generated single-line identity body also failed a missing-return parser check.

The source now matches the official entry's physical layout. This addresses
a plausible line-sensitive parser incompatibility; it is not proof the native
validation error is fixed. A later GUI-owned native validation, Color Page
load and GPU execution must establish that. This source-only repair turn used
no GUI, Resolve console, staging, installation or host validation.

`SourceTests.test_canonical_sdk_entry_layout` always enforces the literal line
and next-line brace. When this installed SDK is present, it also checks them
against the official README/Gain files. The literal regression remains portable
on machines without Resolve. Four-control and excluded-feature checks remain.
