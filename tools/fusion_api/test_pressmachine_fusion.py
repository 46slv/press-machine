"""Offline synthetic SDK mocks. Never load or connect to the Resolve SDK."""
import copy
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import pressmachine_fusion as pm


class Input:
    def __init__(self, iid):
        self.attrs = {"INPS_ID": iid, "INPS_DataType": "Number",
                      "INPB_Connected": False, "INPB_Disabled": False}
        self.expression, self.keys = None, None

    def GetAttrs(self):
        return dict(self.attrs)

    def GetExpression(self):
        return self.expression

    def GetKeyFrames(self):
        return self.keys


class Tool:
    def __init__(self):
        self.attrs = {"TOOLS_Name": "PressMachinev201", "TOOLI_ID": 7, "TOOLS_RegID": pm.REG_ID}
        self.inputs = [Input(iid) for iid in pm.PARAMETER_IDS]
        source = Input("Source")
        source.attrs["INPS_DataType"] = "Image"
        self.inputs.extend([source, Input("Blend"), Input("Fdb")])
        self.values = {iid: row["default"] for iid, row in pm.schema().items()}
        self.values["pm_pre"] = 50.0
        self.reads, self.calls = [], []
        self.returned, self.mutate, self.error, self.on_set = None, True, None, None

    def GetAttrs(self):
        return dict(self.attrs)

    def GetInputList(self):
        return {i + 1: value for i, value in enumerate(self.inputs)}

    def GetInput(self, iid, frame):
        self.reads.append(iid)
        if iid not in pm.PARAMETER_IDS:
            raise AssertionError("Common/Image values must not be read")
        return self.values[iid]

    def SetInput(self, iid, value, frame):
        self.calls.append((iid, value, frame))
        if self.mutate:
            self.values[iid] = value
        if self.on_set:
            self.on_set()
        if self.error:
            raise self.error
        return self.returned


class Comp:
    def __init__(self, tool):
        self.tools = [tool]
        self.CurrentTime, self.rendering, self.locked = 0.0, False, False
        self.start_result, self.end_result = None, None
        self.start_error, self.end_error, self.on_start, self.on_end = None, None, None, None
        self.starts, self.ends = 0, 0

    def GetAttrs(self):
        return {"COMPS_Name": "コンポジション表示名"}

    def GetToolList(self, selected):
        assert selected is False
        return dict(enumerate(self.tools, 1))

    def IsRendering(self):
        return self.rendering

    def IsLocked(self):
        return self.locked

    def StartUndo(self, label):
        self.starts += 1
        if self.on_start:
            self.on_start()
        if self.start_error:
            raise self.start_error
        return self.start_result

    def EndUndo(self, commit):
        assert commit is True
        self.ends += 1
        if self.on_end:
            self.on_end()
        if self.end_error:
            raise self.end_error
        return self.end_result


class Clip:
    def __init__(self, comp):
        self.comp, self.uid, self.name = comp, "test-clip", "Synthetic test clip"
        self.names = ["Composition 1"]

    def GetUniqueId(self):
        return self.uid

    def GetName(self):
        return self.name

    def GetFusionCompNameList(self):
        return self.names

    def GetFusionCompByName(self, name):
        return self.comp if name in self.names else None


class Timeline:
    def __init__(self, clip):
        self.clip, self.uid, self.name = clip, "test-timeline", "Synthetic timeline"
        self.timecode = "01:00:00:00"

    def GetUniqueId(self):
        return self.uid

    def GetName(self):
        return self.name

    def GetCurrentVideoItem(self):
        return self.clip

    def GetCurrentTimecode(self):
        return self.timecode


class Project:
    def __init__(self, timeline):
        self.timeline, self.uid, self.name = timeline, "test-project", "Synthetic project"
        self.rendering = False

    def GetUniqueId(self):
        return self.uid

    def GetName(self):
        return self.name

    def GetCurrentTimeline(self):
        return self.timeline

    def IsRenderingInProgress(self):
        return self.rendering


class Resolve:
    def __init__(self, project):
        self.project = project

    def GetProjectManager(self):
        return self

    def GetCurrentProject(self):
        return self.project


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mock-", dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tool = Tool()
        self.comp = Comp(self.tool)
        self.clip = Clip(self.comp)
        self.timeline = Timeline(self.clip)
        self.project = Project(self.timeline)
        self.resolve = Resolve(self.project)
        self.listing = pm.list_targets(self.resolve)
        self.selection = pm.select_target(self.listing, "Composition 1", "PressMachinev201", 7)
        self.snapshot = pm.inspect_target(self.resolve, self.selection)
        self.path, self.journal = self.root / "before.json", self.root / "journal.jsonl"
        pm.save_snapshot(self.snapshot, self.path)

    def write(self, **kwargs):
        return pm.set_once(self.resolve, self.path, kwargs.get("parameter", "pm_pre"),
                           kwargs.get("expected", 50), kwargs.get("value", 60), self.journal)

    def change_snapshot(self, callback):
        value = pm.load_json(self.path)
        callback(value)
        self.path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")

    def assertNoSetter(self, result):
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(self.tool.calls, [])
        self.assertFalse(result["set_input_attempted"])

    def test_import_is_inert(self):
        spec = importlib.util.spec_from_file_location("fresh_toolkit", pm.__file__)
        with mock.patch("importlib.util.spec_from_file_location", side_effect=AssertionError("SDK load on import")):
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        self.assertTrue(callable(module.connect_resolve))

    def test_none_setter_and_undo_returns_are_success(self):
        result = self.write()
        self.assertEqual(result["outcome"], "success_numeric_only")
        self.assertIsNone(result["setter_return"])
        self.assertEqual(self.tool.calls, [("pm_pre", 60, 0.0)])
        self.assertEqual((self.comp.starts, self.comp.ends), (1, 1))
        self.assertTrue(result["other_parameters_unchanged"])
        self.assertFalse(result["pixel_reflection_tested"])

    def test_preview_rendering_after_set_is_allowed(self):
        self.tool.on_set = lambda: setattr(self.comp, "rendering", True)
        self.assertEqual(self.write()["outcome"], "success_numeric_only")

    def test_association_is_not_localized_display_name(self):
        self.assertNotEqual(self.listing["targets"][0]["comp_display_name"], self.selection["association_name"])
        self.assertEqual(self.write()["outcome"], "success_numeric_only")

    def test_display_name_cannot_select_association(self):
        with self.assertRaises(pm.Blocked):
            pm.select_target(self.listing, "コンポジション表示名", "PressMachinev201", 7)

    def test_list_only_exact_production_regid(self):
        self.tool.attrs["TOOLS_RegID"] += ".fdb"
        self.assertEqual(pm.list_targets(self.resolve)["targets"], [])

    def test_reads_exactly_own_25_not_source_or_common(self):
        self.assertEqual(set(self.tool.reads), set(pm.PARAMETER_IDS))

    def test_context_project_changed(self):
        self.project.uid = "different-project"
        self.assertNoSetter(self.write())

    def test_context_timeline_changed(self):
        self.timeline.uid = "different-timeline"
        self.assertNoSetter(self.write())

    def test_context_clip_changed(self):
        self.clip.uid = "different-clip"
        self.assertNoSetter(self.write())

    def test_context_name_changed(self):
        self.clip.name = "Renamed"
        self.assertNoSetter(self.write())

    def test_playhead_changed(self):
        self.timeline.timecode = "01:00:00:01"
        self.assertNoSetter(self.write())

    def test_frame_changed(self):
        self.comp.CurrentTime = 1
        self.assertNoSetter(self.write())

    def test_tool_id_changed(self):
        self.tool.attrs["TOOLI_ID"] = 8
        self.assertNoSetter(self.write())

    def test_regid_changed(self):
        self.tool.attrs["TOOLS_RegID"] += ".other"
        self.assertNoSetter(self.write())

    def test_duplicate_tool_name(self):
        self.comp.tools.append(Tool())
        self.assertNoSetter(self.write())

    def test_missing_association(self):
        self.clip.names = []
        self.assertNoSetter(self.write())

    def test_duplicate_association(self):
        self.clip.names *= 2
        self.assertNoSetter(self.write())

    def test_stale_target_value(self):
        self.tool.values["pm_pre"] = 51
        self.assertNoSetter(self.write())

    def test_stale_unrelated_value(self):
        self.tool.values["pm_density"] = 1
        self.assertNoSetter(self.write())

    def test_stale_target_metadata(self):
        self.tool.inputs[4].attrs["INPB_Disabled"] = True
        self.assertNoSetter(self.write())

    def test_expired_snapshot(self):
        self.change_snapshot(lambda s: s.update(captured_utc=(datetime.now(timezone.utc) - timedelta(minutes=6)).isoformat()))
        with self.assertRaises(pm.Blocked):
            self.write()
        self.assertFalse(self.journal.exists())

    def test_future_snapshot(self):
        self.change_snapshot(lambda s: s.update(captured_utc=(datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()))
        with self.assertRaises(pm.Blocked):
            self.write()

    def test_expected_before_mismatch(self):
        with self.assertRaises(pm.Blocked):
            self.write(expected=100)

    def test_invalid_parameter_ids(self):
        for iid in ("Source", "Blend", "pm_fdb", "Fdb", "pm_pre ", "PM_PRE", "__import__"):
            with self.subTest(iid=iid), self.assertRaises(pm.Blocked):
                self.write(parameter=iid)
        self.assertEqual(self.tool.calls, [])

    def test_invalid_numeric_ranges_types(self):
        for value in (-0.1, 200.1, float("inf"), float("nan"), True, "60", None, [], 10**400):
            with self.subTest(value=str(value)), self.assertRaises(pm.Blocked):
                self.write(value=value)
        self.assertEqual(self.tool.calls, [])

    def test_choice_requires_integer_index(self):
        for value in (1.0, 1.5, -1, 4, True, "1"):
            with self.subTest(value=value), self.assertRaises(pm.Blocked):
                self.write(parameter="pmi_ig", expected=0, value=value)
        result = self.write(parameter="pmi_ig", expected=0, value=1)
        self.assertEqual(result["outcome"], "success_numeric_only")

    def test_bool_allows_bool_or_integer(self):
        for value in (2, -1, 0.5, 1.0, "true"):
            with self.subTest(value=value), self.assertRaises(pm.Blocked):
                self.write(parameter="pm_db", expected=0, value=value)
        result = self.write(parameter="pm_db", expected=0, value=True)
        self.assertEqual(result["outcome"], "success_numeric_only")
        self.assertEqual(self.tool.calls[0][1], 1)

    def test_schema_range_is_authoritative(self):
        with self.assertRaises(pm.Blocked):
            self.write(parameter="pm_response", expected=2, value=5)

    def test_observed_host_range_is_respected(self):
        self.tool.inputs[4].attrs["INPN_MaxAllowed"] = 55
        snapshot = pm.inspect_target(self.resolve, self.selection)
        self.path = self.root / "bounds.json"
        pm.save_snapshot(snapshot, self.path)
        with self.assertRaises(pm.Blocked):
            self.write()

    def test_missing_control(self):
        self.tool.inputs.pop(0)
        self.assertNoSetter(self.write())

    def test_duplicate_control(self):
        self.tool.inputs.append(Input("pm_pre"))
        self.assertNoSetter(self.write())

    def test_wrong_input_type(self):
        self.tool.inputs[4].attrs["INPS_DataType"] = "Image"
        self.assertNoSetter(self.write())

    def test_nonfinite_host_readback(self):
        self.tool.values["pm_density"] = float("nan")
        self.assertNoSetter(self.write())

    def test_target_animation_blocks(self):
        for field, value in (("expression", "time"), ("keys", {0: 50})):
            with self.subTest(field=field):
                setattr(self.tool.inputs[4], field, value)
                snapshot = pm.inspect_target(self.resolve, self.selection)
                path = self.root / (field + ".json")
                pm.save_snapshot(snapshot, path)
                with self.assertRaises(pm.Blocked):
                    pm.set_once(self.resolve, path, "pm_pre", 50, 60, self.journal)
                setattr(self.tool.inputs[4], field, None)

    def test_unknown_animation_blocks(self):
        with mock.patch.object(self.tool.inputs[4], "GetKeyFrames", side_effect=RuntimeError("unknown")):
            snapshot = pm.inspect_target(self.resolve, self.selection)
            self.path = self.root / "unknown.json"
            pm.save_snapshot(snapshot, self.path)
            with self.assertRaises(pm.Blocked):
                self.write()

    def test_connected_disabled_unknown_target_blocks(self):
        for flag, value in (("INPB_Connected", True), ("INPB_Disabled", True), ("INPB_Disabled", None)):
            with self.subTest(flag=flag, value=value):
                self.tool.inputs[4].attrs[flag] = value
                snapshot = pm.inspect_target(self.resolve, self.selection)
                path = self.root / (flag + str(value) + ".json")
                pm.save_snapshot(snapshot, path)
                with self.assertRaises(pm.Blocked):
                    pm.set_once(self.resolve, path, "pm_pre", 50, 60, self.journal)
                self.tool.inputs[4].attrs[flag] = False

    def test_rendering_locked_and_unknown_prewrite_blocks(self):
        for obj, field, value in ((self.project, "rendering", True), (self.project, "rendering", None),
                                  (self.comp, "rendering", True), (self.comp, "locked", True)):
            with self.subTest(field=field, value=value):
                setattr(obj, field, value)
                self.journal = self.root / ("guard" + str(len(list(self.root.iterdir()))) + ".jsonl")
                self.assertNoSetter(self.write())
                setattr(obj, field, False)

    def test_false_setter_return_is_partial_even_when_changed(self):
        self.tool.returned = False
        result = self.write()
        self.assertEqual(result["outcome"], "partial")
        self.assertTrue(result["numeric_readback_verified"])
        self.assertEqual(len(self.tool.calls), 1)

    def test_false_setter_without_change_is_partial(self):
        self.tool.returned, self.tool.mutate = False, False
        self.assertEqual(self.write()["outcome"], "partial")

    def test_setter_exception_is_uncertain_no_retry(self):
        self.tool.error = RuntimeError("synthetic failure after mutation")
        result = self.write()
        self.assertEqual(result["outcome"], "uncertain")
        self.assertTrue(result["numeric_readback_verified"])
        self.assertEqual(len(self.tool.calls), 1)

    def test_start_undo_false_is_uncertain_no_setter(self):
        self.comp.start_result = False
        self.assertEqual(self.write()["outcome"], "uncertain")
        self.assertEqual(self.tool.calls, [])
        self.assertEqual(self.comp.ends, 0)

    def test_start_undo_exception_is_uncertain(self):
        self.comp.start_error = RuntimeError("undo unknown")
        self.assertEqual(self.write()["outcome"], "uncertain")
        self.assertEqual(self.tool.calls, [])

    def test_end_undo_false_is_uncertain(self):
        self.comp.end_result = False
        self.assertEqual(self.write()["outcome"], "uncertain")

    def test_end_undo_exception_is_uncertain(self):
        self.comp.end_error = RuntimeError("undo unknown")
        self.assertEqual(self.write()["outcome"], "uncertain")

    def test_change_during_start_undo_blocks_setter_and_closes_group(self):
        self.comp.on_start = lambda: self.tool.values.update(pm_density=1)
        self.assertNoSetter(self.write())
        self.assertEqual(self.comp.ends, 1)

    def test_context_change_after_set_is_uncertain(self):
        self.tool.on_set = lambda: setattr(self.clip, "uid", "changed")
        self.assertEqual(self.write()["outcome"], "uncertain")

    def test_project_render_after_set_is_uncertain(self):
        self.tool.on_set = lambda: setattr(self.project, "rendering", True)
        self.assertEqual(self.write()["outcome"], "uncertain")

    def test_unrelated_parameter_change_is_partial(self):
        self.tool.on_set = lambda: self.tool.values.update(pm_density=1)
        result = self.write()
        self.assertEqual(result["outcome"], "partial")
        self.assertFalse(result["other_parameters_unchanged"])

    def test_none_setter_without_change_is_partial(self):
        self.tool.mutate = False
        self.assertEqual(self.write()["outcome"], "partial")

    def test_journal_collision_never_overwrites_or_calls_host(self):
        self.journal.write_text("keep me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.write()
        self.assertEqual(self.journal.read_text(), "keep me")
        self.assertEqual(self.tool.calls, [])
        self.assertEqual(self.comp.starts, 0)

    def test_snapshot_collision_does_not_overwrite(self):
        original = self.path.read_bytes()
        with self.assertRaises(FileExistsError):
            pm.save_snapshot(self.snapshot, self.path)
        self.assertEqual(original, self.path.read_bytes())

    def test_consumed_snapshot_cannot_use_new_journal(self):
        self.comp.on_start = lambda: self.tool.values.update(pm_density=1)
        self.assertNoSetter(self.write())
        self.comp.on_start = None
        self.tool.values["pm_density"] = 0
        self.journal = self.root / "new-journal.jsonl"
        self.assertNoSetter(self.write())
        self.assertEqual(self.comp.starts, 1)

    def test_durable_journal_before_setter(self):
        events_at_setter = []
        def check():
            records = [json.loads(line) for line in self.journal.read_text(encoding="utf-8").splitlines()]
            events_at_setter.extend(row["event"] for row in records)
        self.tool.on_set = check
        self.write()
        self.assertEqual(events_at_setter[-1], "before_set_input")
        self.assertIn("preflight_passed", events_at_setter)

    def test_fsync_failure_before_setter_never_writes(self):
        with mock.patch.object(pm.os, "fsync", side_effect=OSError("synthetic disk failure")):
            result = self.write()
        self.assertNoSetter(result)
        self.assertFalse(result["journal_complete"])

    def test_final_journal_failure_is_uncertain(self):
        original = pm._record
        def fail_final(stream, event, data):
            if event == "final":
                raise OSError("synthetic final write failure")
            return original(stream, event, data)
        with mock.patch.object(pm, "_record", side_effect=fail_final):
            result = self.write()
        self.assertEqual(result["outcome"], "uncertain")
        self.assertFalse(result["journal_complete"])

    def test_journal_close_failure_after_set_is_uncertain(self):
        original_open = Path.open
        journal = self.journal
        class CloseFailure:
            def __init__(self, stream):
                self.stream = stream
            def __getattr__(self, key):
                return getattr(self.stream, key)
            def close(self):
                self.stream.close()
                raise OSError("synthetic journal close failure")
        def special_open(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            return CloseFailure(stream) if path == journal else stream
        with mock.patch.object(Path, "open", special_open):
            result = self.write()
        self.assertEqual(result["outcome"], "uncertain")
        self.assertFalse(result["journal_complete"])
        self.assertEqual(len(self.tool.calls), 1)

    def test_main_unhandled_set_exception_is_uncertain(self):
        error_output = io.StringIO()
        with mock.patch.object(pm, "connect_resolve", return_value=self.resolve), \
             mock.patch.object(pm, "set_once", side_effect=RuntimeError("unexpected set failure")), \
             mock.patch.object(pm.sys, "stderr", error_output):
            code = pm.main(["set", "--snapshot", str(self.path), "--param", "pm_pre",
                            "--expect", "50", "--value", "60", "--journal", str(self.journal)])
        self.assertEqual(code, 4)
        self.assertEqual(json.loads(error_output.getvalue())["outcome"], "uncertain")

    def test_json_nonfinite_overflow_duplicate_keys_blocked(self):
        for index, text in enumerate(("NaN", "Infinity", "-Infinity", "1e999", '{"a":1,"a":2}', str(10**400))):
            path = self.root / ("invalid" + str(index) + ".json")
            path.write_text(text)
            with self.subTest(text=text), self.assertRaises(pm.Blocked):
                pm.load_json(path)

    def test_json_save_nonfinite_is_rejected(self):
        with self.assertRaises(ValueError):
            pm.save_json({"value": float("nan")}, self.root / "nan.json")
        self.assertFalse((self.root / "nan.json").exists())

    def test_schema_hash_tampering_blocked(self):
        original = Path.read_bytes
        def altered(path):
            return b"[]" if path.name == "press_machine_v2.json" else original(path)
        with mock.patch.object(Path, "read_bytes", altered), self.assertRaises(pm.Blocked):
            pm.schema()

    def test_noop_blocked(self):
        with self.assertRaises(pm.Blocked):
            self.write(value=50)

    def test_snapshot_missing_unrelated_parameter(self):
        self.change_snapshot(lambda s: s["state"]["values"].pop("pm_density"))
        with self.assertRaises(pm.Blocked):
            self.write()


if __name__ == "__main__":
    unittest.main()
