#include "dctl_syntax_shim.h"
#include "../SatComp_vNext.dctl"

float3 satcomp_run(
    float r, float g, float b,
    int input_gamut, int input_transfer,
    int output_gamut_ui, int output_transfer_ui,
    float threshold, float ratio, float knee,
    int bypass
) {
    p_input_gamut = (float)input_gamut;
    p_input_transfer = (float)input_transfer;
    p_output_gamut = (float)output_gamut_ui;
    p_output_transfer = (float)output_transfer_ui;
    p_threshold = threshold;
    p_ratio = ratio;
    p_knee = knee;
    p_bypass = (float)bypass;
    return transform(1, 1, 0, 0, r, g, b);
}
