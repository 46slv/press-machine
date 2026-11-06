# Press Machine / SatComp — DEV-12 R2

## Current R2 numerical repair, not a deployed version

This branch also repairs precision loss at nearly cancelling LMS values without changing the R2 color model or guards. See [current repair and remaining model boundary](docs/BOUNDARY_REPAIR_REPORT.md) and [exact-candidate host handoff](docs/BOUNDARY_HOST_HANDOFF.md). The 30-test native suite passes. Resolve/GPU, alpha, real-material performance and user acceptance remain pending. The L-guard jump and exact-model signed-root cusp are not fixed by this arithmetic repair.

## Earlier isolated stability work

This branch adds a same-contract scalar precision repair and a separate, unapproved continuous-domain proposal. See [diagnosis and comparisons](docs/STABILITY_REPORT.md) and [next Resolve checks](docs/STABILITY_HOST_HANDOFF.md). The reported blue L-guard jump is a product-domain conflict; the scalar repair alone does not remove it. Neither new artifact has Resolve/GPU or user visual acceptance.


Local development candidate for high-saturation compression in DaVinci Resolve
Color Page. Input and output must be **DaVinci Wide Gamut / DaVinci Intermediate**.
Resolve host qualification and user visual acceptance are pending. This candidate
has not been installed, published or merged.

The current source includes a conditioned high-tail evaluation and the official
SDK entry layout. See [source correction results](docs/REPAIR_REPORT.md) and
[current host handoff](docs/REPAIR_HOST_HANDOFF.md). Resolve validation of
this exact numerical-repair candidate is pending. The first prebuild/R6 results describe
the earlier d3964ac candidate and are preserved as historical evidence.

`dctl/PressMachine_R2.dctl` has four controls:

| Control | Range | Default |
|---|---|---|
| Threshold S | 0–200, step .1 | 25 |
| Compression % | 0–100, step .1 | 0 |
| Softness % | 0–100, step .1 | 20 |
| Bypass | checkbox | off |

S=100*C/L in D65 Oklab; it is not a percentage or a cap. Compression 50% is
2:1, 75% is 4:1, 90% is 10:1 and 100% is a limiter above the knee. Softness is
relative to Threshold: T25/20% has full knee width 10 S. Compression=0, Bypass
and untouched colors return the original encoded RGB exactly. Eligible colors
reduce Oklab chroma while preserving L and hue. No gamut/tone mapping or clipping
is performed inside SatComp.

## Use the correct node input

In an unmanaged/source-space workflow use:

`Source -> CST In -> SatComp -> CST Out`

Set CST In's input gamut/gamma to the actual source. Set its Output Color Space
to DaVinci Wide Gamut and Output Gamma to DaVinci Intermediate. Disable tone
mapping and gamut mapping before SatComp. CST Out starts from DWG/Intermediate
and converts to the destination. Delivery rendering belongs after SatComp and
is outside the numerical f(S) contract.

If RCM, timeline or group management already supplies actual DWG/DI RGB at the
SatComp node, use SatComp directly and let project/output management handle the
output. Do not add a CST that interprets already converted DWG/DI as the camera
source again: that double conversion is unsupported. Direct Rec.709, camera
log or linear RGB into SatComp is also unsupported. There is no space detection
or internal color-space selector.

## Local prebuild checks

Python 3.11+ and an existing C++17 compiler are required; no third-party Python
packages are needed. On Windows the build script finds an installed Visual
Studio C++ toolchain. On other systems set CXX or provide clang++/g++ on PATH.

```powershell
python -m unittest discover -s tests -v
python tools/scalar_measure.py --output-dir build/scalar-review-unique
```

Use a fresh output-directory name for each measurement. `scalar_measure.py`
compiles the actual DCTL through a native float32 shim, checks the original
corpus against its unchanged frozen budget and measures two separate expanded
scalar corpora. It does not adopt a larger tolerance or overwrite the first
report. See [correction evidence](docs/REPAIR_REPORT.md),
[historical first prebuild](PREBUILD_REPORT.md), and [reference contract](docs/CONTRACT.md).
Do not treat these checks as Resolve/GPU/alpha or image-quality certification.
