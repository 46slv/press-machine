import csv
from pathlib import Path

from color_model import (
    ACESCCT, DWG_INTERMEDIATE, LINEAR_ACESCG, LINEAR_DWG,
    LINEAR_REC2020, LINEAR_REC709, REC709_GAMMA24, REC709_OETF, SRGB,
    apply_satcomp_encoded, xyz_d65_to_encoded_rgb,
)

ENCODINGS = (
    LINEAR_REC709, SRGB, REC709_OETF, REC709_GAMMA24,
    LINEAR_REC2020, LINEAR_DWG, DWG_INTERMEDIATE, LINEAR_ACESCG, ACESCCT,
)
XYZ_SAMPLES = (
    ("neutral18", (0.171085, 0.180000, 0.196054)),
    ("warm_low_sat", (0.260, 0.240, 0.190)),
    ("warm_high_sat", (0.310, 0.220, 0.080)),
    ("blue_high_sat", (0.120, 0.090, 0.420)),
    ("extended_hdr", (1.200, 0.700, 0.180)),
)

out = Path(__file__).with_name("SATCOMP_TEST_VECTORS.csv")
with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "sample", "encoding", "in_r", "in_g", "in_b",
        "s_in", "s_out", "out_r", "out_g", "out_b",
    ])
    for sample_name, xyz in XYZ_SAMPLES:
        for encoding in ENCODINGS:
            rgb = xyz_d65_to_encoded_rgb(xyz, encoding)
            result = apply_satcomp_encoded(
                rgb, encoding, encoding,
                threshold=0.25, ratio=3.0, knee=0.10,
            )
            w.writerow([
                sample_name, encoding.name,
                *[f"{v:.12g}" for v in rgb],
                f"{result.saturation_in:.12g}", f"{result.saturation_out:.12g}",
                *[f"{v:.12g}" for v in result.rgb],
            ])
print(out)
