"""Read and change existing compiled PressMachine v2 Fusion inputs, once.

Import is inert. Only connect_resolve() loads the installed official SDK.
All other host functions accept an already-connected Resolve handle.
No graph editing, rendering, saving, retries, rollback, or global selection changes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

REG_ID = "ofx.com._46slv.PressMachine.v2.skinaxis"
SCHEMA_SHA256 = "43be401f517ee88cdc4a7ac1518b50c9ec62ef69fb3bc88d804cecf654a0f356"
MAX_SNAPSHOT_AGE_SECONDS = 300
PARAMETER_IDS = (
    "pmi_ig", "pmi_it", "pmi_og", "pmi_ot", "pm_pre", "pm_hue_angle",
    "pm_hue_points_index", "pm_hue_compression", "pm_threshold", "pm_compression",
    "pm_softness", "pm_sat_skin", "pm_density", "pm_chroma", "pm_response",
    "pm_shadow", "pm_sr", "pm_highlight", "pm_hr", "pm_density_skin", "pm_db",
    "pm_sd_t", "pm_sd_k", "pm_hd_t", "pm_hd_k",
)
CONTEXT_KEYS = (
    "project_id", "project_name", "timeline_id", "timeline_name",
    "clip_id", "clip_name", "playhead_timecode",
)
TARGET_KEYS = ("association_name", "tool_name", "tool_id", "reg_id", "frame")


class Blocked(ValueError):
    """A precondition failed. The caller must inspect before any new attempt."""


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n"


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Blocked("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _finite_tree(value):
    if isinstance(value, dict):
        for item in value.values():
            _finite_tree(item)
    elif isinstance(value, list):
        for item in value:
            _finite_tree(item)
    elif type(value) in (int, float) and not _number(value):
        raise Blocked("JSON contains a non-finite or unrepresentable number")


def load_json(path):
    """Read JSON data only; reject duplicate keys, NaN, Infinity, and overflow."""
    def reject(token):
        raise Blocked("Non-finite JSON literal: " + token)
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"),
                       object_pairs_hook=_pairs, parse_constant=reject)
    _finite_tree(value)
    return value


def schema():
    """Load the byte-for-byte frozen production schema, never user code."""
    path = Path(__file__).resolve().parent / "schema" / "press_machine_v2.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != SCHEMA_SHA256:
        raise Blocked("Frozen parameter schema hash mismatch")
    records = load_json(path)
    if not isinstance(records, list) or tuple(row.get("id") for row in records) != PARAMETER_IDS:
        raise Blocked("Frozen parameter ID list mismatch")
    return {row["id"]: row for row in records}


def _validate_value(parameter, value, *, host=False):
    definition = schema().get(parameter)
    if definition is None:
        raise Blocked("Not a production processing parameter: " + str(parameter))
    kind = definition["kind"]
    if kind == "bool" and not host and type(value) is bool:
        return int(value)
    if not _number(value):
        raise Blocked("Parameter values must be finite numbers (bool only for bool parameters)")
    if kind in ("choice", "bool"):
        if not float(value).is_integer() or (not host and type(value) is not int):
            raise Blocked("Choice/bool values require an integer, not a fractional or floating value")
        upper = len(definition["options"]) - 1 if kind == "choice" else 1
        if not 0 <= value <= upper:
            raise Blocked("Choice/bool value outside its allowed indices")
        return int(value)
    if not definition["min"] <= value <= definition["max"]:
        raise Blocked("Parameter value outside the frozen schema range")
    return value


def _rows(table):
    if isinstance(table, dict):
        return list(table.values())
    if isinstance(table, (list, tuple)):
        return list(table)
    raise Blocked("The SDK did not return a table")


def _string(value, label):
    if not isinstance(value, str) or not value:
        raise Blocked("Missing explicit " + label)
    return value


def _current(resolve):
    manager = resolve.GetProjectManager()
    project = manager.GetCurrentProject() if manager is not None else None
    timeline = project.GetCurrentTimeline() if project is not None else None
    clip = timeline.GetCurrentVideoItem() if timeline is not None else None
    if project is None or timeline is None or clip is None:
        raise Blocked("A current project, timeline, and video clip are required")
    context = {
        "project_id": project.GetUniqueId(), "project_name": project.GetName(),
        "timeline_id": timeline.GetUniqueId(), "timeline_name": timeline.GetName(),
        "clip_id": clip.GetUniqueId(), "clip_name": clip.GetName(),
        "playhead_timecode": timeline.GetCurrentTimecode(),
    }
    for key, value in context.items():
        _string(value, key)
    return context, project, clip


def _selection(selection):
    if not isinstance(selection, dict) or not isinstance(selection.get("context"), dict):
        raise Blocked("An explicit selection from list_targets is required")
    context = selection["context"]
    if set(context) != set(CONTEXT_KEYS):
        raise Blocked("Incomplete or unexpected context fields")
    for key in CONTEXT_KEYS:
        _string(context[key], key)
    for key in ("association_name", "tool_name"):
        _string(selection.get(key), key)
    if selection.get("reg_id") != REG_ID:
        raise Blocked("Only the exact compiled production RegID is supported")
    if not _number(selection.get("tool_id")) or not _number(selection.get("frame")):
        raise Blocked("Finite observed tool_id and frame are required")
    return {"context": dict(context), **{key: selection[key] for key in TARGET_KEYS}}


def _comp_names(clip):
    names = _rows(clip.GetFusionCompNameList())
    if any(not isinstance(name, str) or not name for name in names):
        raise Blocked("Invalid composition association name")
    if len(names) != len(set(names)):
        raise Blocked("Duplicate composition association names are ambiguous")
    return names


def _resolve_target(resolve, selection, *, require_idle=True):
    selection = _selection(selection)
    context, project, clip = _current(resolve)
    if context != selection["context"]:
        raise Blocked("Current project/timeline/clip/playhead does not match the selection")
    if project.IsRenderingInProgress() is not False:
        raise Blocked("Project render state is active or unknown")
    if selection["association_name"] not in _comp_names(clip):
        raise Blocked("Exact clip/composition association is no longer present")
    # Association names belong to TimelineItem, not localized COMPS_Name.
    comp = clip.GetFusionCompByName(selection["association_name"])
    if comp is None:
        raise Blocked("Associated composition cannot be resolved")
    rendering = comp.IsRendering()
    if (type(rendering) is not bool or (require_idle and rendering)
            or comp.IsLocked() is not False):
        raise Blocked("Composition must be observed idle and unlocked")
    if not _number(comp.CurrentTime) or comp.CurrentTime != selection["frame"]:
        raise Blocked("Composition frame changed")
    matches = []
    for candidate in _rows(comp.GetToolList(False)):
        attrs = candidate.GetAttrs()
        if attrs.get("TOOLS_Name") == selection["tool_name"]:
            matches.append(candidate)
    if len(matches) != 1:
        raise Blocked("Tool name is missing or ambiguous inside the associated composition")
    tool = matches[0]
    attrs = tool.GetAttrs()
    if (attrs.get("TOOLS_RegID") != REG_ID or attrs.get("TOOLI_ID") != selection["tool_id"]):
        raise Blocked("Exact production RegID or session tool ID changed")
    return comp, tool


def list_targets(resolve):
    """Read current clip associations and exact production tools. Never select one."""
    context, project, clip = _current(resolve)
    if project.IsRenderingInProgress() is not False:
        raise Blocked("Project render state is active or unknown")
    targets = []
    for name in _comp_names(clip):
        comp = clip.GetFusionCompByName(name)
        if comp is None:
            raise Blocked("Cannot read a listed composition association")
        if comp.IsRendering() is not False or comp.IsLocked() is not False:
            raise Blocked("Listed composition is rendering, locked, or unknown")
        display = comp.GetAttrs().get("COMPS_Name")
        for tool in _rows(comp.GetToolList(False)):
            attrs = tool.GetAttrs()
            if attrs.get("TOOLS_RegID") == REG_ID:
                target = {
                    "context": dict(context), "association_name": name,
                    "tool_name": attrs.get("TOOLS_Name"), "tool_id": attrs.get("TOOLI_ID"),
                    "reg_id": REG_ID, "frame": comp.CurrentTime,
                }
                target = _selection(target)
                target["comp_display_name"] = display if isinstance(display, str) else None
                targets.append(target)
    if _current(resolve)[0] != context:
        raise Blocked("Context changed during target enumeration")
    return {"format": "pressmachine-targets-v1", "captured_utc": _utc(),
            "schema_sha256": SCHEMA_SHA256, "context": context, "targets": targets}


def select_target(listing, association_name, tool_name, tool_id):
    """Choose one exact inspected association/tool. No fuzzy matching or defaults."""
    if (not isinstance(listing, dict) or listing.get("format") != "pressmachine-targets-v1"
            or listing.get("schema_sha256") != SCHEMA_SHA256):
        raise Blocked("Not a matching toolkit target listing")
    matches = [target for target in listing.get("targets", [])
               if target.get("association_name") == association_name
               and target.get("tool_name") == tool_name and target.get("tool_id") == tool_id]
    if len(matches) != 1:
        raise Blocked("Selection must match exactly one listed association/tool/session ID")
    return _selection(matches[0])


def _observe(resolve, selection, *, require_idle=True):
    selection = _selection(selection)
    comp, tool = _resolve_target(resolve, selection, require_idle=require_idle)
    definitions = schema()
    handles = {}
    for handle in _rows(tool.GetInputList()):
        attrs = handle.GetAttrs()
        iid = attrs.get("INPS_ID")
        if iid in PARAMETER_IDS:
            if iid in handles:
                raise Blocked("Duplicate processing control: " + iid)
            handles[iid] = (handle, attrs)
    if set(handles) != set(PARAMETER_IDS):
        raise Blocked("Missing production processing controls: " + ", ".join(sorted(set(PARAMETER_IDS) - set(handles))))
    values, controls = {}, {}
    for iid in definitions:
        handle, attrs = handles[iid]
        if attrs.get("INPS_DataType") != "Number":
            raise Blocked("Production processing control is not Number: " + iid)
        value = tool.GetInput(iid, selection["frame"])
        _validate_value(iid, value, host=True)
        values[iid] = value
        metadata = {"data_type": "Number", "connected": attrs.get("INPB_Connected"),
                    "disabled": attrs.get("INPB_Disabled")}
        if metadata["connected"] not in (True, False, None) or metadata["disabled"] not in (True, False, None):
            raise Blocked("Unexpected control state: " + iid)
        for field in ("INPN_MinAllowed", "INPN_MaxAllowed"):
            if field in attrs:
                if not _number(attrs[field]):
                    raise Blocked("Non-finite observed control bound: " + iid)
                metadata[field] = attrs[field]
        try:
            expression, keys = handle.GetExpression(), handle.GetKeyFrames()
            metadata["animation_clear"] = (
                expression in (None, "") and (keys is None or isinstance(keys, (dict, list, tuple)) and not keys))
        except Exception:
            metadata["animation_clear"] = None
        controls[iid] = metadata
    # Resolve again through the same exact association, not the active comp.
    _resolve_target(resolve, selection, require_idle=require_idle)
    return {"selection": selection, "values": values, "controls": controls}, comp, tool


def inspect_target(resolve, selection):
    """Read all 25 processing values. No image values or Host/common input values."""
    state, _, _ = _observe(resolve, selection)
    return {"format": "pressmachine-snapshot-v1", "captured_utc": _utc(),
            "schema_sha256": SCHEMA_SHA256, "state": state,
            "pixel_reflection_tested": False, "persistence_tested": False}


def save_json(value, path):
    """Durably save a new local JSON file, exclusively; never overwrite."""
    encoded = _json_text(value)
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    return str(Path(path))


def save_snapshot(snapshot, path):
    if not isinstance(snapshot, dict) or snapshot.get("format") != "pressmachine-snapshot-v1":
        raise Blocked("Not a toolkit snapshot")
    return save_json(snapshot, path)


def _saved_snapshot(path):
    snapshot = load_json(path)
    if (not isinstance(snapshot, dict) or snapshot.get("format") != "pressmachine-snapshot-v1"
            or snapshot.get("schema_sha256") != SCHEMA_SHA256):
        raise Blocked("Missing or incompatible saved snapshot")
    try:
        captured = datetime.fromisoformat(snapshot["captured_utc"])
        if captured.tzinfo is None:
            raise ValueError("UTC offset missing")
        age = (datetime.now(timezone.utc) - captured).total_seconds()
    except (KeyError, TypeError, ValueError) as exc:
        raise Blocked("Invalid snapshot timestamp") from exc
    if not 0 <= age <= MAX_SNAPSHOT_AGE_SECONDS:
        raise Blocked("Snapshot is expired or future-dated; inspect and save a new one")
    state = snapshot.get("state")
    if not isinstance(state, dict) or set(state) != {"selection", "values", "controls"}:
        raise Blocked("Incomplete snapshot state")
    _selection(state["selection"])
    if (not isinstance(state["values"], dict) or set(state["values"]) != set(PARAMETER_IDS)
            or not isinstance(state["controls"], dict) or set(state["controls"]) != set(PARAMETER_IDS)):
        raise Blocked("Snapshot must contain exactly all 25 processing controls")
    for iid, value in state["values"].items():
        _validate_value(iid, value, host=True)
    return snapshot


def _record(stream, event, data):
    stream.write(json.dumps({"utc": _utc(), "event": event, "data": data},
                            ensure_ascii=False, allow_nan=False) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


@contextmanager
def _exclusive_journal(path, result):
    stream = path.open("x", encoding="utf-8", newline="\n")
    try:
        yield stream
    finally:
        try:
            stream.close()
        except Exception as exc:
            result["journal_complete"] = False
            result["outcome"] = "uncertain" if result["set_input_attempted"] or result["undo_attempted"] else "blocked"
            result["errors"].append("Journal close: " + type(exc).__name__ + ": " + str(exc))


def _target_guard(state, parameter, requested):
    metadata = state["controls"][parameter]
    if (metadata.get("connected") is not False or metadata.get("disabled") is not False
            or metadata.get("animation_clear") is not True):
        raise Blocked("Target must be enabled, unconnected, and free of expressions/keyframes")
    if requested < metadata.get("INPN_MinAllowed", requested) or requested > metadata.get("INPN_MaxAllowed", requested):
        raise Blocked("Requested value violates observed Host bounds")


def set_once(resolve, snapshot_path, parameter, expected_before, value, journal_path):
    """One setter, at most. Require a fresh saved snapshot and an exclusive journal.

    Return blocked/success_numeric_only/partial/uncertain. Never repeat this
    call after partial/uncertain. Inspect the actual Host and journal first.
    None from SetInput is permitted; all 25 fresh values determine verification.
    """
    requested = _validate_value(parameter, value)
    _validate_value(parameter, expected_before, host=True)
    if requested == expected_before:
        raise Blocked("Refuse a no-op write")
    snapshot = _saved_snapshot(snapshot_path)
    baseline = snapshot["state"]
    if baseline["values"][parameter] != expected_before:
        raise Blocked("Explicit expected-before value does not match the saved snapshot")
    _target_guard(baseline, parameter, requested)
    journal = Path(journal_path)
    if journal.resolve() == Path(snapshot_path).resolve():
        raise Blocked("Journal cannot be the snapshot file")
    result = {"outcome": "blocked", "parameter": parameter, "expected_before": expected_before,
              "requested": requested, "set_input_attempted": False, "numeric_readback_verified": False,
              "other_parameters_unchanged": False, "undo_attempted": False, "undo_closed": False, "journal_complete": False,
              "pixel_reflection_tested": False, "persistence_tested": False,
              "rollback_attempted": False, "errors": []}
    # x creates a durable exclusive journal before any Host call or mutation.
    with _exclusive_journal(journal, result) as stream:
        undo_started, undo_attempted, setter_exception = False, False, False
        before, comp = None, None
        try:
            _record(stream, "begin", {"schema_sha256": SCHEMA_SHA256,
                    "snapshot_sha256": hashlib.sha256(Path(snapshot_path).read_bytes()).hexdigest(),
                    "parameter": parameter, "requested": requested, "expected_before": expected_before})
            before, comp, tool = _observe(resolve, baseline["selection"])
            if before != baseline:
                raise Blocked("Saved snapshot is stale: context, values, or control state changed")
            _target_guard(before, parameter, requested)
            _record(stream, "preflight_passed", before)
            # A snapshot is one-shot even if the chosen journal filename changes.
            claim = Path(str(snapshot_path) + ".claim")
            save_json({"format": "pressmachine-snapshot-claim-v1", "claimed_utc": _utc()}, claim)
            _record(stream, "before_start_undo", {"meaning": "This call owns its undo group"})
            undo_attempted = True
            result["undo_attempted"] = True
            if comp.StartUndo("Set PressMachine " + parameter) is False:
                raise RuntimeError("StartUndo returned False; undo state is uncertain")
            undo_started = True
            immediate, _, tool = _observe(resolve, baseline["selection"])
            if immediate != before:
                raise Blocked("Context or parameters changed immediately before the setter")
            if _saved_snapshot(snapshot_path) != snapshot:
                raise Blocked("Saved snapshot file changed before the setter")
            _target_guard(immediate, parameter, requested)
            _record(stream, "before_set_input", {
                "parameter": parameter, "frame": baseline["selection"]["frame"],
                "expected_before": expected_before, "requested": requested,
                "meaning": "Setter may execute after this event. Never blindly retry.",
            })
            result["set_input_attempted"] = True
            try:
                returned = tool.SetInput(parameter, requested, baseline["selection"]["frame"])
            except Exception:
                setter_exception = True
                raise
            result["setter_return"] = returned if returned is None or type(returned) in (bool, str) or _number(returned) else "unrecognized"
        except Exception as exc:
            result["errors"].append(type(exc).__name__ + ": " + str(exc))
        finally:
            if undo_started:
                try:
                    if comp.EndUndo(True) is False:
                        raise RuntimeError("EndUndo returned False")
                    result["undo_closed"] = True
                except Exception as exc:
                    result["errors"].append("EndUndo: " + type(exc).__name__ + ": " + str(exc))
        if result["set_input_attempted"]:
            try:
                # SetInput can start a normal composition preview immediately.
                # Only post-write observation permits that; project rendering,
                # a locked comp, or changed context/identity still blocks it.
                after, _, _ = _observe(resolve, baseline["selection"], require_idle=False)
                result["after"] = after
                result["readback"] = after["values"][parameter]
                result["numeric_readback_verified"] = result["readback"] == requested
                changes = {iid: {"before": before["values"][iid], "after": after["values"][iid]}
                           for iid in PARAMETER_IDS if before["values"][iid] != after["values"][iid]}
                result["changes"] = changes
                result["other_parameters_unchanged"] = all(iid == parameter for iid in changes)
                result["control_state_unchanged"] = after["controls"] == before["controls"]
                _target_guard(after, parameter, requested)
                if (result["numeric_readback_verified"] and result["other_parameters_unchanged"]
                        and result["control_state_unchanged"] and result.get("setter_return") is not False
                        and result["undo_closed"] and not result["errors"]):
                    result["outcome"] = "success_numeric_only"
                else:
                    result["outcome"] = "partial"
                if setter_exception or not result["undo_closed"]:
                    result["outcome"] = "uncertain"
            except Exception as exc:
                result["outcome"] = "uncertain"
                result["errors"].append("Post-write observation: " + type(exc).__name__ + ": " + str(exc))
        elif undo_attempted and not result["undo_closed"]:
            result["outcome"] = "uncertain"
        try:
            result["journal_complete"] = True
            _record(stream, "final", result)
        except Exception as exc:
            result["journal_complete"] = False
            if result["set_input_attempted"] or undo_attempted:
                result["outcome"] = "uncertain"
            result["errors"].append("Final journal: " + type(exc).__name__ + ": " + str(exc))
    return result


def connect_resolve():
    """Load only the conventional installed official SDK. No install/config change."""
    if sys.platform == "win32":
        directory = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Blackmagic Design" / "DaVinci Resolve" / "Support" / "Developer" / "Scripting" / "Modules"
    elif sys.platform == "darwin":
        directory = Path("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
    elif sys.platform.startswith("linux"):
        directory = Path("/opt/resolve/Developer/Scripting/Modules")
    else:
        raise Blocked("Unsupported platform for automatic official SDK lookup")
    path = directory / "DaVinciResolveScript.py"
    if not path.is_file():
        raise Blocked("Official installed DaVinciResolveScript module was not found; use an existing Resolve handle from its scripting console")
    spec = importlib.util.spec_from_file_location("DaVinciResolveScript", path)
    if spec is None or spec.loader is None:
        raise Blocked("Official SDK module could not be loaded")
    sdk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sdk)
    resolve = sdk.scriptapp("Resolve")
    if resolve is None:
        raise Blocked("Resolve connection unavailable. No preferences have been changed")
    return resolve


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List existing production targets on the current video clip")
    listing.add_argument("--out", required=True)
    inspection = commands.add_parser("inspect", help="Read all 25 inputs and save a fresh snapshot")
    inspection.add_argument("--targets", required=True)
    inspection.add_argument("--comp", required=True, help="Exact association_name, not COMPS_Name")
    inspection.add_argument("--tool", required=True)
    inspection.add_argument("--tool-id", required=True, type=int)
    inspection.add_argument("--out", required=True)
    setting = commands.add_parser("set", help="One guarded write; never auto-retries")
    setting.add_argument("--snapshot", required=True)
    setting.add_argument("--param", required=True, choices=PARAMETER_IDS)
    setting.add_argument("--expect", required=True, type=json.loads)
    setting.add_argument("--value", required=True, type=json.loads)
    setting.add_argument("--journal", required=True)
    args = parser.parse_args(argv)
    set_call_entered = False
    try:
        resolve = connect_resolve()
        if args.command == "list":
            result = list_targets(resolve)
            save_json(result, args.out)
        elif args.command == "inspect":
            selection = select_target(load_json(args.targets), args.comp, args.tool, args.tool_id)
            result = inspect_target(resolve, selection)
            save_snapshot(result, args.out)
        else:
            set_call_entered = True
            result = set_once(resolve, args.snapshot, args.param, args.expect, args.value, args.journal)
        print(_json_text(result), end="")
        return {"success_numeric_only": 0, "blocked": 2, "partial": 3, "uncertain": 4}.get(result.get("outcome"), 0)
    except Exception as exc:
        # Unexpected failures while a setter call is in progress cannot prove
        # that no mutation happened. Never label those as safely blocked.
        uncertain = set_call_entered and not isinstance(exc, (Blocked, FileExistsError))
        outcome = "uncertain" if uncertain else "blocked"
        print(_json_text({"outcome": outcome, "error": type(exc).__name__ + ": " + str(exc)}), end="", file=sys.stderr)
        return 4 if uncertain else 2


if __name__ == "__main__":
    raise SystemExit(main())
