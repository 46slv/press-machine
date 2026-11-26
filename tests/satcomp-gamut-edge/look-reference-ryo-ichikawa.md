# Reference look: blue shade and cream sunlight

[Source: Ryo Ichikawa, Hello FX5 Setup., 0:50–1:05](https://youtu.be/LacjCmbb3X0?t=50)

Two rendered stills were visually inspected. They show a blue/slate wall and deep blue road shadows, with a cream-to-yellow-green reflection or directly lit facade. The palette is not a uniform teal cast: the brighter sky and lit surfaces have different colors, and warm beige fabric and small red/orange accents remain distinguishable rather than becoming oversaturated. The far darkest regions stay close to neutral/deep navy, not brightly cyan. The full moving segment and original camera settings were not verified; reference images are not redistributed.

## Starting point in the full Press Machine OFX

1. Normalize the source correctly into the working space. Set exposure, white balance, and highlight roll-off with Resolve primaries or HDR wheels first. Avoid double conversion in a managed timeline.
2. Use Hue Angle/Pattern and the luminance-dependent Bias/Split/Pivot/Width controls gently to separate blue/slate low mids from pale warm upper mids and highlights. Check both sides of the pivot on a gray ramp and the shot; do not assume a sign independent of the selected pattern.
3. Use moderate Sat Comp for the more intense cyan/blue and red accents; keep Makeup near neutral initially. Add restrained Density only if colored areas need weight and use Look Skin Protect when relevant. A final small Shadow Desat adjustment should affect the deepest blacks without removing the blue from the low mids.
4. If the sun/shade boundary or warm accents still need independent control, use a second Resolve node with a luminance qualifier/soft window or Hue vs Hue/Sat. Press Machine is not a source-adaptive shot matcher, a relighting tool or a substitute for a tone-curve or optical diffusion.

Use the **full Press Machine OFX** for the look. Standalone SatComp primarily manages saturation and color conversion; it does not provide the whole luminance-dependent look. The real test is a legally reusable graded/neutral A/B clip with blue shade, cream highlights, a warm object, and smooth transitions. Check the matching tonal regions and motion in Resolve before labeling any preset as validated.
