# Evidence index

Only final.json, expanded.json, native-tests.log and native-qualification.json
qualify the current source. Verify their recorded SHA against the DCTL.

- host-numeric-fixture.json.gz: exact synthetic inputs, independent double
  expectations and OLD failed Resolve C75 sampled outputs. Not footage.
- before.json: original ade36d source, four CUDA optimizer modes.
- rounded-pairs.json: explicit RN operations alone, one fast-math failure remains.
- rounded-pairs-cbrt.json: root seed experiment, still failing.
- rounded-inverse.json: paired matrices but float Lab/S, passes narrowly.
- end-to-end-pairs.json: initial end-to-end pairs experiment before final endpoint
  and finite-extreme range refinements. Not the final source.
- subnormal-endpoint-before.json: wide pixel pass but four scalar decreases at
  positive subnormal S with T0/C100; final source repairs exact endpoint handling.
- final.json: current source, original 9894 host vectors, four optimizer modes.
- expanded.json: current source, extra14826 pixels, 677742 scalars per mode,
  exact positive-subnormal T identity regression, C0/bypass RGB word checks.
- native-qualification.json: unchanged frozen original corpus plus boundaries.
- native-tests.log: normalized test-result lines from 34-test MSVC execution.
- preservation.json: source/constants/evidence byte checks and isolated lane.

Raw host EXRs/DRP remain on WS, as linked from the technical report. New host
compilation, alpha and real-material/4K gates remain pending. Intermediate
experiments are retained as causal evidence, not combined into a false final PASS.
