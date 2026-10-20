"""Arithmetic evidence for unadopted legacy knee design alternatives.

This is a comparison model, not a new DCTL variant or host certification.
The legacy column executes the scalar statements from the original source via
the existing small test harness. No existing test suite is run by this script.
"""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path


LEGACY = Path(__file__).resolve().parents[1]
HARNESS = runpy.run_path(str(LEGACY / "v1.2.2/tests/test_neutral_density.py"))
SOURCE_PROBE = HARNESS["probe"]
ORIGINAL = HARNESS["ORIGINAL"]
PARTIAL = HARNESS["CORRECTED"]
DEFAULT = (0.25, 0.1, 4.0)  # UI Threshold, UI Knee, UI Ratio


def h(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def legacy(x: float, ui: float, knee: float, ratio: float) -> float:
    threshold, width = ui**3, max(knee, 1e-6)
    if ratio <= 1.0 or x <= threshold - width:
        return x
    target = threshold + max(x - threshold, 0.0) / (1.0 + math.log(ratio))
    blend = h((x - threshold + width) / (2.0 * width))
    return x * (1.0 - blend) + target * blend


def anchored_gain(x: float, ui: float, knee: float, ratio: float, power: int) -> float:
    """Stable gain for A1/A2 in the affected lower region, including x == 0.

    power 1 removes the intercept with an affine correction; power 2 also
    preserves the legacy left derivative at the threshold. Both remain
    proposals. The x == 0 branch outside that region is an analytic limit.
    """
    threshold, width = ui**3, max(knee, 1e-6)
    if ratio <= 1.0:
        return 1.0
    if 0.0 < threshold < width and x < threshold:
        a, u = threshold / width, x / threshold
        g1 = 1.0 + (a / 4.0) * (1.0 - u) * (
            3.0 * (1.0 - a * a) + a * a * (3.0 * u - u * u)
        )
        if power == 1:
            return g1
        if power == 2:
            # Algebraically F2(x)/x, without subtracting two finite floors.
            return 1.0 + (1.0 - u) * (
                0.5 - 0.25 * a**3 * (1.0 - u) * (2.0 - u)
            )
        raise ValueError("Only the compared A1/A2 designs are supported")
    if x > 0.0:
        return legacy(x, ui, knee, ratio) / x
    if threshold == 0.0:
        return 0.5 * (1.0 + 1.0 / (1.0 + math.log(ratio)))
    return 1.0


def a1(x: float, ui: float, knee: float, ratio: float) -> float:
    return x * anchored_gain(x, ui, knee, ratio, 1)


def a2(x: float, ui: float, knee: float, ratio: float) -> float:
    return x * anchored_gain(x, ui, knee, ratio, 2)


def no_expansion(x: float, ui: float, knee: float, ratio: float) -> float:
    return min(x, legacy(x, ui, knee, ratio))


def quadratic(x: float, ui: float, knee: float, ratio: float) -> float:
    """Alternative C: conventional knee, retaining legacy threshold/ratio maps.

    Legacy Knee is a half-width here. Cap it at threshold so its lower edge
    cannot cross zero. This is a broader creative and UI-response change.
    """
    if ratio <= 1.0:
        return x
    threshold = ui**3
    width = min(max(knee, 1e-6), threshold)
    reciprocal = 1.0 / (1.0 + math.log(ratio))
    if width == 0.0:
        return x * reciprocal
    lower, upper = threshold - width, threshold + width
    if x <= lower:
        return x
    if x >= upper:
        return threshold + (x - threshold) * reciprocal
    return x + (reciprocal - 1.0) * (x - lower)**2 / (4.0 * width)


def close(a: float, b: float, tolerance: float = 2e-15) -> None:
    assert abs(a - b) <= tolerance * max(1.0, abs(a), abs(b)), (a, b)


def main() -> None:
    checks = 0
    ui, knee, ratio = DEFAULT
    threshold = ui**3
    points = (0.0, 1e-12, 1e-9, 0.999999e-6, 1.000001e-6,
              0.005, threshold / 2.0, threshold, 0.03, threshold + knee, 0.12)
    for x in points:
        measured = SOURCE_PROBE(ORIGINAL, x, Sat_Density=0.0)["sat_out"]
        close(legacy(x, *DEFAULT), measured)
    checks += 1

    # Both endpoint-anchored formulas agree with their explicit correction.
    floor = legacy(0.0, *DEFAULT)
    for x in (0.0, 1e-9, 1e-6, 0.005, threshold / 2.0, threshold):
        for power, fn in ((1, a1), (2, a2)):
            close(fn(x, *DEFAULT), legacy(x, *DEFAULT) -
                  floor * (1.0 - x / threshold)**power)
    checks += 1

    for fn in (a1, a2, no_expansion, quadratic):
        values = [fn(x, *DEFAULT) for x in points]
        close(values[0], 0.0)
        assert all(math.isfinite(v) and v >= 0.0 for v in values)
        assert all(right >= left for left, right in zip(values, values[1:]))
    checks += 1

    a = threshold / knee
    expected_limits = (1.0 + 0.75 * a * (1.0 - a*a), 1.5 - 0.5 * a**3)
    for power, limit in enumerate(expected_limits, 1):
        close(anchored_gain(0.0, *DEFAULT, power), limit)
        close(anchored_gain(1e-12, *DEFAULT, power), limit, 5e-11)
    checks += 1

    delta = threshold * 1e-6
    old_left = (threshold - legacy(threshold-delta, *DEFAULT)) / delta
    a2_left = (threshold - a2(threshold-delta, *DEFAULT)) / delta
    a1_left = (threshold - a1(threshold-delta, *DEFAULT)) / delta
    close(a2_left, old_left, 1e-6)
    assert a1_left - old_left > 0.3
    checks += 1

    # Locality: high side unchanged; a knee whose lower edge is nonnegative
    # stays unchanged in A1/A2, including legacy below-threshold lift.
    healthy = (0.5, 0.1, 4.0)
    for fn in (a1, a2):
        for x in (threshold, 0.03, threshold + knee, 0.8):
            close(fn(x, *DEFAULT), legacy(x, *DEFAULT))
        for x in (0.0, 0.02, 0.075, 0.125, 0.3):
            close(fn(x, *healthy), legacy(x, *healthy))
        for k in (threshold * (1.0 - 1e-9), threshold, threshold * (1.0 + 1e-9)):
            close(fn(threshold / 2, ui, k, ratio),
                  legacy(threshold / 2, ui, threshold, ratio), 1e-10)
    checks += 1

    # Proposed gain reconstruction has no switch at the old 1e-6 boundary.
    left, right = 0.999999e-6, 1.000001e-6
    partial_left = SOURCE_PROBE(PARTIAL, left)["luma_final"]
    partial_right = SOURCE_PROBE(PARTIAL, right)["luma_final"]
    y_left, y_right = (0.18 / (1.0 + 2.0*a2(x, *DEFAULT)) for x in (left, right))
    assert partial_left - partial_right > 0.002
    assert abs(y_left - y_right) < 2e-12
    close(a2(0.0, *DEFAULT), 0.0)
    close(0.18 / (1.0 + 2.0*a2(0.0, *DEFAULT)), 0.18)
    checks += 1

    for fn in (a1, a2):
        for x in (0.0, 1e-9, 0.005, 0.12):
            close(fn(x, ui, knee, 1.0), x)
            close(fn(x, 0.0, knee, ratio), legacy(x, 0.0, knee, ratio))
    for pre, makeup in ((0.0, 1.0), (3.0, 0.0), (3.0, 4.0)):
        for sat in (0.0, 1e-9, 1e-6):
            gain = pre * makeup * anchored_gain(pre*sat, *DEFAULT, 2)
            chroma = sat * gain
            assert gain >= 0.0 and math.isfinite(gain)
            close(chroma, makeup*a2(pre*sat, *DEFAULT))
            if sat == 0.0 or pre == 0.0 or makeup == 0.0:
                close(chroma, 0.0)
    checks += 1

    print("Design alternatives only; no DCTL variant adopted.")
    print(f"Focused arithmetic groups: {checks} passed")
    for relative in ("v1.2.1/press_machine_v1_2_1.dctl",
                     "v1.2.2/press_machine_v1_2_2.dctl",
                     "v1.2.2/tests/test_neutral_density.py"):
        data = (LEGACY / relative).read_text(encoding="utf-8").encode("utf-8")
        print(f"Normalized UTF-8 SHA256 {relative}: {hashlib.sha256(data).hexdigest()}")
    print(f"T={threshold:.12f}; k={knee:.12f}; rho={1+math.log(ratio):.12f}")
    print(f"Legacy floor={floor:.12f}; A1 origin gain={expected_limits[0]:.12f}; A2 origin gain={expected_limits[1]:.12f}")
    print("x | source legacy | A1 affine | A2 quadratic reanchor | B no expansion | C capped quadratic")
    for x in (0.0, 1e-9, 1e-6, 0.005, threshold/2, threshold, 0.03, 0.12):
        vals = (legacy(x, *DEFAULT), a1(x, *DEFAULT), a2(x, *DEFAULT),
                no_expansion(x, *DEFAULT), quadratic(x, *DEFAULT))
        print(f"{x:.12g} | " + " | ".join(f"{v:.12f}" for v in vals))
    print("Old guard boundary: v1.2.2 left/right Y = "
          f"{partial_left:.12f} / {partial_right:.12f}")
    print(f"A2 mathematical gain path left/right Y = {y_left:.12f} / {y_right:.12f}")
    print("Healthy lower knee x=.075, UI T=.5, K=.1, R=4: "
          f"legacy/A2/B = {legacy(.075,*healthy):.12f} / {a2(.075,*healthy):.12f} / {no_expansion(.075,*healthy):.12f}")
    print("No GPU, DCTL compiler, Resolve, encoding or visual evaluation was run.")


if __name__ == "__main__":
    main()
