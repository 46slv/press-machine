# Continuous neutral behavior in the legacy path — decision proposal

Status: design comparison only. No new DCTL variant has been adopted. The
v1.2.2 file remains a partial local maintenance candidate, not a completed
Density fix or a release. All previous versions are preserved.

Recommendation: consider **A2**, which removes the erroneous intercept while
preserving the value and existing left derivative at Threshold. It changes only
the lower knee whose span crosses zero. This is a new knee design choice;
the existing legacy specification does not select it over the other valid
behaviors below. Stop before production or experimental DCTL adoption until
that creative choice has been assessed.

Requested model: `gpt-6.1-sol`. Actual runtime model ID: **UNVERIFIED**.
No other writers or agents were used.

## Source and scope

This proposal starts from local commit
`2d8acba3264de6f0c7d5cae4b67b0d6600804a77`, whose v1.2.1 source is preserved
from accepted commit `430aa1528c55abedfc6328cec6873432a374f27d`.

- [v1.2.2 DCTL](../v1.2.2/press_machine_v1_2_2.dctl), lines 142–169:
  Pre-Saturation, Dynamic Density and legacy compressor; lines 178–193:
  Sat Density, its guard, reconstruction and the later saturation boost.
- [v1.2.1 fix record](../v1.2.1/FIX_RECORD.md), lines 3 and 10:
  this is a separate legacy lineage; its low-saturation gain and knee were
  explicitly retained by that earlier repair, rather than specified as bugs.
- [Migration notes](../../docs/MIGRATION_NOTES.md), lines 5, 12, 20–36, 44–46:
  the newer design is separate, retains protection against zero division,
  removes legacy Density and mapping controls, and redesigns the knee without
  promising preset compatibility.
- [Project README](../../README.md), line 5, and
  [algorithm design](../../docs/ALGORITHM.md), sections 1, 3 and 8:
  compression-only and a conventional knee are proposed for the newer core.
  They do not select a replacement legacy look.

Only the compressor, its use by Sat Density, and continuous chroma
reconstruction are discussed here. Dynamic Density remains driven by
`sat_pre`. Luma Mix extrapolation, color encodings, luma decomposition,
Density Compensation, the post-Density saturation boost, and gamut policy
keep their existing meanings. R2 DEV12 is outside this proposal.

## Exact cause and affected parameter region

Let `s = length(chroma_orig)`, `P = Pre_Saturation`, `x = P*s`,
`T = Threshold^3`, `k = max(Knee, 1e-6)`, and `rho = 1 + ln(Ratio)`.
Here legacy `k` is the half-width: the transition runs from `T-k` to `T+k`.
It must not be confused with the full-width convention in the newer core docs.

For `Ratio > 1`, define

```text
H(t) = 3t^2 - 2t^3, with t clamped to [0,1]
t(x) = clamp((x-T+k)/(2k), 0, 1)
L(x) = x + [T + max(x-T,0)/rho - x] H(t(x))
```

When `x <= T-k`, this also gives `L(x)=x`. At `Ratio=1`, source bypasses the
compressor and `L(x)=x`.

If `0 < T < k`, set `t0=(k-T)/(2k)` and `h0=H(t0)`. Then
`L(0)=T*h0 > 0`. Thus the raw positive floor exists precisely when

```text
Ratio > 1 and 0 < Threshold^3 < max(Knee, 1e-6).
```

Makeup must be positive for this floor to reach output. Sat Density additionally
changes luma when its mix is positive, compensation is below one, and the
incoming luma is nonzero. Luma Mix can intentionally produce negative luma;
the rational factor then attenuates its magnitude rather than darkening a
positive value. That existing extrapolation is not being revised.

For UI Knee `0.1`, the floor region is `0 < Threshold < 0.4641588834`.
Even Knee `0` uses the internal `1e-6` half-width and can have this floor when
`0 < Threshold < 0.01`. Threshold exactly zero has no intercept floor.
Ratio just above one enters this below-Threshold behavior because the source
uses `Ratio > 1` as a gate; the below-Threshold blend itself does not depend
on ratio strength. That existing parameter discontinuity is separate.

The v1.2.2 guard suppresses Sat Density only when `s <= 1e-6`. It leaves
`L(0)` intact, including when nonneutral input has Pre-Saturation zero. For
the default reproduction settings `T=.015625`, `k=.1`, `Ratio=4`, the raw
floor is `0.005996346474`. Just above the guard, the emitted chroma is about
`0.0059970771` and positive Y `.18` becomes about `.1778666401`.

## Valid alternatives and the creative decision

All alternatives below retain legacy `Threshold^3`, `1+ln(Ratio)`, Makeup
and the Ratio-one bypass. This avoids importing unrelated new-core mappings.

| Choice | Formula before Makeup | Behavior that must change |
| --- | --- | --- |
| A1: affine removal of the intercept | For `0<T<k` and `0<=x<T`, `F1=L(x)-T*h0*(1-x/T)`; otherwise `L(x)` | Removes part of the low-saturation lift only in the floor-producing lower knee. Changes its left derivative at Threshold. |
| **A2: removal preserving the threshold slope** | In the same region, `F2=L(x)-T*h0*(1-x/T)^2`; otherwise `L(x)` | Retains more low-saturation lift than A1, but removes its intercept. Recommended for its local change and simple polynomial preserving the threshold value and left derivative. |
| B: prevent compressor expansion | `FB=min(x,L(x))` | Makes the complete lower knee identity, including settings with no neutral floor. Preserves the curve above Threshold but changes the effective Knee response and removes the existing Ratio-one low-knee jump. |
| C: conventional quadratic knee | Use `ke=min(k,T)`, `lo=T-ke`, `hi=T+ke`; identity below `lo`, `x+(1/rho-1)*(x-lo)^2/(4ke)` inside, `T+(x-T)/rho` above `hi`; for `T=0`, `x/rho` | Replaces the knee response on both sides of Threshold and caps its effective width. This is the broadest look/UI-response change. |

A1 and A2 change the raw curve **only** for `Ratio>1`, `0<T<k`, `0<=x<T`.
They leave its values at or above Threshold and every knee with `k<=T`
unchanged. This
includes the existing low-saturation gain in knees whose lower edge is
nonnegative. The final effect is also absent if Makeup is zero.

In terms of the original detector, when `P>0` this raw-curve change spans
`0<=s<T/P`; with the reproduction settings and `P=1`, that is all chroma
lengths below `.015625`, not just the `1e-6` neighborhood. When `P=0`, every
input maps to `x=0`, so the old artificial output is removed at any original
chroma length. B instead changes the active lower knee
`max(0,T-k)<x<T` for all `T>0`, plus `x=0` when `k>T`, even if that knee
had no intercept defect. C potentially changes the entire old transition
`max(0,T-k)<x<T+k`; it also changes `0<x<k` when `T=0`.

There is no uniqueness from the requested invariants: the entire family
`Fp=L(x)-T*h0*(1-x/T)^p` for `p>=1` has zero intercept, nonnegative increasing
output on this lower interval, and matches the old curve at Threshold.
For `p>1`, it also preserves the left derivative there. Different `p` values
retain different amounts of lift. Choosing the lowest polynomial degree that
preserves value and first derivative motivates A2, but that is an engineering
recommendation, not an existing creative requirement.

At `x=.005`, the legacy curve yields `.009469006386`; A1 yields
`.005391490784`, A2 `.006696295776`, B `.005`, and C `.004767623914`.
Those are materially different saturation responses. The specification does
not establish whether the retained lift or compression-only behavior is the
intended legacy look. A different knee must therefore be assessed explicitly.

## Why A2 satisfies the neutral and sign invariants

On the affected lower interval, `L(x)=x+(T-x)H(t(x))`. A2 removes exactly
`T*h0` at zero and subtracts zero at Threshold. Its derivative is

```text
F2'(x) = L'(x) + 2*h0*(1-x/T)
L'(x)  = 1-H(t(x)) + (T-x)*H'(t(x))/(2k).
```

For `0<=x<T`, `0<=t<=1/2`, so `L'(x)>=1/2`; the added derivative is
nonnegative. Consequently `F2(0)=0`, `F2(x)>=0`, and it introduces no lower
branch reversal. At Threshold its added derivative is zero. The upper branch
is unchanged. The old curve already has different one-sided derivatives at
Threshold: `1/2` from the left and `(1+1/rho)/2` from the right. A2 preserves
that existing kink; it does not claim a globally C1 curve.

For a stable gain expression put `a=T/k` and `u=x/T` in the affected region:

```text
g2(x) = F2(x)/x
      = 1 + (1-u) [1/2 - (a^3/4)(1-u)(2-u)].
```

This expression is defined at `x=0`; no subtraction of two finite floors or
division by a tiny chroma norm is needed. Because `0<a<1` and `0<=u<1`,
`1<=g2<=1.5`, and

```text
g2(0) = 1.5 - 0.5*(T/k)^3.
```

For the reproduction settings this is `1.498092651367`. Hence `F2(x)` tends
to zero linearly. A1 instead has origin gain
`1+(3/4)*(T/k)*(1-(T/k)^2) = 1.114326477051` at those settings, illustrating
the creative difference. At `k=T`, `h0=0`, so both corrections vanish
continuously as a parameter change; they do not switch to a new finite look
when the lower edge first crosses zero.

## Continuous reconstruction and Density must be considered together

Changing only `L(0)` while retaining the hard reconstruction threshold would
leave a smaller mathematical step at `s=1e-6`. To remove that step, use a
finite gain throughout the chroma path, rather than divide `sat_out/sat_in`
and discard the chroma below that threshold. This is a numerical-policy change
that must accompany an adopted curve; no such source edit is made here.

This reconstruction change has a separate, explicit scope: for any settings
where the old path discarded positive chroma at `0<s<=1e-6`, it retains the
legitimate tiny vector instead. Sat Density uses its continuous scalar value
on both sides of the old guard. Thus the raw-curve locality above does not
claim identical RGB/Density behavior throughout that discarded interval.
There is no new protection range or enlarged epsilon.

Let `g(x)=F(x)/x` with its analytic zero limit. Proposed stage relationships are

```text
x = P*s
y = Makeup * F(x)
chroma_final = chroma_orig * [P * Makeup * g(x)]
Sat Density uses y, before the existing Density_SatBoost multiplier.
```

If Pre-Saturation is zero, the chroma gain and `y` are zero. If original
chroma is zero, its reconstructed vector is zero. For any continuous `F`
above, the chroma vector tends to zero from every direction. A nonnegative
gain cannot flip its direction; zero chroma simply has no hue.

For A2 the unchanged branches can also compute gain without unbounded ratios:

```text
Ratio <= 1: g=1.
x>=T and x>0:
  g=1-(1-1/rho)*(1-T/x)*H(t(x)).
x<T and k<=T:
  lo=T-k; if x<=lo, g=1;
  otherwise d=x-lo,
  g=1+((T-x)/k)*(d/k)*(d/x)*(3-d/k)/4.
x=0 and T=0: g=(1+1/rho)/2.
```

All ratios in these expressions are bounded by their branch conditions.
In the unchanged lower branch `0<d/x<=1`, `0<d/k<=1`, and
`0<(T-x)/k<1`, which also bounds its gain by `1.5`. The upper branch has
`1/rho<=g<=1`. With existing UI bounds Pre-Saturation `0..3`, Makeup `0..4`
and post-Density saturation multiplier `1..2`, the total proposed chroma gain
is at most `36`. This is a mathematical bound, not GPU precision proof.

Let `Yb` be luma after the existing Dynamic Density and Luma Density stages,
`d=Sat_Density`, and `c=Density_Comp`. Then the existing Sat Density equation is

```text
Yfinal = Yb * [(1-c)/(1+2*d*y) + c].
```

Since `y>=0` and tends to zero, its denominator is at least one and
`Yfinal` tends to `Yb` at neutral. This removes Sat-Density darkening at neutral
without overriding intentional Luma Density. Dynamic Density still uses `x`.
The existing saturation boost remains after Sat Density. If a curve is later
adopted, the graph must evaluate that same curve; its normalized identity
baseline and all LogC4 fixes remain intact.

## Focused evidence and limits

Run from the repository root:

```powershell
python -B "Press Machine/legacy/neutral-continuity-proposal/probe_proposals.py"
```

The comparison model uses the existing harness to execute actual legacy scalar
source statements for its baseline. Eight focused arithmetic groups cover the
source derivation, explicit correction equivalence, neutral/sign/monotonic
samples, analytic origin limits, Threshold slope preservation, unchanged
regions, old-guard continuity, and Ratio/Threshold/Pre/Makeup no-op boundaries.
No existing test suite or unrelated matrix is rerun. Complete output is in
`PROBE_RESULTS.txt`; inputs are fingerprinted there by normalized UTF-8 SHA256.

With UI Threshold `.25`, Knee `.1`, Ratio `4`, Makeup `1`, Sat Density `1`,
Compensation `0`, Dynamic Density `0`, Luma Mix `0`, and input Y `.18`:

| Compressor input x | Legacy | A1 | A2 | B | C |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | .005996346474 | 0 | 0 | 0 | 0 |
| .000001 | .005997077027 | .000001114319 | .000001498061 | .000001 | .000000999991 |
| .005 | .009469006386 | .005391490784 | .006696295776 | .005 | .004767623914 |
| .0078125 | .011261917651 | .008263744414 | .009762831032 | .0078125 | .007245175571 |
| .015625 | .015625 | .015625 | .015625 | .015625 | .013355702282 |
| .03 | .024930349917 | .024930349917 | .024930349917 | .024930349917 | .021634460892 |
| .12 | .059364364975 | .059364364975 | .059364364975 | .059364364975 | .059364364975 |

At original chroma lengths `.999999e-6` and `1.000001e-6`, v1.2.2 gives Y
`.180000000000` and `.177866640117`. The A2 mathematical gain path instead
gives `.179999460700` and `.179999460699`, with no branch at that threshold.
At neutral it gives Y `.18` and zero chroma. With a nonproblematic lower knee
(UI Threshold `.5`, Knee `.1`, Ratio `4`, x `.075`), legacy and A2 both give
`.0828125`; B instead gives `.075`.

These are Python double arithmetic and source-model checks. There is no new
DCTL, GPU compile, Resolve rendering, visual assessment, or bit-exact host
neutrality claim. Floating-point dot/length errors and tiny-value handling
would need host evidence after a design choice. Existing signed-luma behavior,
Luma Mix extrapolation, gamut control, and Ratio-one gating are not repaired by
this proposal. No installation, push, PR, merge or release was performed.

The finite outcome is a mathematically specified comparison and recommendation.
An assessed choice of the desired low-saturation response is still required
before creating an experimental legacy variant.
