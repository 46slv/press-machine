"""Repo-independent colorimetry oracle for SatComp.

The production DCTL/OFX implementation should be validated against this module.
No gamut mapping or 0..1 clipping is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable, Tuple

Vec3 = Tuple[float, float, float]
Mat3 = Tuple[Vec3, Vec3, Vec3]


def _mul_mv(m: Mat3, v: Vec3) -> Vec3:
    return tuple(sum(m[r][c] * v[c] for c in range(3)) for r in range(3))  # type: ignore[return-value]


def _mul_mm(a: Mat3, b: Mat3) -> Mat3:
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            row.append(sum(a[r][k] * b[k][c] for k in range(3)))
        rows.append(tuple(row))
    return tuple(rows)  # type: ignore[return-value]


def _diag(v: Vec3) -> Mat3:
    return ((v[0], 0.0, 0.0), (0.0, v[1], 0.0), (0.0, 0.0, v[2]))


def _inverse3(m: Mat3) -> Mat3:
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    A = e * i - f * h
    B = -(d * i - f * g)
    C = d * h - e * g
    D = -(b * i - c * h)
    E = a * i - c * g
    F = -(a * h - b * g)
    G = b * f - c * e
    H = -(a * f - c * d)
    I = a * e - b * d
    det = a * A + b * B + c * C
    if abs(det) < 1e-15:
        raise ValueError("singular matrix")
    inv_det = 1.0 / det
    return (
        (A * inv_det, D * inv_det, G * inv_det),
        (B * inv_det, E * inv_det, H * inv_det),
        (C * inv_det, F * inv_det, I * inv_det),
    )


def xy_to_xyz(xy: Tuple[float, float]) -> Vec3:
    x, y = xy
    if y == 0.0:
        raise ValueError("y chromaticity must not be zero")
    return (x / y, 1.0, (1.0 - x - y) / y)


def derive_rgb_to_xyz(
    red: Tuple[float, float],
    green: Tuple[float, float],
    blue: Tuple[float, float],
    white: Tuple[float, float],
) -> Mat3:
    r, g, b = xy_to_xyz(red), xy_to_xyz(green), xy_to_xyz(blue)
    primaries: Mat3 = (
        (r[0], g[0], b[0]),
        (r[1], g[1], b[1]),
        (r[2], g[2], b[2]),
    )
    scale = _mul_mv(_inverse3(primaries), xy_to_xyz(white))
    return _mul_mm(primaries, _diag(scale))


D65 = (0.3127, 0.3290)
ACES_WHITE = (0.32168, 0.33767)


@dataclass(frozen=True)
class RGBSpace:
    name: str
    red: Tuple[float, float]
    green: Tuple[float, float]
    blue: Tuple[float, float]
    white: Tuple[float, float]

    @property
    def rgb_to_xyz_native(self) -> Mat3:
        return derive_rgb_to_xyz(self.red, self.green, self.blue, self.white)

    @property
    def xyz_native_to_rgb(self) -> Mat3:
        return _inverse3(self.rgb_to_xyz_native)


REC709 = RGBSpace("Rec.709 / sRGB primaries", (0.640, 0.330), (0.300, 0.600), (0.150, 0.060), D65)
REC2020 = RGBSpace("Rec.2020", (0.708, 0.292), (0.170, 0.797), (0.131, 0.046), D65)
DWG = RGBSpace("DaVinci Wide Gamut", (0.8000, 0.3130), (0.1682, 0.9877), (0.0790, -0.1155), D65)
ACESCG = RGBSpace("ACEScg / AP1", (0.713, 0.293), (0.165, 0.830), (0.128, 0.044), ACES_WHITE)

# Bradford cone response matrices.
_BRADFORD: Mat3 = (
    (0.8951, 0.2664, -0.1614),
    (-0.7502, 1.7135, 0.0367),
    (0.0389, -0.0685, 1.0296),
)
_BRADFORD_INV = _inverse3(_BRADFORD)


def bradford_adaptation_matrix(source_white: Tuple[float, float], dest_white: Tuple[float, float]) -> Mat3:
    src = _mul_mv(_BRADFORD, xy_to_xyz(source_white))
    dst = _mul_mv(_BRADFORD, xy_to_xyz(dest_white))
    scale: Vec3 = tuple(dst[i] / src[i] for i in range(3))  # type: ignore[assignment]
    return _mul_mm(_BRADFORD_INV, _mul_mm(_diag(scale), _BRADFORD))


def adapt_xyz(xyz: Vec3, source_white: Tuple[float, float], dest_white: Tuple[float, float]) -> Vec3:
    if source_white == dest_white:
        return xyz
    return _mul_mv(bradford_adaptation_matrix(source_white, dest_white), xyz)


def linear_rgb_to_xyz_d65(rgb: Vec3, space: RGBSpace) -> Vec3:
    xyz_native = _mul_mv(space.rgb_to_xyz_native, rgb)
    return adapt_xyz(xyz_native, space.white, D65)


def xyz_d65_to_linear_rgb(xyz_d65: Vec3, space: RGBSpace) -> Vec3:
    xyz_native = adapt_xyz(xyz_d65, D65, space.white)
    return _mul_mv(space.xyz_native_to_rgb, xyz_native)


# W3C CSS Color 4 64-bit Oklab matrices for XYZ relative to D65.
_XYZ_TO_LMS: Mat3 = (
    (0.8190224379967030, 0.3619062600528904, -0.1288737815209879),
    (0.0329836539323885, 0.9292868615863434, 0.0361446663506424),
    (0.0481771893596242, 0.2642395317527308, 0.6335478284694309),
)
_LMS_TO_OKLAB: Mat3 = (
    (0.2104542683093140, 0.7936177747023054, -0.0040720430116193),
    (1.9779985324311684, -2.4285922420485799, 0.4505937096174110),
    (0.0259040424655478, 0.7827717124575296, -0.8086757549230774),
)
_OKLAB_TO_LMS: Mat3 = (
    (1.0, 0.3963377773761749, 0.2158037573099136),
    (1.0, -0.1055613458156586, -0.0638541728258133),
    (1.0, -0.0894841775298119, -1.2914855480194092),
)
_LMS_TO_XYZ: Mat3 = (
    (1.2268798758459243, -0.5578149944602171, 0.2813910456659647),
    (-0.0405757452148008, 1.1122868032803170, -0.0717110580655164),
    (-0.0763729366746601, -0.4214933324022432, 1.5869240198367816),
)


def _cbrt_signed(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def xyz_d65_to_oklab(xyz: Vec3) -> Vec3:
    lms = _mul_mv(_XYZ_TO_LMS, xyz)
    lms_nl: Vec3 = tuple(_cbrt_signed(v) for v in lms)  # type: ignore[assignment]
    return _mul_mv(_LMS_TO_OKLAB, lms_nl)


def oklab_to_xyz_d65(lab: Vec3) -> Vec3:
    lms_nl = _mul_mv(_OKLAB_TO_LMS, lab)
    lms: Vec3 = tuple(v * v * v for v in lms_nl)  # type: ignore[assignment]
    return _mul_mv(_LMS_TO_XYZ, lms)


def oklab_chroma(lab: Vec3) -> float:
    return math.hypot(lab[1], lab[2])


def oklab_hue(lab: Vec3) -> float:
    return math.atan2(lab[2], lab[1])


def oklab_saturation(lab: Vec3, *, black_floor: float = 1e-7) -> float:
    """Return Oklab saturation S=C/L for normal positive-lightness colors.

    Values at/under the black floor are treated as zero saturation so numerical
    noise near black is not promoted into a large selection signal. This does
    not clamp or alter the RGB itself.
    """
    L = lab[0]
    if L <= black_floor:
        return 0.0
    return oklab_chroma(lab) / L


def compress_oklab_saturation(
    lab: Vec3,
    transfer: Callable[[float], float],
    *,
    black_floor: float = 1e-7,
    neutral_floor: float = 1e-12,
) -> Vec3:
    """Apply a scalar S=C/L transfer while preserving Oklab L and hue exactly."""
    L, a, b = lab
    C = math.hypot(a, b)
    if L <= black_floor or C <= neutral_floor:
        return lab
    S = C / L
    S_out = transfer(S)
    if S_out < 0.0 or not math.isfinite(S_out):
        raise ValueError("saturation transfer must return a finite non-negative value")
    scale = S_out / S if S > 0.0 else 1.0
    return (L, a * scale, b * scale)


# Transfer-function reference implementations. Primaries and transfer are kept separate.

def linear_channel(x: float) -> float:
    return x


def srgb_decode_channel(x: float) -> float:
    # Sign-preserving extension avoids silently clipping extended-range values.
    sign = -1.0 if x < 0.0 else 1.0
    a = abs(x)
    if a <= 0.04045:
        return x / 12.92
    return sign * ((a + 0.055) / 1.055) ** 2.4


def srgb_encode_channel(x: float) -> float:
    sign = -1.0 if x < 0.0 else 1.0
    a = abs(x)
    if a <= 0.0031308:
        return 12.92 * x
    return sign * (1.055 * (a ** (1.0 / 2.4)) - 0.055)


def rec709_decode_channel(x: float) -> float:
    sign = -1.0 if x < 0.0 else 1.0
    a = abs(x)
    if a < 0.081:
        return x / 4.5
    return sign * ((a + 0.099) / 1.099) ** (1.0 / 0.45)


def rec709_encode_channel(x: float) -> float:
    sign = -1.0 if x < 0.0 else 1.0
    a = abs(x)
    if a < 0.018:
        return 4.5 * x
    return sign * (1.099 * (a ** 0.45) - 0.099)


DI_A = 0.0075
DI_B = 7.0
DI_C = 0.07329248
DI_M = 10.44426855
DI_LIN_CUT = 0.00262409
DI_LOG_CUT = 0.02740668


def davinci_intermediate_encode_channel(x: float) -> float:
    if x <= DI_LIN_CUT:
        return x * DI_M
    return (math.log2(x + DI_A) + DI_B) * DI_C


def davinci_intermediate_decode_channel(x: float) -> float:
    if x <= DI_LOG_CUT:
        return x / DI_M
    return 2.0 ** (x / DI_C - DI_B) - DI_A


def acescct_encode_channel(x: float) -> float:
    if x <= 0.0078125:
        return 10.5402377416545 * x + 0.0729055341958355
    return (math.log2(x) + 9.72) / 17.52


def acescct_decode_channel(x: float) -> float:
    break_code = 0.155251141552511
    max_linear = 65504.0
    max_code = (math.log2(max_linear) + 9.72) / 17.52
    if x <= break_code:
        return (x - 0.0729055341958355) / 10.5402377416545
    if x < max_code:
        return 2.0 ** (x * 17.52 - 9.72)
    return max_linear


def map_channels(v: Vec3, fn: Callable[[float], float]) -> Vec3:
    return (fn(v[0]), fn(v[1]), fn(v[2]))


def gamma24_decode_channel(x: float) -> float:
    return math.copysign(abs(x) ** 2.4, x)


def gamma24_encode_channel(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 2.4), x)


@dataclass(frozen=True)
class ColorEncoding:
    name: str
    gamut: RGBSpace
    decode: Callable[[float], float]
    encode: Callable[[float], float]


LINEAR_REC709 = ColorEncoding("Linear Rec.709", REC709, linear_channel, linear_channel)
SRGB = ColorEncoding("sRGB", REC709, srgb_decode_channel, srgb_encode_channel)
REC709_OETF = ColorEncoding("Rec.709 OETF", REC709, rec709_decode_channel, rec709_encode_channel)
REC709_GAMMA24 = ColorEncoding("Rec.709 Gamma 2.4", REC709, gamma24_decode_channel, gamma24_encode_channel)
LINEAR_REC2020 = ColorEncoding("Linear Rec.2020", REC2020, linear_channel, linear_channel)
LINEAR_DWG = ColorEncoding("Linear DaVinci Wide Gamut", DWG, linear_channel, linear_channel)
DWG_INTERMEDIATE = ColorEncoding(
    "DaVinci Wide Gamut / Intermediate", DWG,
    davinci_intermediate_decode_channel, davinci_intermediate_encode_channel,
)
LINEAR_ACESCG = ColorEncoding("ACEScg", ACESCG, linear_channel, linear_channel)
ACESCCT = ColorEncoding("ACEScct", ACESCG, acescct_decode_channel, acescct_encode_channel)


def encoded_rgb_to_xyz_d65(rgb: Vec3, encoding: ColorEncoding) -> Vec3:
    linear_rgb = map_channels(rgb, encoding.decode)
    return linear_rgb_to_xyz_d65(linear_rgb, encoding.gamut)


def xyz_d65_to_encoded_rgb(xyz: Vec3, encoding: ColorEncoding) -> Vec3:
    linear_rgb = xyz_d65_to_linear_rgb(xyz, encoding.gamut)
    return map_channels(linear_rgb, encoding.encode)


@dataclass(frozen=True)
class SatCompResult:
    rgb: Vec3
    saturation_in: float
    saturation_out: float
    changed: bool


def apply_satcomp_encoded(
    rgb: Vec3,
    input_encoding: ColorEncoding,
    output_encoding: ColorEncoding,
    *,
    threshold: float,
    ratio: float,
    knee: float,
    black_floor: float = 1e-7,
) -> SatCompResult:
    """CPU oracle for the complete color-managed SatComp path."""
    from satcomp_transfer import compress_saturation

    xyz = encoded_rgb_to_xyz_d65(rgb, input_encoding)
    lab = xyz_d65_to_oklab(xyz)
    s_in = oklab_saturation(lab, black_floor=black_floor)
    s_out = compress_saturation(s_in, threshold=threshold, ratio=ratio, knee=knee)
    out_lab = compress_oklab_saturation(
        lab,
        lambda _s: s_out,
        black_floor=black_floor,
    )
    out_xyz = oklab_to_xyz_d65(out_lab)
    out_rgb = xyz_d65_to_encoded_rgb(out_xyz, output_encoding)
    return SatCompResult(
        rgb=out_rgb,
        saturation_in=s_in,
        saturation_out=s_out,
        changed=abs(s_out - s_in) > 1e-12,
    )
