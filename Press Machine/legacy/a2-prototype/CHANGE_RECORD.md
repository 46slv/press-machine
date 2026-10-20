# A2 implementation record

Basis: approved proposal at `7e1870cc5a2690d72f37653b39c899c5e6a284b0`.
The candidate copies the preserved legacy v1.2.2 source and changes only its
provenance header, the compressor/gain helper and its uses, the Density guard,
and graph evaluation. It keeps all other source payload unchanged, as enforced
by the focused test's complete payload restoration comparison to v1.2.1.

## Approved curve

Let `x=sat_pre`, `T=Threshold^3`, `k=max(Knee,1e-6)` and `rho=1+ln(Ratio)`.
Let `L(x)` denote the original scalar curve before Makeup. For `Ratio>1`,
`0<T<k`, and `0<=x<T` only:

```text
t0=(k-T)/(2k)
h0=3*t0^2-2*t0^3
F(x)=L(x)-T*h0*(1-x/T)^2.
```

Every other raw-curve region retains `F(x)=L(x)`. In the changed region the
helper computes its analytic gain without subtracting finite floors:

```text
a=T/k; u=x/T; v=1-u
g(x)=1+v*(.5-.25*a^3*v*(2-u)).
```

This includes `g(0)=1.5-.5*(T/k)^3`, so `F(0)=0` and `F(x)` tends to zero.
The polynomial keeps the Threshold value and left derivative. It retains some
low-saturation expansion and does not substitute proposal B or C.

## Other finite branches

`legacy_a2_gain` is shared by the transform and graph. It handles Ratio one
before taking a logarithm. Threshold zero uses
`1-(1-1/rho)*H((x+k)/(2k))`, whose zero-input value is `(1+1/rho)/2`.
For a lower knee with `k<=T`, it either returns identity or the unchanged
lower curve as a product of bounded ratios. At/above Threshold it evaluates
`1-(1-1/rho)*(1-T/x)*H(t)`, with positive x guaranteed by the earlier branches.
All helper divisions have nonzero denominators under the existing UI mapping.

The transform now uses:

```text
sat_gain=legacy_a2_gain(sat_pre,T,k,Ratio)
sat_out=sat_pre*sat_gain*Makeup
chroma_final=chroma_orig*(Pre_Saturation*Makeup*sat_gain).
```

The later Density saturation boost is unchanged. Sat Density uses `sat_out`
without v1.2.2's small-chroma mask, so it follows the emitted pre-boost chroma
continuously. Dynamic Density still uses `sat_pre`. No tiny epsilon was widened
and no universal RGB clamp was introduced.

The graph now calls the same helper at its existing `plot_x` input. Makeup
display scaling and the normalized identity baseline remain unchanged.

## Source evidence and review boundaries

- [Candidate DCTL](press_machine_a2_prototype.dctl): `legacy_a2_gain`, main
  saturation/Density/recombination blocks and graph helper call.
- [Focused tests](tests/test_a2_prototype.py): executes those actual source
  statements, compares all analytical branches to the approved equation,
  and checks unrelated payload and retained contracts.
- [Original v1.2.1](../v1.2.1/press_machine_v1_2_1.dctl), accepted source commit
  `430aa1528c55abedfc6328cec6873432a374f27d`.
- [v1.2.2 partial candidate](../v1.2.2/press_machine_v1_2_2.dctl), local commit
  `2d8acba3264de6f0c7d5cae4b67b0d6600804a77`.
- [Approved proposal](../neutral-continuity-proposal/PROPOSAL.md), preserved as
  a historical pre-approval document; its former decision-pending status is
  superseded for this prototype by the user's explicit A2 approval.

The source is suitable for the next host/visual trial, not certified by these
tests. The rounding and remaining policy limitations are listed in README.md.
