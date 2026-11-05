# DEV-12 Revision 2 reference contract

Authority is the [approved DEV-12 R2 brief](https://app.notion.com/p/3e4fd279a6f381cf85f1e121b69f86f7),
[R4 implementation route](https://app.notion.com/p/3e4fd279a6f38139a0f1da3cc05b8f4f)
and SAT-001..020, fetched 2026-11-05. Local authority snapshots preserve the brief
and requirement properties. Main baseline is `a926635f52411fcd15486790008d38169fcea623`.
The historical PR is reference only; this code is a new R2 implementation.

## Scalar law

S = 100 C/L, C = hypot(a,b), in D65 Oklab. S is a product scale, not percent or
an upper limit. Values above 100 are valid. A=Compression/100, P=Softness/100,
m=1-A, T=Threshold, K=2TP, lo=T(1-P), hi=T(1+P).

| Region | f(S) |
|---|---|
| K=0, S<=T | S |
| K=0, S>T | T+m(S-T) |
| K>0, S<=lo | S |
| K>0, lo<S<hi | S-A(S-lo)^2/(2K) |
| K>0, S>=hi | T+m(S-T) |

For valid controls this is monotone, compression only and C1 at soft-knee
boundaries. Threshold=0 degenerates to the hard knee. Compression=100 makes
the high region T. The DCTL factors the knee multiplication to avoid an
unnecessary square before division, with the same published polynomial.
No Ratio, ceiling, Density, skin selection, weighting or gamut mapping is added.

## Color references, checked 2026-11-05

- [Blackmagic, DaVinci Wide Gamut Intermediate v1.1, August 2021, pp.3–4](https://documents.blackmagicdesign.com/InformationNotes/DaVinci_Resolve_17_Wide_Gamut_Intermediate.pdf):
  published DWG<->XYZ matrices (8 decimal places), D65 xy=(.3127,.3290), and
  piecewise DI encode/decode. The printed matrices are used directly, rather
  than deriving a slightly different inverse from rounded primaries.
- [W3C CSS Color 4, 2026-11-03 CRD, conversion code](https://www.w3.org/TR/2026/CRD-css-color-4-20261103/#color-conversion-code):
  current D65 XYZ<->Oklab matrices. Nonlinear LMS uses a signed real cube root;
  inverse LMS uses a cube. CSS gamut mapping and powerless-hue conventions
  are outside this contract. DWG already uses D65, so no adaptation is added.
- [Oklab author reference](https://bottosson.github.io/posts/oklab/) provides the
  model background; the required conversion constants come from W3C above.

DI constants: A=.0075, B=7, C=.07329248, M=10.44426855,
linear cut=.00262409, code cut=.02740668. Encode uses the linear branch at/below
linear cut; decode uses it at/below code cut. Finite negatives use that linear
branch without clipping. The official mapping table is approximate: at linear
40, its formula gives .903124492603 while the table prints .903125. Tests allow
one final printed decimal unit for table anchors; the formula remains intact.

Path: DI decode -> linear DWG -> XYZ D65 -> signed-root Oklab. Eligible colors
scale a and b by f(S)/S; L is kept. Reverse the same path and DI encode.

## Numerical and identity policy

Bypass, Compression=0 and untouched S return the original encoded RGB, without
an inverse color conversion. Equal-channel neutral also returns the original
RGB before the printed matrices can create residual chroma. Domain guards are
L<=1e-6, C<=1e-7, S<=1e-7 or a nonfinite intermediate. Every intermediate and
final output is checked; an overflow returns the original RGB. FLT_MAX in the
check is the IEEE binary32 representability limit, not a creative ceiling.
The double oracle checks intermediate float32 representability independently;
it does not emulate every float32 arithmetic rounding step.

The DCTL computes a signed root using positive-magnitude pow and restores the
sign. General pow on negative values is never used. The oracle uses math.cbrt.
Finite negative/HDR RGB is neither clamped nor gamut mapped. Nonfinite input
is returned as supplied; the finite-output requirement applies to finite input.
The RGB-only transform has no alpha operation; host alpha behavior remains R6.

Float rounding can move a reconstructed Lab value across an epsilon. In the
current fixture, double C=9.990367548e-8 becomes native C=1.000007614e-7,
crossing the C guard in two states. Maximum encoded difference there is
1.986e-12. Direct Lab guard tests pin equality and both sides at the actual
binary32 constants. No widened epsilon or luminance weighting is introduced.

The scalar contract assumes UI-domain controls. Programmatic out-of-range
controls are unsupported. The DCTL returns original RGB on overflow rather
than promising a meaningful compressor mapping at unrepresentable magnitudes.

## Evidence boundaries

Independent Python double oracle, native float32 execution of the actual DCTL,
and target Resolve execution are separate evidence. Native shim macros model
only the documented RGB entry point/math calls; they do not validate Resolve's
GPU compiler, UI parsing, buffer range, alpha or interactivity.

The prebuild corpus includes negative-LMS and finite negative-L samples. For
example linear DWG (.01,.01,.9) produces negative Oklab L and intentionally
returns identity. Near a zero LMS component, signed cube root magnifies input
rounding; the worst fixture is documented in PREBUILD_REPORT.md. These are
named wide-gamut Oklab risks for host/visual qualification, not reasons to add
a hidden color repair. This slice does not establish final product acceptance.
