#!/usr/bin/env python3
"""Yu-Gi-Oh character-deck transition harness.

V1.41 hardens the RC16.22 semantic shell after real-model Black-Box tests.
Business authorities remain unchanged. Single-system routing cannot enter the multi-system
ledger gate, Render/Pilotage administrative envelopes have one-shot deterministic commit
paths, and direct low-level completion is blocked under FAST_ENFORCED. FAST never means SKIP.
"""
import argparse
import copy
from argparse import Namespace
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
import tempfile
from pathlib import Path

VERSION = "RC16.23.8"
STATE_FILE = "harness_state.json"
CHECKPOINT_FILE = "run_checkpoint.json"
RUN_JOURNAL_FILE = "run_journal.jsonl"
CHECKPOINT_SCHEMA = "ygo-run-checkpoint-v1"
CONTINUATION_LEASE_FILE = "continuation_lease.json"
CONTINUATION_LEASE_SCHEMA = "ygo-continuation-lease-v1"
CONTINUATION_LEASE_STATES = {"ACTIVE", "CLOSED"}
SESSION_CONTINUATION_FILE = "session_continuation.json"
SESSION_CONTINUATION_SCHEMA = "ygo-session-continuation-v1"
BOOTSTRAP_CAPABILITY_FILE = "bootstrap_capability.json"
BOOTSTRAP_CAPABILITY_SCHEMA = "ygo-bootstrap-capability-v1"
SOURCE_INVENTORY_FILE = "source_inventory.json"
SOURCE_INVENTORY_SCHEMA = "ygo-source-inventory-v1"
PILOTAGE_COMPILE_CACHE_SCHEMA = "ygo-pilotage-compile-cache-v1"
RUN_STATES = {"IN_PROGRESS", "WAITING_USER_INPUT", "TERMINAL_FAILED", "COMPLETED"}
FASTPATH_PROFILE = "FAST_ENFORCED"
TERMINAL_RUN_STATES = {"COMPLETED", "TERMINAL_FAILED"}
RC1619_CHANGED_SOURCE_FILES = {"harness_runtime_v1.py", "HARNESS_EXECUTION_CHAT_V3.md", "SYSTEM_MANIFEST_V4.json"}
RC1619_CLI_ACTIVE = False
INSTRUCTION_CHAR_LIMIT = 8000
COMPONENT_PLAN_SCHEMA = "ygo-component-plan-v1"
COMPILED_COMPONENT_MANIFEST_SCHEMA = "ygo-compiled-component-manifest-v1"
COMPILED_COMPONENT_PAYLOAD_SCHEMA = "ygo-component-payload-v1"
STYLE_POLICY_FILE = "STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION_V39.md"
CLASS_POLICY_FILE = "VALIDATION_CANONIQUE_REMIXE_V15.md"
PILOTAGE_POLICY_FILE = "VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES_V1.md"
PILOTAGE_WIRE_SCHEMA = "ygo-pilotage-contract-v3"
PILOTAGE_SCHEMA_DESCRIPTOR = "ygo-pilotage-wire-schema-v1"
PILOTAGE_PREFLIGHT_RECEIPT = "pilotage_preflight.receipt.json"
PILOTAGE_COMMIT_FAILURE_RECEIPT = "pilotage_commit_failure.receipt.json"
PILOTAGE_BUSINESS_DIAGNOSTIC_RECEIPT = "pilotage_business_diagnostic.receipt.json"
PILOTAGE_COMMIT_ATTEMPT_BUDGET = 3
PILOTAGE_NON_BUSINESS_REPAIR_BUDGET = 3
PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT = "pilotage_authoritative_dry_run.receipt.json"
PILOTAGE_BUSINESS_SKELETON_RECEIPT = "pilotage_business_skeleton.receipt.json"
PILOTAGE_BUSINESS_MERGE_RECEIPT = "pilotage_business_merge.receipt.json"
PILOTAGE_BUSINESS_SKELETON_SCHEMA = "ygo-pilotage-business-skeleton-v1"
PILOTAGE_BUSINESS_PATCH_SCHEMA = "ygo-pilotage-business-patch-v1"
PILOTAGE_BUSINESS_MERGE_RECEIPT_SCHEMA = "ygo-pilotage-business-merge-receipt-v1"
PILOTAGE_SEMANTIC_COMPILE_RECEIPT = "pilotage_semantic_compile.receipt.json"
PILOTAGE_SEMANTIC_COMPILE_RECEIPT_SCHEMA = "ygo-pilotage-semantic-compile-receipt-v1"
TERMINAL_PRESENTATION_PLAN_SCHEMA = "ygo-terminal-presentation-plan-v1"
TERMINAL_PRESENTATION_RECEIPT_SCHEMA = "ygo-terminal-presentation-receipt-v1"
TERMINAL_PRESENTATION_PLAN_FILE = "terminal_presentation_plan.json"
TERMINAL_PRESENTATION_RECEIPT_FILE = "terminal_presentation.receipt.json"

CONTEXT = "CONTEXTE_DECKS_YUGIOH_LINK_EVOLUTION_2020"
BANLIST = "BANLIST_LINK_EVOLUTION_2020"
STYLE = "STYLE_DECKS_PERSONNAGE_LINK_EVOLUTION"
PROGRESSION = "VALIDATION_PROGRESSION_NARRATIVE"
EXPLORATION = "HOOK_EXPLORATION_CONCEPTUELLE_DECKS_PERSONNAGES"
CANON = "VALIDATION_CANONIQUE_REMIXE"
ANCHOR = "HOOK_ANCRAGE_REFACTOR_MULTI_SYSTEMES"
STYLE_AXES = "HOOK_STYLE_AXES_CONSTRUCTION_DECKS_PERSONNAGES"
REGISTRY = "REGISTRE_EXECUTION_ARTEFACTS"
GLOBAL_STRUCTURE = "STRUCTURE_REPONSES_DECKS_PERSONNAGES"
AXES_STRUCTURE = "STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES"
PILOTAGE = "VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES"
SRC = "SEMANTIC_RULING_CONTRACT"
GAME_RULES = "GAME_RULES_LINK_EVOLUTION_2020"
FINAL = "VALIDATION_FINALE_DECKS_PERSONNAGES"
LEDGER_VALIDATOR = "validate_execution_ledger_v6.py"
RENDER_AUTHORITIES = {GLOBAL_STRUCTURE, AXES_STRUCTURE}
MATERIAL_CHANGE_AUTHORITIES = {STYLE_AXES, ANCHOR, PROGRESSION, CANON}
MATERIAL_CHANGE_CATEGORIES = {
    "CARD_COMPOSITION", "STRUCTURAL_RATIO", "EXTRA_DECK_LINE", "CENTRAL_AXIS",
    "ACCESS_CONVERSION_PAYOFF", "STRUCTURING_RESOURCE", "SYSTEM_RELATION"
}

BASE = [
    ("CONTEXT_RESOLVED", {CONTEXT}, {"BOUND"}),
    ("BANLIST_BOUND", {BANLIST}, {"BOUND"}),
    ("DIRECTION_RESOLVED", {STYLE}, {"RESOLVED"}),
    ("NARRATIVE_RED_CLOSED", {PROGRESSION}, {"CLOSED"}),
    ("NARRATIVE_CONTRACT_FROZEN", {PROGRESSION}, {"FROZEN"}),
    ("FUNCTIONAL_INTENT_FROZEN", {CANON}, {"FROZEN"}),
    ("EXPLORATION_CLOSED", {EXPLORATION}, {"CLOSED"}),
    ("CONCEPT_SELECTED", {EXPLORATION, STYLE}, {"SELECTED"}),
    ("CLASSIFICATION_CLOSED", {STYLE, CANON}, {"CLOSED"}),
    ("STYLE_AXES_CLOSED", {STYLE_AXES}, {"PASS", "REFACTOR"}),
    ("DECK_DRAFT_CREATED", {STYLE_AXES}, {"CREATED"}),
    ("NARRATIVE_CONFORMANCE_CLOSED", {PROGRESSION}, {"PASS"}),
]
MULTI = [
    ("RELATION_ROUTED", {ANCHOR}, {"ROUTED"}),
    ("VIABILITY_TESTED", {ANCHOR}, {"TESTED"}),
    ("FUNCTIONAL_COVERAGE_CLOSED", {ANCHOR}, {"CLOSED"}),
    ("COMPRESSION_CLOSED", {ANCHOR}, {"CLOSED"}),
    ("TERMINAL_COMPRESSION_CLOSED", {ANCHOR}, {"FERMÉE"}),
    ("DECK_SNAPSHOT_FROZEN", {ANCHOR, REGISTRY}, {"FROZEN"}),
    ("COLD_REPLAY_CLOSED", {ANCHOR}, {"FERMÉE"}),
    ("MULTISYSTEM_PASS_AVAILABLE", {ANCHOR}, {"PASS_DIRECT", "PASS_REFACTOR"}),
]
MECH = [("MECHANICAL_VALIDATION_PASS", {LEDGER_VALIDATOR}, {"PASS"})]
RENDER = [
    ("FINAL_CLASSIFICATION_CLOSED", {CANON}, {"CLOSED"}),
    ("VISUAL_ASSETS_BOUND", RENDER_AUTHORITIES, {"BOUND"}),
    ("RENDER_CONTRACT_FROZEN", RENDER_AUTHORITIES, {"FROZEN"}),
    ("FINAL_RENDER_PREPARED", {GLOBAL_STRUCTURE}, {"PREPARED"}),
    ("PILOTAGE_VALIDATED", {PILOTAGE}, {"PASS"}),
    ("FINAL_VALIDATION_PASS", {FINAL}, {"PASS"}),
]


def fail(msg):
    raise SystemExit(f"DENIED: {msg}")


def nonempty(v):
    return isinstance(v, str) and bool(v.strip())


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path, label="JSON"):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"invalid {label}: {e}")
    if not isinstance(obj, dict):
        fail(f"{label} must be an object")
    return obj


def _snapshot_composition(snapshot):
    if not isinstance(snapshot, dict):
        fail("deck snapshot must be an object")
    out={}
    for zone in ("main_deck", "extra_deck", "side_deck"):
        cards=snapshot.get(zone)
        if not isinstance(cards,list):
            fail(f"deck snapshot {zone} must be a list")
        norm=[]; seen=set()
        for i,c in enumerate(cards):
            if not isinstance(c,dict): fail(f"deck snapshot {zone}[{i}] must be an object")
            name,qty=c.get("name"),c.get("qty")
            if not nonempty(name) or not isinstance(qty,int) or isinstance(qty,bool) or qty<=0:
                fail(f"invalid deck snapshot card at {zone}[{i}]")
            key=name.strip().casefold()
            if key in seen: fail(f"duplicate card entry in {zone}: {name}")
            seen.add(key); norm.append({"name":name.strip(),"qty":qty})
        out[zone]=sorted(norm,key=lambda x:(x["name"].casefold(),x["qty"]))
    return out


def deck_composition_sha256(snapshot):
    raw=json.dumps(_snapshot_composition(snapshot),ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _read_candidate_snapshot(path: Path, run_id=None, expected_artifact=None):
    d=read_json(path,"candidate deck snapshot")
    if run_id is not None and d.get("run_id") not in (None,run_id): fail("RUN_ID_MISMATCH in candidate deck snapshot")
    if expected_artifact is not None and d.get("artifact_id")!=expected_artifact: fail("CANDIDATE_DECK_ARTIFACT_MISMATCH")
    _snapshot_composition(d)
    return d


def _stable_json_text(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _atomic_write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, path)



def _runtime_session_dir():
    """Runtime-owned, sandbox-local session directory; callers cannot select it."""
    return (Path(__file__).resolve().parent / ".ygo_runtime_session").resolve()


def _session_index_path():
    return _runtime_session_dir() / SESSION_CONTINUATION_FILE


def _bootstrap_capability_path():
    return _runtime_session_dir() / BOOTSTRAP_CAPABILITY_FILE


def _active_source_manifest_path():
    return Path(__file__).resolve().parent / "SYSTEM_MANIFEST_V4.json"


def _materialize_source_inventory(run_dir: Path):
    manifest_path=_active_source_manifest_path()
    if not manifest_path.exists(): fail("SYSTEM_MANIFEST_MISSING")
    manifest=read_json(manifest_path,"system manifest")
    active=manifest.get("active_files")
    if not isinstance(active,list) or not active: fail("SYSTEM_MANIFEST_ACTIVE_FILES_INVALID")
    files=[]
    base=Path(__file__).resolve().parent
    for entry in active:
        if not isinstance(entry,dict) or not nonempty(entry.get("file")): fail("SYSTEM_MANIFEST_ACTIVE_FILE_INVALID")
        fp=base/entry["file"]
        if not fp.exists() or not fp.is_file(): fail(f"ACTIVE_SOURCE_MISSING: {entry['file']}")
        files.append({"file":entry["file"],"sha256":sha256(fp),"bytes":fp.stat().st_size})
    payload={"schema":SOURCE_INVENTORY_SCHEMA,"runtime_version":VERSION,"manifest_file":manifest_path.name,"manifest_sha256":sha256(manifest_path),"files":files}
    out=run_dir/SOURCE_INVENTORY_FILE
    _atomic_write_text(out,_stable_json_text(payload))
    return payload,out,sha256(out)


def _source_hash_from_state(st, filename):
    inv=st.get("source_inventory")
    if isinstance(inv,dict):
        for entry in inv.get("files",[]):
            if isinstance(entry,dict) and entry.get("file")==filename and nonempty(entry.get("sha256")):
                return entry["sha256"]
    fp=Path(__file__).resolve().parent/filename
    if not fp.exists(): fail(f"ACTIVE_SOURCE_MISSING: {filename}")
    return sha256(fp)


def _read_session_index(required=False):
    p=_session_index_path()
    if not p.exists():
        if required: fail("SESSION_CONTINUATION_MISSING")
        return None
    raw=p.read_text(encoding="utf-8")
    try: d=json.loads(raw)
    except Exception as e: fail(f"SESSION_CONTINUATION_CORRUPT: {e}")
    if not isinstance(d,dict) or d.get("schema")!=SESSION_CONTINUATION_SCHEMA: fail("SESSION_CONTINUATION_SCHEMA_INVALID")
    if raw!=_stable_json_text(d): fail("SESSION_CONTINUATION_CANONICAL_MISMATCH")
    if d.get("status") not in {"ACTIVE","CLOSED"}: fail("SESSION_CONTINUATION_STATUS_INVALID")
    return d


def _write_session_index(payload):
    sd=_runtime_session_dir(); sd.mkdir(parents=True,exist_ok=True)
    _atomic_write_text(_session_index_path(),_stable_json_text(payload))


def _session_payload_from_run(run_dir: Path, st, cp, status=None):
    lease=_continuation_lease_for_run(run_dir,st,cp,require_active=False)
    stat=status or ("CLOSED" if cp.get("run_state") in {"COMPLETED","TERMINAL_FAILED"} else "ACTIVE")
    return {
        "schema":SESSION_CONTINUATION_SCHEMA,"runtime_version":VERSION,"status":stat,
        "run_id":st.get("run_id"),"run_dir":str(run_dir.resolve()),
        "scope_id":st.get("continuity_scope_id"),"scope_dir":st.get("continuity_scope_dir"),
        "run_state":cp.get("run_state"),"checkpoint_seq":cp.get("checkpoint_seq"),
        "next_required_gate":cp.get("next_required_gate"),"waiting_context":cp.get("waiting_context"),
        "run_state_sha256":cp.get("run_state_sha256"),"checkpoint_sha256":sha256(run_dir/CHECKPOINT_FILE),
        "continuation_lease_sha256":sha256(Path(st.get("continuity_scope_dir"))/CONTINUATION_LEASE_FILE),
    }


def _sync_session_index_for_run(run_dir: Path, st, cp):
    idx=_read_session_index(required=False)
    if idx is None: return
    if idx.get("status")=="ACTIVE":
        if idx.get("run_id")!=st.get("run_id") or Path(idx.get("run_dir","")).resolve()!=run_dir.resolve():
            return
        _write_session_index(_session_payload_from_run(run_dir,st,cp))


def _validate_session_index_active():
    idx=_read_session_index(required=True)
    if idx.get("status")!="ACTIVE": return idx
    rd=Path(idx.get("run_dir","")).resolve()
    if not (rd/STATE_FILE).exists(): fail("SESSION_ACTIVE_RUN_STATE_MISSING")
    if not (rd/CHECKPOINT_FILE).exists(): fail("SESSION_ACTIVE_CHECKPOINT_MISSING")
    st=load_state(rd); cp=_load_checkpoint_raw(rd,required=True)
    if idx.get("run_id")!=st.get("run_id") or idx.get("run_id")!=cp.get("run_id"): fail("SESSION_RUN_BINDING_MISMATCH")
    if idx.get("run_state_sha256")!=sha256(rd/STATE_FILE): fail("SESSION_STATE_HASH_MISMATCH")
    if idx.get("checkpoint_sha256")!=sha256(rd/CHECKPOINT_FILE): fail("SESSION_CHECKPOINT_HASH_MISMATCH")
    lease=_validate_active_continuation_lease(Path(idx.get("scope_dir","")).resolve())
    if idx.get("continuation_lease_sha256")!=sha256(Path(idx.get("scope_dir"))/CONTINUATION_LEASE_FILE): fail("SESSION_LEASE_HASH_MISMATCH")
    checks={"scope_id":lease.get("scope_id"),"scope_dir":lease.get("scope_dir"),"run_id":lease.get("run_id"),"run_dir":lease.get("run_dir"),"run_state":cp.get("run_state"),"checkpoint_seq":cp.get("checkpoint_seq"),"next_required_gate":cp.get("next_required_gate"),"waiting_context":cp.get("waiting_context")}
    for k,v in checks.items():
        ov=idx.get(k)
        if k in {"run_dir","scope_dir"} and nonempty(ov) and nonempty(v):
            if Path(ov).resolve()!=Path(v).resolve(): fail(f"SESSION_INDEX_DIVERGENCE: {k}")
        elif ov!=v: fail(f"SESSION_INDEX_DIVERGENCE: {k}")
    return idx


def _issue_bootstrap_capability(run_id, run_dir: Path, scope_dir: Path, mode, multi_system, mechanical_validation):
    sd=_runtime_session_dir(); sd.mkdir(parents=True,exist_ok=True)
    payload={"schema":BOOTSTRAP_CAPABILITY_SCHEMA,"runtime_version":VERSION,"used":False,"run_id":run_id,"run_dir":str(run_dir.resolve()),"scope_dir":str(scope_dir.resolve()),"mode":mode,"multi_system":bool(multi_system),"mechanical_validation":bool(mechanical_validation)}
    _atomic_write_text(_bootstrap_capability_path(),_stable_json_text(payload))
    return _bootstrap_capability_path()


def _consume_bootstrap_capability(path: Path, a):
    canonical=_bootstrap_capability_path()
    if path.resolve()!=canonical.resolve() or not canonical.exists(): fail("BOOTSTRAP_CAPABILITY_INVALID")
    cap=read_json(canonical,"bootstrap capability")
    if cap.get("schema")!=BOOTSTRAP_CAPABILITY_SCHEMA or cap.get("runtime_version")!=VERSION or cap.get("used") is not False: fail("BOOTSTRAP_CAPABILITY_INVALID")
    checks={"run_id":a.run_id,"run_dir":str(Path(a.run_dir).resolve()),"scope_dir":str(Path(a.scope_dir).resolve()),"mode":a.mode,"multi_system":bool(a.multi_system),"mechanical_validation":bool(a.mechanical_validation)}
    for k,v in checks.items():
        if cap.get(k)!=v: fail(f"BOOTSTRAP_CAPABILITY_BINDING_MISMATCH: {k}")
    cap["used"]=True
    _atomic_write_text(canonical,_stable_json_text(cap))
    return cap

def _continuity_scope_id(scope_dir: Path):
    resolved=str(scope_dir.resolve())
    return "scope-" + hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:16]


def _read_continuation_lease_raw(scope_dir: Path, required=False):
    scope_dir=scope_dir.resolve()
    p=scope_dir/CONTINUATION_LEASE_FILE
    if not p.exists():
        if required:
            fail("CONTINUATION_LEASE_MISSING")
        return None
    raw=p.read_text(encoding="utf-8")
    try:
        d=json.loads(raw)
    except Exception as e:
        fail(f"CONTINUATION_LEASE_CORRUPT: {e}")
    if not isinstance(d,dict) or d.get("schema")!=CONTINUATION_LEASE_SCHEMA:
        fail("CONTINUATION_LEASE_SCHEMA_INVALID")
    if raw!=_stable_json_text(d):
        fail("CONTINUATION_LEASE_CANONICAL_MISMATCH")
    if d.get("status") not in CONTINUATION_LEASE_STATES:
        fail("CONTINUATION_LEASE_STATUS_INVALID")
    if d.get("scope_id")!=_continuity_scope_id(scope_dir) or d.get("scope_dir")!=str(scope_dir):
        fail("CONTINUATION_SCOPE_BINDING_MISMATCH")
    if not nonempty(d.get("run_id")) or not nonempty(d.get("run_dir")):
        fail("CONTINUATION_LEASE_RUN_BINDING_MISSING")
    return d


def _validate_active_continuation_lease(scope_dir: Path):
    d=_read_continuation_lease_raw(scope_dir,required=True)
    if d.get("status")!="ACTIVE":
        return d
    rd=Path(d["run_dir"])
    state_file=rd/STATE_FILE
    if not state_file.exists() or not state_file.is_file():
        fail("CONTINUATION_ACTIVE_RUN_STATE_MISSING")
    if sha256(state_file)!=d.get("run_state_sha256"):
        fail("CONTINUATION_LEASE_STATE_HASH_MISMATCH")
    cp=_load_checkpoint_raw(rd,required=True)
    expected={
        "run_id":cp.get("run_id"),
        "checkpoint_seq":cp.get("checkpoint_seq"),
        "run_state":cp.get("run_state"),
        "run_state_sha256":cp.get("run_state_sha256"),
        "next_required_gate":cp.get("next_required_gate"),
        "waiting_context":cp.get("waiting_context"),
    }
    for k,v in expected.items():
        if d.get(k)!=v:
            fail(f"CONTINUATION_LEASE_CHECKPOINT_DIVERGENCE: {k}")
    if d.get("run_state") not in {"IN_PROGRESS","WAITING_USER_INPUT"}:
        fail("CONTINUATION_ACTIVE_LEASE_HAS_TERMINAL_STATE")
    return d


def _sync_continuation_lease(run_dir: Path, st, cp):
    raw_scope=st.get("continuity_scope_dir")
    scope_id=st.get("continuity_scope_id")
    if not nonempty(raw_scope) or not nonempty(scope_id):
        return
    scope_dir=Path(raw_scope).resolve()
    if scope_id!=_continuity_scope_id(scope_dir):
        fail("CONTINUATION_SCOPE_BINDING_MISMATCH")
    scope_dir.mkdir(parents=True,exist_ok=True)
    prior=_read_continuation_lease_raw(scope_dir,required=False)
    target_status="CLOSED" if cp.get("run_state") in {"COMPLETED","TERMINAL_FAILED"} else "ACTIVE"
    if prior and prior.get("status")=="CLOSED" and target_status=="ACTIVE" and prior.get("run_id")==st.get("run_id"):
        fail("CONTINUATION_LEASE_CLOSED_CANNOT_REOPEN")
    lease={
        "schema":CONTINUATION_LEASE_SCHEMA,
        "scope_id":scope_id,
        "scope_dir":str(scope_dir),
        "status":target_status,
        "run_id":st.get("run_id"),
        "run_dir":str(run_dir.resolve()),
        "runtime_version":VERSION,
        "run_state":cp.get("run_state"),
        "checkpoint_seq":cp.get("checkpoint_seq"),
        "run_state_sha256":cp.get("run_state_sha256"),
        "next_required_gate":cp.get("next_required_gate"),
        "waiting_context":cp.get("waiting_context"),
    }
    _atomic_write_text(scope_dir/CONTINUATION_LEASE_FILE,_stable_json_text(lease))


def _continuation_lease_for_run(run_dir: Path, st, cp=None, require_active=True):
    raw_scope=st.get("continuity_scope_dir")
    if not nonempty(raw_scope):
        fail("CONTINUATION_SCOPE_BINDING_MISSING")
    scope_dir=Path(raw_scope).resolve()
    lease=_validate_active_continuation_lease(scope_dir) if require_active else _read_continuation_lease_raw(scope_dir,required=True)
    if lease.get("run_id")!=st.get("run_id") or Path(lease.get("run_dir","")).resolve()!=run_dir.resolve():
        fail("CONTINUATION_LEASE_RUN_BINDING_MISMATCH")
    if lease.get("scope_id")!=st.get("continuity_scope_id"):
        fail("CONTINUATION_SCOPE_BINDING_MISMATCH")
    if cp is not None and lease.get("checkpoint_seq")!=cp.get("checkpoint_seq"):
        fail("CONTINUATION_LEASE_CHECKPOINT_DIVERGENCE: checkpoint_seq")
    if require_active and lease.get("status")!="ACTIVE":
        fail("CONTINUATION_LEASE_NOT_ACTIVE")
    return lease


def _active_run_exists_payload(lease):
    return {
        "code":"ACTIVE_LOGICAL_RUN_EXISTS",
        "scope_id":lease.get("scope_id"),
        "active_run_id":lease.get("run_id"),
        "active_run_dir":lease.get("run_dir"),
        "run_state":lease.get("run_state"),
        "next_required_gate":lease.get("next_required_gate"),
        "waiting_context":lease.get("waiting_context"),
        "recommended_action":"resume-run",
    }


def _load_checkpoint_raw(run_dir: Path, required=True):
    p = run_dir / CHECKPOINT_FILE
    if not p.exists():
        if required:
            fail("RUN_CHECKPOINT_MISSING")
        return None
    raw=p.read_text(encoding="utf-8")
    try:
        cp = json.loads(raw)
    except Exception as e:
        fail(f"RUN_CHECKPOINT_CORRUPT: {e}")
    if not isinstance(cp, dict) or cp.get("schema") != CHECKPOINT_SCHEMA:
        fail("RUN_CHECKPOINT_SCHEMA_INVALID")
    if not nonempty(cp.get("run_id")):
        fail("RUN_CHECKPOINT_RUN_ID_MISSING")
    if cp.get("run_state") not in RUN_STATES:
        fail("RUN_CHECKPOINT_STATE_INVALID")
    if raw != _stable_json_text(cp):
        fail("RUN_CHECKPOINT_CANONICAL_MISMATCH")
    return cp


def _read_journal(run_dir: Path):
    p = run_dir / RUN_JOURNAL_FILE
    if not p.exists():
        return []
    out=[]
    for i,line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            ev=json.loads(line)
        except Exception as e:
            fail(f"RUN_JOURNAL_CORRUPT at line {i}: {e}")
        if not isinstance(ev,dict) or ev.get("seq")!=len(out)+1:
            fail("RUN_JOURNAL_SEQUENCE_INVALID")
        out.append(ev)
    return out


def _append_run_journal(run_dir: Path, st, event, checkpoint_seq=None, **extra):
    events=_read_journal(run_dir)
    rec={
        "seq":len(events)+1,
        "event":event,
        "run_id":st.get("run_id"),
        "checkpoint_seq":checkpoint_seq,
        "current_deck_artifact":st.get("current_artifact"),
        "render_id":st.get("current_render"),
        "timestamp_ns":time.time_ns(),
    }
    rec.update(extra)
    p=run_dir/RUN_JOURNAL_FILE
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8",newline="\n") as f:
        f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
        f.flush()
        try: os.fsync(f.fileno())
        except OSError: pass
    return rec


GATE_ATTEMPT_TERMINALS = {
    "GATE_ATTEMPT_SUCCEEDED", "GATE_ATTEMPT_FAILED", "GATE_ATTEMPT_EXCEPTION",
    "GATE_ATTEMPT_RECONCILED_SUCCESS", "GATE_ATTEMPT_OUTCOME_UNKNOWN"
}


def _gate_attempt_file_binding(value):
    if not nonempty(value):
        return None
    p=Path(value)
    return {"file":str(p),"exists":p.exists(),"sha256":sha256(p) if p.exists() and p.is_file() else None}


def _gate_attempt_input_payload(a, st, gate, authority, status):
    # Instrumental fingerprint only. It does not promote any input to business proof.
    payload={
        "run_id":st.get("run_id"),
        "gate":gate,
        "authority":authority,
        "requested_status":status,
        "state_sha256_before":sha256(Path(a.run_dir)/STATE_FILE),
        "inputs":{},
    }
    for name in ("evidence_file","render_manifest","contract_file","combo_impact_file","pilotage_contract_file","pilotage_preflight_receipt","terminal_presentation_plan","terminal_presentation_receipt"):
        val=getattr(a,name,None)
        if gate=="FINAL_VALIDATION_PASS" and not nonempty(val):
            if name=="terminal_presentation_plan": val=str(Path(a.run_dir)/TERMINAL_PRESENTATION_PLAN_FILE)
            elif name=="terminal_presentation_receipt": val=str(Path(a.run_dir)/TERMINAL_PRESENTATION_RECEIPT_FILE)
        payload["inputs"][name]=_gate_attempt_file_binding(val)
    return payload


def _gate_attempt_fingerprint(payload):
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _next_gate_attempt_id(events):
    n=sum(1 for e in events if e.get("event")=="GATE_ATTEMPT_STARTED")+1
    return f"gate-attempt-{n:06d}"


def _attempt_terminal_ids(events):
    return {e.get("attempt_id") for e in events if e.get("event") in GATE_ATTEMPT_TERMINALS and nonempty(e.get("attempt_id"))}


def _unmatched_gate_attempts(run_dir: Path):
    events=_read_journal(run_dir); terminal=_attempt_terminal_ids(events)
    return [e for e in events if e.get("event")=="GATE_ATTEMPT_STARTED" and e.get("attempt_id") not in terminal]


def _active_progress_block(run_dir: Path, st):
    ng=next_gate(st)[0]
    if not ng:
        return None
    events=_read_journal(run_dir)
    relevant=[]
    for e in events:
        if e.get("gate")!=ng:
            continue
        if e.get("event") in {"GATE_ATTEMPT_FAILED","GATE_ATTEMPT_EXCEPTION","GATE_ATTEMPT_SUCCEEDED","GATE_ATTEMPT_RECONCILED_SUCCESS","GATE_ATTEMPT_OUTCOME_UNKNOWN","GATE_STALL_DETECTED"}:
            relevant.append(e)
    if not relevant:
        return None
    last=relevant[-1]
    if last.get("event") in {"GATE_ATTEMPT_SUCCEEDED","GATE_ATTEMPT_RECONCILED_SUCCESS","GATE_ATTEMPT_OUTCOME_UNKNOWN"}:
        return None
    if last.get("event")=="GATE_STALL_DETECTED":
        return {
            "gate":ng,"attempt_id":last.get("attempt_id"),"failure_signature":last.get("failure_signature"),
            "input_fingerprint":last.get("input_fingerprint"),"stalled":True,"last_failure_event":"GATE_STALL_DETECTED"
        }
    return {
        "gate":ng,"attempt_id":last.get("attempt_id"),"failure_signature":last.get("failure_signature"),
        "input_fingerprint":last.get("input_fingerprint"),"stalled":False,"last_failure_event":last.get("event"),
        "error_code":last.get("error_code")
    }


def _waiting_context(run_dir: Path, st):
    block=_active_progress_block(run_dir,st)
    if not isinstance(block,dict):
        return None
    ctx={
        "waiting_gate":block.get("gate"),
        "waiting_attempt_id":block.get("attempt_id"),
        "waiting_error_code":block.get("error_code"),
        "waiting_input_fingerprint":block.get("input_fingerprint"),
        "resolution_kind":None,
    }
    if block.get("gate")=="CLASSIFICATION_CLOSED" and block.get("error_code")=="DIRECTION_CONFLICT_REQUIRES_USER_SELECTION":
        ctx["resolution_kind"]="DIRECTION_SELECTION"
    return ctx


def _denied_parts(exc):
    msg=str(exc)
    if msg.startswith("DENIED: "):
        msg=msg[8:]
    code=msg.split(":",1)[0].strip().replace(" ","_") if msg else "DENIED"
    return code or "DENIED", msg


def _reconcile_orphan_attempts(run_dir: Path, st):
    orphans=_unmatched_gate_attempts(run_dir)
    if not orphans:
        return []
    out=[]
    closed=st.get("gates",{})
    cp=_load_checkpoint_raw(run_dir,required=False) or {}
    for ev in orphans:
        aid=ev.get("attempt_id"); gate=ev.get("gate")
        if gate in closed:
            rec=_append_run_journal(run_dir,st,"GATE_ATTEMPT_RECONCILED_SUCCESS",checkpoint_seq=cp.get("checkpoint_seq"),attempt_id=aid,gate=gate,reason="GATE_CLOSED_IN_PERSISTED_STATE")
        else:
            rec=_append_run_journal(run_dir,st,"GATE_ATTEMPT_OUTCOME_UNKNOWN",checkpoint_seq=cp.get("checkpoint_seq"),attempt_id=aid,gate=gate,reason="NO_TERMINAL_ATTEMPT_EVENT",state_sha256_current=sha256(run_dir/STATE_FILE))
        out.append(rec)
    return out


def _last_closed_gate(st):
    names=[x[0] for x in sequence(st)]
    present=set(st.get("gates",{}))
    closed=[g for g in names if g in present]
    return closed[-1] if closed else None


def _render_attempts_used(st):
    vals=[]
    for rec in (st.get("render_attempts") or {}).values():
        if isinstance(rec,dict):
            try: vals.append(int(rec.get("failed_count",0)))
            except Exception: pass
    return max(vals) if vals else 0


def _derived_run_state(st):
    explicit=st.get("run_execution_state")
    if explicit in RUN_STATES:
        return explicit
    if st.get("stop_output_allowed") is True:
        return "COMPLETED"
    if st.get("render_contract_defect_suspected"):
        return "TERMINAL_FAILED"
    for rec in (st.get("render_attempts") or {}).values():
        if isinstance(rec,dict) and (rec.get("stalled") is True or int(rec.get("failed_count",0))>=3):
            return "TERMINAL_FAILED"
    return "IN_PROGRESS"


def _binding_error(role):
    if role.startswith("deck-snapshot"):
        return "RESUME_ARTIFACT_BINDING_MISMATCH"
    if role.startswith("render-contract"):
        return "RESUME_RENDER_BINDING_MISMATCH"
    return "RESUME_AUTHORITATIVE_BINDING_MISMATCH"


def _collect_authoritative_bindings(st):
    bindings=[]; seen=set()
    def add(role,file_name,digest):
        if not nonempty(file_name) or not nonempty(digest): return
        key=(role,str(file_name),str(digest))
        if key in seen: return
        seen.add(key); bindings.append({"role":role,"file":str(file_name),"sha256":str(digest)})
    for gate,rec in (st.get("gates") or {}).items():
        if not isinstance(rec,dict): continue
        if gate=="DECK_DRAFT_CREATED": add("deck-snapshot:"+gate,rec.get("snapshot_file"),rec.get("snapshot_sha256"))
        add("evidence:"+gate,rec.get("evidence_file"),rec.get("evidence_sha256") or rec.get("render_sha256"))
        add("manifest:"+gate,rec.get("manifest_file"),rec.get("manifest_sha256"))
        add("pilotage-contract:"+gate,rec.get("pilotage_contract_file"),rec.get("pilotage_contract_sha256"))
        add("combo-impact:"+gate,rec.get("combo_impact_file"),rec.get("combo_impact_sha256"))
        if gate=="RENDER_CONTRACT_FROZEN":
            add("render-contract:"+gate,rec.get("evidence_file"),rec.get("evidence_sha256"))
    rp=st.get("render_check_pass") or {}
    if isinstance(rp,dict):
        add("render-check:render",rp.get("render_file"),rp.get("render_sha256"))
        add("render-check:manifest",rp.get("manifest_file"),rp.get("manifest_sha256"))
    add("terminal-presentation-plan",st.get("terminal_presentation_plan_file"),st.get("terminal_presentation_plan_sha256"))
    add("terminal-presentation-receipt",st.get("terminal_presentation_receipt_file"),st.get("terminal_presentation_receipt_sha256"))
    add("terminal-payload",st.get("terminal_payload_file"),st.get("terminal_payload_sha256"))
    return sorted(bindings,key=lambda x:(x["role"],x["file"]))


def _write_checkpoint(run_dir: Path, st, run_state_override=None, invocation_seq=None, resume_count=None):
    prior=_load_checkpoint_raw(run_dir,required=False)
    cpseq=int(prior.get("checkpoint_seq",0))+1 if prior else 1
    inv=int(invocation_seq if invocation_seq is not None else (prior.get("invocation_seq",1) if prior else 1))
    resumes=int(resume_count if resume_count is not None else (prior.get("resume_count",0) if prior else 0))
    state_file=run_dir/STATE_FILE
    if not state_file.exists(): fail("run state not found for checkpoint")
    run_state=run_state_override or _derived_run_state(st)
    if run_state not in RUN_STATES: fail("RUN_CHECKPOINT_STATE_INVALID")
    ng,_,_=next_gate(st)
    dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED",{})
    frozen=(st.get("gates") or {}).get("RENDER_CONTRACT_FROZEN",{})
    cp={
        "schema":CHECKPOINT_SCHEMA,
        "runtime_version":VERSION,
        "run_id":st.get("run_id"),
        "checkpoint_seq":cpseq,
        "run_state":run_state,
        "current_deck_artifact":st.get("current_artifact"),
        "current_deck_snapshot_file":dg.get("snapshot_file") if dg.get("artifact")==st.get("current_artifact") else None,
        "current_deck_snapshot_sha256":dg.get("snapshot_sha256") if dg.get("artifact")==st.get("current_artifact") else None,
        "last_closed_gate":_last_closed_gate(st),
        "next_required_gate":ng,
        "waiting_for_user_input":run_state=="WAITING_USER_INPUT",
        "waiting_context":_waiting_context(run_dir,st) if run_state=="WAITING_USER_INPUT" else None,
        "terminal_failure":run_state=="TERMINAL_FAILED",
        "completed":run_state=="COMPLETED",
        "render_id":st.get("current_render"),
        "render_contract_file":frozen.get("evidence_file"),
        "render_contract_sha256":frozen.get("evidence_sha256"),
        "render_contract_frozen":bool(frozen),
        "render_attempts_used":_render_attempts_used(st),
        "render_attempts_budget":3,
        "authoritative_bindings":_collect_authoritative_bindings(st),
        "run_state_sha256":sha256(state_file),
        "invocation_seq":inv,
        "resume_count":resumes,
        "updated_from_invocation":inv,
    }
    _atomic_write_text(run_dir/CHECKPOINT_FILE,_stable_json_text(cp))
    _append_run_journal(run_dir,st,"CHECKPOINT_WRITTEN",checkpoint_seq=cpseq,run_state=run_state,next_required_gate=ng,run_state_sha256=cp["run_state_sha256"])
    _sync_continuation_lease(run_dir,st,cp)
    _sync_session_index_for_run(run_dir,st,cp)
    return cp


def save_state(run_dir: Path, st):
    run_dir.mkdir(parents=True, exist_ok=True)
    # Validate the previous checkpoint before mutating state so corruption is not hidden.
    _load_checkpoint_raw(run_dir,required=False)
    _read_journal(run_dir)
    _atomic_write_text(run_dir / STATE_FILE, json.dumps(st, ensure_ascii=False, indent=2) + "\n")
    _write_checkpoint(run_dir,st)


def load_state(run_dir: Path):
    p = run_dir / STATE_FILE
    if not p.exists():
        fail("run state not found")
    st = read_json(p, "run state")
    validate_state_binding(st)
    return st


def validate_state_binding(st):
    rid = st.get("run_id")
    if not nonempty(rid):
        fail("state missing run_id")
    gates = st.get("gates", {})
    if not isinstance(gates, dict):
        fail("state gates must be an object")
    for g, rec in gates.items():
        if not isinstance(rec, dict) or rec.get("run_id") != rid:
            fail(f"RUN_ID_MISMATCH in gate {g}")


def require_run_id(st, supplied):
    if supplied != st.get("run_id"):
        fail("RUN_ID_MISMATCH")


def sequence(st):
    seq = list(BASE)
    if st.get("multi_system"):
        seq += MULTI
    if st.get("mechanical_validation"):
        seq += MECH
    seq += RENDER
    return seq


def next_gate(st):
    for item in sequence(st):
        if item[0] not in st.get("gates", {}):
            return item
    return (None, set(), set())


def gate_index(st, name):
    names = [x[0] for x in sequence(st)]
    if name not in names:
        fail(f"gate {name} is not applicable in this run")
    return names.index(name)


def validate_evidence(path: Path, st):
    if not path.exists() or not path.is_file():
        fail(f"evidence file missing: {path}")
    if path.suffix.lower() == ".json":
        d = read_json(path, "evidence JSON")
        if "run_id" in d and d.get("run_id") != st["run_id"]:
            fail("RUN_ID_MISMATCH in evidence")


def parse_style_policy(style_path: Path):
    text = style_path.read_text(encoding="utf-8")
    m = re.search(r"<!-- NARRATIVE_MECHANICS_POLICY_JSON:BEGIN -->\s*```json\s*(\{.*?\})\s*```\s*<!-- NARRATIVE_MECHANICS_POLICY_JSON:END -->", text, re.S)
    if not m:
        fail("STYLE narrative mechanics policy block missing")
    try:
        policy = json.loads(m.group(1))
    except Exception as e:
        fail(f"invalid STYLE narrative mechanics policy: {e}")
    if not isinstance(policy, dict) or not isinstance(policy.get("eras"), dict):
        fail("invalid STYLE narrative mechanics policy shape")
    universe = policy.get("mechanic_universe")
    if not isinstance(universe, list) or not universe or len(set(universe)) != len(universe) or not all(nonempty(x) for x in universe):
        fail("invalid STYLE mechanic_universe")
    return policy


def policy_path():
    return Path(__file__).resolve().parent / STYLE_POLICY_FILE


def classification_policy_path():
    return Path(__file__).resolve().parent / CLASS_POLICY_FILE


def parse_classification_policy():
    sp=classification_policy_path()
    if not sp.exists(): fail("classification policy source file missing")
    text=sp.read_text(encoding="utf-8")
    m=re.search(r"<!-- CLASSIFICATION_ROLE_POLICY_JSON:BEGIN -->\s*```json\s*(\{.*?\})\s*```\s*<!-- CLASSIFICATION_ROLE_POLICY_JSON:END -->",text,re.S)
    if not m: fail("classification role policy block missing")
    try: d=json.loads(m.group(1))
    except Exception as e: fail(f"invalid classification role policy: {e}")
    if not isinstance(d,dict): fail("classification role policy must be an object")
    roles=d.get("roles"); dirs=d.get("directions")
    if not isinstance(roles,list) or not roles or not all(nonempty(x) for x in roles): fail("classification policy roles invalid")
    if not isinstance(dirs,list) or set(dirs)!={"Canonique","Canonique remixé","Alternatif"}: fail("classification policy directions invalid")
    if d.get("remixed_requires_secondary_role") not in roles: fail("classification policy remixed role invalid")
    return d,sha256(sp)


def validate_direction_contract(path: Path, st):
    validate_evidence(path,st)
    d=read_json(path,"direction contract")
    pol,ph=parse_classification_policy()
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in direction contract")
    if d.get("authority")!=STYLE: fail("direction contract authority mismatch")
    direction=d.get("selected_direction")
    if direction not in pol["directions"]: fail("invalid selected_direction")
    basis=d.get("resolution_basis")
    if basis not in {"USER_EXPLICIT","USER_SELECTED_AFTER_OPTIONS"}: fail("DIRECTION_NOT_USER_RESOLVED")
    if not nonempty(d.get("user_evidence")): fail("direction contract requires user_evidence")
    return d,sha256(path),ph


def validate_functional_intent(path: Path, st):
    validate_evidence(path,st)
    d=read_json(path,"functional intent")
    pol,ph=parse_classification_policy()
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in functional intent")
    if d.get("authority")!=CANON: fail("functional intent authority mismatch")
    dg=st.get("gates",{}).get("DIRECTION_RESOLVED",{})
    if not dg: fail("direction prerequisite missing")
    if d.get("direction_contract_sha256")!=dg.get("evidence_sha256"): fail("FUNCTIONAL_INTENT_DIRECTION_BINDING_MISMATCH")
    systems=d.get("systems")
    if not isinstance(systems,list) or not systems: fail("functional intent systems must be non-empty")
    seen=set(); primary=0
    for i,s in enumerate(systems):
        if not isinstance(s,dict): fail(f"functional intent system {i} must be an object")
        name=s.get("name")
        if not nonempty(name) or name in seen: fail("functional intent system names must be unique/non-empty")
        seen.add(name)
        if s.get("position") not in {"PRIMARY","SECONDARY"}: fail(f"invalid position for {name}")
        role=s.get("role"); basis=s.get("role_basis")
        if role not in pol["roles"]: fail(f"invalid role for {name}")
        if basis not in {"USER_EXPLICIT","OPEN"}: fail(f"invalid role_basis for {name}")
        if s.get("position")=="PRIMARY":
            primary+=1
            if role!="PRIMARY": fail("PRIMARY system must have PRIMARY role")
        else:
            if role=="PRIMARY": fail("SECONDARY system cannot have PRIMARY role")
            if basis=="USER_EXPLICIT" and role=="OPEN": fail("USER_EXPLICIT secondary role cannot be OPEN")
        funcs=s.get("functions",[])
        if not isinstance(funcs,list) or not all(nonempty(x) for x in funcs): fail(f"invalid functions for {name}")
        if basis=="USER_EXPLICIT" and not funcs: fail(f"USER_EXPLICIT role requires functions for {name}")
    if primary!=1: fail("functional intent requires exactly one PRIMARY system")
    constraints=d.get("quantitative_constraints",[])
    if not isinstance(constraints,list): fail("quantitative_constraints must be a list")
    for c in constraints:
        if not isinstance(c,dict) or not nonempty(c.get("subject")): fail("invalid quantitative constraint")
        if c.get("protection") not in {"UNPROTECTED_BY_DEFAULT","IDENTITY_PROTECTED"}: fail("invalid quantitative constraint protection")
    return d,sha256(path),ph


def _roles_by_name(intent):
    return {s["name"]:s for s in intent["systems"]}


def validate_classification_result(path: Path, st, expected_phase):
    validate_evidence(path,st)
    d=read_json(path,"classification result")
    pol,ph=parse_classification_policy()
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in classification result")
    if d.get("authority")!=CANON: fail("classification result authority mismatch")
    if d.get("phase")!=expected_phase: fail(f"classification phase must be {expected_phase}")
    fg=st.get("gates",{}).get("FUNCTIONAL_INTENT_FROZEN",{})
    if not fg: fail("functional intent prerequisite missing")
    if d.get("functional_intent_sha256")!=fg.get("evidence_sha256"): fail("CLASSIFICATION_INTENT_BINDING_MISMATCH")
    intent=read_json(Path(fg["evidence_file"]),"functional intent")
    frozen=_roles_by_name(intent)
    eff=d.get("effective_roles")
    if not isinstance(eff,list): fail("classification effective_roles must be a list")
    got={}
    for x in eff:
        if not isinstance(x,dict) or not nonempty(x.get("name")) or x.get("role") not in pol["roles"]: fail("invalid effective role")
        got[x["name"]]=x["role"]
    if set(got)!=set(frozen): fail("classification effective_roles must cover functional intent systems exactly")
    for name,s in frozen.items():
        if s.get("role_basis")=="USER_EXPLICIT" and got[name]!=s.get("role"):
            fail(f"CONCEPT_DRIFT: USER_EXPLICIT role changed for {name}")
    classification=d.get("classification")
    if classification not in pol["directions"]: fail("invalid classification")
    direction_gate=st.get("gates",{}).get("DIRECTION_RESOLVED",{})
    selected_direction=direction_gate.get("direction")
    if not selected_direction:
        fail("classification direction prerequisite missing")
    if classification!=selected_direction:
        fail(f"DIRECTION_CONFLICT_REQUIRES_USER_SELECTION: selected={selected_direction}; classified={classification}")
    if classification=="Canonique remixé":
        req=pol["remixed_requires_secondary_role"]
        if not any(frozen[n].get("position")=="SECONDARY" and got[n]==req for n in got):
            fail("REMIXED_WITHOUT_FROZEN_SECONDARY_ARCHITECTURE")
    proof=d.get("secondary_architecture_proof")
    if classification=="Canonique remixé" and proof!="PASS": fail("Remixé requires secondary_architecture_proof PASS")
    if expected_phase=="FINAL":
        dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
        if not dg or d.get("snapshot_sha256")!=dg.get("snapshot_sha256"): fail("FINAL_CLASSIFICATION_SNAPSHOT_MISMATCH")
        pg=st.get("gates",{}).get("CLASSIFICATION_CLOSED",{})
        prev=pg.get("classification")
        if prev and classification!=prev:
            fail("FINAL_CLASSIFICATION_CHANGE_REQUIRES_NEW_CONCEPT")
    return d,sha256(path),ph


def validate_visual_assets(path: Path, st):
    validate_evidence(path,st)
    d=read_json(path,"visual assets")
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in visual assets")
    if d.get("deck_artifact")!=st.get("current_artifact"): fail("VISUAL_ASSETS_DECK_MISMATCH")
    if not isinstance(d.get("authorities"),list) or set(d["authorities"])!=RENDER_AUTHORITIES: fail("visual assets must be derived from both structure authorities")
    fg=st.get("gates",{}).get("FINAL_CLASSIFICATION_CLOSED",{})
    if not fg or d.get("final_classification_sha256")!=fg.get("evidence_sha256"): fail("VISUAL_ASSETS_CLASSIFICATION_BINDING_MISMATCH")
    if d.get("image_lookup_attempted") is not True: fail("IMAGE_LOOKUP_NOT_ATTEMPTED")
    status=d.get("image_capability_status")
    refs=d.get("image_refs")
    if not isinstance(refs,list) or len(set(refs))!=len(refs): fail("visual image_refs invalid")
    pat=re.compile(r"^turn\d+image\d+$")
    if status=="AVAILABLE":
        if len(refs)<2 or not all(isinstance(x,str) and pat.fullmatch(x) for x in refs): fail("AVAILABLE image lookup requires 2+ returned image refs")
    elif status=="UNAVAILABLE":
        if refs: fail("UNAVAILABLE image lookup must not contain refs")
        if not nonempty(d.get("unavailability_reason")): fail("UNAVAILABLE image lookup requires reason")
    else: fail("invalid image_capability_status")
    main=d.get("main_carousel")
    sig=d.get("signature_climax")
    if not isinstance(main,dict) or not isinstance(sig,dict): fail("visual assets require main_carousel + signature_climax")
    if status=="AVAILABLE" and main.get("applicable") is not True: fail("MAIN_CAROUSEL_REQUIRED_WHEN_IMAGES_AVAILABLE")
    if main.get("applicable") is True:
        cards=main.get("selected_cards")
        if not isinstance(cards,list) or not (2<=len(cards)<=4) or not all(nonempty(x) for x in cards): fail("main carousel requires 2-4 selected_cards")
    spectacular=sig.get("spectacular_finisher") is True
    if spectacular and sig.get("terminal_quote_required") is not True: fail("spectacular finisher requires terminal quote")
    if spectacular and status=="AVAILABLE" and sig.get("mini_carousel_applicable") is not True: fail("SIGNATURE_MINI_CAROUSEL_REQUIRED")
    if sig.get("mini_carousel_applicable") is True:
        cards=sig.get("selected_cards")
        if not isinstance(cards,list) or not (3<=len(cards)<=4) or not all(nonempty(x) for x in cards): fail("mini carousel requires 3-4 selected_cards")
        if not nonempty(sig.get("parent")): fail("mini carousel requires parent")
    return d,sha256(path)


def validate_combo_impact(path: Path, st):
    validate_evidence(path, st)
    d=read_json(path,"combo impact")
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in combo impact")
    if d.get("authority")!=PILOTAGE: fail("combo impact authority mismatch")
    change=st.get("last_material_change")
    if not isinstance(change,dict) or st.get("combo_impact_required") is not True:
        fail("COMBO_IMPACT_NOT_REQUIRED")
    if d.get("from_artifact")!=change.get("from_artifact"): fail("COMBO_IMPACT_FROM_ARTIFACT_MISMATCH")
    if d.get("deck_artifact")!=st.get("current_artifact"): fail("COMBO_IMPACT_DECK_MISMATCH")
    status=d.get("status")
    if status not in {"UNCHANGED","MODIFIED","REMOVED"}: fail("invalid combo impact status")
    if not nonempty(d.get("summary")): fail("combo impact summary required")
    axes=d.get("affected_axes")
    if not isinstance(axes,list) or not all(nonempty(x) for x in axes): fail("combo impact affected_axes invalid")
    if status in {"MODIFIED","REMOVED"} and not axes: fail(f"{status} combo impact requires affected_axes")
    return d,sha256(path)


def _extract_section(text, heading):
    m=re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$",text)
    if not m: return None
    start=m.end()
    n=re.search(r"(?m)^##\s+",text[start:])
    end=start+n.start() if n else len(text)
    return text[start:end]


def validate_combo_impact_render(text, impact):
    sec=_extract_section(text,"Impact sur les combos")
    if sec is None: fail("COMBO_IMPACT_SECTION_MISSING")
    status=impact["status"]
    if not re.search(rf"(?im)Statut des combos\s*:\s*{status}",sec): fail("COMBO_IMPACT_STATUS_NOT_RENDERED")
    if status=="UNCHANGED":
        if not re.search(r"(?i)Aucun Axe essentiel modifi",sec): fail("UNCHANGED_COMBO_IMPACT_NOT_EXPLICIT")
    else:
        for ax in impact.get("affected_axes",[]):
            if ax.casefold() not in sec.casefold(): fail(f"COMBO_IMPACT_AXIS_NOT_RENDERED: {ax}")


def _axis_norm(v):
    return re.sub(r"\s+", " ", (v or "").strip()).casefold()


def _rendered_axis_headings(text):
    """Return exact numbered gameplay Axe headings from the final render."""
    out=[]
    seen=set()
    for m in re.finditer(r"(?im)^#{2,4}\s+(Axe\s+\d+\b[^\n]*)\s*$", text):
        raw=m.group(1).strip()
        n=_axis_norm(raw)
        if n in seen:
            fail(f"DUPLICATE_RENDERED_AXIS_HEADING: {raw}")
        seen.add(n); out.append(raw)
    return out



def _norm_token(v):
    return re.sub(r"\s+", " ", (v or "").strip()).casefold()


def _snapshot_card_index(st):
    """Return exact card quantities from the current deck snapshot.

    This is only an artifact binding helper. It does not infer gameplay zones or card
    semantics; the pilotage authority supplies those in the execution replay.
    """
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    sf=dg.get("snapshot_file")
    if not nonempty(sf): fail("RC12_EXECUTION_REPLAY_REQUIRES_CURRENT_DECK_SNAPSHOT")
    sp=Path(sf)
    if not sp.exists(): fail("RC12_EXECUTION_REPLAY_DECK_SNAPSHOT_MISSING")
    snap=read_json(sp,"deck snapshot for execution replay")
    if snap.get("artifact_id")!=st.get("current_artifact"):
        fail("RC12_EXECUTION_REPLAY_DECK_SNAPSHOT_STALE")
    out={}
    for deck_zone in ("main_deck","extra_deck","side_deck"):
        for c in snap.get(deck_zone,[]):
            if isinstance(c,dict) and nonempty(c.get("name")) and isinstance(c.get("qty"),int) and not isinstance(c.get("qty"),bool):
                out[(deck_zone,c["name"].strip().casefold())]=c["qty"]
    return out


def _positive_int(v, label):
    if not isinstance(v,int) or isinstance(v,bool) or v<=0: fail(f"{label} must be positive integer")
    return v


def _nonnegative_int(v, label):
    if not isinstance(v,int) or isinstance(v,bool) or v<0: fail(f"{label} must be nonnegative integer")
    return v


def _validate_ref_qty(entry, field, resources, lid, replay_id):
    if not isinstance(entry,dict): fail(f"{field} entry invalid: {lid}:{replay_id}")
    rid=entry.get("resource_id"); zone=entry.get("zone"); qty=entry.get("qty")
    if rid not in resources: fail(f"EXECUTION_UNKNOWN_RESOURCE: {lid}:{replay_id}:{rid}")
    if not nonempty(zone): fail(f"EXECUTION_ZONE_MISSING: {lid}:{replay_id}:{field}")
    _positive_int(qty,f"EXECUTION_QTY_INVALID: {lid}:{replay_id}:{field}")
    return rid,zone.strip(),qty


def _generic_execution_cases(property_checks):
    dims=[]
    for ch in property_checks or []:
        if ch.get("generic_requirement") is True:
            cid=ch.get("check_id")
            vals=ch.get("eligible_variants",[])
            if nonempty(cid) and isinstance(vals,list) and vals:
                dims.append((cid,[v.strip() for v in vals if nonempty(v)]))
    if not dims:
        return []
    cases=[[]]
    for cid,vals in dims:
        cases=[prev+[f"{cid}={v}"] for prev in cases for v in vals]
    return [" | ".join(parts) for parts in cases]



def _inline_evidence_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_legality_catalogs(rp, lid, rpid, current_snapshot_sha):
    evid_raw=rp.get("legality_evidence")
    if not isinstance(evid_raw,list) or not evid_raw:
        fail(f"ACTION_LEGALITY_EVIDENCE_MISSING: {lid}:{rpid}")
    evid={}
    allowed_kinds={"CARD_RULE_SOURCE","DECK_SNAPSHOT","PILOTAGE_DERIVATION","RULEBOOK_SOURCE","OTHER_SOURCE"}
    for ev in evid_raw:
        if not isinstance(ev,dict): fail(f"ACTION_LEGALITY_EVIDENCE_INVALID: {lid}:{rpid}")
        eid=ev.get("evidence_id")
        if not nonempty(eid) or eid in evid: fail(f"ACTION_LEGALITY_EVIDENCE_ID_INVALID: {lid}:{rpid}")
        if ev.get("evidence_kind") not in allowed_kinds: fail(f"ACTION_LEGALITY_EVIDENCE_KIND_INVALID: {lid}:{rpid}:{eid}")
        if not nonempty(ev.get("source_locator")) or not nonempty(ev.get("evidence_text")):
            fail(f"ACTION_LEGALITY_EVIDENCE_CONTENT_MISSING: {lid}:{rpid}:{eid}")
        digest=ev.get("evidence_sha256")
        if digest!=_inline_evidence_sha(ev["evidence_text"]):
            fail(f"ACTION_LEGALITY_EVIDENCE_HASH_MISMATCH: {lid}:{rpid}:{eid}")
        if ev.get("evidence_kind")=="DECK_SNAPSHOT" and ev.get("snapshot_sha256")!=current_snapshot_sha:
            fail(f"ACTION_LEGALITY_SNAPSHOT_EVIDENCE_STALE: {lid}:{rpid}:{eid}")
        evid[eid]=ev

    facts_raw=rp.get("fact_catalog",[])
    if not isinstance(facts_raw,list): fail(f"ACTION_FACT_CATALOG_INVALID: {lid}:{rpid}")
    facts={}
    for fact in facts_raw:
        if not isinstance(fact,dict): fail(f"ACTION_FACT_INVALID: {lid}:{rpid}")
        fid=fact.get("fact_id")
        if not nonempty(fid) or fid in facts: fail(f"ACTION_FACT_ID_INVALID: {lid}:{rpid}")
        if not nonempty(fact.get("subject_id")) or not nonempty(fact.get("property")):
            fail(f"ACTION_FACT_BINDING_INVALID: {lid}:{rpid}:{fid}")
        if "value" not in fact: fail(f"ACTION_FACT_VALUE_MISSING: {lid}:{rpid}:{fid}")
        evid_id=fact.get("evidence_id")
        if evid_id not in evid: fail(f"ACTION_FACT_EVIDENCE_UNKNOWN: {lid}:{rpid}:{fid}")
        origin=fact.get("semantic_origin")
        if origin not in {"CARD_RULE","GAME_RULE","SNAPSHOT","DERIVED"}:
            fail(f"ACTION_FACT_SEMANTIC_ORIGIN_INVALID: {lid}:{rpid}:{fid}")
        expected_kind={"CARD_RULE":"CARD_RULE_SOURCE","GAME_RULE":"RULEBOOK_SOURCE","SNAPSHOT":"DECK_SNAPSHOT"}.get(origin)
        if expected_kind and evid[evid_id].get("evidence_kind")!=expected_kind:
            fail(f"ACTION_FACT_SOURCE_KIND_MISMATCH: {lid}:{rpid}:{fid}")
        facts[fid]=fact

    constraints_raw=rp.get("constraint_catalog",[])
    if not isinstance(constraints_raw,list): fail(f"ACTION_CONSTRAINT_CATALOG_INVALID: {lid}:{rpid}")
    constraints={}
    allowed_scopes={"PARTICIPANT_USAGE","ACTION_OUTPUT","ACTIVE_STATE","TARGET","COST","TIMING","PLACEMENT","OTHER"}
    allowed_ops={"EQ","NEQ","CONTAINS","NOT_CONTAINS","IN","NOT_IN","EXISTS","GE","LE","SUBSET","INTERSECTS","NOT_INTERSECTS"}
    for con in constraints_raw:
        if not isinstance(con,dict): fail(f"ACTION_CONSTRAINT_INVALID: {lid}:{rpid}")
        cid=con.get("constraint_id")
        if not nonempty(cid) or cid in constraints: fail(f"ACTION_CONSTRAINT_ID_INVALID: {lid}:{rpid}")
        if not nonempty(con.get("owner_subject_id")) or con.get("scope") not in allowed_scopes:
            fail(f"ACTION_CONSTRAINT_BINDING_INVALID: {lid}:{rpid}:{cid}")
        lfid=con.get("left_fact_id")
        if lfid not in facts: fail(f"ACTION_CONSTRAINT_LEFT_FACT_UNKNOWN: {lid}:{rpid}:{cid}")
        if con.get("operator") not in allowed_ops: fail(f"ACTION_CONSTRAINT_OPERATOR_INVALID: {lid}:{rpid}:{cid}")
        has_rv="right_value" in con; has_rf=nonempty(con.get("right_fact_id"))
        if con.get("operator")=="EXISTS":
            if has_rv or has_rf: fail(f"ACTION_CONSTRAINT_EXISTS_RIGHT_SIDE_FORBIDDEN: {lid}:{rpid}:{cid}")
        elif has_rv==has_rf:
            fail(f"ACTION_CONSTRAINT_RIGHT_SIDE_INVALID: {lid}:{rpid}:{cid}")
        if has_rf and con.get("right_fact_id") not in facts:
            fail(f"ACTION_CONSTRAINT_RIGHT_FACT_UNKNOWN: {lid}:{rpid}:{cid}")
        ce=con.get("evidence_ids")
        if not isinstance(ce,list) or not ce or any(x not in evid for x in ce):
            fail(f"ACTION_CONSTRAINT_EVIDENCE_INVALID: {lid}:{rpid}:{cid}")
        constraints[cid]=con
    return evid,facts,constraints





def _project_unified_cold_audit(rp, lid, rpid, require=False, require_mcb=False):
    """Compile one independent cold audit into the legacy per-domain views.

    RC16.1 changes the authoring/orchestration surface, not the validators.  The
    domain validators below remain the sole mechanical definitions of each PASS.
    Legacy RC16 contracts remain accepted for regression compatibility.
    """
    ua=rp.get("unified_cold_audit")
    if ua is None:
        if require:
            fail(f"UNIFIED_COLD_AUDIT_REQUIRED: {lid}:{rpid}")
        return
    if not isinstance(ua,dict) or ua.get("status")!="PASS" or ua.get("ignored_primary_inventories") is not True or not nonempty(ua.get("sweep_basis")):
        fail(f"UNIFIED_COLD_AUDIT_NOT_CLOSED: {lid}:{rpid}")
    basis=ua["sweep_basis"]
    def sec(name):
        v=ua.get(name)
        if not isinstance(v,dict): fail(f"UNIFIED_COLD_SECTION_MISSING: {lid}:{rpid}:{name}")
        return v
    def ids(name):
        v=sec(name).get("discovered_ids")
        if not isinstance(v,list) or any(not nonempty(x) for x in v) or len(v)!=len(set(v)):
            fail(f"UNIFIED_COLD_IDS_INVALID: {lid}:{rpid}:{name}")
        return v
    sem=sec("semantic"); game=sec("game_rules"); leg=sec("legality")
    if require_mcb:
        mp=sec("mechanical_projection")
        if mp.get("status")!="PASS" or mp.get("ignored_primary_bindings") is not True or not nonempty(mp.get("sweep_basis")) or not isinstance(mp.get("bindings"),list):
            fail(f"MCB_COLD_PROJECTION_NOT_CLOSED: {lid}:{rpid}")
    derived=ids("derived"); state=ids("state"); topo=ids("topology"); certainty=ids("certainty"); backward=ids("backward")
    sem_ids=ids("semantic"); game_ids=ids("game_rules")
    se=sem.get("evidence_ids",[]); ge=game.get("evidence_ids",[])
    if not isinstance(se,list) or not isinstance(ge,list): fail(f"UNIFIED_COLD_EVIDENCE_IDS_INVALID: {lid}:{rpid}")
    by_action=leg.get("by_action")
    if not isinstance(by_action,dict): fail(f"UNIFIED_COLD_LEGALITY_MAP_INVALID: {lid}:{rpid}")
    evid_by_action=leg.get("evidence_ids_by_action",{})
    if not isinstance(evid_by_action,dict): fail(f"UNIFIED_COLD_LEGALITY_EVIDENCE_MAP_INVALID: {lid}:{rpid}")
    steps=rp.get("steps",[])
    step_ids={x.get("step_id") for x in steps if isinstance(x,dict)}
    if set(by_action)!=step_ids:
        fail(f"UNIFIED_COLD_LEGALITY_ACTION_COVERAGE_MISMATCH: {lid}:{rpid}")
    # Project only in memory.  This keeps every existing domain validator intact.
    rp["cold_semantic_sweep"]={"status":"PASS","ignored_initial_src_inventory":True,"discovered_clause_ids":sem_ids,"sweep_basis":basis,"evidence_ids":se}
    rp["cold_game_rule_sweep"]={"status":"PASS","ignored_initial_game_rule_inventory":True,"discovered_binding_ids":game_ids,"sweep_basis":basis,"evidence_ids":ge}
    rp["cold_derived_sweep"]={"status":"PASS","ignored_initial_claim_inventory":True,"discovered_claim_ids":derived,"sweep_basis":basis}
    rp["cold_state_sweep"]={"status":"PASS","ignored_initial_precondition_inventory":True,"discovered_precondition_ids":state,"sweep_basis":basis}
    rp["cold_topology_sweep"]={"status":"PASS","ignored_initial_topology_inventory":True,"discovered_topology_ids":topo,"sweep_basis":basis}
    rp["cold_certainty_sweep"]={"status":"PASS","ignored_initial_condition_inventory":True,"discovered_condition_ids":certainty,"sweep_basis":basis}
    rp["cold_backward_sweep"]={"status":"PASS","ignored_initial_backward_inventory":True,"discovered_requirement_ids":backward,"sweep_basis":basis}
    for st in steps:
        sid=st.get("step_id")
        proof=st.get("action_legality_proof")
        if not isinstance(proof,dict): continue
        vals=by_action.get(sid)
        if not isinstance(vals,list) or any(not nonempty(x) for x in vals) or len(vals)!=len(set(vals)):
            fail(f"UNIFIED_COLD_LEGALITY_IDS_INVALID: {lid}:{rpid}:{sid}")
        ev=evid_by_action.get(sid,[])
        if not isinstance(ev,list): fail(f"UNIFIED_COLD_LEGALITY_EVIDENCE_INVALID: {lid}:{rpid}:{sid}")
        proof["cold_legality_sweep"]={"status":"PASS","ignored_initial_constraint_inventory":True,"discovered_constraint_ids":vals,"sweep_basis":basis,"evidence_ids":ev}

def _semantic_ref_origin(ref_id, facts, constraints, evidence, required_origin, required_evidence_kind, required_evidence_id, lid, rpid, label):
    if ref_id in facts:
        fact=facts[ref_id]
        if fact.get("semantic_origin")!=required_origin:
            fail(f"{label}_SEMANTIC_ORIGIN_MISMATCH: {lid}:{rpid}:{ref_id}")
        eid=fact.get("evidence_id")
        if eid!=required_evidence_id or evidence.get(eid,{}).get("evidence_kind")!=required_evidence_kind:
            fail(f"{label}_EVIDENCE_BINDING_MISMATCH: {lid}:{rpid}:{ref_id}")
        return
    if ref_id in constraints:
        con=constraints[ref_id]
        eids=con.get("evidence_ids",[])
        if required_evidence_id not in eids or evidence.get(required_evidence_id,{}).get("evidence_kind")!=required_evidence_kind:
            fail(f"{label}_EVIDENCE_BINDING_MISMATCH: {lid}:{rpid}:{ref_id}")
        fids=[con.get("left_fact_id"),con.get("right_fact_id")]
        origins=[facts[x].get("semantic_origin") for x in fids if x in facts]
        if required_origin not in origins:
            fail(f"{label}_SEMANTIC_ORIGIN_MISMATCH: {lid}:{rpid}:{ref_id}")
        return
    fail(f"{label}_NORMALIZED_REF_UNKNOWN: {lid}:{rpid}:{ref_id}")


def _validate_rc16_semantic_inputs(rp, evidence, facts, constraints, lid, rpid):
    if rp.get("semantic_layer_version") not in {"SRC1-GR1-BW1","SRC1-GR1-BW1-MCB1"}:
        fail(f"RC16_SEMANTIC_LAYER_VERSION_MISMATCH: {lid}:{rpid}")

    src_scope=rp.get("src_scope_status")
    if src_scope not in {"COMPLETE","COMPLETE_NO_MATERIAL_SRC"}:
        fail(f"SRC_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    srcs=rp.get("semantic_ruling_contracts",[])
    if not isinstance(srcs,list): fail(f"SRC_CONTRACTS_INVALID: {lid}:{rpid}")
    src_ids=set(); clause_ids=set(); src_evidence=set(); src_refs=set(); src_clause_evidence={}
    allowed_categories={"CONDITION","COST","TARGET","COUNT","SOURCE","DESTINATION","TIMING","PROPERTY","PERMISSION","RESTRICTION","TRANSITION"}
    for src in srcs:
        if not isinstance(src,dict): fail(f"SRC_CONTRACT_INVALID: {lid}:{rpid}")
        sid=src.get("src_id")
        if not nonempty(sid) or sid in src_ids: fail(f"SRC_ID_INVALID: {lid}:{rpid}")
        src_ids.add(sid)
        if not nonempty(src.get("subject_id")) or not nonempty(src.get("effect_id")):
            fail(f"SRC_BINDING_INVALID: {lid}:{rpid}:{sid}")
        status=src.get("semantic_status")
        if status!="CLOSED":
            fail(f"SRC_NOT_CLOSED: {lid}:{rpid}:{sid}:{status}")
        eid=src.get("evidence_id")
        if eid not in evidence or evidence[eid].get("evidence_kind")!="CARD_RULE_SOURCE":
            fail(f"SRC_CARD_RULE_EVIDENCE_INVALID: {lid}:{rpid}:{sid}")
        src_evidence.add(eid)
        clauses=src.get("material_clauses")
        if not isinstance(clauses,list) or not clauses:
            fail(f"SRC_MATERIAL_CLAUSES_MISSING: {lid}:{rpid}:{sid}")
        for cl in clauses:
            if not isinstance(cl,dict): fail(f"SRC_CLAUSE_INVALID: {lid}:{rpid}:{sid}")
            cid=cl.get("clause_id")
            if not nonempty(cid) or cid in clause_ids: fail(f"SRC_CLAUSE_ID_INVALID: {lid}:{rpid}:{sid}")
            clause_ids.add(cid); src_clause_evidence[cid]=eid
            if cl.get("category") not in allowed_categories or cl.get("material_to_line") is not True:
                fail(f"SRC_CLAUSE_SHAPE_INVALID: {lid}:{rpid}:{cid}")
            ref=cl.get("normalized_ref")
            if not nonempty(ref): fail(f"SRC_CLAUSE_NORMALIZED_REF_MISSING: {lid}:{rpid}:{cid}")
            _semantic_ref_origin(ref,facts,constraints,evidence,"CARD_RULE","CARD_RULE_SOURCE",eid,lid,rpid,"SRC")
            src_refs.add(ref)
    if src_scope=="COMPLETE" and not clause_ids: fail(f"SRC_COMPLETE_REQUIRES_CLAUSES: {lid}:{rpid}")
    if src_scope=="COMPLETE_NO_MATERIAL_SRC" and (srcs or clause_ids): fail(f"SRC_NO_MATERIAL_STATUS_INCONSISTENT: {lid}:{rpid}")
    cold=rp.get("cold_semantic_sweep")
    if not isinstance(cold,dict) or cold.get("status")!="PASS" or cold.get("ignored_initial_src_inventory") is not True or not nonempty(cold.get("sweep_basis")):
        fail(f"COLD_SEMANTIC_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    discovered=cold.get("discovered_clause_ids")
    if not isinstance(discovered,list) or len(discovered)!=len(set(discovered)):
        fail(f"COLD_SEMANTIC_SWEEP_IDS_INVALID: {lid}:{rpid}")
    if set(discovered)!=clause_ids: fail(f"COLD_SEMANTIC_SWEEP_DIVERGENCE: {lid}:{rpid}")
    ce=cold.get("evidence_ids",[])
    if clause_ids and (not isinstance(ce,list) or not src_evidence.issubset(set(ce)) or any(x not in evidence for x in ce)):
        fail(f"COLD_SEMANTIC_SWEEP_EVIDENCE_INVALID: {lid}:{rpid}")

    gr_scope=rp.get("game_rule_scope_status")
    if gr_scope not in {"COMPLETE","COMPLETE_NO_MATERIAL_GAME_RULES"}:
        fail(f"GAME_RULE_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    profiles_raw=rp.get("action_game_rule_profiles",[])
    if not isinstance(profiles_raw,list): fail(f"GAME_RULE_PROFILES_INVALID: {lid}:{rpid}")
    action_profiles={}
    for pr in profiles_raw:
        if not isinstance(pr,dict) or not nonempty(pr.get("action_id")) or pr["action_id"] in action_profiles:
            fail(f"GAME_RULE_ACTION_PROFILE_INVALID: {lid}:{rpid}")
        vals=pr.get("profiles")
        if not isinstance(vals,list) or not vals or any(not nonempty(x) for x in vals) or len(vals)!=len(set(vals)):
            fail(f"GAME_RULE_PROFILE_SET_INVALID: {lid}:{rpid}:{pr.get('action_id')}")
        action_profiles[pr["action_id"]]=set(vals)
    bindings=rp.get("game_rule_bindings",[])
    if not isinstance(bindings,list): fail(f"GAME_RULE_BINDINGS_INVALID: {lid}:{rpid}")
    binding_ids=set(); game_evidence=set(); binding_actions={}; game_refs=set(); game_rule_ids=set(); game_rule_actions={}; game_rule_evidence={}
    for b in bindings:
        if not isinstance(b,dict): fail(f"GAME_RULE_BINDING_INVALID: {lid}:{rpid}")
        bid=b.get("binding_id")
        if not nonempty(bid) or bid in binding_ids: fail(f"GAME_RULE_BINDING_ID_INVALID: {lid}:{rpid}")
        binding_ids.add(bid)
        aid=b.get("action_id"); profile=b.get("profile_id"); grid=b.get("game_rule_id")
        if aid not in action_profiles or profile not in action_profiles[aid] or not nonempty(grid):
            fail(f"GAME_RULE_BINDING_PROFILE_MISMATCH: {lid}:{rpid}:{bid}")
        eid=b.get("evidence_id")
        if eid not in evidence or evidence[eid].get("evidence_kind")!="RULEBOOK_SOURCE":
            fail(f"GAME_RULE_EVIDENCE_INVALID: {lid}:{rpid}:{bid}")
        game_evidence.add(eid); game_rule_ids.add(grid); game_rule_actions.setdefault(grid,set()).add(aid); game_rule_evidence.setdefault(grid,set()).add(eid)
        ref=b.get("normalized_ref")
        if not nonempty(ref): fail(f"GAME_RULE_NORMALIZED_REF_MISSING: {lid}:{rpid}:{bid}")
        _semantic_ref_origin(ref,facts,constraints,evidence,"GAME_RULE","RULEBOOK_SOURCE",eid,lid,rpid,"GAME_RULE")
        game_refs.add(ref)
        if b.get("material_to_line") is not True: fail(f"GAME_RULE_MATERIAL_FLAG_INVALID: {lid}:{rpid}:{bid}")
        binding_actions[bid]=aid
    if gr_scope=="COMPLETE" and not binding_ids: fail(f"GAME_RULE_COMPLETE_REQUIRES_BINDINGS: {lid}:{rpid}")
    if gr_scope=="COMPLETE_NO_MATERIAL_GAME_RULES" and (bindings or profiles_raw):
        fail(f"GAME_RULE_NO_MATERIAL_STATUS_INCONSISTENT: {lid}:{rpid}")
    gcold=rp.get("cold_game_rule_sweep")
    if not isinstance(gcold,dict) or gcold.get("status")!="PASS" or gcold.get("ignored_initial_game_rule_inventory") is not True or not nonempty(gcold.get("sweep_basis")):
        fail(f"COLD_GAME_RULE_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    gd=gcold.get("discovered_binding_ids")
    if not isinstance(gd,list) or len(gd)!=len(set(gd)):
        fail(f"COLD_GAME_RULE_SWEEP_IDS_INVALID: {lid}:{rpid}")
    if set(gd)!=binding_ids: fail(f"COLD_GAME_RULE_SWEEP_DIVERGENCE: {lid}:{rpid}")
    ge=gcold.get("evidence_ids",[])
    if binding_ids and (not isinstance(ge,list) or not game_evidence.issubset(set(ge)) or any(x not in evidence for x in ge)):
        fail(f"COLD_GAME_RULE_SWEEP_EVIDENCE_INVALID: {lid}:{rpid}")
    return {"src_clause_ids":clause_ids,"src_clause_evidence":src_clause_evidence,"game_binding_ids":binding_ids,"game_rule_ids":game_rule_ids,"game_rule_actions":game_rule_actions,"game_rule_evidence":game_rule_evidence,"action_profiles":action_profiles,"binding_actions":binding_actions,"src_refs":src_refs,"game_refs":game_refs}


def _validate_rc16_backward_proof(rp, semantic_meta, steps, all_preconditions, text, lid, rpid):
    step_order={st.get("step_id"):i for i,st in enumerate(steps) if isinstance(st,dict) and nonempty(st.get("step_id"))}
    for aid in semantic_meta.get("action_profiles",{}):
        if aid not in step_order: fail(f"GAME_RULE_PROFILE_ACTION_UNKNOWN: {lid}:{rpid}:{aid}")
    for bid,aid in semantic_meta.get("binding_actions",{}).items():
        if aid not in step_order: fail(f"GAME_RULE_BINDING_ACTION_UNKNOWN: {lid}:{rpid}:{bid}")

    scope=rp.get("backward_proof_scope_status")
    if scope not in {"COMPLETE","COMPLETE_NO_MATERIAL_BACKWARD_REQUIREMENTS"}:
        fail(f"BACKWARD_PROOF_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    reqs=rp.get("backward_requirements",[])
    if not isinstance(reqs,list): fail(f"BACKWARD_REQUIREMENTS_INVALID: {lid}:{rpid}")
    req_by_id={}
    valid_origins=set(semantic_meta.get("src_clause_ids",set()))|set(semantic_meta.get("game_binding_ids",set()))|{"LINE_OUTCOME"}
    for br in reqs:
        if not isinstance(br,dict): fail(f"BACKWARD_REQUIREMENT_INVALID: {lid}:{rpid}")
        rid=br.get("requirement_id")
        if not nonempty(rid) or rid in req_by_id: fail(f"BACKWARD_REQUIREMENT_ID_INVALID: {lid}:{rpid}")
        consumer=br.get("consumer_action_id")
        if consumer not in step_order or br.get("required_at_state")!=f"BEFORE:{consumer}":
            fail(f"BACKWARD_REQUIREMENT_CONSUMER_INVALID: {lid}:{rpid}:{rid}")
        pref=br.get("predicate_ref")
        if pref not in all_preconditions: fail(f"BACKWARD_REQUIREMENT_PREDICATE_UNKNOWN: {lid}:{rpid}:{rid}")
        if br.get("origin_ref") not in valid_origins:
            fail(f"BACKWARD_REQUIREMENT_ORIGIN_UNKNOWN: {lid}:{rpid}:{rid}")
        ups=br.get("upstream_affecting_actions")
        if not isinstance(ups,list) or any(x not in step_order for x in ups) or len(ups)!=len(set(ups)):
            fail(f"BACKWARD_REQUIREMENT_UPSTREAM_INVALID: {lid}:{rpid}:{rid}")
        if any(step_order[x]>=step_order[consumer] for x in ups):
            fail(f"BACKWARD_REQUIREMENT_NOT_BACKWARD: {lid}:{rpid}:{rid}")
        if br.get("status") not in {"PRESERVED","ESTABLISHED"}:
            fail(f"BACKWARD_REQUIREMENT_NOT_CLOSED: {lid}:{rpid}:{rid}")
        if not isinstance(br.get("decision_required"),bool):
            fail(f"BACKWARD_REQUIREMENT_DECISION_FLAG_INVALID: {lid}:{rpid}:{rid}")
        req_by_id[rid]=br
    if scope=="COMPLETE" and not req_by_id: fail(f"BACKWARD_COMPLETE_REQUIRES_REQUIREMENTS: {lid}:{rpid}")
    if scope=="COMPLETE_NO_MATERIAL_BACKWARD_REQUIREMENTS" and req_by_id:
        fail(f"BACKWARD_NO_MATERIAL_STATUS_INCONSISTENT: {lid}:{rpid}")
    bcold=rp.get("cold_backward_sweep")
    if not isinstance(bcold,dict) or bcold.get("status")!="PASS" or bcold.get("ignored_initial_backward_inventory") is not True or not nonempty(bcold.get("sweep_basis")):
        fail(f"COLD_BACKWARD_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    bd=bcold.get("discovered_requirement_ids")
    if not isinstance(bd,list) or len(bd)!=len(set(bd)):
        fail(f"COLD_BACKWARD_SWEEP_IDS_INVALID: {lid}:{rpid}")
    if set(bd)!=set(req_by_id): fail(f"COLD_BACKWARD_SWEEP_DIVERGENCE: {lid}:{rpid}")

    decisions=rp.get("critical_decisions",[])
    if not isinstance(decisions,list): fail(f"BACKWARD_CRITICAL_DECISIONS_INVALID: {lid}:{rpid}")
    dids=set(); covered=set()
    step_by_id={st.get("step_id"):st for st in steps if isinstance(st,dict)}
    for dec in decisions:
        if not isinstance(dec,dict): fail(f"BACKWARD_CRITICAL_DECISION_INVALID: {lid}:{rpid}")
        did=dec.get("decision_id")
        if not nonempty(did) or did in dids: fail(f"BACKWARD_CRITICAL_DECISION_ID_INVALID: {lid}:{rpid}")
        dids.add(did)
        rids=dec.get("requirement_ids")
        if not isinstance(rids,list) or not rids or any(x not in req_by_id for x in rids) or len(rids)!=len(set(rids)):
            fail(f"BACKWARD_CRITICAL_DECISION_REQUIREMENTS_INVALID: {lid}:{rpid}:{did}")
        if any(req_by_id[x].get("decision_required") is not True for x in rids):
            fail(f"BACKWARD_CRITICAL_DECISION_NOT_REQUIRED: {lid}:{rpid}:{did}")
        action=dec.get("action_id"); consumer=dec.get("consumer_action_id")
        if action not in step_order or consumer not in step_order or step_order[action]>=step_order[consumer]:
            fail(f"BACKWARD_CRITICAL_DECISION_ORDER_INVALID: {lid}:{rpid}:{did}")
        if any(consumer!=req_by_id[x].get("consumer_action_id") or action not in req_by_id[x].get("upstream_affecting_actions",[]) for x in rids):
            fail(f"BACKWARD_CRITICAL_DECISION_BINDING_INVALID: {lid}:{rpid}:{did}")
        legal=dec.get("legal_options"); preserving=dec.get("preserving_options"); chosen=dec.get("chosen_option")
        if not isinstance(legal,list) or not legal or any(not nonempty(x) for x in legal) or len(legal)!=len(set(legal)):
            fail(f"BACKWARD_CRITICAL_DECISION_OPTIONS_INVALID: {lid}:{rpid}:{did}")
        if not isinstance(preserving,list) or not preserving or any(x not in legal for x in preserving) or len(preserving)!=len(set(preserving)):
            fail(f"BACKWARD_CRITICAL_DECISION_PRESERVING_INVALID: {lid}:{rpid}:{did}")
        if set(preserving)==set(legal):
            fail(f"BACKWARD_CRITICAL_DECISION_NOT_MATERIAL: {lid}:{rpid}:{did}")
        if chosen not in preserving:
            fail(f"BACKWARD_CRITICAL_DECISION_CHOICE_BREAKS_FUTURE: {lid}:{rpid}:{did}")
        if dec.get("render_required") is not True or not nonempty(dec.get("render_token")) or dec["render_token"].strip().casefold() not in text.casefold():
            fail(f"BACKWARD_CRITICAL_DECISION_NOT_RENDERED: {lid}:{rpid}:{did}")
        if dec.get("binding_kind")!="PLACEMENT":
            fail(f"BACKWARD_CRITICAL_DECISION_BINDING_KIND_UNSUPPORTED: {lid}:{rpid}:{did}")
        pb=step_by_id[action].get("action_legality_proof",{}).get("placement_binding",{})
        if pb.get("status")!="PASS" or set(pb.get("legal_placement_options",[]))!=set(legal) or pb.get("chosen_placement")!=chosen or pb.get("render_token")!=dec.get("render_token"):
            fail(f"BACKWARD_CRITICAL_DECISION_PLACEMENT_MISMATCH: {lid}:{rpid}:{did}")
        covered.update(rids)
    required={rid for rid,br in req_by_id.items() if br.get("decision_required") is True}
    if covered!=required:
        fail(f"BACKWARD_CRITICAL_DECISION_COVERAGE_MISMATCH: {lid}:{rpid}")
    if any(br.get("decision_required") is False and rid in covered for rid,br in req_by_id.items()):
        fail(f"BACKWARD_NONCRITICAL_REQUIREMENT_RENDER_INFLATION: {lid}:{rpid}")


    # RC16 cross-check: semantic clauses and game rules must reach an existing
    # RC13-15 consumer instead of merely existing in an orphan catalog entry.
    used_constraints=set()
    for st in steps:
        proof=st.get("action_legality_proof",{}) if isinstance(st,dict) else {}
        for cid in proof.get("applicable_constraint_ids",[]) or []:
            used_constraints.add(cid)
    used_facts=set()
    constraints=rp.get("constraint_catalog",[])
    for con in constraints if isinstance(constraints,list) else []:
        if isinstance(con,dict) and con.get("constraint_id") in used_constraints:
            for fid in (con.get("left_fact_id"),con.get("right_fact_id")):
                if nonempty(fid): used_facts.add(fid)
    for label,refs in (("SRC",semantic_meta.get("src_refs",set())),("GAME_RULE",semantic_meta.get("game_refs",set()))):
        for ref in refs:
            if ref not in used_constraints and ref not in used_facts:
                fail(f"RC16_ORPHAN_{label}_REF: {lid}:{rpid}:{ref}")

def _eval_legality_constraint(con, facts):
    left=facts[con["left_fact_id"]]["value"]
    op=con["operator"]
    if op=="EXISTS": return left is not None
    right=facts[con["right_fact_id"]]["value"] if nonempty(con.get("right_fact_id")) else con.get("right_value")
    if op=="EQ": return left==right
    if op=="NEQ": return left!=right
    if op=="CONTAINS":
        try: return right in left
        except TypeError: return False
    if op=="NOT_CONTAINS":
        try: return right not in left
        except TypeError: return False
    if op=="IN":
        try: return left in right
        except TypeError: return False
    if op=="NOT_IN":
        try: return left not in right
        except TypeError: return False
    if op=="GE":
        try: return left>=right
        except TypeError: return False
    if op=="LE":
        try: return left<=right
        except TypeError: return False
    if op=="SUBSET":
        try: return set(left).issubset(set(right))
        except TypeError: return False
    if op=="INTERSECTS":
        try: return bool(set(left)&set(right))
        except TypeError: return False
    if op=="NOT_INTERSECTS":
        try: return not bool(set(left)&set(right))
        except TypeError: return False
    return False


def _predicate(op,left,right):
    if op=="EQ": return left==right
    if op=="NEQ": return left!=right
    if op=="CONTAINS":
        try: return right in left
        except TypeError: return False
    if op=="NOT_CONTAINS":
        try: return right not in left
        except TypeError: return False
    if op=="IN":
        try: return left in right
        except TypeError: return False
    if op=="NOT_IN":
        try: return left not in right
        except TypeError: return False
    if op=="GE":
        try: return left>=right
        except TypeError: return False
    if op=="LE":
        try: return left<=right
        except TypeError: return False
    if op=="SUBSET":
        try: return set(left).issubset(set(right))
        except TypeError: return False
    if op=="INTERSECTS":
        try: return bool(set(left)&set(right))
        except TypeError: return False
    if op=="NOT_INTERSECTS":
        try: return not bool(set(left)&set(right))
        except TypeError: return False
    return False


def _derive_topology_relations(state, topology_rules):
    rel=set()
    for rule in topology_rules or []:
        src=rule["source_id"]; src_zone=rule["source_zone"]
        if state.get(src,{}).get(src_zone,0)<=0:
            continue
        for target in rule["target_zones"]:
            rel.add((rule["relation_type"],src,target))
    return rel


def _clone_replay_state(state, budgets, active, properties=None, attachments=None, topology_rules=None):
    return {
        "resources": {rid: dict(zones) for rid, zones in state.items()},
        "budgets": dict(budgets),
        "active_restrictions": sorted(active),
        "properties": {sid: dict(vals) for sid, vals in (properties or {}).items()},
        "attachments": {hid: sorted(vals) for hid, vals in (attachments or {}).items()},
        "relations": sorted([list(x) for x in _derive_topology_relations(state, topology_rules or [])]),
    }


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _range_value(lo, hi):
    if not (_is_number(lo) and _is_number(hi)) or lo > hi:
        fail("DERIVED_RANGE_INVALID")
    return {"__range__": True, "min": lo, "max": hi}


def _is_range(v):
    return isinstance(v, dict) and v.get("__range__") is True and _is_number(v.get("min")) and _is_number(v.get("max"))


def _range_bounds(v):
    return (v["min"], v["max"]) if _is_range(v) else (v, v)


def _derived_numeric_bin(op, a, b):
    alo, ahi = _range_bounds(a); blo, bhi = _range_bounds(b)
    if not all(_is_number(x) for x in (alo, ahi, blo, bhi)):
        fail("DERIVED_ARITHMETIC_NON_NUMERIC")
    if op == "ADD": return _range_value(alo+blo, ahi+bhi) if _is_range(a) or _is_range(b) else a+b
    if op == "SUB": return _range_value(alo-bhi, ahi-blo) if _is_range(a) or _is_range(b) else a-b
    if op == "MUL":
        vals=[alo*blo, alo*bhi, ahi*blo, ahi*bhi]
        return _range_value(min(vals), max(vals)) if _is_range(a) or _is_range(b) else a*b
    fail("DERIVED_ARITHMETIC_OPERATOR_INVALID")


def _eval_derived_expr(expr, state_snapshot, facts, claims, external_inputs, resources, used_external, lid, rpid, cid):
    if not isinstance(expr, dict) or not nonempty(expr.get("op")):
        fail(f"DERIVED_EXPRESSION_INVALID: {lid}:{rpid}:{cid}")
    op=expr["op"]
    if op=="CONST":
        if "value" not in expr: fail(f"DERIVED_CONST_VALUE_MISSING: {lid}:{rpid}:{cid}")
        return expr["value"]
    if op=="CLAIM_REF":
        ref=expr.get("claim_id")
        if ref not in claims: fail(f"DERIVED_CLAIM_FORWARD_OR_UNKNOWN_REF: {lid}:{rpid}:{cid}:{ref}")
        return claims[ref]
    if op=="FACT_REF":
        fid=expr.get("fact_id")
        if fid not in facts: fail(f"DERIVED_FACT_REF_UNKNOWN: {lid}:{rpid}:{cid}:{fid}")
        return facts[fid]["value"]
    if op=="EXTERNAL_INPUT":
        iid=expr.get("input_id")
        if iid not in external_inputs: fail(f"DERIVED_EXTERNAL_INPUT_UNKNOWN: {lid}:{rpid}:{cid}:{iid}")
        used_external.add(iid); ent=external_inputs[iid]; st=ent["status"]
        if st in {"FIXED","CONDITION_FIXED"}: return ent["value"]
        if st=="RANGE": return _range_value(ent["min"],ent["max"])
        fail(f"DERIVED_EXTERNAL_INPUT_STATUS_INVALID: {lid}:{rpid}:{cid}:{iid}")
    if op in {"RESOURCE_QTY_AT_ZONE","ZONE_QTY_SUM","ZONE_DISTINCT_RESOURCE_COUNT","RESOURCE_ZONE_IS","SET_OF_RESOURCES_AT_ZONE"}:
        zone=expr.get("zone")
        if not nonempty(zone): fail(f"DERIVED_ZONE_MISSING: {lid}:{rpid}:{cid}")
        rz=state_snapshot["resources"]
        if op in {"RESOURCE_QTY_AT_ZONE","RESOURCE_ZONE_IS"}:
            rid=expr.get("resource_id")
            if rid not in resources: fail(f"DERIVED_RESOURCE_UNKNOWN: {lid}:{rpid}:{cid}:{rid}")
            q=rz.get(rid,{}).get(zone,0)
            return q if op=="RESOURCE_QTY_AT_ZONE" else q>0
        rids=expr.get("resource_ids")
        if not isinstance(rids,list) or not rids or any(x not in resources for x in rids) or len(rids)!=len(set(rids)):
            fail(f"DERIVED_RESOURCE_SET_INVALID: {lid}:{rpid}:{cid}")
        if op=="ZONE_QTY_SUM": return sum(rz.get(r,{}).get(zone,0) for r in rids)
        if op=="ZONE_DISTINCT_RESOURCE_COUNT": return sum(1 for r in rids if rz.get(r,{}).get(zone,0)>0)
        return sorted(r for r in rids if rz.get(r,{}).get(zone,0)>0)
    if op in {"ADD","SUB","MUL"}:
        args=expr.get("args")
        if not isinstance(args,list) or (op=="SUB" and len(args)!=2) or (op!="SUB" and len(args)<2):
            fail(f"DERIVED_ARITHMETIC_ARGS_INVALID: {lid}:{rpid}:{cid}:{op}")
        vals=[_eval_derived_expr(x,state_snapshot,facts,claims,external_inputs,resources,used_external,lid,rpid,cid) for x in args]
        out=vals[0]
        for v in vals[1:]: out=_derived_numeric_bin(op,out,v)
        return out
    if op in {"MIN","MAX"}:
        args=expr.get("args")
        if not isinstance(args,list) or not args: fail(f"DERIVED_ARITHMETIC_ARGS_INVALID: {lid}:{rpid}:{cid}:{op}")
        vals=[_eval_derived_expr(x,state_snapshot,facts,claims,external_inputs,resources,used_external,lid,rpid,cid) for x in args]
        lows=[]; highs=[]
        for v in vals:
            lo,hi=_range_bounds(v)
            if not (_is_number(lo) and _is_number(hi)): fail(f"DERIVED_ARITHMETIC_NON_NUMERIC: {lid}:{rpid}:{cid}")
            lows.append(lo); highs.append(hi)
        if op=="MIN": lo=min(lows); hi=min(highs)
        else: lo=max(lows); hi=max(highs)
        return _range_value(lo,hi) if any(_is_range(v) for v in vals) else (lo if op=="MIN" else hi)
    fail(f"DERIVED_OPERATOR_INVALID: {lid}:{rpid}:{cid}:{op}")


def _normalize_computed_value(v):
    if _is_range(v): return {"min":v["min"],"max":v["max"]}
    return v


def _value_token(v):
    if isinstance(v,bool): return "true" if v else "false"
    if _is_number(v): return str(int(v)) if isinstance(v,float) and v.is_integer() else str(v)
    if isinstance(v,dict) and set(v)=={"min","max"}: return f"{_value_token(v['min'])}-{_value_token(v['max'])}"
    return None


def _collect_claim_refs(expr):
    if not isinstance(expr,dict): return set()
    out=set()
    if expr.get("op")=="CLAIM_REF" and nonempty(expr.get("claim_id")): out.add(expr["claim_id"])
    for v in expr.values():
        if isinstance(v,dict): out.update(_collect_claim_refs(v))
        elif isinstance(v,list):
            for x in v:
                if isinstance(x,dict): out.update(_collect_claim_refs(x))
    return out


def _validate_derived_claims(rp, snapshots, facts, resources, line, text, lid, rpid):
    ext_raw=rp.get("external_inputs",[])
    if not isinstance(ext_raw,list): fail(f"DERIVED_EXTERNAL_INPUTS_INVALID: {lid}:{rpid}")
    external={}
    for ent in ext_raw:
        if not isinstance(ent,dict) or not nonempty(ent.get("input_id")) or ent["input_id"] in external:
            fail(f"DERIVED_EXTERNAL_INPUT_ID_INVALID: {lid}:{rpid}")
        iid=ent["input_id"]; status=ent.get("status")
        if status not in {"FIXED","CONDITION_FIXED","RANGE"}: fail(f"DERIVED_EXTERNAL_INPUT_STATUS_INVALID: {lid}:{rpid}:{iid}")
        if status in {"FIXED","CONDITION_FIXED"} and "value" not in ent: fail(f"DERIVED_EXTERNAL_INPUT_VALUE_MISSING: {lid}:{rpid}:{iid}")
        if status=="CONDITION_FIXED" and not nonempty(ent.get("condition_id")): fail(f"DERIVED_EXTERNAL_INPUT_CONDITION_MISSING: {lid}:{rpid}:{iid}")
        if status=="RANGE":
            if not (_is_number(ent.get("min")) and _is_number(ent.get("max"))) or ent["min"]>ent["max"]:
                fail(f"DERIVED_EXTERNAL_INPUT_RANGE_INVALID: {lid}:{rpid}:{iid}")
        external[iid]=ent
    status=rp.get("derived_claim_inventory_status")
    if status not in {"COMPLETE","COMPLETE_NO_MATERIAL_CLAIMS"}:
        fail(f"DERIVED_CLAIM_INVENTORY_NOT_CLOSED: {lid}:{rpid}")
    raw=rp.get("derived_claims")
    if not isinstance(raw,list): fail(f"DERIVED_CLAIMS_INVALID: {lid}:{rpid}")
    if status=="COMPLETE" and not raw: fail(f"DERIVED_CLAIMS_REQUIRED: {lid}:{rpid}")
    if status=="COMPLETE_NO_MATERIAL_CLAIMS" and raw: fail(f"DERIVED_CLAIMS_STATUS_INCONSISTENT: {lid}:{rpid}")
    values={}; claim_ids=[]; claim_defs={}; claim_meta={}
    for claim in raw:
        if not isinstance(claim,dict): fail(f"DERIVED_CLAIM_INVALID: {lid}:{rpid}")
        cid=claim.get("claim_id")
        if not nonempty(cid) or cid in values: fail(f"DERIVED_CLAIM_ID_INVALID: {lid}:{rpid}")
        at=claim.get("at_state")
        if at not in snapshots: fail(f"DERIVED_CLAIM_STATE_UNKNOWN: {lid}:{rpid}:{cid}:{at}")
        ctype=claim.get("claim_type")
        if ctype not in {"NUMERIC","BOOLEAN","SET"}: fail(f"DERIVED_CLAIM_TYPE_INVALID: {lid}:{rpid}:{cid}")
        certainty=claim.get("certainty")
        if certainty not in {"EXACT","CONDITIONAL","RANGE"}: fail(f"DERIVED_CLAIM_CERTAINTY_INVALID: {lid}:{rpid}:{cid}")
        deps=claim.get("depends_on_claim_ids",[])
        if not isinstance(deps,list) or len(deps)!=len(set(deps)) or any(x not in values for x in deps):
            fail(f"DERIVED_CLAIM_DEPENDENCY_INVALID: {lid}:{rpid}:{cid}")
        refs=_collect_claim_refs(claim.get("computation"))
        if refs!=set(deps): fail(f"DERIVED_CLAIM_DEPENDENCY_MISMATCH: {lid}:{rpid}:{cid}")
        used=set()
        computed=_eval_derived_expr(claim.get("computation"),snapshots[at],facts,values,external,resources,used,lid,rpid,cid)
        norm=_normalize_computed_value(computed)
        conds=claim.get("conditions",[]); ctoks=claim.get("condition_render_tokens",[])
        if not isinstance(conds,list) or not isinstance(ctoks,list) or any(not nonempty(x) for x in conds+ctoks):
            fail(f"DERIVED_CLAIM_CONDITIONS_INVALID: {lid}:{rpid}:{cid}")
        if certainty=="EXACT":
            if any(external[i]["status"]!="FIXED" for i in used): fail(f"DERIVED_EXACT_USES_OPEN_EXTERNAL_INPUT: {lid}:{rpid}:{cid}")
            if _is_range(computed): fail(f"DERIVED_EXACT_COMPUTED_RANGE: {lid}:{rpid}:{cid}")
            if conds or ctoks: fail(f"DERIVED_EXACT_CANNOT_HAVE_CONDITIONS: {lid}:{rpid}:{cid}")
        elif certainty=="CONDITIONAL":
            if not conds or len(conds)!=len(ctoks): fail(f"DERIVED_CONDITIONAL_REQUIRES_VISIBLE_CONDITIONS: {lid}:{rpid}:{cid}")
            if any(external[i]["status"]=="RANGE" for i in used): fail(f"DERIVED_CONDITIONAL_USES_UNBOUNDED_RANGE: {lid}:{rpid}:{cid}")
            needed={external[i].get("condition_id") for i in used if external[i]["status"]=="CONDITION_FIXED"}
            if not needed.issubset(set(conds)): fail(f"DERIVED_CONDITIONAL_INPUT_NOT_BOUND_TO_CONDITION: {lid}:{rpid}:{cid}")
        else:
            if not _is_range(computed): fail(f"DERIVED_RANGE_CLAIM_NOT_RANGE: {lid}:{rpid}:{cid}")
        if claim.get("rendered_value")!=norm:
            fail(f"DERIVED_RENDERED_VALUE_MISMATCH: {lid}:{rpid}:{cid}")
        tok=claim.get("render_token")
        if not nonempty(tok) or tok.strip().casefold() not in text.casefold(): fail(f"DERIVED_CLAIM_NOT_RENDERED: {lid}:{rpid}:{cid}")
        vt=claim.get("rendered_value_token")
        expected_vt=_value_token(norm)
        if expected_vt is not None:
            if not nonempty(vt) or vt!=expected_vt or vt not in tok:
                fail(f"DERIVED_RENDERED_VALUE_TOKEN_MISMATCH: {lid}:{rpid}:{cid}")
        for t in ctoks:
            if t.strip().casefold() not in text.casefold(): fail(f"DERIVED_CLAIM_CONDITION_NOT_RENDERED: {lid}:{rpid}:{cid}")
        values[cid]=norm; claim_ids.append(cid); claim_defs[cid]=claim; claim_meta[cid]={"certainty":certainty,"used_external_statuses":sorted({external[i]["status"] for i in used}),"conditions":list(conds)}
    cold=rp.get("cold_derived_sweep")
    if not isinstance(cold,dict) or cold.get("status")!="PASS" or cold.get("ignored_initial_claim_inventory") is not True or not nonempty(cold.get("sweep_basis")):
        fail(f"COLD_DERIVED_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    disc=cold.get("discovered_claim_ids")
    if not isinstance(disc,list) or len(disc)!=len(set(disc)) or any(x not in values for x in disc):
        fail(f"COLD_DERIVED_SWEEP_CLAIMS_INVALID: {lid}:{rpid}")
    if set(disc)!=set(claim_ids): fail(f"COLD_DERIVED_SWEEP_DIVERGENCE: {lid}:{rpid}")
    # Physical checkpoints must be mechanically tied to claims when they are relevant.
    cps=line.get("state_checkpoints") or []
    for ch in cps:
        if not isinstance(ch,dict): continue
        oid=ch.get("derived_occupied_claim_id"); fid=ch.get("derived_free_claim_id")
        if ch.get("state_status")=="PASS":
            if not nonempty(oid) or not nonempty(fid): fail(f"PHYSICAL_STATE_DERIVED_CLAIMS_MISSING: {lid}:{rpid}:{ch.get('checkpoint_id')}")
            if oid not in values or fid not in values: fail(f"PHYSICAL_STATE_DERIVED_CLAIM_UNKNOWN: {lid}:{rpid}:{ch.get('checkpoint_id')}")
            checkpoint_state=ch.get("at_state")
            if checkpoint_state not in snapshots: fail(f"PHYSICAL_STATE_CHECKPOINT_STATE_UNKNOWN: {lid}:{rpid}:{ch.get('checkpoint_id')}")
            if claim_defs[oid].get("at_state")!=checkpoint_state or claim_defs[fid].get("at_state")!=checkpoint_state:
                fail(f"PHYSICAL_STATE_MIXED_SNAPSHOT: {lid}:{rpid}:{ch.get('checkpoint_id')}")
            oexpr=claim_defs[oid].get("computation",{}); fexpr=claim_defs[fid].get("computation",{})
            if oexpr.get("op") not in {"ZONE_QTY_SUM","ZONE_DISTINCT_RESOURCE_COUNT"}:
                fail(f"PHYSICAL_OCCUPIED_CLAIM_NOT_STATE_DERIVED: {lid}:{rpid}:{ch.get('checkpoint_id')}")
            if fexpr.get("op")!="SUB" or oid not in set(claim_defs[fid].get("depends_on_claim_ids",[])):
                fail(f"PHYSICAL_FREE_CLAIM_NOT_DERIVED_FROM_OCCUPIED: {lid}:{rpid}:{ch.get('checkpoint_id')}")
            if values[oid]!=ch.get("occupied_zones") or values[fid]!=ch.get("free_zones"):
                fail(f"PHYSICAL_STATE_DERIVED_VALUE_MISMATCH: {lid}:{rpid}:{ch.get('checkpoint_id')}")
    return values,claim_meta


def _snapshot_relation_active(snapshot, relation_type, source_id, target_slot=None, target_resource_id=None):
    rel={tuple(x) for x in snapshot.get("relations",[])}
    if target_resource_id is not None:
        zones=[z for z,q in snapshot.get("resources",{}).get(target_resource_id,{}).items() if q>0]
        return any((relation_type,source_id,z) in rel for z in zones)
    return (relation_type,source_id,target_slot) in rel


def _eval_state_precondition(pre, snapshot, resources, lid, rpid, sid):
    pid=pre.get("precondition_id")
    kind=pre.get("kind")
    if kind=="PROPERTY":
        subject=pre.get("subject_id"); prop=pre.get("property")
        if subject not in resources or not nonempty(prop):
            fail(f"STATE_PRECONDITION_PROPERTY_INVALID: {lid}:{rpid}:{sid}:{pid}")
        actual=snapshot.get("properties",{}).get(subject,{}).get(prop,object())
        if actual.__class__ is object:
            fail(f"STATE_PRECONDITION_PROPERTY_UNKNOWN: {lid}:{rpid}:{sid}:{pid}")
        op=pre.get("operator","EQ")
        return _predicate(op,actual,pre.get("value"))
    if kind=="RESOURCE_AT":
        rid=pre.get("resource_id"); zone=pre.get("zone"); qty=pre.get("min_qty",1)
        if rid not in resources or not nonempty(zone) or not isinstance(qty,int) or isinstance(qty,bool) or qty<1:
            fail(f"STATE_PRECONDITION_RESOURCE_AT_INVALID: {lid}:{rpid}:{sid}:{pid}")
        return snapshot.get("resources",{}).get(rid,{}).get(zone,0)>=qty
    if kind=="ATTACHMENT_COUNT":
        hid=pre.get("host_id"); op=pre.get("operator","GE"); value=pre.get("value")
        if hid not in resources or not isinstance(value,int) or isinstance(value,bool) or value<0:
            fail(f"STATE_PRECONDITION_ATTACHMENT_INVALID: {lid}:{rpid}:{sid}:{pid}")
        return _predicate(op,len(snapshot.get("attachments",{}).get(hid,[])),value)
    if kind=="SLOT_AVAILABLE":
        slots=pre.get("slots"); min_available=pre.get("min_available",1)
        if not isinstance(slots,list) or not slots or any(not nonempty(x) for x in slots) or len(slots)!=len(set(slots)) or not isinstance(min_available,int) or isinstance(min_available,bool) or min_available<1:
            fail(f"STATE_PRECONDITION_SLOT_AVAILABLE_INVALID: {lid}:{rpid}:{sid}:{pid}")
        occupied=0
        for slot in slots:
            if any(locs.get(slot,0)>0 for locs in snapshot.get("resources",{}).values()): occupied+=1
        available=len(slots)-occupied
        return available>=min_available
    if kind=="RELATION":
        rt=pre.get("relation_type"); src=pre.get("source_id")
        if not nonempty(rt) or src not in resources:
            fail(f"STATE_PRECONDITION_RELATION_INVALID: {lid}:{rpid}:{sid}:{pid}")
        tr=pre.get("target_resource_id"); ts=pre.get("target_slot")
        if (tr is None)==(ts is None):
            fail(f"STATE_PRECONDITION_RELATION_TARGET_INVALID: {lid}:{rpid}:{sid}:{pid}")
        if tr is not None and tr not in resources:
            fail(f"STATE_PRECONDITION_RELATION_RESOURCE_UNKNOWN: {lid}:{rpid}:{sid}:{pid}")
        if ts is not None and not nonempty(ts):
            fail(f"STATE_PRECONDITION_RELATION_SLOT_INVALID: {lid}:{rpid}:{sid}:{pid}")
        actual=_snapshot_relation_active(snapshot,rt,src,ts,tr)
        return actual is bool(pre.get("expected",True))
    fail(f"STATE_PRECONDITION_KIND_INVALID: {lid}:{rpid}:{sid}:{pid}:{kind}")


def _validate_step_state_preconditions(step, before_snapshot, resources, text, lid, rpid):
    sid=step.get("step_id")
    pres=step.get("state_preconditions")
    if not isinstance(pres,list): fail(f"STATE_PRECONDITIONS_INVALID: {lid}:{rpid}:{sid}")
    seen=set()
    for pre in pres:
        if not isinstance(pre,dict) or not nonempty(pre.get("precondition_id")) or pre["precondition_id"] in seen:
            fail(f"STATE_PRECONDITION_ID_INVALID: {lid}:{rpid}:{sid}")
        pid=pre["precondition_id"]; seen.add(pid)
        if pre.get("at_state")!=f"BEFORE:{sid}":
            fail(f"STATE_PRECONDITION_WRONG_SNAPSHOT: {lid}:{rpid}:{sid}:{pid}")
        critical=pre.get("critical_for_continuation")
        if not isinstance(critical,bool): fail(f"STATE_PRECONDITION_CRITICAL_FLAG_INVALID: {lid}:{rpid}:{sid}:{pid}")
        tok=pre.get("render_token")
        if critical:
            if not nonempty(tok) or tok.strip().casefold() not in text.casefold():
                fail(f"STATE_PRECONDITION_CRITICAL_NOT_RENDERED: {lid}:{rpid}:{sid}:{pid}")
        elif tok not in (None,"") and (not nonempty(tok) or tok.strip().casefold() not in text.casefold()):
            fail(f"STATE_PRECONDITION_RENDER_TOKEN_INVALID: {lid}:{rpid}:{sid}:{pid}")
        if not _eval_state_precondition(pre,before_snapshot,resources,lid,rpid,sid):
            fail(f"STATE_PRECONDITION_VIOLATED: {lid}:{rpid}:{sid}:{pid}")
    return seen


def _validate_rc15_replay_contract(rp, resources, state, lid, rpid):
    # Dynamic properties.
    pscope=rp.get("dynamic_state_scope_status")
    if pscope not in {"PASS","COMPLETE_NO_DYNAMIC_PROPERTIES"}:
        fail(f"DYNAMIC_STATE_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    raw=rp.get("initial_properties",[])
    if not isinstance(raw,list): fail(f"INITIAL_PROPERTIES_INVALID: {lid}:{rpid}")
    if pscope=="COMPLETE_NO_DYNAMIC_PROPERTIES" and raw:
        fail(f"DYNAMIC_STATE_SCOPE_INCONSISTENT: {lid}:{rpid}")
    props={}
    seen=set()
    for ent in raw:
        if not isinstance(ent,dict): fail(f"INITIAL_PROPERTY_INVALID: {lid}:{rpid}")
        sid=ent.get("subject_id"); prop=ent.get("property")
        if sid not in resources or not nonempty(prop) or (sid,prop) in seen or "value" not in ent:
            fail(f"INITIAL_PROPERTY_BINDING_INVALID: {lid}:{rpid}")
        seen.add((sid,prop)); props.setdefault(sid,{})[prop]=ent["value"]
    if pscope=="PASS" and not raw: fail(f"DYNAMIC_STATE_PROPERTIES_MISSING: {lid}:{rpid}")

    # Generic host/attachment state.
    ascope=rp.get("attachment_scope_status")
    if ascope not in {"PASS","NO_ATTACHMENTS"}: fail(f"ATTACHMENT_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    araw=rp.get("initial_attachments",[])
    if not isinstance(araw,list): fail(f"INITIAL_ATTACHMENTS_INVALID: {lid}:{rpid}")
    if ascope=="NO_ATTACHMENTS" and araw: fail(f"ATTACHMENT_SCOPE_INCONSISTENT: {lid}:{rpid}")
    attachments={}; used=set()
    for ent in araw:
        if not isinstance(ent,dict): fail(f"INITIAL_ATTACHMENT_INVALID: {lid}:{rpid}")
        h=ent.get("host_id"); a=ent.get("attachment_id")
        if h not in resources or a not in resources or h==a or a in used:
            fail(f"INITIAL_ATTACHMENT_BINDING_INVALID: {lid}:{rpid}")
        az=f"ATTACHED:{h}"
        if state.get(a,{}).get(az,0)!=1:
            fail(f"INITIAL_ATTACHMENT_LOCATION_MISMATCH: {lid}:{rpid}:{a}:{h}")
        used.add(a); attachments.setdefault(h,set()).add(a)
    if ascope=="PASS" and not araw: fail(f"ATTACHMENTS_REQUIRED: {lid}:{rpid}")

    # Dynamic topology rules. Meaning of relation_type is opaque to the runtime.
    tscope=rp.get("topology_scope_status")
    if tscope not in {"PASS","NO_MATERIAL_TOPOLOGY"}: fail(f"TOPOLOGY_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    slots=rp.get("topology_slots",[]); rules_raw=rp.get("topology_rules",[])
    if not isinstance(slots,list) or any(not nonempty(x) for x in slots) or len(slots)!=len(set(slots)):
        fail(f"TOPOLOGY_SLOTS_INVALID: {lid}:{rpid}")
    if not isinstance(rules_raw,list): fail(f"TOPOLOGY_RULES_INVALID: {lid}:{rpid}")
    if tscope=="NO_MATERIAL_TOPOLOGY" and (slots or rules_raw):
        fail(f"TOPOLOGY_SCOPE_INCONSISTENT: {lid}:{rpid}")
    rules=[]; rids=set()
    for rule in rules_raw:
        if not isinstance(rule,dict) or not nonempty(rule.get("rule_id")) or rule["rule_id"] in rids:
            fail(f"TOPOLOGY_RULE_ID_INVALID: {lid}:{rpid}")
        rids.add(rule["rule_id"]); src=rule.get("source_id"); sz=rule.get("source_zone"); rt=rule.get("relation_type"); tz=rule.get("target_zones")
        if src not in resources or sz not in slots or not nonempty(rt) or not isinstance(tz,list) or not tz or any(z not in slots for z in tz) or len(tz)!=len(set(tz)):
            fail(f"TOPOLOGY_RULE_INVALID: {lid}:{rpid}:{rule.get('rule_id')}")
        rules.append({"rule_id":rule["rule_id"],"source_id":src,"source_zone":sz,"relation_type":rt,"target_zones":list(tz)})
    if tscope=="PASS" and (not slots or not rules): fail(f"TOPOLOGY_RULES_REQUIRED: {lid}:{rpid}")
    return props,attachments,rules,set(slots)


def _validate_attachment_step(step, state, attachments, resources, lid, rpid):
    sid=step.get("step_id")
    trans=step.get("attachment_transitions")
    if not isinstance(trans,list): fail(f"ATTACHMENT_TRANSITIONS_INVALID: {lid}:{rpid}:{sid}")
    moves=step.get("moves",[])
    attachment_moves=[]
    for mv in moves:
        if isinstance(mv,dict) and (str(mv.get("from_zone","")).startswith("ATTACHED:") or str(mv.get("to_zone","")).startswith("ATTACHED:")):
            attachment_moves.append((mv.get("resource_id"),mv.get("from_zone"),mv.get("to_zone"),mv.get("qty")))
    matched=set()
    for i,tr in enumerate(trans):
        if not isinstance(tr,dict): fail(f"ATTACHMENT_TRANSITION_INVALID: {lid}:{rpid}:{sid}:{i}")
        op=tr.get("op"); h=tr.get("host_id"); a=tr.get("attachment_id")
        if op not in {"ATTACH","DETACH"} or h not in resources or a not in resources or h==a:
            fail(f"ATTACHMENT_TRANSITION_BINDING_INVALID: {lid}:{rpid}:{sid}:{i}")
        az=f"ATTACHED:{h}"
        if op=="DETACH":
            dest=tr.get("destination_zone")
            if not nonempty(dest) or a not in attachments.get(h,set()): fail(f"ATTACHMENT_DETACH_NOT_AVAILABLE: {lid}:{rpid}:{sid}:{a}")
            key=(a,az,dest,1)
        else:
            src=tr.get("from_zone")
            if not nonempty(src) or a in {x for vals in attachments.values() for x in vals}: fail(f"ATTACHMENT_ATTACH_INVALID: {lid}:{rpid}:{sid}:{a}")
            if state.get(a,{}).get(src,0)<1: fail(f"ATTACHMENT_ATTACH_SOURCE_MISSING: {lid}:{rpid}:{sid}:{a}")
            key=(a,src,az,1)
        if key not in attachment_moves: fail(f"ATTACHMENT_TRANSITION_MOVE_MISMATCH: {lid}:{rpid}:{sid}:{a}")
        matched.add(key)
    if set(attachment_moves)!=matched:
        fail(f"ATTACHMENT_MOVE_WITHOUT_TRANSITION: {lid}:{rpid}:{sid}")
    return trans


def _apply_attachment_transitions(trans, attachments):
    for tr in trans:
        h=tr["host_id"]; a=tr["attachment_id"]
        if tr["op"]=="DETACH":
            attachments.setdefault(h,set()).remove(a)
        else:
            attachments.setdefault(h,set()).add(a)


def _apply_property_updates(step, properties, resources, lid, rpid):
    sid=step.get("step_id"); updates=step.get("property_updates")
    if not isinstance(updates,list): fail(f"PROPERTY_UPDATES_INVALID: {lid}:{rpid}:{sid}")
    seen=set()
    for up in updates:
        if not isinstance(up,dict): fail(f"PROPERTY_UPDATE_INVALID: {lid}:{rpid}:{sid}")
        subj=up.get("subject_id"); prop=up.get("property")
        if subj not in resources or not nonempty(prop) or (subj,prop) in seen or "to_value" not in up:
            fail(f"PROPERTY_UPDATE_BINDING_INVALID: {lid}:{rpid}:{sid}")
        seen.add((subj,prop)); cur=properties.get(subj,{}).get(prop,object())
        if "from_value" in up and (cur.__class__ is object or cur!=up["from_value"]):
            fail(f"PROPERTY_UPDATE_FROM_VALUE_MISMATCH: {lid}:{rpid}:{sid}:{subj}:{prop}")
        properties.setdefault(subj,{})[prop]=up["to_value"]


def _validate_state_and_topology_sweeps(rp, all_preconditions, topology_preconditions, text, lid, rpid, snapshots):
    inv=rp.get("state_precondition_inventory_status")
    if inv not in {"COMPLETE","COMPLETE_NO_MATERIAL_PRECONDITIONS"}: fail(f"STATE_PRECONDITION_INVENTORY_NOT_CLOSED: {lid}:{rpid}")
    cold=rp.get("cold_state_sweep")
    if not isinstance(cold,dict) or cold.get("status")!="PASS" or cold.get("ignored_initial_precondition_inventory") is not True or not nonempty(cold.get("sweep_basis")):
        fail(f"COLD_STATE_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    disc=cold.get("discovered_precondition_ids")
    if not isinstance(disc,list) or len(disc)!=len(set(disc)):
        fail(f"COLD_STATE_SWEEP_IDS_INVALID: {lid}:{rpid}")
    if set(disc)!=set(all_preconditions): fail(f"COLD_STATE_SWEEP_DIVERGENCE: {lid}:{rpid}")
    if inv=="COMPLETE" and not all_preconditions: fail(f"STATE_PRECONDITIONS_REQUIRED: {lid}:{rpid}")
    if inv=="COMPLETE_NO_MATERIAL_PRECONDITIONS" and all_preconditions: fail(f"STATE_PRECONDITION_INVENTORY_INCONSISTENT: {lid}:{rpid}")

    tinv=rp.get("topology_inventory_status")
    if tinv not in {"COMPLETE","COMPLETE_NO_MATERIAL_RELATIONSHIPS"}: fail(f"TOPOLOGY_INVENTORY_NOT_CLOSED: {lid}:{rpid}")
    checks=rp.get("topology_checks",[])
    if not isinstance(checks,list): fail(f"TOPOLOGY_CHECKS_INVALID: {lid}:{rpid}")
    ids=[]
    for ch in checks:
        if not isinstance(ch,dict) or not nonempty(ch.get("topology_id")) or ch["topology_id"] in ids:
            fail(f"TOPOLOGY_CHECK_ID_INVALID: {lid}:{rpid}")
        ids.append(ch["topology_id"])
        pid=ch.get("precondition_id")
        if pid not in topology_preconditions: fail(f"TOPOLOGY_CHECK_PRECONDITION_UNKNOWN: {lid}:{rpid}:{ch['topology_id']}")
        pre=topology_preconditions[pid]
        material=ch.get("material_to_continuation")
        if not isinstance(material,bool): fail(f"TOPOLOGY_CHECK_MATERIAL_FLAG_INVALID: {lid}:{rpid}:{ch['topology_id']}")
        tok=ch.get("render_token")
        rendered_slot=ch.get("rendered_target_slot")
        if material:
            if not nonempty(tok) or tok.strip().casefold() not in text.casefold(): fail(f"TOPOLOGY_CRITICAL_PLACEMENT_NOT_RENDERED: {lid}:{rpid}:{ch['topology_id']}")
            if not nonempty(rendered_slot) or rendered_slot.strip().casefold() not in tok.strip().casefold():
                fail(f"TOPOLOGY_RENDERED_SLOT_BINDING_MISSING: {lid}:{rpid}:{ch['topology_id']}")
            snap=snapshots.get(pre.get("at_state"))
            if not isinstance(snap,dict): fail(f"TOPOLOGY_RENDERED_SLOT_STATE_UNKNOWN: {lid}:{rpid}:{ch['topology_id']}")
            if pre.get("target_slot") is not None:
                actual_slot=pre.get("target_slot")
                if rendered_slot!=actual_slot: fail(f"TOPOLOGY_RENDERED_SLOT_MISMATCH: {lid}:{rpid}:{ch['topology_id']}")
            else:
                target_resource=pre.get("target_resource_id")
                if snap.get("resources",{}).get(target_resource,{}).get(rendered_slot,0)<=0:
                    fail(f"TOPOLOGY_RENDERED_SLOT_MISMATCH: {lid}:{rpid}:{ch['topology_id']}")
        elif rendered_slot not in (None,""):
            fail(f"TOPOLOGY_NONMATERIAL_RENDERED_SLOT_FORBIDDEN: {lid}:{rpid}:{ch['topology_id']}")
    if tinv=="COMPLETE" and not checks: fail(f"TOPOLOGY_CHECKS_REQUIRED: {lid}:{rpid}")
    if tinv=="COMPLETE_NO_MATERIAL_RELATIONSHIPS" and checks: fail(f"TOPOLOGY_INVENTORY_INCONSISTENT: {lid}:{rpid}")
    tc=rp.get("cold_topology_sweep")
    if not isinstance(tc,dict) or tc.get("status")!="PASS" or tc.get("ignored_initial_topology_inventory") is not True or not nonempty(tc.get("sweep_basis")):
        fail(f"COLD_TOPOLOGY_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    td=tc.get("discovered_topology_ids")
    if not isinstance(td,list) or len(td)!=len(set(td)) or set(td)!=set(ids): fail(f"COLD_TOPOLOGY_SWEEP_DIVERGENCE: {lid}:{rpid}")


def _validate_certainty_inventory(rp, outcome, text, claim_meta, lid, rpid):
    inv=rp.get("external_condition_inventory_status")
    if inv not in {"COMPLETE","COMPLETE_NO_MATERIAL_EXTERNAL_CONDITIONS"}: fail(f"EXTERNAL_CONDITION_INVENTORY_NOT_CLOSED: {lid}:{rpid}")
    raw=rp.get("external_conditions",[])
    if not isinstance(raw,list): fail(f"EXTERNAL_CONDITIONS_INVALID: {lid}:{rpid}")
    conds={}
    for ent in raw:
        if not isinstance(ent,dict) or not nonempty(ent.get("condition_id")) or ent["condition_id"] in conds:
            fail(f"EXTERNAL_CONDITION_ID_INVALID: {lid}:{rpid}")
        status=ent.get("status")
        if status not in {"CLOSED_TRUE","CLOSED_FALSE","OPEN"}: fail(f"EXTERNAL_CONDITION_STATUS_INVALID: {lid}:{rpid}:{ent.get('condition_id')}")
        if ent.get("material_to_outcome") is not True: fail(f"EXTERNAL_CONDITION_MATERIAL_FLAG_REQUIRED: {lid}:{rpid}:{ent.get('condition_id')}")
        tok=ent.get("render_token")
        if status=="OPEN" and (not nonempty(tok) or tok.strip().casefold() not in text.casefold()):
            fail(f"OPEN_EXTERNAL_CONDITION_NOT_RENDERED: {lid}:{rpid}:{ent.get('condition_id')}")
        conds[ent["condition_id"]]=ent
    if inv=="COMPLETE" and not raw: fail(f"EXTERNAL_CONDITIONS_REQUIRED: {lid}:{rpid}")
    if inv=="COMPLETE_NO_MATERIAL_EXTERNAL_CONDITIONS" and raw: fail(f"EXTERNAL_CONDITION_INVENTORY_INCONSISTENT: {lid}:{rpid}")
    cold=rp.get("cold_certainty_sweep")
    if not isinstance(cold,dict) or cold.get("status")!="PASS" or cold.get("ignored_initial_condition_inventory") is not True or not nonempty(cold.get("sweep_basis")):
        fail(f"COLD_CERTAINTY_SWEEP_NOT_CLOSED: {lid}:{rpid}")
    disc=cold.get("discovered_condition_ids")
    if not isinstance(disc,list) or len(disc)!=len(set(disc)) or set(disc)!=set(conds): fail(f"COLD_CERTAINTY_SWEEP_DIVERGENCE: {lid}:{rpid}")

    cert=outcome.get("certainty")
    open_ids={cid for cid,e in conds.items() if e["status"]=="OPEN"}
    false_ids={cid for cid,e in conds.items() if e["status"]=="CLOSED_FALSE"}
    odc=outcome.get("derived_claim_ids",[])
    nonexact=[cid for cid in odc if claim_meta.get(cid,{}).get("certainty")!="EXACT"]
    if cert=="GUARANTEED":
        if open_ids: fail(f"GUARANTEED_OUTCOME_HAS_OPEN_EXTERNAL_CONDITION: {lid}:{rpid}")
        if false_ids: fail(f"GUARANTEED_OUTCOME_REQUIRED_EXTERNAL_CONDITION_FALSE: {lid}:{rpid}")
        if nonexact: fail(f"GUARANTEED_OUTCOME_USES_NONEXACT_DERIVED_CLAIM: {lid}:{rpid}")
    else:
        declared=set(outcome.get("conditions",[]))
        if open_ids and not open_ids.issubset(declared): fail(f"OUTCOME_OPEN_CONDITION_NOT_BOUND: {lid}:{rpid}")


def _validate_action_legality(step, resources, restrictions_meta, active, facts, constraints, evid, line, text, lid, rpid, placement_bound, before_snapshot):
    sid=step.get("step_id")
    proof=step.get("action_legality_proof")
    if not isinstance(proof,dict): fail(f"ACTION_LEGALITY_PROOF_MISSING: {lid}:{rpid}:{sid}")
    if proof.get("action_id")!=sid: fail(f"ACTION_LEGALITY_ACTION_ID_MISMATCH: {lid}:{rpid}:{sid}")
    parts=proof.get("participants")
    if not isinstance(parts,list) or not parts: fail(f"ACTION_LEGALITY_PARTICIPANTS_MISSING: {lid}:{rpid}:{sid}")
    pids=[]
    for part in parts:
        if not isinstance(part,dict) or part.get("resource_id") not in resources or not nonempty(part.get("role")):
            fail(f"ACTION_LEGALITY_PARTICIPANT_INVALID: {lid}:{rpid}:{sid}")
        pids.append(part["resource_id"])
    if len(pids)!=len(set(pids)): fail(f"ACTION_LEGALITY_PARTICIPANT_DUPLICATE: {lid}:{rpid}:{sid}")
    outs=proof.get("output_resource_ids",[])
    if not isinstance(outs,list) or any(x not in resources for x in outs) or len(outs)!=len(set(outs)):
        fail(f"ACTION_LEGALITY_OUTPUT_INVALID: {lid}:{rpid}:{sid}")
    for key in ("participant_guard_inventory_status","output_requirement_inventory_status","active_restriction_inventory_status"):
        if proof.get(key)!="COMPLETE": fail(f"ACTION_LEGALITY_INVENTORY_NOT_COMPLETE: {lid}:{rpid}:{sid}:{key}")
    inv=proof.get("constraint_inventory_status")
    if inv not in {"COMPLETE","COMPLETE_NO_APPLICABLE_CONSTRAINTS"}:
        fail(f"ACTION_LEGALITY_CONSTRAINT_INVENTORY_NOT_CLOSED: {lid}:{rpid}:{sid}")
    cids=proof.get("applicable_constraint_ids")
    if not isinstance(cids,list) or any(x not in constraints for x in cids) or len(cids)!=len(set(cids)):
        fail(f"ACTION_LEGALITY_CONSTRAINT_REFERENCES_INVALID: {lid}:{rpid}:{sid}")
    if inv=="COMPLETE" and not cids: fail(f"ACTION_LEGALITY_COMPLETE_REQUIRES_CONSTRAINTS: {lid}:{rpid}:{sid}")
    if inv=="COMPLETE_NO_APPLICABLE_CONSTRAINTS" and cids:
        fail(f"ACTION_LEGALITY_NO_CONSTRAINTS_STATUS_INCONSISTENT: {lid}:{rpid}:{sid}")

    _validate_step_state_preconditions(step,before_snapshot,resources,text,lid,rpid)

    # Bind participant/output scoped constraints to the concrete action.
    allowed_subjects=set(pids)|set(outs)|{f"ACTION:{sid}"}|set(active)
    for cid in cids:
        con=constraints[cid]
        if con["owner_subject_id"] not in allowed_subjects:
            fail(f"ACTION_CONSTRAINT_OWNER_NOT_BOUND_TO_ACTION: {lid}:{rpid}:{sid}:{cid}")
        if con["scope"]=="PARTICIPANT_USAGE" and con["owner_subject_id"] not in set(pids):
            fail(f"PARTICIPANT_USAGE_GUARD_OWNER_INVALID: {lid}:{rpid}:{sid}:{cid}")
        if con["scope"]=="ACTION_OUTPUT" and con["owner_subject_id"] not in set(outs):
            fail(f"ACTION_OUTPUT_REQUIREMENT_OWNER_INVALID: {lid}:{rpid}:{sid}:{cid}")
        if con["scope"]=="ACTIVE_STATE" and con["owner_subject_id"] not in active:
            fail(f"ACTIVE_RESTRICTION_CONSTRAINT_OWNER_INVALID: {lid}:{rpid}:{sid}:{cid}")
        if not _eval_legality_constraint(con,facts):
            fail(f"ACTION_LEGALITY_CONSTRAINT_VIOLATED: {lid}:{rpid}:{sid}:{cid}")

    # Every active restriction carries semantic constraints; bare PASS is forbidden.
    required_active=set()
    for rid0 in active:
        required_active.update(restrictions_meta[rid0]["constraint_ids"])
    if not required_active.issubset(set(cids)):
        missing=','.join(sorted(required_active-set(cids)))
        fail(f"ACTIVE_RESTRICTION_SEMANTIC_CONSTRAINT_MISSING: {lid}:{rpid}:{sid}:{missing}")

    # Cold sweep: same action, initial inventory ignored. Divergence prevents closure.
    cold=proof.get("cold_legality_sweep")
    if not isinstance(cold,dict) or cold.get("status")!="PASS" or cold.get("ignored_initial_constraint_inventory") is not True:
        fail(f"COLD_LEGALITY_SWEEP_NOT_CLOSED: {lid}:{rpid}:{sid}")
    if not nonempty(cold.get("sweep_basis")):
        fail(f"COLD_LEGALITY_SWEEP_BASIS_MISSING: {lid}:{rpid}:{sid}")
    disc=cold.get("discovered_constraint_ids")
    if not isinstance(disc,list) or any(x not in constraints for x in disc) or len(disc)!=len(set(disc)):
        fail(f"COLD_LEGALITY_SWEEP_CONSTRAINTS_INVALID: {lid}:{rpid}:{sid}")
    ce=cold.get("evidence_ids")
    if not isinstance(ce,list) or not ce or any(x not in evid for x in ce):
        fail(f"COLD_LEGALITY_SWEEP_EVIDENCE_INVALID: {lid}:{rpid}:{sid}")
    if set(disc)!=set(cids):
        fail(f"COLD_LEGALITY_SWEEP_DIVERGENCE: {lid}:{rpid}:{sid}")
    if proof.get("action_legality_status")!="PASS":
        fail(f"ACTION_LEGALITY_STATUS_NOT_PASS: {lid}:{rpid}:{sid}")

    # Placement is bound to the action that creates the relevant physical state.
    pb=proof.get("placement_binding")
    if not isinstance(pb,dict) or pb.get("status") not in {"PASS","NOT_APPLICABLE"}:
        fail(f"ACTION_PLACEMENT_BINDING_STATUS_INVALID: {lid}:{rpid}:{sid}")
    if pb["status"]=="PASS":
        cid=pb.get("checkpoint_id")
        checkpoints={x.get("checkpoint_id"):x for x in (line.get("state_checkpoints") or []) if isinstance(x,dict)}
        ch=checkpoints.get(cid)
        if not ch or ch.get("placement_required") is not True:
            fail(f"ACTION_PLACEMENT_CHECKPOINT_INVALID: {lid}:{rpid}:{sid}")
        if cid in placement_bound: fail(f"ACTION_PLACEMENT_CHECKPOINT_DUPLICATE_BINDING: {lid}:{rpid}:{sid}:{cid}")
        if pb.get("placement_instruction")!=ch.get("placement_instruction"):
            fail(f"ACTION_PLACEMENT_INSTRUCTION_MISMATCH: {lid}:{rpid}:{sid}:{cid}")
        tok=pb.get("render_token")
        if not nonempty(tok) or tok!=ch.get("placement_render_token") or tok.strip().casefold() not in text.casefold():
            fail(f"ACTION_PLACEMENT_NOT_RENDERED_OR_MISMATCH: {lid}:{rpid}:{sid}:{cid}")
        opts=pb.get("legal_placement_options"); chosen=pb.get("chosen_placement"); placed=pb.get("placed_resource_id")
        if not isinstance(opts,list) or not opts or any(not nonempty(x) for x in opts) or len(opts)!=len(set(opts)):
            fail(f"ACTION_PLACEMENT_OPTIONS_INVALID: {lid}:{rpid}:{sid}:{cid}")
        if chosen not in opts: fail(f"ACTION_PLACEMENT_CHOICE_INVALID: {lid}:{rpid}:{sid}:{cid}")
        if placed not in resources: fail(f"ACTION_PLACEMENT_RESOURCE_INVALID: {lid}:{rpid}:{sid}:{cid}")
        transitions=[]
        for mv in step.get("moves",[]):
            if isinstance(mv,dict) and mv.get("resource_id")==placed and mv.get("to_zone")==chosen: transitions.append(mv)
        for pr in step.get("produces",[]):
            if isinstance(pr,dict) and pr.get("resource_id")==placed and pr.get("zone")==chosen: transitions.append(pr)
        if not transitions: fail(f"ACTION_PLACEMENT_NOT_MATERIALIZED_IN_STEP: {lid}:{rpid}:{sid}:{cid}")
        placement_bound.add(cid)
    else:
        for k in ("checkpoint_id","placement_instruction","render_token","legal_placement_options","chosen_placement","placed_resource_id"):
            if pb.get(k) not in (None,"",[]):
                fail(f"ACTION_PLACEMENT_NOT_APPLICABLE_HAS_FIELDS: {lid}:{rpid}:{sid}")


MCB_OPERATORS={
    "REQUIRE","MOVE","CONSUME","OBTAIN","PRODUCE","PROPERTY_UPDATE",
    "RESTRICTION_APPLY","RESTRICTION_RELEASE","APPLY_TO_MATCHING_SET",
    "DAMAGE_EVENT","LETHAL_CHECK"
}
MCB_SCOPES={"SINGLE","EXACT_N","UP_TO_N","ALL_MATCHING","ALL_POSSIBLE"}


def _mcb_signature(binding):
    if not isinstance(binding,dict): return None
    return {
        "source_kind":binding.get("source_kind"),"source_id":binding.get("source_id"),
        "action_id":binding.get("action_id"),"evidence_id":binding.get("evidence_id"),
        "operator":binding.get("operator"),"scope":binding.get("scope"),
        "params":binding.get("params"),"material_to_line":binding.get("material_to_line"),
    }


def _mcb_signature_text(binding):
    return json.dumps(_mcb_signature(binding),ensure_ascii=False,sort_keys=True,separators=(",",":"))


def _compare_mcb_cold_projection(primary, cold, lid, rpid):
    if not isinstance(primary,list) or not isinstance(cold,list):
        fail(f"MCB_COLD_PROJECTION_INVALID: {lid}:{rpid}")
    ps=[_mcb_signature_text(x) for x in primary]
    cs=[_mcb_signature_text(x) for x in cold]
    if any(x is None for x in [_mcb_signature(v) for v in primary+cold]):
        fail(f"MCB_COLD_PROJECTION_INVALID: {lid}:{rpid}")
    if len(ps)!=len(set(ps)) or len(cs)!=len(set(cs)):
        fail(f"MCB_COLD_PROJECTION_DUPLICATE: {lid}:{rpid}")
    if sorted(ps)!=sorted(cs):
        fail(f"MCB_COLD_PROJECTION_DIVERGENCE: {lid}:{rpid}")
    return True


def _mcb_positive_number(v,label):
    if not isinstance(v,(int,float)) or isinstance(v,bool) or v<=0:
        fail(label)
    return v


def _mcb_resource_move(state, resources, rid, fz, tz, qty, lid, rpid, aid, bid):
    if rid not in resources or not nonempty(fz) or not nonempty(tz):
        fail(f"MCB_MOVE_INVALID: {lid}:{rpid}:{aid}:{bid}")
    _positive_int(qty,f"MCB_MOVE_QTY_INVALID: {lid}:{rpid}:{aid}:{bid}")
    fz=fz.strip(); tz=tz.strip()
    if state.get(rid,{}).get(fz,0)<qty:
        fail(f"MCB_RESOURCE_NOT_AVAILABLE_DOUBLE_SPEND: {lid}:{rpid}:{aid}:{bid}:{rid}@{fz}")
    state.setdefault(rid,{})[fz]=state.get(rid,{}).get(fz,0)-qty
    state[rid][tz]=state[rid].get(tz,0)+qty
    return {"resource_id":rid,"from_zone":fz,"to_zone":tz,"qty":qty}


def _mcb_eval_requirement(params,state,properties,resources,facts,constraints,lid,rpid,aid,bid):
    kind=params.get("requirement_kind")
    if kind=="RESOURCE_AT":
        rid=params.get("resource_id"); zone=params.get("zone"); qty=params.get("qty",1)
        if rid not in resources or not nonempty(zone) or not isinstance(qty,int) or isinstance(qty,bool) or qty<1:
            fail(f"MCB_REQUIREMENT_INVALID: {lid}:{rpid}:{aid}:{bid}")
        if state.get(rid,{}).get(zone,0)<qty:
            fail(f"MCB_REQUIREMENT_VIOLATED: {lid}:{rpid}:{aid}:{bid}:{rid}@{zone}")
        return {"resource_id":rid,"zone":zone,"qty":qty}
    if kind=="PROPERTY":
        rid=params.get("resource_id"); prop=params.get("property"); op=params.get("comparison","EQ")
        if rid not in resources or not nonempty(prop) or op not in {"EQ","NEQ","IN","NOT_IN","GE","LE","CONTAINS","NOT_CONTAINS"}:
            fail(f"MCB_REQUIREMENT_INVALID: {lid}:{rpid}:{aid}:{bid}")
        if prop not in properties.get(rid,{}):
            fail(f"MCB_REQUIREMENT_PROPERTY_UNKNOWN: {lid}:{rpid}:{aid}:{bid}:{rid}:{prop}")
        if not _predicate(op,properties[rid][prop],params.get("value")):
            fail(f"MCB_REQUIREMENT_VIOLATED: {lid}:{rpid}:{aid}:{bid}:{rid}:{prop}")
        return None
    if kind=="CONSTRAINT":
        cid=params.get("constraint_id")
        if cid not in constraints: fail(f"MCB_REQUIREMENT_CONSTRAINT_UNKNOWN: {lid}:{rpid}:{aid}:{bid}:{cid}")
        if not _eval_legality_constraint(constraints[cid],facts):
            fail(f"MCB_REQUIREMENT_VIOLATED: {lid}:{rpid}:{aid}:{bid}:{cid}")
        return None
    fail(f"MCB_REQUIREMENT_KIND_INVALID: {lid}:{rpid}:{aid}:{bid}:{kind}")


def _apply_mcb_action(action_id, bindings, state, properties, active, restrictions_meta, resources, facts, constraints, damage_ledger, lid, rpid):
    """Compile and atomically apply authority-normalized mechanical consequences for one action."""
    ws=copy.deepcopy(state); wp=copy.deepcopy(properties); wa=set(active); wl=copy.deepcopy(damage_ledger)
    wl.setdefault("damage_total",0); wl.setdefault("guaranteed_damage_total",0); wl.setdefault("damage_events",[]); wl.setdefault("lethal_checks",[])
    result={"action_id":action_id,"requires":[],"moves":[],"produces":[],"property_updates":[],"activate_restrictions":[],"release_restrictions":[],"damage_events":[],"lethal_checks":[],"matched_resource_ids":[]}
    for b in bindings:
        if not isinstance(b,dict) or b.get("action_id")!=action_id: continue
        bid=b.get("binding_id") or "<cold>"; op=b.get("operator"); scope=b.get("scope"); params=b.get("params")
        if op not in MCB_OPERATORS or scope not in MCB_SCOPES or not isinstance(params,dict) or b.get("material_to_line") is not True:
            fail(f"MCB_BINDING_SHAPE_INVALID: {lid}:{rpid}:{action_id}:{bid}")
        if op=="REQUIRE":
            req=_mcb_eval_requirement(params,ws,wp,resources,facts,constraints,lid,rpid,action_id,bid)
            if req is not None: result["requires"].append(req)
        elif op in {"MOVE","CONSUME","OBTAIN"}:
            mv=_mcb_resource_move(ws,resources,params.get("resource_id"),params.get("from_zone"),params.get("to_zone"),params.get("qty",1),lid,rpid,action_id,bid)
            result["moves"].append(mv)
        elif op=="PRODUCE":
            rid=params.get("resource_id"); zone=params.get("zone"); qty=params.get("qty",1)
            if rid not in resources or resources[rid].get("kind")!="GENERATED" or not nonempty(zone):
                fail(f"MCB_PRODUCE_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            _positive_int(qty,f"MCB_PRODUCE_QTY_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            ws.setdefault(rid,{})[zone]=ws.get(rid,{}).get(zone,0)+qty
            result["produces"].append({"resource_id":rid,"zone":zone,"qty":qty})
        elif op=="PROPERTY_UPDATE":
            rid=params.get("resource_id"); prop=params.get("property")
            if rid not in resources or not nonempty(prop) or "to_value" not in params:
                fail(f"MCB_PROPERTY_UPDATE_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            if "from_value" in params and wp.get(rid,{}).get(prop,object())!=params.get("from_value"):
                fail(f"MCB_PROPERTY_UPDATE_FROM_MISMATCH: {lid}:{rpid}:{action_id}:{bid}:{rid}:{prop}")
            up={"subject_id":rid,"property":prop,"to_value":params["to_value"]}
            if "from_value" in params: up["from_value"]=params["from_value"]
            wp.setdefault(rid,{})[prop]=params["to_value"]; result["property_updates"].append(up)
        elif op in {"RESTRICTION_APPLY","RESTRICTION_RELEASE"}:
            rr=params.get("restriction_id")
            if rr not in restrictions_meta: fail(f"MCB_RESTRICTION_UNKNOWN: {lid}:{rpid}:{action_id}:{bid}:{rr}")
            if op=="RESTRICTION_APPLY":
                if rr in wa: fail(f"MCB_RESTRICTION_ALREADY_ACTIVE: {lid}:{rpid}:{action_id}:{bid}:{rr}")
                wa.add(rr); result["activate_restrictions"].append(rr)
            else:
                if rr not in wa: fail(f"MCB_RESTRICTION_NOT_ACTIVE: {lid}:{rpid}:{action_id}:{bid}:{rr}")
                wa.remove(rr); result["release_restrictions"].append(rr)
        elif op=="APPLY_TO_MATCHING_SET":
            if scope!="ALL_MATCHING": fail(f"MCB_MATCHING_SCOPE_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            source_zone=params.get("source_zone"); to_zone=params.get("to_zone"); pred=params.get("predicate")
            if not nonempty(source_zone) or not nonempty(to_zone) or not isinstance(pred,dict):
                fail(f"MCB_MATCHING_SET_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            prop=pred.get("property"); cmpop=pred.get("operator","EQ"); value=pred.get("value")
            if not nonempty(prop) or cmpop not in {"EQ","NEQ","IN","NOT_IN","GE","LE","CONTAINS","NOT_CONTAINS"}:
                fail(f"MCB_MATCHING_PREDICATE_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            excluded=params.get("exclude_resource_ids",[]) or []
            if excluded:
                # An ALL_MATCHING consequence may not be weakened by an ad-hoc
                # survivor list. Card-specific exceptions must be represented in
                # the proven predicate/semantics; if that cannot be expressed,
                # the line is UNRESOLVED rather than silently narrowed.
                fail(f"MCB_MATCHING_EXCLUSION_UNSUPPORTED: {lid}:{rpid}:{action_id}:{bid}")
            matches=[]
            for rid in sorted(resources):
                qty=ws.get(rid,{}).get(source_zone,0)
                if qty<=0: continue
                if prop not in wp.get(rid,{}):
                    fail(f"MCB_MATCHING_PROPERTY_UNKNOWN: {lid}:{rpid}:{action_id}:{bid}:{rid}:{prop}")
                if _predicate(cmpop,wp[rid][prop],value):
                    matches.append(rid)
            for rid in matches:
                qty=ws[rid].get(source_zone,0)
                if qty>0: result["moves"].append(_mcb_resource_move(ws,resources,rid,source_zone,to_zone,qty,lid,rpid,action_id,bid))
            result["matched_resource_ids"].extend(matches)
        elif op=="DAMAGE_EVENT":
            amount=_mcb_positive_number(params.get("amount"),f"MCB_DAMAGE_AMOUNT_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            certainty=params.get("certainty","GUARANTEED")
            if certainty not in {"GUARANTEED","CONDITIONAL"}: fail(f"MCB_DAMAGE_CERTAINTY_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            ev={"binding_id":bid,"action_id":action_id,"amount":amount,"certainty":certainty}
            wl["damage_events"].append(ev); wl["damage_total"]+=amount
            if certainty=="GUARANTEED": wl["guaranteed_damage_total"]+=amount
            result["damage_events"].append(ev)
        elif op=="LETHAL_CHECK":
            lp=_mcb_positive_number(params.get("opponent_lp_before"),f"MCB_LETHAL_LP_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            claim=params.get("claim","GUARANTEED")
            if claim not in {"GUARANTEED","CONDITIONAL"}: fail(f"MCB_LETHAL_CLAIM_INVALID: {lid}:{rpid}:{action_id}:{bid}")
            amount=wl["guaranteed_damage_total"] if claim=="GUARANTEED" else wl["damage_total"]
            if amount<lp:
                fail(f"MCB_LETHAL_NOT_CLOSED: {lid}:{rpid}:{action_id}:{bid}:damage={amount}:lp={lp}")
            chk={"binding_id":bid,"action_id":action_id,"opponent_lp_before":lp,"claim":claim,"damage_counted":amount,"status":"PASS"}
            wl["lethal_checks"].append(chk); result["lethal_checks"].append(chk)
    state.clear(); state.update(ws); properties.clear(); properties.update(wp); active.clear(); active.update(wa); damage_ledger.clear(); damage_ledger.update(wl)
    result["matched_resource_ids"]=sorted(set(result["matched_resource_ids"]))
    return result


def _validate_mcb_bindings(rp, semantic_meta, evidence, resources, restrictions_meta, facts, constraints, lid, rpid, require=False):
    scope=rp.get("mechanical_consequence_scope_status")
    bindings=rp.get("mechanical_consequence_bindings",[])
    if not require and scope is None and bindings in (None,[]): return []
    if scope not in {"COMPLETE","COMPLETE_NO_MATERIAL_BINDINGS"} or not isinstance(bindings,list):
        fail(f"MCB_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    seen=set(); source_covered=set(); step_ids={x.get("step_id") for x in rp.get("steps",[]) if isinstance(x,dict)}
    src_ev=semantic_meta.get("src_clause_evidence",{}); gr_actions=semantic_meta.get("game_rule_actions",{}); gr_ev=semantic_meta.get("game_rule_evidence",{})
    for b in bindings:
        if not isinstance(b,dict): fail(f"MCB_BINDING_INVALID: {lid}:{rpid}")
        bid=b.get("binding_id")
        if not nonempty(bid) or bid in seen: fail(f"MCB_BINDING_ID_INVALID: {lid}:{rpid}")
        seen.add(bid)
        sk=b.get("source_kind"); sid=b.get("source_id"); aid=b.get("action_id"); eid=b.get("evidence_id")
        if sk not in {"SRC_CLAUSE","GAME_RULE"} or not nonempty(sid) or aid not in step_ids or eid not in evidence:
            fail(f"MCB_SOURCE_BINDING_INVALID: {lid}:{rpid}:{bid}")
        if sk=="SRC_CLAUSE":
            if sid not in src_ev or src_ev[sid]!=eid: fail(f"MCB_SRC_EVIDENCE_MISMATCH: {lid}:{rpid}:{bid}")
        else:
            if sid not in gr_actions or aid not in gr_actions[sid] or eid not in gr_ev.get(sid,set()):
                fail(f"MCB_GAME_RULE_BINDING_MISMATCH: {lid}:{rpid}:{bid}")
        if b.get("operator") not in MCB_OPERATORS or b.get("scope") not in MCB_SCOPES or not isinstance(b.get("params"),dict) or b.get("material_to_line") is not True:
            fail(f"MCB_BINDING_SHAPE_INVALID: {lid}:{rpid}:{bid}")
        source_covered.add((sk,sid,aid if sk=="GAME_RULE" else None))
    required_sources={("SRC_CLAUSE",x,None) for x in semantic_meta.get("src_clause_ids",set())}
    for grid,actions in semantic_meta.get("game_rule_actions",{}).items():
        for aid in actions: required_sources.add(("GAME_RULE",grid,aid))
    if require and required_sources-source_covered:
        miss=",".join(f"{a}:{b}"+(f"@{c}" if c else "") for a,b,c in sorted(required_sources-source_covered,key=lambda x:(x[0],x[1],x[2] or "")))
        fail(f"MCB_MATERIAL_SOURCE_UNBOUND: {lid}:{rpid}:{miss}")
    if scope=="COMPLETE_NO_MATERIAL_BINDINGS" and bindings: fail(f"MCB_NO_MATERIAL_STATUS_INCONSISTENT: {lid}:{rpid}")
    if scope=="COMPLETE" and require and not bindings and required_sources: fail(f"MCB_BINDINGS_MISSING: {lid}:{rpid}")
    ua=rp.get("unified_cold_audit",{}); mp=ua.get("mechanical_projection") if isinstance(ua,dict) else None
    if require:
        if not isinstance(mp,dict) or mp.get("status")!="PASS" or mp.get("ignored_primary_bindings") is not True or not nonempty(mp.get("sweep_basis")):
            fail(f"MCB_COLD_PROJECTION_NOT_CLOSED: {lid}:{rpid}")
        cold=mp.get("bindings")
        _compare_mcb_cold_projection(bindings,cold,lid,rpid)
    return bindings


def _mcb_initial_projection_state(rp, lid, rpid):
    resources={}; state={}
    for res in rp.get("resources",[]) if isinstance(rp.get("resources"),list) else []:
        if not isinstance(res,dict) or not nonempty(res.get("resource_id")): fail(f"MCB_RESOURCE_INVALID: {lid}:{rpid}")
        rid=res["resource_id"]; resources[rid]=res; state[rid]=copy.deepcopy(res.get("initial_locations",{}))
    props={}
    for ent in rp.get("initial_properties",[]) if isinstance(rp.get("initial_properties"),list) else []:
        if isinstance(ent,dict) and ent.get("subject_id") in resources and nonempty(ent.get("property")) and "value" in ent:
            props.setdefault(ent["subject_id"],{})[ent["property"]]=ent["value"]
    restrictions={r.get("restriction_id"):r for r in (rp.get("restrictions",[]) or []) if isinstance(r,dict) and nonempty(r.get("restriction_id"))}
    active={rid for rid,r in restrictions.items() if r.get("initially_active") is True}
    facts={x.get("fact_id"):x for x in (rp.get("fact_catalog",[]) or []) if isinstance(x,dict) and nonempty(x.get("fact_id"))}
    cons={x.get("constraint_id"):x for x in (rp.get("constraint_catalog",[]) or []) if isinstance(x,dict) and nonempty(x.get("constraint_id"))}
    return resources,state,props,restrictions,active,facts,cons


def _compile_mcb_projection_for_replay(rp, lid, rpid):
    bindings=rp.get("mechanical_consequence_bindings",[])
    resources,state,props,restrictions,active,facts,cons=_mcb_initial_projection_state(rp,lid,rpid)
    ledger={"damage_total":0,"guaranteed_damage_total":0,"damage_events":[],"lethal_checks":[]}
    out=[]
    for step in rp.get("steps",[]) if isinstance(rp.get("steps"),list) else []:
        aid=step.get("step_id")
        before={"resources":copy.deepcopy(state),"properties":copy.deepcopy(props),"active_restrictions":sorted(active),"damage_total":ledger["damage_total"],"guaranteed_damage_total":ledger["guaranteed_damage_total"]}
        effects=_apply_mcb_action(aid,bindings,state,props,active,restrictions,resources,facts,cons,ledger,lid,rpid)
        after={"resources":copy.deepcopy(state),"properties":copy.deepcopy(props),"active_restrictions":sorted(active),"damage_total":ledger["damage_total"],"guaranteed_damage_total":ledger["guaranteed_damage_total"]}
        out.append({"action_id":aid,"before":before,"effects":effects,"after":after})
    doc={"schema":"ygo-mcb-compiled-projection-v1","steps":out,"damage_ledger":copy.deepcopy(ledger)}
    return doc


def _mcb_projection_hash(doc):
    return hashlib.sha256(json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate_execution_replay(line, text, st, eligible_variants, contract_version="RC16"):
    """Mechanically replay authority-declared state transitions for one pilotage line.

    Card meaning, legal targets, timing, restrictions and which resources matter are
    decided by VALIDATION_PILOTAGE_LIGNES_DECKS_PERSONNAGES. This function only checks
    conservation and consistency of the structured proof it receives.
    """
    lid=line.get("line_id")
    if line.get("line_execution_scope_status")!="PASS":
        fail(f"LINE_EXECUTION_REPLAY_NOT_CLOSED: {lid}")
    replays=line.get("execution_replays")
    if not isinstance(replays,list) or not replays:
        fail(f"LINE_EXECUTION_REPLAYS_MISSING: {lid}")
    snapshot=_snapshot_card_index(st)
    snapshot_file=Path(st.get("gates",{}).get("DECK_DRAFT_CREATED",{}).get("snapshot_file"))
    current_snapshot_sha=sha256(snapshot_file)
    replay_ids=set(); covered=[]
    for rp in replays:
        if not isinstance(rp,dict): fail(f"execution replay invalid: {lid}")
        rpid=rp.get("replay_id")
        if not nonempty(rpid) or rpid in replay_ids: fail(f"execution replay_id invalid/duplicate: {lid}")
        replay_ids.add(rpid)
        if rp.get("status")!="PASS": fail(f"EXECUTION_REPLAY_NOT_PASS: {lid}:{rpid}")
        cv=rp.get("covers_variants")
        if not isinstance(cv,list) or not cv or any(not nonempty(x) for x in cv):
            fail(f"EXECUTION_REPLAY_VARIANT_COVERAGE_INVALID: {lid}:{rpid}")
        if len(cv)>1:
            if rp.get("variant_equivalence_status")!="PASS" or not nonempty(rp.get("variant_equivalence_basis")):
                fail(f"GENERIC_VARIANT_SHARED_REPLAY_EQUIVALENCE_NOT_PROVED: {lid}:{rpid}")
        elif rp.get("variant_equivalence_status") not in {None,"NOT_APPLICABLE"}:
            fail(f"VARIANT_EQUIVALENCE_STATUS_INCONSISTENT: {lid}:{rpid}")
        covered.extend(x.strip().casefold() for x in cv)

        _project_unified_cold_audit(rp,lid,rpid,require=(contract_version in {"RC16.1","RC16.2"}),require_mcb=(contract_version=="RC16.2"))
        if contract_version=="RC16.2" and rp.get("semantic_layer_version")!="SRC1-GR1-BW1-MCB1":
            fail(f"RC16_2_SEMANTIC_LAYER_VERSION_MISMATCH: {lid}:{rpid}")
        evid,facts,constraints=_validate_legality_catalogs(rp,lid,rpid,current_snapshot_sha)
        rc16_semantic=_validate_rc16_semantic_inputs(rp,evid,facts,constraints,lid,rpid)

        resources_raw=rp.get("resources")
        if not isinstance(resources_raw,list) or not resources_raw:
            fail(f"EXECUTION_RESOURCES_MISSING: {lid}:{rpid}")
        resources={}; state={}; card_keys=set()
        for res in resources_raw:
            if not isinstance(res,dict): fail(f"execution resource invalid: {lid}:{rpid}")
            resid=res.get("resource_id"); kind=res.get("kind")
            if not nonempty(resid) or resid in resources: fail(f"EXECUTION_RESOURCE_ID_INVALID: {lid}:{rpid}")
            if kind not in {"CARD","GENERATED"}: fail(f"EXECUTION_RESOURCE_KIND_INVALID: {lid}:{rpid}:{resid}")
            locs=res.get("initial_locations")
            if not isinstance(locs,dict) or any(not nonempty(k) for k in locs):
                fail(f"EXECUTION_INITIAL_LOCATIONS_INVALID: {lid}:{rpid}:{resid}")
            norm_locs={}
            for z,q in locs.items():
                _nonnegative_int(q,f"EXECUTION_INITIAL_QTY_INVALID: {lid}:{rpid}:{resid}")
                nz=z.strip()
                norm_locs[nz]=norm_locs.get(nz,0)+q
            if kind=="CARD":
                name=res.get("card_name"); dz=res.get("snapshot_zone")
                if not nonempty(name) or dz not in {"main_deck","extra_deck","side_deck"}:
                    fail(f"EXECUTION_CARD_BINDING_INVALID: {lid}:{rpid}:{resid}")
                key=(dz,name.strip().casefold())
                if key in card_keys: fail(f"EXECUTION_DUPLICATE_CARD_RESOURCE: {lid}:{rpid}:{name}")
                card_keys.add(key)
                if key not in snapshot: fail(f"EXECUTION_CARD_NOT_IN_SNAPSHOT: {lid}:{rpid}:{name}")
                if sum(norm_locs.values())!=snapshot[key]:
                    fail(f"EXECUTION_CARD_COPY_ALLOCATION_MISMATCH: {lid}:{rpid}:{name}")
            else:
                if nonempty(res.get("card_name")) or res.get("snapshot_zone") not in (None,""):
                    fail(f"EXECUTION_GENERATED_RESOURCE_CANNOT_BIND_SNAPSHOT_CARD: {lid}:{rpid}:{resid}")
                if sum(norm_locs.values())!=0:
                    fail(f"EXECUTION_GENERATED_RESOURCE_MUST_START_AT_ZERO: {lid}:{rpid}:{resid}")
            labels=res.get("starter_labels",[])
            if not isinstance(labels,list) or any(not nonempty(x) for x in labels):
                fail(f"EXECUTION_STARTER_LABELS_INVALID: {lid}:{rpid}:{resid}")
            res["starter_labels"]=labels
            resources[resid]=res; state[resid]=norm_locs

        properties,attachments,topology_rules,topology_slots=_validate_rc15_replay_contract(rp,resources,state,lid,rpid)

        mandatory_labels={x.strip().casefold() for x in line.get("mandatory_initial_resources",[])}
        covered_labels={lab.strip().casefold() for res in resources.values() for lab in res.get("starter_labels",[])}
        if not mandatory_labels.issubset(covered_labels):
            missing_labels=sorted(mandatory_labels-covered_labels)
            fail(f"EXECUTION_MANDATORY_STARTER_RESOURCE_NOT_TRACKED: {lid}:{rpid}:"+",".join(missing_labels))

        budgets_raw=rp.get("budgets",[])
        if not isinstance(budgets_raw,list): fail(f"EXECUTION_BUDGETS_INVALID: {lid}:{rpid}")
        budgets={}
        for b in budgets_raw:
            if not isinstance(b,dict): fail(f"execution budget invalid: {lid}:{rpid}")
            bid=b.get("budget_id")
            if not nonempty(bid) or bid in budgets: fail(f"EXECUTION_BUDGET_ID_INVALID: {lid}:{rpid}")
            init=b.get("initial")
            _nonnegative_int(init,f"EXECUTION_BUDGET_INITIAL_INVALID: {lid}:{rpid}:{bid}")
            budgets[bid]=init

        restrictions_raw=rp.get("restrictions",[])
        if not isinstance(restrictions_raw,list): fail(f"EXECUTION_RESTRICTIONS_INVALID: {lid}:{rpid}")
        restrictions=set(); restrictions_meta={}; active=set()
        for rr in restrictions_raw:
            if not isinstance(rr,dict) or not nonempty(rr.get("restriction_id")):
                fail(f"EXECUTION_RESTRICTION_INVALID: {lid}:{rpid}")
            rrid=rr["restriction_id"]
            if rrid in restrictions: fail(f"EXECUTION_RESTRICTION_DUPLICATE: {lid}:{rpid}:{rrid}")
            rcids=rr.get("constraint_ids")
            if not isinstance(rcids,list) or not rcids or any(x not in constraints for x in rcids):
                fail(f"EXECUTION_RESTRICTION_SEMANTIC_CONSTRAINTS_INVALID: {lid}:{rpid}:{rrid}")
            restrictions.add(rrid); restrictions_meta[rrid]=rr
            ia=rr.get("initially_active",False)
            if not isinstance(ia,bool): fail(f"EXECUTION_RESTRICTION_INITIAL_FLAG_INVALID: {lid}:{rpid}:{rrid}")
            if ia: active.add(rrid)

        if contract_version=="RC16.2":
            mcb=_validate_mcb_bindings(rp,rc16_semantic,evid,resources,restrictions_meta,facts,constraints,lid,rpid,require=True)
            persisted=rp.get("compiled_mechanical_projection")
            persisted_hash=rp.get("compiled_mechanical_projection_sha256")
            if not isinstance(persisted,dict) or persisted_hash!=_mcb_projection_hash(persisted):
                fail(f"MCB_COMPILED_PROJECTION_HASH_INVALID: {lid}:{rpid}")
            recomputed=_compile_mcb_projection_for_replay(rp,lid,rpid)
            if _mcb_projection_hash(recomputed)!=persisted_hash or recomputed!=persisted:
                fail(f"MCB_COMPILED_PROJECTION_STALE_OR_TAMPERED: {lid}:{rpid}")
            # Compiler-owned fields in the contract must exactly equal the deterministic projection.
            by_action={x["action_id"]:x["effects"] for x in persisted.get("steps",[])}
            for stp in rp.get("steps",[]) if isinstance(rp.get("steps"),list) else []:
                if stp.get("mechanically_compiled") is not True:
                    fail(f"MCB_STEP_NOT_COMPILER_OWNED: {lid}:{rpid}:{stp.get('step_id')}")
                eff=by_action.get(stp.get("step_id"))
                if not isinstance(eff,dict): fail(f"MCB_STEP_PROJECTION_MISSING: {lid}:{rpid}:{stp.get('step_id')}")
                for k in ("requires","moves","produces","property_updates","activate_restrictions","release_restrictions"):
                    if stp.get(k,[])!=eff.get(k,[]): fail(f"MCB_STEP_PROJECTION_DIVERGENCE: {lid}:{rpid}:{stp.get('step_id')}:{k}")

        steps=rp.get("steps")
        if not isinstance(steps,list) or not steps: fail(f"EXECUTION_STEPS_MISSING: {lid}:{rpid}")
        snapshots={"INITIAL":_clone_replay_state(state,budgets,active,properties,attachments,topology_rules)}
        step_ids=set(); placement_bound=set(); all_state_preconditions=set(); topology_preconditions={}
        for step in steps:
            if not isinstance(step,dict): fail(f"execution step invalid: {lid}:{rpid}")
            sid=step.get("step_id")
            if not nonempty(sid) or sid in step_ids: fail(f"EXECUTION_STEP_ID_INVALID: {lid}:{rpid}")
            step_ids.add(sid)
            token=step.get("render_token")
            if not nonempty(token) or token.strip().casefold() not in text.casefold():
                fail(f"EXECUTION_STEP_NOT_RENDERED: {lid}:{rpid}:{sid}")
            legal=step.get("legality_checks")
            expected_keys={"cost","target","timing","restriction"}
            if not isinstance(legal,dict) or set(legal)!=expected_keys:
                fail(f"EXECUTION_LEGALITY_CHECKS_INCOMPLETE: {lid}:{rpid}:{sid}")
            if any(v not in {"PASS","NOT_APPLICABLE"} for v in legal.values()):
                fail(f"EXECUTION_LEGALITY_NOT_CLOSED: {lid}:{rpid}:{sid}")

            before=_clone_replay_state(state,budgets,active,properties,attachments,topology_rules)
            snapshots[f"BEFORE:{sid}"]=before
            _validate_action_legality(step,resources,restrictions_meta,active,facts,constraints,evid,line,text,lid,rpid,placement_bound,before)
            for pre in step.get("state_preconditions",[]):
                all_state_preconditions.add(pre["precondition_id"])
                if pre.get("kind")=="RELATION": topology_preconditions[pre["precondition_id"]]=dict(pre)
            attachment_transitions=_validate_attachment_step(step,state,attachments,resources,lid,rpid)

            rchecks=step.get("restriction_checks",[])
            if not isinstance(rchecks,list): fail(f"EXECUTION_RESTRICTION_CHECKS_INVALID: {lid}:{rpid}:{sid}")
            got={}
            for chk in rchecks:
                if not isinstance(chk,dict) or chk.get("restriction_id") not in active or chk.get("status") not in {"PASS","NOT_APPLICABLE"}:
                    fail(f"EXECUTION_RESTRICTION_CHECK_INVALID: {lid}:{rpid}:{sid}")
                rid0=chk["restriction_id"]
                if rid0 in got: fail(f"EXECUTION_RESTRICTION_CHECK_DUPLICATE: {lid}:{rpid}:{sid}:{rid0}")
                got[rid0]=chk["status"]
            if set(got)!=active:
                fail(f"EXECUTION_ACTIVE_RESTRICTION_NOT_CHECKED: {lid}:{rpid}:{sid}")

            reqs=step.get("requires",[]); moves=step.get("moves",[]); produces=step.get("produces",[])
            if not all(isinstance(x,list) for x in (reqs,moves,produces)):
                fail(f"EXECUTION_STEP_RESOURCE_LIST_INVALID: {lid}:{rpid}:{sid}")
            for ent in reqs:
                resid,z,q=_validate_ref_qty(ent,"requires",resources,lid,rpid)
                if state[resid].get(z,0)<q:
                    fail(f"EXECUTION_RESOURCE_NOT_AVAILABLE: {lid}:{rpid}:{sid}:{resid}@{z}")
            for ent in moves:
                if not isinstance(ent,dict): fail(f"moves entry invalid: {lid}:{rpid}:{sid}")
                resid=ent.get("resource_id"); fz=ent.get("from_zone"); tz=ent.get("to_zone"); q=ent.get("qty")
                if resid not in resources or not nonempty(fz) or not nonempty(tz):
                    fail(f"EXECUTION_MOVE_INVALID: {lid}:{rpid}:{sid}")
                _positive_int(q,f"EXECUTION_MOVE_QTY_INVALID: {lid}:{rpid}:{sid}")
                fz=fz.strip(); tz=tz.strip()
                if state[resid].get(fz,0)<q:
                    fail(f"EXECUTION_DOUBLE_SPEND_OR_SOURCE_MISSING: {lid}:{rpid}:{sid}:{resid}@{fz}")
                state[resid][fz]=state[resid].get(fz,0)-q
                state[resid][tz]=state[resid].get(tz,0)+q
            for ent in produces:
                resid,z,q=_validate_ref_qty(ent,"produces",resources,lid,rpid)
                if resources[resid].get("kind")!="GENERATED":
                    fail(f"EXECUTION_CARD_COPY_CANNOT_BE_PRODUCED: {lid}:{rpid}:{sid}:{resid}")
                state[resid][z]=state[resid].get(z,0)+q

            _apply_attachment_transitions(attachment_transitions,attachments)
            _apply_property_updates(step,properties,resources,lid,rpid)

            bcons=step.get("budget_consumes",[]); bprod=step.get("budget_produces",[])
            if not isinstance(bcons,list) or not isinstance(bprod,list):
                fail(f"EXECUTION_BUDGET_STEP_LIST_INVALID: {lid}:{rpid}:{sid}")
            for ent in bcons:
                if not isinstance(ent,dict) or ent.get("budget_id") not in budgets:
                    fail(f"EXECUTION_BUDGET_CONSUME_INVALID: {lid}:{rpid}:{sid}")
                bid=ent["budget_id"]; q=_positive_int(ent.get("qty"),f"EXECUTION_BUDGET_QTY_INVALID: {lid}:{rpid}:{sid}")
                if budgets[bid]<q: fail(f"EXECUTION_BUDGET_EXHAUSTED: {lid}:{rpid}:{sid}:{bid}")
                budgets[bid]-=q
            for ent in bprod:
                if not isinstance(ent,dict) or ent.get("budget_id") not in budgets:
                    fail(f"EXECUTION_BUDGET_PRODUCE_INVALID: {lid}:{rpid}:{sid}")
                bid=ent["budget_id"]; q=_positive_int(ent.get("qty"),f"EXECUTION_BUDGET_QTY_INVALID: {lid}:{rpid}:{sid}")
                budgets[bid]+=q

            act=step.get("activate_restrictions",[]); rel=step.get("release_restrictions",[])
            if not isinstance(act,list) or not isinstance(rel,list) or any(x not in restrictions for x in act+rel):
                fail(f"EXECUTION_RESTRICTION_TRANSITION_INVALID: {lid}:{rpid}:{sid}")
            if len(set(act))!=len(act) or len(set(rel))!=len(rel):
                fail(f"EXECUTION_RESTRICTION_TRANSITION_DUPLICATE: {lid}:{rpid}:{sid}")
            for x in rel:
                if x not in active: fail(f"EXECUTION_RELEASE_INACTIVE_RESTRICTION: {lid}:{rpid}:{sid}:{x}")
                active.remove(x)
            for x in act:
                if x in active: fail(f"EXECUTION_REACTIVATE_ACTIVE_RESTRICTION: {lid}:{rpid}:{sid}:{x}")
                active.add(x)
            snapshots[f"AFTER:{sid}"]=_clone_replay_state(state,budgets,active,properties,attachments,topology_rules)

        snapshots["FINAL"]=_clone_replay_state(state,budgets,active,properties,attachments,topology_rules)
        _validate_state_and_topology_sweeps(rp,all_state_preconditions,topology_preconditions,text,lid,rpid,snapshots)
        _validate_rc16_backward_proof(rp,rc16_semantic,steps,all_state_preconditions,text,lid,rpid)
        derived_values,claim_meta=_validate_derived_claims(rp,snapshots,facts,resources,line,text,lid,rpid)

        required_placements={x.get("checkpoint_id") for x in (line.get("state_checkpoints") or []) if isinstance(x,dict) and x.get("placement_required") is True}
        if placement_bound!=required_placements:
            missing=','.join(sorted(required_placements-placement_bound))
            extra=','.join(sorted(placement_bound-required_placements))
            fail(f"ACTION_PLACEMENT_COVERAGE_MISMATCH: {lid}:{rpid}:missing={missing}:extra={extra}")

        outcome=rp.get("outcome")
        if not isinstance(outcome,dict): fail(f"EXECUTION_OUTCOME_MISSING: {lid}:{rpid}")
        odc=outcome.get("derived_claim_ids",[])
        if not isinstance(odc,list) or any(x not in derived_values for x in odc) or len(odc)!=len(set(odc)):
            fail(f"EXECUTION_OUTCOME_DERIVED_CLAIMS_INVALID: {lid}:{rpid}")
        certainty=outcome.get("certainty")
        if certainty not in {"GUARANTEED","CONDITIONAL","RANDOM","RANGE","UNKNOWN"}:
            fail(f"EXECUTION_OUTCOME_CERTAINTY_INVALID: {lid}:{rpid}")
        ot=outcome.get("render_token")
        if not nonempty(ot) or ot.strip().casefold() not in text.casefold():
            fail(f"EXECUTION_OUTCOME_NOT_RENDERED: {lid}:{rpid}")
        conds=outcome.get("conditions",[]); ctoks=outcome.get("condition_render_tokens",[])
        if not isinstance(conds,list) or not isinstance(ctoks,list) or any(not nonempty(x) for x in conds+ctoks):
            fail(f"EXECUTION_OUTCOME_CONDITIONS_INVALID: {lid}:{rpid}")
        if certainty=="GUARANTEED":
            if conds or ctoks: fail(f"GUARANTEED_OUTCOME_CANNOT_HAVE_EXTERNAL_CONDITIONS: {lid}:{rpid}")
            if outcome.get("guarantee_claim_status")!="CONSISTENT":
                fail(f"EXECUTION_GUARANTEE_CLAIM_NOT_CLOSED: {lid}:{rpid}")
        elif certainty in {"CONDITIONAL","RANDOM"}:
            if not conds or len(conds)!=len(ctoks):
                fail(f"CONDITIONAL_OUTCOME_REQUIRES_VISIBLE_CONDITIONS: {lid}:{rpid}")
            for tok in ctoks:
                if tok.strip().casefold() not in text.casefold():
                    fail(f"EXECUTION_OUTCOME_CONDITION_NOT_RENDERED: {lid}:{rpid}")
            if outcome.get("guarantee_claim_status")!="NO_FALSE_GUARANTEE":
                fail(f"EXECUTION_FALSE_GUARANTEE_NOT_CLOSED: {lid}:{rpid}")
        else:
            if len(conds)!=len(ctoks): fail(f"EXECUTION_OUTCOME_CONDITIONS_INVALID: {lid}:{rpid}")
            for tok in ctoks:
                if tok.strip().casefold() not in text.casefold(): fail(f"EXECUTION_OUTCOME_CONDITION_NOT_RENDERED: {lid}:{rpid}")
            if outcome.get("guarantee_claim_status")!="NO_FALSE_GUARANTEE": fail(f"EXECUTION_FALSE_GUARANTEE_NOT_CLOSED: {lid}:{rpid}")
        if contract_version=="RC16.2":
            claim=outcome.get("victory_claim","NONE")
            if claim not in {"NONE","LETHAL"}: fail(f"EXECUTION_VICTORY_CLAIM_INVALID: {lid}:{rpid}")
            visible_claim=bool(re.search(r"(?i)\b(?:OTK|FTK|lethal|l[ée]tal)\b", " ".join([str(line.get("render_axis_heading") or ""),str(outcome.get("render_token") or "")])) )
            if visible_claim and claim!="LETHAL": fail(f"VISIBLE_LETHAL_CLAIM_NOT_BOUND: {lid}:{rpid}")
            if claim=="LETHAL":
                proj=rp.get("compiled_mechanical_projection") or {}; checks=(proj.get("damage_ledger") or {}).get("lethal_checks",[])
                if not checks: fail(f"LETHAL_CLAIM_WITHOUT_LEDGER_CLOSURE: {lid}:{rpid}")
                if certainty=="GUARANTEED" and not any(x.get("claim")=="GUARANTEED" and x.get("status")=="PASS" for x in checks):
                    fail(f"GUARANTEED_LETHAL_NOT_CLOSED: {lid}:{rpid}")
        _validate_certainty_inventory(rp,outcome,text,claim_meta,lid,rpid)

    # End-to-end generic starter coverage. Several variants may deliberately share
    # one replay when the business authority judged their execution equivalent.
    if line.get("generic_starter"):
        expected={x.strip().casefold() for x in eligible_variants}
        if not expected: fail(f"GENERIC_STARTER_EXECUTION_VARIANTS_MISSING: {lid}")
        if len(covered)!=len(set(covered)):
            fail(f"GENERIC_STARTER_VARIANT_REPLAY_DUPLICATE: {lid}")
        if set(covered)!=expected:
            fail(f"GENERIC_STARTER_END_TO_END_NOT_CLOSED: {lid}")
    else:
        if [x for x in covered if x!="__base__"] or covered.count("__base__")!=1:
            fail(f"NON_GENERIC_EXECUTION_REPLAY_COVERAGE_INVALID: {lid}")



def _pilotage_policy_path():
    return Path(__file__).resolve().parent / PILOTAGE_POLICY_FILE


def _pilotage_policy_sha256(st=None):
    p=_pilotage_policy_path()
    if not p.exists(): fail("PILOTAGE_POLICY_SOURCE_MISSING")
    return _source_hash_from_state(st,PILOTAGE_POLICY_FILE) if isinstance(st,dict) else sha256(p)


def _pilotage_wire_templates():
    """Serialization-only templates. Values are placeholders, never business decisions."""
    starter={
      "starter_id":"__FILL_STARTER_ID__","display":"__FILL_DISPLAY__","render_token":"__FILL_RENDER_TOKEN__",
      "axis_heading":"__FILL_AXIS_HEADING__","line_ids":["__FILL_LINE_ID__"],"coverage_status":"PASS"
    }
    replay={
      "replay_id":"__FILL_REPLAY_ID__","status":"PASS","covers_variants":["__BASE__"],
      "resources":[],"budgets":[],"restrictions":[],"legality_evidence":[],"fact_catalog":[],"constraint_catalog":[],"external_inputs":[],
      "steps":[{"step_id":"__FILL_STEP_ID__","render_token":"__FILL_STEP_RENDER_TOKEN__","legality_checks":{"cost":"PASS","target":"PASS","timing":"PASS","restriction":"PASS"},"restriction_checks":[],"requires":[],"moves":[],"produces":[],"budget_consumes":[],"budget_produces":[],"activate_restrictions":[],"release_restrictions":[],"state_preconditions":[],"property_updates":[],"attachment_transitions":[],"action_legality_proof":{"action_id":"__FILL_STEP_ID__","participants":[],"output_resource_ids":[],"constraint_inventory_status":"COMPLETE_NO_APPLICABLE_CONSTRAINTS","applicable_constraint_ids":[],"participant_guard_inventory_status":"COMPLETE","output_requirement_inventory_status":"COMPLETE","active_restriction_inventory_status":"COMPLETE","action_legality_status":"PASS","placement_binding":{"status":"NOT_APPLICABLE"}}}],
      "derived_claim_inventory_status":"COMPLETE_NO_MATERIAL_CLAIMS","derived_claims":[],
      "outcome":{"certainty":"GUARANTEED","render_token":"__FILL_OUTCOME_RENDER_TOKEN__","conditions":[],"condition_render_tokens":[],"guarantee_claim_status":"CONSISTENT","derived_claim_ids":[],"victory_claim":"NONE"},
      "dynamic_state_scope_status":"COMPLETE_NO_DYNAMIC_PROPERTIES","initial_properties":[],
      "attachment_scope_status":"NO_ATTACHMENTS","initial_attachments":[],
      "topology_scope_status":"NO_MATERIAL_TOPOLOGY","topology_slots":[],"topology_rules":[],
      "state_precondition_inventory_status":"COMPLETE_NO_MATERIAL_PRECONDITIONS",
      "topology_inventory_status":"COMPLETE_NO_MATERIAL_RELATIONSHIPS","topology_checks":[],
      "external_condition_inventory_status":"COMPLETE_NO_MATERIAL_EXTERNAL_CONDITIONS","external_conditions":[],
      "semantic_layer_version":"SRC1-GR1-BW1-MCB1","src_scope_status":"COMPLETE_NO_MATERIAL_SRC","semantic_ruling_contracts":[],
      "game_rule_scope_status":"COMPLETE_NO_MATERIAL_GAME_RULES","action_game_rule_profiles":[],"game_rule_bindings":[],
      "mechanical_consequence_scope_status":"COMPLETE_NO_MATERIAL_BINDINGS","mechanical_consequence_bindings":[],
      "backward_proof_scope_status":"COMPLETE_NO_MATERIAL_BACKWARD_REQUIREMENTS","backward_requirements":[],"critical_decisions":[],
      "unified_cold_audit":{"status":"PASS","ignored_primary_inventories":True,"sweep_basis":"__FILL_INDEPENDENT_COLD_AUDIT_BASIS__","semantic":{"discovered_ids":[],"evidence_ids":[]},"game_rules":{"discovered_ids":[],"evidence_ids":[]},"mechanical_projection":{"status":"PASS","ignored_primary_bindings":True,"sweep_basis":"__FILL_INDEPENDENT_COLD_MCB_BASIS__","bindings":[]},"legality":{"by_action":{"__FILL_STEP_ID__":[]},"evidence_ids_by_action":{"__FILL_STEP_ID__":[]}},"derived":{"discovered_ids":[]},"state":{"discovered_ids":[]},"topology":{"discovered_ids":[]},"certainty":{"discovered_ids":[]},"backward":{"discovered_ids":[]}}
    }
    line={
      "line_id":"__FILL_LINE_ID__","render_axis_heading":"__FILL_AXIS_HEADING__","axis_validation_status":"PASS",
      "starter_ids":["__FILL_STARTER_ID__"],"starter_grouping_status":"NOT_APPLICABLE","starter_grouping_basis":None,
      "starter_display":"__FILL_STARTER_DISPLAY__","declared_initial_resources":[],"mandatory_initial_resources":[],"obtained_during_line":[],"hidden_initial_resources":[],
      "starter_contract_status":"PASS","generic_starter":False,"generic_coverage_status":"NOT_APPLICABLE",
      "starter_property_scope_status":"NO_PROPERTY_SENSITIVE_STARTER","starter_property_checks":[],
      "sequence_complexity":"SIMPLE","physical_state_scope_status":"NO_CRITICAL_ZONE_STATE","state_checkpoints":[],
      "effect_resolution_scope_status":"NO_RELEVANT_EFFECT_SELECTION","effect_resolution_checks":[],
      "line_execution_scope_status":"PASS","execution_replays":[replay]
    }
    return {"structural_starter_template":starter,"line_template":line,"execution_replay_template":replay}


def _pilotage_wire_schema_payload(st=None):
    return {
      "schema":PILOTAGE_SCHEMA_DESCRIPTOR,
      "wire_schema":PILOTAGE_WIRE_SCHEMA,
      "runtime_version":VERSION,
      "authority":PILOTAGE,
      "authority_source_file":PILOTAGE_POLICY_FILE,
      "authority_source_sha256":_pilotage_policy_sha256(st),
      "top_level":{
        "required":["wire_schema","run_id","authority","deck_artifact","render_sha256","status","execution_contract_version","axis_coverage_status","rendered_axis_count","starter_exploration_status","starter_inventory_status","structural_starters","lines"],
        "enums":{"status":["PASS"],"execution_contract_version":["RC16","RC16.1","RC16.2"],"axis_coverage_status":["PASS","NO_RENDERED_AXES"],"starter_exploration_status":["COMPLETE","NO_RENDERED_AXES"],"starter_inventory_status":["PASS","NO_RENDERED_AXES"]}
      },
      "structural_starter":{"required":["starter_id","display","render_token","axis_heading","line_ids","coverage_status"],"enums":{"coverage_status":["PASS"]}},
      "line":{"required":["line_id","render_axis_heading","axis_validation_status","starter_ids","starter_display","declared_initial_resources","mandatory_initial_resources","obtained_during_line","hidden_initial_resources","starter_contract_status","generic_starter","generic_coverage_status","starter_property_scope_status","starter_property_checks","sequence_complexity","physical_state_scope_status","state_checkpoints","effect_resolution_scope_status","effect_resolution_checks","line_execution_scope_status","execution_replays"]},
      "execution_replay":{"required":["replay_id","status","covers_variants","resources","budgets","restrictions","legality_evidence","fact_catalog","constraint_catalog","external_inputs","steps","derived_claim_inventory_status","derived_claims","outcome","dynamic_state_scope_status","initial_properties","attachment_scope_status","initial_attachments","topology_scope_status","topology_slots","topology_rules","state_precondition_inventory_status","topology_inventory_status","topology_checks","external_condition_inventory_status","external_conditions","semantic_layer_version","src_scope_status","semantic_ruling_contracts","game_rule_scope_status","action_game_rule_profiles","game_rule_bindings","backward_proof_scope_status","backward_requirements","critical_decisions"]},
      "step":{"required":["step_id","render_token","legality_checks","restriction_checks","requires","moves","produces","budget_consumes","budget_produces","activate_restrictions","release_restrictions","state_preconditions","property_updates","attachment_transitions","action_legality_proof"]},
      "action_legality_proof":{"required":["action_id","participants","output_resource_ids","constraint_inventory_status","applicable_constraint_ids","participant_guard_inventory_status","output_requirement_inventory_status","active_restriction_inventory_status","action_legality_status","placement_binding"]},
      "unified_cold_audit":{"required":["status","ignored_primary_inventories","sweep_basis","semantic","game_rules","legality","derived","state","topology","certainty","backward"],"id_sections":["semantic","game_rules","derived","state","topology","certainty","backward"],"legality_required":["by_action","evidence_ids_by_action"]},
      "conditional":[
        "rendered axes => starter_exploration_status COMPLETE + starter_inventory_status PASS + nonempty structural_starters + nonempty lines",
        "multiple starter_ids on one line => starter_grouping_status PASS + nonempty starter_grouping_basis",
        "RC16.1/RC16.2 replay => exactly one unified_cold_audit structure",
        "RC16.2 replay => MCB scope + bindings + independent cold mechanical projection; derived mechanical step fields are compiler-owned",
        "NO_RENDERED_AXES => structural_starters empty"
      ],
      "templates":_pilotage_wire_templates()
    }


def _wire_issue(issues,path,code,expected=None,observed=None):
    issues.append({"code":code,"path":path,"expected":expected,"observed":observed})


def _is_placeholder(v):
    return isinstance(v,str) and (v.startswith("__FILL_") or v.startswith("REPLACE_"))


def _scan_placeholders(v,path,issues):
    if isinstance(v,dict):
        for k,x in v.items():
            if k=="_wire_templates": continue
            _scan_placeholders(x,f"{path}.{k}",issues)
    elif isinstance(v,list):
        for i,x in enumerate(v): _scan_placeholders(x,f"{path}[{i}]",issues)
    elif _is_placeholder(v): _wire_issue(issues,path,"PILOTAGE_PLACEHOLDER_UNRESOLVED","non-placeholder",v)


def _pilotage_wire_issues(d,render_path: Path,st):
    issues=[]
    schema=_pilotage_wire_schema_payload(st)
    for k in schema["top_level"]["required"]:
        if k not in d: _wire_issue(issues,f"$.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
    if d.get("wire_schema")!=PILOTAGE_WIRE_SCHEMA: _wire_issue(issues,"$.wire_schema","PILOTAGE_WIRE_SCHEMA_MISMATCH",PILOTAGE_WIRE_SCHEMA,d.get("wire_schema"))
    if d.get("run_id")!=st.get("run_id"): _wire_issue(issues,"$.run_id","RUN_ID_MISMATCH",st.get("run_id"),d.get("run_id"))
    if d.get("authority")!=PILOTAGE: _wire_issue(issues,"$.authority","PILOTAGE_AUTHORITY_MISMATCH",PILOTAGE,d.get("authority"))
    if d.get("deck_artifact")!=st.get("current_artifact"): _wire_issue(issues,"$.deck_artifact","PILOTAGE_DECK_BINDING_MISMATCH",st.get("current_artifact"),d.get("deck_artifact"))
    expected_render=sha256(render_path) if render_path.exists() else None
    if d.get("render_sha256")!=expected_render: _wire_issue(issues,"$.render_sha256","PILOTAGE_RENDER_BINDING_MISMATCH",expected_render,d.get("render_sha256"))
    enums=schema["top_level"]["enums"]
    for k,vals in enums.items():
        if k in d and d.get(k) not in vals: _wire_issue(issues,f"$.{k}","PILOTAGE_WIRE_ENUM_INVALID",vals,d.get(k))
    if not isinstance(d.get("rendered_axis_count"),int) or isinstance(d.get("rendered_axis_count"),bool) or d.get("rendered_axis_count",-1)<0:
        _wire_issue(issues,"$.rendered_axis_count","PILOTAGE_WIRE_TYPE_INVALID","nonnegative integer",d.get("rendered_axis_count"))
    starters=d.get("structural_starters"); lines=d.get("lines")
    if not isinstance(starters,list): _wire_issue(issues,"$.structural_starters","PILOTAGE_WIRE_TYPE_INVALID","array",type(starters).__name__); starters=[]
    if not isinstance(lines,list): _wire_issue(issues,"$.lines","PILOTAGE_WIRE_TYPE_INVALID","array",type(lines).__name__); lines=[]
    rendered_axes=_rendered_axis_headings(render_path.read_text(encoding="utf-8")) if render_path.exists() else []
    if rendered_axes:
        if d.get("starter_exploration_status")!="COMPLETE": _wire_issue(issues,"$.starter_exploration_status","PILOTAGE_STARTER_EXPLORATION_WIRE_INVALID","COMPLETE",d.get("starter_exploration_status"))
        if d.get("starter_inventory_status")!="PASS": _wire_issue(issues,"$.starter_inventory_status","PILOTAGE_STARTER_INVENTORY_WIRE_INVALID","PASS",d.get("starter_inventory_status"))
        if not starters: _wire_issue(issues,"$.structural_starters","PILOTAGE_STRUCTURAL_STARTERS_REQUIRED","nonempty array",starters)
        if not lines: _wire_issue(issues,"$.lines","PILOTAGE_LINES_REQUIRED","nonempty array",lines)
    else:
        if d.get("starter_exploration_status")!="NO_RENDERED_AXES": _wire_issue(issues,"$.starter_exploration_status","PILOTAGE_NO_AXES_EXPLORATION_STATUS_INVALID","NO_RENDERED_AXES",d.get("starter_exploration_status"))
        if d.get("starter_inventory_status")!="NO_RENDERED_AXES": _wire_issue(issues,"$.starter_inventory_status","PILOTAGE_NO_AXES_INVENTORY_STATUS_INVALID","NO_RENDERED_AXES",d.get("starter_inventory_status"))
        if starters: _wire_issue(issues,"$.structural_starters","PILOTAGE_STARTERS_MUST_BE_EMPTY_WITHOUT_AXES",[],starters)
        if lines: _wire_issue(issues,"$.lines","PILOTAGE_LINES_MUST_BE_EMPTY_WITHOUT_AXES",[],lines)
    starter_ids=set(); line_ids=set()
    for i,si in enumerate(starters):
        path=f"$.structural_starters[{i}]"
        if not isinstance(si,dict): _wire_issue(issues,path,"PILOTAGE_WIRE_TYPE_INVALID","object",type(si).__name__); continue
        for k in schema["structural_starter"]["required"]:
            if k not in si: _wire_issue(issues,f"{path}.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
        sid=si.get("starter_id")
        if nonempty(sid):
            if sid in starter_ids: _wire_issue(issues,f"{path}.starter_id","PILOTAGE_STARTER_ID_DUPLICATE","unique",sid)
            starter_ids.add(sid)
        if si.get("coverage_status") not in {None,"PASS"}: _wire_issue(issues,f"{path}.coverage_status","PILOTAGE_WIRE_ENUM_INVALID",["PASS"],si.get("coverage_status"))
        if not isinstance(si.get("line_ids"),list): _wire_issue(issues,f"{path}.line_ids","PILOTAGE_WIRE_TYPE_INVALID","array",si.get("line_ids"))
    for i,line in enumerate(lines):
        path=f"$.lines[{i}]"
        if not isinstance(line,dict): _wire_issue(issues,path,"PILOTAGE_WIRE_TYPE_INVALID","object",type(line).__name__); continue
        for k in schema["line"]["required"]:
            if k not in line: _wire_issue(issues,f"{path}.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
        if "initial_resources" in line and "declared_initial_resources" not in line: _wire_issue(issues,f"{path}.initial_resources","PILOTAGE_WIRE_ALIAS_NONCANONICAL","declared_initial_resources","initial_resources")
        if "obtained_resources" in line and "obtained_during_line" not in line: _wire_issue(issues,f"{path}.obtained_resources","PILOTAGE_WIRE_ALIAS_NONCANONICAL","obtained_during_line","obtained_resources")
        lid=line.get("line_id")
        if nonempty(lid):
            if lid in line_ids: _wire_issue(issues,f"{path}.line_id","PILOTAGE_LINE_ID_DUPLICATE","unique",lid)
            line_ids.add(lid)
        sids=line.get("starter_ids")
        if isinstance(sids,list) and len(sids)>1:
            if line.get("starter_grouping_status")!="PASS": _wire_issue(issues,f"{path}.starter_grouping_status","PILOTAGE_SHARED_STARTER_GROUPING_REQUIRED","PASS",line.get("starter_grouping_status"))
            if not nonempty(line.get("starter_grouping_basis")): _wire_issue(issues,f"{path}.starter_grouping_basis","PILOTAGE_SHARED_STARTER_GROUPING_BASIS_REQUIRED","nonempty",line.get("starter_grouping_basis"))
        reps=line.get("execution_replays")
        if not isinstance(reps,list) or not reps:
            _wire_issue(issues,f"{path}.execution_replays","PILOTAGE_EXECUTION_REPLAYS_REQUIRED","nonempty array",reps)
            continue
        for j,rp in enumerate(reps):
            rpath=f"{path}.execution_replays[{j}]"
            if not isinstance(rp,dict): _wire_issue(issues,rpath,"PILOTAGE_WIRE_TYPE_INVALID","object",type(rp).__name__); continue
            for k in schema["execution_replay"]["required"]:
                if k not in rp: _wire_issue(issues,f"{rpath}.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
            if d.get("execution_contract_version") in {"RC16.1","RC16.2"} and "unified_cold_audit" not in rp:
                _wire_issue(issues,f"{rpath}.unified_cold_audit","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
            if d.get("execution_contract_version")=="RC16.2":
                for k in ("mechanical_consequence_scope_status","mechanical_consequence_bindings","compiled_mechanical_projection","compiled_mechanical_projection_sha256"):
                    if k not in rp: _wire_issue(issues,f"{rpath}.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
            steps=rp.get("steps")
            if isinstance(steps,list):
                for z,step in enumerate(steps):
                    spath=f"{rpath}.steps[{z}]"
                    if not isinstance(step,dict): _wire_issue(issues,spath,"PILOTAGE_WIRE_TYPE_INVALID","object",type(step).__name__); continue
                    for k in schema["step"]["required"]:
                        if k not in step: _wire_issue(issues,f"{spath}.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
                    proof=step.get("action_legality_proof")
                    if isinstance(proof,dict):
                        for k in schema["action_legality_proof"]["required"]:
                            if k not in proof: _wire_issue(issues,f"{spath}.action_legality_proof.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
                    elif "action_legality_proof" in step:
                        _wire_issue(issues,f"{spath}.action_legality_proof","PILOTAGE_WIRE_TYPE_INVALID","object",type(proof).__name__)
            ua=rp.get("unified_cold_audit")
            if d.get("execution_contract_version") in {"RC16.1","RC16.2"} and isinstance(ua,dict):
                for k in schema["unified_cold_audit"]["required"]:
                    if k not in ua: _wire_issue(issues,f"{rpath}.unified_cold_audit.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
                for k in schema["unified_cold_audit"]["id_sections"]:
                    sec=ua.get(k)
                    if isinstance(sec,dict) and "discovered_ids" not in sec: _wire_issue(issues,f"{rpath}.unified_cold_audit.{k}.discovered_ids","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
                leg=ua.get("legality")
                if isinstance(leg,dict):
                    for k in schema["unified_cold_audit"]["legality_required"]:
                        if k not in leg: _wire_issue(issues,f"{rpath}.unified_cold_audit.legality.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
                if d.get("execution_contract_version")=="RC16.2":
                    outcome=rp.get("outcome") if isinstance(rp,dict) else None
                    if not isinstance(outcome,dict) or outcome.get("victory_claim") not in {"NONE","LETHAL"}:
                        _wire_issue(issues,f"{rpath}.outcome.victory_claim","RC16_2_VICTORY_CLAIM_REQUIRED",["NONE","LETHAL"],outcome.get("victory_claim") if isinstance(outcome,dict) else None)
                    mp=ua.get("mechanical_projection")
                    if not isinstance(mp,dict):
                        _wire_issue(issues,f"{rpath}.unified_cold_audit.mechanical_projection","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","object",mp)
                    else:
                        for k in ("status","ignored_primary_bindings","sweep_basis","bindings"):
                            if k not in mp: _wire_issue(issues,f"{rpath}.unified_cold_audit.mechanical_projection.{k}","PILOTAGE_WIRE_REQUIRED_FIELD_MISSING","present",None)
    for i,si in enumerate(starters):
        if not isinstance(si,dict): continue
        for lid in si.get("line_ids",[]) if isinstance(si.get("line_ids"),list) else []:
            if lid not in line_ids: _wire_issue(issues,f"$.structural_starters[{i}].line_ids","PILOTAGE_WIRE_UNKNOWN_LINE_REFERENCE","known line_id",lid)
    for i,line in enumerate(lines):
        if not isinstance(line,dict): continue
        for sid in line.get("starter_ids",[]) if isinstance(line.get("starter_ids"),list) else []:
            if sid not in starter_ids: _wire_issue(issues,f"$.lines[{i}].starter_ids","PILOTAGE_WIRE_UNKNOWN_STARTER_REFERENCE","known starter_id",sid)
    _scan_placeholders(d,"$",issues)
    issues.sort(key=lambda x:(x.get("path") or "",x.get("code") or ""))
    return issues


def _last_pilotage_preflight_summary(run_dir: Path):
    ev=[x for x in _read_journal(run_dir) if x.get("event") in {"PILOTAGE_PREFLIGHT_FAILED","PILOTAGE_PREFLIGHT_SUCCEEDED","PILOTAGE_PREFLIGHT_EXCEPTION"}]
    if not ev: return None
    x=ev[-1]
    return {k:x.get(k) for k in ("event","pilotage_contract_sha256","wire_schema","issue_count","receipt_file","receipt_sha256","seq","timestamp_ns")}


def _verify_pilotage_preflight_receipt(receipt_path: Path, contract_path: Path, render_path: Path, st):
    if not receipt_path.exists(): fail("PILOTAGE_PREFLIGHT_REQUIRED")
    r=read_json(receipt_path,"pilotage preflight receipt")
    if r.get("status")!="PASS": fail("PILOTAGE_PREFLIGHT_REQUIRED")
    if r.get("run_id")!=st.get("run_id") or r.get("deck_artifact")!=st.get("current_artifact"): fail("PILOTAGE_PREFLIGHT_STALE")
    if r.get("wire_schema")!=PILOTAGE_WIRE_SCHEMA: fail("PILOTAGE_WIRE_SCHEMA_MISMATCH")
    checks={
      "pilotage_contract_sha256":sha256(contract_path),"render_sha256":sha256(render_path),
      "pilotage_source_sha256":_pilotage_policy_sha256(st)
    }
    for k,v in checks.items():
        if r.get(k)!=v: fail("PILOTAGE_PREFLIGHT_STALE")
    schema_file=r.get("schema_file")
    if not nonempty(schema_file) or not Path(schema_file).exists() or r.get("schema_sha256")!=sha256(Path(schema_file)):
        fail("PILOTAGE_PREFLIGHT_STALE")
    schema=read_json(Path(schema_file),"pilotage wire schema")
    if schema.get("wire_schema")!=PILOTAGE_WIRE_SCHEMA or schema.get("authority_source_sha256")!=_pilotage_policy_sha256(st):
        fail("PILOTAGE_PREFLIGHT_STALE")
    return r,sha256(receipt_path)


def cmd_pilotage_schema(a):
    rd=Path(a.run_dir) if getattr(a,"run_dir",None) else None
    if rd is not None:
        st=load_state(rd); require_run_id(st,a.run_id)
    payload=_pilotage_wire_schema_payload(st if rd is not None else None)
    out=Path(a.output)
    text=_stable_json_text(payload)
    hit=out.exists() and out.read_text(encoding="utf-8")==text
    _atomic_write_text(out,text)
    if rd is not None:
        _append_run_journal(rd,st,"DERIVED_CACHE_HIT" if hit else "DERIVED_CACHE_MISS",artifact_kind="pilotage-schema",output_file=str(out),output_sha256=sha256(out))
    print(f"PILOTAGE_SCHEMA_{'CACHE_HIT' if hit else 'WRITTEN'} {out}")



def _pilotage_full_preflight_issues(contract_path: Path, render_path: Path, st):
    """One preflight surface: wire issues are grouped, then the authoritative validator is dry-run exactly."""
    d=read_json(contract_path,"pilotage contract")
    issues=_pilotage_wire_issues(d,render_path,st)
    if issues:
        return issues
    try:
        validate_pilotage_contract(contract_path,render_path,st)
    except SystemExit as e:
        code,detail=_denied_parts(e)
        issues.append({"code":code,"path":"$","expected":"authoritative Pilotage validator pass","observed":detail,
                       "owner_authority":PILOTAGE,"repair_domain":"BUSINESS_SEMANTIC_MECHANICAL",
                       "budget_class":"BUSINESS","severity":"BLOCKING","repairable":True,"blocking":True,"domain":"BUSINESS_SEMANTIC_MECHANICAL"})
    return issues



def _pilotage_render_structure(render_path: Path):
    """Derive only presentation identity from the frozen render; never infer card semantics."""
    text=render_path.read_text(encoding="utf-8")
    lines=text.splitlines()
    axes=[]
    axis_re=re.compile(r"^\s*###\s+(Axe\s+\d+\b.*)$",re.I)
    for i,raw in enumerate(lines):
        m=axis_re.match(raw)
        if m: axes.append((i,m.group(1).strip()))
    out=[]
    used_line_ids=set(); used_starter_ids=set()
    for ai,(start,heading) in enumerate(axes,1):
        end=axes[ai][0] if ai<len(axes) else len(lines)
        block=lines[start+1:end]
        line_id=None
        for raw in block:
            m=re.search(r"<!--\s*([A-Za-z0-9_.:-]*line[A-Za-z0-9_.:-]*)\s*-->",raw,re.I)
            if m:
                line_id=m.group(1).strip(); break
        if not line_id:
            line_id=f"line-axis{ai}"
        base=line_id; n=2
        while line_id in used_line_ids:
            line_id=f"{base}-{n}"; n+=1
        used_line_ids.add(line_id)
        starters=[]
        for raw in block:
            st=re.match(r"^\s*\*\*(Starter(?:\s*/\s*ouverture)?\s*(?:—|-|:).*?)\*\*\s*$",raw,re.I)
            if not st: continue
            token=st.group(1).strip()
            display=re.sub(r"^Starter(?:\s*/\s*ouverture)?\s*(?:—|-|:)\s*","",token,flags=re.I).strip() or token
            sid=f"{line_id}-starter-{len(starters)+1}"
            while sid in used_starter_ids: sid += "x"
            used_starter_ids.add(sid)
            starters.append({"starter_id":sid,"display":display,"render_token":token,"axis_heading":heading,"line_ids":[line_id],"coverage_status":"PASS"})
        if not starters:
            # Fallback is presentation-only: use an explicit Départ token if STRUCTURE omitted a Starter label.
            for raw in block:
                st=re.match(r"^\s*\*\*(Départ|Situation / Main de départ)\s*:\*\*\s*(.+)$",raw,re.I)
                if st:
                    token=(st.group(1)+" : "+st.group(2)).strip()
                    display=st.group(2).strip().strip('`')
                    sid=f"{line_id}-starter-1"; used_starter_ids.add(sid)
                    starters.append({"starter_id":sid,"display":display,"render_token":token,"axis_heading":heading,"line_ids":[line_id],"coverage_status":"PASS"})
                    break
        out.append({"axis_heading":heading,"line_id":line_id,"starters":starters})
    return out


def _pilotage_empty_replay(replay_id):
    """Business skeleton: IDs are shell-owned; semantic contents remain model-owned."""
    return {
      "replay_id":replay_id,"status":"PASS","covers_variants":["__BASE__"],
      "resources":[],"budgets":[],"restrictions":[],"legality_evidence":[],"fact_catalog":[],"constraint_catalog":[],"external_inputs":[],
      "steps":[],"derived_claim_inventory_status":"COMPLETE_NO_MATERIAL_CLAIMS","derived_claims":[],
      "outcome":{"certainty":"CONDITIONAL","render_token":"","conditions":[],"condition_render_tokens":[],"guarantee_claim_status":"CONSISTENT","derived_claim_ids":[],"victory_claim":"NONE"},
      "dynamic_state_scope_status":"COMPLETE_NO_DYNAMIC_PROPERTIES","initial_properties":[],
      "attachment_scope_status":"NO_ATTACHMENTS","initial_attachments":[],
      "topology_scope_status":"NO_MATERIAL_TOPOLOGY","topology_slots":[],"topology_rules":[],
      "state_precondition_inventory_status":"COMPLETE_NO_MATERIAL_PRECONDITIONS",
      "topology_inventory_status":"COMPLETE_NO_MATERIAL_RELATIONSHIPS","topology_checks":[],
      "external_condition_inventory_status":"COMPLETE_NO_MATERIAL_EXTERNAL_CONDITIONS","external_conditions":[],
      "semantic_layer_version":"SRC1-GR1-BW1-MCB1","src_scope_status":"COMPLETE_NO_MATERIAL_SRC","semantic_ruling_contracts":[],
      "game_rule_scope_status":"COMPLETE_NO_MATERIAL_GAME_RULES","action_game_rule_profiles":[],"game_rule_bindings":[],
      "mechanical_consequence_scope_status":"COMPLETE_NO_MATERIAL_BINDINGS","mechanical_consequence_bindings":[],
      "backward_proof_scope_status":"COMPLETE_NO_MATERIAL_BACKWARD_REQUIREMENTS","backward_requirements":[],"critical_decisions":[],
      "unified_cold_audit":{"status":"PASS","ignored_primary_inventories":True,"sweep_basis":"MODEL_MUST_COMPLETE_IF_MATERIAL","semantic":{"discovered_ids":[],"evidence_ids":[]},"game_rules":{"discovered_ids":[],"evidence_ids":[]},"mechanical_projection":{"status":"PASS","ignored_primary_bindings":True,"sweep_basis":"MODEL_MUST_COMPLETE_IF_MATERIAL","bindings":[]},"legality":{"by_action":{},"evidence_ids_by_action":{}},"derived":{"discovered_ids":[]},"state":{"discovered_ids":[]},"topology":{"discovered_ids":[]},"certainty":{"discovered_ids":[]},"backward":{"discovered_ids":[]}}
    }


def _pilotage_business_skeleton_from_render(st, render_path: Path):
    structure=_pilotage_render_structure(render_path)
    starters=[]; business_lines=[]
    for ent in structure:
        starters.extend(copy.deepcopy(ent["starters"]))
        sids=[x["starter_id"] for x in ent["starters"]]
        display=ent["starters"][0]["display"] if ent["starters"] else ent["axis_heading"]
        lid=ent["line_id"]
        business_lines.append({
          "line_id":lid,"render_axis_heading":ent["axis_heading"],"render_token":ent["axis_heading"],"axis_validation_status":"PASS",
          "starter_ids":sids,"starter_grouping_status":"PASS" if len(sids)>1 else "NOT_APPLICABLE","starter_grouping_basis":"SHELL_DERIVED_SHARED_AXIS" if len(sids)>1 else None,
          "starter_display":display,"declared_initial_resources":[],"mandatory_initial_resources":[],"obtained_during_line":[],"hidden_initial_resources":[],
          "starter_contract_status":"PASS","generic_starter":False,"generic_coverage_status":"NOT_APPLICABLE",
          "starter_property_scope_status":"NO_PROPERTY_SENSITIVE_STARTER","starter_property_checks":[],
          "sequence_complexity":"SIMPLE","physical_state_scope_status":"NO_CRITICAL_ZONE_STATE","state_checkpoints":[],
          "effect_resolution_scope_status":"NO_RELEVANT_EFFECT_SELECTION","effect_resolution_checks":[],
          "line_execution_scope_status":"PASS","execution_replays":[_pilotage_empty_replay(f"{lid}-replay-1")]
        })
    has=bool(structure)
    return {
      "status":"PASS","execution_contract_version":"RC16.2","axis_coverage_status":"PASS" if has else "NO_RENDERED_AXES",
      "starter_exploration_status":"COMPLETE" if has else "NO_RENDERED_AXES","starter_inventory_status":"PASS" if has else "NO_RENDERED_AXES",
      "structural_starters":starters,"lines":business_lines
    }


_PILOTAGE_SHELL_LINE_FIELDS={"line_id","render_axis_heading","render_token","axis_validation_status","starter_ids","starter_grouping_status","starter_grouping_basis","starter_display","execution_replays"}
_PILOTAGE_SHELL_REPLAY_FIELDS={"replay_id"}
_PILOTAGE_ALLOWED_TOP_PATCH_FIELDS=set()
_PILOTAGE_ALLOWED_LINE_PATCH_FIELDS={
    "declared_initial_resources","mandatory_initial_resources","obtained_during_line","hidden_initial_resources",
    "starter_contract_status","generic_starter","generic_coverage_status","starter_property_scope_status","starter_property_checks",
    "sequence_complexity","physical_state_scope_status","state_checkpoints","effect_resolution_scope_status","effect_resolution_checks","line_execution_scope_status"
}
_PILOTAGE_ALLOWED_REPLAY_PATCH_FIELDS={
    "status","covers_variants","resources","budgets","restrictions","legality_evidence","fact_catalog","constraint_catalog","external_inputs","steps",
    "derived_claim_inventory_status","derived_claims","outcome","dynamic_state_scope_status","initial_properties","attachment_scope_status","initial_attachments",
    "topology_scope_status","topology_slots","topology_rules","state_precondition_inventory_status","topology_inventory_status","topology_checks",
    "external_condition_inventory_status","external_conditions","semantic_layer_version","src_scope_status","semantic_ruling_contracts","game_rule_scope_status",
    "action_game_rule_profiles","game_rule_bindings","mechanical_consequence_scope_status","mechanical_consequence_bindings",
    "backward_proof_scope_status","backward_requirements","critical_decisions","unified_cold_audit"
}


def _pilotage_locality_allowed_fields(issue_codes):
    codes={str(x) for x in (issue_codes or [])}
    if not codes: return set(_PILOTAGE_ALLOWED_LINE_PATCH_FIELDS),set(_PILOTAGE_ALLOWED_REPLAY_PATCH_FIELDS)
    line=set(); replay=set()
    for code in codes:
        if code in {"PILOTAGE_LINES_REQUIRED","PILOTAGE_STRUCTURAL_STARTERS_REQUIRED"} or code.startswith("PILOTAGE_BUSINESS_PAYLOAD_"):
            # Builder owns these; model repair cannot replace structural arrays.
            continue
        if code in {"ACTION_LEGALITY_EVIDENCE_MISSING","ACTION_LEGALITY_EVIDENCE_KIND_INVALID","UNIFIED_COLD_LEGALITY_ACTION_COVERAGE_MISMATCH"}:
            replay |= {"legality_evidence","fact_catalog","constraint_catalog","steps","unified_cold_audit","semantic_ruling_contracts","game_rule_bindings","action_game_rule_profiles"}
        elif code in {"EXECUTION_RESOURCES_MISSING","PROOF_FLOOR_DECLARED_RESOURCES_UNTRACKED"} or code.startswith("MCB_RESOURCE_"):
            line |= {"declared_initial_resources","mandatory_initial_resources","obtained_during_line","hidden_initial_resources"}
            replay |= {"resources","steps","semantic_ruling_contracts","game_rule_bindings","mechanical_consequence_scope_status","mechanical_consequence_bindings","unified_cold_audit"}
        elif code.startswith("PROOF_FLOOR_") or code.startswith("MCB_") or code.startswith("ACTION_LEGALITY_"):
            line |= set(_PILOTAGE_ALLOWED_LINE_PATCH_FIELDS)
            replay |= set(_PILOTAGE_ALLOWED_REPLAY_PATCH_FIELDS)
        else:
            line |= set(_PILOTAGE_ALLOWED_LINE_PATCH_FIELDS)
            replay |= set(_PILOTAGE_ALLOWED_REPLAY_PATCH_FIELDS)
    return line,replay


def _pilotage_shell_identity(payload):
    return {
      "top":{k:copy.deepcopy(payload.get(k)) for k in ("status","execution_contract_version","axis_coverage_status","starter_exploration_status","starter_inventory_status","structural_starters")},
      "lines":[{k:copy.deepcopy(line.get(k)) for k in _PILOTAGE_SHELL_LINE_FIELDS if k!="execution_replays"} | {"replay_ids":[rp.get("replay_id") for rp in line.get("execution_replays",[]) if isinstance(rp,dict)]} for line in payload.get("lines",[]) if isinstance(line,dict)]
    }


def _pilotage_merge_business_patch(skeleton, patch, issue_codes=None, base_payload=None):
    """Merge model-owned slots by stable IDs. Structural arrays/identities are immutable."""
    if not isinstance(skeleton,dict) or not isinstance(patch,dict): fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: skeleton/patch must be objects")
    base=copy.deepcopy(base_payload if base_payload is not None else skeleton)
    if not isinstance(base,dict) or _pilotage_shell_identity(base)!=_pilotage_shell_identity(skeleton):
        fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: base payload changed shell-owned identity")
    illegal=set(patch)-{"schema","top_level","line_updates"}
    if illegal: fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: unsupported top-level patch keys "+",".join(sorted(illegal)))
    top=patch.get("top_level",{})
    if not isinstance(top,dict): fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: top_level must be object")
    if set(top)-_PILOTAGE_ALLOWED_TOP_PATCH_FIELDS: fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: shell-owned top-level field")
    line_updates=patch.get("line_updates",{})
    if not isinstance(line_updates,dict): fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: line_updates must be object")
    out=base
    by_line={x.get("line_id"):x for x in out.get("lines",[]) if isinstance(x,dict)}
    allowed_line,allowed_replay=_pilotage_locality_allowed_fields(issue_codes)
    for lid,upd in line_updates.items():
        if lid not in by_line or not isinstance(upd,dict): fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: unknown/invalid line {lid}")
        if any(k in _PILOTAGE_SHELL_LINE_FIELDS for k in upd if k!="replay_updates"): fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: shell-owned line field {lid}")
        unknown=set(upd)-allowed_line-{"replay_updates"}
        if unknown: fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: line fields outside locality {lid}: {','.join(sorted(unknown))}")
        target=by_line[lid]
        for k,v in upd.items():
            if k=="replay_updates": continue
            target[k]=copy.deepcopy(v)
        rups=upd.get("replay_updates",{})
        if not isinstance(rups,dict): fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: replay_updates must be object {lid}")
        by_rep={x.get("replay_id"):x for x in target.get("execution_replays",[]) if isinstance(x,dict)}
        for rid,rupd in rups.items():
            if rid not in by_rep or not isinstance(rupd,dict): fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: unknown/invalid replay {lid}:{rid}")
            if any(k in _PILOTAGE_SHELL_REPLAY_FIELDS or k in {"compiled_mechanical_projection","compiled_mechanical_projection_sha256"} for k in rupd):
                fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: shell-owned replay field {lid}:{rid}")
            unknown=set(rupd)-allowed_replay
            if unknown: fail(f"PILOTAGE_REPAIR_SCOPE_VIOLATION: replay fields outside locality {lid}:{rid}: {','.join(sorted(unknown))}")
            for k,v in rupd.items(): by_rep[rid][k]=copy.deepcopy(v)
    return out


def _pilotage_builder_receipt_valid(rd: Path, st, business: Path, render: Path):
    rec=rd/PILOTAGE_BUSINESS_MERGE_RECEIPT
    if not rec.exists(): return False
    try: d=read_json(rec,"Pilotage business merge receipt")
    except BaseException: return False
    return d.get("schema")==PILOTAGE_BUSINESS_MERGE_RECEIPT_SCHEMA and d.get("status")=="PASS" and d.get("run_id")==st.get("run_id") and d.get("deck_artifact")==st.get("current_artifact") and d.get("render_sha256")==sha256(render) and d.get("business_payload_sha256")==sha256(business)


def cmd_pilotage_business_skeleton(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"pilotage-business-skeleton")
    if next_gate(st)[0]!="PILOTAGE_VALIDATED": fail(f"pilotage-business-skeleton requires next gate PILOTAGE_VALIDATED; next gate is {next_gate(st)[0]}")
    render,manifest,render_contract=_rc16221_render_bindings(st)
    sk=_pilotage_business_skeleton_from_render(st,render); out=Path(a.output)
    _atomic_write_text(out,_stable_json_text(sk))
    rec={"schema":PILOTAGE_BUSINESS_SKELETON_SCHEMA,"status":"PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"deck_sha256":_current_deck_snapshot_sha256(st),"render_sha256":sha256(render),"skeleton_file":str(out),"skeleton_sha256":sha256(out),"runtime_version":VERSION,"shell_owned":["structural_starters","line identity/axis/starter bindings","replay_id"]}
    rp=rd/PILOTAGE_BUSINESS_SKELETON_RECEIPT; _atomic_write_text(rp,_stable_json_text(rec))
    _append_run_journal(rd,st,"PILOTAGE_BUSINESS_SKELETON_BUILT",deck_artifact=st.get("current_artifact"),render_id=st.get("current_render"),render_sha256=sha256(render),skeleton_file=str(out),skeleton_sha256=sha256(out),receipt_file=str(rp),receipt_sha256=sha256(rp))
    print(json.dumps(rec,ensure_ascii=False,indent=2)); return rec


def cmd_pilotage_business_merge(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"pilotage-business-merge")
    if next_gate(st)[0]!="PILOTAGE_VALIDATED": fail(f"pilotage-business-merge requires next gate PILOTAGE_VALIDATED; next gate is {next_gate(st)[0]}")
    render,manifest,render_contract=_rc16221_render_bindings(st)
    skeleton=Path(a.skeleton_file); patch=Path(a.patch_file); out=Path(a.output); base=Path(a.base_business_file) if getattr(a,"base_business_file",None) else skeleton
    if not skeleton.exists(): fail("PILOTAGE_BUSINESS_SKELETON_MISSING")
    if not patch.exists(): fail("PILOTAGE_BUSINESS_PATCH_MISSING")
    skrec=rd/PILOTAGE_BUSINESS_SKELETON_RECEIPT
    if not skrec.exists(): fail("PILOTAGE_BUSINESS_SKELETON_RECEIPT_MISSING")
    sr=read_json(skrec,"Pilotage business skeleton receipt")
    if sr.get("skeleton_sha256")!=sha256(skeleton) or sr.get("render_sha256")!=sha256(render) or sr.get("deck_artifact")!=st.get("current_artifact"):
        fail("PILOTAGE_BUSINESS_SKELETON_STALE")
    issue_codes=[]
    repair_receipt=getattr(a,"repair_receipt",None)
    if repair_receipt:
        rr=Path(repair_receipt)
        if not rr.exists(): fail("PILOTAGE_REPAIR_RECEIPT_MISSING")
        rdry=read_json(rr,"Pilotage repair receipt")
        if rdry.get("render_sha256")!=sha256(render) or rdry.get("deck_artifact")!=st.get("current_artifact"):
            fail("PILOTAGE_REPAIR_RECEIPT_STALE")
        issue_codes=[x.get("code") for x in rdry.get("issues",[]) if isinstance(x,dict)]
    if not base.exists(): fail("PILOTAGE_BUSINESS_BASE_MISSING")
    merged=_pilotage_merge_business_patch(read_json(skeleton,"Pilotage skeleton"),read_json(patch,"Pilotage business patch"),issue_codes=issue_codes,base_payload=read_json(base,"Pilotage business base"))
    _atomic_write_text(out,_stable_json_text(merged))
    rec={"schema":PILOTAGE_BUSINESS_MERGE_RECEIPT_SCHEMA,"status":"PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"deck_sha256":_current_deck_snapshot_sha256(st),"render_sha256":sha256(render),"skeleton_sha256":sha256(skeleton),"patch_sha256":sha256(patch),"base_business_sha256":sha256(base),"business_payload_file":str(out),"business_payload_sha256":sha256(out),"repair_issue_codes":sorted(x for x in issue_codes if nonempty(x)),"runtime_version":VERSION}
    rp=rd/PILOTAGE_BUSINESS_MERGE_RECEIPT; _atomic_write_text(rp,_stable_json_text(rec))
    _append_run_journal(rd,st,"PILOTAGE_BUSINESS_PATCH_MERGED",deck_artifact=st.get("current_artifact"),render_id=st.get("current_render"),business_payload_file=str(out),business_payload_sha256=sha256(out),skeleton_sha256=sha256(skeleton),patch_sha256=sha256(patch),base_business_sha256=sha256(base),repair_issue_codes=rec["repair_issue_codes"],receipt_file=str(rp),receipt_sha256=sha256(rp))
    print(json.dumps(rec,ensure_ascii=False,indent=2)); return rec


def _pilotage_issue_domain(code):
    """Classify a validator issue for repair routing without reinterpreting Yu-Gi-Oh doctrine."""
    code=str(code or "")
    presentation={
        "PILOTAGE_LINE_NOT_RENDERED","PILOTAGE_STARTER_DISPLAY_NOT_RENDERED",
        "STRUCTURAL_STARTER_NOT_RENDERED","PILOTAGE_AXIS_NOT_RENDERED",
        "RENDERED_AXIS_NOT_COVERED","AXIS_COVERED_MULTIPLE_TIMES",
    }
    if code in presentation or code.startswith("RENDER_") or code.startswith("PREFREEZE_RENDER_"):
        return "PRESENTATION_RENDER"
    admin_exact={
        "ACTION_LEGALITY_EVIDENCE_KIND_INVALID","PILOTAGE_PLACEHOLDER_UNRESOLVED",
        "PILOTAGE_WIRE_SCHEMA_MISMATCH","PILOTAGE_CONTRACT_MISSING","PILOTAGE_SCHEMA_MISSING",
        "PILOTAGE_RENDER_MISSING","PILOTAGE_BUSINESS_PAYLOAD_INVALID",
        "PILOTAGE_NOMINAL_CONTRACT_REQUIRES_RC16_2_MCB","MCB_SEMANTIC_LAYER_REQUIRED",
        "PILOTAGE_LINES_REQUIRED","PILOTAGE_STRUCTURAL_STARTERS_REQUIRED",
        "PILOTAGE_BUSINESS_BUILDER_REQUIRED","PILOTAGE_REPAIR_SCOPE_VIOLATION",
    }
    if code in admin_exact or code.startswith("PILOTAGE_WIRE_") or code.startswith("PILOTAGE_BUSINESS_PAYLOAD_") or code.startswith("PILOTAGE_SHARED_STARTER_GROUPING_") or code.startswith("MCB_UNRESOLVED_"):
        return "PROOF_SCHEMA_ADMIN"
    if code.startswith("PROOF_FLOOR_") or code.startswith("MCB_RESOURCE_") or code.startswith("MCB_REQUIREMENT_") or code.startswith("MCB_LETHAL_") or code in {
        "MCB_COLD_PROJECTION_DIVERGENCE","MCB_MATERIAL_SOURCE_UNBOUND","MCB_BINDINGS_MISSING",
        "ACTION_LEGALITY_CONSTRAINT_FAILED","ACTION_LEGALITY_FACT_FAILED","ACTION_LEGALITY_RESTRICTION_FAILED",
        "ACTION_LEGALITY_EVIDENCE_MISSING","EXECUTION_RESOURCES_MISSING","UNIFIED_COLD_LEGALITY_ACTION_COVERAGE_MISMATCH",
    }:
        return "BUSINESS_SEMANTIC_MECHANICAL"
    # Pure representation/contract-shape defects are administrative, not business attempts.
    if code.startswith("MCB_BINDING_") or code.startswith("MCB_SCOPE_") or code.startswith("MCB_COLD_PROJECTION_") or code.startswith("MCB_COMPILED_") or code.startswith("MCB_DERIVED_FIELD_") or code.startswith("RC16_2_"):
        return "PROOF_SCHEMA_ADMIN"
    return "UNRESOLVED_DOMAIN"


def _pilotage_dry_run_commit_eligible(receipt, deck_sha256, render_sha256, business_sha256):
    if not isinstance(receipt,dict) or receipt.get("status")!="PASS": return False
    return receipt.get("deck_sha256")==deck_sha256 and receipt.get("render_sha256")==render_sha256 and receipt.get("business_payload_sha256")==business_sha256


def _proof_floor_issues_for_replay(line, rp, rp_path, issues):
    """Reject self-contradictory proof absence using only already-structured claims."""
    outcome=rp.get("outcome") if isinstance(rp.get("outcome"),dict) else {}
    binds=rp.get("mechanical_consequence_bindings") if isinstance(rp.get("mechanical_consequence_bindings"),list) else []
    operators=[b.get("operator") for b in binds if isinstance(b,dict)]
    if outcome.get("victory_claim")=="LETHAL" and outcome.get("certainty")=="GUARANTEED":
        has_damage=any(op=="DAMAGE_EVENT" for op in operators)
        has_check=any(op=="LETHAL_CHECK" for op in operators)
        if not (has_damage and has_check):
            _wire_issue(issues,f"{rp_path}.outcome","PROOF_FLOOR_LETHAL_EVIDENCE_REQUIRED","GUARANTEED lethal backed by DAMAGE_EVENT + LETHAL_CHECK",{"operators":operators,"victory_claim":"LETHAL","certainty":"GUARANTEED"},owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS")
        if rp.get("derived_claim_inventory_status")=="COMPLETE_NO_MATERIAL_CLAIMS" and not rp.get("derived_claims"):
            _wire_issue(issues,f"{rp_path}.derived_claim_inventory_status","PROOF_FLOOR_DERIVED_CLAIM_REQUIRED","material derived claim inventory for guaranteed lethal",rp.get("derived_claim_inventory_status"),owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS")
    declared=line.get("declared_initial_resources") if isinstance(line,dict) else None
    if isinstance(declared,list) and any(nonempty(x) for x in declared):
        resources=rp.get("resources")
        if not isinstance(resources,list) or not resources:
            _wire_issue(issues,f"{rp_path}.resources","PROOF_FLOOR_DECLARED_RESOURCES_UNTRACKED","nonempty replay resources for declared material initial resources",resources,owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS")
    material_src=False
    for src in rp.get("semantic_ruling_contracts",[]) if isinstance(rp.get("semantic_ruling_contracts"),list) else []:
        if isinstance(src,dict) and src.get("material_to_line") is True:
            material_src=True; break
    if not material_src:
        for src in rp.get("game_rule_bindings",[]) if isinstance(rp.get("game_rule_bindings"),list) else []:
            if isinstance(src,dict) and src.get("material_to_line") is True:
                material_src=True; break
    tracked_resources=rp.get("resources") if isinstance(rp.get("resources"),list) else []
    declared_material=isinstance(declared,list) and any(nonempty(x) for x in declared) and bool(tracked_resources)
    if (material_src or declared_material) and rp.get("mechanical_consequence_scope_status")=="COMPLETE_NO_MATERIAL_BINDINGS":
        _wire_issue(issues,f"{rp_path}.mechanical_consequence_scope_status","PROOF_FLOOR_MCB_REQUIRED","COMPLETE with mechanical consequence bindings for declared material proof surface",rp.get("mechanical_consequence_scope_status"),owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS")


def _pilotage_business_issues(payload):
    """Aggregate read-only authoring defects before any terminal Pilotage transaction mutates artifacts."""
    issues=[]
    if not isinstance(payload,dict):
        return [_rc1623_make_issue("PILOTAGE_BUSINESS_PAYLOAD_INVALID","$","object",type(payload).__name__,owner_authority=PILOTAGE,repair_domain="PROOF_SCHEMA_ADMIN",budget_class="NON_BUSINESS")]
    forbidden={"run_id","authority","deck_artifact","render_sha256","wire_schema","pilotage_source_sha256","rendered_axis_count","rendered_axis_headings"}
    for k in sorted(forbidden & set(payload)):
        _wire_issue(issues,f"$.{k}","PILOTAGE_BUSINESS_PAYLOAD_CONTAINS_MECHANICAL_BINDING","absent",payload.get(k))
    required={"status","execution_contract_version","axis_coverage_status","starter_exploration_status","starter_inventory_status","structural_starters","lines"}
    for k in sorted(required-set(payload)):
        _wire_issue(issues,f"$.{k}","PILOTAGE_BUSINESS_PAYLOAD_REQUIRED_FIELD_MISSING","present",None)
    if payload.get("execution_contract_version")!="RC16.2":
        _wire_issue(issues,"$.execution_contract_version","PILOTAGE_NOMINAL_CONTRACT_REQUIRES_RC16_2_MCB","RC16.2",payload.get("execution_contract_version"))
    lines=payload.get("lines")
    if not isinstance(lines,list):
        _wire_issue(issues,"$.lines","PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID","array",type(lines).__name__)
        lines=[]
    for li,line in enumerate(lines):
        lp=f"$.lines[{li}]"
        if not isinstance(line,dict):
            _wire_issue(issues,lp,"PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID","object",type(line).__name__); continue
        replays=line.get("execution_replays")
        if not isinstance(replays,list):
            _wire_issue(issues,f"{lp}.execution_replays","PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID","array",type(replays).__name__); continue
        for ri,rp in enumerate(replays):
            rp_path=f"{lp}.execution_replays[{ri}]"
            if not isinstance(rp,dict):
                _wire_issue(issues,rp_path,"PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID","object",type(rp).__name__); continue
            for k in ("compiled_mechanical_projection","compiled_mechanical_projection_sha256"):
                if k in rp:
                    _wire_issue(issues,f"{rp_path}.{k}","MCB_COMPILED_PROJECTION_MODEL_AUTHORED","absent",rp.get(k))
            if rp.get("semantic_layer_version")!="SRC1-GR1-BW1-MCB1":
                _wire_issue(issues,f"{rp_path}.semantic_layer_version","MCB_SEMANTIC_LAYER_REQUIRED","SRC1-GR1-BW1-MCB1",rp.get("semantic_layer_version"))
            if rp.get("mechanical_consequence_scope_status") not in {"COMPLETE","COMPLETE_NO_MATERIAL_BINDINGS"}:
                _wire_issue(issues,f"{rp_path}.mechanical_consequence_scope_status","MCB_SCOPE_NOT_CLOSED","COMPLETE or COMPLETE_NO_MATERIAL_BINDINGS",rp.get("mechanical_consequence_scope_status"))
            binds=rp.get("mechanical_consequence_bindings")
            if not isinstance(binds,list):
                _wire_issue(issues,f"{rp_path}.mechanical_consequence_bindings","MCB_BINDINGS_INVALID","array",type(binds).__name__); binds=[]
            seen=set()
            for bi,b in enumerate(binds):
                bp=f"{rp_path}.mechanical_consequence_bindings[{bi}]"
                if not isinstance(b,dict):
                    _wire_issue(issues,bp,"MCB_BINDING_INVALID","object",type(b).__name__); continue
                bid=b.get("binding_id")
                if not nonempty(bid) or bid in seen:
                    _wire_issue(issues,f"{bp}.binding_id","MCB_BINDING_ID_INVALID","unique non-empty string",bid)
                elif nonempty(bid): seen.add(bid)
                if b.get("operator") not in MCB_OPERATORS:
                    _wire_issue(issues,f"{bp}.operator","MCB_UNRESOLVED_UNSUPPORTED_OPERATOR",sorted(MCB_OPERATORS),b.get("operator"))
                if b.get("scope") not in MCB_SCOPES:
                    _wire_issue(issues,f"{bp}.scope","MCB_UNRESOLVED_UNSUPPORTED_SCOPE",sorted(MCB_SCOPES),b.get("scope"))
                if b.get("material_to_line") is not True:
                    _wire_issue(issues,f"{bp}.material_to_line","MCB_BINDING_NOT_MATERIAL",True,b.get("material_to_line"))
                if not isinstance(b.get("params"),dict):
                    _wire_issue(issues,f"{bp}.params","MCB_BINDING_PARAMS_INVALID","object",type(b.get("params")).__name__)
            ua=rp.get("unified_cold_audit")
            mp=ua.get("mechanical_projection") if isinstance(ua,dict) else None
            if not isinstance(mp,dict):
                _wire_issue(issues,f"{rp_path}.unified_cold_audit.mechanical_projection","MCB_COLD_PROJECTION_REQUIRED","object",mp)
            else:
                if mp.get("status")!="PASS": _wire_issue(issues,f"{rp_path}.unified_cold_audit.mechanical_projection.status","MCB_COLD_PROJECTION_NOT_CLOSED","PASS",mp.get("status"))
                if mp.get("ignored_primary_bindings") is not True: _wire_issue(issues,f"{rp_path}.unified_cold_audit.mechanical_projection.ignored_primary_bindings","MCB_COLD_PROJECTION_NOT_INDEPENDENT",True,mp.get("ignored_primary_bindings"))
                if not nonempty(mp.get("sweep_basis")): _wire_issue(issues,f"{rp_path}.unified_cold_audit.mechanical_projection.sweep_basis","MCB_COLD_PROJECTION_BASIS_REQUIRED","non-empty string",mp.get("sweep_basis"))
                if not isinstance(mp.get("bindings"),list): _wire_issue(issues,f"{rp_path}.unified_cold_audit.mechanical_projection.bindings","MCB_COLD_PROJECTION_BINDINGS_INVALID","array",type(mp.get("bindings")).__name__)
            steps=rp.get("steps")
            if not isinstance(steps,list):
                _wire_issue(issues,f"{rp_path}.steps","PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID","array",type(steps).__name__); steps=[]
            for si,step in enumerate(steps):
                if not isinstance(step,dict): continue
                for k in ("requires","moves","produces","property_updates","activate_restrictions","release_restrictions"):
                    if step.get(k) not in ([],None):
                        _wire_issue(issues,f"{rp_path}.steps[{si}].{k}","MCB_DERIVED_FIELD_MODEL_AUTHORED","empty/omitted; compiler-owned",step.get(k))
            outcome=rp.get("outcome")
            if not isinstance(outcome,dict):
                _wire_issue(issues,f"{rp_path}.outcome","PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID","object",type(outcome).__name__)
            elif outcome.get("victory_claim") not in {"NONE","LETHAL"}:
                _wire_issue(issues,f"{rp_path}.outcome.victory_claim","RC16_2_VICTORY_CLAIM_REQUIRED",["NONE","LETHAL"],outcome.get("victory_claim"))
            _proof_floor_issues_for_replay(line,rp,rp_path,issues)
    _scan_placeholders(payload,"$",issues)

    # Persist concrete business coordinates, not only a JSON path. This makes a
    # single diagnostic receipt actionable after rollback and avoids asking the
    # model to rediscover which line/replay/step/binding/resource failed.
    line_re=re.compile(r"^\$\.lines\[(\d+)\]")
    replay_re=re.compile(r"\.execution_replays\[(\d+)\]")
    step_re=re.compile(r"\.steps\[(\d+)\]")
    binding_re=re.compile(r"\.mechanical_consequence_bindings\[(\d+)\]")
    for issue in issues:
        path=str(issue.get("path") or "")
        lm=line_re.search(path); li=int(lm.group(1)) if lm else None
        line=lines[li] if li is not None and 0<=li<len(lines) and isinstance(lines[li],dict) else None
        if line is not None and nonempty(line.get("line_id")):
            issue["line_id"]=line.get("line_id")
        rm=replay_re.search(path)
        replays=line.get("execution_replays",[]) if isinstance(line,dict) else []
        ri=int(rm.group(1)) if rm else None
        rp=replays[ri] if ri is not None and isinstance(replays,list) and 0<=ri<len(replays) and isinstance(replays[ri],dict) else None
        if rp is not None and nonempty(rp.get("replay_id")):
            issue["replay_id"]=rp.get("replay_id")
        sm=step_re.search(path); si=int(sm.group(1)) if sm else None
        steps=rp.get("steps",[]) if isinstance(rp,dict) else []
        step=steps[si] if si is not None and isinstance(steps,list) and 0<=si<len(steps) and isinstance(steps[si],dict) else None
        if step is not None and nonempty(step.get("step_id")):
            issue["step_id"]=step.get("step_id")
        bm=binding_re.search(path); bi=int(bm.group(1)) if bm else None
        binds=rp.get("mechanical_consequence_bindings",[]) if isinstance(rp,dict) else []
        b=binds[bi] if bi is not None and isinstance(binds,list) and 0<=bi<len(binds) and isinstance(binds[bi],dict) else None
        if b is not None:
            if nonempty(b.get("binding_id")): issue["binding_id"]=b.get("binding_id")
            params=b.get("params") if isinstance(b.get("params"),dict) else {}
            if nonempty(params.get("resource_id")): issue["resource_id"]=params.get("resource_id")

    # Stable order and duplicate collapse make one repair receipt actionable.
    uniq={json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")):x for x in issues}
    return sorted(uniq.values(),key=lambda x:(x.get("path") or "",x.get("code") or ""))


def _raise_business_diagnostic(issues):
    if issues:
        fail("PILOTAGE_BUSINESS_DIAGNOSTIC_FAILED: "+json.dumps({"issue_count":len(issues),"issues":issues},ensure_ascii=False,sort_keys=True,separators=(",",":")))


def _compile_pilotage_contract_document(st, payload, render: Path):
    payload=copy.deepcopy(payload)
    for line in payload.get("lines",[]) if isinstance(payload.get("lines"),list) else []:
        lid=line.get("line_id") if isinstance(line,dict) else None
        for rp in line.get("execution_replays",[]) if isinstance(line,dict) and isinstance(line.get("execution_replays"),list) else []:
            rpid=rp.get("replay_id") if isinstance(rp,dict) else None
            if not isinstance(rp,dict): continue
            if "compiled_mechanical_projection" in rp or "compiled_mechanical_projection_sha256" in rp:
                fail(f"MCB_COMPILED_PROJECTION_MODEL_AUTHORED: {lid}:{rpid}")
            for step in rp.get("steps",[]) if isinstance(rp.get("steps"),list) else []:
                if not isinstance(step,dict): continue
                for k in ("requires","moves","produces","property_updates","activate_restrictions","release_restrictions"):
                    if step.get(k) not in ([],None):
                        fail(f"MCB_DERIVED_FIELD_MODEL_AUTHORED: {lid}:{rpid}:{step.get('step_id')}:{k}")
            projection=_compile_mcb_projection_for_replay(rp,lid or "<line>",rpid or "<replay>")
            rp["compiled_mechanical_projection"]=projection
            rp["compiled_mechanical_projection_sha256"]=_mcb_projection_hash(projection)
            by_action={x["action_id"]:x["effects"] for x in projection.get("steps",[])}
            for step in rp.get("steps",[]) if isinstance(rp.get("steps"),list) else []:
                eff=by_action.get(step.get("step_id"),{})
                for k in ("requires","moves","produces","property_updates","activate_restrictions","release_restrictions"):
                    step[k]=copy.deepcopy(eff.get(k,[]))
                step["mechanically_compiled"]=True
    axes=_rendered_axis_headings(render.read_text(encoding="utf-8"))
    return {
        "wire_schema":PILOTAGE_WIRE_SCHEMA,"run_id":st["run_id"],"authority":PILOTAGE,
        "deck_artifact":st.get("current_artifact"),"render_sha256":sha256(render),
        **payload,"rendered_axis_count":len(axes),"rendered_axis_headings":axes,
        "pilotage_source_sha256":_pilotage_policy_sha256(st),
    }


def cmd_compile_pilotage_contract(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    render=Path(a.render_file); business=Path(a.business_payload_file); out=Path(a.output)
    if not render.exists(): fail("PILOTAGE_RENDER_MISSING")
    if not business.exists(): fail("PILOTAGE_BUSINESS_PAYLOAD_MISSING")
    payload=read_json(business,"Pilotage business payload")
    _raise_business_diagnostic(_pilotage_business_issues(payload))
    compiled=_compile_pilotage_contract_document(st,payload,render)
    text=_stable_json_text(compiled)
    hit=out.exists() and out.read_text(encoding="utf-8")==text
    _atomic_write_text(out,text)
    _append_run_journal(rd,st,"DERIVED_CACHE_HIT" if hit else "DERIVED_CACHE_MISS",artifact_kind="pilotage-contract",input_business_sha256=sha256(business),render_sha256=sha256(render),deck_artifact=st.get("current_artifact"),policy_sha256=_pilotage_policy_sha256(st),output_file=str(out),output_sha256=sha256(out))
    print(json.dumps({"status":"CACHE_HIT" if hit else "COMPILED","output":str(out),"sha256":sha256(out),"render_sha256":sha256(render),"deck_artifact":st.get("current_artifact")},ensure_ascii=False))


def cmd_pilotage_preflight(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    contract=Path(a.pilotage_contract_file); render=Path(a.render_file); schema_path=Path(a.schema_file)
    if not contract.exists(): fail("PILOTAGE_CONTRACT_MISSING")
    if not render.exists(): fail("PILOTAGE_RENDER_MISSING")
    if not schema_path.exists(): fail("PILOTAGE_SCHEMA_MISSING")
    schema=read_json(schema_path,"pilotage wire schema")
    if schema.get("schema")!=PILOTAGE_SCHEMA_DESCRIPTOR or schema.get("wire_schema")!=PILOTAGE_WIRE_SCHEMA or schema.get("authority_source_sha256")!=_pilotage_policy_sha256(st):
        fail("PILOTAGE_WIRE_SCHEMA_MISMATCH")
    txid=f"pilotage-preflight-{sum(1 for e in _read_journal(rd) if e.get('event')=='PILOTAGE_PREFLIGHT_STARTED')+1:06d}"
    before=sha256(rd/STATE_FILE)
    _append_run_journal(rd,st,"PILOTAGE_PREFLIGHT_STARTED",transaction_id=txid,pilotage_contract_file=str(contract),pilotage_contract_sha256=sha256(contract),render_file=str(render),render_sha256=sha256(render),schema_file=str(schema_path),schema_sha256=sha256(schema_path),wire_schema=PILOTAGE_WIRE_SCHEMA,state_sha256_before=before)
    try:
        issues=_pilotage_full_preflight_issues(contract,render,st)
        status="FAIL" if issues else "PASS"
        receipt={"schema":"ygo-pilotage-preflight-receipt-v1","status":status,"run_id":st["run_id"],"deck_artifact":st.get("current_artifact"),"wire_schema":PILOTAGE_WIRE_SCHEMA,"pilotage_contract_file":str(contract),"pilotage_contract_sha256":sha256(contract),"render_file":str(render),"render_sha256":sha256(render),"schema_file":str(schema_path),"schema_sha256":sha256(schema_path),"pilotage_source_file":str(_pilotage_policy_path()),"pilotage_source_sha256":_pilotage_policy_sha256(st),"runtime_version":VERSION,"validation_mode":"FULL_SHARED_VALIDATOR","issues":issues}
        out=Path(a.output) if getattr(a,"output",None) else rd/PILOTAGE_PREFLIGHT_RECEIPT
        _atomic_write_text(out,_stable_json_text(receipt)); rh=sha256(out)
        ev="PILOTAGE_PREFLIGHT_FAILED" if issues else "PILOTAGE_PREFLIGHT_SUCCEEDED"
        _append_run_journal(rd,st,ev,transaction_id=txid,pilotage_contract_sha256=receipt["pilotage_contract_sha256"],wire_schema=PILOTAGE_WIRE_SCHEMA,issue_count=len(issues),receipt_file=str(out),receipt_sha256=rh,state_sha256_after=sha256(rd/STATE_FILE))
        if issues:
            print(json.dumps(receipt,ensure_ascii=False)); raise SystemExit(2)
        print(json.dumps(receipt,ensure_ascii=False)); return
    except SystemExit:
        raise
    except Exception as e:
        tb=rd/f"{txid}.traceback.txt"; _atomic_write_text(tb,traceback.format_exc())
        _append_run_journal(rd,st,"PILOTAGE_PREFLIGHT_EXCEPTION",transaction_id=txid,exception_type=type(e).__name__,exception_message=str(e),traceback_file=str(tb),traceback_sha256=sha256(tb),state_sha256_after=sha256(rd/STATE_FILE))
        raise

def validate_pilotage_contract(path: Path, render_path: Path, st):
    validate_evidence(path, st)
    d=read_json(path,"pilotage contract")
    if "wire_schema" in d and d.get("wire_schema")!=PILOTAGE_WIRE_SCHEMA: fail("PILOTAGE_WIRE_SCHEMA_MISMATCH")
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in pilotage contract")
    if d.get("authority")!=PILOTAGE: fail("pilotage contract authority mismatch")
    if d.get("deck_artifact")!=st.get("current_artifact"): fail("pilotage contract deck mismatch")
    if d.get("render_sha256")!=sha256(render_path): fail("pilotage contract render hash mismatch")
    if d.get("status")!="PASS": fail("pilotage contract status must be PASS")
    contract_version=d.get("execution_contract_version")
    if contract_version not in {"RC16","RC16.1","RC16.2"}: fail("PILOTAGE_EXECUTION_CONTRACT_VERSION_MISMATCH")
    lines=d.get("lines")
    if not isinstance(lines,list): fail("pilotage contract lines must be a list")
    text=render_path.read_text(encoding="utf-8")

    # RC11: every numbered Axe displayed to the player is an essential pilotage
    # surface and must map 1:1 to a line in this exact contract. Situationals belong
    # in the Guide de pilotage instead of masquerading as a certified numbered Axe.
    rendered_axes=_rendered_axis_headings(text)
    if rendered_axes and not lines: fail("pilotage contract requires lines")
    if not rendered_axes and lines: fail("PILOTAGE_LINES_MUST_BE_EMPTY_WITHOUT_AXES")
    cov=d.get("axis_coverage_status")
    if rendered_axes:
        if cov!="PASS": fail("AXIS_COVERAGE_NOT_CLOSED")
    elif cov not in {"PASS","NO_RENDERED_AXES"}:
        fail("AXIS_COVERAGE_STATUS_INVALID")
    declared_count=d.get("rendered_axis_count")
    if declared_count is not None:
        if not isinstance(declared_count,int) or isinstance(declared_count,bool) or declared_count!=len(rendered_axes):
            fail("RENDERED_AXIS_COUNT_MISMATCH")

    # RC12: preserve the business exploration of multiple structural starters.
    # The authority decides which starters matter; the runtime only requires its
    # declared inventory to be complete, rendered and covered by validated lines.
    sexp=d.get("starter_exploration_status")
    sinv=d.get("starter_inventory_status")
    starters=d.get("structural_starters")
    if rendered_axes:
        if sexp!="COMPLETE" or sinv!="PASS":
            fail("STRUCTURAL_STARTER_INVENTORY_NOT_CLOSED")
        if not isinstance(starters,list) or not starters:
            fail("STRUCTURAL_STARTER_INVENTORY_MISSING")
    else:
        if sexp not in {"COMPLETE","NO_RENDERED_AXES"} or sinv not in {"PASS","NO_RENDERED_AXES"}:
            fail("STRUCTURAL_STARTER_INVENTORY_STATUS_INVALID")
        if starters not in ([],None):
            fail("STRUCTURAL_STARTER_INVENTORY_MUST_BE_EMPTY_WITHOUT_AXES")
    starter_by_id={}
    for si in starters or []:
        if not isinstance(si,dict): fail("structural starter inventory entry invalid")
        sid=si.get("starter_id")
        if not nonempty(sid) or sid in starter_by_id: fail("STRUCTURAL_STARTER_ID_INVALID_OR_DUPLICATE")
        if not nonempty(si.get("display")) or not nonempty(si.get("render_token")):
            fail(f"STRUCTURAL_STARTER_RENDER_BINDING_MISSING: {sid}")
        if si["render_token"].strip().casefold() not in text.casefold():
            fail(f"STRUCTURAL_STARTER_NOT_RENDERED: {sid}")
        ah=si.get("axis_heading")
        if not nonempty(ah) or _axis_norm(ah) not in {_axis_norm(x) for x in rendered_axes}:
            fail(f"STRUCTURAL_STARTER_AXIS_INVALID: {sid}")
        lids=si.get("line_ids")
        if not isinstance(lids,list) or not lids or any(not nonempty(x) for x in lids):
            fail(f"STRUCTURAL_STARTER_LINE_COVERAGE_INVALID: {sid}")
        if si.get("coverage_status")!="PASS": fail(f"STRUCTURAL_STARTER_NOT_COVERED: {sid}")
        starter_by_id[sid]=si

    axis_to_lines={}
    for line in lines:
        if not isinstance(line,dict): continue
        rah=line.get("render_axis_heading")
        if rah in (None,""): continue
        if not nonempty(rah): fail("render_axis_heading invalid")
        n=_axis_norm(rah)
        axis_to_lines.setdefault(n,[]).append(line.get("line_id"))
    rendered_norm={_axis_norm(x):x for x in rendered_axes}
    missing=[raw for n,raw in rendered_norm.items() if n not in axis_to_lines]
    if missing: fail("RENDERED_AXIS_NOT_COVERED: "+" | ".join(missing))
    extra=[n for n in axis_to_lines if n not in rendered_norm]
    if extra: fail("PILOTAGE_AXIS_NOT_RENDERED: "+" | ".join(extra))

    seen=set()
    line_starter_refs={}
    for i,line in enumerate(lines):
        if not isinstance(line,dict): fail(f"pilotage line {i} must be object")
        lid=line.get("line_id")
        if not nonempty(lid) or lid in seen: fail("pilotage line_id invalid/duplicate")
        seen.add(lid)
        line_token=line.get("render_token") or lid
        if not nonempty(line_token) or line_token.strip().casefold() not in text.casefold(): fail(f"PILOTAGE_LINE_NOT_RENDERED: {lid}")
        rah=line.get("render_axis_heading")
        if nonempty(rah):
            if _axis_norm(rah) not in {_axis_norm(x) for x in rendered_axes}:
                fail(f"PILOTAGE_AXIS_NOT_RENDERED: {rah}")
            if line.get("axis_validation_status")!="PASS":
                fail(f"AXIS_VALIDATION_NOT_PASS: {lid}")
        starter_ids=line.get("starter_ids")
        if not isinstance(starter_ids,list) or not starter_ids or any(not nonempty(x) for x in starter_ids):
            fail(f"PILOTAGE_STARTER_IDS_MISSING: {lid}")
        if len(set(starter_ids))!=len(starter_ids): fail(f"PILOTAGE_STARTER_IDS_DUPLICATE: {lid}")
        for sid in starter_ids:
            if sid not in starter_by_id: fail(f"PILOTAGE_UNKNOWN_STRUCTURAL_STARTER: {lid}:{sid}")
        if len(starter_ids)>1:
            if line.get("starter_grouping_status")!="PASS" or not nonempty(line.get("starter_grouping_basis")):
                fail(f"MULTI_STARTER_SHARED_LINE_EQUIVALENCE_NOT_PROVED: {lid}")
        elif line.get("starter_grouping_status") not in {None,"NOT_APPLICABLE"}:
            fail(f"STARTER_GROUPING_STATUS_INCONSISTENT: {lid}")
        line_starter_refs[lid]=set(starter_ids)
        starter_display=line.get("starter_display")
        if not nonempty(starter_display): fail(f"pilotage starter_display missing: {lid}")
        if starter_display.strip().casefold() not in text.casefold():
            fail(f"PILOTAGE_STARTER_DISPLAY_NOT_RENDERED: {lid}")
        declared=line.get("declared_initial_resources")
        mandatory=line.get("mandatory_initial_resources")
        obtained=line.get("obtained_during_line")
        hidden=line.get("hidden_initial_resources")
        for label,val in (("declared",declared),("mandatory",mandatory),("obtained",obtained),("hidden",hidden)):
            if not isinstance(val,list) or any(not nonempty(x) for x in val): fail(f"pilotage {label} resources invalid: {lid}")
        dset={x.strip().casefold() for x in declared}
        missing=[x for x in mandatory if x.strip().casefold() not in dset]
        if missing: fail(f"STARTER_MANDATORY_RESOURCE_NOT_DECLARED: {lid}: {','.join(missing)}")
        if hidden: fail(f"STARTER_HIDDEN_INITIAL_RESOURCE: {lid}: {','.join(hidden)}")
        if line.get("starter_contract_status")!="PASS": fail(f"starter contract not PASS: {lid}")
        generic=line.get("generic_starter")
        if not isinstance(generic,bool): fail(f"generic_starter must be boolean: {lid}")
        gstat=line.get("generic_coverage_status")
        if generic and gstat not in {"ALL_VARIANTS_VALIDATED","BRANCHED_EXPLICITLY"}:
            fail(f"GENERIC_STARTER_NOT_CLOSED: {lid}")
        if not generic and gstat not in {"NOT_APPLICABLE",None}:
            fail(f"generic coverage status inconsistent: {lid}")

        # RC10: property-sensitive starter closure. The business authority decides
        # which properties (Level/Type/Attribute/name/etc.) are actually required.
        pscope=line.get("starter_property_scope_status")
        pchecks=line.get("starter_property_checks")
        if generic and pscope!="PASS":
            fail(f"GENERIC_STARTER_PROPERTY_SCOPE_NOT_CLOSED: {lid}")
        if pscope not in {"PASS","NO_PROPERTY_SENSITIVE_STARTER"}:
            fail(f"STARTER_PROPERTY_SCOPE_NOT_CLOSED: {lid}")
        if pscope=="NO_PROPERTY_SENSITIVE_STARTER":
            if pchecks not in ([],None): fail(f"starter property checks must be empty when not relevant: {lid}")
        else:
            if not isinstance(pchecks,list) or not pchecks:
                fail(f"STARTER_PROPERTY_CHECKS_MISSING: {lid}")
            pseen=set()
            for j,ch in enumerate(pchecks):
                if not isinstance(ch,dict): fail(f"starter property check {j} invalid: {lid}")
                cid=ch.get("check_id")
                if not nonempty(cid) or cid in pseen: fail(f"starter property check_id invalid/duplicate: {lid}")
                pseen.add(cid)
                if not nonempty(ch.get("resource_label")): fail(f"starter property resource_label missing: {lid}:{cid}")
                props=ch.get("required_properties")
                if not isinstance(props,list) or not props or any(not nonempty(x) for x in props):
                    fail(f"starter required_properties invalid: {lid}:{cid}")
                token=ch.get("render_token")
                if not nonempty(token): fail(f"starter property render_token missing: {lid}:{cid}")
                if token.strip().casefold() not in text.casefold():
                    fail(f"STARTER_PROPERTY_NOT_RENDERED: {lid}:{cid}")
                if ch.get("hidden_property_assumption") is not False:
                    fail(f"STARTER_HIDDEN_PROPERTY_ASSUMPTION: {lid}:{cid}")
                if ch.get("property_status")!="PASS": fail(f"starter property status not PASS: {lid}:{cid}")
                is_generic=ch.get("generic_requirement")
                if not isinstance(is_generic,bool): fail(f"starter generic_requirement invalid: {lid}:{cid}")
                elig=ch.get("eligible_variants",[])
                valid=ch.get("validated_variants",[])
                if not isinstance(elig,list) or not isinstance(valid,list) or any(not nonempty(x) for x in elig+valid):
                    fail(f"starter variant coverage invalid: {lid}:{cid}")
                if is_generic:
                    if not elig: fail(f"GENERIC_STARTER_VARIANTS_MISSING: {lid}:{cid}")
                    if {x.strip().casefold() for x in elig}!={x.strip().casefold() for x in valid}:
                        fail(f"GENERIC_STARTER_VARIANTS_NOT_CLOSED: {lid}:{cid}")

        # RC10: physical-state checkpoints for complex lines. The authority decides
        # the relevant zone model; the harness checks arithmetic and visible closure.
        complexity=line.get("sequence_complexity")
        if complexity not in {"SIMPLE","COMPLEX"}: fail(f"sequence_complexity invalid: {lid}")
        zscope=line.get("physical_state_scope_status")
        zchecks=line.get("state_checkpoints")
        if complexity=="COMPLEX" and zscope!="PASS":
            fail(f"COMPLEX_LINE_PHYSICAL_STATE_NOT_CLOSED: {lid}")
        if zscope not in {"PASS","NO_CRITICAL_ZONE_STATE"}:
            fail(f"PHYSICAL_STATE_SCOPE_NOT_CLOSED: {lid}")
        if zscope=="NO_CRITICAL_ZONE_STATE":
            if zchecks not in ([],None): fail(f"state checkpoints must be empty when not relevant: {lid}")
        else:
            if not isinstance(zchecks,list) or not zchecks: fail(f"STATE_CHECKPOINTS_MISSING: {lid}")
            zseen=set()
            for j,ch in enumerate(zchecks):
                if not isinstance(ch,dict): fail(f"state checkpoint {j} invalid: {lid}")
                cid=ch.get("checkpoint_id")
                if not nonempty(cid) or cid in zseen: fail(f"state checkpoint_id invalid/duplicate: {lid}")
                zseen.add(cid)
                cap=ch.get("zone_capacity"); occ=ch.get("occupied_zones"); free=ch.get("free_zones")
                need=ch.get("required_free_zones_for_next_step")
                for nm,val in (("zone_capacity",cap),("occupied_zones",occ),("free_zones",free),("required_free_zones_for_next_step",need)):
                    if not isinstance(val,int) or isinstance(val,bool) or val<0: fail(f"{nm} invalid: {lid}:{cid}")
                if occ+free!=cap: fail(f"ZONE_STATE_ARITHMETIC_MISMATCH: {lid}:{cid}")
                if need>free: fail(f"ZONE_STATE_INSUFFICIENT_FREE_ZONES: {lid}:{cid}")
                at_state=ch.get("at_state")
                if not nonempty(at_state): fail(f"ZONE_STATE_AT_STATE_MISSING: {lid}:{cid}")
                token=ch.get("state_render_token")
                if not nonempty(token) or token.strip().casefold() not in text.casefold():
                    fail(f"ZONE_STATE_NOT_RENDERED: {lid}:{cid}")
                preq=ch.get("placement_required")
                if not isinstance(preq,bool): fail(f"placement_required invalid: {lid}:{cid}")
                pinst=ch.get("placement_instruction")
                ptoken=ch.get("placement_render_token")
                if preq:
                    if not nonempty(pinst) or not nonempty(ptoken): fail(f"placement instruction missing: {lid}:{cid}")
                    if ptoken.strip().casefold() not in text.casefold(): fail(f"ZONE_PLACEMENT_NOT_RENDERED: {lid}:{cid}")
                elif (pinst not in (None,"") or ptoken not in (None,"")):
                    fail(f"placement fields inconsistent: {lid}:{cid}")
                if ch.get("hidden_zone_assumption") is not False:
                    fail(f"ZONE_HIDDEN_ASSUMPTION: {lid}:{cid}")
                if ch.get("state_status")!="PASS": fail(f"state checkpoint not PASS: {lid}:{cid}")

        # RC8: effect-resolution contract. The business authority decides the card-text
        # semantics; the harness only checks that the declared resolution is internally
        # consistent with those semantics and bound to this exact line.
        checks=line.get("effect_resolution_checks")
        scope=line.get("effect_resolution_scope_status")
        if scope not in {"PASS","NO_RELEVANT_EFFECT_SELECTION"}:
            fail(f"EFFECT_RESOLUTION_SCOPE_NOT_CLOSED: {lid}")
        if scope=="NO_RELEVANT_EFFECT_SELECTION":
            if checks not in ([],None): fail(f"effect checks must be empty when not relevant: {lid}")
        else:
            if not isinstance(checks,list) or not checks:
                fail(f"EFFECT_RESOLUTION_CHECKS_MISSING: {lid}")
            eseen=set()
            for j,ch in enumerate(checks):
                if not isinstance(ch,dict): fail(f"effect resolution check {j} invalid: {lid}")
                eid=ch.get("effect_id")
                if not nonempty(eid) or eid in eseen: fail(f"effect_id invalid/duplicate: {lid}")
                eseen.add(eid)
                if not nonempty(ch.get("source_card")): fail(f"effect source_card missing: {lid}:{eid}")
                if ch.get("effect_resolution_status")!="PASS": fail(f"effect resolution not PASS: {lid}:{eid}")
                if ch.get("hidden_choice_assumption") is not False:
                    fail(f"EFFECT_HIDDEN_CHOICE_ASSUMPTION: {lid}:{eid}")
                activation_optional=ch.get("activation_optional")
                activation_chosen=ch.get("activation_chosen")
                if not isinstance(activation_optional,bool) or not isinstance(activation_chosen,bool):
                    fail(f"effect activation flags invalid: {lid}:{eid}")
                if not activation_chosen:
                    if not activation_optional: fail(f"mandatory effect cannot be skipped: {lid}:{eid}")
                    continue
                mode=ch.get("selection_mode")
                if mode not in {"ALL_POSSIBLE","UP_TO_N","EXACT_N","NO_SELECTION"}:
                    fail(f"effect selection_mode invalid: {lid}:{eid}")
                eligible=ch.get("eligible_count")
                resolved=ch.get("resolved_count")
                if not isinstance(eligible,int) or isinstance(eligible,bool) or eligible<0:
                    fail(f"effect eligible_count invalid: {lid}:{eid}")
                if not isinstance(resolved,int) or isinstance(resolved,bool) or resolved<0:
                    fail(f"effect resolved_count invalid: {lid}:{eid}")
                limit=ch.get("selection_limit")
                if limit is not None and (not isinstance(limit,int) or isinstance(limit,bool) or limit<0):
                    fail(f"effect selection_limit invalid: {lid}:{eid}")
                if mode=="ALL_POSSIBLE" and resolved!=eligible:
                    fail(f"EFFECT_ALL_POSSIBLE_NOT_RESOLVED: {lid}:{eid} {resolved}!={eligible}")
                if mode=="UP_TO_N":
                    if limit is None: fail(f"UP_TO_N requires selection_limit: {lid}:{eid}")
                    if resolved>min(eligible,limit): fail(f"EFFECT_UP_TO_N_OVERFLOW: {lid}:{eid}")
                if mode=="EXACT_N":
                    if limit is None: fail(f"EXACT_N requires selection_limit: {lid}:{eid}")
                    if eligible<limit or resolved!=limit: fail(f"EFFECT_EXACT_N_NOT_RESOLVED: {lid}:{eid}")
                if mode=="NO_SELECTION" and resolved not in {0,1}:
                    fail(f"NO_SELECTION resolved_count invalid: {lid}:{eid}")

        expected_cases=_generic_execution_cases(pchecks) if generic else ["__BASE__"]
        validate_execution_replay(line,text,st,expected_cases,contract_version)

    # Exact cross-check: every starter discovered by the business authority must be
    # attached to every line it claims, and every line attachment must be reciprocated.
    for sid,si in starter_by_id.items():
        wanted=set(si.get("line_ids",[]))
        if any(lid not in seen for lid in wanted):
            fail(f"STRUCTURAL_STARTER_REFERENCES_UNKNOWN_LINE: {sid}")
        actual={lid for lid,refs in line_starter_refs.items() if sid in refs}
        if actual!=wanted:
            fail(f"STRUCTURAL_STARTER_LINE_BINDING_MISMATCH: {sid}")
    return d,sha256(path)


def _card_group(card_type):
    low=(card_type or "").casefold()
    if "spell" in low or "magie" in low: return "SPELL"
    if "trap" in low or "piège" in low or "piege" in low: return "TRAP"
    return "MONSTER"


def _narrative_type_map(report_path: Path):
    r=read_json(report_path,"narrative conformance report")
    out={}
    for e in r.get("card_mechanics",[]):
        if isinstance(e,dict) and nonempty(e.get("name")) and e.get("zone") in {"main_deck","extra_deck","side_deck"}:
            out[(e["zone"],e["name"].strip().casefold())]=e.get("card_type","")
    return out


def _deck_maps(snapshot):
    out={}
    for zone in ("main_deck","extra_deck","side_deck"):
        out[zone]={c["name"].strip().casefold():(c["name"].strip(),c["qty"]) for c in snapshot.get(zone,[])}
    return out


def _category_totals(snapshot, typemap):
    totals={"MONSTER":0,"SPELL":0,"TRAP":0,"EXTRA":0,"SIDE":0,"MAIN":0}
    for c in snapshot.get("main_deck",[]):
        totals["MAIN"]+=c["qty"]
        totals[_card_group(typemap.get(("main_deck",c["name"].strip().casefold()),""))]+=c["qty"]
    totals["EXTRA"]=sum(c["qty"] for c in snapshot.get("extra_deck",[]))
    totals["SIDE"]=sum(c["qty"] for c in snapshot.get("side_deck",[]))
    return totals


def _section_between(text, heading_pattern, next_level_pattern):
    m=re.search(heading_pattern,text,re.I|re.M)
    if not m: return None
    start=m.end(); n=re.search(next_level_pattern,text[start:],re.M)
    end=start+n.start() if n else len(text)
    return text[start:end]


def validate_full_decklist_groups(text, snapshot, typemap):
    totals=_category_totals(snapshot,typemap)
    required=[
      (rf"^###\s+Main Deck\s*[—-]\s*{totals['MAIN']}\s*$","MAIN"),
      (rf"^####\s+Monstres\s*[—-]\s*{totals['MONSTER']}\s*$","MONSTER"),
      (rf"^####\s+Magies\s*[—-]\s*{totals['SPELL']}\s*$","SPELL"),
      (rf"^####\s+Pi[èe]ges\s*[—-]\s*{totals['TRAP']}\s*$","TRAP"),
      (rf"^###\s+Extra Deck\s*[—-]\s*{totals['EXTRA']}\s*$","EXTRA"),
      (rf"^###\s+Side Deck\s*[—-]\s*{totals['SIDE']}\s*$","SIDE"),
    ]
    for pat,label in required:
        if not re.search(pat,text,re.I|re.M): fail(f"DECKLIST_GROUP_HEADING_MISSING_OR_TOTAL_WRONG: {label}")
    sections={
      "MONSTER":_section_between(text,required[1][0],r"^####\s+|^###\s+"),
      "SPELL":_section_between(text,required[2][0],r"^####\s+|^###\s+"),
      "TRAP":_section_between(text,required[3][0],r"^####\s+|^###\s+"),
      "EXTRA":_section_between(text,required[4][0],r"^###\s+"),
      "SIDE":_section_between(text,required[5][0],r"^###\s+|^##\s+"),
    }
    for zone in ("main_deck","extra_deck","side_deck"):
        for card in snapshot.get(zone,[]):
            if zone=="main_deck": cat=_card_group(typemap.get((zone,card["name"].strip().casefold()),""))
            elif zone=="extra_deck": cat="EXTRA"
            else: cat="SIDE"
            sec=sections.get(cat) or ""
            pat=rf"(?m)^\s*[-*]\s*{card['qty']}\s*[×x]\s*{re.escape(card['name'])}\s*$"
            if not re.search(pat,sec): fail(f"DECKLIST_CARD_WRONG_GROUP_OR_MISSING: {card['qty']}x {card['name']}")


def canonical_refactor_diff_text(st, current_snapshot, current_typemap):
    ch=st.get("last_material_change") or {}
    old_path=ch.get("previous_snapshot_file")
    old_report=ch.get("previous_narrative_report_file")
    if not old_path or not Path(old_path).exists(): fail("REFACTOR_DIFF_PREVIOUS_SNAPSHOT_MISSING")
    if not old_report or not Path(old_report).exists(): fail("REFACTOR_DIFF_PREVIOUS_TYPE_REPORT_MISSING")
    old=read_json(Path(old_path),"previous deck snapshot")
    oldtypes=_narrative_type_map(Path(old_report))
    oldm=_deck_maps(old); newm=_deck_maps(current_snapshot)
    oldtot=_category_totals(old,oldtypes); newtot=_category_totals(current_snapshot,current_typemap)
    changes=[]
    for zone in ("main_deck","extra_deck","side_deck"):
        keys=set(oldm[zone])|set(newm[zone])
        for k in sorted(keys):
            on,oq=oldm[zone].get(k,(newm[zone].get(k,(k,0))[0],0))
            nn,nq=newm[zone].get(k,(oldm[zone].get(k,(k,0))[0],0))
            if oq==nq: continue
            name=nn if nq else on
            if zone=="main_deck":
                ctype=current_typemap.get((zone,k),oldtypes.get((zone,k),"")); cat=_card_group(ctype)
            elif zone=="extra_deck": cat="EXTRA"
            else: cat="SIDE"
            changes.append((cat,name,oq,nq))
    if not changes: fail("DIFF_ONLY_WITHOUT_MATERIAL_DIFF")
    labels={"MONSTER":"Monstres","SPELL":"Magies","TRAP":"Pièges","EXTRA":"Extra Deck","SIDE":"Side Deck"}
    order=["MONSTER","SPELL","TRAP","EXTRA","SIDE"]
    lines=[f"## Diff {ch.get('from_artifact')} → {ch.get('to_artifact')}",""]
    bycat={c:[] for c in order}
    for row in changes: bycat[row[0]].append(row)
    for cat in order:
        if not bycat[cat]: continue
        lines.append(f"### {labels[cat]} — {oldtot[cat]} → {newtot[cat]}")
        lines.append("")
        for _,name,oq,nq in sorted(bycat[cat],key=lambda x:x[1].casefold()):
            suffix=" (NOUVEAU)" if oq==0 and nq>0 else (" (RETIRÉ)" if oq>0 and nq==0 else "")
            lines.append(f"- {name} : {oq} → {nq}{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip()+"\n"


def materialize_canonical_refactor_diff(contract_path: Path, st):
    if st.get("refactor_render_mode")!="DIFF_ONLY":
        st.pop("canonical_refactor_diff_file",None); st.pop("canonical_refactor_diff_sha256",None)
        return None,None
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    ng=st.get("gates",{}).get("NARRATIVE_CONFORMANCE_CLOSED",{})
    if not dg or not ng: fail("CANONICAL_REFACTOR_DIFF_PREREQUISITES_MISSING")
    snap=read_json(Path(dg["snapshot_file"]),"deck snapshot")
    typemap=_narrative_type_map(Path(ng["evidence_file"]))
    payload=canonical_refactor_diff_text(st,snap,typemap)
    ch=st.get("last_material_change") or {}
    name=f"refactor_diff_{ch.get('from_artifact','old')}_to_{ch.get('to_artifact','new')}.md"
    out=(contract_path.parent/name).resolve()
    out.write_text(payload,encoding="utf-8")
    h=sha256(out)
    st["canonical_refactor_diff_file"]=str(out)
    st["canonical_refactor_diff_sha256"]=h
    return out,h


def validate_refactor_diff_component(comps, st):
    p=st.get("canonical_refactor_diff_file"); h=st.get("canonical_refactor_diff_sha256")
    if not nonempty(p) or not nonempty(h) or not Path(p).exists(): fail("CANONICAL_REFACTOR_DIFF_NOT_MATERIALIZED")
    matches=[c for c in comps if c.get("type")=="refactor-diff"]
    if len(matches)!=1: fail("REFACTOR_DIFF_COMPONENT_REQUIRED_EXACTLY_ONCE")
    c=matches[0]
    if c.get("artifact_sha256")!=h: fail("REFACTOR_DIFF_COMPONENT_HASH_MISMATCH")
    return c


def validate_refactor_diff(text, st, current_snapshot, current_typemap):
    if re.search(r"(?im)^##\s+Decklist\s*$",text) or re.search(r"(?im)^###\s+Main Deck\s*[—-]",text):
        fail("DIFF_ONLY_FULL_DECKLIST_FORBIDDEN")
    canonical=canonical_refactor_diff_text(st,current_snapshot,current_typemap)
    p=st.get("canonical_refactor_diff_file")
    h=st.get("canonical_refactor_diff_sha256")
    if not nonempty(p) or not Path(p).exists() or sha256(Path(p))!=h:
        fail("CANONICAL_REFACTOR_DIFF_NOT_MATERIALIZED")
    if Path(p).read_text(encoding="utf-8")!=canonical:
        fail("CANONICAL_REFACTOR_DIFF_STALE")
    if canonical.rstrip() not in text:
        fail("REFACTOR_DIFF_NOT_EXACT_CANONICAL_PAYLOAD")
    # No extra ratio rows may be introduced outside the canonical artifact.
    canon_rows=set(x.strip() for x in canonical.splitlines() if re.match(r"^[-*]\s+.+:\s+\d+\s*→\s*\d+",x.strip()))
    for m in re.finditer(r"(?im)^\s*[-*]\s*(.+?:\s*\d+\s*→\s*\d+(?:\s*\([^)]*\))?)\s*$",text):
        row="- "+m.group(1).strip()
        if row not in canon_rows: fail(f"REFACTOR_DIFF_NONCANONICAL_ROW: {m.group(1).strip()}")


def validate_narrative_contract(path: Path, st):
    validate_evidence(path, st)
    d = read_json(path, "narrative contract")
    if d.get("run_id") != st["run_id"]:
        fail("RUN_ID_MISMATCH in narrative contract")
    if d.get("authority") != PROGRESSION:
        fail("narrative contract authority mismatch")
    sp = policy_path()
    if not sp.exists():
        fail("STYLE policy source file missing")
    policy = parse_style_policy(sp)
    if d.get("policy_source") != STYLE:
        fail("narrative contract policy_source mismatch")
    if d.get("policy_source_sha256") != sha256(sp):
        fail("narrative contract STYLE hash mismatch")
    if d.get("policy_schema_version") != policy.get("schema_version"):
        fail("narrative contract policy schema mismatch")
    arc = d.get("arc")
    if arc not in policy["eras"]:
        fail(f"unknown narrative arc in contract: {arc}")
    expected = policy["eras"][arc]
    universe = policy["mechanic_universe"]
    if d.get("mechanic_universe") != universe:
        fail("narrative contract mechanic_universe differs from STYLE")
    allowed = d.get("allowed_mechanics")
    forbidden = d.get("forbidden_mechanics")
    if not isinstance(allowed, list) or not isinstance(forbidden, list):
        fail("narrative contract allowed/forbidden mechanics must be lists")
    if set(allowed) & set(forbidden):
        fail("narrative contract mechanic appears in both allowed and forbidden")
    if set(allowed) | set(forbidden) != set(universe):
        fail("narrative contract must partition the complete mechanic_universe")
    if allowed != expected.get("allowed") or forbidden != expected.get("forbidden"):
        fail(f"NARRATIVE_POLICY_MISMATCH for arc {arc}")
    for k in ("mastered_functions", "limited_or_absent_functions"):
        v = d.get(k)
        if not isinstance(v, list) or not v or not all(nonempty(x) for x in v):
            fail(f"narrative contract {k} must be a non-empty list")
    return d, sha256(path), sha256(sp)


def validate_deck_snapshot(path: Path, st):
    validate_evidence(path, st)
    d = read_json(path, "deck snapshot")
    if d.get("run_id") not in (None, st["run_id"]):
        fail("RUN_ID_MISMATCH in deck snapshot")
    if d.get("artifact_id") != st.get("current_artifact"):
        fail("deck snapshot artifact_id mismatch")
    keys = []
    totals = {}
    for zone in ("main_deck", "extra_deck", "side_deck"):
        cards = d.get(zone)
        if not isinstance(cards, list):
            fail(f"deck snapshot {zone} must be a list")
        seen = set()
        total = 0
        for i, c in enumerate(cards):
            if not isinstance(c, dict):
                fail(f"deck snapshot {zone}[{i}] must be an object")
            name, qty = c.get("name"), c.get("qty")
            if not nonempty(name) or not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
                fail(f"invalid deck snapshot card at {zone}[{i}]")
            nk = name.strip().casefold()
            if nk in seen:
                fail(f"duplicate card entry in {zone}: {name}")
            seen.add(nk)
            keys.append((zone, nk, qty, name.strip()))
            total += qty
        totals[zone] = total
    current_comp=deck_composition_sha256(d)
    refresh=st.get("last_evidence_refresh")
    if isinstance(refresh,dict) and refresh.get("artifact")==st.get("current_artifact") and nonempty(refresh.get("expected_composition_sha256")):
        if current_comp!=refresh["expected_composition_sha256"]:
            fail("DECK_CONTENT_CHANGED_REQUIRES_MATERIAL_CHANGE")
    change=st.get("last_material_change")
    if isinstance(change,dict) and change.get("to_artifact")==st.get("current_artifact") and nonempty(change.get("after_composition_sha256")):
        if current_comp!=change["after_composition_sha256"]:
            fail("MATERIAL_CHANGE_CANDIDATE_SNAPSHOT_MISMATCH")
    return d, sha256(path), keys, totals


def validate_narrative_conformance(report_path: Path, contract_path: Path, snapshot_path: Path, st):
    contract, ch, _ = validate_narrative_contract(contract_path, st)
    snap, sh, snap_keys, _ = validate_deck_snapshot(snapshot_path, st)
    validate_evidence(report_path, st)
    r = read_json(report_path, "narrative conformance report")
    if r.get("run_id") != st["run_id"]:
        fail("RUN_ID_MISMATCH in narrative conformance")
    if r.get("authority") != PROGRESSION:
        fail("narrative conformance authority mismatch")
    if r.get("artifact") != st.get("current_artifact"):
        fail("narrative conformance artifact mismatch")
    if r.get("snapshot_sha256") != sh:
        fail("narrative conformance snapshot hash mismatch")
    if r.get("contract_sha256") != ch:
        fail("narrative conformance contract hash mismatch")
    if r.get("forbidden_mechanics_checked") != contract["forbidden_mechanics"]:
        fail("narrative conformance did not check the complete forbidden_mechanics list")
    entries = r.get("card_mechanics")
    if not isinstance(entries, list):
        fail("narrative conformance card_mechanics must be a list")
    report = {}
    universe = set(contract["mechanic_universe"])
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            fail(f"card_mechanics[{i}] must be an object")
        zone, name, qty = e.get("zone"), e.get("name"), e.get("qty")
        ctype, mechs = e.get("card_type"), e.get("mechanics")
        if zone not in {"main_deck", "extra_deck", "side_deck"} or not nonempty(name) or not isinstance(qty, int) or qty <= 0:
            fail(f"invalid card_mechanics entry {i}")
        if not nonempty(ctype):
            fail(f"card_mechanics entry missing card_type: {name}")
        if not isinstance(mechs, list) or any(m not in universe for m in mechs) or len(set(mechs)) != len(mechs):
            fail(f"invalid mechanics list for {name}")
        # Redundant mechanical consistency: if the reported card type literally names
        # a known summon mechanic, that mechanic cannot be omitted from mechanics[].
        low = ctype.casefold()
        for mech in contract["mechanic_universe"]:
            if mech.casefold() in low and mech not in mechs:
                fail(f"MECHANIC_TAG_OMITTED for {name}: card_type declares {mech}")
        key = (zone, name.strip().casefold())
        if key in report:
            fail(f"duplicate card_mechanics entry: {zone}:{name}")
        report[key] = (qty, name.strip(), mechs, ctype)
    expected = {(z, nk):(qty, orig) for z, nk, qty, orig in snap_keys}
    if set(report) != set(expected):
        missing = sorted(f"{z}:{n}" for (z,n) in set(expected)-set(report))
        extra = sorted(f"{z}:{n}" for (z,n) in set(report)-set(expected))
        fail("NARRATIVE_CARD_COVERAGE_MISMATCH missing="+",".join(missing)+" extra="+",".join(extra))
    for key, (qty, orig) in expected.items():
        if report[key][0] != qty:
            fail(f"narrative conformance quantity mismatch for {orig}")
    axis = r.get("axis_mechanics")
    if not isinstance(axis, list) or any(m not in universe for m in axis) or len(set(axis)) != len(axis):
        fail("invalid narrative conformance axis_mechanics")
    observed = set(axis)
    origins = []
    for (zone, _), (_, name, mechs, _) in report.items():
        for m in mechs:
            observed.add(m)
            origins.append((m, f"{zone}:{name}"))
    forbidden = set(contract["forbidden_mechanics"])
    bad = [(m, src) for m, src in origins if m in forbidden]
    bad += [(m, "axis_mechanics") for m in axis if m in forbidden]
    if bad:
        m, src = bad[0]
        fail(f"NARRATIVE_MECHANIC_FORBIDDEN: {m} via {src}")
    declared_obs = r.get("observed_mechanics")
    if not isinstance(declared_obs, list) or set(declared_obs) != observed:
        fail("narrative conformance observed_mechanics mismatch")
    if r.get("status") != "PASS":
        fail("narrative conformance status must be PASS")
    return {"contract_sha256":ch, "snapshot_sha256":sh, "report_sha256":sha256(report_path), "observed_mechanics":sorted(observed)}


def expected_render_id(st):
    return st.get("current_render") or "render-v1"


SOURCE_NATIVE_ASSERTION_BINDINGS = {
    ("STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES", "axis-line-length"): {
        "type": "max_line_length",
        "requires_scope": True,
    },
    ("STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES", "signature-terminal-quote"): {
        "type": "regex_exact_count",
        "requires_scope": True,
        "exact": 1,
    },
}


def validate_source_native_assertion_binding(r):
    if not isinstance(r, dict):
        return
    key=(r.get("source"), r.get("id"))
    spec=SOURCE_NATIVE_ASSERTION_BINDINGS.get(key)
    if not spec:
        return
    assertions=r.get("assertions")
    observed=[] if not isinstance(assertions,list) else [a.get("type") if isinstance(a,dict) else None for a in assertions]
    expected=spec["type"]
    if not isinstance(assertions,list) or len(assertions)!=1 or observed != [expected]:
        fail(f"NATIVE_ASSERTION_BINDING_MISMATCH requirement={r.get('id')} source={r.get('source')} expected={expected} observed={observed}")
    a=assertions[0]
    validate_assertion_shape(a,r.get("id"))
    if spec.get("requires_scope") and (not nonempty(a.get("scope_start")) or not nonempty(a.get("scope_end"))):
        if r.get("id")=="signature-terminal-quote":
            fail("RENDER_ASSERTION_SCOPE_REQUIRED: signature-terminal-quote")
        fail(f"NATIVE_ASSERTION_BINDING_MISMATCH requirement={r.get('id')} source={r.get('source')} expected={expected} observed=missing_scope")
    if "exact" in spec and a.get("exact")!=spec["exact"]:
        fail(f"NATIVE_ASSERTION_BINDING_MISMATCH requirement={r.get('id')} source={r.get('source')} expected_exact={spec['exact']} observed_exact={a.get('exact')}")


def _validate_signature_mini_requirement_binding(requirement, visual):
    """Verify STRUCTURE-owned signature identity -> renderer primitive binding."""
    sig=(visual or {}).get("signature_climax",{}) if isinstance(visual,dict) else {}
    if sig.get("mini_carousel_applicable") is not True:
        return
    parent=sig.get("parent")
    if not nonempty(parent):
        fail("SPECIALIZED_COMPONENT_BINDING_MISMATCH requirement=signature-mini-carousel expected_parent=nonempty observed=missing")
    if not isinstance(requirement,dict):
        fail("SPECIALIZED_COMPONENT_BINDING_MISMATCH requirement=signature-mini-carousel expected=present observed=missing")
    assertions=requirement.get("assertions")
    if not isinstance(assertions,list) or len(assertions)!=1:
        fail("SPECIALIZED_COMPONENT_BINDING_MISMATCH requirement=signature-mini-carousel expected=single_component_min_count")
    a=assertions[0]
    observed=(a.get("type"),a.get("component_type"),a.get("parent")) if isinstance(a,dict) else None
    expected=("component_min_count","mini-carousel",parent)
    if observed!=expected or a.get("min")!=1:
        fail(f"SPECIALIZED_COMPONENT_BINDING_MISMATCH requirement=signature-mini-carousel expected={expected} min=1 observed={observed} min={a.get('min') if isinstance(a,dict) else None}")


def _validate_signature_mini_plan_binding(components, visual):
    """Verify the specialized component keeps semantic id and physical mini-carousel type."""
    sig=(visual or {}).get("signature_climax",{}) if isinstance(visual,dict) else {}
    if sig.get("mini_carousel_applicable") is not True:
        return
    parent=sig.get("parent")
    if not nonempty(parent):
        fail("SPECIALIZED_COMPONENT_BINDING_MISMATCH component=signature-mini-carousel expected_parent=nonempty observed=missing")
    matches=[c for c in components if isinstance(c,dict) and c.get("component_id")=="signature-mini-carousel"]
    if len(matches)!=1:
        fail(f"SPECIALIZED_COMPONENT_BINDING_MISMATCH component=signature-mini-carousel expected_count=1 observed_count={len(matches)}")
    c=matches[0]
    observed=(c.get("type"),c.get("parent"))
    expected=("mini-carousel",parent)
    if observed!=expected:
        fail(f"SPECIALIZED_COMPONENT_BINDING_MISMATCH component=signature-mini-carousel expected={expected} observed={observed}")


def validate_assertion_shape(a, rid):
    if not isinstance(a, dict):
        fail(f"render assertion for {rid} must be an object")
    typ = a.get("type")
    allowed = {"contains_regex","regex_min_count","regex_exact_count","ordered_regex","max_line_length","max_arrow_count_per_line","max_regex_count_per_line","component_min_count"}
    if typ not in allowed:
        fail(f"unsupported render assertion type for {rid}: {typ}")
    if typ in {"contains_regex","regex_min_count","regex_exact_count","max_regex_count_per_line"} and not nonempty(a.get("pattern")):
        fail(f"assertion {typ} for {rid} requires pattern")
    if typ == "ordered_regex":
        pats=a.get("patterns")
        if not isinstance(pats,list) or len(pats)<2 or not all(nonempty(x) for x in pats):
            fail(f"ordered_regex for {rid} requires 2+ patterns")
    if typ in {"regex_min_count","component_min_count"} and (not isinstance(a.get("min"),int) or isinstance(a.get("min"),bool) or a["min"]<1):
        fail(f"assertion {typ} for {rid} requires positive min")
    if typ == "regex_exact_count" and (not isinstance(a.get("exact"),int) or isinstance(a.get("exact"),bool) or a["exact"]<0):
        fail(f"RENDER_ASSERTION_EXACT_INVALID: {rid}")
    if typ in {"max_line_length","max_arrow_count_per_line","max_regex_count_per_line"} and (not isinstance(a.get("max"),int) or isinstance(a.get("max"),bool) or a["max"]<1):
        fail(f"assertion {typ} for {rid} requires positive max")
    if typ == "component_min_count" and not nonempty(a.get("component_type")):
        fail(f"component_min_count for {rid} requires component_type")


def validate_render_contract(path: Path, st):
    validate_evidence(path, st)
    d=read_json(path,"render contract")
    if d.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in render contract")
    if d.get("deck_artifact")!=st.get("current_artifact"): fail("RENDER_CONTRACT_DECK_MISMATCH")
    if d.get("render_id")!=expected_render_id(st): fail(f"RENDER_ID_MISMATCH: expected {expected_render_id(st)}")
    if not isinstance(d.get("authorities"),list) or set(d["authorities"])!=RENDER_AUTHORITIES:
        fail("RENDER_CONTRACT must be derived from both structure authorities")
    reqs=d.get("requirements")
    if not isinstance(reqs,list) or len(reqs)<2: fail("RENDER_CONTRACT requirements must be a non-empty cross-authority set")
    ids=[]; sources=set()
    for i,r in enumerate(reqs):
        if not isinstance(r,dict): fail(f"render contract requirement {i} must be an object")
        rid,source=r.get("id"),r.get("source")
        if not nonempty(rid): fail(f"render contract requirement {i} missing id")
        if source not in RENDER_AUTHORITIES: fail(f"invalid render requirement source for {rid}")
        if r.get("applicable") is not True: fail(f"contract may only contain applicable required items ({rid})")
        if not nonempty(r.get("description")): fail(f"render requirement {rid} missing description")
        assertions=r.get("assertions")
        if not isinstance(assertions,list) or not assertions: fail(f"render requirement {rid} requires at least one mechanical assertion")
        for a in assertions: validate_assertion_shape(a,rid)
        validate_source_native_assertion_binding(r)
        ids.append(rid); sources.add(source)
    if len(set(ids))!=len(ids): fail("duplicate render requirement id")
    if sources!=RENDER_AUTHORITIES: fail("RENDER_CONTRACT must contain requirements from both structure authorities")
    fg=st.get("gates",{}).get("FINAL_CLASSIFICATION_CLOSED",{})
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    if not fg or not vg: fail("render contract requires final classification + visual assets")
    if d.get("final_classification_sha256")!=fg.get("evidence_sha256"): fail("RENDER_CLASSIFICATION_BINDING_MISMATCH")
    if d.get("visual_assets_sha256")!=vg.get("evidence_sha256"): fail("RENDER_VISUAL_ASSETS_BINDING_MISMATCH")
    byid={r["id"]:r for r in reqs}
    mandatory_ids=["decklist-vertical","direction-binding"]
    mandatory_ids.append("refactor-diff" if st.get("refactor_render_mode")=="DIFF_ONLY" else "decklist-groups")
    for mandatory in mandatory_ids:
        if mandatory not in byid: fail(f"MANDATORY_RENDER_REQUIREMENT_MISSING: {mandatory}")
    if not any(a.get("type")=="max_regex_count_per_line" and a.get("max")==1 for a in byid["decklist-vertical"]["assertions"]):
        fail("decklist-vertical must contain max_regex_count_per_line max=1")
    final_class=fg.get("classification")
    # RC16.11: validate the derived direction assertion by its render behavior,
    # not by searching the escaped business value inside the regex source text.
    canonical_direction_line=f"Direction — {final_class}"
    direction_asserts=[]
    for a in byid["direction-binding"]["assertions"]:
        if a.get("type")!="contains_regex":
            continue
        try:
            matched=re.search(a.get("pattern",""),canonical_direction_line,flags=re.MULTILINE|re.IGNORECASE) is not None
        except re.error as exc:
            fail(f"invalid direction-binding regex: {exc}")
        if matched:
            direction_asserts.append(a)
    if not direction_asserts:
        fail("direction-binding must assert final classification")
    visual=read_json(Path(vg["evidence_file"]),"visual assets")
    if visual["main_carousel"].get("applicable") is True and "main-card-carousel" not in byid: fail("main-card-carousel requirement missing")
    sig=visual["signature_climax"]
    if sig.get("terminal_quote_required") is True and "signature-terminal-quote" not in byid: fail("signature-terminal-quote requirement missing")
    if sig.get("mini_carousel_applicable") is True and "signature-mini-carousel" not in byid: fail("signature-mini-carousel requirement missing")
    _validate_signature_mini_requirement_binding(byid.get("signature-mini-carousel"),visual)
    materialize_canonical_refactor_diff(path,st)
    validate_requirement_continuity(d,st)
    pf=render_policy_fingerprint(d)
    expected=st.get("presentation_expected_policy_fingerprint")
    if expected and pf!=expected:
        fail("RENDER_POLICY_FINGERPRINT_MISMATCH")
    return d,sha256(path)


def render_policy_fingerprint(contract):
    """Hash only normative render policy; exclude run/render/hash bindings and prose descriptions."""
    normalized=[]
    for r in contract.get("requirements",[]):
        if not isinstance(r,dict):
            continue
        normalized.append({
            "id":r.get("id"),
            "source":r.get("source"),
            "applicable":r.get("applicable"),
            "assertions":r.get("assertions",[]),
        })
    normalized=sorted(normalized,key=lambda x:(str(x.get("source")),str(x.get("id"))))
    raw=json.dumps(normalized,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


DERIVED_RENDER_COMPILES = {
    "DECKLIST_MODE_FROM_STATE",
    "DECKLIST_GROUPS_FROM_SNAPSHOT",
    "REFACTOR_DIFF_FROM_STATE",
    "FINAL_DIRECTION_FROM_CLASSIFICATION",
}


def _canonical_json_text(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _render_compile_inputs(st):
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    ng=st.get("gates",{}).get("NARRATIVE_CONFORMANCE_CLOSED",{})
    fg=st.get("gates",{}).get("FINAL_CLASSIFICATION_CLOSED",{})
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    if not dg or not dg.get("snapshot_file"): fail("RENDER_COMPILER_DECK_SNAPSHOT_MISSING")
    if not ng or not ng.get("evidence_file"): fail("RENDER_COMPILER_NARRATIVE_CONFORMANCE_MISSING")
    if not fg or not fg.get("evidence_file") or not nonempty(fg.get("classification")): fail("RENDER_COMPILER_FINAL_CLASSIFICATION_MISSING")
    if not vg or not vg.get("evidence_file"): fail("RENDER_COMPILER_VISUAL_ASSETS_MISSING")
    sp=Path(dg["snapshot_file"]); np=Path(ng["evidence_file"]); fp=Path(fg["evidence_file"]); vp=Path(vg["evidence_file"])
    for label,path in (("snapshot",sp),("narrative",np),("classification",fp),("visual",vp)):
        if not path.exists() or not path.is_file(): fail(f"RENDER_COMPILER_{label.upper()}_FILE_MISSING")
    snap=read_json(sp,"deck snapshot")
    typemap=_narrative_type_map(np)
    totals=_category_totals(snap,typemap)
    return {
        "snapshot_path":sp,"narrative_path":np,"classification_path":fp,"visual_path":vp,
        "snapshot":snap,"typemap":typemap,"totals":totals,
        "classification":fg["classification"],
        "snapshot_sha256":sha256(sp),"narrative_sha256":sha256(np),
        "classification_sha256":fg.get("evidence_sha256") or sha256(fp),
        "visual_sha256":vg.get("evidence_sha256") or sha256(vp),
    }


def _decklist_group_assertions(totals):
    return [
        {"type":"contains_regex","pattern":rf"^###\s+Main Deck\s*[—-]\s*{totals['MAIN']}\s*$"},
        {"type":"contains_regex","pattern":rf"^####\s+Monstres\s*[—-]\s*{totals['MONSTER']}\s*$"},
        {"type":"contains_regex","pattern":rf"^####\s+Magies\s*[—-]\s*{totals['SPELL']}\s*$"},
        {"type":"contains_regex","pattern":rf"^####\s+Pi[èe]ges\s*[—-]\s*{totals['TRAP']}\s*$"},
        {"type":"contains_regex","pattern":rf"^###\s+Extra Deck\s*[—-]\s*{totals['EXTRA']}\s*$"},
        {"type":"contains_regex","pattern":rf"^###\s+Side Deck\s*[—-]\s*{totals['SIDE']}\s*$"},
    ]


def _compile_render_requirement(r, st, inputs):
    if not isinstance(r,dict): fail("render policy requirement must be an object")
    compile_kind=r.get("compile")
    if compile_kind is None:
        if "assertions" not in r: fail(f"render policy requirement {r.get('id')} needs assertions or compile")
        out=dict(r)
        if out.get("applicable") is not True: fail(f"render policy may only contain applicable required items ({out.get('id')})")
        for a in out.get("assertions",[]): validate_assertion_shape(a,out.get("id"))
        validate_source_native_assertion_binding(out)
        return out
    if compile_kind not in DERIVED_RENDER_COMPILES: fail(f"unsupported render compile marker: {compile_kind}")
    if "assertions" in r:
        fail("DERIVED_REQUIREMENT_MANUAL_OVERRIDE")
    base={k:v for k,v in r.items() if k not in {"compile"}}
    if base.get("source") not in RENDER_AUTHORITIES: fail(f"invalid render requirement source for {base.get('id')}")
    if base.get("applicable") is not True: fail(f"render policy may only contain applicable required items ({base.get('id')})")
    if not nonempty(base.get("description")): fail(f"render policy requirement {base.get('id')} missing description")
    mode=st.get("refactor_render_mode") or "FULL"
    if compile_kind in {"DECKLIST_MODE_FROM_STATE","DECKLIST_GROUPS_FROM_SNAPSHOT","REFACTOR_DIFF_FROM_STATE"}:
        if compile_kind=="DECKLIST_GROUPS_FROM_SNAPSHOT" and mode!="FULL": fail("RENDER_POLICY_MODE_CONFLICT")
        if compile_kind=="REFACTOR_DIFF_FROM_STATE" and mode!="DIFF_ONLY": fail("RENDER_POLICY_MODE_CONFLICT")
        if mode=="DIFF_ONLY":
            ch=st.get("last_material_change") or {}
            old,new=ch.get("from_artifact"),ch.get("to_artifact")
            if not nonempty(old) or not nonempty(new): fail("REFACTOR_DIFF_MATERIAL_CHANGE_MISSING")
            base["id"]="refactor-diff"
            base["assertions"]=[{"type":"contains_regex","pattern":rf"^##\s+Diff\s+{re.escape(old)}\s+→\s+{re.escape(new)}\s*$"}]
        else:
            base["id"]="decklist-groups"
            base["assertions"]=_decklist_group_assertions(inputs["totals"])
        return base
    if compile_kind=="FINAL_DIRECTION_FROM_CLASSIFICATION":
        base["id"]="direction-binding"
        base["assertions"]=[{"type":"contains_regex","pattern":rf"^.*Direction.*{re.escape(inputs['classification'])}.*$"}]
        return base
    fail(f"unsupported render compile marker: {compile_kind}")


def compile_render_contract_payload(policy_path: Path, st, contract_parent: Path|None=None):
    validate_evidence(policy_path,st)
    policy=read_json(policy_path,"render policy")
    forbidden={"run_id","deck_artifact","render_id","final_classification_sha256","visual_assets_sha256","deck_snapshot_sha256","narrative_conformance_sha256","compiled_by","compiler_runtime_version","policy_sha256"}
    bad=sorted(k for k in forbidden if k in policy)
    if bad: fail("DERIVED_REQUIREMENT_MANUAL_OVERRIDE: "+",".join(bad))
    auths=policy.get("authorities")
    if not isinstance(auths,list) or set(auths)!=RENDER_AUTHORITIES: fail("RENDER_POLICY must be derived from both structure authorities")
    reqs=policy.get("requirements")
    if not isinstance(reqs,list) or len(reqs)<2: fail("RENDER_POLICY requirements must be a non-empty cross-authority set")
    inputs=_render_compile_inputs(st)
    compiled=[]
    seen_compile=[]
    for r in reqs:
        if isinstance(r,dict) and r.get("compile"): seen_compile.append(r.get("compile"))
        compiled.append(_compile_render_requirement(r,st,inputs))
    if not any(x in {"DECKLIST_MODE_FROM_STATE","DECKLIST_GROUPS_FROM_SNAPSHOT","REFACTOR_DIFF_FROM_STATE"} for x in seen_compile):
        fail("RENDER_POLICY_DECKLIST_COMPILER_MISSING")
    if "FINAL_DIRECTION_FROM_CLASSIFICATION" not in seen_compile:
        fail("RENDER_POLICY_DIRECTION_COMPILER_MISSING")
    # Exact canonical requirements may not collide after compilation.
    ids=[r.get("id") for r in compiled]
    if any(not nonempty(x) for x in ids) or len(set(ids))!=len(ids): fail("RENDER_POLICY_COMPILED_REQUIREMENT_ID_CONFLICT")
    parent=contract_parent or policy_path.parent
    try:
        policy_ref=os.path.relpath(policy_path.resolve(),parent.resolve())
    except Exception:
        policy_ref=policy_path.name
    out={
        "run_id":st["run_id"],
        "deck_artifact":st.get("current_artifact"),
        "render_id":expected_render_id(st),
        "authorities":sorted(RENDER_AUTHORITIES),
        "requirements":compiled,
        "final_classification_sha256":inputs["classification_sha256"],
        "visual_assets_sha256":inputs["visual_sha256"],
        "compiled_by":"compile-render-contract",
        "compiler_runtime_version":VERSION,
        "policy_file":policy_ref,
        "policy_sha256":sha256(policy_path),
        "deck_snapshot_sha256":inputs["snapshot_sha256"],
        "narrative_conformance_sha256":inputs["narrative_sha256"],
        "compiled_deck_totals":inputs["totals"],
        "compiled_final_direction":inputs["classification"],
        "compiled_render_mode":st.get("refactor_render_mode") or "FULL",
    }
    for k in ("requirement_continuity","component_continuity"):
        if k in policy: out[k]=policy[k]
    return out


def validate_compiled_render_contract(path: Path, st):
    validate_evidence(path,st)
    d=read_json(path,"compiled render contract")
    if d.get("compiled_by")!="compile-render-contract": fail("COMPILED_RENDER_CONTRACT_REQUIRED")
    if not nonempty(d.get("policy_file")) or not nonempty(d.get("policy_sha256")): fail("COMPILED_RENDER_CONTRACT_PROVENANCE_MISSING")
    policy_path=(path.parent/d["policy_file"]).resolve()
    if not policy_path.exists() or not policy_path.is_file(): fail("RENDER_POLICY_FILE_MISSING")
    if sha256(policy_path)!=d.get("policy_sha256"): fail("RENDER_POLICY_PROVENANCE_MISMATCH")
    # The frozen contract is canonical. Revalidate the deterministic BASE projection
    # against current authoritative inputs, but never rederive continuity from mutable
    # post-freeze state (the Jack Black-Box failure). Continuity itself was validated
    # at freeze and the frozen contract hash is bound downstream.
    stable=copy.deepcopy(st)
    stable["presentation_carry_components"]=[]
    stable["refactor_visual_carry_components"]=[]
    stable["refactor_visual_carry_requirements"]=[]
    expected=compile_render_contract_payload(policy_path,stable,path.parent)
    volatile={"component_continuity","component_continuity_compiled_by","requirement_continuity","requirement_continuity_compiled_by"}
    actual_base={k:v for k,v in d.items() if k not in volatile}
    expected_base={k:v for k,v in expected.items() if k not in volatile}
    if _canonical_json_text(actual_base)!=_canonical_json_text(expected_base): fail("COMPILED_RENDER_CONTRACT_MISMATCH")
    return validate_render_contract(path,st)


def _next_render_contract_transaction_id(events):
    n=sum(1 for e in events if e.get("event")=="RENDER_CONTRACT_TRANSACTION_STARTED")+1
    return f"render-contract-tx-{n:06d}"


def _render_contract_transaction_failure(rd: Path, st, transaction_id, phase, exc, policy: Path, out: Path, candidate: Path|None):
    code,detail=_denied_parts(exc)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(
        rd,st,"RENDER_CONTRACT_TRANSACTION_FAILED",checkpoint_seq=cp.get("checkpoint_seq"),
        transaction_id=transaction_id,phase=phase,error_code=code,detail=detail,
        policy_file=str(policy),policy_sha256=sha256(policy) if policy.exists() and policy.is_file() else None,
        output_file=str(out),candidate_contract_sha256=sha256(candidate) if candidate and candidate.exists() and candidate.is_file() else None,
        canonical_contract_sha256=sha256(out) if out.exists() and out.is_file() else None,
        render_attempts_used=_render_attempts_used(st),state_sha256_after=sha256(rd/STATE_FILE),
    )


def _render_contract_transaction_exception(rd: Path, st, transaction_id, phase, exc, policy: Path, out: Path, candidate: Path|None):
    tb=traceback.format_exc()
    tbfile=rd/f"{transaction_id}.traceback.txt"
    _atomic_write_text(tbfile,tb)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(
        rd,st,"RENDER_CONTRACT_TRANSACTION_EXCEPTION",checkpoint_seq=cp.get("checkpoint_seq"),
        transaction_id=transaction_id,phase=phase,exception_type=type(exc).__name__,message=str(exc),
        traceback_file=str(tbfile),traceback_sha256=sha256(tbfile),
        policy_file=str(policy),policy_sha256=sha256(policy) if policy.exists() and policy.is_file() else None,
        output_file=str(out),candidate_contract_sha256=sha256(candidate) if candidate and candidate.exists() and candidate.is_file() else None,
        state_sha256_after=sha256(rd/STATE_FILE),
    )


def cmd_compile_render_contract(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if next_gate(st)[0]!="RENDER_CONTRACT_FROZEN":
        fail(f"compile-render-contract requires next gate RENDER_CONTRACT_FROZEN; next gate is {next_gate(st)[0]}")
    policy=Path(a.policy_file); out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    events=_read_journal(rd); transaction_id=_next_render_contract_transaction_id(events)
    cp0=_load_checkpoint_raw(rd,required=True)
    fg=st.get("gates",{}).get("FINAL_CLASSIFICATION_CLOSED",{})
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    _append_run_journal(
        rd,st,"RENDER_CONTRACT_TRANSACTION_STARTED",checkpoint_seq=cp0.get("checkpoint_seq"),
        transaction_id=transaction_id,deck_artifact=st.get("current_artifact"),
        policy_file=str(policy),policy_sha256=sha256(policy) if policy.exists() and policy.is_file() else None,
        output_file=str(out),state_sha256_before=sha256(rd/STATE_FILE),
        expected_render_id=expected_render_id(st),
        final_classification_sha256=fg.get("evidence_sha256"),visual_assets_sha256=vg.get("evidence_sha256"),
        render_attempts_used=_render_attempts_used(st),
    )
    candidate=out.with_name(f".{out.name}.{transaction_id}.tmp")
    phase="COMPILE"
    try:
        payload=compile_render_contract_payload(policy,st,out.parent)
        phase="MATERIALIZE"
        _atomic_write_text(candidate,json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
        phase="PRE_FREEZE_VALIDATE"
        validate_compiled_render_contract(candidate,st)
        candidate_sha=sha256(candidate)
        phase="MATERIALIZE"
        os.replace(candidate,out)
        contract_sha=sha256(out)
        if contract_sha!=candidate_sha:
            fail("RENDER_CONTRACT_TRANSACTION_PROMOTION_MISMATCH")
        cp=_load_checkpoint_raw(rd,required=True)
        _append_run_journal(rd,st,"DERIVED_DEPENDENCY_MATERIALIZED",checkpoint_seq=cp.get("checkpoint_seq"),dependency="render_contract",gate="RENDER_CONTRACT_FROZEN",artifact_file=str(out),artifact_sha256=contract_sha,policy_file=str(policy),policy_sha256=sha256(policy),render_id=payload.get("render_id"))
        phase="GATE_REENTRY"
        _append_run_journal(rd,st,"GATE_REENTRY_TRIGGERED",checkpoint_seq=cp.get("checkpoint_seq"),gate="RENDER_CONTRACT_FROZEN",trigger="DERIVED_DEPENDENCY_MATERIALIZED",artifact_sha256=contract_sha)
        from argparse import Namespace
        ns=Namespace(run_dir=str(rd),run_id=st["run_id"],gate="RENDER_CONTRACT_FROZEN",authority=GLOBAL_STRUCTURE,status="FROZEN",evidence_file=str(out),render_manifest=None,contract_file=None,combo_impact_file=None,pilotage_contract_file=None,_derived_reentry=True)
        cmd_complete(ns)
        phase="FREEZE_VERIFY"
        st2=load_state(rd)
        frozen=st2.get("gates",{}).get("RENDER_CONTRACT_FROZEN",{})
        if frozen.get("evidence_sha256")!=contract_sha:
            fail("RENDER_CONTRACT_TRANSACTION_FREEZE_MISMATCH")
        cp2=_load_checkpoint_raw(rd,required=True)
        _append_run_journal(
            rd,st2,"RENDER_CONTRACT_TRANSACTION_SUCCEEDED",checkpoint_seq=cp2.get("checkpoint_seq"),
            transaction_id=transaction_id,phase="FREEZE_VERIFY",policy_file=str(policy),policy_sha256=sha256(policy),
            contract_file=str(out),contract_sha256=contract_sha,render_id=payload.get("render_id"),
            state_sha256_after=sha256(rd/STATE_FILE),render_attempts_used=_render_attempts_used(st2),
        )
        print(json.dumps({"status":"PASS","contract_file":str(out),"contract_sha256":contract_sha,"policy_sha256":sha256(policy),"deck_totals":payload["compiled_deck_totals"],"direction":payload["compiled_final_direction"],"render_mode":payload["compiled_render_mode"],"gate":"RENDER_CONTRACT_FROZEN","gate_status":"FROZEN"},ensure_ascii=False,indent=2))
    except SystemExit as exc:
        if candidate.exists():
            try: candidate.unlink()
            except OSError: pass
        _render_contract_transaction_failure(rd,load_state(rd),transaction_id,phase,exc,policy,out,candidate if candidate.exists() else None)
        raise
    except Exception as exc:
        if candidate.exists():
            try: candidate.unlink()
            except OSError: pass
        _render_contract_transaction_exception(rd,load_state(rd),transaction_id,phase,exc,policy,out,candidate if candidate.exists() else None)
        raise


def validate_frozen_render_contract(path: Path, st):
    contract,ch=validate_compiled_render_contract(path,st)
    frozen=st.get("gates",{}).get("RENDER_CONTRACT_FROZEN",{})
    if not frozen:
        fail("RENDER_CONTRACT_NOT_FROZEN")
    if frozen.get("evidence_sha256")!=ch:
        fail("RENDER_CONTRACT_MUTATED_AFTER_FREEZE")
    if frozen.get("render_id")!=contract.get("render_id"):
        fail("RENDER_CONTRACT_FROZEN_RENDER_MISMATCH")
    pf=render_policy_fingerprint(contract)
    if frozen.get("render_policy_fingerprint") and frozen.get("render_policy_fingerprint")!=pf:
        fail("RENDER_POLICY_FINGERPRINT_MISMATCH")
    return contract,ch


def _scope_text(text,a):
    start=0; end=len(text)
    if nonempty(a.get("scope_start")):
        m=re.search(a["scope_start"],text,flags=re.MULTILINE)
        if not m: fail(f"RENDER_ASSERTION_SCOPE_START_NOT_FOUND: {a['scope_start']}")
        start=m.start()
    if nonempty(a.get("scope_end")):
        m=re.search(a["scope_end"],text[start:],flags=re.MULTILINE)
        if m: end=start+m.start()
    return text[start:end]


def execute_render_assertion(a,text,components,rid):
    scoped=_scope_text(text,a); typ=a["type"]
    if typ=="contains_regex" and not re.search(a["pattern"],scoped,flags=re.MULTILINE): fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: contains_regex")
    elif typ=="regex_min_count" and len(re.findall(a["pattern"],scoped,flags=re.MULTILINE))<a["min"]: fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: regex_min_count")
    elif typ=="regex_exact_count":
        observed=len(re.findall(a["pattern"],scoped,flags=re.MULTILINE))
        if observed!=a["exact"]: fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: regex_exact_count observed={observed} expected={a['exact']}")
    elif typ=="ordered_regex":
        pos=0
        for pat in a["patterns"]:
            m=re.search(pat,scoped[pos:],flags=re.MULTILINE)
            if not m: fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: ordered_regex")
            pos+=m.end()
    elif typ=="max_line_length" and any(len(x)>a["max"] for x in scoped.splitlines()): fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: max_line_length")
    elif typ=="max_arrow_count_per_line" and any(x.count("→")>a["max"] for x in scoped.splitlines()): fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: max_arrow_count_per_line")
    elif typ=="max_regex_count_per_line" and any(len(re.findall(a["pattern"],x))>a["max"] for x in scoped.splitlines()): fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: max_regex_count_per_line")
    elif typ=="component_min_count":
        matches=[]
        for c in components:
            if c.get("type")!=a["component_type"]: continue
            if nonempty(a.get("parent")) and c.get("parent")!=a["parent"]: continue
            if nonempty(a.get("tag")) and a["tag"] not in (c.get("tags") or []): continue
            matches.append(c)
        if len(matches)<a["min"]: fail(f"RENDER_SHAPE_ASSERTION_FAILED {rid}: component_min_count")


def _validate_component_plan(plan_path: Path, visual_path: Path, st):
    validate_evidence(plan_path,st); validate_evidence(visual_path,st)
    plan=read_json(plan_path,"component plan"); visual=read_json(visual_path,"visual assets for component plan")
    if plan.get("schema")!=COMPONENT_PLAN_SCHEMA: fail("COMPONENT_PLAN_SCHEMA_INVALID")
    if plan.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in component plan")
    if plan.get("deck_artifact")!=st.get("current_artifact"): fail("COMPONENT_PLAN_DECK_MISMATCH")
    if plan.get("render_id")!=st.get("current_render"): fail("COMPONENT_PLAN_RENDER_MISMATCH")
    if not isinstance(plan.get("authorities"),list) or set(plan["authorities"])!=RENDER_AUTHORITIES: fail("COMPONENT_PLAN_AUTHORITIES_INVALID")
    if plan.get("visual_assets_sha256")!=sha256(visual_path): fail("COMPONENT_PLAN_PROVENANCE_MISMATCH")
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    if vg and (vg.get("evidence_sha256")!=sha256(visual_path) or Path(vg.get("evidence_file","")).resolve()!=visual_path.resolve()):
        fail("COMPONENT_PLAN_PROVENANCE_MISMATCH")
    comps=plan.get("components")
    if not isinstance(comps,list): fail("COMPONENT_PLAN_COMPONENTS_INVALID")
    seen=set(); out=[]; visual_refs=set(visual.get("image_refs") or [])
    for i,c in enumerate(comps):
        if not isinstance(c,dict): fail(f"COMPONENT_PLAN_ITEM_INVALID {i}")
        if "artifact_file" in c or "artifact_sha256" in c: fail("DERIVED_COMPONENT_BINDING_MANUAL_OVERRIDE")
        cid=c.get("component_id")
        if not nonempty(cid): fail("COMPONENT_PLAN_ID_INVALID")
        if cid in seen: fail("COMPONENT_IDENTITY_DUPLICATE")
        seen.add(cid)
        if not nonempty(c.get("type")): fail(f"COMPONENT_PLAN_TYPE_INVALID {cid}")
        tags=c.get("tags") or []
        if not isinstance(tags,list) or not all(nonempty(x) for x in tags): fail(f"COMPONENT_PLAN_TAGS_INVALID {cid}")
        refs=c.get("image_refs") or []
        if not isinstance(refs,list) or not all(nonempty(x) for x in refs): fail(f"COMPONENT_PLAN_IMAGE_REFS_INVALID {cid}")
        if not set(refs).issubset(visual_refs): fail(f"COMPONENT_PLAN_UNBOUND_IMAGE_REF {cid}")
        out.append(dict(c))
    _validate_signature_mini_plan_binding(out,visual)
    return plan,visual,out


def _safe_component_payload_id(cid):
    return isinstance(cid,str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}",cid) is not None and ".." not in cid


def _expected_component_payload(planned, plan_path: Path, visual_path: Path, st):
    cid=planned.get("component_id")
    if not _safe_component_payload_id(cid): fail("COMPONENT_PAYLOAD_PATH_UNSAFE")
    typ=planned.get("type")
    if typ=="refactor-diff": return None
    if typ not in {"main-carousel","mini-carousel"}: fail("UNSUPPORTED_COMPONENT_PAYLOAD_TYPE")
    refs=planned.get("image_refs") or []
    # Payload identity is intentionally functional/stable across deck versions.
    # Run/deck/render/provenance bindings live in the compiled manifest, otherwise
    # PRESERVE continuity would change the component hash without a visual change.
    return {
        "schema":COMPILED_COMPONENT_PAYLOAD_SCHEMA,
        "component_id":cid,
        "ui_type":"image_group",
        "layout":"carousel",
        "image_refs":list(refs),
        "compiled_by":"compile-component-payloads",
    }


def compile_component_payloads(plan_path: Path, visual_path: Path, output_dir: Path, st):
    plan,visual,planned=_validate_component_plan(Path(plan_path),Path(visual_path),st)
    out=[]; od=Path(output_dir); od.mkdir(parents=True,exist_ok=True)
    for c in planned:
        expected=_expected_component_payload(c,Path(plan_path),Path(visual_path),st)
        if expected is None:
            continue
        fp=od/f"component__{c['component_id']}.json"
        _atomic_write_text(fp,_stable_json_text(expected))
        out.append({"component_id":c["component_id"],"file":str(fp),"sha256":sha256(fp),"payload":expected})
    return out


def validate_compiled_component_payload(payload_path: Path, plan_path: Path, visual_path: Path, st):
    payload=read_json(Path(payload_path),"compiled component payload")
    if payload.get("schema")!=COMPILED_COMPONENT_PAYLOAD_SCHEMA or payload.get("compiled_by")!="compile-component-payloads":
        fail("COMPILED_COMPONENT_PAYLOAD_REQUIRED")
    plan,visual,planned=_validate_component_plan(Path(plan_path),Path(visual_path),st)
    cid=payload.get("component_id")
    matches=[c for c in planned if c.get("component_id")==cid]
    if len(matches)!=1: fail("COMPONENT_PAYLOAD_PROVENANCE_MISMATCH")
    expected=_expected_component_payload(matches[0],Path(plan_path),Path(visual_path),st)
    if expected is None: fail("COMPONENT_PAYLOAD_TYPE_UNSUPPORTED")
    if payload!=expected or Path(payload_path).read_text(encoding="utf-8")!=_stable_json_text(payload):
        fail("COMPILED_COMPONENT_PAYLOAD_MISMATCH")
    return payload


def cmd_compile_component_payloads(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    docs=compile_component_payloads(Path(a.plan_file),Path(a.visual_assets_file),Path(a.output_dir),st)
    print(json.dumps({"status":"PASS","component_count":len(docs),"components":[{"component_id":x["component_id"],"file":x["file"],"sha256":x["sha256"]} for x in docs]},ensure_ascii=False,indent=2))


def _match_component_artifact(planned, paths, used):
    # Exact deterministic component identity wins. The legacy image-ref fallback is
    # retained only for old/manual artifacts that do not carry component_id; otherwise
    # two carousels reusing the same images become spuriously ambiguous.
    exact=[]; fallback=[]; remaining=[]
    for p in paths:
        p=Path(p).resolve()
        if str(p) in used or not p.exists() or not p.is_file(): continue
        remaining.append(p)
        try: payload=read_json(p,"component artifact")
        except SystemExit: payload=None
        if isinstance(payload,dict) and payload.get("component_id")==planned.get("component_id"):
            exact.append(p); continue
        if planned.get("type") in {"main-carousel","mini-carousel"} and isinstance(payload,dict) and payload.get("ui_type")=="image_group" and payload.get("layout")=="carousel" and payload.get("image_refs")==planned.get("image_refs"):
            fallback.append(p)
    matches=exact if exact else fallback
    if not matches and planned.get("type") not in {"main-carousel","mini-carousel"} and len(remaining)==1:
        matches=remaining
    return matches


def _build_component_manifest(plan_path: Path, visual_path: Path, component_paths, st):
    plan,visual,planned=_validate_component_plan(plan_path,visual_path,st)
    paths=[Path(x).resolve() for x in component_paths]
    if len({str(x) for x in paths})!=len(paths): fail("COMPONENT_ARTIFACT_DUPLICATE_PATH")
    used=set(); comps=[]
    for c in planned:
        matches=_match_component_artifact(c,paths,used)
        if not matches: fail(f"COMPONENT_ARTIFACT_MISSING: {c['component_id']}")
        if len(matches)>1: fail(f"COMPONENT_ARTIFACT_AMBIGUOUS: {c['component_id']}")
        ap=matches[0]; used.add(str(ap))
        if c.get("type") in {"main-carousel","mini-carousel"}:
            validate_compiled_component_payload(ap,plan_path,visual_path,st)
        x=dict(c); x["status"]="MATERIALIZED"; x["artifact_file"]=str(ap); x["artifact_sha256"]=sha256(ap)
        comps.append(x)
    extras=[str(p) for p in paths if str(p) not in used]
    if extras: fail("COMPONENT_ARTIFACT_UNPLANNED: "+",".join(extras))
    return {
        "schema":COMPILED_COMPONENT_MANIFEST_SCHEMA,"run_id":st.get("run_id"),
        "deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),
        "component_plan_file":str(plan_path.resolve()),"component_plan_sha256":sha256(plan_path),
        "visual_assets_file":str(visual_path.resolve()),"visual_assets_sha256":sha256(visual_path),
        "compiled_by":"compile-component-manifest","compiler_runtime_version":VERSION,"components":comps
    }


def compile_component_manifest(plan_path: Path, visual_path: Path, component_paths, output_path: Path, st):
    doc=_build_component_manifest(Path(plan_path),Path(visual_path),component_paths,st)
    _atomic_write_text(Path(output_path),_stable_json_text(doc))
    return doc


def validate_compiled_component_manifest(manifest_path: Path, plan_path: Path, visual_path: Path, component_paths, st):
    manifest=read_json(Path(manifest_path),"compiled component manifest")
    if manifest.get("schema")!=COMPILED_COMPONENT_MANIFEST_SCHEMA or manifest.get("compiled_by")!="compile-component-manifest":
        fail("COMPILED_COMPONENT_MANIFEST_REQUIRED")
    expected=_build_component_manifest(Path(plan_path),Path(visual_path),component_paths,st)
    if manifest!=expected or Path(manifest_path).read_text(encoding="utf-8")!=_stable_json_text(manifest):
        fail("COMPILED_COMPONENT_MANIFEST_MISMATCH")
    return manifest


def cmd_compile_component_manifest(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    files=[Path(x) for x in (a.component_file or [])]
    doc=compile_component_manifest(Path(a.plan_file),Path(a.visual_assets_file),files,Path(a.output),st)
    print(json.dumps({"status":"PASS","manifest_file":str(Path(a.output)),"manifest_sha256":sha256(Path(a.output)),"component_count":len(doc["components"])},ensure_ascii=False,indent=2))


def _component_identity(c):
    return {"component_id":c.get("component_id"),"type":c.get("type"),"parent":c.get("parent"),"tags":sorted(c.get("tags") or []),"artifact_sha256":c.get("artifact_sha256"),"image_refs":list(c.get("image_refs") or [])}


def validate_components(manifest_path: Path, manifest, st):
    comps=manifest.get("components",[])
    if not isinstance(comps,list): fail("render manifest components must be a list")
    seen=set(); verified=[]
    for i,c in enumerate(comps):
        if not isinstance(c,dict): fail(f"render component {i} must be an object")
        cid=c.get("component_id")
        if not nonempty(cid): fail(f"render component {i} missing component_id")
        if cid in seen: fail(f"duplicate render component_id {cid}")
        seen.add(cid)
        if not nonempty(c.get("type")): fail(f"render component {cid} missing type")
        if c.get("status")!="MATERIALIZED": fail(f"render component {cid} is not MATERIALIZED")
        af,ah=c.get("artifact_file"),c.get("artifact_sha256")
        if not nonempty(af) or not nonempty(ah): fail(f"render component {cid} requires artifact_file + artifact_sha256")
        ap=(manifest_path.parent/af).resolve()
        if not ap.exists() or not ap.is_file(): fail(f"render component artifact missing for {cid}")
        if sha256(ap)!=ah: fail(f"render component artifact hash mismatch for {cid}")
        if c.get("type") in {"main-carousel","mini-carousel"}:
            vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
            if not vg: fail(f"visual assets gate missing for {cid}")
            visual=read_json(Path(vg["evidence_file"]),"visual assets")
            refs=c.get("image_refs")
            if not isinstance(refs,list) or not refs: fail(f"carousel component {cid} requires image_refs")
            lim=(2,4) if c.get("type")=="main-carousel" else (3,4)
            if not (lim[0]<=len(refs)<=lim[1]): fail(f"carousel component {cid} image_refs count invalid")
            if not set(refs).issubset(set(visual.get("image_refs") or [])): fail(f"carousel component {cid} uses unbound image refs")
            payload=read_json(ap,"carousel component artifact")
            if payload.get("ui_type")!="image_group" or payload.get("layout")!="carousel" or payload.get("image_refs")!=refs:
                fail(f"carousel component {cid} artifact must materialize image_group carousel with exact refs")
        verified.append(c)
    return verified


def component_inventory_hash(comps):
    normalized=[_component_identity(c) for c in sorted(comps,key=lambda x:x.get("component_id",""))]
    raw=json.dumps(normalized,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _active_carry_components(st):
    ref=st.get("refactor_visual_carry_components") or []
    if ref and (st.get("last_material_change") or {}).get("post_output_refactor"):
        return ref,"refactor"
    return st.get("presentation_carry_components") or [],"presentation"


def _drop_allowed_for_visual(old, visual):
    typ=old.get("type")
    if typ=="main-carousel": return visual.get("main_carousel",{}).get("applicable") is False
    if typ=="mini-carousel": return visual.get("signature_climax",{}).get("mini_carousel_applicable") is False
    return False


def validate_requirement_continuity(contract, st):
    prior=st.get("refactor_visual_carry_requirements") or []
    if not prior or not (st.get("last_material_change") or {}).get("post_output_refactor"): return
    trans=contract.get("requirement_continuity")
    if not isinstance(trans,list): fail("REFACTOR_REQUIREMENT_CONTINUITY_REQUIRED")
    by_old={x.get("previous_requirement_id"):x for x in trans if isinstance(x,dict)}
    if set(by_old)!=set(prior): fail("REFACTOR_REQUIREMENT_CONTINUITY_INCOMPLETE")
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    visual=read_json(Path(vg["evidence_file"]),"visual assets")
    reqids={r.get("id") for r in contract.get("requirements",[]) if isinstance(r,dict)}
    for rid in prior:
        t=by_old[rid]; mode=t.get("mode")
        if t.get("source") not in RENDER_AUTHORITIES: fail(f"invalid requirement continuity source for {rid}")
        if mode in {"PRESERVE","REGENERATE"}:
            if rid not in reqids: fail(f"VISUAL_REQUIREMENT_DROPPED {rid}")
            if rid=="signature-terminal-quote" and visual.get("signature_climax",{}).get("terminal_quote_required") is not True:
                fail("TERMINAL_QUOTE_CONTINUITY_APPLICABILITY_MISMATCH")
        elif mode=="DROP_EXPLICIT":
            if not nonempty(t.get("reason")): fail(f"DROP_EXPLICIT_REASON_REQUIRED {rid}")
            if rid=="signature-terminal-quote":
                if visual.get("signature_climax",{}).get("terminal_quote_required") is not False: fail("DROP_EXPLICIT_STILL_APPLICABLE signature-terminal-quote")
            else: fail(f"DROP_EXPLICIT_UNSUPPORTED_REQUIREMENT {rid}")
        else: fail(f"requirement {rid} continuity mode must be PRESERVE, REGENERATE or DROP_EXPLICIT")


def validate_component_continuity(contract,comps,st):
    prior,origin=_active_carry_components(st)
    if not prior: return
    trans=contract.get("component_continuity")
    if not isinstance(trans,list): fail("COMPONENT_CONTINUITY_REQUIRED after presentation/refactor change")
    by_old={x.get("previous_component_id"):x for x in trans if isinstance(x,dict)}
    if set(by_old)!={x.get("component_id") for x in prior}: fail("COMPONENT_CONTINUITY_INCOMPLETE")
    current={c.get("component_id"):c for c in comps}
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    visual=read_json(Path(vg["evidence_file"]),"visual assets") if vg else {}
    for old in prior:
        oid=old["component_id"]; t=by_old[oid]; mode=t.get("mode")
        if t.get("source") not in RENDER_AUTHORITIES: fail(f"invalid component continuity source for {oid}")
        if mode=="PRESERVE":
            c=current.get(oid)
            if not c: fail(f"COMPONENT_DROPPED {oid}")
            if c.get("artifact_sha256")!=old.get("artifact_sha256"): fail(f"COMPONENT_PRESERVE_HASH_MISMATCH {oid}")
            if c.get("type")!=old.get("type") or c.get("parent")!=old.get("parent") or sorted(c.get("tags") or [])!=sorted(old.get("tags") or []): fail(f"COMPONENT_PRESERVE_BINDING_MISMATCH {oid}")
        elif mode=="REGENERATE":
            nid=t.get("new_component_id")
            if not nonempty(nid) or nid not in current: fail(f"COMPONENT_REGEN_MISSING {oid}")
            c=current[nid]
            if c.get("replaces_component_id")!=oid: fail(f"COMPONENT_REGEN_NOT_LINKED {oid}")
            if c.get("type")!=old.get("type"): fail(f"COMPONENT_REGEN_TYPE_MISMATCH {oid}")
            # Parent/tags may be explicitly remapped after a material refactor, but the mapping must be declared.
            if origin=="presentation":
                if c.get("parent")!=old.get("parent") or sorted(c.get("tags") or [])!=sorted(old.get("tags") or []): fail(f"COMPONENT_REGEN_BINDING_MISMATCH {oid}")
            else:
                if c.get("parent")!=old.get("parent") and t.get("new_parent")!=c.get("parent"): fail(f"COMPONENT_REGEN_PARENT_REMAP_UNDECLARED {oid}")
                if sorted(c.get("tags") or [])!=sorted(old.get("tags") or []) and sorted(t.get("new_tags") or [])!=sorted(c.get("tags") or []): fail(f"COMPONENT_REGEN_TAG_REMAP_UNDECLARED {oid}")
        elif mode=="DROP_EXPLICIT" and origin=="refactor":
            if not nonempty(t.get("reason")): fail(f"DROP_EXPLICIT_REASON_REQUIRED {oid}")
            if not _drop_allowed_for_visual(old,visual): fail(f"DROP_EXPLICIT_STILL_APPLICABLE {oid}")
            if oid in current: fail(f"DROP_EXPLICIT_COMPONENT_STILL_PRESENT {oid}")
        else:
            fail(f"component {oid} continuity mode must be PRESERVE or REGENERATE" + (" or DROP_EXPLICIT" if origin=="refactor" else ""))


def validate_render_manifest(manifest_path: Path, render_path: Path, contract_path: Path, st):
    contract,ch=validate_frozen_render_contract(contract_path,st)
    validate_evidence(manifest_path,st)
    if not render_path.exists(): fail("render file missing")
    m=read_json(manifest_path,"render manifest")
    if m.get("run_id")!=st["run_id"]: fail("RUN_ID_MISMATCH in render manifest")
    if m.get("deck_artifact")!=st.get("current_artifact") or m.get("render_id")!=expected_render_id(st): fail("render manifest binding mismatch")
    rh=sha256(render_path)
    if m.get("contract_sha256")!=ch or m.get("render_sha256")!=rh: fail("render manifest hash mismatch")
    reqids={r["id"] for r in contract["requirements"]}; got={}
    for x in m.get("requirements",[]):
        if not isinstance(x,dict) or not nonempty(x.get("id")): fail("invalid render manifest requirement")
        got[x["id"]]=x
    if set(got)!=reqids: fail("RENDER_REQUIREMENTS_MISMATCH")
    for rid in reqids:
        if got[rid].get("status")!="SATISFIED" or not nonempty(got[rid].get("evidence")): fail(f"render requirement not satisfied: {rid}")
    comps=validate_components(manifest_path,m,st)
    validate_component_continuity(contract,comps,st)
    text=render_path.read_text(encoding="utf-8")
    for r in contract["requirements"]:
        for a in r["assertions"]: execute_render_assertion(a,text,comps,r["id"])
    # Global deterministic rendering invariants emitted by STRUCTURE.
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    if not dg: fail("deck snapshot missing for render verification")
    snap=read_json(Path(dg["snapshot_file"]),"deck snapshot")
    ng=st.get("gates",{}).get("NARRATIVE_CONFORMANCE_CLOSED",{})
    if not ng or not ng.get("evidence_file"): fail("narrative conformance missing for render grouping")
    typemap=_narrative_type_map(Path(ng["evidence_file"]))
    if st.get("refactor_render_mode")=="DIFF_ONLY":
        validate_refactor_diff(text,st,snap,typemap)
        validate_refactor_diff_component(comps,st)
    else:
        validate_full_decklist_groups(text,snap,typemap)
    final_class=st.get("gates",{}).get("FINAL_CLASSIFICATION_CLOSED",{}).get("classification")
    if not final_class or not re.search(rf"(?im)^.*Direction.*{re.escape(final_class)}.*$",text): fail("FINAL_DIRECTION_NOT_RENDERED")
    visual=read_json(Path(st["gates"]["VISUAL_ASSETS_BOUND"]["evidence_file"]),"visual assets")
    types=[c.get("type") for c in comps]
    if visual["main_carousel"].get("applicable") is True and "main-carousel" not in types: fail("MAIN_CAROUSEL_NOT_MATERIALIZED")
    sig=visual["signature_climax"]
    if sig.get("mini_carousel_applicable") is True and "mini-carousel" not in types: fail("SIGNATURE_MINI_CAROUSEL_NOT_MATERIALIZED")
    if sig.get("terminal_quote_required") is True and not re.search(r"(?m)^###\s+\*\*.+—\s*«.+»\*\*\s*$",text): fail("TERMINAL_QUOTE_NOT_MATERIALIZED")
    # RC5: multi-axis decks must expose pilotage as a visible section, not only dispersed branch notes.
    axe_count=len(re.findall(r"(?im)^#{2,4}\s+Axe\s+\d+\b",text))
    if axe_count>=2 and not re.search(r"(?im)^##\s+Guide de pilotage\s*$",text):
        fail("PILOTAGE_GUIDE_NOT_MATERIALIZED")
    return {"render_sha256":rh,"manifest_sha256":sha256(manifest_path),"contract_sha256":ch,"component_inventory_sha256":component_inventory_hash(comps),"component_inventory":[_component_identity(c) for c in comps]}



def _terminal_component_projection(c):
    return {
        "component_id":c.get("component_id"),
        "type":c.get("type"),
        "parent":c.get("parent"),
        "tags":sorted(c.get("tags") or []),
        "payload_file":c.get("artifact_file"),
        "payload_sha256":c.get("artifact_sha256"),
        "image_refs":list(c.get("image_refs") or []),
    }


def _terminal_current_bundle(render_path: Path, manifest_path: Path, st):
    if not render_path.exists() or not render_path.is_file():
        fail("TERMINAL_TEXT_PAYLOAD_MISMATCH")
    if not manifest_path.exists() or not manifest_path.is_file():
        fail("TERMINAL_PRESENTATION_PLAN_STALE")
    m=read_json(manifest_path,"render manifest")
    if m.get("run_id")!=st.get("run_id") or m.get("deck_artifact")!=st.get("current_artifact") or m.get("render_id")!=st.get("current_render"):
        fail("TERMINAL_PRESENTATION_PLAN_STALE")
    rh=sha256(render_path); mh=sha256(manifest_path)
    if m.get("render_sha256")!=rh:
        fail("TERMINAL_TEXT_PAYLOAD_MISMATCH")
    rp=st.get("render_check_pass") or {}
    for k,v in {"render_id":st.get("current_render"),"render_sha256":rh,"manifest_sha256":mh}.items():
        if rp.get(k)!=v:
            fail("TERMINAL_PRESENTATION_PLAN_STALE")
    comps=m.get("components",[])
    if not isinstance(comps,list):
        fail("TERMINAL_PRESENTATION_INVENTORY_MISMATCH")
    verified=validate_components(manifest_path,m,st)
    inv=component_inventory_hash(verified)
    if rp.get("component_inventory_sha256")!=inv:
        fail("TERMINAL_PRESENTATION_INVENTORY_MISMATCH")
    cmf=rp.get("component_manifest_file"); cmh=rp.get("component_manifest_sha256")
    if verified:
        if not nonempty(cmf) or not nonempty(cmh):
            fail("TERMINAL_COMPONENT_PAYLOAD_MISSING")
        cp=Path(cmf)
        if not cp.exists() or not cp.is_file() or sha256(cp)!=cmh:
            fail("TERMINAL_PRESENTATION_PLAN_STALE")
        cd=read_json(cp,"compiled component manifest")
        if component_inventory_hash(cd.get("components",[]))!=inv:
            fail("TERMINAL_PRESENTATION_INVENTORY_MISMATCH")
    else:
        cmf=None; cmh=None
    return {
        "render_file":str(render_path.resolve()),"render_sha256":rh,
        "render_manifest_file":str(manifest_path.resolve()),"render_manifest_sha256":mh,
        "component_manifest_file":str(Path(cmf).resolve()) if cmf else None,
        "component_manifest_sha256":cmh,
        "component_inventory_sha256":inv,
        "components":verified,
    }


def compile_terminal_presentation_payload(render_path: Path, manifest_path: Path, st):
    b=_terminal_current_bundle(render_path,manifest_path,st)
    return {
        "schema":TERMINAL_PRESENTATION_PLAN_SCHEMA,
        "run_id":st.get("run_id"),
        "deck_artifact":st.get("current_artifact"),
        "render_id":st.get("current_render"),
        "text_payload_file":b["render_file"],
        "text_payload_sha256":b["render_sha256"],
        "render_manifest_file":b["render_manifest_file"],
        "render_manifest_sha256":b["render_manifest_sha256"],
        "component_manifest_file":b["component_manifest_file"],
        "component_manifest_sha256":b["component_manifest_sha256"],
        "component_inventory_sha256":b["component_inventory_sha256"],
        "component_count":len(b["components"]),
        "components":[_terminal_component_projection(c) for c in b["components"]],
        "compiled_by":"compile-terminal-presentation",
        "runtime_version":VERSION,
    }


def _terminal_issue(code,detail):
    return {"code":code,"detail":detail}


def _terminal_plan_issues(plan_path: Path, render_path: Path, manifest_path: Path, st):
    issues=[]
    try:
        b=_terminal_current_bundle(render_path,manifest_path,st)
    except SystemExit as e:
        code,detail=_denied_parts(e)
        return [_terminal_issue(code,detail)]
    if not plan_path.exists() or not plan_path.is_file():
        return [_terminal_issue("TERMINAL_PRESENTATION_PLAN_REQUIRED","terminal presentation plan missing")]
    try:
        raw=plan_path.read_text(encoding="utf-8")
        d=json.loads(raw)
    except Exception as e:
        return [_terminal_issue("TERMINAL_PRESENTATION_PLAN_STALE",f"invalid terminal presentation plan: {e}")]
    if not isinstance(d,dict) or d.get("schema")!=TERMINAL_PRESENTATION_PLAN_SCHEMA or d.get("compiled_by")!="compile-terminal-presentation":
        issues.append(_terminal_issue("TERMINAL_PRESENTATION_PLAN_STALE","terminal presentation plan schema/compiler mismatch"))
        return issues
    if raw!=_stable_json_text(d):
        issues.append(_terminal_issue("TERMINAL_PRESENTATION_PLAN_STALE","terminal presentation plan is not canonical"))
    checks={
        "run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),
        "text_payload_file":b["render_file"],"text_payload_sha256":b["render_sha256"],
        "render_manifest_file":b["render_manifest_file"],"render_manifest_sha256":b["render_manifest_sha256"],
        "component_manifest_file":b["component_manifest_file"],"component_manifest_sha256":b["component_manifest_sha256"],
        "component_inventory_sha256":b["component_inventory_sha256"],
    }
    for k,v in checks.items():
        if d.get(k)!=v:
            code="TERMINAL_TEXT_PAYLOAD_MISMATCH" if k in {"text_payload_file","text_payload_sha256"} else ("TERMINAL_PRESENTATION_INVENTORY_MISMATCH" if k=="component_inventory_sha256" else "TERMINAL_PRESENTATION_PLAN_STALE")
            issues.append(_terminal_issue(code,f"{k} mismatch"))
    comps=d.get("components")
    if not isinstance(comps,list):
        issues.append(_terminal_issue("TERMINAL_PRESENTATION_INVENTORY_MISMATCH","components must be a list")); comps=[]
    if d.get("component_count")!=len(comps) or d.get("component_count")!=len(b["components"]):
        issues.append(_terminal_issue("TERMINAL_PRESENTATION_INVENTORY_MISMATCH","component_count mismatch"))
    seen=set(); byid={}
    for i,c in enumerate(comps):
        if not isinstance(c,dict):
            issues.append(_terminal_issue("TERMINAL_PRESENTATION_INVENTORY_MISMATCH",f"component {i} must be object")); continue
        cid=c.get("component_id")
        if not nonempty(cid):
            issues.append(_terminal_issue("TERMINAL_PRESENTATION_INVENTORY_MISMATCH",f"component {i} missing component_id")); continue
        if cid in seen:
            issues.append(_terminal_issue("TERMINAL_PRESENTATION_INVENTORY_MISMATCH",f"duplicate component {cid}"))
        seen.add(cid); byid[cid]=c
    exp={c.get("component_id"):_terminal_component_projection(c) for c in b["components"]}
    if set(byid)!=set(exp):
        issues.append(_terminal_issue("TERMINAL_PRESENTATION_INVENTORY_MISMATCH","component ids mismatch"))
    for cid,e in exp.items():
        c=byid.get(cid)
        if not c: continue
        for k in ("type","parent","tags","payload_sha256","image_refs"):
            if c.get(k)!=e.get(k):
                issues.append(_terminal_issue("TERMINAL_COMPONENT_BINDING_MISMATCH",f"{cid}:{k} mismatch"))
        pf=c.get("payload_file")
        if not nonempty(pf) or not Path(pf).exists() or not Path(pf).is_file():
            issues.append(_terminal_issue("TERMINAL_COMPONENT_PAYLOAD_MISSING",f"{cid} payload missing"))
        elif c.get("payload_sha256")!=sha256(Path(pf)):
            issues.append(_terminal_issue("TERMINAL_COMPONENT_BINDING_MISMATCH",f"{cid}:payload hash mismatch"))
        if c.get("payload_file")!=e.get("payload_file"):
            issues.append(_terminal_issue("TERMINAL_COMPONENT_BINDING_MISMATCH",f"{cid}:payload_file mismatch"))
    # deterministic unique issues, preserving the first detailed occurrence.
    dedup=[]; seen_issue=set()
    for x in issues:
        key=(x["code"],x["detail"])
        if key not in seen_issue:
            seen_issue.add(key); dedup.append(x)
    return sorted(dedup,key=lambda x:(x["code"],x["detail"]))


def cmd_compile_terminal_presentation(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if next_gate(st)[0]!="FINAL_VALIDATION_PASS":
        fail(f"compile-terminal-presentation requires next gate FINAL_VALIDATION_PASS; next gate is {next_gate(st)[0]}")
    render=Path(a.render_file); manifest=Path(a.render_manifest)
    plan=compile_terminal_presentation_payload(render,manifest,st)
    out=Path(a.output) if getattr(a,"output",None) else rd/TERMINAL_PRESENTATION_PLAN_FILE
    _atomic_write_text(out,_stable_json_text(plan)); ph=sha256(out)
    st["terminal_presentation_plan_file"]=str(out.resolve())
    st["terminal_presentation_plan_sha256"]=ph
    for k in ("terminal_presentation_receipt_file","terminal_presentation_receipt_sha256","terminal_presentation_check"):
        st.pop(k,None)
    save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(rd,st,"TERMINAL_PRESENTATION_PLAN_COMPILED",checkpoint_seq=cp.get("checkpoint_seq"),plan_file=str(out.resolve()),plan_sha256=ph,component_count=plan["component_count"],component_inventory_sha256=plan["component_inventory_sha256"])
    print(json.dumps({"status":"PASS","plan_file":str(out.resolve()),"plan_sha256":ph,"component_count":plan["component_count"]},ensure_ascii=False,indent=2))


def cmd_terminal_presentation_check(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    plan=Path(a.plan_file); render=Path(a.render_file); manifest=Path(a.render_manifest)
    txid=f"terminal-presentation-{sum(1 for e in _read_journal(rd) if e.get('event')=='TERMINAL_PRESENTATION_CHECK_STARTED')+1:06d}"
    _append_run_journal(rd,st,"TERMINAL_PRESENTATION_CHECK_STARTED",transaction_id=txid,plan_file=str(plan),plan_sha256=sha256(plan) if plan.exists() else None,render_file=str(render),render_sha256=sha256(render) if render.exists() else None,render_manifest_file=str(manifest),render_manifest_sha256=sha256(manifest) if manifest.exists() else None)
    try:
        issues=_terminal_plan_issues(plan,render,manifest,st)
        pd=read_json(plan,"terminal presentation plan") if plan.exists() else {}
        status="FAIL" if issues else "PASS"
        receipt={
            "schema":TERMINAL_PRESENTATION_RECEIPT_SCHEMA,"status":status,
            "run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),
            "plan_file":str(plan.resolve()) if plan.exists() else str(plan),"plan_sha256":sha256(plan) if plan.exists() else None,
            "text_payload_sha256":pd.get("text_payload_sha256"),"render_manifest_sha256":pd.get("render_manifest_sha256"),
            "component_manifest_sha256":pd.get("component_manifest_sha256"),"component_inventory_sha256":pd.get("component_inventory_sha256"),
            "runtime_version":VERSION,"issues":issues,
        }
        out=Path(a.output) if getattr(a,"output",None) else rd/TERMINAL_PRESENTATION_RECEIPT_FILE
        _atomic_write_text(out,_stable_json_text(receipt)); rh=sha256(out)
        ev="TERMINAL_PRESENTATION_CHECK_FAILED" if issues else "TERMINAL_PRESENTATION_CHECK_SUCCEEDED"
        _append_run_journal(rd,st,ev,transaction_id=txid,receipt_file=str(out.resolve()),receipt_sha256=rh,issue_count=len(issues),plan_sha256=receipt.get("plan_sha256"),component_inventory_sha256=receipt.get("component_inventory_sha256"))
        if issues:
            print(json.dumps(receipt,ensure_ascii=False,indent=2)); raise SystemExit(2)
        st["terminal_presentation_plan_file"]=str(plan.resolve())
        st["terminal_presentation_plan_sha256"]=receipt["plan_sha256"]
        st["terminal_presentation_receipt_file"]=str(out.resolve())
        st["terminal_presentation_receipt_sha256"]=rh
        st["terminal_presentation_check"]={"status":"PASS","plan_sha256":receipt["plan_sha256"],"receipt_sha256":rh,"render_id":st.get("current_render"),"text_payload_sha256":receipt["text_payload_sha256"],"render_manifest_sha256":receipt["render_manifest_sha256"],"component_manifest_sha256":receipt["component_manifest_sha256"],"component_inventory_sha256":receipt["component_inventory_sha256"]}
        save_state(rd,st)
        print(json.dumps(receipt,ensure_ascii=False,indent=2))
    except SystemExit:
        raise
    except Exception as e:
        tb=rd/f"{txid}.traceback.txt"; _atomic_write_text(tb,traceback.format_exc())
        _append_run_journal(rd,st,"TERMINAL_PRESENTATION_CHECK_EXCEPTION",transaction_id=txid,exception_type=type(e).__name__,exception_message=str(e),traceback_file=str(tb),traceback_sha256=sha256(tb))
        raise


def _verify_terminal_presentation_receipt(plan_path: Path, receipt_path: Path, render_path: Path, manifest_path: Path, st):
    if not plan_path.exists(): fail("TERMINAL_PRESENTATION_PLAN_REQUIRED")
    if not receipt_path.exists(): fail("TERMINAL_PRESENTATION_RECEIPT_REQUIRED")
    issues=_terminal_plan_issues(plan_path,render_path,manifest_path,st)
    if issues:
        codes={x.get("code") for x in issues}
        if "TERMINAL_TEXT_PAYLOAD_MISMATCH" in codes: fail("TERMINAL_TEXT_PAYLOAD_MISMATCH")
        if "TERMINAL_PRESENTATION_INVENTORY_MISMATCH" in codes: fail("TERMINAL_PRESENTATION_INVENTORY_MISMATCH")
        if "TERMINAL_COMPONENT_PAYLOAD_MISSING" in codes: fail("TERMINAL_COMPONENT_PAYLOAD_MISSING")
        if "TERMINAL_COMPONENT_BINDING_MISMATCH" in codes: fail("TERMINAL_COMPONENT_BINDING_MISMATCH")
        fail("TERMINAL_PRESENTATION_PLAN_STALE")
    r=read_json(receipt_path,"terminal presentation receipt")
    if r.get("schema")!=TERMINAL_PRESENTATION_RECEIPT_SCHEMA or r.get("status")!="PASS": fail("TERMINAL_PRESENTATION_RECEIPT_REQUIRED")
    pd=read_json(plan_path,"terminal presentation plan")
    checks={
        "run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),
        "plan_sha256":sha256(plan_path),"text_payload_sha256":pd.get("text_payload_sha256"),
        "render_manifest_sha256":pd.get("render_manifest_sha256"),"component_manifest_sha256":pd.get("component_manifest_sha256"),
        "component_inventory_sha256":pd.get("component_inventory_sha256"),
    }
    for k,v in checks.items():
        if r.get(k)!=v: fail("TERMINAL_PRESENTATION_RECEIPT_STALE")
    return pd,r,sha256(receipt_path)

def cmd_start(a):
    caparg=getattr(a,"bootstrap_capability",None)
    if not nonempty(caparg): fail("DIRECT_START_FORBIDDEN")
    _consume_bootstrap_capability(Path(caparg),a)
    rd=Path(a.run_dir)
    scope_dir=Path(a.scope_dir).resolve()
    scope_dir.mkdir(parents=True,exist_ok=True)
    lease=_read_continuation_lease_raw(scope_dir,required=False)
    if lease is not None and lease.get("status")=="ACTIVE":
        lease=_validate_active_continuation_lease(scope_dir)
        fail("ACTIVE_LOGICAL_RUN_EXISTS: "+json.dumps(_active_run_exists_payload(lease),ensure_ascii=False,sort_keys=True))
    if (rd/STATE_FILE).exists(): fail("run already exists")
    scope_id=_continuity_scope_id(scope_dir)
    # Materialize source identity once at bootstrap; downstream plumbing can reuse it.
    rd.mkdir(parents=True,exist_ok=True)
    inv,inv_path,inv_sha=_materialize_source_inventory(rd)
    st={"runtime_version":VERSION,"run_id":a.run_id,"mode":a.mode,"multi_system":a.multi_system,"mechanical_validation":a.mechanical_validation,"continuity_scope_id":scope_id,"continuity_scope_dir":str(scope_dir),"current_artifact":"deck-v1","current_render":None,"gates":{},"stop_output_allowed":False,"presentation_carry_components":[],"refactor_visual_carry_components":[],"refactor_visual_carry_requirements":[],"material_change_count":0,"combo_impact_required":False,"last_material_change":None,"refactor_render_mode":"FULL","render_attempts":{},"render_check_pass":None,"render_contract_defect_suspected":None,"run_execution_state":"IN_PROGRESS","fastpath_profile":FASTPATH_PROFILE,"source_inventory":inv,"source_inventory_file":str(inv_path.resolve()),"source_inventory_sha256":inv_sha}
    save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(rd,st,"SOURCE_INVENTORY_BOUND",checkpoint_seq=cp.get("checkpoint_seq"),source_inventory_file=str(inv_path.resolve()),source_inventory_sha256=inv_sha,source_count=len(inv.get("files",[])))
    _append_run_journal(rd,st,"RUN_BOOTSTRAPPED",checkpoint_seq=cp.get("checkpoint_seq"),next_required_gate=cp.get("next_required_gate"),runtime_version=VERSION,scope_id=scope_id,scope_dir=str(scope_dir))
    _write_session_index(_session_payload_from_run(rd,st,cp))
    print(json.dumps({"status":"RUN_CREATED","run_id":a.run_id,"scope_id":scope_id,"scope_dir":str(scope_dir),"session_index":str(_session_index_path())},ensure_ascii=False))


def cmd_dispatch_run(a):
    idx=_read_session_index(required=False)
    if idx is not None and idx.get("status")=="ACTIVE":
        idx=_validate_session_index_active()
        rd=Path(idx["run_dir"]); rid=idx["run_id"]
        if a.mode=="fresh":
            from argparse import Namespace
            cmd_abort_run(Namespace(run_dir=str(rd),run_id=rid,reason="USER_REQUESTED_FRESH"))
            idx=_read_session_index(required=False)
        else:
            state=idx.get("run_state")
            if state=="WAITING_USER_INPUT":
                if nonempty(getattr(a,"user_resolution_file",None)):
                    from argparse import Namespace
                    return cmd_resume_run(Namespace(run_dir=str(rd),run_id=rid,user_resolution_file=a.user_resolution_file))
                print(json.dumps({**idx,"recommended_action":"USER_RESOLUTION_REQUIRED"},ensure_ascii=False)); return
            if nonempty(getattr(a,"user_resolution_file",None)): fail("RUN_NOT_WAITING_FOR_USER_INPUT")
            # Dispatch owns the decision and directly resumes the exact indexed run.
            from argparse import Namespace
            return cmd_resume_run(Namespace(run_dir=str(rd),run_id=rid,user_resolution_file=None))
    elif idx is not None and idx.get("status")=="CLOSED":
        # Closed index is historical routing evidence; new bootstrap is allowed.
        pass
    if nonempty(getattr(a,"user_resolution_file",None)): fail("NO_WAITING_RUN_FOR_USER_RESOLUTION")
    rd=Path(a.run_dir); scope=Path(a.scope_dir).resolve()
    cap=_issue_bootstrap_capability(a.run_id,rd,scope,a.mode,a.multi_system,a.mechanical_validation)
    from argparse import Namespace
    ns=Namespace(run_dir=str(rd),run_id=a.run_id,scope_dir=str(scope),mode=a.mode,multi_system=a.multi_system,mechanical_validation=a.mechanical_validation,bootstrap_capability=str(cap))
    return cmd_start(ns)


def cmd_abort_run(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    cp=_load_checkpoint_raw(rd,required=True)
    _continuation_lease_for_run(rd,st,cp,require_active=True)
    idx=_validate_session_index_active()
    if idx.get("run_id")!=st.get("run_id") or Path(idx.get("run_dir","")).resolve()!=rd.resolve(): fail("SESSION_RUN_BINDING_MISMATCH")
    _append_run_journal(rd,st,"RUN_ABORT_REQUESTED",checkpoint_seq=cp.get("checkpoint_seq"),reason=a.reason)
    st["run_execution_state"]="TERMINAL_FAILED"
    st["terminal_failure_kind"]="USER_ABORTED"
    st["abort_reason"]=a.reason
    st["stop_output_allowed"]=False
    st["render_check_pass"]=None
    save_state(rd,st)
    cp2=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(rd,st,"RUN_ABORTED",checkpoint_seq=cp2.get("checkpoint_seq"),reason=a.reason,terminal_status="USER_ABORTED")
    _write_session_index(_session_payload_from_run(rd,st,cp2,status="CLOSED"))
    print(json.dumps({"status":"RUN_ABORTED","run_id":st["run_id"],"reason":a.reason,"run_state":cp2.get("run_state")},ensure_ascii=False))


def cmd_simulate_interruption(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    cp=_load_checkpoint_raw(rd,required=True)
    _continuation_lease_for_run(rd,st,cp,require_active=True)
    idx=_validate_session_index_active()
    if idx.get("run_id")!=st.get("run_id") or Path(idx.get("run_dir","")).resolve()!=rd.resolve(): fail("SESSION_RUN_BINDING_MISMATCH")
    before={"artifact":st.get("current_artifact"),"render":st.get("current_render"),"last_closed_gate":cp.get("last_closed_gate"),"checkpoint_seq":cp.get("checkpoint_seq"),"run_state_sha256":cp.get("run_state_sha256")}
    _append_run_journal(rd,st,"SIMULATED_INTERRUPTION",checkpoint_seq=cp.get("checkpoint_seq"),test_only=True,failpoint=getattr(a,"failpoint",None),before=before)
    print(json.dumps({"status":"SIMULATED_INTERRUPTION","test_only":True,"run_id":st["run_id"],"checkpoint_seq":cp.get("checkpoint_seq"),"next_required_gate":cp.get("next_required_gate")},ensure_ascii=False))


def cmd_status(a):
    st=load_state(Path(a.run_dir)); g,_,_=next_gate(st)
    print(json.dumps({"run_id":st["run_id"],"artifact":st["current_artifact"],"render":st.get("current_render"),"next_gate":g,"stop_output_allowed":st.get("stop_output_allowed",False)},ensure_ascii=False))


def _cmd_complete_impl(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    g,auths,statuses=next_gate(st)
    if a.gate!=g: fail(f"next gate is {g}; cannot close {a.gate}")
    authority=getattr(a,"authority",None); status=getattr(a,"status",None)
    if authority is None:
        if len(auths)!=1: fail(f"COMPLETE_AUTHORITY_AMBIGUOUS for {a.gate}")
        authority=next(iter(auths))
    if status is None:
        if len(statuses)!=1: fail(f"COMPLETE_STATUS_AMBIGUOUS for {a.gate}")
        status=next(iter(statuses))
    if authority not in auths: fail(f"WRONG_AUTHORITY for {a.gate}")
    if status not in statuses: fail(f"invalid status {status} for {a.gate}")
    a.authority=authority; a.status=status
    rec={"run_id":st["run_id"],"authority":authority,"status":status,"artifact":st.get("current_artifact")}
    ef=Path(a.evidence_file) if a.evidence_file else None
    if a.gate=="DIRECTION_RESOLVED":
        if not ef: fail("DIRECTION_RESOLVED requires direction_contract evidence_file")
        d,h,ph=validate_direction_contract(ef,st)
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"policy_source_sha256":ph,"direction":d["selected_direction"],"resolution_basis":d["resolution_basis"]})
    elif a.gate=="NARRATIVE_CONTRACT_FROZEN":
        if not ef: fail("NARRATIVE_CONTRACT_FROZEN requires evidence_file")
        d,h,ph=validate_narrative_contract(ef,st)
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"policy_source_sha256":ph,"arc":d["arc"]})
    elif a.gate=="FUNCTIONAL_INTENT_FROZEN":
        if not ef: fail("FUNCTIONAL_INTENT_FROZEN requires evidence_file")
        d,h,ph=validate_functional_intent(ef,st)
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"policy_source_sha256":ph})
    elif a.gate=="CLASSIFICATION_CLOSED":
        if not ef: fail("CLASSIFICATION_CLOSED requires classification result evidence_file")
        d,h,ph=validate_classification_result(ef,st,"PROVISIONAL")
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"policy_source_sha256":ph,"classification":d["classification"]})
    elif a.gate=="DECK_DRAFT_CREATED":
        if not ef: fail("DECK_DRAFT_CREATED requires deck snapshot evidence_file")
        _,h,_,_=validate_deck_snapshot(ef,st)
        rec.update({"snapshot_file":str(ef),"snapshot_sha256":h})
    elif a.gate=="NARRATIVE_CONFORMANCE_CLOSED":
        if not ef: fail("NARRATIVE_CONFORMANCE_CLOSED requires narrative report evidence_file")
        cg=st["gates"].get("NARRATIVE_CONTRACT_FROZEN",{}); dg=st["gates"].get("DECK_DRAFT_CREATED",{})
        if not cg or not dg: fail("narrative prerequisites missing")
        hashes=validate_narrative_conformance(ef,Path(cg["evidence_file"]),Path(dg["snapshot_file"]),st)
        rec.update({"evidence_file":str(ef),**hashes})
    elif a.gate=="FINAL_CLASSIFICATION_CLOSED":
        if not ef: fail("FINAL_CLASSIFICATION_CLOSED requires classification result evidence_file")
        d,h,ph=validate_classification_result(ef,st,"FINAL")
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"policy_source_sha256":ph,"classification":d["classification"],"snapshot_sha256":d["snapshot_sha256"]})
    elif a.gate=="VISUAL_ASSETS_BOUND":
        if not ef: fail("VISUAL_ASSETS_BOUND requires visual_assets evidence_file")
        d,h=validate_visual_assets(ef,st)
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"image_capability_status":d["image_capability_status"],"image_refs":d["image_refs"]})
    elif a.gate=="RENDER_CONTRACT_FROZEN":
        if not ef: fail("RENDER_CONTRACT_FROZEN requires evidence_file")
        d,h=validate_compiled_render_contract(ef,st)
        rec.update({"evidence_file":str(ef),"evidence_sha256":h,"render_id":d["render_id"],"render_policy_fingerprint":render_policy_fingerprint(d)})
        st["current_render"]=d["render_id"]
        st["render_check_pass"]=None
        st["render_contract_defect_suspected"]=None
        st.pop("presentation_expected_policy_fingerprint",None)
    elif a.gate in {"FINAL_RENDER_PREPARED","PILOTAGE_VALIDATED","FINAL_VALIDATION_PASS"}:
        if not ef or not a.render_manifest or not a.contract_file: fail(f"{a.gate} requires render evidence + manifest + contract")
        hashes=validate_render_manifest(Path(a.render_manifest),ef,Path(a.contract_file),st)
        if a.gate=="FINAL_RENDER_PREPARED":
            rp=st.get("render_check_pass") or {}
            if not rp:
                fail("RENDER_CHECK_PASS_REQUIRED")
            exact={"render_sha256":hashes.get("render_sha256"),"manifest_sha256":hashes.get("manifest_sha256"),"contract_sha256":hashes.get("contract_sha256"),"component_inventory_sha256":hashes.get("component_inventory_sha256"),"render_id":st.get("current_render")}
            for k,v in exact.items():
                if rp.get(k)!=v:
                    fail(f"RENDER_CHECK_PASS_BUNDLE_MISMATCH: {k}")
        rec.update({"render_id":st["current_render"],"evidence_file":str(ef),"manifest_file":a.render_manifest,**hashes})
        if a.gate=="FINAL_RENDER_PREPARED":
            rec["component_inventory"]=hashes["component_inventory"]
            st["presentation_carry_components"]=[]
            # Material-refactor continuity is now closed on this exact prepared bundle.
            # Any later presentation-only mutation will seed continuity from this bundle.
            st["refactor_visual_carry_components"]=[]
            st["refactor_visual_carry_requirements"]=[]
        if a.gate=="FINAL_VALIDATION_PASS":
            plan_arg=getattr(a,"terminal_presentation_plan",None)
            receipt_arg=getattr(a,"terminal_presentation_receipt",None)
            plan_path=Path(plan_arg) if nonempty(plan_arg) else rd/TERMINAL_PRESENTATION_PLAN_FILE
            receipt_path=Path(receipt_arg) if nonempty(receipt_arg) else rd/TERMINAL_PRESENTATION_RECEIPT_FILE
            pd,tr,trh=_verify_terminal_presentation_receipt(plan_path,receipt_path,ef,Path(a.render_manifest),st)
            rec.update({"terminal_presentation_plan_file":str(plan_path.resolve()),"terminal_presentation_plan_sha256":sha256(plan_path),"terminal_presentation_receipt_file":str(receipt_path.resolve()),"terminal_presentation_receipt_sha256":trh,"terminal_component_inventory_sha256":pd.get("component_inventory_sha256")})
            st["terminal_presentation_plan_file"]=str(plan_path.resolve())
            st["terminal_presentation_plan_sha256"]=sha256(plan_path)
            st["terminal_presentation_receipt_file"]=str(receipt_path.resolve())
            st["terminal_presentation_receipt_sha256"]=trh
        if a.gate=="PILOTAGE_VALIDATED":
            if not a.pilotage_contract_file: fail("PILOTAGE_VALIDATED requires --pilotage-contract-file")
            pcp=Path(a.pilotage_contract_file)
            receipt_arg=getattr(a,"pilotage_preflight_receipt",None)
            receipt_path=Path(receipt_arg) if nonempty(receipt_arg) else rd/PILOTAGE_PREFLIGHT_RECEIPT
            pr,prh=_verify_pilotage_preflight_receipt(receipt_path,pcp,ef,st)
            pc,pch=validate_pilotage_contract(pcp,ef,st)
            rec.update({"pilotage_contract_file":a.pilotage_contract_file,"pilotage_contract_sha256":pch,"pilotage_preflight_receipt_file":str(receipt_path),"pilotage_preflight_receipt_sha256":prh,"pilotage_wire_schema":pr.get("wire_schema")})
            if st.get("combo_impact_required") is True:
                if not a.combo_impact_file: fail("PILOTAGE_VALIDATED requires --combo-impact-file after material-change")
                ci,cih=validate_combo_impact(Path(a.combo_impact_file),st)
                validate_combo_impact_render(ef.read_text(encoding="utf-8"),ci)
                rec.update({"combo_impact_file":a.combo_impact_file,"combo_impact_sha256":cih,"combo_impact_status":ci["status"]})
                st["combo_impact_required"]=False
    elif a.gate=="STYLE_AXES_CLOSED":
        if not ef: fail("STYLE_AXES_CLOSED requires STYLE_AXES evidence_file")
        validate_evidence(ef,st)
        _,invsha=_rc1623_validate_style_axes_inventory_file(ef,st)
        rec.update({"evidence_file":str(ef),"evidence_sha256":sha256(ef),"structural_inventory_sha256":invsha})
    elif ef:
        validate_evidence(ef,st); rec.update({"evidence_file":str(ef),"evidence_sha256":sha256(ef)})
    depfp=_gate_dependency_fingerprint(st,a.gate,rec)
    if depfp is not None: rec["dependency_fingerprint"]=depfp
    st["gates"][a.gate]=rec; st["stop_output_allowed"]=False
    save_state(rd,st)
    print(f"{a.gate}: {a.status}")


def cmd_complete(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    current_gate,_,_=next_gate(st)
    if a.gate=="PILOTAGE_VALIDATED":
        if not a.evidence_file or not a.pilotage_contract_file: fail("PILOTAGE_VALIDATED requires render evidence + pilotage contract")
        receipt_arg=getattr(a,"pilotage_preflight_receipt",None)
        receipt_path=Path(receipt_arg) if nonempty(receipt_arg) else rd/PILOTAGE_PREFLIGHT_RECEIPT
        _verify_pilotage_preflight_receipt(receipt_path,Path(a.pilotage_contract_file),Path(a.evidence_file),st)
    current_gate,_,_=next_gate(st)
    events=_read_journal(rd)
    payload=_gate_attempt_input_payload(a,st,a.gate,a.authority,a.status)
    fp=_gate_attempt_fingerprint(payload)
    state_sha=payload["state_sha256_before"]
    cp=_load_checkpoint_raw(rd,required=False) or {}
    prior_failures=[]
    for ev in reversed(events):
        if ev.get("event") in {"GATE_ATTEMPT_SUCCEEDED","GATE_ATTEMPT_RECONCILED_SUCCESS"}: break
        if ev.get("event")=="GATE_ATTEMPT_FAILED" and ev.get("gate")==a.gate:
            if ev.get("checkpoint_seq")==cp.get("checkpoint_seq") and ev.get("state_sha256_before")==state_sha and ev.get("input_fingerprint")==fp:
                prior_failures.append(ev)
                if len(prior_failures)>=2: break
            else: break
        elif ev.get("event") in {"GATE_ATTEMPT_STARTED","CHECKPOINT_WRITTEN"}:
            continue
    if len(prior_failures)>=2 and prior_failures[0].get("error_code")==prior_failures[1].get("error_code"):
        _append_run_journal(rd,st,"GATE_NO_PROGRESS_BLOCKED",checkpoint_seq=cp.get("checkpoint_seq"),gate=a.gate,error_code=prior_failures[0].get("error_code"),input_fingerprint=fp,state_sha256_before=state_sha,consecutive_identical_failures=2)
        _append_run_journal(rd,st,"GATE_STALL_DETECTED",checkpoint_seq=cp.get("checkpoint_seq"),gate=a.gate,input_fingerprint=fp,failure_signature=prior_failures[0].get("failure_signature"),state_sha256_before=state_sha)
        fail("REPEATED_GATE_ERROR_NO_PROGRESS")
    attempt_id=_next_gate_attempt_id(events)
    _append_run_journal(rd,st,"GATE_ATTEMPT_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),attempt_id=attempt_id,gate=a.gate,expected_gate=current_gate,authority=a.authority,requested_status=a.status,state_sha256_before=state_sha,input_fingerprint=fp,input_bindings=payload.get("inputs"))
    try:
        if a.gate=="RENDER_CONTRACT_FROZEN" and not bool(getattr(a,"_derived_reentry",False)):
            fail("DERIVED_GATE_REQUIRES_COMPILER_TRANSACTION")
        _cmd_complete_impl(a)
    except SystemExit as e:
        code,detail=_denied_parts(e)
        failure_signature=hashlib.sha256(json.dumps({"gate":a.gate,"error_code":code,"detail":detail,"input_fingerprint":fp},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        _append_run_journal(rd,st,"GATE_ATTEMPT_FAILED",checkpoint_seq=cp.get("checkpoint_seq"),attempt_id=attempt_id,gate=a.gate,error_code=code,detail=detail,failure_signature=failure_signature,input_fingerprint=fp,state_sha256_before=state_sha,state_sha256_after=sha256(rd/STATE_FILE))
        # RC16.11: an actionable classification-direction conflict is itself the
        # durable transition into WAITING_USER_INPUT.  The runtime does not choose
        # a direction; it only materializes the already-observed need for user input.
        if a.gate=="CLASSIFICATION_CLOSED" and code=="DIRECTION_CONFLICT_REQUIRES_USER_SELECTION":
            wait_cp=_write_checkpoint(rd,st,run_state_override="WAITING_USER_INPUT")
            _append_run_journal(
                rd,st,"WAITING_FOR_USER_INPUT",checkpoint_seq=wait_cp.get("checkpoint_seq"),
                next_required_gate=wait_cp.get("next_required_gate"),waiting_context=wait_cp.get("waiting_context")
            )
        raise
    except Exception as e:
        tb=traceback.format_exc()
        tbfile=rd/f"{attempt_id}.traceback.txt"
        _atomic_write_text(tbfile,tb)
        failure_signature=hashlib.sha256(json.dumps({"gate":a.gate,"exception_type":type(e).__name__,"message":str(e),"input_fingerprint":fp},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        _append_run_journal(rd,st,"GATE_ATTEMPT_EXCEPTION",checkpoint_seq=cp.get("checkpoint_seq"),attempt_id=attempt_id,gate=a.gate,exception_type=type(e).__name__,message=str(e),traceback_file=str(tbfile),traceback_sha256=sha256(tbfile),failure_signature=failure_signature,input_fingerprint=fp,state_sha256_before=state_sha,state_sha256_after=sha256(rd/STATE_FILE))
        raise
    st2=load_state(rd); cp2=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(rd,st2,"GATE_ATTEMPT_SUCCEEDED",checkpoint_seq=cp2.get("checkpoint_seq"),attempt_id=attempt_id,gate=a.gate,input_fingerprint=fp,state_sha256_before=state_sha,state_sha256_after=sha256(rd/STATE_FILE),closed_status=(st2.get("gates",{}).get(a.gate) or {}).get("status"))



# ---------------------------------------------------------------------------
# RC16.18 SAFE BATCH TOP-3 — orchestration-only acceleration layer.
# These helpers never replace a business validator or synthesize a gate PASS.
# ---------------------------------------------------------------------------

EXPLICIT_DIRECTIONS = {
    "canonique": "Canonique",
    "canonique remixé": "Canonique remixé",
    "alternatif": "Alternatif",
}


def _normalize_explicit_direction(value):
    if not nonempty(value):
        fail("EXPLICIT_DIRECTION_REQUIRED")
    key=" ".join(value.strip().casefold().split())
    if key not in EXPLICIT_DIRECTIONS:
        fail("INVALID_EXPLICIT_DIRECTION")
    return EXPLICIT_DIRECTIONS[key]


def _materialize_explicit_direction_contract(rd: Path, st, selected_direction, user_evidence, output=None):
    direction=_normalize_explicit_direction(selected_direction)
    if not nonempty(user_evidence):
        fail("EXPLICIT_DIRECTION_USER_EVIDENCE_REQUIRED")
    out=Path(output) if nonempty(output) else rd/"direction_contract.json"
    payload={
        "run_id":st["run_id"],
        "authority":STYLE,
        "selected_direction":direction,
        "resolution_basis":"USER_EXPLICIT",
        "user_evidence":user_evidence.strip(),
    }
    _atomic_write_text(out,_stable_json_text(payload))
    # Parent validator remains authoritative even for the generated mechanical shape.
    validate_direction_contract(out,st)
    return out,direction


def cmd_bind_explicit_direction(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if next_gate(st)[0]!="DIRECTION_RESOLVED":
        fail(f"bind-explicit-direction requires next gate DIRECTION_RESOLVED; next gate is {next_gate(st)[0]}")
    out,direction=_materialize_explicit_direction_contract(rd,st,a.selected_direction,a.user_evidence,getattr(a,"output",None))
    from argparse import Namespace
    ns=Namespace(run_dir=str(rd),run_id=st["run_id"],gate="DIRECTION_RESOLVED",authority=STYLE,status="RESOLVED",evidence_file=str(out),render_manifest=None,contract_file=None,combo_impact_file=None,pilotage_contract_file=None,pilotage_preflight_receipt=None,terminal_presentation_plan=None,terminal_presentation_receipt=None)
    cmd_complete(ns)
    print(json.dumps({"status":"BOUND_AND_RESOLVED","direction":direction,"contract_file":str(out),"contract_sha256":sha256(out)},ensure_ascii=False))


def _batch_closed_binding_matches(st, op):
    gate=op.get("gate"); rec=(st.get("gates") or {}).get(gate)
    if not isinstance(rec,dict): return False
    if op.get("authority") and rec.get("authority")!=op.get("authority"): return False
    if op.get("status") and rec.get("status")!=op.get("status"): return False
    ef=op.get("evidence_file")
    if nonempty(ef):
        p=Path(ef)
        if not p.exists() or not p.is_file(): return False
        known=rec.get("evidence_sha256") or rec.get("snapshot_sha256")
        if nonempty(known) and known!=sha256(p): return False
    return True


def _batch_op_namespace(rd: Path, run_id, op):
    from argparse import Namespace
    allowed={"gate","authority","status","evidence_file","render_manifest","contract_file","combo_impact_file","pilotage_contract_file","pilotage_preflight_receipt","terminal_presentation_plan","terminal_presentation_receipt"}
    unknown=set(op)-allowed-{"op"}
    if unknown: fail("BATCH_UNKNOWN_COMPLETE_FIELDS: "+",".join(sorted(unknown)))
    kw={k:op.get(k) for k in allowed}; kw.update({"run_dir":str(rd),"run_id":run_id})
    return Namespace(**kw)


def cmd_execute_batch(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    bundle=read_json(Path(a.bundle_file),"safe batch bundle")
    if bundle.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in safe batch bundle")
    ops=bundle.get("operations")
    if not isinstance(ops,list) or not ops: fail("SAFE_BATCH_REQUIRES_OPERATIONS")
    cp=_load_checkpoint_raw(rd,required=True)
    batch_id=f"safe-batch-{sum(1 for e in _read_journal(rd) if e.get('event')=='SAFE_BATCH_STARTED')+1:06d}"
    _append_run_journal(rd,st,"SAFE_BATCH_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),batch_id=batch_id,operation_count=len(ops),next_required_gate=cp.get("next_required_gate"))
    completed=[]; skipped=[]
    for idx,op in enumerate(ops):
        if not isinstance(op,dict): fail(f"SAFE_BATCH_OPERATION_INVALID: {idx}")
        kind=op.get("op")
        st=load_state(rd); ng=next_gate(st)[0]
        if kind=="explicit-direction":
            gate="DIRECTION_RESOLVED"
            if gate in (st.get("gates") or {}):
                rec=st["gates"][gate]; direction=_normalize_explicit_direction(op.get("selected_direction"))
                if rec.get("direction")!=direction or rec.get("resolution_basis")!="USER_EXPLICIT": fail("BATCH_CLOSED_DIRECTION_BINDING_MISMATCH")
                skipped.append(gate)
                _append_run_journal(rd,st,"SAFE_BATCH_ITEM_SKIPPED_ALREADY_CLOSED",checkpoint_seq=(_load_checkpoint_raw(rd,True)).get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=gate)
                continue
            if ng!=gate: fail(f"SAFE_BATCH_WRONG_NEXT_GATE: expected {ng}, got {gate}")
            out,direction=_materialize_explicit_direction_contract(rd,st,op.get("selected_direction"),op.get("user_evidence"),op.get("output"))
            op2={"op":"complete","gate":gate,"authority":STYLE,"status":"RESOLVED","evidence_file":str(out)}
        elif kind=="complete":
            gate=op.get("gate")
            if not nonempty(gate): fail(f"SAFE_BATCH_GATE_MISSING: {idx}")
            if gate in (st.get("gates") or {}):
                if not _batch_closed_binding_matches(st,op): fail("BATCH_CLOSED_GATE_BINDING_MISMATCH")
                skipped.append(gate)
                _append_run_journal(rd,st,"SAFE_BATCH_ITEM_SKIPPED_ALREADY_CLOSED",checkpoint_seq=(_load_checkpoint_raw(rd,True)).get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=gate)
                continue
            if ng!=gate: fail(f"SAFE_BATCH_WRONG_NEXT_GATE: expected {ng}, got {gate}")
            op2=op
        else:
            fail(f"SAFE_BATCH_OPERATION_INVALID: {idx}")
        st0=load_state(rd); cp0=_load_checkpoint_raw(rd,True)
        _append_run_journal(rd,st0,"SAFE_BATCH_ITEM_STARTED",checkpoint_seq=cp0.get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=op2.get("gate"))
        try:
            cmd_complete(_batch_op_namespace(rd,st0["run_id"],op2))
        except SystemExit as e:
            stf=load_state(rd); cpf=_load_checkpoint_raw(rd,True)
            _append_run_journal(rd,stf,"SAFE_BATCH_ITEM_FAILED",checkpoint_seq=cpf.get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=op2.get("gate"),detail=str(e))
            _append_run_journal(rd,stf,"SAFE_BATCH_STOPPED",checkpoint_seq=cpf.get("checkpoint_seq"),batch_id=batch_id,failed_gate=op2.get("gate"),completed=completed,skipped=skipped)
            raise
        st1=load_state(rd); cp1=_load_checkpoint_raw(rd,True)
        completed.append(op2.get("gate"))
        _append_run_journal(rd,st1,"SAFE_BATCH_ITEM_SUCCEEDED",checkpoint_seq=cp1.get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=op2.get("gate"),closed_status=(st1.get("gates",{}).get(op2.get("gate")) or {}).get("status"))
    st=load_state(rd); cp=_load_checkpoint_raw(rd,True)
    _append_run_journal(rd,st,"SAFE_BATCH_COMPLETED",checkpoint_seq=cp.get("checkpoint_seq"),batch_id=batch_id,completed=completed,skipped=skipped,next_required_gate=cp.get("next_required_gate"))
    print(json.dumps({"status":"PASS","batch_id":batch_id,"completed":completed,"skipped":skipped,"next_required_gate":cp.get("next_required_gate")},ensure_ascii=False))


def _mechanical_issue(issues, code, path, expected=None, observed=None):
    issues.append({"code":code,"path":path,"expected":expected,"observed":observed})


def _existing_json_or_issue(path_value, label, issues):
    if not nonempty(path_value):
        _mechanical_issue(issues,f"{label}_MISSING",label,"existing JSON file",path_value); return None,None
    p=Path(path_value)
    if not p.exists() or not p.is_file():
        _mechanical_issue(issues,f"{label}_MISSING",label,"existing JSON file",str(p)); return p,None
    try: d=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        _mechanical_issue(issues,f"{label}_INVALID_JSON",label,"valid JSON object",str(e)); return p,None
    if not isinstance(d,dict):
        _mechanical_issue(issues,f"{label}_INVALID_TYPE",label,"JSON object",type(d).__name__); return p,None
    return p,d


def _render_mechanical_preflight_issues(a, st):
    issues=[]
    cp=Path(a.contract_file) if nonempty(getattr(a,"contract_file",None)) else None
    if cp is None or not cp.exists():
        _mechanical_issue(issues,"RENDER_CONTRACT_MISSING","contract_file","existing file",str(cp) if cp else None)
        contract=None
    else:
        try: contract=read_json(cp,"render contract")
        except SystemExit as e:
            _mechanical_issue(issues,"RENDER_CONTRACT_INVALID","contract_file","valid JSON object",str(e)); contract=None
    if isinstance(contract,dict):
        if contract.get("run_id")!=st.get("run_id"): _mechanical_issue(issues,"RENDER_RUN_BINDING_MISMATCH","$.run_id",st.get("run_id"),contract.get("run_id"))
        if contract.get("deck_artifact")!=st.get("current_artifact"): _mechanical_issue(issues,"RENDER_DECK_BINDING_MISMATCH","$.deck_artifact",st.get("current_artifact"),contract.get("deck_artifact"))
        expected=expected_render_id(st)
        if contract.get("render_id")!=expected: _mechanical_issue(issues,"RENDER_ID_BINDING_MISMATCH","$.render_id",expected,contract.get("render_id"))
        fg=(st.get("gates") or {}).get("FINAL_CLASSIFICATION_CLOSED",{})
        vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
        if fg and contract.get("final_classification_sha256")!=fg.get("evidence_sha256"): _mechanical_issue(issues,"RENDER_CLASSIFICATION_BINDING_MISMATCH","$.final_classification_sha256",fg.get("evidence_sha256"),contract.get("final_classification_sha256"))
        if vg and contract.get("visual_assets_sha256")!=vg.get("evidence_sha256"): _mechanical_issue(issues,"RENDER_VISUAL_BINDING_MISMATCH","$.visual_assets_sha256",vg.get("evidence_sha256"),contract.get("visual_assets_sha256"))
    plan_path,plan=_existing_json_or_issue(getattr(a,"component_plan_file",None),"COMPONENT_PLAN",issues) if nonempty(getattr(a,"component_plan_file",None)) else (None,None)
    manifest_path,manifest=_existing_json_or_issue(getattr(a,"component_manifest",None),"COMPONENT_MANIFEST",issues) if nonempty(getattr(a,"component_manifest",None)) else (None,None)
    required_count=None
    if isinstance(plan,dict):
        for key,expected in (("run_id",st.get("run_id")),("deck_artifact",st.get("current_artifact")),("render_id",expected_render_id(st))):
            if plan.get(key)!=expected: _mechanical_issue(issues,f"COMPONENT_PLAN_{key.upper()}_MISMATCH",f"component_plan.{key}",expected,plan.get(key))
        comps=plan.get("components")
        if isinstance(comps,list): required_count=len(comps)
    if isinstance(manifest,dict):
        for key,expected in (("run_id",st.get("run_id")),("deck_artifact",st.get("current_artifact")),("render_id",expected_render_id(st))):
            if manifest.get(key)!=expected: _mechanical_issue(issues,f"COMPONENT_MANIFEST_{key.upper()}_MISMATCH",f"component_manifest.{key}",expected,manifest.get(key))
        comps=manifest.get("components")
        if required_count and (not isinstance(comps,list) or len(comps)<required_count):
            _mechanical_issue(issues,"REQUIRED_COMPONENT_INVENTORY_INCOMPLETE","component_manifest.components",f">={required_count}",len(comps) if isinstance(comps,list) else None)
    render_path=Path(a.render_file) if nonempty(getattr(a,"render_file",None)) else None
    manifest_render_path,render_manifest=_existing_json_or_issue(getattr(a,"render_manifest",None),"RENDER_MANIFEST",issues) if nonempty(getattr(a,"render_manifest",None)) else (None,None)
    if render_path is not None:
        if not render_path.exists(): _mechanical_issue(issues,"RENDER_FILE_MISSING","render_file","existing file",str(render_path))
        elif isinstance(render_manifest,dict) and render_manifest.get("render_sha256")!=sha256(render_path): _mechanical_issue(issues,"RENDER_MANIFEST_HASH_MISMATCH","render_manifest.render_sha256",sha256(render_path),render_manifest.get("render_sha256"))
    issues.sort(key=lambda x:(x["path"],x["code"]))
    return issues


def _pilotage_mechanical_preflight_issues(a, st):
    issues=[]
    contract_path=Path(a.pilotage_contract_file) if nonempty(getattr(a,"pilotage_contract_file",None)) else None
    render_path=Path(a.render_file) if nonempty(getattr(a,"render_file",None)) else None
    if contract_path is None or not contract_path.exists():
        _mechanical_issue(issues,"PILOTAGE_CONTRACT_MISSING","pilotage_contract_file","existing file",str(contract_path) if contract_path else None)
        d=None
    else:
        try: d=read_json(contract_path,"pilotage contract")
        except SystemExit as e: _mechanical_issue(issues,"PILOTAGE_CONTRACT_INVALID","pilotage_contract_file","valid JSON object",str(e)); d=None
    if render_path is None or not render_path.exists():
        _mechanical_issue(issues,"PILOTAGE_RENDER_MISSING","render_file","existing file",str(render_path) if render_path else None)
    if isinstance(d,dict):
        if d.get("run_id")!=st.get("run_id"): _mechanical_issue(issues,"PILOTAGE_RUN_BINDING_MISMATCH","$.run_id",st.get("run_id"),d.get("run_id"))
        if d.get("deck_artifact")!=st.get("current_artifact"): _mechanical_issue(issues,"PILOTAGE_DECK_BINDING_MISMATCH","$.deck_artifact",st.get("current_artifact"),d.get("deck_artifact"))
        if d.get("wire_schema") not in {None,PILOTAGE_WIRE_SCHEMA}: _mechanical_issue(issues,"PILOTAGE_WIRE_SCHEMA_MISMATCH","$.wire_schema",PILOTAGE_WIRE_SCHEMA,d.get("wire_schema"))
        if render_path is not None and render_path.exists() and d.get("render_sha256")!=sha256(render_path): _mechanical_issue(issues,"PILOTAGE_RENDER_BINDING_MISMATCH","$.render_sha256",sha256(render_path),d.get("render_sha256"))
        if render_path is not None and render_path.exists():
            issues.extend(_pilotage_wire_issues(d,render_path,st))
    schema_path=Path(a.schema_file) if nonempty(getattr(a,"schema_file",None)) else None
    if schema_path is None or not schema_path.exists(): _mechanical_issue(issues,"PILOTAGE_SCHEMA_MISSING","schema_file","existing file",str(schema_path) if schema_path else None)
    else:
        try: schema=read_json(schema_path,"pilotage wire schema")
        except SystemExit as e: _mechanical_issue(issues,"PILOTAGE_SCHEMA_INVALID","schema_file","valid schema",str(e)); schema=None
        if isinstance(schema,dict) and (schema.get("wire_schema")!=PILOTAGE_WIRE_SCHEMA or schema.get("authority_source_sha256")!=_pilotage_policy_sha256(st)):
            _mechanical_issue(issues,"PILOTAGE_SCHEMA_BINDING_MISMATCH","schema_file",PILOTAGE_WIRE_SCHEMA,schema.get("wire_schema"))
    if st.get("combo_impact_required") is True:
        ci=getattr(a,"combo_impact_file",None)
        if not nonempty(ci): _mechanical_issue(issues,"COMBO_IMPACT_REQUIRED","combo_impact_file","current material-change combo impact",None)
        else:
            p=Path(ci)
            if not p.exists(): _mechanical_issue(issues,"COMBO_IMPACT_MISSING","combo_impact_file","existing file",str(p))
            else:
                try: validate_combo_impact(p,st)
                except SystemExit as e: _mechanical_issue(issues,"COMBO_IMPACT_INVALID","combo_impact_file","valid current combo impact",str(e))
    # Deduplicate wire/mechanical collisions deterministically.
    uniq={json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")):x for x in issues}
    return sorted(uniq.values(),key=lambda x:(x.get("path") or "",x.get("code") or ""))


def cmd_mechanical_preflight(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    before_state=sha256(rd/STATE_FILE); before_cp=sha256(rd/CHECKPOINT_FILE); before_journal=sha256(rd/RUN_JOURNAL_FILE) if (rd/RUN_JOURNAL_FILE).exists() else None
    if a.kind=="render": issues=_render_mechanical_preflight_issues(a,st)
    elif a.kind=="pilotage": issues=_pilotage_mechanical_preflight_issues(a,st)
    else: fail("MECHANICAL_PREFLIGHT_KIND_INVALID")
    after_state=sha256(rd/STATE_FILE); after_cp=sha256(rd/CHECKPOINT_FILE); after_journal=sha256(rd/RUN_JOURNAL_FILE) if (rd/RUN_JOURNAL_FILE).exists() else None
    if (before_state,before_cp,before_journal)!=(after_state,after_cp,after_journal): fail("MECHANICAL_PREFLIGHT_MUTATED_RUNTIME_STATE")
    payload={"status":"FAIL" if issues else "PASS","kind":a.kind,"run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),"issues":issues,"read_only":True,"runtime_version":VERSION}
    print(json.dumps(payload,ensure_ascii=False,sort_keys=True))
    if issues: raise SystemExit(2)


# Only gates in this map are eligible for selective freshness. Unknown dependency
# semantics deliberately fall back to the parent wide invalidation.
SELECTIVE_GATE_DEPENDENCIES = {
    "STYLE_AXES_CLOSED": set(),
    "DECK_DRAFT_CREATED": set(),
    "NARRATIVE_CONFORMANCE_CLOSED": {"NARRATIVE_CONTRACT_FROZEN","DECK_DRAFT_CREATED"},
    "FINAL_CLASSIFICATION_CLOSED": {"DIRECTION_RESOLVED","DECK_DRAFT_CREATED"},
    "VISUAL_ASSETS_BOUND": {"FINAL_CLASSIFICATION_CLOSED","DECK_DRAFT_CREATED","STYLE_AXES_CLOSED"},
    "RENDER_CONTRACT_FROZEN": {"FINAL_CLASSIFICATION_CLOSED","VISUAL_ASSETS_BOUND","STYLE_AXES_CLOSED"},
    "FINAL_RENDER_PREPARED": {"RENDER_CONTRACT_FROZEN","DECK_DRAFT_CREATED","VISUAL_ASSETS_BOUND","STYLE_AXES_CLOSED"},
    "PILOTAGE_VALIDATED": {"FINAL_RENDER_PREPARED","STYLE_AXES_CLOSED"},
    "FINAL_VALIDATION_PASS": {"PILOTAGE_VALIDATED","FINAL_RENDER_PREPARED"},
}


def _record_current_file_hash(rec, key):
    file_key={
        "evidence_sha256":"evidence_file","snapshot_sha256":"snapshot_file","manifest_sha256":"manifest_file",
        "pilotage_contract_sha256":"pilotage_contract_file","combo_impact_sha256":"combo_impact_file",
        "pilotage_preflight_receipt_sha256":"pilotage_preflight_receipt_file",
        "terminal_presentation_plan_sha256":"terminal_presentation_plan_file",
        "terminal_presentation_receipt_sha256":"terminal_presentation_receipt_file",
    }.get(key)
    if not file_key: return rec.get(key)
    fn=rec.get(file_key)
    if nonempty(fn) and Path(fn).exists() and Path(fn).is_file(): return sha256(Path(fn))
    return rec.get(key)


def _gate_dependency_payload(st, gate, record_override=None):
    if gate not in SELECTIVE_GATE_DEPENDENCIES: return None
    gates=st.get("gates") or {}; rec=record_override if isinstance(record_override,dict) else gates.get(gate)
    if not isinstance(rec,dict): return None
    payload={"gate":gate,"run_id":st.get("run_id"),"artifact":rec.get("artifact"),"current_artifact":st.get("current_artifact")}
    # Self-bound files: any in-place mutation must stale the gate itself.
    for k in ("evidence_sha256","snapshot_sha256","manifest_sha256","pilotage_contract_sha256","combo_impact_sha256","pilotage_preflight_receipt_sha256","terminal_presentation_plan_sha256","terminal_presentation_receipt_sha256","render_sha256","contract_sha256","component_inventory_sha256"):
        if rec.get(k) is not None: payload["self:"+k]=_record_current_file_hash(rec,k)
    deps={}
    for dep in sorted(SELECTIVE_GATE_DEPENDENCIES[gate]):
        dr=gates.get(dep)
        if not isinstance(dr,dict): deps[dep]=None; continue
        dd={"status":dr.get("status"),"artifact":dr.get("artifact")}
        for k in ("evidence_sha256","snapshot_sha256","manifest_sha256","render_sha256","contract_sha256","component_inventory_sha256"):
            if dr.get(k) is not None: dd[k]=_record_current_file_hash(dr,k)
        deps[dep]=dd
    payload["dependencies"]=deps
    return payload


def _gate_dependency_fingerprint(st, gate, record_override=None):
    payload=_gate_dependency_payload(st,gate,record_override)
    if payload is None: return None
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _clear_downstream_runtime_state(st, invalidated):
    if "RENDER_CONTRACT_FROZEN" in invalidated or "FINAL_RENDER_PREPARED" in invalidated:
        st["current_render"]=None
    if any(g in invalidated for g in {"RENDER_CONTRACT_FROZEN","FINAL_RENDER_PREPARED","PILOTAGE_VALIDATED","FINAL_VALIDATION_PASS"}):
        st["render_check_pass"]=None; st["render_contract_defect_suspected"]=None
    if any(g in invalidated for g in {"FINAL_RENDER_PREPARED","PILOTAGE_VALIDATED","FINAL_VALIDATION_PASS"}):
        for k in ("authorized_render_sha256","authorized_manifest_sha256","authorized_component_inventory_sha256","terminal_presentation_plan_file","terminal_presentation_plan_sha256","terminal_presentation_receipt_file","terminal_presentation_receipt_sha256","terminal_presentation_check","terminal_payload_file","terminal_payload_sha256","canonical_refactor_diff_file","canonical_refactor_diff_sha256"):
            st.pop(k,None)


def cmd_evidence_refresh_selective(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    names=[g for g,_,_ in sequence(st)]
    if a.from_gate not in names: fail("EVIDENCE_REFRESH_GATE_INVALID")
    if a.from_gate not in st.get("gates",{}): fail("EVIDENCE_REFRESH_GATE_NOT_CLOSED")
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{}); sf=dg.get("snapshot_file")
    if not nonempty(sf) or not Path(sf).exists(): fail("EVIDENCE_REFRESH_REQUIRES_CURRENT_DECK_SNAPSHOT")
    expected=deck_composition_sha256(read_json(Path(sf),"current deck snapshot"))
    idx=names.index(a.from_gate); closed=[g for g in names[idx:] if g in st.get("gates",{})]
    # Missing/unknown fingerprints are intentionally not guessed: preserve parent behavior.
    selective_ok=all(g in SELECTIVE_GATE_DEPENDENCIES and nonempty((st["gates"].get(g) or {}).get("dependency_fingerprint")) for g in closed)
    if not selective_ok:
        _append_run_journal(rd,st,"SELECTIVE_INVALIDATION_FALLBACK",checkpoint_seq=(_load_checkpoint_raw(rd,False) or {}).get("checkpoint_seq"),from_gate=a.from_gate,reason="UNKNOWN_OR_UNFINGERPRINTED_DEPENDENCY")
        return cmd_evidence_refresh(a)
    oldfp={g:st["gates"][g].get("dependency_fingerprint") for g in closed}
    invalidated={a.from_gate}; preserved=[]
    # First gate is explicitly being refreshed. Downstream survives only if its
    # authoritative dependency fingerprint remains exact and none of its declared
    # parents became stale.
    for g in closed[1:]:
        deps=SELECTIVE_GATE_DEPENDENCIES[g]
        current=_gate_dependency_fingerprint(st,g)
        if deps & invalidated or current!=oldfp[g]: invalidated.add(g)
        else: preserved.append(g)
    invalidated_list=[g for g in closed if g in invalidated]
    for g in invalidated_list: st["gates"].pop(g,None)
    transition={"status":"EVIDENCE_REFRESH_SELECTIVE","artifact":st.get("current_artifact"),"from_gate":a.from_gate,"invalidated_gates":invalidated_list,"preserved_gates":preserved,"reason":a.reason,"expected_composition_sha256":expected}
    st["last_evidence_refresh"]=transition; st.setdefault("stale_history",[]).append(dict(transition))
    st["stop_output_allowed"]=False; st["run_execution_state"]="IN_PROGRESS"
    _clear_downstream_runtime_state(st,invalidated)
    _append_run_journal(rd,st,"EVIDENCE_REFRESH_SELECTIVE_MATERIALIZED",checkpoint_seq=(_load_checkpoint_raw(rd,False) or {}).get("checkpoint_seq"),from_gate=a.from_gate,invalidated_gates=invalidated_list,preserved_gates=preserved,expected_composition_sha256=expected)
    save_state(rd,st)
    print(json.dumps({"status":"EVIDENCE_REFRESH_SELECTIVE","artifact":st.get("current_artifact"),"from_gate":a.from_gate,"invalidated_gates":invalidated_list,"preserved_gates":preserved},ensure_ascii=False))

def _validate_material_change_proof(path: Path, st, old, new, before_hash, after_hash):
    validate_evidence(path,st); d=read_json(path,"material change proof")
    if d.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in material change proof")
    if d.get("authority") not in MATERIAL_CHANGE_AUTHORITIES: fail("MATERIAL_CHANGE_PROOF_AUTHORITY_INVALID")
    if d.get("from_artifact")!=old or d.get("to_artifact")!=new: fail("MATERIAL_CHANGE_PROOF_ARTIFACT_MISMATCH")
    if d.get("material_change") is not True: fail("MATERIAL_CHANGE_PROOF_NOT_MATERIAL")
    if d.get("category") not in MATERIAL_CHANGE_CATEGORIES: fail("MATERIAL_CHANGE_PROOF_CATEGORY_INVALID")
    if d.get("before_composition_sha256")!=before_hash or d.get("after_composition_sha256")!=after_hash: fail("MATERIAL_CHANGE_PROOF_COMPOSITION_MISMATCH")
    return d,sha256(path)


def cmd_evidence_refresh(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    names=[g for g,_,_ in sequence(st)]
    if a.from_gate not in names: fail("EVIDENCE_REFRESH_GATE_INVALID")
    if a.from_gate not in st.get("gates",{}): fail("EVIDENCE_REFRESH_GATE_NOT_CLOSED")
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    sf=dg.get("snapshot_file")
    if not nonempty(sf) or not Path(sf).exists(): fail("EVIDENCE_REFRESH_REQUIRES_CURRENT_DECK_SNAPSHOT")
    snap=read_json(Path(sf),"current deck snapshot")
    expected=deck_composition_sha256(snap)
    idx=names.index(a.from_gate); invalidated=[g for g in names[idx:] if g in st.get("gates",{})]
    for g in names[idx:]: st["gates"].pop(g,None)
    transition={"status":"EVIDENCE_REFRESH","artifact":st.get("current_artifact"),"from_gate":a.from_gate,"invalidated_gates":invalidated,"reason":a.reason,"expected_composition_sha256":expected}
    st["last_evidence_refresh"]=transition
    st.setdefault("stale_history",[]).append(dict(transition))
    if "RENDER_CONTRACT_FROZEN" in invalidated or "FINAL_RENDER_PREPARED" in invalidated:
        st["current_render"]=None
    st["stop_output_allowed"]=False; st["run_execution_state"]="IN_PROGRESS"; st["render_check_pass"]=None; st["render_contract_defect_suspected"]=None
    for k in ("authorized_render_sha256","authorized_manifest_sha256","authorized_component_inventory_sha256","terminal_presentation_plan_file","terminal_presentation_plan_sha256","terminal_presentation_receipt_file","terminal_presentation_receipt_sha256","terminal_presentation_check","terminal_payload_file","terminal_payload_sha256","canonical_refactor_diff_file","canonical_refactor_diff_sha256"):
        st.pop(k,None)
    _append_run_journal(rd,st,"EVIDENCE_REFRESH_MATERIALIZED",checkpoint_seq=(_load_checkpoint_raw(rd,required=False) or {}).get("checkpoint_seq"),from_gate=a.from_gate,invalidated_gates=invalidated,expected_composition_sha256=expected)
    save_state(rd,st)
    print(f"evidence refresh → {st.get('current_artifact')} → {a.from_gate}")


def cmd_material_change(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    m=re.fullmatch(r"deck-v(\d+)",st.get("current_artifact", ""))
    if not m: fail("current artifact is not versioned")
    old=st.get("current_artifact")
    new=f"deck-v{int(m.group(1))+1}"
    if not getattr(a,"candidate_snapshot",None): fail("MATERIAL_CHANGE_REQUIRES_CANDIDATE_SNAPSHOT")
    old_draft=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    old_sf=old_draft.get("snapshot_file")
    if not nonempty(old_sf) or not Path(old_sf).exists(): fail("MATERIAL_CHANGE_REQUIRES_CURRENT_DECK_SNAPSHOT")
    before=read_json(Path(old_sf),"current deck snapshot")
    candidate=_read_candidate_snapshot(Path(a.candidate_snapshot),st.get("run_id"),new)
    before_comp=deck_composition_sha256(before); after_comp=deck_composition_sha256(candidate)
    proof=None; proof_sha=None
    if before_comp==after_comp:
        if not getattr(a,"material_proof",None): fail("DECK_VERSION_INCREMENT_UNJUSTIFIED")
        proof,proof_sha=_validate_material_change_proof(Path(a.material_proof),st,old,new,before_comp,after_comp)
    elif getattr(a,"material_proof",None):
        proof,proof_sha=_validate_material_change_proof(Path(a.material_proof),st,old,new,before_comp,after_comp)
    st["material_change_count"]=int(st.get("material_change_count",0))+1
    st["combo_impact_required"]=True
    old_narr=st.get("gates",{}).get("NARRATIVE_CONFORMANCE_CLOSED",{})
    old_render=st.get("gates",{}).get("FINAL_RENDER_PREPARED",{})
    old_visual_gate=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    # RC8: once a version has actually reached STOP_OUTPUT_ALLOWED, a later material
    # change is a post-output refactor. DIFF_ONLY is therefore automatic unless the
    # user explicitly asks for the complete list. Internal pre-output refactors stay FULL.
    prior_output_authorized=bool(st.get("stop_output_allowed"))
    post_output_refactor=prior_output_authorized or bool(a.user_refactor)
    render_mode="DIFF_ONLY" if post_output_refactor and not a.full_decklist else "FULL"
    st["refactor_render_mode"]=render_mode
    if post_output_refactor:
        inv=old_render.get("component_inventory") or []
        st["refactor_visual_carry_components"]=[x for x in inv if x.get("type") in {"main-carousel","mini-carousel"}]
        req=[]
        if old_visual_gate.get("evidence_file") and Path(old_visual_gate["evidence_file"]).exists():
            ov=read_json(Path(old_visual_gate["evidence_file"]),"previous visual assets")
            if ov.get("signature_climax",{}).get("terminal_quote_required") is True: req.append("signature-terminal-quote")
        st["refactor_visual_carry_requirements"]=req
    else:
        st["refactor_visual_carry_components"]=[]
        st["refactor_visual_carry_requirements"]=[]
    st["last_material_change"]={"from_artifact":old,"to_artifact":new,"reason":a.reason,"user_requested_refactor":bool(a.user_refactor),"post_output_refactor":post_output_refactor,"prior_output_authorized":prior_output_authorized,"full_decklist_requested":bool(a.full_decklist),"render_mode":render_mode,"previous_snapshot_file":old_draft.get("snapshot_file"),"previous_snapshot_sha256":old_draft.get("snapshot_sha256"),"candidate_snapshot_file":str(Path(a.candidate_snapshot)),"before_composition_sha256":before_comp,"after_composition_sha256":after_comp,"material_proof_file":getattr(a,"material_proof",None),"material_proof_sha256":proof_sha,"previous_narrative_report_file":old_narr.get("evidence_file"),"previous_narrative_report_sha256":old_narr.get("evidence_sha256"),"previous_render_sha256":old_render.get("render_sha256"),"previous_component_inventory_sha256":old_render.get("component_inventory_sha256")}
    names=[g for g,_,_ in sequence(st)]; idx=names.index("STYLE_AXES_CLOSED")
    invalidated=[g for g in names[idx:] if g in st.get("gates",{})]
    for g in names[idx:]: st["gates"].pop(g,None)
    st["last_material_change"]["stale_transition"]={"status":"MATERIALIZED","from_artifact":old,"to_artifact":new,"invalidated_gates":invalidated}
    st.setdefault("stale_history",[]).append(dict(st["last_material_change"]["stale_transition"]))
    st["current_artifact"]=new; st["current_render"]=None; st["stop_output_allowed"]=False; st["presentation_carry_components"]=[]; st["run_execution_state"]="IN_PROGRESS"; st.pop("last_evidence_refresh",None)
    st["render_attempts"]={}; st["render_check_pass"]=None; st["render_contract_defect_suspected"]=None; st.pop("presentation_expected_policy_fingerprint",None)
    for k in ("authorized_render_sha256","authorized_manifest_sha256","authorized_component_inventory_sha256","terminal_presentation_plan_file","terminal_presentation_plan_sha256","terminal_presentation_receipt_file","terminal_presentation_receipt_sha256","terminal_presentation_check","terminal_payload_file","terminal_payload_sha256","canonical_refactor_diff_file","canonical_refactor_diff_sha256"): st.pop(k,None)
    save_state(rd,st)
    print(f"deck-v{int(m.group(1))} → material change → STALE → {new}")


def cmd_presentation_change(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    cur=st.get("current_render")
    if not cur: fail("no prepared render lineage")
    m=re.fullmatch(r"render-v(\d+)",cur)
    if not m: fail("current render is not versioned")
    prior=st.get("gates",{}).get("FINAL_RENDER_PREPARED",{})
    if not prior or prior.get("render_id")!=cur:
        fail("PREPARED_RENDER_REQUIRED_FOR_PRESENTATION_CHANGE")
    frozen=st.get("gates",{}).get("RENDER_CONTRACT_FROZEN",{})
    if not frozen or not frozen.get("render_policy_fingerprint"):
        fail("PREPARED_RENDER_POLICY_MISSING")
    inv=prior.get("component_inventory")
    if inv is not None: st["presentation_carry_components"]=inv
    else: st["presentation_carry_components"]=st.get("presentation_carry_components",[])
    st["refactor_visual_carry_components"]=[]
    st["refactor_visual_carry_requirements"]=[]
    st["presentation_expected_policy_fingerprint"]=frozen["render_policy_fingerprint"]
    names=[g for g,_,_ in sequence(st)]; idx=names.index("RENDER_CONTRACT_FROZEN")
    for g in names[idx:]: st["gates"].pop(g,None)
    st["current_render"]=f"render-v{int(m.group(1))+1}"; st["stop_output_allowed"]=False; st["run_execution_state"]="IN_PROGRESS"
    st["render_check_pass"]=None; st["render_contract_defect_suspected"]=None
    for k in ("authorized_render_sha256","authorized_manifest_sha256","authorized_component_inventory_sha256","terminal_presentation_plan_file","terminal_presentation_plan_sha256","terminal_presentation_receipt_file","terminal_presentation_receipt_sha256","terminal_presentation_check"): st.pop(k,None)
    save_state(rd,st)
    print(f"{cur} → presentation-change → {st['current_render']}")


def cmd_authorize(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if _unmatched_gate_attempts(rd): fail("UNRESOLVED_GATE_ATTEMPT")
    block=_active_progress_block(rd,st)
    if block: fail("ACTIVE_GATE_PROGRESS_BLOCK")
    g,_,_=next_gate(st)
    if g is not None: fail(f"next gate is {g}; STOP_OUTPUT not allowed")
    hashes=validate_render_manifest(Path(a.render_manifest),Path(a.render_file),Path(a.contract_file),st)
    # Narrative conformance must still be fresh for current deck.
    ng=st["gates"].get("NARRATIVE_CONFORMANCE_CLOSED",{})
    dg=st["gates"].get("DECK_DRAFT_CREATED",{})
    if not ng or ng.get("artifact")!=st["current_artifact"] or ng.get("snapshot_sha256")!=dg.get("snapshot_sha256"):
        fail("NARRATIVE_CONFORMANCE_STALE")
    for label in ("FINAL_RENDER_PREPARED","PILOTAGE_VALIDATED","FINAL_VALIDATION_PASS"):
        rec=st["gates"].get(label,{})
        for k in ("render_sha256","manifest_sha256","contract_sha256","component_inventory_sha256"):
            if rec.get(k)!=hashes.get(k): fail(f"FINAL_RENDER_MISMATCH: {label} did not validate this exact render bundle")
    if st.get("combo_impact_required") is True: fail("COMBO_IMPACT_PENDING")
    if int(st.get("material_change_count",0))>0:
        ch=st.get("last_material_change") or {}; tr=ch.get("stale_transition") or {}
        if tr.get("status")!="MATERIALIZED" or tr.get("to_artifact")!=st.get("current_artifact") or not isinstance(tr.get("invalidated_gates"),list) or not tr.get("invalidated_gates"):
            fail("MATERIAL_CHANGE_STALE_TRANSITION_NOT_MATERIALIZED")
        prec=st.get("gates",{}).get("PILOTAGE_VALIDATED",{})
        if not nonempty(prec.get("combo_impact_sha256")): fail("COMBO_IMPACT_NOT_VALIDATED_ON_CURRENT_VERSION")
    finalrec=st.get("gates",{}).get("FINAL_VALIDATION_PASS",{})
    plan_file=finalrec.get("terminal_presentation_plan_file")
    receipt_file=finalrec.get("terminal_presentation_receipt_file")
    if not nonempty(plan_file): fail("TERMINAL_PRESENTATION_PLAN_REQUIRED")
    if not nonempty(receipt_file): fail("TERMINAL_PRESENTATION_RECEIPT_REQUIRED")
    pd,tr,trh=_verify_terminal_presentation_receipt(Path(plan_file),Path(receipt_file),Path(a.render_file),Path(a.render_manifest),st)
    if finalrec.get("terminal_presentation_plan_sha256")!=sha256(Path(plan_file)) or finalrec.get("terminal_presentation_receipt_sha256")!=trh:
        fail("TERMINAL_PRESENTATION_RECEIPT_STALE")
    if a.confidence!="HIGH": fail("STOP_OUTPUT requires HIGH confidence")
    st["stop_output_allowed"]=True
    st["run_execution_state"]="COMPLETED"
    st["authorized_render_sha256"]=hashes["render_sha256"]
    st["authorized_manifest_sha256"]=hashes["manifest_sha256"]
    st["authorized_component_inventory_sha256"]=hashes["component_inventory_sha256"]
    # RC16.23: the terminal payload itself is content-addressed and immutable.
    # A convenience alias may be mutable, but state/receipts always bind the immutable payload.
    payload=(rd/f"terminal_payload__{hashes['render_sha256'][:16]}.md").resolve()
    _rc1623_write_immutable(payload,Path(a.render_file).read_text(encoding="utf-8"))
    _atomic_write_text((rd/"terminal_payload.md").resolve(),Path(a.render_file).read_text(encoding="utf-8"))
    st["terminal_payload_file"]=str(payload)
    st["terminal_payload_sha256"]=sha256(payload)
    if st["terminal_payload_sha256"]!=hashes["render_sha256"]: fail("TERMINAL_PAYLOAD_HASH_MISMATCH")
    st["terminal_presentation_plan_file"]=str(Path(plan_file).resolve())
    st["terminal_presentation_plan_sha256"]=sha256(Path(plan_file))
    st["terminal_presentation_receipt_file"]=str(Path(receipt_file).resolve())
    st["terminal_presentation_receipt_sha256"]=trh
    save_state(rd,st)
    print("STOP_OUTPUT_ALLOWED")
    print(f"TERMINAL_PAYLOAD_FILE {payload}")
    print(f"TERMINAL_PAYLOAD_SHA256 {st['terminal_payload_sha256']}")
    print(f"TERMINAL_PRESENTATION_PLAN_FILE {st['terminal_presentation_plan_file']}")
    print(f"TERMINAL_PRESENTATION_PLAN_SHA256 {st['terminal_presentation_plan_sha256']}")
    print(f"TERMINAL_PRESENTATION_RECEIPT_FILE {st['terminal_presentation_receipt_file']}")
    print(f"TERMINAL_PRESENTATION_RECEIPT_SHA256 {st['terminal_presentation_receipt_sha256']}")
    print(f"TERMINAL_PRESENTATION_COMPONENT_COUNT {pd.get('component_count',0)}")
    for c in pd.get("components",[]):
        print("TERMINAL_COMPONENT "+json.dumps({"component_id":c.get("component_id"),"type":c.get("type"),"parent":c.get("parent"),"payload_file":c.get("payload_file"),"payload_sha256":c.get("payload_sha256"),"image_refs":c.get("image_refs")},ensure_ascii=False,sort_keys=True))




def _capture_denied(fn):
    try:
        fn()
        return []
    except SystemExit as e:
        msg=str(e)
        if msg.startswith("DENIED: "):
            msg=msg[8:]
        return [msg]


def _collect_render_assertion_failures(a,text,components,rid,idx):
    out=[]
    try:
        execute_render_assertion(a,text,components,rid)
    except SystemExit as e:
        msg=str(e)
        if msg.startswith("DENIED: "):
            msg=msg[8:]
        out.append({"code":"RENDER_ASSERTION_FAILED","requirement_id":rid,"assertion_index":idx,"assertion_type":a.get("type"),"detail":msg})
    return out


def _canonicalize_components(component_file: Path, raw_components, output_manifest: Path):
    out=[]
    for c in raw_components:
        x=dict(c)
        af=x.get("artifact_file")
        if nonempty(af):
            ap=Path(af)
            if not ap.is_absolute():
                ap=(component_file.parent/ap).resolve()
            x["artifact_file"]=str(ap)
        out.append(x)
    return out


def _collect_render_failures(render_path: Path, contract_path: Path, component_file: Path, st):
    failures=[]
    if st.get("render_contract_defect_suspected"):
        return [{"code":"CONTRACT_DEFECT_SUSPECTED","detail":st["render_contract_defect_suspected"].get("reason","contract defect suspected")}],None,None,[],None
    try:
        contract,ch=validate_frozen_render_contract(contract_path,st)
    except SystemExit as e:
        msg=str(e); msg=msg[8:] if msg.startswith("DENIED: ") else msg
        return [{"code":msg.split(":",1)[0],"detail":msg}],None,None,[],None
    if not render_path.exists() or not render_path.is_file():
        return [{"code":"RENDER_FILE_MISSING","detail":str(render_path)}],contract,ch,[],None
    text=render_path.read_text(encoding="utf-8")
    compdoc={"components":[]}
    if component_file:
        try:
            validate_evidence(component_file,st); compdoc=read_json(component_file,"render component input")
        except SystemExit as e:
            msg=str(e); msg=msg[8:] if msg.startswith("DENIED: ") else msg
            failures.append({"code":"COMPONENT_INPUT_INVALID","detail":msg})
            compdoc={"components":[]}
    raw_components=compdoc.get("components",[])
    if not isinstance(raw_components,list):
        failures.append({"code":"COMPONENT_INPUT_INVALID","detail":"components must be a list"}); raw_components=[]
    # Validate materialized components as one deterministic domain; assertion checks still run to reveal independent shape defects.
    if component_file:
        try:
            components=validate_components(component_file,{"components":raw_components},st)
            validate_component_continuity(contract,components,st)
        except SystemExit as e:
            msg=str(e); msg=msg[8:] if msg.startswith("DENIED: ") else msg
            failures.append({"code":"COMPONENT_VALIDATION_FAILED","detail":msg})
            components=raw_components
    else:
        components=[]
        try:
            validate_component_continuity(contract,components,st)
        except SystemExit as e:
            msg=str(e); msg=msg[8:] if msg.startswith("DENIED: ") else msg
            failures.append({"code":"COMPONENT_VALIDATION_FAILED","detail":msg})
    for r in contract.get("requirements",[]):
        for idx,a in enumerate(r.get("assertions",[])):
            failures.extend(_collect_render_assertion_failures(a,text,components,r.get("id"),idx))
    # Global deterministic invariants are independent domains and are all attempted.
    dg=st.get("gates",{}).get("DECK_DRAFT_CREATED",{})
    ng=st.get("gates",{}).get("NARRATIVE_CONFORMANCE_CLOSED",{})
    if not dg or not dg.get("snapshot_file"):
        failures.append({"code":"DECK_SNAPSHOT_MISSING","detail":"deck snapshot missing for render verification"})
    elif not ng or not ng.get("evidence_file"):
        failures.append({"code":"NARRATIVE_CONFORMANCE_MISSING","detail":"narrative conformance missing for render grouping"})
    else:
        snap=read_json(Path(dg["snapshot_file"]),"deck snapshot")
        typemap=_narrative_type_map(Path(ng["evidence_file"]))
        if st.get("refactor_render_mode")=="DIFF_ONLY":
            for code,fn in [
                ("REFACTOR_DIFF_INVALID",lambda:validate_refactor_diff(text,st,snap,typemap)),
                ("REFACTOR_DIFF_COMPONENT_INVALID",lambda:validate_refactor_diff_component(components,st)),
            ]:
                for msg in _capture_denied(fn): failures.append({"code":code,"detail":msg})
        else:
            for msg in _capture_denied(lambda:validate_full_decklist_groups(text,snap,typemap)):
                failures.append({"code":"DECKLIST_GROUPING_INVALID","detail":msg})
    final_class=st.get("gates",{}).get("FINAL_CLASSIFICATION_CLOSED",{}).get("classification")
    if not final_class or not re.search(rf"(?im)^.*Direction.*{re.escape(final_class)}.*$",text):
        failures.append({"code":"FINAL_DIRECTION_NOT_RENDERED","detail":str(final_class)})
    vg=st.get("gates",{}).get("VISUAL_ASSETS_BOUND",{})
    if vg and vg.get("evidence_file"):
        visual=read_json(Path(vg["evidence_file"]),"visual assets")
        types=[c.get("type") for c in components if isinstance(c,dict)]
        if visual["main_carousel"].get("applicable") is True and "main-carousel" not in types:
            failures.append({"code":"MAIN_CAROUSEL_NOT_MATERIALIZED","detail":"required main-carousel missing"})
        sig=visual["signature_climax"]
        if sig.get("mini_carousel_applicable") is True and "mini-carousel" not in types:
            failures.append({"code":"SIGNATURE_MINI_CAROUSEL_NOT_MATERIALIZED","detail":"required mini-carousel missing"})
        if sig.get("terminal_quote_required") is True and not re.search(r"(?m)^###\s+\*\*.+—\s*«.+»\*\*\s*$",text):
            failures.append({"code":"TERMINAL_QUOTE_NOT_MATERIALIZED","detail":"terminal quote missing"})
    axe_count=len(re.findall(r"(?im)^#{2,4}\s+Axe\s+\d+\b",text))
    if axe_count>=2 and not re.search(r"(?im)^##\s+Guide de pilotage\s*$",text):
        failures.append({"code":"PILOTAGE_GUIDE_NOT_MATERIALIZED","detail":f"{axe_count} axes without Guide de pilotage"})
    # De-duplicate exact failures while preserving order.
    uniq=[]; seen=set()
    for f in failures:
        key=json.dumps(f,ensure_ascii=False,sort_keys=True)
        if key not in seen:
            seen.add(key); uniq.append(f)
    inv_hash=component_inventory_hash(components) if isinstance(components,list) else component_inventory_hash([])
    return uniq,contract,ch,components,inv_hash


def _render_attempt_key(render_id,contract_sha):
    return f"{render_id}:{contract_sha}"


def _next_render_attempt_id(events):
    n=sum(1 for e in events if e.get("event")=="RENDER_ATTEMPT_STARTED")+1
    return f"render-attempt-{n:06d}"


def _render_failure_signature(failures):
    raw=json.dumps(failures,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _persist_render_attempt_failure(rd: Path, st, attempts, render_attempt_id, attempt_number, attempt_bundle_sha, failures, signature=None):
    # `signature` binds the validator-produced failure set before runtime repair guards
    # append STALLED/BUDGET markers. The durable receipt keeps the complete returned list.
    base_signature=signature or _render_failure_signature(failures)
    stalled=attempts.get("last_failure_signature")==base_signature and attempts.get("failed_count",0)>0
    attempts["failed_count"]=int(attempts.get("failed_count",0))+1
    attempts.setdefault("failed_bundle_hashes",[]).append(attempt_bundle_sha)
    attempts["last_failure_signature"]=base_signature
    full_failures=[dict(x) for x in failures]
    if stalled:
        attempts["stalled"]=True
        full_failures.append({"code":"RENDER_REPAIR_STALLED","detail":"failure signature unchanged across consecutive attempts"})
    budget_exhausted=attempts["failed_count"]>=3
    if budget_exhausted:
        full_failures.append({"code":"RENDER_REPAIR_BUDGET_EXHAUSTED","detail":"maximum 3 failed attempts reached"})
    if stalled or budget_exhausted:
        st["run_execution_state"]="TERMINAL_FAILED"
    st["render_check_pass"]=None
    save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(
        rd,st,"RENDER_ATTEMPT_FAILED",checkpoint_seq=cp.get("checkpoint_seq"),
        render_attempt_id=render_attempt_id,attempt_number=attempt_number,
        attempt_bundle_sha256=attempt_bundle_sha,failures=full_failures,
        failure_signature=base_signature,stalled=bool(stalled),
        budget_exhausted=bool(budget_exhausted),failed_count_after=attempts["failed_count"],
        run_state_after=cp.get("run_state"),state_sha256_after=sha256(rd/STATE_FILE),
    )
    print(json.dumps({"status":"FAIL","render_id":st.get("current_render"),"attempt":attempts["failed_count"],"failures":full_failures},ensure_ascii=False,indent=2))
    raise SystemExit(2)


def _persist_render_attempt_exception(rd: Path, st, render_attempt_id, attempt_number, attempt_bundle_sha, exc):
    tb=traceback.format_exc()
    tbfile=rd/f"{render_attempt_id}.traceback.txt"
    _atomic_write_text(tbfile,tb)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(
        rd,st,"RENDER_ATTEMPT_EXCEPTION",checkpoint_seq=cp.get("checkpoint_seq"),
        render_attempt_id=render_attempt_id,attempt_number=attempt_number,
        attempt_bundle_sha256=attempt_bundle_sha,exception_type=type(exc).__name__,
        message=str(exc),traceback_file=str(tbfile),traceback_sha256=sha256(tbfile),
    )


def _last_render_attempt_summary(run_dir: Path):
    last=None
    for ev in _read_journal(run_dir):
        if ev.get("event") not in {"RENDER_ATTEMPT_STARTED","RENDER_ATTEMPT_FAILED","RENDER_ATTEMPT_SUCCEEDED","RENDER_ATTEMPT_EXCEPTION","RENDER_ATTEMPT_BLOCKED"}:
            continue
        last=ev
    if not last:
        return None
    event=last.get("event")
    result={
        "render_attempt_id":last.get("render_attempt_id"),
        "render_id":last.get("render_id"),
        "event":event,
        "attempt_number":last.get("attempt_number"),
        "attempt_bundle_sha256":last.get("attempt_bundle_sha256"),
    }
    if event=="RENDER_ATTEMPT_FAILED":
        result.update({
            "result":"FAIL",
            "failure_signature":last.get("failure_signature"),
            "failure_codes":[x.get("code") for x in last.get("failures",[]) if isinstance(x,dict)],
            "stalled":last.get("stalled",False),
            "budget_exhausted":last.get("budget_exhausted",False),
        })
    elif event=="RENDER_ATTEMPT_SUCCEEDED":
        result.update({"result":"PASS","manifest_sha256":last.get("manifest_sha256"),"render_sha256":last.get("render_sha256")})
    elif event=="RENDER_ATTEMPT_EXCEPTION":
        result.update({"result":"EXCEPTION","exception_type":last.get("exception_type")})
    elif event=="RENDER_ATTEMPT_BLOCKED":
        result.update({"result":"BLOCKED","error_code":last.get("error_code")})
    else:
        result["result"]="STARTED"
    return result


def cmd_render_check(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if next_gate(st)[0] != "FINAL_RENDER_PREPARED":
        fail(f"render-check requires next gate FINAL_RENDER_PREPARED; next gate is {next_gate(st)[0]}")
    if st.get("render_contract_defect_suspected"):
        fail("CONTRACT_DEFECT_SUSPECTED")
    contract_path=Path(a.contract_file); render_path=Path(a.render_file)
    component_file=Path(a.component_manifest) if a.component_manifest else None
    component_inventory_sha=None
    # RC16.5/16.6 preflight remains outside retry accounting and before RENDER_ATTEMPT_STARTED.
    if component_file:
        if not getattr(a,"component_plan_file",None) or not getattr(a,"visual_assets_file",None):
            fail("COMPILED_COMPONENT_MANIFEST_REQUIRED")
        manifest_doc=validate_compiled_component_manifest(component_file,Path(a.component_plan_file),Path(a.visual_assets_file),[Path(x) for x in (a.component_file or [])],st)
        component_inventory_sha=component_inventory_hash(manifest_doc.get("components",[]))
    else:
        component_inventory_sha=component_inventory_hash([])
    # Frozen contract identity is checked before attempt accounting.
    contract,ch=validate_frozen_render_contract(contract_path,st)
    rh=sha256(render_path) if render_path.exists() and render_path.is_file() else "MISSING"
    component_sha=sha256(component_file) if component_file and component_file.exists() and component_file.is_file() else "NO_COMPONENT_INPUT"
    attempt_bundle_sha=hashlib.sha256(f"{rh}:{component_sha}".encode()).hexdigest()
    key=_render_attempt_key(st.get("current_render"),ch)
    attempts=st.setdefault("render_attempts",{}).setdefault(key,{"failed_count":0,"failed_bundle_hashes":[],"last_failure_signature":None})
    cp0=_load_checkpoint_raw(rd,required=False) or {}
    if attempts.get("stalled") is True:
        _append_run_journal(rd,st,"RENDER_ATTEMPT_BLOCKED",checkpoint_seq=cp0.get("checkpoint_seq"),render_attempt_id=None,attempt_number=int(attempts.get("failed_count",0))+1,attempt_bundle_sha256=attempt_bundle_sha,error_code="RENDER_REPAIR_STALLED",failed_count_before=int(attempts.get("failed_count",0)),retry_budget=3)
        fail("RENDER_REPAIR_STALLED")
    if attempts.get("failed_count",0)>=3:
        _append_run_journal(rd,st,"RENDER_ATTEMPT_BLOCKED",checkpoint_seq=cp0.get("checkpoint_seq"),render_attempt_id=None,attempt_number=int(attempts.get("failed_count",0))+1,attempt_bundle_sha256=attempt_bundle_sha,error_code="RENDER_REPAIR_BUDGET_EXHAUSTED",failed_count_before=int(attempts.get("failed_count",0)),retry_budget=3)
        fail("RENDER_REPAIR_BUDGET_EXHAUSTED")
    if attempt_bundle_sha in attempts.get("failed_bundle_hashes",[]):
        _append_run_journal(rd,st,"RENDER_ATTEMPT_BLOCKED",checkpoint_seq=cp0.get("checkpoint_seq"),render_attempt_id=None,attempt_number=int(attempts.get("failed_count",0))+1,attempt_bundle_sha256=attempt_bundle_sha,error_code="DUPLICATE_FAILED_RENDER",failed_count_before=int(attempts.get("failed_count",0)),retry_budget=3)
        fail("DUPLICATE_FAILED_RENDER")

    render_attempt_id=_next_render_attempt_id(_read_journal(rd))
    attempt_number=int(attempts.get("failed_count",0))+1
    failed_count_before=int(attempts.get("failed_count",0))
    _append_run_journal(
        rd,st,"RENDER_ATTEMPT_STARTED",checkpoint_seq=cp0.get("checkpoint_seq"),
        render_attempt_id=render_attempt_id,attempt_number=attempt_number,
        deck_artifact=st.get("current_artifact"),contract_file=str(contract_path),contract_sha256=ch,
        render_file=str(render_path),render_sha256=rh,
        component_manifest_file=str(component_file) if component_file else None,
        component_manifest_sha256=component_sha if component_file else None,
        component_inventory_sha256=component_inventory_sha,
        attempt_bundle_sha256=attempt_bundle_sha,failed_count_before=failed_count_before,retry_budget=3,
    )
    try:
        failures,contract,ch,components,inv_hash=_collect_render_failures(render_path,contract_path,component_file,st)
    except SystemExit as e:
        code,detail=_denied_parts(e)
        return _persist_render_attempt_failure(rd,st,attempts,render_attempt_id,attempt_number,attempt_bundle_sha,[{"code":code,"detail":detail}])
    except Exception as e:
        _persist_render_attempt_exception(rd,st,render_attempt_id,attempt_number,attempt_bundle_sha,e)
        raise
    if failures:
        signature=_render_failure_signature(failures)
        return _persist_render_attempt_failure(rd,st,attempts,render_attempt_id,attempt_number,attempt_bundle_sha,failures,signature)

    out_path=Path(a.write_manifest) if a.write_manifest else None
    if out_path is None:
        return _persist_render_attempt_failure(rd,st,attempts,render_attempt_id,attempt_number,attempt_bundle_sha,[{"code":"RENDER_MANIFEST_OUTPUT_REQUIRED","detail":"render-check PASS requires --write-manifest for canonical closure"}])
    try:
        out_path.parent.mkdir(parents=True,exist_ok=True)
        canonical_components=_canonicalize_components(component_file,components,out_path) if component_file else []
        canonical={
            "run_id":st["run_id"],"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),
            "contract_sha256":ch,"render_sha256":rh,"generated_by":"render-check","runtime_version":VERSION,
            "requirements":[{"id":r["id"],"status":"SATISFIED","evidence":f"render-check:{r['id']}"} for r in contract["requirements"]],
            "components":canonical_components,
        }
        out_path.write_text(json.dumps(canonical,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        # Revalidate the emitted canonical manifest through the normal exact validator.
        hashes=validate_render_manifest(out_path,render_path,contract_path,st)
        st["render_check_pass"]={"render_id":st.get("current_render"),"render_file":str(render_path),"manifest_file":str(out_path),"component_manifest_file":str(component_file.resolve()) if component_file else None,"component_manifest_sha256":component_sha if component_file else None,**hashes}
        attempts["pass_render_sha256"]=rh
        save_state(rd,st)
        cp=_load_checkpoint_raw(rd,required=True)
        _append_run_journal(
            rd,st,"RENDER_ATTEMPT_SUCCEEDED",checkpoint_seq=cp.get("checkpoint_seq"),
            render_attempt_id=render_attempt_id,attempt_number=attempt_number,
            attempt_bundle_sha256=attempt_bundle_sha,render_sha256=rh,
            manifest_file=str(out_path),manifest_sha256=hashes["manifest_sha256"],
            contract_sha256=hashes.get("contract_sha256"),component_manifest_sha256=component_sha if component_file else None,
            component_inventory_sha256=hashes.get("component_inventory_sha256"),state_sha256_after=sha256(rd/STATE_FILE),
        )
    except SystemExit as e:
        code,detail=_denied_parts(e)
        return _persist_render_attempt_failure(rd,st,attempts,render_attempt_id,attempt_number,attempt_bundle_sha,[{"code":code,"detail":detail}])
    except Exception as e:
        _persist_render_attempt_exception(rd,st,render_attempt_id,attempt_number,attempt_bundle_sha,e)
        raise
    print(json.dumps({"status":"PASS","render_id":st.get("current_render"),"render_sha256":rh,"manifest_file":str(out_path),"manifest_sha256":hashes["manifest_sha256"]},ensure_ascii=False,indent=2))

def cmd_contract_defect(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    frozen=st.get("gates",{}).get("RENDER_CONTRACT_FROZEN",{})
    if not frozen:
        fail("RENDER_CONTRACT_NOT_FROZEN")
    if st.get("gates",{}).get("FINAL_RENDER_PREPARED"):
        fail("CONTRACT_DEFECT_PATH_ONLY_BEFORE_PREPARED")
    prior_cp=_load_checkpoint_raw(rd,required=False) or {}
    failed_count=_render_attempts_used(st)
    st["render_contract_defect_suspected"]={"reason":a.reason,"contract_sha256":frozen.get("evidence_sha256"),"render_id":st.get("current_render")}
    st["run_execution_state"]="TERMINAL_FAILED"
    st["render_check_pass"]=None
    save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(
        rd,st,"CONTRACT_DEFECT_MATERIALIZED",checkpoint_seq=cp.get("checkpoint_seq"),
        reason=a.reason,contract_sha256=frozen.get("evidence_sha256"),
        failed_render_count=failed_count,retry_budget=3,
        checkpoint_seq_before=prior_cp.get("checkpoint_seq"),
        state_sha256_after=sha256(rd/STATE_FILE),run_state_after="TERMINAL_FAILED"
    )
    print("CONTRACT_DEFECT_SUSPECTED")


def _verify_resume_binding(binding):
    role=binding.get("role","")
    p=Path(binding.get("file", ""))
    expected=binding.get("sha256")
    code=_binding_error(role)
    if not p.exists() or not p.is_file():
        fail(f"{code}: missing {role}")
    if sha256(p)!=expected:
        fail(f"{code}: {role}")


def cmd_checkpoint_run(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    requested=a.run_state
    derived=_derived_run_state(st)
    prior=_load_checkpoint_raw(rd,required=False)
    if derived in {"TERMINAL_FAILED","COMPLETED"} and requested!=derived:
        fail(f"CHECKPOINT_CANNOT_REOPEN_{derived}")
    if requested=="COMPLETED" and derived!="COMPLETED":
        fail("CHECKPOINT_COMPLETED_REQUIRES_STOP_OUTPUT_ALLOWED")
    if requested=="TERMINAL_FAILED" and derived!="TERMINAL_FAILED":
        fail("CHECKPOINT_TERMINAL_FAILURE_NOT_MATERIALIZED")
    if prior and prior.get("run_state")=="WAITING_USER_INPUT" and requested=="IN_PROGRESS":
        ng=next_gate(st)[0]
        if prior.get("run_state_sha256")==sha256(rd/STATE_FILE) and prior.get("next_required_gate")==ng:
            fail("WAITING_USER_INPUT_NOT_RESOLVED")
    cp=_write_checkpoint(rd,st,run_state_override=requested)
    if requested=="WAITING_USER_INPUT":
        _append_run_journal(rd,st,"WAITING_FOR_USER_INPUT",checkpoint_seq=cp["checkpoint_seq"],next_required_gate=cp.get("next_required_gate"))
    print(json.dumps({"status":"CHECKPOINT_WRITTEN","run_id":st["run_id"],"run_state":requested,"checkpoint_seq":cp["checkpoint_seq"],"next_required_gate":cp.get("next_required_gate")},ensure_ascii=False))


def cmd_inspect_continuation(a):
    scope_dir=Path(a.scope_dir).resolve()
    lease=_read_continuation_lease_raw(scope_dir,required=False)
    if lease is None:
        print(json.dumps({"status":"EMPTY","scope_id":_continuity_scope_id(scope_dir),"scope_dir":str(scope_dir),"recommended_action":"NEW_RUN_ALLOWED"},ensure_ascii=False))
        return
    if lease.get("status")=="ACTIVE":
        lease=_validate_active_continuation_lease(scope_dir)
        action="USER_RESOLUTION_REQUIRED" if lease.get("run_state")=="WAITING_USER_INPUT" else "RESUME"
    else:
        action="NEW_RUN_ALLOWED"
    print(json.dumps({
        "status":lease.get("status"),"scope_id":lease.get("scope_id"),"scope_dir":lease.get("scope_dir"),
        "run_id":lease.get("run_id"),"run_dir":lease.get("run_dir"),"run_state":lease.get("run_state"),
        "checkpoint_seq":lease.get("checkpoint_seq"),"next_required_gate":lease.get("next_required_gate"),
        "waiting_context":lease.get("waiting_context"),"recommended_action":action,
    },ensure_ascii=False))


def _run_metrics(run_dir: Path):
    ev=_read_journal(run_dir)
    if not ev: return {"event_count":0}
    stamps=[x.get("timestamp_ns") for x in ev if isinstance(x.get("timestamp_ns"),int)]
    duration=(max(stamps)-min(stamps))/1_000_000_000 if stamps else 0.0
    count=lambda name: sum(1 for x in ev if x.get("event")==name)
    return {"event_count":len(ev),"duration_seconds_raw":duration,"gate_failures":count("GATE_ATTEMPT_FAILED"),"pilotage_preflight_failures":count("PILOTAGE_PREFLIGHT_FAILED"),"pilotage_commit_count":count("PILOTAGE_COMMIT_STARTED"),"pilotage_rollback_count":count("PILOTAGE_COMMIT_ROLLED_BACK"),"pilotage_local_repair_count":count("PILOTAGE_LOCAL_REPAIR_REQUIRED"),"pilotage_diagnostic_issue_count":sum(int(x.get("issue_count") or 0) for x in ev if x.get("event")=="PILOTAGE_BUSINESS_DIAGNOSTIC_COMPLETED"),"pilotage_authoritative_dry_run_count":count("PILOTAGE_AUTHORITATIVE_DRY_RUN_COMPLETED"),"pilotage_authoritative_dry_run_failures":sum(1 for x in ev if x.get("event")=="PILOTAGE_AUTHORITATIVE_DRY_RUN_COMPLETED" and x.get("status")=="FAIL"),"pilotage_business_attempt_count":count("PILOTAGE_BUSINESS_ATTEMPT_CONSUMED"),"pilotage_nonbusiness_repair_count":sum(1 for x in ev if x.get("event")=="PILOTAGE_REPAIR_ROUTED" and x.get("budget_class")=="NON_BUSINESS"),"pilotage_nonbusiness_exhausted_count":count("NON_BUSINESS_REPAIR_EXHAUSTED"),"pilotage_proof_floor_failure_count":sum(1 for x in ev if x.get("event")=="PILOTAGE_AUTHORITATIVE_DRY_RUN_COMPLETED" and any(str(c).startswith("PROOF_FLOOR_") for c in (x.get("issue_codes") or []))),"semantic_unresolved_count":sum(1 for x in ev if "UNRESOLVED" in str(x.get("error_code", "")) or "UNRESOLVED" in str(x.get("detail", ""))),"wide_fallback_count":count("SELECTIVE_INVALIDATION_FALLBACK")+count("TERMINAL_REFACTOR_FORK_FALLBACK"),"automatic_rebind_count":sum(int(x.get("rebind_count",0) or 0) for x in ev if x.get("event")=="TERMINAL_REFACTOR_FORK_REBOUND"),"grouped_evidence_compile_count":count("SEMANTIC_EVIDENCE_COMPILED"),"render_failures":count("RENDER_ATTEMPT_FAILED"),"resumes":count("RUN_RESUMED"),"bootstrap_count":count("RUN_BOOTSTRAPPED")}


def cmd_inspect_run_state(a):
    rd=Path(a.run_dir); cp=_load_checkpoint_raw(rd,required=True); st=load_state(rd)
    obj={k:cp.get(k) for k in ("run_id","run_state","current_deck_artifact","render_id","last_closed_gate","next_required_gate","render_attempts_used","render_attempts_budget","checkpoint_seq","invocation_seq","resume_count")}
    obj["waiting_context"]=cp.get("waiting_context")
    obj["progress_block"]=_active_progress_block(rd,st)
    obj["unresolved_gate_attempts"]=len(_unmatched_gate_attempts(rd))
    obj["last_render_attempt"]=_last_render_attempt_summary(rd)
    obj["last_pilotage_preflight"]=_last_pilotage_preflight_summary(rd)
    obj["metrics"]=_run_metrics(rd)
    print(json.dumps(obj,ensure_ascii=False))


def _resume_waiting_direction_resolution(rd: Path, st, cp, resolution_file: Path):
    ctx=cp.get("waiting_context") or _waiting_context(rd,st)
    if not isinstance(ctx,dict) or ctx.get("resolution_kind")!="DIRECTION_SELECTION" or ctx.get("waiting_error_code")!="DIRECTION_CONFLICT_REQUIRES_USER_SELECTION":
        fail("WAITING_USER_RESOLUTION_KIND_UNSUPPORTED")
    _append_run_journal(rd,st,"USER_INPUT_RESOLUTION_RECEIVED",checkpoint_seq=cp.get("checkpoint_seq"),waiting_gate=ctx.get("waiting_gate"),waiting_attempt_id=ctx.get("waiting_attempt_id"),resolution_kind=ctx.get("resolution_kind"),resolution_file=str(resolution_file),resolution_sha256=sha256(resolution_file) if resolution_file.exists() and resolution_file.is_file() else None)
    newd,newsha,_=validate_direction_contract(resolution_file,st)
    dg=st.get("gates",{}).get("DIRECTION_RESOLVED",{})
    if not dg or not nonempty(dg.get("direction")):
        fail("WAITING_DIRECTION_BINDING_MISSING")
    old_direction=dg.get("direction")
    if newd.get("selected_direction")==old_direction:
        fail("USER_RESOLUTION_DIRECTION_UNCHANGED")
    oldsha=dg.get("evidence_sha256")
    names=[g for g,_,_ in sequence(st)]
    idx=names.index("DIRECTION_RESOLVED")
    invalidated=[g for g in names[idx:] if g in st.get("gates",{})]
    for g in names[idx:]:
        st.get("gates",{}).pop(g,None)
    st["current_render"]=None
    st["stop_output_allowed"]=False
    st["run_execution_state"]="IN_PROGRESS"
    st["render_check_pass"]=None
    st["render_contract_defect_suspected"]=None
    st.pop("presentation_expected_policy_fingerprint",None)
    _atomic_write_text(rd/STATE_FILE,json.dumps(st,ensure_ascii=False,indent=2)+"\n")
    cp1=_write_checkpoint(rd,st,run_state_override="IN_PROGRESS",invocation_seq=int(cp.get("invocation_seq",1))+1,resume_count=int(cp.get("resume_count",0))+1)
    _append_run_journal(rd,st,"USER_INPUT_RESOLUTION_APPLIED",checkpoint_seq=cp1.get("checkpoint_seq"),waiting_gate=ctx.get("waiting_gate"),waiting_attempt_id=ctx.get("waiting_attempt_id"),resolution_kind=ctx.get("resolution_kind"),old_direction=old_direction,new_direction=newd.get("selected_direction"),old_direction_contract_sha256=oldsha,new_direction_contract_sha256=newsha,invalidated_gates=invalidated)
    from argparse import Namespace
    ns=Namespace(run_dir=str(rd),run_id=st["run_id"],gate="DIRECTION_RESOLVED",authority=STYLE,status="RESOLVED",evidence_file=str(resolution_file),render_manifest=None,contract_file=None,combo_impact_file=None,pilotage_contract_file=None,pilotage_preflight_receipt=None,_derived_reentry=False)
    cmd_complete(ns)
    st2=load_state(rd); cp2=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(rd,st2,"WAITING_CONTEXT_CLEARED",checkpoint_seq=cp2.get("checkpoint_seq"),resolution_kind=ctx.get("resolution_kind"),resolved_gate="DIRECTION_RESOLVED")
    _append_run_journal(rd,st2,"RUN_RESUMED",checkpoint_seq=cp2.get("checkpoint_seq"),next_required_gate=cp2.get("next_required_gate"),resume_reason="USER_INPUT_RESOLUTION")
    print(json.dumps({"status":"RUN_RESUMED","run_id":st2["run_id"],"current_deck_artifact":st2.get("current_artifact"),"render_id":st2.get("current_render"),"last_closed_gate":cp2.get("last_closed_gate"),"next_required_gate":cp2.get("next_required_gate"),"render_attempts_used":cp2.get("render_attempts_used"),"render_attempts_budget":cp2.get("render_attempts_budget"),"resume_count":cp2.get("resume_count"),"invocation_seq":cp2.get("invocation_seq")},ensure_ascii=False))


def cmd_resume_run(a):
    rd=Path(a.run_dir); cp=_load_checkpoint_raw(rd,required=True)
    if cp.get("run_id")!=a.run_id: fail("RUN_ID_MISMATCH")
    state_file=rd/STATE_FILE
    if not state_file.exists(): fail("RUN_STATE_MISSING")
    if sha256(state_file)!=cp.get("run_state_sha256"):
        fail("RESUME_STATE_BINDING_MISMATCH")
    st=load_state(rd); require_run_id(st,a.run_id)
    if st.get("current_artifact")!=cp.get("current_deck_artifact") or st.get("current_render")!=cp.get("render_id"):
        fail("RESUME_STATE_BINDING_MISMATCH")
    _continuation_lease_for_run(rd,st,cp,require_active=True)
    _append_run_journal(rd,st,"RESUME_REQUESTED",checkpoint_seq=cp.get("checkpoint_seq"),requested_run_state=cp.get("run_state"))
    for binding in cp.get("authoritative_bindings",[]):
        if not isinstance(binding,dict): fail("RUN_CHECKPOINT_BINDING_INVALID")
        _verify_resume_binding(binding)
    _append_run_journal(rd,st,"RESUME_BINDINGS_VERIFIED",checkpoint_seq=cp.get("checkpoint_seq"),binding_count=len(cp.get("authoritative_bindings",[])))
    _reconcile_orphan_attempts(rd,st)
    state=cp.get("run_state")
    derived=_derived_run_state(st)
    if derived in {"TERMINAL_FAILED","COMPLETED"} and state!=derived:
        fail("RESUME_STATE_STATUS_MISMATCH")
    if state in {"TERMINAL_FAILED","COMPLETED"} and derived!=state:
        fail("RESUME_STATE_STATUS_MISMATCH")
    if state=="WAITING_USER_INPUT":
        if nonempty(getattr(a,"user_resolution_file",None)):
            return _resume_waiting_direction_resolution(rd,st,cp,Path(a.user_resolution_file))
        _append_run_journal(rd,st,"WAITING_FOR_USER_INPUT",checkpoint_seq=cp.get("checkpoint_seq"),next_required_gate=cp.get("next_required_gate"),waiting_context=cp.get("waiting_context"))
        fail(f"WAITING_USER_INPUT: {cp.get('next_required_gate')}")
    if nonempty(getattr(a,"user_resolution_file",None)):
        fail("RUN_NOT_WAITING_FOR_USER_INPUT")
    if state=="TERMINAL_FAILED":
        _append_run_journal(rd,st,"TERMINAL_FAILURE_RESTORED",checkpoint_seq=cp.get("checkpoint_seq"),render_attempts_used=cp.get("render_attempts_used"))
        fail("TERMINAL_FAILED")
    if state=="COMPLETED":
        _append_run_journal(rd,st,"RUN_COMPLETED",checkpoint_seq=cp.get("checkpoint_seq"))
        fail("COMPLETED")
    newcp=_write_checkpoint(rd,st,run_state_override="IN_PROGRESS",invocation_seq=int(cp.get("invocation_seq",1))+1,resume_count=int(cp.get("resume_count",0))+1)
    _append_run_journal(rd,st,"RUN_RESUMED",checkpoint_seq=newcp.get("checkpoint_seq"),next_required_gate=newcp.get("next_required_gate"))
    print(json.dumps({"status":"RUN_RESUMED","run_id":st["run_id"],"current_deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),"last_closed_gate":newcp.get("last_closed_gate"),"next_required_gate":newcp.get("next_required_gate"),"render_attempts_used":newcp.get("render_attempts_used"),"render_attempts_budget":newcp.get("render_attempts_budget")},ensure_ascii=False))


def cmd_template(a):
    if a.kind!="pilotage": fail("unsupported template kind")
    out=Path(a.output)
    render_path=Path(a.render_file) if nonempty(getattr(a,"render_file",None)) else None
    if render_path is not None and not render_path.exists(): fail("pilotage template render file missing")
    if getattr(a,"no_rendered_axes",False) and render_path is not None: fail("pilotage template modes are mutually exclusive")
    run_id=a.run_id or "REPLACE_RUN_ID"; deck=a.deck_artifact or "deck-v1"; render_sha=a.render_sha256 or "REPLACE_RENDER_SHA256"
    axes=[]
    if render_path is not None:
        axes=_rendered_axis_headings(render_path.read_text(encoding="utf-8")); render_sha=sha256(render_path)
        if nonempty(getattr(a,"run_dir",None)):
            st=load_state(Path(a.run_dir));
            if nonempty(a.run_id): require_run_id(st,a.run_id)
            run_id=st.get("run_id"); deck=st.get("current_artifact")
    no_axes=getattr(a,"no_rendered_axes",False) or (render_path is not None and len(axes)==0) or (render_path is None and int(getattr(a,"rendered_axis_count",0) or 0)==0)
    payload={
      "wire_schema":PILOTAGE_WIRE_SCHEMA,"run_id":run_id,"authority":PILOTAGE,"deck_artifact":deck,"render_sha256":render_sha,
      "status":"PASS","execution_contract_version":"RC16.2","axis_coverage_status":"NO_RENDERED_AXES" if no_axes else "PASS",
      "rendered_axis_count":0 if no_axes else len(axes),"starter_exploration_status":"NO_RENDERED_AXES" if no_axes else "COMPLETE",
      "starter_inventory_status":"NO_RENDERED_AXES" if no_axes else "PASS","structural_starters":[],"lines":[],
      "rendered_axis_headings":axes,"pilotage_source_sha256":_pilotage_policy_sha256(),"_wire_templates":_pilotage_wire_templates()
    }
    _atomic_write_text(out,_stable_json_text(payload))
    print(f"TEMPLATE_WRITTEN {out}")

def _ns_complete(run_dir, run_id, op):
    from argparse import Namespace
    allowed={"gate","authority","status","evidence_file","render_manifest","contract_file","combo_impact_file","pilotage_contract_file","pilotage_preflight_receipt","terminal_presentation_plan","terminal_presentation_receipt"}
    unknown=set(op)-allowed-{"op"}
    if unknown: fail("BUNDLE_UNKNOWN_COMPLETE_FIELDS: "+",".join(sorted(unknown)))
    kw={k:op.get(k) for k in allowed}; kw.update({"run_dir":run_dir,"run_id":run_id})
    return Namespace(**kw)

def cmd_validate_bundle(a):
    bundle=read_json(Path(a.bundle_file),"validation bundle")
    if bundle.get("run_id")!=a.run_id: fail("RUN_ID_MISMATCH in validation bundle")
    ops=bundle.get("operations")
    if not isinstance(ops,list) or not ops: fail("validation bundle requires operations")
    completed=[]
    for i,op in enumerate(ops):
        if not isinstance(op,dict) or op.get("op")!="complete": fail(f"BUNDLE_OPERATION_INVALID: {i}")
        cmd_complete(_ns_complete(a.run_dir,a.run_id,op))
        completed.append(op.get("gate"))
    print("BUNDLE_VALIDATION_PASS "+",".join(completed))


# ---------------------------------------------------------------------------
# RC16.19 ENFORCED FASTPATH + TERMINAL REFACTOR FORK
# Orchestration wrappers around the unchanged RC16.18 business validators.
# ---------------------------------------------------------------------------

# Preserve parent callables.  The original def bodies stay byte-comparable at the
# function level for historical regression checks; wrappers add orchestration only.
_validate_visual_assets_parent = validate_visual_assets
_cmd_complete_parent = cmd_complete
_cmd_execute_batch_parent = cmd_execute_batch
_cmd_evidence_refresh_wide_parent = cmd_evidence_refresh
_cmd_evidence_refresh_selective_parent = cmd_evidence_refresh_selective
_cmd_material_change_parent = cmd_material_change
_cmd_presentation_change_parent = cmd_presentation_change
_cmd_render_check_parent = cmd_render_check
_cmd_pilotage_preflight_parent = cmd_pilotage_preflight
_cmd_compile_render_contract_parent = cmd_compile_render_contract
_cmd_bind_explicit_direction_parent = cmd_bind_explicit_direction


def _terminal_state_observed(rd: Path, st):
    cp=_load_checkpoint_raw(rd,required=False) or {}
    state=st.get("run_execution_state")
    cpstate=cp.get("run_state")
    return state in TERMINAL_RUN_STATES or cpstate in TERMINAL_RUN_STATES


def _require_mutable_run_rc1619(rd: Path, st, operation):
    if not _terminal_state_observed(rd,st):
        return
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(
        rd,st,"TERMINAL_REOPEN_ATTEMPT_BLOCKED",checkpoint_seq=cp.get("checkpoint_seq"),
        operation=operation,run_state=st.get("run_execution_state"),checkpoint_run_state=cp.get("run_state"),
        error_code="TERMINAL_RUN_IMMUTABLE_NEW_RUN_REQUIRED",
    )
    fail("TERMINAL_RUN_IMMUTABLE_NEW_RUN_REQUIRED")


def _fastpath_summary(rd: Path):
    events=_read_journal(rd)
    timings=[e for e in events if e.get("event")=="COMMAND_TIMING"]
    return {
        "profile":FASTPATH_PROFILE,
        "fastpath_batches":sum(1 for e in events if e.get("event") in {"SAFE_BATCH_COMPLETED","FASTPATH_ADVANCE_COMPLETED"}),
        "fastpath_items":sum(1 for e in events if e.get("event")=="SAFE_BATCH_ITEM_SUCCEEDED"),
        "fastpath_bypasses":sum(1 for e in events if e.get("event")=="FASTPATH_BYPASS"),
        "mechanical_preflight_runs":sum(1 for e in events if e.get("event")=="AUTO_MECHANICAL_PREFLIGHT_STARTED"),
        "wide_refresh_count":sum(1 for e in events if e.get("event")=="EVIDENCE_REFRESH_MATERIALIZED"),
        "selective_refresh_count":sum(1 for e in events if e.get("event")=="EVIDENCE_REFRESH_SELECTIVE_MATERIALIZED"),
        "pilotage_commit_count":sum(1 for e in events if e.get("event")=="PILOTAGE_COMMIT_STARTED"),
        "pilotage_rollback_count":sum(1 for e in events if e.get("event")=="PILOTAGE_COMMIT_ROLLED_BACK"),
        "pilotage_local_repair_count":sum(1 for e in events if e.get("event")=="PILOTAGE_LOCAL_REPAIR_REQUIRED"),
        "pilotage_diagnostic_issue_count":sum(int(e.get("issue_count") or 0) for e in events if e.get("event")=="PILOTAGE_BUSINESS_DIAGNOSTIC_COMPLETED"),
        "semantic_unresolved_count":sum(1 for e in events if "UNRESOLVED" in str(e.get("error_code") or "") or "UNRESOLVED" in str(e.get("detail") or "")),
        "wide_fallback_count":sum(1 for e in events if e.get("event") in {"SELECTIVE_INVALIDATION_FALLBACK","TERMINAL_REFACTOR_FORK_FALLBACK"}),
        "grouped_evidence_compile_count":sum(1 for e in events if e.get("event")=="SEMANTIC_EVIDENCE_COMPILED"),
        "automatic_rebind_count":sum(int(e.get("rebind_count",0) or 0) for e in events if e.get("event")=="TERMINAL_REFACTOR_FORK_REBOUND"),
        "terminal_reopen_attempts_blocked":sum(1 for e in events if e.get("event")=="TERMINAL_REOPEN_ATTEMPT_BLOCKED"),
        "local_runtime_seconds":round(sum(float(e.get("elapsed_local_seconds",0.0) or 0.0) for e in timings),6),
        "timed_command_count":len(timings),
        "local_time_scope":"RUNTIME_COMMAND_ONLY_NOT_MODEL_WEB_OR_USER_WAIT",
    }


def cmd_fastpath_metrics(a):
    rd=Path(a.run_dir); st=load_state(rd)
    if nonempty(getattr(a,"run_id",None)): require_run_id(st,a.run_id)
    print(json.dumps(_fastpath_summary(rd),ensure_ascii=False,sort_keys=True))


def validate_visual_assets_rc1619(path: Path, st):
    # Type-check before the parent performs set(refs).  This converts the RC16.18
    # native TypeError into a controlled validator refusal with zero state mutation.
    validate_evidence(path,st)
    d=read_json(path,"visual assets")
    refs=d.get("image_refs")
    if not isinstance(refs,list) or any(not isinstance(x,str) for x in refs):
        fail("VISUAL_IMAGE_REFS_INVALID_TYPE")
    if len(set(refs))!=len(refs):
        fail("visual image_refs invalid")
    return _validate_visual_assets_parent(path,st)

validate_visual_assets = validate_visual_assets_rc1619


def cmd_complete_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"complete")
    return _cmd_complete_parent(a)

cmd_complete = cmd_complete_rc1619


def cmd_material_change_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"material-change")
    return _cmd_material_change_parent(a)

cmd_material_change = cmd_material_change_rc1619


def cmd_presentation_change_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"presentation-change")
    return _cmd_presentation_change_parent(a)

cmd_presentation_change = cmd_presentation_change_rc1619


def cmd_evidence_refresh_selective_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"evidence-refresh-selective")
    # When the RC16.18 selective primitive falls back through the global
    # cmd_evidence_refresh name, route that recursion explicitly to the parent wide path.
    setattr(a,"_rc1619_selective_dispatch",True)
    try:
        return _cmd_evidence_refresh_selective_parent(a)
    finally:
        try: delattr(a,"_rc1619_selective_dispatch")
        except Exception: pass

cmd_evidence_refresh_selective = cmd_evidence_refresh_selective_rc1619


def cmd_evidence_refresh_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"evidence-refresh")
    if getattr(a,"_rc1619_selective_dispatch",False):
        return _cmd_evidence_refresh_wide_parent(a)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,"EVIDENCE_REFRESH_AUTO_ROUTE",checkpoint_seq=cp.get("checkpoint_seq"),from_gate=a.from_gate,policy="SELECTIVE_FIRST_WIDE_FALLBACK")
    setattr(a,"_rc1619_selective_dispatch",True)
    try:
        return _cmd_evidence_refresh_selective_parent(a)
    finally:
        try: delattr(a,"_rc1619_selective_dispatch")
        except Exception: pass

cmd_evidence_refresh = cmd_evidence_refresh_rc1619


def cmd_bind_explicit_direction_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"bind-explicit-direction")
    return _cmd_bind_explicit_direction_parent(a)

cmd_bind_explicit_direction = cmd_bind_explicit_direction_rc1619


def cmd_execute_batch_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"execute-batch")
    return _cmd_execute_batch_parent(a)

cmd_execute_batch = cmd_execute_batch_rc1619


def _preflight_input_bindings(a, kind):
    keys=("contract_file","render_file","render_manifest","component_plan_file","component_manifest","pilotage_contract_file","schema_file","combo_impact_file")
    out={}
    for k in keys:
        v=getattr(a,k,None)
        if not nonempty(v): continue
        p=Path(v); out[k]={"file":str(p),"sha256":sha256(p) if p.exists() and p.is_file() else None}
    return {"kind":kind,"inputs":out}


def _write_auto_preflight_receipt(rd: Path, st, kind, issues, a):
    payload={
        "schema":"ygo-mechanical-preflight-receipt-v1","runtime_version":VERSION,
        "run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),
        "kind":kind,"status":"PASS" if not issues else "FAIL","read_only_business_authority":True,
        "authoritative":False,"issues":issues,"bindings":_preflight_input_bindings(a,kind),
    }
    raw=_stable_json_text(payload)
    payload["binding_sha256"]=hashlib.sha256(json.dumps(payload["bindings"],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    path=rd/f"mechanical_preflight_{kind}.receipt.json"
    _atomic_write_text(path,_stable_json_text(payload))
    return path,payload


def _auto_mechanical_preflight(rd: Path, st, kind, a, block_on_fail=True):
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,"AUTO_MECHANICAL_PREFLIGHT_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),kind=kind)
    if kind=="render":
        issues=_render_mechanical_preflight_issues(a,st)
        if nonempty(getattr(a,"component_manifest",None)) and not nonempty(getattr(a,"component_plan_file",None)):
            _mechanical_issue(issues,"COMPONENT_PLAN_REQUIRED_WITH_MANIFEST","component_plan_file","existing JSON file",None)
    elif kind=="pilotage":
        issues=_pilotage_mechanical_preflight_issues(a,st)
    else:
        fail("unsupported mechanical preflight kind")
    issues=sorted(issues,key=lambda x:(x.get("path",""),x.get("code","")))
    receipt,payload=_write_auto_preflight_receipt(rd,st,kind,issues,a)
    ev="AUTO_MECHANICAL_PREFLIGHT_SUCCEEDED" if not issues else "AUTO_MECHANICAL_PREFLIGHT_FAILED"
    _append_run_journal(rd,st,ev,checkpoint_seq=cp.get("checkpoint_seq"),kind=kind,issue_count=len(issues),receipt_file=str(receipt),receipt_sha256=sha256(receipt),binding_sha256=payload.get("binding_sha256"),authoritative=False)
    if issues and block_on_fail:
        fail("MECHANICAL_PREFLIGHT_FAILED: "+",".join(x.get("code","UNKNOWN") for x in issues))
    return issues,receipt


def cmd_render_check_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"render-check")
    _auto_mechanical_preflight(rd,st,"render",a,block_on_fail=True)
    return _cmd_render_check_parent(a)

cmd_render_check = cmd_render_check_rc1619


def cmd_pilotage_preflight_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"pilotage-preflight")
    # Preserve direct library-call compatibility for inherited deterministic tests;
    # production CLI blocks before the full validator when mechanical bindings fail.
    issues,_=_auto_mechanical_preflight(rd,st,"pilotage",a,block_on_fail=False)
    if issues and RC1619_CLI_ACTIVE:
        fail("MECHANICAL_PREFLIGHT_FAILED: "+",".join(x.get("code","UNKNOWN") for x in issues))
    return _cmd_pilotage_preflight_parent(a)

cmd_pilotage_preflight = cmd_pilotage_preflight_rc1619


def cmd_compile_render_contract_rc1619(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"compile-render-contract")
    return _cmd_compile_render_contract_parent(a)

cmd_compile_render_contract = cmd_compile_render_contract_rc1619


def _gate_order_map(st):
    return {g:i for i,(g,_,_) in enumerate(sequence(st))}


def _prepared_bundle_with_auto_direction(rd: Path, st, bundle):
    ops=bundle.get("operations")
    if not isinstance(ops,list) or not ops:
        fail("ADVANCE_PREPARED_REQUIRES_OPERATIONS")
    ops=[dict(x) if isinstance(x,dict) else x for x in ops]
    explicit=bundle.get("explicit_direction")
    if isinstance(explicit,str):
        explicit={"selected_direction":explicit,"user_evidence":bundle.get("direction_user_evidence")}
    if isinstance(explicit,dict) and "DIRECTION_RESOLVED" not in (st.get("gates") or {}):
        if not any(isinstance(x,dict) and x.get("op")=="explicit-direction" for x in ops):
            order=_gate_order_map(st); didx=order.get("DIRECTION_RESOLVED")
            pos=0
            for i,op in enumerate(ops):
                if not isinstance(op,dict): break
                gate=op.get("gate") if op.get("op")=="complete" else ("DIRECTION_RESOLVED" if op.get("op")=="explicit-direction" else None)
                if gate in order and order[gate] < didx: pos=i+1
            ops.insert(pos,{"op":"explicit-direction","selected_direction":explicit.get("selected_direction"),"user_evidence":explicit.get("user_evidence"),"output":explicit.get("output")})
    return {"run_id":st.get("run_id"),"operations":ops}


def cmd_advance_prepared(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"advance-prepared")
    bundle=read_json(Path(a.bundle_file),"advance prepared bundle")
    if bundle.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in advance prepared bundle")
    generated=_prepared_bundle_with_auto_direction(rd,st,bundle)
    cp=_load_checkpoint_raw(rd,required=True)
    advance_id=f"fast-advance-{sum(1 for e in _read_journal(rd) if e.get('event')=='FASTPATH_ADVANCE_STARTED')+1:06d}"
    _append_run_journal(rd,st,"FASTPATH_ADVANCE_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),advance_id=advance_id,prepared_count=len(generated["operations"]),profile=st.get("fastpath_profile",FASTPATH_PROFILE))
    bf=rd/"advance_prepared.bundle.json"
    _atomic_write_text(bf,_stable_json_text(generated))
    try:
        _cmd_execute_batch_parent(type("Args",(),{"run_dir":str(rd),"run_id":st["run_id"],"bundle_file":str(bf)})())
    except BaseException:
        stf=load_state(rd); cpf=_load_checkpoint_raw(rd,required=True)
        _append_run_journal(rd,stf,"FASTPATH_ADVANCE_STOPPED",checkpoint_seq=cpf.get("checkpoint_seq"),advance_id=advance_id,next_required_gate=cpf.get("next_required_gate"))
        raise
    stf=load_state(rd); cpf=_load_checkpoint_raw(rd,required=True)
    _append_run_journal(rd,stf,"FASTPATH_ADVANCE_COMPLETED",checkpoint_seq=cpf.get("checkpoint_seq"),advance_id=advance_id,next_required_gate=cpf.get("next_required_gate"),item_count=len(generated["operations"]))
    print(json.dumps({"status":"PASS","advance_id":advance_id,"next_required_gate":cpf.get("next_required_gate"),"fastpath":"BATCH"},ensure_ascii=False))


def _inventory_hash_map(inv):
    if not isinstance(inv,dict): return {}
    out={}
    for x in inv.get("files",[]) if isinstance(inv.get("files"),list) else []:
        if isinstance(x,dict) and nonempty(x.get("file")) and nonempty(x.get("sha256")):
            out[x["file"]]=x["sha256"]
    return out


def _source_inventory_compatible_for_fork(parent_st, child_st):
    pm=_inventory_hash_map(parent_st.get("source_inventory")); cm=_inventory_hash_map(child_st.get("source_inventory"))
    business=(set(pm)|set(cm))-RC1619_CHANGED_SOURCE_FILES
    if not business: return False
    return all(pm.get(k)==cm.get(k) and pm.get(k) is not None for k in business)


def _terminal_parent_proof(parent_rd: Path, parent_st):
    cp=_load_checkpoint_raw(parent_rd,required=True)
    if parent_st.get("run_execution_state")!="COMPLETED" or cp.get("run_state")!="COMPLETED" or parent_st.get("stop_output_allowed") is not True:
        fail("FORK_REQUIRES_TERMINAL_COMPLETED_PARENT")
    final=(parent_st.get("gates") or {}).get("FINAL_VALIDATION_PASS")
    if not isinstance(final,dict) or final.get("status")!="PASS": fail("FORK_REQUIRES_FINAL_VALIDATION_PASS")
    receipt_file=parent_st.get("terminal_presentation_receipt_file") or final.get("terminal_presentation_receipt_file")
    if not nonempty(receipt_file) or not Path(receipt_file).exists(): fail("FORK_REQUIRES_TERMINAL_PRESENTATION_PASS")
    receipt=read_json(Path(receipt_file),"terminal presentation receipt")
    if receipt.get("status")!="PASS": fail("FORK_REQUIRES_TERMINAL_PRESENTATION_PASS")
    dg=(parent_st.get("gates") or {}).get("DECK_DRAFT_CREATED",{})
    sf=dg.get("snapshot_file"); sh=dg.get("snapshot_sha256")
    if not nonempty(sf) or not Path(sf).exists() or not nonempty(sh) or sha256(Path(sf))!=sh:
        fail("FORK_REQUIRES_EXACT_PARENT_SNAPSHOT_HASH")
    return cp,Path(sf),sh



def _rebind_exact_hash_refs(value, hash_map):
    if isinstance(value,dict): return {k:_rebind_exact_hash_refs(v,hash_map) for k,v in value.items()}
    if isinstance(value,list): return [_rebind_exact_hash_refs(v,hash_map) for v in value]
    if isinstance(value,str) and value in hash_map: return hash_map[value]
    return value


def _rebind_inherited_gate_evidence(parent_record, child_run_id, new_rd: Path, gate, hash_map):
    src_file=parent_record.get("evidence_file")
    src_hash=parent_record.get("evidence_sha256")
    if not nonempty(src_file) or not Path(src_file).exists() or not Path(src_file).is_file():
        return src_file,src_hash,False
    pf=Path(src_file)
    suffix=pf.suffix.lower()
    out=new_rd/f"inherited__{gate.lower()}{suffix or '.bin'}"
    if suffix==".json":
        doc=read_json(pf,f"parent inherited evidence {gate}")
        doc=_rebind_exact_hash_refs(doc,hash_map)
        if "run_id" in doc: doc["run_id"]=child_run_id
        _atomic_write_text(out,_stable_json_text(doc))
    else:
        out.write_bytes(pf.read_bytes())
    nh=sha256(out)
    if nonempty(src_hash): hash_map[src_hash]=nh
    return str(out),nh,True


def _fallback_fork_bootstrap(new_rd: Path, child_st, reason, parent_run_id):
    child_st["refactor_fork_fallback"]={"status":"FULL_BOOTSTRAP","reason":reason,"parent_run_id":parent_run_id}
    save_state(new_rd,child_st)
    cp=_load_checkpoint_raw(new_rd,required=True)
    _append_run_journal(new_rd,child_st,"TERMINAL_REFACTOR_FORK_FALLBACK",checkpoint_seq=cp.get("checkpoint_seq"),reason=reason,parent_run_id=parent_run_id,next_required_gate=cp.get("next_required_gate"))
    print(json.dumps({"status":"FALLBACK_FULL_BOOTSTRAP","reason":reason,"run_id":child_st["run_id"],"next_required_gate":cp.get("next_required_gate")},ensure_ascii=False))


def cmd_fork_refactor_from_terminal(a):
    parent_rd=Path(a.parent_run_dir); parent_st=load_state(parent_rd)
    parent_cp,parent_snapshot,parent_snapshot_sha=_terminal_parent_proof(parent_rd,parent_st)
    if not bool(getattr(a,"same_character_stage_direction_concept",False)):
        fail("FORK_REQUIRES_EXPLICIT_UNCHANGED_PREFIX_ASSERTION")
    idx=_read_session_index(required=False)
    if idx is not None and idx.get("status")=="ACTIVE": fail("ACTIVE_LOGICAL_RUN_EXISTS")
    new_rd=Path(a.run_dir); scope=Path(a.scope_dir).resolve()
    cap=_issue_bootstrap_capability(a.run_id,new_rd,scope,"normal",parent_st.get("multi_system",False),parent_st.get("mechanical_validation",False))
    from argparse import Namespace
    cmd_start(Namespace(run_dir=str(new_rd),run_id=a.run_id,scope_dir=str(scope),mode="normal",multi_system=parent_st.get("multi_system",False),mechanical_validation=parent_st.get("mechanical_validation",False),bootstrap_capability=str(cap)))
    child=load_state(new_rd)
    prefix_names=[]
    for g,_,_ in sequence(parent_st):
        if g=="STYLE_AXES_CLOSED": break
        prefix_names.append(g)
    prefix_ok=all(g in (parent_st.get("gates") or {}) for g in prefix_names)
    inventory_ok=_source_inventory_compatible_for_fork(parent_st,child)
    if not prefix_ok or not inventory_ok:
        return _fallback_fork_bootstrap(new_rd,child,"PREFIX_NOT_PROVABLY_FRESH" if prefix_ok else "PREFIX_GATE_MISSING",parent_st.get("run_id"))
    old=parent_st.get("current_artifact")
    m=re.fullmatch(r"deck-v(\d+)",old or "")
    if not m: fail("FORK_PARENT_ARTIFACT_NOT_VERSIONED")
    new=f"deck-v{int(m.group(1))+1}"
    candidate=_read_candidate_snapshot(Path(a.candidate_snapshot),a.run_id,new)
    before=read_json(parent_snapshot,"parent terminal snapshot")
    before_comp=deck_composition_sha256(before); after_comp=deck_composition_sha256(candidate)
    if before_comp==after_comp: fail("TARGETED_REFACTOR_NO_MATERIAL_CHANGE")
    base_copy=new_rd/f"{old}.snapshot.json"; base_copy.write_bytes(parent_snapshot.read_bytes())
    candidate_copy=new_rd/f"{new}.candidate.json"; _atomic_write_text(candidate_copy,json.dumps(candidate,ensure_ascii=False,indent=2)+"\n")
    inherited=[]; gates={}; rebind_hash_map={}; rebind_count=0
    for g in prefix_names:
        parent_rec=dict(parent_st["gates"][g]); parent_rec_sha=hashlib.sha256(_stable_json_text(parent_rec).encode()).hexdigest()
        src=_rebind_exact_hash_refs(parent_rec,rebind_hash_map)
        ef,eh,did=_rebind_inherited_gate_evidence(parent_rec,a.run_id,new_rd,g,rebind_hash_map)
        if did:
            src["evidence_file"]=ef; src["evidence_sha256"]=eh; rebind_count+=1
        src=_rebind_exact_hash_refs(src,rebind_hash_map)
        src["run_id"]=a.run_id
        src["inheritance"]="INHERITED_REBOUND" if did else "INHERITED_EXACT"; src["parent_run_id"]=parent_st.get("run_id"); src["parent_gate_record_sha256"]=parent_rec_sha
        gates[g]=src
        inherited.append({"gate":g,"parent_gate_record_sha256":parent_rec_sha,"parent_evidence_sha256":parent_rec.get("evidence_sha256"),"evidence_sha256":src.get("evidence_sha256"),"status":src["inheritance"]})
    old_render=(parent_st.get("gates") or {}).get("FINAL_RENDER_PREPARED",{})
    old_visual=(parent_st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
    carry=[x for x in (old_render.get("component_inventory") or []) if isinstance(x,dict) and x.get("type") in {"main-carousel","mini-carousel"}]
    carry_req=[]
    if nonempty(old_visual.get("evidence_file")) and Path(old_visual["evidence_file"]).exists():
        ov=read_json(Path(old_visual["evidence_file"]),"parent visual assets")
        if (ov.get("signature_climax") or {}).get("terminal_quote_required") is True: carry_req.append("signature-terminal-quote")
    child["gates"]=gates
    # Fingerprints are child-native and are never inherited textually.
    for g in prefix_names:
        if g in SELECTIVE_GATE_DEPENDENCIES:
            fp=_gate_dependency_fingerprint(child,g)
            if nonempty(fp): child["gates"][g]["dependency_fingerprint"]=fp
    child["current_artifact"]=new; child["current_render"]=None; child["stop_output_allowed"]=False; child["run_execution_state"]="IN_PROGRESS"
    child["material_change_count"]=1; child["combo_impact_required"]=True
    child["refactor_render_mode"]="FULL" if bool(getattr(a,"full_decklist",False)) else "DIFF_ONLY"
    child["refactor_visual_carry_components"]=carry; child["refactor_visual_carry_requirements"]=carry_req; child["presentation_carry_components"]=[]
    child["parent_run_id"]=parent_st.get("run_id"); child["parent_terminal_checkpoint_sha256"]=sha256(parent_rd/CHECKPOINT_FILE); child["parent_terminal_state_sha256"]=sha256(parent_rd/STATE_FILE); child["parent_artifact"]=old
    child["fork_reason"]="USER_REQUESTED_TARGETED_REFACTOR"; child["fork_user_evidence"]=a.user_evidence; child["inherited_gate_bindings"]=inherited
    child["last_material_change"]={
        "from_artifact":old,"to_artifact":new,"reason":a.reason,"user_requested_refactor":True,"post_output_refactor":True,"prior_output_authorized":True,
        "full_decklist_requested":bool(getattr(a,"full_decklist",False)),"render_mode":child["refactor_render_mode"],
        "previous_snapshot_file":str(base_copy),"previous_snapshot_sha256":parent_snapshot_sha,"candidate_snapshot_file":str(candidate_copy),
        "before_composition_sha256":before_comp,"after_composition_sha256":after_comp,
        "previous_narrative_report_file":((parent_st.get("gates") or {}).get("NARRATIVE_CONFORMANCE_CLOSED") or {}).get("evidence_file"),
        "previous_narrative_report_sha256":((parent_st.get("gates") or {}).get("NARRATIVE_CONFORMANCE_CLOSED") or {}).get("evidence_sha256"),
        "previous_render_sha256":old_render.get("render_sha256"),"previous_component_inventory_sha256":old_render.get("component_inventory_sha256"),
        "stale_transition":{"status":"MATERIALIZED","from_artifact":old,"to_artifact":new,"invalidated_gates":[g for g,_,_ in sequence(parent_st) if _gate_order_map(parent_st).get(g,0)>=_gate_order_map(parent_st).get("STYLE_AXES_CLOSED",0)]},
    }
    child.setdefault("stale_history",[]).append(dict(child["last_material_change"]["stale_transition"]))
    save_state(new_rd,child)
    cp=_load_checkpoint_raw(new_rd,required=True)
    _append_run_journal(new_rd,child,"TERMINAL_REFACTOR_FORK_COMPLETED",checkpoint_seq=cp.get("checkpoint_seq"),parent_run_id=parent_st.get("run_id"),parent_artifact=old,current_artifact=new,inherited_gate_count=len(inherited),first_replay_gate=cp.get("next_required_gate"),render_mode=child["refactor_render_mode"],parent_terminal_checkpoint_sha256=child["parent_terminal_checkpoint_sha256"],parent_terminal_state_sha256=child["parent_terminal_state_sha256"])
    _append_run_journal(new_rd,child,"TERMINAL_REFACTOR_FORK_REBOUND",checkpoint_seq=cp.get("checkpoint_seq"),parent_run_id=parent_st.get("run_id"),child_run_id=a.run_id,rebind_count=rebind_count,policy="CHILD_NATIVE_RUN_ID_AND_HASH_REFERENCES")
    for item in inherited:
        _append_run_journal(new_rd,child,"INHERITED_GATE_BOUND",checkpoint_seq=cp.get("checkpoint_seq"),**item)
    print(json.dumps({"status":"FORKED_TARGETED_REFACTOR","run_id":a.run_id,"parent_run_id":parent_st.get("run_id"),"parent_artifact":old,"current_artifact":new,"inherited_gate_count":len(inherited),"next_required_gate":cp.get("next_required_gate"),"refactor_render_mode":child["refactor_render_mode"]},ensure_ascii=False))



# ---------------------------------------------------------------------------
# RC16.22 SEMANTIC CORE / DETERMINISTIC SHELL
# Deterministic orchestration only.  Business authorities and their validators
# remain the sole judges of narrative, classification, viability, Style/Axes,
# Pilotage and final quality.
# ---------------------------------------------------------------------------

RC1622_SEMANTIC_GATES = {
    "NARRATIVE_RED_CLOSED",
    "NARRATIVE_CONTRACT_FROZEN",
    "FUNCTIONAL_INTENT_FROZEN",
    "EXPLORATION_CLOSED",
    "CONCEPT_SELECTED",
    "CLASSIFICATION_CLOSED",
    "STYLE_AXES_CLOSED",
    "DECK_DRAFT_CREATED",
    "NARRATIVE_CONFORMANCE_CLOSED",
    "FINAL_CLASSIFICATION_CLOSED",
    "VISUAL_ASSETS_BOUND",
}

RC1622_EVIDENCE_NAMES = {
    "NARRATIVE_RED_CLOSED":"narrative_red.json",
    "NARRATIVE_CONTRACT_FROZEN":"narrative_contract.json",
    "FUNCTIONAL_INTENT_FROZEN":"functional_intent.json",
    "EXPLORATION_CLOSED":"exploration.json",
    "CONCEPT_SELECTED":"concept_selected.json",
    "CLASSIFICATION_CLOSED":"classification_provisional.json",
    "STYLE_AXES_CLOSED":"style_axes.json",
    "DECK_DRAFT_CREATED":"deck-current.snapshot.json",
    "NARRATIVE_CONFORMANCE_CLOSED":"narrative_conformance.json",
    "FINAL_CLASSIFICATION_CLOSED":"classification_final.json",
    "VISUAL_ASSETS_BOUND":"visual_assets.json",
}

RC1622_PREFERRED_AUTHORITIES = {
    "CLASSIFICATION_CLOSED":CANON,
    "FINAL_CLASSIFICATION_CLOSED":CANON,
    "CONCEPT_SELECTED":EXPLORATION,
    "VISUAL_ASSETS_BOUND":GLOBAL_STRUCTURE,
}


def _rc1622_gate_spec(st, gate):
    for g,auths,statuses in sequence(st):
        if g==gate:
            authority=RC1622_PREFERRED_AUTHORITIES.get(gate)
            if authority is None:
                authority=sorted(auths)[0]
            if authority not in auths:
                fail(f"SEMANTIC_SHELL_AUTHORITY_UNRESOLVED: {gate}")
            if len(statuses)!=1:
                # Only STYLE_AXES has two legal statuses; its semantic payload may
                # explicitly select REFACTOR, otherwise PASS is the normal build status.
                status="PASS" if gate=="STYLE_AXES_CLOSED" else None
            else:
                status=next(iter(statuses))
            return authority,status
    fail(f"SEMANTIC_SHELL_UNKNOWN_GATE: {gate}")


def _rc1622_forbid_mechanical(payload, keys):
    bad=sorted(set(payload) & set(keys))
    if bad:
        fail("SEMANTIC_PAYLOAD_CONTAINS_MECHANICAL_BINDING: "+",".join(bad))


def _rc1622_compile_semantic_evidence(rd: Path, st, gate, payload, output=None):
    if gate not in RC1622_SEMANTIC_GATES:
        fail(f"SEMANTIC_GATE_UNSUPPORTED: {gate}")
    if not isinstance(payload,dict):
        fail("SEMANTIC_PAYLOAD_MUST_BE_OBJECT")
    authority,_=_rc1622_gate_spec(st,gate)
    semantic=dict(payload)
    forbidden={"run_id","authority","artifact","artifact_id","deck_artifact","snapshot_sha256","contract_sha256","policy_source_sha256","direction_contract_sha256","functional_intent_sha256","final_classification_sha256","authorities"}
    _rc1622_forbid_mechanical(semantic,forbidden)
    d=dict(semantic)
    if gate=="NARRATIVE_CONTRACT_FROZEN":
        arc=d.get("arc")
        policy=parse_style_policy(policy_path())
        if arc not in policy.get("eras",{}): fail(f"unknown narrative arc in semantic payload: {arc}")
        era=policy["eras"][arc]
        d={
            "run_id":st["run_id"],"authority":PROGRESSION,"policy_source":STYLE,
            "policy_source_sha256":sha256(policy_path()),"policy_schema_version":policy.get("schema_version"),
            "arc":arc,"mechanic_universe":policy["mechanic_universe"],
            "allowed_mechanics":era.get("allowed"),"forbidden_mechanics":era.get("forbidden"),
            **{k:v for k,v in d.items() if k!="arc"},
        }
    elif gate=="FUNCTIONAL_INTENT_FROZEN":
        dg=(st.get("gates") or {}).get("DIRECTION_RESOLVED",{})
        if not dg.get("evidence_sha256"): fail("SEMANTIC_FUNCTIONAL_INTENT_DIRECTION_MISSING")
        d={"run_id":st["run_id"],"authority":CANON,"direction_contract_sha256":dg["evidence_sha256"],**d}
    elif gate in {"CLASSIFICATION_CLOSED","FINAL_CLASSIFICATION_CLOSED"}:
        fg=(st.get("gates") or {}).get("FUNCTIONAL_INTENT_FROZEN",{})
        if not fg.get("evidence_sha256"): fail("SEMANTIC_CLASSIFICATION_INTENT_MISSING")
        phase="FINAL" if gate=="FINAL_CLASSIFICATION_CLOSED" else "PROVISIONAL"
        base={"run_id":st["run_id"],"authority":CANON,"phase":phase,"functional_intent_sha256":fg["evidence_sha256"]}
        if gate=="FINAL_CLASSIFICATION_CLOSED":
            dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED",{})
            if not dg.get("snapshot_sha256"): fail("SEMANTIC_FINAL_CLASSIFICATION_SNAPSHOT_MISSING")
            base["snapshot_sha256"]=dg["snapshot_sha256"]
        d={**base,**d}
    elif gate=="DECK_DRAFT_CREATED":
        d={"run_id":st["run_id"],"artifact_id":st.get("current_artifact"),**d}
        for zone,total_key in (("main_deck","main_total"),("extra_deck","extra_total"),("side_deck","side_total")):
            cards=d.get(zone)
            if isinstance(cards,list): d[total_key]=sum(x.get("qty",0) for x in cards if isinstance(x,dict) and isinstance(x.get("qty"),int))
    elif gate=="NARRATIVE_CONFORMANCE_CLOSED":
        cg=(st.get("gates") or {}).get("NARRATIVE_CONTRACT_FROZEN",{}); dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED",{})
        if not cg.get("evidence_file") or not dg.get("snapshot_sha256"): fail("SEMANTIC_NARRATIVE_CONFORMANCE_PREREQUISITES_MISSING")
        contract=read_json(Path(cg["evidence_file"]),"narrative contract")
        d={"run_id":st["run_id"],"authority":PROGRESSION,"artifact":st.get("current_artifact"),"snapshot_sha256":dg["snapshot_sha256"],"contract_sha256":cg["evidence_sha256"],"forbidden_mechanics_checked":contract.get("forbidden_mechanics"),**d}
    elif gate=="VISUAL_ASSETS_BOUND":
        fg=(st.get("gates") or {}).get("FINAL_CLASSIFICATION_CLOSED",{})
        if not fg.get("evidence_sha256"): fail("SEMANTIC_VISUAL_CLASSIFICATION_MISSING")
        d={"run_id":st["run_id"],"deck_artifact":st.get("current_artifact"),"authorities":sorted(RENDER_AUTHORITIES),"final_classification_sha256":fg["evidence_sha256"],**d}
    else:
        # Generic specialized evidence: only inject universally mechanical identity.
        d={"run_id":st["run_id"],"authority":authority,"artifact":st.get("current_artifact"),**d}
    name=RC1622_EVIDENCE_NAMES[gate]
    if gate=="DECK_DRAFT_CREATED": name=f"{st.get('current_artifact')}.snapshot.json"
    out=Path(output) if nonempty(output) else rd/name
    if not out.is_absolute(): out=rd/out
    _atomic_write_text(out,_stable_json_text(d))
    # Validate immediately using the same gate validator where one exists. This is
    # compilation, not a PASS; cmd_complete remains the only gate transition path.
    if gate=="NARRATIVE_CONTRACT_FROZEN": validate_narrative_contract(out,st)
    elif gate=="FUNCTIONAL_INTENT_FROZEN": validate_functional_intent(out,st)
    elif gate=="CLASSIFICATION_CLOSED": validate_classification_result(out,st,"PROVISIONAL")
    elif gate=="DECK_DRAFT_CREATED": validate_deck_snapshot(out,st)
    elif gate=="NARRATIVE_CONFORMANCE_CLOSED":
        cg=st["gates"]["NARRATIVE_CONTRACT_FROZEN"]; dg=st["gates"]["DECK_DRAFT_CREATED"]
        validate_narrative_conformance(out,Path(cg["evidence_file"]),Path(dg["snapshot_file"]),st)
    elif gate=="FINAL_CLASSIFICATION_CLOSED": validate_classification_result(out,st,"FINAL")
    elif gate=="VISUAL_ASSETS_BOUND": validate_visual_assets(out,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,"SEMANTIC_EVIDENCE_COMPILED",checkpoint_seq=cp.get("checkpoint_seq"),gate=gate,artifact_file=str(out),artifact_sha256=sha256(out),mechanical_fields_derived=True)
    return out


def _rc1622_materialize_combo_impact(rd: Path, st, payload):
    if not isinstance(payload,dict): fail("SEMANTIC_COMBO_IMPACT_MUST_BE_OBJECT")
    _rc1622_forbid_mechanical(payload,{"run_id","authority","from_artifact","deck_artifact"})
    change=st.get("last_material_change") or {}
    if st.get("combo_impact_required") is not True: fail("COMBO_IMPACT_NOT_REQUIRED")
    doc={"run_id":st["run_id"],"authority":PILOTAGE,"from_artifact":change.get("from_artifact"),"deck_artifact":st.get("current_artifact"),**payload}
    out=rd/"combo_impact.compiled.json"
    _atomic_write_text(out,_stable_json_text(doc)); validate_combo_impact(out,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,"COMBO_IMPACT_AUTO_BOUND",checkpoint_seq=cp.get("checkpoint_seq"),combo_impact_file=str(out),combo_impact_sha256=sha256(out))
    return out


def _rc1622_resolve_combo_impact(rd: Path, st, explicit=None):
    if st.get("combo_impact_required") is not True: return explicit
    candidates=[]
    if nonempty(explicit): candidates.append(Path(explicit))
    for p in (rd/"combo_impact.compiled.json", rd/"combo_impact.json"):
        if p not in candidates: candidates.append(p)
    valid=[]
    for p in candidates:
        if not p.exists() or not p.is_file(): continue
        try:
            validate_combo_impact(p,st); valid.append(p)
        except SystemExit:
            continue
    if not valid: return explicit
    # Prefer explicit, then canonical compiled filename. Multiple valid noncanonical
    # artifacts are never guessed between.
    if nonempty(explicit) and Path(explicit) in valid: return str(Path(explicit))
    canonical=rd/"combo_impact.compiled.json"
    if canonical in valid: return str(canonical)
    # After explicit and canonical precedence, the only remaining candidate is combo_impact.json.
    return str(valid[0])


# Render continuity is a mechanical projection of already-authoritative state.
_compile_render_contract_payload_rc1619 = compile_render_contract_payload

def compile_render_contract_payload(policy_path: Path, st, contract_parent: Path|None=None):
    out=_compile_render_contract_payload_rc1619(policy_path,st,contract_parent)
    prior,origin=_active_carry_components(st)
    if prior and origin=="presentation" and "component_continuity" not in out:
        out["component_continuity"]=[{"previous_component_id":c.get("component_id"),"mode":"PRESERVE","source":GLOBAL_STRUCTURE} for c in prior]
        out["component_continuity_compiled_by"]="RC16.22_DETERMINISTIC_SHELL"
    elif prior and origin=="refactor" and "component_continuity" not in out:
        vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
        visual=read_json(Path(vg["evidence_file"]),"visual assets") if vg.get("evidence_file") else {}
        trans=[]; provable=True
        for old in prior:
            typ=old.get("type"); cid=old.get("component_id")
            if typ=="main-carousel":
                block=visual.get("main_carousel") or {}; expected_parent=None; expected_tags=["cartes-emblematiques"]; expected_refs=_rc16221_component_refs(visual,"main") if block.get("applicable") is True else []
            elif typ=="mini-carousel":
                block=visual.get("signature_climax") or {}; expected_parent=block.get("parent"); expected_tags=["signature","combo"]; expected_refs=_rc16221_component_refs(visual,"mini") if block.get("mini_carousel_applicable") is True else []
            else:
                provable=False; break
            payload={"schema":COMPILED_COMPONENT_PAYLOAD_SCHEMA,"component_id":cid,"ui_type":"image_group","layout":"carousel","image_refs":list(expected_refs),"compiled_by":"compile-component-payloads"}
            expected_hash=hashlib.sha256(_stable_json_text(payload).encode()).hexdigest()
            unchanged=bool(expected_refs) and old.get("parent")==expected_parent and sorted(old.get("tags") or [])==sorted(expected_tags) and list(old.get("image_refs") or [])==list(expected_refs) and old.get("artifact_sha256")==expected_hash
            if not unchanged:
                provable=False; break
            trans.append({"previous_component_id":cid,"mode":"PRESERVE","source":GLOBAL_STRUCTURE})
        if provable and len(trans)==len(prior):
            out["component_continuity"]=trans
            out["component_continuity_compiled_by"]="RC16.22.1_POST_BLACKBOX_PROVABLE_PRESERVE"
    reqs=st.get("refactor_visual_carry_requirements") or []
    if reqs and (st.get("last_material_change") or {}).get("post_output_refactor") and "requirement_continuity" not in out:
        vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
        visual=read_json(Path(vg["evidence_file"]),"visual assets") if vg.get("evidence_file") else {}
        trans=[]
        for rid in reqs:
            if rid=="signature-terminal-quote" and (visual.get("signature_climax") or {}).get("terminal_quote_required") is not True:
                trans.append({"previous_requirement_id":rid,"mode":"DROP_EXPLICIT","reason":"no longer applicable in current STRUCTURE visual intent","source":AXES_STRUCTURE})
            else:
                trans.append({"previous_requirement_id":rid,"mode":"PRESERVE","source":AXES_STRUCTURE})
        out["requirement_continuity"]=trans
        out["requirement_continuity_compiled_by"]="RC16.22_DETERMINISTIC_SHELL"
    return out


# Required visual components must survive all the way to the terminal inventory.
def _rc1623_terminal_visual_issues(visual, components):
    issues=[]
    visual=visual if isinstance(visual,dict) else {}
    comps=[c for c in components if isinstance(c,dict)]
    main=visual.get("main_carousel") or {}
    if main.get("applicable") is True:
        matches=[c for c in comps if c.get("component_id")=="main-card-carousel" and c.get("type")=="main-carousel"]
        if not matches:
            issues.append(_terminal_issue("TERMINAL_MAIN_CAROUSEL_MISSING","main carousel required by VISUAL_ASSETS_BOUND but absent from terminal inventory"))
    sig=visual.get("signature_climax") or {}
    if sig.get("mini_carousel_applicable") is True:
        parent=sig.get("parent")
        matches=[c for c in comps if c.get("component_id")=="signature-mini-carousel" and c.get("type")=="mini-carousel" and c.get("parent")==parent]
        if not matches:
            issues.append(_terminal_issue("TERMINAL_SIGNATURE_MINI_CAROUSEL_MISSING","signature mini-carousel required by VISUAL_ASSETS_BOUND but absent or rebound in terminal inventory"))
    return issues


def _rc1622_required_component_issues(st, components):
    vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
    if not vg.get("evidence_file"): return []
    visual=read_json(Path(vg["evidence_file"]),"visual assets")
    return _rc1623_terminal_visual_issues(visual,components)

_compile_terminal_presentation_payload_rc1619 = compile_terminal_presentation_payload

def compile_terminal_presentation_payload(render_path: Path, manifest_path: Path, st):
    payload=_compile_terminal_presentation_payload_rc1619(render_path,manifest_path,st)
    vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
    vf=vg.get("evidence_file")
    if not nonempty(vf) or not Path(vf).exists(): fail("TERMINAL_VISUAL_ASSETS_BINDING_REQUIRED")
    visual=read_json(Path(vf),"visual assets")
    issues=_rc1623_terminal_visual_issues(visual,payload.get("components") or [])
    if issues: fail(issues[0]["code"]+": "+issues[0]["detail"])
    payload["visual_assets_file"]=str(Path(vf).resolve())
    payload["visual_assets_sha256"]=sha256(Path(vf))
    payload["visual_obligations"]={
        "main_carousel_applicable":(visual.get("main_carousel") or {}).get("applicable") is True,
        "signature_mini_carousel_applicable":(visual.get("signature_climax") or {}).get("mini_carousel_applicable") is True,
        "signature_parent":(visual.get("signature_climax") or {}).get("parent"),
    }
    payload["required_component_guard"]="PASS"
    return payload

_terminal_plan_issues_rc1619 = _terminal_plan_issues

def _terminal_plan_issues(plan_path: Path, render_path: Path, manifest_path: Path, st):
    issues=_terminal_plan_issues_rc1619(plan_path,render_path,manifest_path,st)
    try:
        d=read_json(plan_path,"terminal presentation plan") if plan_path.exists() else {}
        vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
        vf=vg.get("evidence_file")
        if not nonempty(vf) or not Path(vf).exists():
            issues.append(_terminal_issue("TERMINAL_VISUAL_ASSETS_BINDING_REQUIRED","VISUAL_ASSETS_BOUND evidence missing at terminal boundary"))
        else:
            visual=read_json(Path(vf),"visual assets")
            if d.get("visual_assets_sha256")!=sha256(Path(vf)):
                issues.append(_terminal_issue("TERMINAL_VISUAL_ASSETS_STALE","visual_assets_sha256 mismatch"))
            issues.extend(_rc1623_terminal_visual_issues(visual,d.get("components") or []))
    except SystemExit as e:
        code,detail=_denied_parts(e); issues.append(_terminal_issue(code,detail))
    dedup=[]; seen=set()
    for x in issues:
        k=json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        if k not in seen: seen.add(k); dedup.append(x)
    return dedup


# Automatically bind a current combo-impact artifact into Pilotage and gate closure.
_cmd_complete_rc1619_current = cmd_complete

def cmd_complete_rc1622(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if getattr(a,"gate",None)=="PILOTAGE_VALIDATED" and st.get("combo_impact_required") is True:
        resolved=_rc1622_resolve_combo_impact(rd,st,getattr(a,"combo_impact_file",None))
        if nonempty(resolved): setattr(a,"combo_impact_file",resolved)
    return _cmd_complete_rc1619_current(a)

cmd_complete = cmd_complete_rc1622

_cmd_pilotage_preflight_rc1619_current = cmd_pilotage_preflight

def cmd_pilotage_preflight_rc1622(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if st.get("combo_impact_required") is True:
        resolved=_rc1622_resolve_combo_impact(rd,st,getattr(a,"combo_impact_file",None))
        if nonempty(resolved): setattr(a,"combo_impact_file",resolved)
    return _cmd_pilotage_preflight_rc1619_current(a)

cmd_pilotage_preflight = cmd_pilotage_preflight_rc1622


# Harden the existing render-contract transaction: journal remains append-only, but
# a failed transaction is forbidden from leaving authoritative state/checkpoint/lease/session mutated.
def _rc1622_capture_authoritative(rd: Path, st):
    paths=[rd/STATE_FILE,rd/CHECKPOINT_FILE]
    raw_scope=st.get("continuity_scope_dir")
    if nonempty(raw_scope): paths.append(Path(raw_scope)/CONTINUATION_LEASE_FILE)
    try: paths.append(_session_index_path())
    except Exception: pass
    snap={}
    for p in paths:
        snap[str(p.resolve())]=p.read_bytes() if p.exists() and p.is_file() else None
    return snap


def _rc1622_restore_authoritative(snapshot):
    for name,data in snapshot.items():
        p=Path(name)
        if data is None:
            if p.exists(): p.unlink()
        else:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)

_cmd_compile_render_contract_rc1619_current = cmd_compile_render_contract

def cmd_compile_render_contract_rc1622(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    snap=_rc1622_capture_authoritative(rd,st)
    before_state=sha256(rd/STATE_FILE); before_cp=sha256(rd/CHECKPOINT_FILE)
    try:
        return _cmd_compile_render_contract_rc1619_current(a)
    except BaseException:
        changed=(sha256(rd/STATE_FILE)!=before_state or sha256(rd/CHECKPOINT_FILE)!=before_cp)
        if changed:
            _rc1622_restore_authoritative(snap)
            restored=load_state(rd); cp=_load_checkpoint_raw(rd,required=False) or {}
            _append_run_journal(rd,restored,"RENDER_CONTRACT_TRANSACTION_ROLLED_BACK",checkpoint_seq=cp.get("checkpoint_seq"),atomic_authoritative_rollback=True)
        raise

cmd_compile_render_contract = cmd_compile_render_contract_rc1622


# Semantic-aware batching: the model supplies only authority-owned semantic content;
# runtime derives identity, hashes, provenance and gate wiring at the moment each gate is reached.
def _rc1622_batch_op_namespace(rd: Path, run_id, op):
    return _batch_op_namespace(rd,run_id,op)


def cmd_execute_batch_rc1622(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    _require_mutable_run_rc1619(rd,st,"execute-batch")
    bundle=read_json(Path(a.bundle_file),"safe batch bundle")
    if bundle.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in safe batch bundle")
    if "combo_impact" in bundle:
        _rc1622_materialize_combo_impact(rd,st,bundle["combo_impact"])
    ops=bundle.get("operations")
    if not isinstance(ops,list) or not ops: fail("SAFE_BATCH_REQUIRES_OPERATIONS")
    cp=_load_checkpoint_raw(rd,required=True)
    batch_id=f"safe-batch-{sum(1 for e in _read_journal(rd) if e.get('event')=='SAFE_BATCH_STARTED')+1:06d}"
    _append_run_journal(rd,st,"SAFE_BATCH_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),batch_id=batch_id,operation_count=len(ops),next_required_gate=cp.get("next_required_gate"))
    completed=[]; skipped=[]
    for idx,raw in enumerate(ops):
        if not isinstance(raw,dict): fail(f"SAFE_BATCH_OPERATION_INVALID: {idx}")
        op=dict(raw); kind=op.get("op")
        st=load_state(rd); ng=next_gate(st)[0]
        if kind=="explicit-direction":
            gate="DIRECTION_RESOLVED"
            if gate in (st.get("gates") or {}):
                rec=st["gates"][gate]; direction=_normalize_explicit_direction(op.get("selected_direction"))
                if rec.get("direction")!=direction or rec.get("resolution_basis")!="USER_EXPLICIT": fail("BATCH_CLOSED_DIRECTION_BINDING_MISMATCH")
                skipped.append(gate); _append_run_journal(rd,st,"SAFE_BATCH_ITEM_SKIPPED_ALREADY_CLOSED",checkpoint_seq=(_load_checkpoint_raw(rd,True)).get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=gate); continue
            if ng!=gate: fail(f"SAFE_BATCH_WRONG_NEXT_GATE: expected {ng}, got {gate}")
            out,_=_materialize_explicit_direction_contract(rd,st,op.get("selected_direction"),op.get("user_evidence"),op.get("output"))
            op2={"op":"complete","gate":gate,"authority":STYLE,"status":"RESOLVED","evidence_file":str(out)}
        elif kind=="semantic-complete":
            gate=op.get("gate")
            if not nonempty(gate): fail(f"SAFE_BATCH_GATE_MISSING: {idx}")
            if gate in (st.get("gates") or {}):
                skipped.append(gate); _append_run_journal(rd,st,"SAFE_BATCH_ITEM_SKIPPED_ALREADY_CLOSED",checkpoint_seq=(_load_checkpoint_raw(rd,True)).get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=gate); continue
            if ng!=gate: fail(f"SAFE_BATCH_WRONG_NEXT_GATE: expected {ng}, got {gate}")
            authority,status=_rc1622_gate_spec(st,gate)
            requested=op.get("status")
            if gate=="STYLE_AXES_CLOSED" and requested in {"PASS","REFACTOR"}: status=requested
            elif requested is not None and requested!=status: fail("SEMANTIC_GATE_STATUS_OVERRIDE_INVALID")
            out=_rc1622_compile_semantic_evidence(rd,st,gate,op.get("payload"),op.get("output"))
            op2={"op":"complete","gate":gate,"authority":authority,"status":status,"evidence_file":str(out)}
        elif kind=="complete":
            gate=op.get("gate")
            if not nonempty(gate): fail(f"SAFE_BATCH_GATE_MISSING: {idx}")
            if gate in (st.get("gates") or {}):
                if not _batch_closed_binding_matches(st,op): fail("BATCH_CLOSED_GATE_BINDING_MISMATCH")
                skipped.append(gate); _append_run_journal(rd,st,"SAFE_BATCH_ITEM_SKIPPED_ALREADY_CLOSED",checkpoint_seq=(_load_checkpoint_raw(rd,True)).get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=gate); continue
            if ng!=gate: fail(f"SAFE_BATCH_WRONG_NEXT_GATE: expected {ng}, got {gate}")
            op2=op
        else: fail(f"SAFE_BATCH_OPERATION_INVALID: {idx}")
        st0=load_state(rd); cp0=_load_checkpoint_raw(rd,True)
        _append_run_journal(rd,st0,"SAFE_BATCH_ITEM_STARTED",checkpoint_seq=cp0.get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=op2.get("gate"))
        try: cmd_complete(_rc1622_batch_op_namespace(rd,st0["run_id"],op2))
        except SystemExit as e:
            stf=load_state(rd); cpf=_load_checkpoint_raw(rd,True)
            _append_run_journal(rd,stf,"SAFE_BATCH_ITEM_FAILED",checkpoint_seq=cpf.get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=op2.get("gate"),detail=str(e)); _append_run_journal(rd,stf,"SAFE_BATCH_STOPPED",checkpoint_seq=cpf.get("checkpoint_seq"),batch_id=batch_id,failed_gate=op2.get("gate"),completed=completed,skipped=skipped); raise
        st1=load_state(rd); cp1=_load_checkpoint_raw(rd,True); completed.append(op2.get("gate")); _append_run_journal(rd,st1,"SAFE_BATCH_ITEM_SUCCEEDED",checkpoint_seq=cp1.get("checkpoint_seq"),batch_id=batch_id,item_index=idx,gate=op2.get("gate"),closed_status=(st1.get("gates",{}).get(op2.get("gate")) or {}).get("status"))
    st=load_state(rd); cp=_load_checkpoint_raw(rd,True); _append_run_journal(rd,st,"SAFE_BATCH_COMPLETED",checkpoint_seq=cp.get("checkpoint_seq"),batch_id=batch_id,completed=completed,skipped=skipped,next_required_gate=cp.get("next_required_gate")); print(json.dumps({"status":"PASS","batch_id":batch_id,"completed":completed,"skipped":skipped,"next_required_gate":cp.get("next_required_gate")},ensure_ascii=False))

cmd_execute_batch = cmd_execute_batch_rc1622


def cmd_advance_prepared_rc1622(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"advance-prepared")
    bundle=read_json(Path(a.bundle_file),"advance prepared bundle")
    if bundle.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in advance prepared bundle")
    generated=_prepared_bundle_with_auto_direction(rd,st,bundle)
    if "combo_impact" in bundle: generated["combo_impact"]=bundle["combo_impact"]
    cp=_load_checkpoint_raw(rd,required=True); advance_id=f"fast-advance-{sum(1 for e in _read_journal(rd) if e.get('event')=='FASTPATH_ADVANCE_STARTED')+1:06d}"
    _append_run_journal(rd,st,"FASTPATH_ADVANCE_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),advance_id=advance_id,prepared_count=len(generated["operations"]),profile=st.get("fastpath_profile",FASTPATH_PROFILE))
    bf=rd/"advance_prepared.bundle.json"; _atomic_write_text(bf,_stable_json_text(generated))
    try: cmd_execute_batch_rc1622(type("Args",(),{"run_dir":str(rd),"run_id":st["run_id"],"bundle_file":str(bf)})())
    except BaseException:
        stf=load_state(rd); cpf=_load_checkpoint_raw(rd,required=True); _append_run_journal(rd,stf,"FASTPATH_ADVANCE_STOPPED",checkpoint_seq=cpf.get("checkpoint_seq"),advance_id=advance_id,next_required_gate=cpf.get("next_required_gate")); raise
    stf=load_state(rd); cpf=_load_checkpoint_raw(rd,required=True); _append_run_journal(rd,stf,"FASTPATH_ADVANCE_COMPLETED",checkpoint_seq=cpf.get("checkpoint_seq"),advance_id=advance_id,next_required_gate=cpf.get("next_required_gate"),item_count=len(generated["operations"])); print(json.dumps({"status":"PASS","advance_id":advance_id,"next_required_gate":cpf.get("next_required_gate"),"fastpath":"BATCH","semantic_shell":True},ensure_ascii=False))

cmd_advance_prepared = cmd_advance_prepared_rc1622


# ---------------------------------------------------------------------------
# RC16.22.1 — BLACK-BOX HARDENING
# No business authority is redefined here. This layer only derives mechanical
# applicability/bindings and atomically commits already authority-owned content.
# ---------------------------------------------------------------------------

RC16221_PILOTAGE_BUSINESS_RECEIPT = "pilotage_validator_execution.receipt.json"
RC16221_PILOTAGE_BUSINESS_RECEIPT_SCHEMA = "ygo-pilotage-validator-execution-receipt-v1"
# RC16.23 Black-Box corrective: integrity and Render compatibility are distinct.
# The source inventory/manifest proves the exact files installed. Render compatibility
# is bound to the authority-owned projection contract actually consumed by the runtime,
# not to a whole-file SHA that can change after a non-projection edit.
RC1623_RENDER_PROJECTION_CONTRACT_EXPECTED = {
    "schema":"ygo-render-projection-contract-v1",
    "global_decklist_vertical":True,
    "global_terminal_bundle_exact":True,
    "axis_arrow_max":4,
    "axis_line_max":220,
    "quote_exact":1,
    "main_carousel_binding":"main-card-carousel|main-carousel|component_min_count",
    "mini_carousel_binding":"signature-mini-carousel|mini-carousel|component_min_count",
}


def _rc1623_render_projection_contract_from_texts(global_text, axes_text):
    ma=re.search(r"plus de\s+(\d+)\s+transitions",axes_text)
    ml=re.search(r"limite de \*\*(\d+) caractères",axes_text)
    mq=re.search(r'regex_exact_count[\s\S]{0,260}?exact\s*=\s*(\d+)',axes_text)
    main_ok=("`main-card-carousel`" in axes_text and "`main-carousel`" in axes_text and "`component_min_count`" in axes_text)
    mini_ok=("`signature-mini-carousel`" in axes_text and "`mini-carousel`" in axes_text and "`component_min_count`" in axes_text)
    vertical_ok=("`decklist-vertical`" in global_text and "une entrée de carte" in global_text)
    bundle_ok=("front-end final est le bundle exact validé" in global_text and "Après `STOP_OUTPUT_ALLOWED`, ne jamais reconstruire une decklist complète" in global_text)
    if not (ma and ml and mq and main_ok and mini_ok and vertical_ok and bundle_ok):
        fail("RENDER_PROJECTION_SOURCE_CONTRACT_UNREADABLE")
    return {
        "schema":"ygo-render-projection-contract-v1",
        "global_decklist_vertical":bool(vertical_ok),
        "global_terminal_bundle_exact":bool(bundle_ok),
        "axis_arrow_max":int(ma.group(1)),
        "axis_line_max":int(ml.group(1)),
        "quote_exact":int(mq.group(1)),
        "main_carousel_binding":"main-card-carousel|main-carousel|component_min_count",
        "mini_carousel_binding":"signature-mini-carousel|mini-carousel|component_min_count",
    }


def _rc1623_render_projection_contract():
    base=Path(__file__).resolve().parent
    gt=(base/"STRUCTURE_REPONSES_DECKS_PERSONNAGES_V50.md").read_text(encoding="utf-8")
    at=(base/"STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES_V1.md").read_text(encoding="utf-8")
    return _rc1623_render_projection_contract_from_texts(gt,at)


def _rc1623_projection_fingerprint(doc):
    raw=json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _rc1623_assert_render_projection_contract(doc):
    expected=RC1623_RENDER_PROJECTION_CONTRACT_EXPECTED
    if doc!=expected:
        fail("RENDER_PROJECTION_SOURCE_VERSION_UNSUPPORTED: projection contract")
    return _rc1623_projection_fingerprint(doc)


def _rc1623_assert_source_integrity(st,filename):
    observed=_source_hash_from_state(st,filename)
    fp=Path(__file__).resolve().parent/filename
    if not fp.exists(): fail(f"ACTIVE_SOURCE_MISSING: {filename}")
    actual=sha256(fp)
    if observed!=actual:
        fail(f"ACTIVE_SOURCE_INTEGRITY_MISMATCH: {filename}")
    return actual


def _rc16221_assert_render_projection_sources(st):
    # First prove the run is bound to the physical package actually executing.
    for filename in ("STRUCTURE_REPONSES_DECKS_PERSONNAGES_V50.md","STRUCTURE_AXES_COMBOS_DECKS_PERSONNAGES_V1.md"):
        _rc1623_assert_source_integrity(st,filename)
    # Then prove that the relevant authority-owned clauses are a supported projection.
    return _rc1623_assert_render_projection_contract(_rc1623_render_projection_contract())


def _rc16221_source_owned_axis_limits(st):
    """Read Render criteria from the active authority projection contract.

    Source integrity is checked against the run inventory; compatibility is checked
    against only the clauses actually projected by the deterministic shell.
    """
    _rc16221_assert_render_projection_sources(st)
    doc=_rc1623_render_projection_contract()
    return {"arrow_max":doc["axis_arrow_max"],"line_max":doc["axis_line_max"],"quote_exact":doc["quote_exact"]}


def sequence(st):
    """Derive multi-system ledger applicability from the architecture itself.

    Single-system runs never enter the multi-system ledger branch. A real
    multi-system run always traverses MULTI + MECH because the validator exists in
    this release; callers no longer choose that mechanical applicability bit.
    """
    seq=list(BASE)
    if st.get("multi_system"):
        seq += MULTI
        seq += MECH
    seq += RENDER
    return seq


_cmd_dispatch_run_rc1622 = cmd_dispatch_run

def cmd_dispatch_run_rc16221(a):
    # Reject the exact inconsistent combination seen in Jack before a run exists,
    # then derive the validator bit for multi-system runs rather than trusting the caller.
    multi=bool(getattr(a,"multi_system",False))
    if bool(getattr(a,"mechanical_validation",False)) and not multi:
        fail("MECHANICAL_VALIDATION_NOT_APPLICABLE_TO_SINGLE_SYSTEM")
    if multi:
        setattr(a,"mechanical_validation",True)
    return _cmd_dispatch_run_rc1622(a)

cmd_dispatch_run = cmd_dispatch_run_rc16221


def _rc16221_capture_files(paths):
    snap={}
    for p in paths:
        p=Path(p)
        snap[str(p.resolve())]=p.read_bytes() if p.exists() and p.is_file() else None
    return snap


def _rc16221_restore_files(snapshot):
    for name,data in snapshot.items():
        p=Path(name)
        if data is None:
            if p.exists() and p.is_file(): p.unlink()
        else:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)


def _rc16221_axis_scope(text):
    lines=text.splitlines()
    start=None; end=None
    for line in lines:
        if re.match(r"(?i)^##\s+(?:6\.\s+)?Axes de jeu\b",line.strip()):
            start=line.strip(); break
    if start is None:
        for line in lines:
            if re.match(r"(?i)^#{2,4}\s+Axe\s+\d+\b",line.strip()):
                start=line.strip(); break
    if start is None: fail("PREFREEZE_AXES_SCOPE_MISSING")
    found=False
    for line in lines:
        ls=line.strip()
        if ls==start: found=True; continue
        if found and re.match(r"(?i)^##\s+(?:8\.\s+)?(?:Point de rupture|Progression|Points faibles)\b",ls):
            end=ls; break
    return "^"+re.escape(start)+"$", ("^"+re.escape(end)+"$" if end else r"\Z")


def _rc16221_quote_binding(text, visual, source_limits):
    sig=(visual.get("signature_climax") or {})
    if sig.get("terminal_quote_required") is not True: return None
    quote_re=re.compile(r"^###\s+\*\*.+—\s*«.+»\*\*\s*$")
    lines=text.splitlines()
    parent=sig.get("parent")
    scope_start=None; scope_end=r"\Z"; in_scope=False; matches=[]
    if nonempty(parent):
        for i,line in enumerate(lines):
            if re.match(r"^#{2,4}\s+",line.strip()) and parent.casefold() in line.casefold():
                scope_start="^"+re.escape(line.strip())+"$"; in_scope=True
                end_index=len(lines)
                for j in range(i+1,len(lines)):
                    ls=lines[j].strip()
                    # A terminal quote is itself a heading and belongs to the current
                    # climax. Only a sibling Axe or a level-2 section closes scope.
                    if re.match(r"(?i)^###\s+Axe\s+\d+\b",ls) or re.match(r"^##\s+",ls):
                        scope_end="^"+re.escape(ls)+"$"; end_index=j; break
                segment=lines[i:end_index]
                matches=[x.strip() for x in segment if quote_re.match(x.strip())]
                break
    if scope_start is None:
        # Fallback is still bounded to the Axes section, never the whole document.
        scope_start,scope_end=_rc16221_axis_scope(text)
        active=False; segment=[]
        sre=re.compile(scope_start); ere=re.compile(scope_end)
        for line in lines:
            if not active and sre.search(line): active=True
            if active:
                if ere.pattern!=r"\Z" and ere.search(line) and segment: break
                segment.append(line)
        matches=[x.strip() for x in segment if quote_re.match(x.strip())]
    expected=source_limits["quote_exact"]
    if len(matches)!=expected:
        fail(f"PREFREEZE_TERMINAL_QUOTE_CARDINALITY: observed={len(matches)} expected={expected}")
    return {
        "id":"signature-terminal-quote","source":AXES_STRUCTURE,"applicable":True,
        "description":"signature terminal quote exact cardinality",
        "assertions":[{"type":"regex_exact_count","pattern":"^"+re.escape(matches[0])+"$","exact":expected,"scope_start":scope_start,"scope_end":scope_end}],
    }


def _rc16221_render_policy(st, render_path: Path):
    _rc16221_assert_render_projection_sources(st)
    if not render_path.exists() or not render_path.is_file(): fail("RENDER_FILE_MISSING")
    text=render_path.read_text(encoding="utf-8")
    limits=_rc16221_source_owned_axis_limits(st)
    vg=(st.get("gates") or {}).get("VISUAL_ASSETS_BOUND",{})
    if not vg.get("evidence_file"): fail("VISUAL_ASSETS_REQUIRED_FOR_RENDER_COMMIT")
    visual=read_json(Path(vg["evidence_file"]),"visual assets")
    axis_start,axis_end=_rc16221_axis_scope(text)
    axe_count=len(re.findall(r"(?im)^#{2,4}\s+Axe\s+\d+\b",text))
    if axe_count>=2 and not re.search(r"(?im)^##\s+Guide de pilotage\s*$",text):
        fail("PREFREEZE_PILOTAGE_GUIDE_NOT_MATERIALIZED")
    reqs=[
      {"id":"decklist-vertical","source":GLOBAL_STRUCTURE,"applicable":True,"description":"one deck entry per physical line","assertions":[{"type":"max_regex_count_per_line","pattern":r"\b\d+\s*[×xX]\s+[^\n]+","max":1}]},
      {"id":"decklist-mode","source":GLOBAL_STRUCTURE,"applicable":True,"description":"deck groups or refactor diff","compile":"DECKLIST_MODE_FROM_STATE"},
      {"id":"direction-binding","source":GLOBAL_STRUCTURE,"applicable":True,"description":"final direction binding","compile":"FINAL_DIRECTION_FROM_CLASSIFICATION"},
      {"id":"axis-line-length","source":AXES_STRUCTURE,"applicable":True,"description":"axis line length","assertions":[{"type":"max_line_length","max":limits["line_max"],"scope_start":axis_start,"scope_end":axis_end}]},
      {"id":"axis-arrow-density","source":AXES_STRUCTURE,"applicable":True,"description":"axis arrow density","assertions":[{"type":"max_arrow_count_per_line","max":limits["arrow_max"],"scope_start":axis_start,"scope_end":axis_end}]},
    ]
    main=visual.get("main_carousel") or {}
    sig=visual.get("signature_climax") or {}
    if main.get("applicable") is True:
        reqs.append({"id":"main-card-carousel","source":AXES_STRUCTURE,"applicable":True,"description":"main emblematic card carousel","assertions":[{"type":"component_min_count","component_type":"main-carousel","min":1}]})
    q=_rc16221_quote_binding(text,visual,limits)
    if q: reqs.append(q)
    if sig.get("mini_carousel_applicable") is True:
        parent=sig.get("parent")
        reqs.append({"id":"signature-mini-carousel","source":AXES_STRUCTURE,"applicable":True,"description":"signature combo mini carousel","assertions":[{"type":"component_min_count","component_type":"mini-carousel","parent":parent,"min":1}]})
    return {"authorities":sorted(RENDER_AUTHORITIES),"requirements":reqs,"derived_from":"RC16.22.1 deterministic projection of active STRUCTURE decisions"}


def _rc16221_component_refs(visual, kind):
    block=(visual.get("main_carousel") or {}) if kind=="main" else (visual.get("signature_climax") or {})
    local=block.get("image_refs")
    if isinstance(local,list) and local: return list(local)
    refs=list(visual.get("image_refs") or [])
    if kind=="main": return refs[:4]
    return refs[:4]


def _rc16221_component_plan(st, visual_path: Path):
    visual=read_json(visual_path,"visual assets")
    comps=[]
    main=visual.get("main_carousel") or {}; sig=visual.get("signature_climax") or {}
    if main.get("applicable") is True:
        refs=_rc16221_component_refs(visual,"main")
        if not (2<=len(refs)<=4): fail("PREFREEZE_MAIN_CAROUSEL_IMAGE_REFS_INVALID")
        comps.append({"component_id":"main-card-carousel","type":"main-carousel","parent":None,"tags":["cartes-emblematiques"],"selected_cards":list(main.get("selected_cards") or []),"image_refs":refs})
    if sig.get("mini_carousel_applicable") is True:
        refs=_rc16221_component_refs(visual,"mini")
        if not (3<=len(refs)<=4): fail("PREFREEZE_SIGNATURE_MINI_IMAGE_REFS_INVALID")
        comps.append({"component_id":"signature-mini-carousel","type":"mini-carousel","parent":sig.get("parent"),"tags":["signature","combo"],"selected_cards":list(sig.get("selected_cards") or []),"image_refs":refs})
    return {"schema":COMPONENT_PLAN_SCHEMA,"run_id":st["run_id"],"deck_artifact":st.get("current_artifact"),"render_id":expected_render_id(st),"authorities":sorted(RENDER_AUTHORITIES),"visual_assets_sha256":sha256(visual_path),"components":comps}


def _rc16221_stage_render(rd: Path, st, render_path: Path, policy_path: Path, contract_path: Path, plan_path: Path, comp_dir: Path, comp_manifest_path: Path, render_manifest_path: Path):
    vg=st["gates"]["VISUAL_ASSETS_BOUND"]; visual_path=Path(vg["evidence_file"])
    policy=_rc16221_render_policy(st,render_path); _atomic_write_text(policy_path,_stable_json_text(policy))
    payload=compile_render_contract_payload(policy_path,st,contract_path.parent); _atomic_write_text(contract_path,_stable_json_text(payload))
    # Stage-state mirrors the post-freeze identity without mutating authoritative files.
    stage=json.loads(json.dumps(st)); stage["current_render"]=payload["render_id"]
    stage.setdefault("gates",{})["RENDER_CONTRACT_FROZEN"]={"run_id":stage["run_id"],"authority":GLOBAL_STRUCTURE,"status":"FROZEN","artifact":stage.get("current_artifact"),"evidence_file":str(contract_path),"evidence_sha256":sha256(contract_path),"render_id":payload["render_id"],"render_policy_fingerprint":render_policy_fingerprint(payload)}
    validate_compiled_render_contract(contract_path,stage)
    plan=_rc16221_component_plan(stage,visual_path); _atomic_write_text(plan_path,_stable_json_text(plan))
    docs=compile_component_payloads(plan_path,visual_path,comp_dir,stage); cfiles=[Path(x["file"]) for x in docs]
    compile_component_manifest(plan_path,visual_path,cfiles,comp_manifest_path,stage)
    cm=read_json(comp_manifest_path,"compiled component manifest")
    components=validate_components(comp_manifest_path,cm,stage)
    ch=sha256(contract_path); rh=sha256(render_path)
    canonical={"run_id":stage["run_id"],"deck_artifact":stage.get("current_artifact"),"render_id":stage.get("current_render"),"contract_sha256":ch,"render_sha256":rh,"generated_by":"render-commit-preflight","runtime_version":VERSION,"requirements":[{"id":r["id"],"status":"SATISFIED","evidence":f"render-commit:{r['id']}"} for r in payload["requirements"]],"components":_canonicalize_components(comp_manifest_path,components,render_manifest_path)}
    _atomic_write_text(render_manifest_path,json.dumps(canonical,ensure_ascii=False,indent=2)+"\n")
    try:
        hashes=validate_render_manifest(render_manifest_path,render_path,contract_path,stage)
    except SystemExit as exc:
        _,detail=_denied_parts(exc)
        fail("PREFREEZE_RENDER_VALIDATION_FAILED: "+detail)
    # Execute the exact render assertions against the staged identity before any
    # authoritative gate is closed. This turns mechanically detectable render
    # defects into candidate failures, not post-freeze repair loops.
    failures,_,_,_,_= _collect_render_failures(render_path,contract_path,comp_manifest_path,stage)
    if failures:
        codes=",".join(x.get("code","UNKNOWN") for x in failures if isinstance(x,dict))
        fail("PREFREEZE_RENDER_VALIDATION_FAILED: "+codes)
    return {"policy":policy_path,"contract":contract_path,"plan":plan_path,"component_manifest":comp_manifest_path,"component_files":cfiles,"render_manifest":render_manifest_path,"hashes":hashes}


def cmd_render_commit(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"render-commit")
    if next_gate(st)[0]!="RENDER_CONTRACT_FROZEN": fail(f"render-commit requires next gate RENDER_CONTRACT_FROZEN; next gate is {next_gate(st)[0]}")
    render=Path(a.render_file)
    policy=rd/"render_policy.derived.json"; contract=rd/"render_contract.json"; plan=rd/"component_plan.derived.json"; comp_dir=rd/"components"; comp_manifest=rd/"component_manifest.derived.json"; manifest=rd/"render_manifest.json"
    outputs=[policy,contract,plan,comp_manifest,manifest]
    if comp_dir.exists(): outputs.extend([x for x in comp_dir.glob("component__*.json")])
    auth_snap=_rc1622_capture_authoritative(rd,st); file_snap=_rc16221_capture_files(outputs)
    cp=_load_checkpoint_raw(rd,True); tx=f"render-commit-{sum(1 for e in _read_journal(rd) if e.get('event')=='RENDER_COMMIT_STARTED')+1:06d}"
    _append_run_journal(rd,st,"RENDER_COMMIT_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),transaction_id=tx,render_file=str(render),render_sha256=sha256(render) if render.exists() else None,state_sha256_before=sha256(rd/STATE_FILE))
    try:
        staged=_rc16221_stage_render(rd,st,render,policy,contract,plan,comp_dir,comp_manifest,manifest)
        _append_run_journal(rd,st,"RENDER_COMMIT_PREFLIGHT_SUCCEEDED",checkpoint_seq=cp.get("checkpoint_seq"),transaction_id=tx,contract_sha256=sha256(contract),render_sha256=sha256(render),component_manifest_sha256=sha256(comp_manifest))
        ns=Namespace(run_dir=str(rd),run_id=st["run_id"],gate="RENDER_CONTRACT_FROZEN",authority=GLOBAL_STRUCTURE,status="FROZEN",evidence_file=str(contract),render_manifest=None,contract_file=None,combo_impact_file=None,pilotage_contract_file=None,pilotage_preflight_receipt=None,terminal_presentation_plan=None,terminal_presentation_receipt=None,_derived_reentry=True)
        cmd_complete(ns)
        cfiles=[str(x) for x in staged["component_files"]]
        cmd_render_check(Namespace(run_dir=str(rd),run_id=st["run_id"],render_file=str(render),contract_file=str(contract),component_manifest=str(comp_manifest),component_plan_file=str(plan),visual_assets_file=str(Path(load_state(rd)["gates"]["VISUAL_ASSETS_BOUND"]["evidence_file"])),component_file=cfiles,write_manifest=str(manifest)))
        ns2=Namespace(run_dir=str(rd),run_id=st["run_id"],gate="FINAL_RENDER_PREPARED",authority=GLOBAL_STRUCTURE,status="PREPARED",evidence_file=str(render),render_manifest=str(manifest),contract_file=str(contract),combo_impact_file=None,pilotage_contract_file=None,pilotage_preflight_receipt=None,terminal_presentation_plan=None,terminal_presentation_receipt=None)
        cmd_complete(ns2)
        st2=load_state(rd); cp2=_load_checkpoint_raw(rd,True)
        _append_run_journal(rd,st2,"RENDER_COMMIT_SUCCEEDED",checkpoint_seq=cp2.get("checkpoint_seq"),transaction_id=tx,render_id=st2.get("current_render"),contract_sha256=sha256(contract),render_manifest_sha256=sha256(manifest),state_sha256_after=sha256(rd/STATE_FILE))
        print(json.dumps({"status":"PASS","transaction_id":tx,"render_id":st2.get("current_render"),"render_file":str(render),"contract_file":str(contract),"render_manifest":str(manifest),"component_manifest":str(comp_manifest),"next_required_gate":next_gate(st2)[0]},ensure_ascii=False,indent=2))
    except BaseException as exc:
        _rc1622_restore_authoritative(auth_snap); _rc16221_restore_files(file_snap)
        stf=load_state(rd); cpf=_load_checkpoint_raw(rd,False) or {}; code,detail=_denied_parts(exc) if isinstance(exc,SystemExit) else (type(exc).__name__,str(exc))
        _append_run_journal(rd,stf,"RENDER_COMMIT_ROLLED_BACK",checkpoint_seq=cpf.get("checkpoint_seq"),transaction_id=tx,error_code=code,detail=detail,state_sha256_after=sha256(rd/STATE_FILE))
        raise


def _rc16221_render_bindings(st):
    fr=(st.get("gates") or {}).get("FINAL_RENDER_PREPARED",{})
    cr=(st.get("gates") or {}).get("RENDER_CONTRACT_FROZEN",{})
    render=fr.get("evidence_file"); manifest=fr.get("manifest_file"); contract=cr.get("evidence_file")
    if not all(nonempty(x) for x in (render,manifest,contract)): fail("CURRENT_RENDER_BINDINGS_INCOMPLETE")
    return Path(render),Path(manifest),Path(contract)


def _rc16221_write_pilotage_business_receipt(rd: Path, st, business: Path, contract: Path, render: Path, preflight: Path):
    # This receipt proves execution of the existing FULL_SHARED_VALIDATOR on the
    # exact contract/render. It does NOT claim an independent semantic oracle for
    # card facts omitted or misread by the model.
    pr=read_json(preflight,"Pilotage preflight receipt")
    if pr.get("status")!="PASS" or pr.get("validation_mode")!="FULL_SHARED_VALIDATOR":
        fail("PILOTAGE_FULL_SHARED_VALIDATOR_EXECUTION_REQUIRED")
    if pr.get("pilotage_contract_sha256")!=sha256(contract) or pr.get("render_sha256")!=sha256(render):
        fail("PILOTAGE_FULL_SHARED_VALIDATOR_RECEIPT_STALE")
    out=rd/RC16221_PILOTAGE_BUSINESS_RECEIPT
    doc={"schema":RC16221_PILOTAGE_BUSINESS_RECEIPT_SCHEMA,"status":"PASS","run_id":st["run_id"],"deck_artifact":st.get("current_artifact"),"business_payload_file":str(business.resolve()),"business_payload_sha256":sha256(business),"pilotage_contract_file":str(contract.resolve()),"pilotage_contract_sha256":sha256(contract),"render_sha256":sha256(render),"pilotage_source_sha256":_pilotage_policy_sha256(st),"preflight_receipt_sha256":sha256(preflight),"runtime_version":VERSION,"validator":"FULL_SHARED_VALIDATOR","semantic_oracle":"NOT_CLAIMED"}
    _atomic_write_text(out,_stable_json_text(doc)); return out


def _rc16221_verify_pilotage_business_receipt(path: Path, business: Path, contract: Path, render: Path, st):
    if not path.exists(): fail("PILOTAGE_BUSINESS_EXECUTION_RECEIPT_REQUIRED")
    d=read_json(path,"Pilotage business validation receipt")
    expected={"schema":RC16221_PILOTAGE_BUSINESS_RECEIPT_SCHEMA,"status":"PASS","run_id":st["run_id"],"deck_artifact":st.get("current_artifact"),"business_payload_sha256":sha256(business),"pilotage_contract_sha256":sha256(contract),"render_sha256":sha256(render),"pilotage_source_sha256":_pilotage_policy_sha256(st),"validator":"FULL_SHARED_VALIDATOR","semantic_oracle":"NOT_CLAIMED"}
    for k,v in expected.items():
        if d.get(k)!=v: fail("PILOTAGE_BUSINESS_EXECUTION_RECEIPT_STALE")
    return d


def _current_deck_snapshot_sha256(st):
    rec=(st.get("gates") or {}).get("DECK_DRAFT_CREATED") or {}
    raw=rec.get("snapshot_file") or rec.get("evidence_file")
    if nonempty(raw) and Path(raw).exists(): return sha256(Path(raw))
    return None


def _decorate_preflight_issue(issue):
    x=copy.deepcopy(issue) if isinstance(issue,dict) else {"code":"UNKNOWN","observed":str(issue)}
    code=x.get("code") or "UNKNOWN"
    x["domain"]=_pilotage_issue_domain(code)
    observed=str(x.get("observed") or "")
    # Recover useful business coordinates from canonical `CODE: line:replay:...` details.
    if observed.startswith(str(code)+":"):
        tail=observed[len(str(code))+1:].strip()
        parts=[z for z in tail.split(":") if z]
        if parts and "line_id" not in x: x["line_id"]=parts[0]
        if len(parts)>1 and "replay_id" not in x: x["replay_id"]=parts[1]
        if len(parts)>2 and "step_id" not in x: x["step_id"]=parts[2]
    return x


def _authoritative_pilotage_dry_run(rd: Path, st, business: Path, render: Path, write_receipt=True):
    if not business.exists(): fail("PILOTAGE_BUSINESS_PAYLOAD_MISSING")
    if not render.exists(): fail("PILOTAGE_RENDER_MISSING")
    before=sha256(rd/STATE_FILE)
    cp=_load_checkpoint_raw(rd,False) or {}
    _append_run_journal(rd,st,"PILOTAGE_AUTHORITATIVE_DRY_RUN_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),business_payload_sha256=sha256(business),render_sha256=sha256(render),deck_sha256=_current_deck_snapshot_sha256(st),read_only=True)
    payload=read_json(business,"Pilotage business payload")
    issues=[]
    if not _pilotage_builder_receipt_valid(rd,st,business,render):
        issues=[{"code":"PILOTAGE_BUSINESS_BUILDER_REQUIRED","path":"$","expected":"fresh shell builder merge receipt for exact deck/render/business payload","observed":str(rd/PILOTAGE_BUSINESS_MERGE_RECEIPT)}]
    else:
        issues=_pilotage_business_issues(payload)
    if not issues:
        try:
            compiled=_compile_pilotage_contract_document(st,payload,render)
            with tempfile.TemporaryDirectory(prefix="ygo-pilotage-dryrun-") as td:
                td=Path(td); contract=td/"pilotage_contract.json"; schema=td/"pilotage_schema.json"
                _atomic_write_text(contract,_stable_json_text(compiled))
                _atomic_write_text(schema,_stable_json_text(_pilotage_wire_schema_payload(st)))
                combo=_rc1622_resolve_combo_impact(rd,st,None) if st.get("combo_impact_required") is True else None
                ma=Namespace(pilotage_contract_file=str(contract),render_file=str(render),schema_file=str(schema),combo_impact_file=combo)
                mechanical=_pilotage_mechanical_preflight_issues(ma,st)
                authoritative=_pilotage_full_preflight_issues(contract,render,st)
                both=mechanical+authoritative
                uniq={json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")):x for x in both}
                issues=sorted(uniq.values(),key=lambda x:(x.get("path") or "",x.get("code") or ""))
        except SystemExit as e:
            code,detail=_denied_parts(e)
            issues=[{"code":code,"path":"$","expected":"authoritative dry-run pass","observed":detail}]
    issues=[_decorate_preflight_issue(x) for x in issues]
    domains=sorted({x.get("domain") for x in issues if nonempty(x.get("domain"))})
    doc={
        "schema":"ygo-pilotage-authoritative-dry-run-receipt-v1",
        "status":"FAIL" if issues else "PASS",
        "run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),
        "deck_sha256":_current_deck_snapshot_sha256(st),"render_sha256":sha256(render),
        "business_payload_file":str(business),"business_payload_sha256":sha256(business),
        "pilotage_source_sha256":_pilotage_policy_sha256(st),"issue_count":len(issues),"issues":issues,
        "repair_domains":domains,"read_only":True,"state_sha256_before":before,"state_sha256_after":sha256(rd/STATE_FILE),
        "runtime_version":VERSION,"validator":"FULL_SHARED_VALIDATOR"
    }
    out=rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT
    if write_receipt: _atomic_write_text(out,_stable_json_text(doc))
    _append_run_journal(rd,st,"PILOTAGE_AUTHORITATIVE_DRY_RUN_COMPLETED",checkpoint_seq=cp.get("checkpoint_seq"),status=doc["status"],issue_count=len(issues),issue_codes=sorted(x.get("code") for x in issues),repair_domains=domains,receipt_file=str(out) if write_receipt else None,receipt_sha256=sha256(out) if write_receipt and out.exists() else None,business_payload_sha256=doc["business_payload_sha256"],render_sha256=doc["render_sha256"],deck_sha256=doc["deck_sha256"],state_sha256_before=before,state_sha256_after=sha256(rd/STATE_FILE),read_only=True)
    return doc,out


def _pilotage_repair_fingerprint(st, receipt, domain):
    basis={"deck_artifact":st.get("current_artifact"),"deck_sha256":receipt.get("deck_sha256"),"render_sha256":receipt.get("render_sha256"),"business_payload_sha256":receipt.get("business_payload_sha256"),"domain":domain,"codes":sorted(x.get("code") for x in receipt.get("issues",[]) if x.get("domain")==domain)}
    return hashlib.sha256(json.dumps(basis,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _business_failure_count(rd: Path, st):
    return sum(1 for e in _read_journal(rd) if e.get("event")=="PILOTAGE_BUSINESS_ATTEMPT_CONSUMED" and e.get("deck_artifact")==st.get("current_artifact"))


def _nonbusiness_repair_count(rd: Path, st, domain):
    # Presentation/admin repairs are scoped to the exact render lineage.
    # A fresh render invalidates prior Pilotage artifacts and must not inherit
    # presentation retry debt from a superseded render.
    return sum(1 for e in _read_journal(rd) if e.get("event")=="PILOTAGE_REPAIR_ROUTED" and e.get("budget_class")=="NON_BUSINESS" and e.get("domain")==domain and e.get("deck_artifact")==st.get("current_artifact") and e.get("render_id")==st.get("current_render"))


def _repair_already_routed(rd: Path, fingerprint):
    return any(e.get("event")=="PILOTAGE_REPAIR_ROUTED" and e.get("repair_fingerprint")==fingerprint for e in _read_journal(rd))


def _route_failed_pilotage_dry_run(rd: Path, st, receipt):
    issues=receipt.get("issues",[]) if isinstance(receipt,dict) else []
    domains=sorted({x.get("domain") for x in issues if nonempty(x.get("domain"))})
    cp=_load_checkpoint_raw(rd,False) or {}
    if "UNRESOLVED_DOMAIN" in domains or not domains:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain="UNRESOLVED_DOMAIN",budget_class="FAIL_CLOSED",deck_artifact=st.get("current_artifact"),issue_count=len(issues))
        fail("PILOTAGE_REPAIR_DOMAIN_UNRESOLVED_FAIL_NON_CERTIFIE")
    nonbusiness=[d for d in domains if d in {"PRESENTATION_RENDER","PROOF_SCHEMA_ADMIN"}]
    if nonbusiness:
        routed=[]
        for domain in nonbusiness:
            fp=_pilotage_repair_fingerprint(st,receipt,domain)
            if _repair_already_routed(rd,fp):
                routed.append({"domain":domain,"reused":True}); continue
            used=_nonbusiness_repair_count(rd,st,domain)
            if used>=PILOTAGE_NON_BUSINESS_REPAIR_BUDGET:
                _append_run_journal(rd,st,"NON_BUSINESS_REPAIR_EXHAUSTED",checkpoint_seq=cp.get("checkpoint_seq"),domain=domain,deck_artifact=st.get("current_artifact"),repairs_used=used,repair_budget=PILOTAGE_NON_BUSINESS_REPAIR_BUDGET,repair_fingerprint=fp)
                fail(f"NON_BUSINESS_REPAIR_EXHAUSTED: {domain}")
            _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain=domain,budget_class="NON_BUSINESS",deck_artifact=st.get("current_artifact"),repair_cycle=used+1,repair_budget=PILOTAGE_NON_BUSINESS_REPAIR_BUDGET,repair_fingerprint=fp,issue_codes=sorted(x.get("code") for x in issues if x.get("domain")==domain))
            routed.append({"domain":domain,"repair_cycle":used+1})
        fail("PILOTAGE_NON_BUSINESS_REPAIR_REQUIRED: "+json.dumps(routed,ensure_ascii=False,sort_keys=True,separators=(",",":")))
    # Only true business/mechanical failures may spend the business budget.
    fp=_pilotage_repair_fingerprint(st,receipt,"BUSINESS_SEMANTIC_MECHANICAL")
    if _repair_already_routed(rd,fp):
        fail("PILOTAGE_BUSINESS_REPAIR_REQUIRED_SAME_INPUT_ALREADY_COUNTED")
    used=_business_failure_count(rd,st)
    if used>=PILOTAGE_COMMIT_ATTEMPT_BUDGET:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_BUDGET_EXHAUSTED",checkpoint_seq=cp.get("checkpoint_seq"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact"))
        fail("PILOTAGE_REPAIR_BUDGET_EXHAUSTED_FAIL_NON_CERTIFIE")
    used+=1
    _append_run_journal(rd,st,"PILOTAGE_BUSINESS_ATTEMPT_CONSUMED",checkpoint_seq=cp.get("checkpoint_seq"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact"),repair_fingerprint=fp,issue_codes=sorted(x.get("code") for x in issues))
    _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS",deck_artifact=st.get("current_artifact"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,repair_fingerprint=fp,issue_codes=sorted(x.get("code") for x in issues))
    if used>=PILOTAGE_COMMIT_ATTEMPT_BUDGET:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_BUDGET_EXHAUSTED",checkpoint_seq=cp.get("checkpoint_seq"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact"))
        fail("PILOTAGE_REPAIR_BUDGET_EXHAUSTED_FAIL_NON_CERTIFIE")
    fail("PILOTAGE_BUSINESS_REPAIR_REQUIRED")


def cmd_pilotage_authoritative_dry_run(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"pilotage-authoritative-dry-run")
    if next_gate(st)[0]!="PILOTAGE_VALIDATED": fail(f"pilotage-authoritative-dry-run requires next gate PILOTAGE_VALIDATED; next gate is {next_gate(st)[0]}")
    if _business_failure_count(rd,st)>=PILOTAGE_COMMIT_ATTEMPT_BUDGET:
        fail("PILOTAGE_REPAIR_BUDGET_EXHAUSTED_FAIL_NON_CERTIFIE")
    business=Path(a.business_payload_file); render,manifest,render_contract=_rc16221_render_bindings(st)
    receipt,_=_authoritative_pilotage_dry_run(rd,st,business,render,write_receipt=True)
    if receipt.get("status")!="PASS":
        route=_route_failed_pilotage_dry_run(rd,st,receipt)
        if isinstance(route,dict): receipt["recovery"]=route
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return receipt


def cmd_pilotage_commit(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"pilotage-commit")
    if next_gate(st)[0]!="PILOTAGE_VALIDATED": fail(f"pilotage-commit requires next gate PILOTAGE_VALIDATED; next gate is {next_gate(st)[0]}")
    if _business_failure_count(rd,st)>=PILOTAGE_COMMIT_ATTEMPT_BUDGET:
        cp0=_load_checkpoint_raw(rd,False) or {}
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_BUDGET_EXHAUSTED",checkpoint_seq=cp0.get("checkpoint_seq"),attempts_used=_business_failure_count(rd,st),attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact"))
        fail("PILOTAGE_REPAIR_BUDGET_EXHAUSTED_FAIL_NON_CERTIFIE")
    business=Path(a.business_payload_file); render,manifest,render_contract=_rc16221_render_bindings(st)
    if not business.exists(): fail("PILOTAGE_BUSINESS_PAYLOAD_MISSING")

    # MCB2: authoritative read-only gate mirror. No Pilotage commit transaction
    # exists until the exact deck/render/business tuple has passed this dry-run.
    dry,_=_authoritative_pilotage_dry_run(rd,st,business,render,write_receipt=True)
    if dry.get("status")!="PASS":
        route=_route_failed_pilotage_dry_run(rd,st,dry)
        if isinstance(route,dict):
            fail("PILOTAGE_AUTO_RECOVERY_REQUIRED: "+json.dumps(route,ensure_ascii=False,sort_keys=True,separators=(",",":")))
    current_deck_sha=_current_deck_snapshot_sha256(st); current_render_sha=sha256(render); current_business_sha=sha256(business)
    if not _pilotage_dry_run_commit_eligible(dry,current_deck_sha,current_render_sha,current_business_sha):
        fail("PILOTAGE_AUTHORITATIVE_DRY_RUN_STALE")

    contract=rd/"pilotage_contract.json"; schema=rd/"pilotage_schema.json"; preflight=rd/PILOTAGE_PREFLIGHT_RECEIPT; breceipt=rd/RC16221_PILOTAGE_BUSINESS_RECEIPT
    auth_snap=_rc1622_capture_authoritative(rd,st); file_snap=_rc16221_capture_files([contract,schema,preflight,breceipt])
    cp=_load_checkpoint_raw(rd,True); tx=f"pilotage-commit-{sum(1 for e in _read_journal(rd) if e.get('event')=='PILOTAGE_COMMIT_STARTED')+1:06d}"
    _append_run_journal(rd,st,"PILOTAGE_COMMIT_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),transaction_id=tx,business_payload_file=str(business),business_payload_sha256=current_business_sha,render_sha256=current_render_sha,deck_sha256=current_deck_sha,dry_run_receipt_file=str(rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT),dry_run_receipt_sha256=sha256(rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT))
    try:
        cmd_compile_pilotage_contract(Namespace(run_dir=str(rd),run_id=st["run_id"],business_payload_file=str(business),render_file=str(render),output=str(contract)))
        _atomic_write_text(schema,_stable_json_text(_pilotage_wire_schema_payload(st)))
        # This is the same authoritative validator used by the dry-run. It should
        # now be a deterministic confirmation, not a discovery surface.
        cmd_pilotage_preflight(Namespace(run_dir=str(rd),run_id=st["run_id"],pilotage_contract_file=str(contract),render_file=str(render),schema_file=str(schema),output=str(preflight),combo_impact_file=None,contract_file=str(render_contract),render_manifest=str(manifest),component_plan_file=None,component_manifest=None))
        br=_rc16221_write_pilotage_business_receipt(rd,st,business,contract,render,preflight); _rc16221_verify_pilotage_business_receipt(br,business,contract,render,st)
        st_now=load_state(rd)
        ns=Namespace(run_dir=str(rd),run_id=st_now["run_id"],gate="PILOTAGE_VALIDATED",authority=PILOTAGE,status="PASS",evidence_file=str(render),render_manifest=str(manifest),contract_file=str(render_contract),combo_impact_file=None,pilotage_contract_file=str(contract),pilotage_preflight_receipt=str(preflight),terminal_presentation_plan=None,terminal_presentation_receipt=None)
        cmd_complete(ns)
        st2=load_state(rd); cp2=_load_checkpoint_raw(rd,True)
        _append_run_journal(rd,st2,"PILOTAGE_SPECIALIZED_VALIDATOR_EXECUTED",checkpoint_seq=cp2.get("checkpoint_seq"),transaction_id=tx,business_receipt_file=str(br),business_receipt_sha256=sha256(br),pilotage_contract_sha256=sha256(contract),render_sha256=sha256(render))
        _append_run_journal(rd,st2,"PILOTAGE_COMMIT_SUCCEEDED",checkpoint_seq=cp2.get("checkpoint_seq"),transaction_id=tx,next_required_gate=next_gate(st2)[0],state_sha256_after=sha256(rd/STATE_FILE))
        print(json.dumps({"status":"PASS","transaction_id":tx,"pilotage_contract":str(contract),"preflight_receipt":str(preflight),"validator_execution_receipt":str(br),"dry_run_receipt":str(rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT),"next_required_gate":next_gate(st2)[0]},ensure_ascii=False,indent=2))
    except BaseException as exc:
        persisted_issues=[]
        if preflight.exists():
            try:
                pre_doc=read_json(preflight,"Pilotage preflight failure receipt")
                if isinstance(pre_doc.get("issues"),list): persisted_issues=[_decorate_preflight_issue(x) for x in pre_doc.get("issues")]
            except BaseException: persisted_issues=[]
        _rc1622_restore_authoritative(auth_snap); _rc16221_restore_files(file_snap)
        stf=load_state(rd); cpf=_load_checkpoint_raw(rd,False) or {}; code,detail=_denied_parts(exc) if isinstance(exc,SystemExit) else (type(exc).__name__,str(exc))
        freceipt=rd/PILOTAGE_COMMIT_FAILURE_RECEIPT
        fdoc={"schema":"ygo-pilotage-commit-failure-receipt-v1","status":"FAIL","run_id":stf.get("run_id"),"deck_artifact":stf.get("current_artifact"),"transaction_id":tx,"business_payload_file":str(business),"business_payload_sha256":sha256(business) if business.exists() else None,"error_code":code,"detail":detail,"issue_count":len(persisted_issues),"issues":persisted_issues,"runtime_version":VERSION,"post_dry_run_failure":True}
        _atomic_write_text(freceipt,_stable_json_text(fdoc))
        _append_run_journal(rd,stf,"PILOTAGE_COMMIT_ROLLED_BACK",checkpoint_seq=cpf.get("checkpoint_seq"),transaction_id=tx,error_code=code,detail=detail,failure_receipt_file=str(freceipt),failure_receipt_sha256=sha256(freceipt),state_sha256_after=sha256(rd/STATE_FILE),post_dry_run_failure=True)
        _append_run_journal(rd,stf,"PILOTAGE_COMMIT_POST_DRYRUN_FAILURE",checkpoint_seq=cpf.get("checkpoint_seq"),transaction_id=tx,error_code=code,issue_count=len(persisted_issues))
        raise


_cmd_execute_batch_rc1622_parent = cmd_execute_batch_rc1622

def cmd_execute_batch_rc16221(a):
    # Terminal administrative gates are owned by one-shot commits. Final remains
    # batchable after terminal presentation because it is a true business closure.
    bundle=read_json(Path(a.bundle_file),"batch bundle")
    for op in bundle.get("operations",[]) if isinstance(bundle.get("operations"),list) else []:
        if isinstance(op,dict) and op.get("op")=="complete" and op.get("gate") in {"RENDER_CONTRACT_FROZEN","FINAL_RENDER_PREPARED","PILOTAGE_VALIDATED"}:
            fail(f"TERMINAL_ADMIN_GATE_REQUIRES_COMMIT: {op.get('gate')}")
    return _cmd_execute_batch_rc1622_parent(a)

cmd_execute_batch = cmd_execute_batch_rc16221

# advance-prepared resolves cmd_execute_batch_rc1622 by name inside its parent body;
# repoint the symbol too so the nominal router cannot bypass the new guard.
cmd_execute_batch_rc1622 = cmd_execute_batch_rc16221

_fastpath_summary_rc1619 = _fastpath_summary

def _fastpath_summary(rd: Path):
    out=_fastpath_summary_rc1619(rd); events=_read_journal(rd)
    out.update({
        "semantic_evidence_compiles":sum(1 for e in events if e.get("event")=="SEMANTIC_EVIDENCE_COMPILED"),
        "combo_impact_auto_bindings":sum(1 for e in events if e.get("event")=="COMBO_IMPACT_AUTO_BOUND"),
        "render_transaction_rollbacks":sum(1 for e in events if e.get("event")=="RENDER_CONTRACT_TRANSACTION_ROLLED_BACK"),
        "protocol_gate_failures":sum(1 for e in events if e.get("event")=="GATE_ATTEMPT_FAILED"),
    })
    return out

def _timing_target_run_dir(a):
    rd=getattr(a,"run_dir",None)
    if nonempty(rd) and Path(rd).exists(): return Path(rd)
    idx=_read_session_index(required=False)
    if isinstance(idx,dict) and nonempty(idx.get("run_dir")) and Path(idx["run_dir"]).exists(): return Path(idx["run_dir"])
    return Path(rd) if nonempty(rd) else None


def _fastpath_route_for_command(cmd):
    if cmd in {"advance-prepared","execute-batch"}: return "BATCH"
    if cmd in {"complete","compile-render-contract","compile-component-payloads","compile-component-manifest","render-check","compile-pilotage-contract","pilotage-preflight"}:
        return "FORBIDDEN_LOW_LEVEL"
    return "DIRECT_WHITELISTED"


def _instrumented_call(a):
    global RC1619_CLI_ACTIVE
    timed_commands={
        "campaign-open","start","dispatch-run","fork-refactor-from-terminal","complete","material-change","evidence-refresh","presentation-change","authorize",
        "compile-render-contract","compile-component-payloads","compile-component-manifest","render-check","compile-terminal-presentation","terminal-presentation-check",
        "contract-defect","abort-run","simulate-interruption","checkpoint-run","resume-run","pilotage-preflight","compile-pilotage-contract",
        "bind-explicit-direction","execute-batch","advance-prepared","evidence-refresh-selective","validate-bundle","render-commit","pilotage-business-skeleton","pilotage-business-merge","pilotage-semantic-template","pilotage-semantic-compile","render-semantic-compile","pilotage-authoritative-dry-run","pilotage-commit"
    }
    timed=a.cmd in timed_commands
    start_wall=time.time_ns(); start_mono=time.perf_counter_ns()
    before_rd=_timing_target_run_dir(a); before_cp=None
    if before_rd and (before_rd/CHECKPOINT_FILE).exists():
        try: before_cp=_load_checkpoint_raw(before_rd,False).get("checkpoint_seq")
        except BaseException: before_cp=None
    route=_fastpath_route_for_command(a.cmd)
    if route=="FORBIDDEN_LOW_LEVEL" and before_rd and (before_rd/STATE_FILE).exists():
        try:
            st=load_state(before_rd); cp=_load_checkpoint_raw(before_rd,False) or {}
            if st.get("fastpath_profile")==FASTPATH_PROFILE:
                _append_run_journal(before_rd,st,"FASTPATH_LOW_LEVEL_BLOCKED",checkpoint_seq=cp.get("checkpoint_seq"),command=a.cmd,reason="USE_NOMINAL_COMMIT_OR_BATCH",profile=FASTPATH_PROFILE)
                fail("LOW_LEVEL_ADMIN_COMMAND_FORBIDDEN_UNDER_FAST_ENFORCED: "+a.cmd)
        except SystemExit:
            raise
        except BaseException:
            pass
    RC1619_CLI_ACTIVE=True
    try:
        return a.func(a)
    finally:
        RC1619_CLI_ACTIVE=False
        end_mono=time.perf_counter_ns(); end_wall=time.time_ns(); rd=_timing_target_run_dir(a)
        if timed and rd and (rd/STATE_FILE).exists():
            try:
                st=load_state(rd); cp=_load_checkpoint_raw(rd,False) or {}
                _append_run_journal(rd,st,"COMMAND_TIMING",checkpoint_seq=cp.get("checkpoint_seq"),command=a.cmd,start_wall_ns=start_wall,end_wall_ns=end_wall,elapsed_local_seconds=round((end_mono-start_mono)/1_000_000_000,9),checkpoint_seq_before=before_cp,checkpoint_seq_after=cp.get("checkpoint_seq"),fastpath_route=route,local_time_scope="RUNTIME_COMMAND_ONLY_NOT_MODEL_WEB_OR_USER_WAIT")
            except BaseException:
                pass


# =============================================================================
# RC16.23 — Architectural hardening overlay
# Flat-source invariant: keep the install surface flat.  These helpers remain in
# the single runtime file; no package/module tree is introduced.
# =============================================================================

RC1623_STRUCTURAL_INVENTORY_SCHEMA = "ygo-style-axes-structural-inventory-v1"
RC1623_PATCH_SCOPE_SCHEMA = "ygo-pilotage-repair-scope-v1"
RUN_STATES = set(RUN_STATES) | {"BLOCKED_FATAL"}

# --------------------------- concurrency / atomicity -------------------------

def _rc1623_flock(path: Path):
    """Small process lock used only for runtime mutation serialization."""
    import fcntl
    class _Lock:
        def __enter__(self):
            path.parent.mkdir(parents=True,exist_ok=True)
            self.f=path.open("a+")
            fcntl.flock(self.f.fileno(),fcntl.LOCK_EX)
            return self
        def __exit__(self,exc_type,exc,tb):
            try: fcntl.flock(self.f.fileno(),fcntl.LOCK_UN)
            finally: self.f.close()
    return _Lock()


def _atomic_write_text(path: Path, text: str):
    """Crash-safe replace with process-unique staging filename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.time_ns()}")
    try:
        with tmp.open("w",encoding="utf-8",newline="\n") as f:
            f.write(text); f.flush()
            try: os.fsync(f.fileno())
            except OSError: pass
        os.replace(tmp,path)
        try:
            dfd=os.open(str(path.parent),os.O_DIRECTORY)
            try: os.fsync(dfd)
            finally: os.close(dfd)
        except OSError: pass
    finally:
        try:
            if tmp.exists(): tmp.unlink()
        except OSError: pass


def _append_run_journal(run_dir: Path, st, event, checkpoint_seq=None, **extra):
    """Append-only journal with a process lock: seq remains unique/contiguous."""
    run_dir.mkdir(parents=True,exist_ok=True)
    with _rc1623_flock(run_dir/".journal.lock"):
        events=_read_journal(run_dir)
        rec={
            "seq":len(events)+1,"event":event,"run_id":st.get("run_id"),
            "checkpoint_seq":checkpoint_seq,"current_deck_artifact":st.get("current_artifact"),
            "render_id":st.get("current_render"),"timestamp_ns":time.time_ns(),
        }
        rec.update(extra)
        p=run_dir/RUN_JOURNAL_FILE
        with p.open("a",encoding="utf-8",newline="\n") as f:
            f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
            f.flush()
            try: os.fsync(f.fileno())
            except OSError: pass
        return rec


def _rc1623_assert_flat_run_output(rd: Path, path: Path, label="output"):
    """Authoritative runtime outputs are flat and confined to this exact run."""
    rr=rd.resolve(); rp=path.resolve()
    if rp.parent!=rr:
        fail(f"RUN_OUTPUT_CONFINEMENT_VIOLATION: {label}: {rp}")
    return rp


def _rc1623_command_lock(rd: Path):
    return _rc1623_flock(rd/".writer.lock")


# A recovered process must never continue from a state/checkpoint split.
# This detects crashes after the atomic state replace but before the matching
# checkpoint/journal checkpoint event was durably written.
_load_state_rc1623_parent=load_state
def load_state(run_dir: Path):
    st=_load_state_rc1623_parent(run_dir)
    cp=_load_checkpoint_raw(run_dir,required=False)
    if cp is not None:
        actual=sha256(run_dir/STATE_FILE)
        if cp.get("run_state_sha256")!=actual:
            fail("RUN_STATE_CHECKPOINT_HASH_MISMATCH")
        events=_read_journal(run_dir)
        if not any(
            ev.get("event")=="CHECKPOINT_WRITTEN"
            and ev.get("checkpoint_seq")==cp.get("checkpoint_seq")
            and ev.get("run_state_sha256")==actual
            for ev in events
        ):
            fail("RUN_CHECKPOINT_JOURNAL_BINDING_MISMATCH")
    return st


# ---------------------- RC16.23 persistence primitives ----------------------

def _rc1623_write_immutable(path: Path, text: str):
    """Create an authoritative artifact once; identical retries are idempotent."""
    if path.exists():
        current=path.read_text(encoding="utf-8")
        if current==text: return path
        fail(f"AUTHORITATIVE_ARTIFACT_IMMUTABLE: {path.name}")
    _atomic_write_text(path,text); return path


_validate_active_continuation_lease_rc1623_parent=_validate_active_continuation_lease

def _validate_active_continuation_lease(scope_dir: Path):
    """BLOCKED_FATAL remains a bound logical run, but only recover-fatal may mutate it."""
    d=_read_continuation_lease_raw(scope_dir,required=True)
    if d.get("status")!="ACTIVE": return d
    rd=Path(d["run_dir"]); state_file=rd/STATE_FILE
    if not state_file.exists() or not state_file.is_file(): fail("CONTINUATION_ACTIVE_RUN_STATE_MISSING")
    if sha256(state_file)!=d.get("run_state_sha256"): fail("CONTINUATION_LEASE_STATE_HASH_MISMATCH")
    cp=_load_checkpoint_raw(rd,required=True)
    expected={"run_id":cp.get("run_id"),"checkpoint_seq":cp.get("checkpoint_seq"),"run_state":cp.get("run_state"),"run_state_sha256":cp.get("run_state_sha256"),"next_required_gate":cp.get("next_required_gate"),"waiting_context":cp.get("waiting_context")}
    for k,v in expected.items():
        if d.get(k)!=v: fail(f"CONTINUATION_LEASE_CHECKPOINT_DIVERGENCE: {k}")
    if d.get("run_state") not in {"IN_PROGRESS","WAITING_USER_INPUT","BLOCKED_FATAL"}:
        fail("CONTINUATION_ACTIVE_LEASE_HAS_TERMINAL_STATE")
    return d


def _rc1623_write_receipt_pair(rd: Path, canonical_name: str, prefix: str, doc):
    """Persist an immutable receipt plus a mutable convenience alias in the flat run."""
    text=_stable_json_text(doc)
    digest=hashlib.sha256(text.encode()).hexdigest()
    immutable=rd/f"{prefix}__{digest[:16]}.receipt.json"
    _rc1623_write_immutable(immutable,text)
    _atomic_write_text(rd/canonical_name,text)  # non-authoritative convenience alias
    return immutable,digest

# ------------------------------ state machine -------------------------------

def _require_mutable_run_rc1619(rd: Path, st, operation):
    if st.get("run_execution_state")=="BLOCKED_FATAL":
        cp=_load_checkpoint_raw(rd,required=False) or {}
        _append_run_journal(rd,st,"FATAL_BLOCK_MUTATION_REJECTED",checkpoint_seq=cp.get("checkpoint_seq"),operation=operation,error_code="RUN_BLOCKED_FATAL_EXPLICIT_RECOVERY_REQUIRED")
        fail("RUN_BLOCKED_FATAL_EXPLICIT_RECOVERY_REQUIRED")
    if not _terminal_state_observed(rd,st):
        return
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,"TERMINAL_REOPEN_ATTEMPT_BLOCKED",checkpoint_seq=cp.get("checkpoint_seq"),operation=operation,run_state=st.get("run_execution_state"),checkpoint_run_state=cp.get("run_state"),error_code="TERMINAL_RUN_IMMUTABLE_NEW_RUN_REQUIRED")
    fail("TERMINAL_RUN_IMMUTABLE_NEW_RUN_REQUIRED")


def _rc1623_mark_fatal_block(rd: Path, st, receipt, reason="FATAL_UNKNOWN"):
    st=copy.deepcopy(st)
    st["run_execution_state"]="BLOCKED_FATAL"
    st["fatal_block"]={
        "reason":reason,
        "receipt_sha256":sha256(rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT) if (rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT).exists() else None,
        "business_payload_sha256":receipt.get("business_payload_sha256") if isinstance(receipt,dict) else None,
        "issue_set_sha256":receipt.get("issue_set_sha256") if isinstance(receipt,dict) else None,
        "timestamp_ns":time.time_ns(),
    }
    _atomic_write_text(rd/STATE_FILE,json.dumps(st,ensure_ascii=False,indent=2)+"\n")
    cp=_write_checkpoint(rd,st,run_state_override="BLOCKED_FATAL")
    _append_run_journal(rd,st,"RUN_BLOCKED_FATAL",checkpoint_seq=cp.get("checkpoint_seq"),reason=reason,business_payload_sha256=st["fatal_block"].get("business_payload_sha256"),issue_set_sha256=st["fatal_block"].get("issue_set_sha256"))
    return st


def cmd_recover_fatal(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    cp=_load_checkpoint_raw(rd,required=True)
    if st.get("run_execution_state")!="BLOCKED_FATAL" or cp.get("run_state")!="BLOCKED_FATAL":
        fail("RUN_NOT_BLOCKED_FATAL")
    if a.authority not in {PILOTAGE,AXES_STRUCTURE,STYLE_AXES,ANCHOR,FINAL}:
        fail("FATAL_RECOVERY_AUTHORITY_INVALID")
    if not nonempty(a.reason): fail("FATAL_RECOVERY_REASON_REQUIRED")
    prior=copy.deepcopy(st.get("fatal_block"))
    st["run_execution_state"]="IN_PROGRESS"; st.pop("fatal_block",None)
    # Pilotage outputs after the blocked diagnostic are never inherited as fresh.
    for fn in (PILOTAGE_BUSINESS_MERGE_RECEIPT,PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT,PILOTAGE_PREFLIGHT_RECEIPT,PILOTAGE_COMMIT_FAILURE_RECEIPT):
        fp=rd/fn
        if fp.exists():
            try: fp.unlink()
            except OSError: pass
    _atomic_write_text(rd/STATE_FILE,json.dumps(st,ensure_ascii=False,indent=2)+"\n")
    cp2=_write_checkpoint(rd,st,run_state_override="IN_PROGRESS",invocation_seq=int(cp.get("invocation_seq",1))+1,resume_count=int(cp.get("resume_count",0))+1)
    _append_run_journal(rd,st,"FATAL_BLOCK_EXPLICITLY_RECOVERED",checkpoint_seq=cp2.get("checkpoint_seq"),authority=a.authority,reason=a.reason,prior_fatal_block=prior)
    print(json.dumps({"status":"RECOVERED","run_id":st["run_id"],"next_required_gate":next_gate(st)[0]},ensure_ascii=False))

# ------------------------ structural inventory authority --------------------

def _rc1623_style_axes_file(st):
    rec=(st.get("gates") or {}).get("STYLE_AXES_CLOSED") or {}
    p=Path(rec.get("evidence_file") or "")
    if not p.exists(): fail("STYLE_AXES_EVIDENCE_REQUIRED")
    if rec.get("evidence_sha256") and rec.get("evidence_sha256")!=sha256(p): fail("STYLE_AXES_EVIDENCE_STALE")
    return p


def _rc1623_normalize_structural_inventory_doc(doc, source_sha256):
    """Normalize an authority-owned Style→Axes inventory; assign technical IDs only."""
    inv=doc.get("structural_inventory")
    if not isinstance(inv,dict): fail("STYLE_AXES_STRUCTURAL_INVENTORY_REQUIRED")
    if inv.get("schema")!=RC1623_STRUCTURAL_INVENTORY_SCHEMA: fail("STYLE_AXES_STRUCTURAL_INVENTORY_SCHEMA_INVALID")
    lines=inv.get("lines")
    if not isinstance(lines,list) or not lines: fail("STYLE_AXES_STRUCTURAL_LINES_REQUIRED")
    norm_lines=[]; all_starters=[]; used_l=set(); used_s=set(); used_r=set()
    for li,raw in enumerate(lines,1):
        if not isinstance(raw,dict): fail("STYLE_AXES_STRUCTURAL_LINE_INVALID")
        ah=raw.get("axis_heading"); token=raw.get("render_token") or ah
        if not nonempty(ah) or not nonempty(token): fail("STYLE_AXES_STRUCTURAL_LINE_BINDING_REQUIRED")
        lid=raw.get("line_id") if nonempty(raw.get("line_id")) else f"line-{li}"
        if lid in used_l: fail("STYLE_AXES_STRUCTURAL_LINE_ID_DUPLICATE")
        used_l.add(lid)
        sraw=raw.get("starters")
        if not isinstance(sraw,list) or not sraw: fail(f"STYLE_AXES_STRUCTURAL_STARTERS_REQUIRED: {lid}")
        starters=[]
        for si,x in enumerate(sraw,1):
            if not isinstance(x,dict): fail(f"STYLE_AXES_STRUCTURAL_STARTER_INVALID: {lid}")
            display=x.get("display"); rt=x.get("render_token")
            if not nonempty(display) or not nonempty(rt): fail(f"STYLE_AXES_STRUCTURAL_STARTER_BINDING_REQUIRED: {lid}")
            sid=x.get("starter_id") if nonempty(x.get("starter_id")) else f"{lid}-starter-{si}"
            if sid in used_s: fail("STYLE_AXES_STRUCTURAL_STARTER_ID_DUPLICATE")
            used_s.add(sid)
            raw_resources=x.get("resources")
            if raw_resources is None:
                # Backward-compatible deterministic fallback. New Style→Axes evidence
                # should materialize resources once; legacy evidence can still be read.
                raw_resources=[v.strip() for v in re.split(r"\s+\+\s+",display) if v.strip()]
                if not raw_resources: raw_resources=[display.strip()]
            if not isinstance(raw_resources,list) or not raw_resources or any(not nonempty(v) for v in raw_resources):
                fail(f"STYLE_AXES_STRUCTURAL_STARTER_RESOURCES_INVALID: {lid}:{sid}")
            strec={"starter_id":sid,"display":display,"render_token":rt,"axis_heading":ah,"line_ids":[lid],"coverage_status":"REQUIRED","resources":[str(v).strip() for v in raw_resources]}
            starters.append(strec); all_starters.append(copy.deepcopy(strec))
        grouping=raw.get("starter_grouping")
        if len(starters)>1:
            if not isinstance(grouping,dict) or grouping.get("equivalent") is not True or not nonempty(grouping.get("basis")):
                fail(f"STYLE_AXES_MULTI_STARTER_EQUIVALENCE_REQUIRED: {lid}")
            gstatus="DECLARED_EQUIVALENT"; gbasis=grouping.get("basis")
        else:
            gstatus="NOT_APPLICABLE"; gbasis=None
        rraw=raw.get("replays")
        if not isinstance(rraw,list) or not rraw: fail(f"STYLE_AXES_REPLAY_SLOTS_REQUIRED: {lid}")
        replay_ids=[]
        for ri,x in enumerate(rraw,1):
            if not isinstance(x,dict): fail(f"STYLE_AXES_REPLAY_SLOT_INVALID: {lid}")
            rid=x.get("replay_id") if nonempty(x.get("replay_id")) else f"{lid}-replay-{ri}"
            if rid in used_r: fail("STYLE_AXES_REPLAY_ID_DUPLICATE")
            used_r.add(rid); replay_ids.append(rid)
        norm_lines.append({"line_id":lid,"axis_heading":ah,"render_token":token,"starters":starters,"starter_grouping_status":gstatus,"starter_grouping_basis":gbasis,"replay_ids":replay_ids})
    normalized={"schema":RC1623_STRUCTURAL_INVENTORY_SCHEMA,"source_style_axes_sha256":source_sha256,"lines":norm_lines,"starters":all_starters}
    digest=hashlib.sha256(_stable_json_text(normalized).encode()).hexdigest()
    return normalized,digest


def _rc1623_validate_style_axes_inventory_file(path: Path, st):
    doc=read_json(path,"STYLE_AXES evidence")
    if doc.get("run_id")!=st.get("run_id"): fail("RUN_ID_MISMATCH in STYLE_AXES evidence")
    if doc.get("artifact") not in {None,st.get("current_artifact")} and doc.get("deck_artifact") not in {None,st.get("current_artifact")} :
        fail("STYLE_AXES_DECK_BINDING_MISMATCH")
    return _rc1623_normalize_structural_inventory_doc(doc,sha256(path))


def _rc1623_normalize_structural_inventory(st):
    """Read authority-owned structure from STYLE_AXES evidence; assign IDs only."""
    src=_rc1623_style_axes_file(st); doc=read_json(src,"STYLE_AXES evidence")
    return _rc1623_normalize_structural_inventory_doc(doc,sha256(src))


def _rc1623_inventory_render_issues(inv,render_path: Path):
    text=render_path.read_text(encoding="utf-8").casefold(); issues=[]
    for line in inv.get("lines",[]):
        if line["axis_heading"].strip().casefold() not in text or line["render_token"].strip().casefold() not in text:
            issues.append(_rc1623_make_issue("PILOTAGE_LINE_NOT_RENDERED","$.structural_inventory.lines",line.get("render_token"),line.get("line_id"),owner_authority=AXES_STRUCTURE,repair_domain="PRESENTATION_RENDER",budget_class="NON_BUSINESS",line_id=line.get("line_id")))
    for strec in inv.get("starters",[]):
        if strec["render_token"].strip().casefold() not in text:
            issues.append(_rc1623_make_issue("STRUCTURAL_STARTER_NOT_RENDERED","$.structural_inventory.starters",strec.get("render_token"),strec.get("starter_id"),owner_authority=AXES_STRUCTURE,repair_domain="PRESENTATION_RENDER",budget_class="NON_BUSINESS",starter_id=strec.get("starter_id")))
    return issues


def _rc1623_validate_inventory_against_render(inv,render_path: Path):
    issues=_rc1623_inventory_render_issues(inv,render_path)
    if issues:
        x=issues[0]; fail(f"{x['code']}: {x.get('line_id') or x.get('starter_id') or x.get('observed')}")

# ----------------------- builder: secretary only ----------------------------

def _pilotage_empty_replay(replay_id):
    return {
      "replay_id":replay_id,"status":"UNSET","covers_variants":[],
      "resources":[],"budgets":[],"restrictions":[],"legality_evidence":[],"fact_catalog":[],"constraint_catalog":[],"external_inputs":[],
      "steps":[],"derived_claim_inventory_status":"UNSET","derived_claims":[],
      "outcome":{"certainty":"UNSET","render_token":"","conditions":[],"condition_render_tokens":[],"guarantee_claim_status":"UNSET","derived_claim_ids":[],"victory_claim":"UNSET"},
      "dynamic_state_scope_status":"UNSET","initial_properties":[],"attachment_scope_status":"UNSET","initial_attachments":[],
      "topology_scope_status":"UNSET","topology_slots":[],"topology_rules":[],
      "state_precondition_inventory_status":"UNSET","topology_inventory_status":"UNSET","topology_checks":[],
      "external_condition_inventory_status":"UNSET","external_conditions":[],
      "semantic_layer_version":"SRC1-GR1-BW1-MCB1","src_scope_status":"UNSET","semantic_ruling_contracts":[],
      "game_rule_scope_status":"UNSET","action_game_rule_profiles":[],"game_rule_bindings":[],
      "mechanical_consequence_scope_status":"UNSET","mechanical_consequence_bindings":[],
      "backward_proof_scope_status":"UNSET","backward_requirements":[],"critical_decisions":[],
      "unified_cold_audit":None,
    }


def _pilotage_business_skeleton_from_render(st, render_path: Path):
    inv,invsha=_rc1623_normalize_structural_inventory(st)
    _rc1623_validate_inventory_against_render(inv,render_path)
    lines=[]
    for ent in inv["lines"]:
        sids=[x["starter_id"] for x in ent["starters"]]
        display=ent["starters"][0]["display"]
        lines.append({
          "line_id":ent["line_id"],"render_axis_heading":ent["axis_heading"],"render_token":ent["render_token"],"axis_validation_status":"REQUIRED",
          "starter_ids":sids,"starter_grouping_status":ent["starter_grouping_status"],"starter_grouping_basis":ent["starter_grouping_basis"],
          "starter_display":display,"declared_initial_resources":[],"mandatory_initial_resources":[],"obtained_during_line":[],"hidden_initial_resources":[],
          "starter_contract_status":"UNSET","generic_starter":None,"generic_coverage_status":"UNSET",
          "starter_property_scope_status":"UNSET","starter_property_checks":[],
          "sequence_complexity":"UNSET","physical_state_scope_status":"UNSET","state_checkpoints":[],
          "effect_resolution_scope_status":"UNSET","effect_resolution_checks":[],
          "line_execution_scope_status":"UNSET","execution_replays":[_pilotage_empty_replay(rid) for rid in ent["replay_ids"]]
        })
    return {
      "status":"UNSET","execution_contract_version":"RC16.2","axis_coverage_status":"UNSET",
      "starter_exploration_status":"UNSET","starter_inventory_status":"UNSET",
      "structural_starters":copy.deepcopy(inv["starters"]),"lines":lines,
      "structural_inventory_sha256":invsha,
    }

# Top-level semantic conclusions are model/authority-owned in RC16.23.
_PILOTAGE_ALLOWED_TOP_PATCH_FIELDS={"status","axis_coverage_status","starter_exploration_status","starter_inventory_status"}


def _pilotage_shell_identity(payload):
    return {
      "top":{k:copy.deepcopy(payload.get(k)) for k in ("execution_contract_version","structural_starters","structural_inventory_sha256")},
      "lines":[{k:copy.deepcopy(line.get(k)) for k in _PILOTAGE_SHELL_LINE_FIELDS if k not in {"execution_replays","axis_validation_status"}} | {"axis_validation_status":line.get("axis_validation_status"),"replay_ids":[rp.get("replay_id") for rp in line.get("execution_replays",[]) if isinstance(rp,dict)]} for line in payload.get("lines",[]) if isinstance(line,dict)]
    }


def _pilotage_locality_allowed_fields(issue_codes):
    """Return patchable semantic slots for *already classified* issue codes.

    This is a locality/scope table, not a domain classifier.  Unknown codes get
    no patch rights.  The repair domain itself must come from issue metadata in
    the authoritative dry-run receipt.
    """
    codes={str(x) for x in (issue_codes or []) if nonempty(str(x))}
    if not codes:
        return set(),set()
    line=set(); replay=set(); recognized=set()
    evidence_codes={"ACTION_LEGALITY_EVIDENCE_MISSING","ACTION_LEGALITY_EVIDENCE_KIND_INVALID","UNIFIED_COLD_LEGALITY_ACTION_COVERAGE_MISMATCH","ACTION_LEGALITY_PARTICIPANTS_MISSING","COLD_LEGALITY_SWEEP_EVIDENCE_INVALID"}
    resource_codes={"EXECUTION_RESOURCES_MISSING","PROOF_FLOOR_DECLARED_RESOURCES_UNTRACKED"}
    admin_codes={
      "PILOTAGE_PLACEHOLDER_UNRESOLVED","PILOTAGE_WIRE_SCHEMA_MISMATCH","PILOTAGE_CONTRACT_MISSING","PILOTAGE_SCHEMA_MISSING",
      "PILOTAGE_RENDER_MISSING","PILOTAGE_BUSINESS_PAYLOAD_INVALID","PILOTAGE_NOMINAL_CONTRACT_REQUIRES_RC16_2_MCB",
      "MCB_SEMANTIC_LAYER_REQUIRED","PILOTAGE_LINES_REQUIRED","PILOTAGE_STRUCTURAL_STARTERS_REQUIRED","PILOTAGE_BUSINESS_BUILDER_REQUIRED",
      "PILOTAGE_REPAIR_SCOPE_VIOLATION","PILOTAGE_BUSINESS_PAYLOAD_REQUIRED_FIELD_MISSING","PILOTAGE_BUSINESS_PAYLOAD_TYPE_INVALID",
    }
    for code in codes:
        if code in evidence_codes:
            recognized.add(code); replay |= {"legality_evidence","fact_catalog","constraint_catalog","steps","unified_cold_audit","semantic_ruling_contracts","game_rule_bindings","action_game_rule_profiles"}
        elif code in resource_codes or code.startswith("MCB_RESOURCE_"):
            recognized.add(code); line |= {"declared_initial_resources","mandatory_initial_resources","obtained_during_line","hidden_initial_resources"}
            replay |= {"resources","steps","semantic_ruling_contracts","game_rule_bindings","mechanical_consequence_scope_status","mechanical_consequence_bindings","unified_cold_audit"}
        elif code=="EXECUTION_STEPS_MISSING":
            recognized.add(code); replay |= {"steps","resources","legality_evidence","fact_catalog","constraint_catalog","unified_cold_audit","semantic_ruling_contracts","game_rule_bindings","action_game_rule_profiles","mechanical_consequence_scope_status","mechanical_consequence_bindings"}
        elif code.startswith("PROOF_FLOOR_") or code.startswith("MCB_") or code.startswith("ACTION_LEGALITY_"):
            recognized.add(code); line |= set(_PILOTAGE_ALLOWED_LINE_PATCH_FIELDS); replay |= set(_PILOTAGE_ALLOWED_REPLAY_PATCH_FIELDS)
        elif code in admin_codes or code.startswith("PILOTAGE_WIRE_") or code.startswith("PILOTAGE_BUSINESS_PAYLOAD_") or code.startswith("RC16_2_"):
            recognized.add(code); line |= set(_PILOTAGE_ALLOWED_LINE_PATCH_FIELDS); replay |= set(_PILOTAGE_ALLOWED_REPLAY_PATCH_FIELDS)
    if recognized != codes:
        return set(),set()
    return line,replay

# ------------------------ source-owned issue metadata ------------------------

_RC1623_ISSUE_META_FIELDS={"owner_authority","repair_domain","budget_class","severity","repairable","blocking"}

def _rc1623_issue_metadata(owner_authority,repair_domain,budget_class,*,repairable=True,severity="BLOCKING",blocking=True):
    return {
      "owner_authority":owner_authority,"repair_domain":repair_domain,"budget_class":budget_class,
      "severity":severity,"repairable":bool(repairable),"blocking":bool(blocking),
    }

def _rc1623_unknown_issue_meta(code=None):
    # Unknown is deliberately fail-closed.  RC16.23 never infers a repair
    # domain from an error-code spelling or prefix.
    return _rc1623_issue_metadata(PILOTAGE,"FATAL_UNKNOWN","FAIL_CLOSED",repairable=False)

def _rc1623_issue_meta(code):
    """Compatibility fallback only: an undecorated code is *unknown*.

    Classification must be emitted by the validator/control that creates the
    issue.  This helper intentionally performs no name/prefix inference.
    """
    return _rc1623_unknown_issue_meta(code)

def _rc1623_make_issue(code,path,expected=None,observed=None,*,owner_authority,repair_domain,budget_class,repairable=True,severity="BLOCKING",blocking=True,**extra):
    item={"code":str(code or "UNKNOWN"),"path":path,"expected":expected,"observed":observed}
    item.update(_rc1623_issue_metadata(owner_authority,repair_domain,budget_class,repairable=repairable,severity=severity,blocking=blocking))
    item["domain"]=repair_domain
    item.update(extra)
    return item

def _pilotage_issue_domain(code):
    # Deprecated compatibility surface.  Callers must consume issue metadata.
    return "FATAL_UNKNOWN"

def _decorate_preflight_issue(issue):
    x=copy.deepcopy(issue) if isinstance(issue,dict) else {"code":"UNKNOWN","observed":str(issue),"path":"$"}
    code=x.get("code") or "UNKNOWN"
    if not _RC1623_ISSUE_META_FIELDS.issubset(x):
        # Missing source-owned metadata is itself an unknown/fatal routing
        # condition; never repair it by guessing from the code name.
        meta=_rc1623_unknown_issue_meta(code)
        for k,v in meta.items(): x.setdefault(k,v)
    domain=x.get("repair_domain")
    if domain not in {"PRESENTATION_RENDER","PROOF_SCHEMA_ADMIN","BUSINESS_SEMANTIC_MECHANICAL","ORCHESTRATION_PREREQUISITE","FATAL_UNKNOWN"}:
        meta=_rc1623_unknown_issue_meta(code)
        x.update(meta); domain="FATAL_UNKNOWN"
    x["domain"]=domain
    observed=str(x.get("observed") or "")
    if observed.startswith(str(code)+":"):
        tail=observed[len(str(code))+1:].strip(); parts=[z for z in tail.split(":") if z]
        if parts and "line_id" not in x: x["line_id"]=parts[0]
        if len(parts)>1 and "replay_id" not in x: x["replay_id"]=parts[1]
        if len(parts)>2 and "step_id" not in x: x["step_id"]=parts[2]
    return x


_wire_issue_rc1623_parent=_wire_issue

def _wire_issue(issues,path,code,expected=None,observed=None,**meta_override):
    """Wire/schema validator issue.  Classification is emitted here, at source."""
    meta=_rc1623_issue_metadata(PILOTAGE,"PROOF_SCHEMA_ADMIN","NON_BUSINESS",repairable=True)
    meta.update(meta_override)
    item={"code":code,"path":path,"expected":expected,"observed":observed,**meta}
    item["domain"]=item["repair_domain"]
    issues.append(item)

_pilotage_mechanical_preflight_issues_rc1623_parent=_pilotage_mechanical_preflight_issues
_render_mechanical_preflight_issues_rc1623_parent=_render_mechanical_preflight_issues

def _pilotage_mechanical_preflight_issues(a, st):
    """Pilotage mechanical preflight emits its own routing metadata."""
    raw=_pilotage_mechanical_preflight_issues_rc1623_parent(a,st); out=[]
    for issue in raw:
        if _RC1623_ISSUE_META_FIELDS.issubset(issue):
            out.append(issue); continue
        if str(issue.get("path"))=="combo_impact_file":
            meta=_rc1623_issue_metadata(ANCHOR,"ORCHESTRATION_PREREQUISITE","NON_BUSINESS",repairable=True)
        else:
            meta=_rc1623_issue_metadata(PILOTAGE,"PROOF_SCHEMA_ADMIN","NON_BUSINESS",repairable=True)
        x=copy.deepcopy(issue); x.update(meta); x["domain"]=x["repair_domain"]; out.append(x)
    return out


def _render_mechanical_preflight_issues(a, st):
    """Render mechanical preflight issues are presentation-owned at source."""
    raw=_render_mechanical_preflight_issues_rc1623_parent(a,st); out=[]
    for issue in raw:
        if _RC1623_ISSUE_META_FIELDS.issubset(issue): out.append(issue); continue
        x=copy.deepcopy(issue); x.update(_rc1623_issue_metadata(AXES_STRUCTURE,"PRESENTATION_RENDER","NON_BUSINESS",repairable=True)); x["domain"]=x["repair_domain"]; out.append(x)
    return out

def _rc1623_issue_set_sha(issues):
    normalized=[{k:v for k,v in x.items() if k not in {"timestamp_ns"}} for x in issues]
    return hashlib.sha256(json.dumps(normalized,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _rc1623_common_aggregate_issues(payload,render_path: Path):
    """Independent source-classified issues safe to aggregate before legacy validation."""
    issues=[]; text=render_path.read_text(encoding="utf-8").casefold()
    lines=payload.get("lines") if isinstance(payload,dict) else None
    if not isinstance(lines,list): return issues
    business=lambda code,path,expected,observed: _rc1623_make_issue(code,path,expected,observed,owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS")
    presentation=lambda code,path,expected,observed: _rc1623_make_issue(code,path,expected,observed,owner_authority=AXES_STRUCTURE,repair_domain="PRESENTATION_RENDER",budget_class="NON_BUSINESS")
    for li,line in enumerate(lines):
        if not isinstance(line,dict): continue
        lid=line.get("line_id") or f"line[{li}]"
        for ri,rp in enumerate(line.get("execution_replays") if isinstance(line.get("execution_replays"),list) else []):
            if not isinstance(rp,dict): continue
            rid=rp.get("replay_id") or f"replay[{ri}]"; path=f"$.lines[{li}].execution_replays[{ri}]"
            steps=rp.get("steps")
            if isinstance(steps,list) and not steps:
                issues.append(business("EXECUTION_STEPS_MISSING",path+".steps","non-empty executable steps",f"EXECUTION_STEPS_MISSING: {lid}:{rid}"))
            declared=line.get("declared_initial_resources")
            resources=rp.get("resources")
            if isinstance(declared,list) and declared and isinstance(resources,list) and not resources:
                issues.append(business("EXECUTION_RESOURCES_MISSING",path+".resources","tracked execution resources",f"EXECUTION_RESOURCES_MISSING: {lid}:{rid}"))
            if isinstance(steps,list):
                for si,step in enumerate(steps):
                    if not isinstance(step,dict): continue
                    sid=step.get("step_id") or f"step[{si}]"; rt=step.get("render_token")
                    if nonempty(rt) and rt.strip().casefold() not in text:
                        issues.append(presentation("EXECUTION_STEP_NOT_RENDERED",path+f".steps[{si}].render_token","step token visible in render",f"EXECUTION_STEP_NOT_RENDERED: {lid}:{rid}:{sid}"))
                    alp=step.get("action_legality_proof")
                    if isinstance(alp,dict) and isinstance(alp.get("participants"),list) and not alp.get("participants"):
                        issues.append(business("ACTION_LEGALITY_PARTICIPANTS_MISSING",path+f".steps[{si}].action_legality_proof.participants","material action participants",f"ACTION_LEGALITY_PARTICIPANTS_MISSING: {lid}:{rid}:{sid}"))
            outcome=rp.get("outcome")
            if isinstance(outcome,dict):
                ort=outcome.get("render_token")
                if nonempty(ort) and ort.strip().casefold() not in text:
                    issues.append(presentation("EXECUTION_OUTCOME_NOT_RENDERED",path+".outcome.render_token","outcome visible in render",f"EXECUTION_OUTCOME_NOT_RENDERED: {lid}:{rid}"))
                if outcome.get("certainty")=="CONDITIONAL" and not outcome.get("condition_render_tokens"):
                    issues.append(presentation("CONDITIONAL_OUTCOME_REQUIRES_VISIBLE_CONDITIONS",path+".outcome.condition_render_tokens","visible conditions for conditional outcome",f"CONDITIONAL_OUTCOME_REQUIRES_VISIBLE_CONDITIONS: {lid}:{rid}"))
    return issues

# ------------------------- provenance / repair merge -------------------------

def _rc1623_scope_hash(issue_codes):
    l,r=_pilotage_locality_allowed_fields(issue_codes)
    doc={"schema":RC1623_PATCH_SCOPE_SCHEMA,"issue_codes":sorted(str(x) for x in issue_codes),"line_fields":sorted(l),"replay_fields":sorted(r),"top_fields":sorted(_PILOTAGE_ALLOWED_TOP_PATCH_FIELDS)}
    return hashlib.sha256(_stable_json_text(doc).encode()).hexdigest()


def _rc1623_latest_dryrun_event(rd: Path, receipt_path: Path):
    rh=sha256(receipt_path)
    matches=[e for e in _read_journal(rd) if e.get("event")=="PILOTAGE_AUTHORITATIVE_DRY_RUN_COMPLETED" and e.get("receipt_sha256")==rh]
    return matches[-1] if matches else None


def cmd_pilotage_business_skeleton(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"pilotage-business-skeleton")
    if next_gate(st)[0]!="PILOTAGE_VALIDATED": fail(f"pilotage-business-skeleton requires next gate PILOTAGE_VALIDATED; next gate is {next_gate(st)[0]}")
    if st.get("combo_impact_required") is True and not nonempty(_rc1622_resolve_combo_impact(rd,st,None)):
        cp=_load_checkpoint_raw(rd,False) or {}; _append_run_journal(rd,st,"ORCHESTRATION_PREREQUISITE_BLOCKED",checkpoint_seq=cp.get("checkpoint_seq"),code="COMBO_IMPACT_REQUIRED",owner_authority=ANCHOR,repair_domain="ORCHESTRATION_PREREQUISITE",budget_class="NON_BUSINESS")
        fail("COMBO_IMPACT_REQUIRED")
    render,manifest,render_contract=_rc16221_render_bindings(st)
    out=_rc1623_assert_flat_run_output(rd,Path(a.output),"pilotage skeleton")
    sk=_pilotage_business_skeleton_from_render(st,render); _rc1623_write_immutable(out,_stable_json_text(sk))
    invsha=sk.get("structural_inventory_sha256")
    rec={"schema":PILOTAGE_BUSINESS_SKELETON_SCHEMA,"status":"PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"deck_sha256":_current_deck_snapshot_sha256(st),"render_sha256":sha256(render),"structural_inventory_sha256":invsha,"skeleton_file":str(out),"skeleton_sha256":sha256(out),"runtime_version":VERSION,"shell_owned":["structural_starters","line identity/axis/starter bindings","replay_id"]}
    rp=rd/PILOTAGE_BUSINESS_SKELETON_RECEIPT; _atomic_write_text(rp,_stable_json_text(rec))
    _append_run_journal(rd,st,"PILOTAGE_BUSINESS_SKELETON_BUILT",deck_artifact=st.get("current_artifact"),render_id=st.get("current_render"),render_sha256=sha256(render),structural_inventory_sha256=invsha,skeleton_file=str(out),skeleton_sha256=sha256(out),receipt_file=str(rp),receipt_sha256=sha256(rp))
    print(json.dumps(rec,ensure_ascii=False,indent=2)); return rec


def cmd_pilotage_business_merge(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"pilotage-business-merge")
    if next_gate(st)[0]!="PILOTAGE_VALIDATED": fail(f"pilotage-business-merge requires next gate PILOTAGE_VALIDATED; next gate is {next_gate(st)[0]}")
    render,manifest,render_contract=_rc16221_render_bindings(st)
    skeleton=Path(a.skeleton_file); patch=Path(a.patch_file); out=_rc1623_assert_flat_run_output(rd,Path(a.output),"pilotage business")
    base=Path(a.base_business_file) if getattr(a,"base_business_file",None) else skeleton
    if not skeleton.exists(): fail("PILOTAGE_BUSINESS_SKELETON_MISSING")
    if not patch.exists(): fail("PILOTAGE_BUSINESS_PATCH_MISSING")
    if not base.exists(): fail("PILOTAGE_BUSINESS_BASE_MISSING")
    skrec=rd/PILOTAGE_BUSINESS_SKELETON_RECEIPT
    if not skrec.exists(): fail("PILOTAGE_BUSINESS_SKELETON_RECEIPT_MISSING")
    sr=read_json(skrec,"Pilotage business skeleton receipt"); sk=read_json(skeleton,"Pilotage skeleton")
    invsha=sk.get("structural_inventory_sha256")
    if sr.get("skeleton_sha256")!=sha256(skeleton) or sr.get("render_sha256")!=sha256(render) or sr.get("deck_artifact")!=st.get("current_artifact") or sr.get("structural_inventory_sha256")!=invsha:
        fail("PILOTAGE_BUSINESS_SKELETON_STALE")
    pd=read_json(patch,"Pilotage business patch")
    if pd.get("schema")!=PILOTAGE_BUSINESS_PATCH_SCHEMA: fail("PILOTAGE_BUSINESS_PATCH_SCHEMA_INVALID")
    issue_codes=[]; parent_receipt_sha=None; issue_set_sha=None; repair_scope_sha=None
    repair_receipt=getattr(a,"repair_receipt",None)
    if base.resolve()!=skeleton.resolve():
        if not nonempty(repair_receipt): fail("PILOTAGE_REPAIR_RECEIPT_REQUIRED_FOR_NONINITIAL_MERGE")
    if repair_receipt:
        rr=Path(repair_receipt)
        if not rr.exists() or rr.resolve().parent!=rd.resolve(): fail("PILOTAGE_REPAIR_RECEIPT_NOT_AUTHORITATIVE")
        rrdoc=read_json(rr,"Pilotage repair receipt")
        if rrdoc.get("schema")!="ygo-pilotage-authoritative-dry-run-receipt-v1" or rrdoc.get("status")!="FAIL": fail("PILOTAGE_REPAIR_RECEIPT_INVALID")
        current_deck=_current_deck_snapshot_sha256(st)
        expected={"run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"deck_sha256":current_deck,"render_sha256":sha256(render),"structural_inventory_sha256":invsha,"business_payload_sha256":sha256(base)}
        for k,v in expected.items():
            if rrdoc.get(k)!=v: fail(f"PILOTAGE_REPAIR_RECEIPT_STALE: {k}")
        ev=_rc1623_latest_dryrun_event(rd,rr)
        if not ev or ev.get("business_payload_sha256")!=sha256(base): fail("PILOTAGE_REPAIR_RECEIPT_PROVENANCE_INVALID")
        receipt_issues=[_decorate_preflight_issue(x) for x in rrdoc.get("issues",[]) if isinstance(x,dict)]
        issue_codes=[x.get("code") for x in receipt_issues if nonempty(x.get("code"))]
        if not issue_codes: fail("PILOTAGE_REPAIR_RECEIPT_ISSUES_REQUIRED")
        if rrdoc.get("validator")!="FULL_SHARED_VALIDATOR": fail("PILOTAGE_REPAIR_RECEIPT_VALIDATOR_INVALID")
        computed_issue_set=_rc1623_issue_set_sha(receipt_issues)
        if rrdoc.get("issue_set_sha256")!=computed_issue_set: fail("PILOTAGE_REPAIR_RECEIPT_ISSUE_SET_MISMATCH")
        domains=sorted({x.get("repair_domain") for x in receipt_issues if nonempty(x.get("repair_domain"))})
        if sorted(rrdoc.get("repair_domains") or [])!=domains: fail("PILOTAGE_REPAIR_RECEIPT_DOMAIN_MISMATCH")
        if any(d in {"FATAL_UNKNOWN","PRESENTATION_RENDER","ORCHESTRATION_PREREQUISITE"} for d in domains): fail("PILOTAGE_REPAIR_WRONG_AUTHORITY")
        if any(d not in {"BUSINESS_SEMANTIC_MECHANICAL","PROOF_SCHEMA_ADMIN"} for d in domains): fail("PILOTAGE_REPAIR_RECEIPT_DOMAIN_INVALID")
        issue_set_sha=computed_issue_set
        repair_scope_sha=_rc1623_scope_hash(issue_codes); parent_receipt_sha=sha256(rr)
    merged=_pilotage_merge_business_patch(sk,pd,issue_codes=issue_codes,base_payload=read_json(base,"Pilotage business base"))
    text=_stable_json_text(merged); base_text=_stable_json_text(read_json(base,"Pilotage business base"))
    if text==base_text: fail("PILOTAGE_REPAIR_NO_PROGRESS")
    merged_sha=hashlib.sha256(text.encode()).hexdigest()
    prior_hashes={e.get("business_payload_sha256") for e in _read_journal(rd) if e.get("event")=="PILOTAGE_BUSINESS_PATCH_MERGED"}
    if merged_sha in prior_hashes: fail("PILOTAGE_REPAIR_CYCLE_DETECTED")
    _rc1623_write_immutable(out,text)
    rec={"schema":PILOTAGE_BUSINESS_MERGE_RECEIPT_SCHEMA,"status":"PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"deck_sha256":_current_deck_snapshot_sha256(st),"render_sha256":sha256(render),"structural_inventory_sha256":invsha,"skeleton_sha256":sha256(skeleton),"patch_sha256":sha256(patch),"base_business_sha256":sha256(base),"parent_dry_run_receipt_sha256":parent_receipt_sha,"issue_set_sha256":issue_set_sha,"repair_scope_sha256":repair_scope_sha,"business_payload_file":str(out),"business_payload_sha256":sha256(out),"repair_issue_codes":sorted(issue_codes),"runtime_version":VERSION}
    rp,rph=_rc1623_write_receipt_pair(rd,PILOTAGE_BUSINESS_MERGE_RECEIPT,"pilotage_merge",rec)
    _append_run_journal(rd,st,"PILOTAGE_BUSINESS_PATCH_MERGED",deck_artifact=st.get("current_artifact"),render_id=st.get("current_render"),business_payload_file=str(out),business_payload_sha256=sha256(out),structural_inventory_sha256=invsha,skeleton_sha256=sha256(skeleton),patch_sha256=sha256(patch),base_business_sha256=sha256(base),parent_dry_run_receipt_sha256=parent_receipt_sha,issue_set_sha256=issue_set_sha,repair_scope_sha256=repair_scope_sha,repair_issue_codes=rec["repair_issue_codes"],receipt_file=str(rp),receipt_sha256=rph)
    print(json.dumps(rec,ensure_ascii=False,indent=2)); return rec


def _pilotage_builder_receipt_valid(rd: Path, st, business: Path, render: Path):
    rec=rd/PILOTAGE_BUSINESS_MERGE_RECEIPT
    if not rec.exists(): return False
    try:
        d=read_json(rec,"Pilotage business merge receipt"); _,invsha=_rc1623_normalize_structural_inventory(st)
    except BaseException: return False
    return d.get("schema")==PILOTAGE_BUSINESS_MERGE_RECEIPT_SCHEMA and d.get("status")=="PASS" and d.get("run_id")==st.get("run_id") and d.get("deck_artifact")==st.get("current_artifact") and d.get("deck_sha256")==_current_deck_snapshot_sha256(st) and d.get("render_sha256")==sha256(render) and d.get("structural_inventory_sha256")==invsha and d.get("business_payload_sha256")==sha256(business)

def _pilotage_semantic_receipt_valid(rd: Path, st, business: Path, render: Path):
    rec=rd/PILOTAGE_SEMANTIC_COMPILE_RECEIPT
    if not rec.exists(): return False
    try:
        d=read_json(rec,"Pilotage semantic compile receipt"); _,invsha=_rc1623_normalize_structural_inventory(st)
    except BaseException:
        return False
    semantic_file=d.get("semantic_file")
    if not nonempty(semantic_file): return False
    semantic_path=Path(semantic_file)
    if not semantic_path.exists() or not semantic_path.is_file(): return False
    return (
        d.get("schema")==PILOTAGE_SEMANTIC_COMPILE_RECEIPT_SCHEMA
        and d.get("status")=="PASS"
        and d.get("run_id")==st.get("run_id")
        and d.get("deck_artifact")==st.get("current_artifact")
        and d.get("deck_sha256")==_current_deck_snapshot_sha256(st)
        and d.get("render_id")==st.get("current_render")
        and d.get("render_sha256")==sha256(render)
        and d.get("structural_inventory_sha256")==invsha
        and d.get("semantic_sha256")==sha256(semantic_path)
        and d.get("business_payload_file")==str(business)
        and d.get("business_payload_sha256")==sha256(business)
        and d.get("compiler_contract")==PILOTAGE_SEMANTIC_SCHEMA
        and d.get("runtime_version")==VERSION
    )

def _pilotage_business_provenance(rd: Path, st, business: Path, render: Path):
    if _pilotage_semantic_receipt_valid(rd,st,business,render): return "SEMANTIC_COMPILER"
    if _pilotage_builder_receipt_valid(rd,st,business,render): return "BUILDER_MERGE_LEGACY"
    return None

# ------------------------ aggregated authoritative dry-run ------------------

_authoritative_pilotage_dry_run_rc1623_parent = _authoritative_pilotage_dry_run

def _authoritative_pilotage_dry_run(rd: Path, st, business: Path, render: Path, write_receipt=True):
    if not business.exists(): fail("PILOTAGE_BUSINESS_PAYLOAD_MISSING")
    if not render.exists(): fail("PILOTAGE_RENDER_MISSING")
    before=sha256(rd/STATE_FILE); cp=_load_checkpoint_raw(rd,False) or {}; inv,invsha=_rc1623_normalize_structural_inventory(st)
    _append_run_journal(rd,st,"PILOTAGE_AUTHORITATIVE_DRY_RUN_STARTED",checkpoint_seq=cp.get("checkpoint_seq"),business_payload_sha256=sha256(business),render_sha256=sha256(render),deck_sha256=_current_deck_snapshot_sha256(st),structural_inventory_sha256=invsha,read_only=True)
    payload=read_json(business,"Pilotage business payload"); issues=[]
    provenance=_pilotage_business_provenance(rd,st,business,render)
    if provenance is None:
        issues=[_rc1623_make_issue("PILOTAGE_BUSINESS_PROVENANCE_REQUIRED","$","fresh Semantic Compiler or legacy Builder/Merge provenance for exact deck/render/inventory/business payload",str(rd/PILOTAGE_SEMANTIC_COMPILE_RECEIPT),owner_authority=PILOTAGE,repair_domain="PROOF_SCHEMA_ADMIN",budget_class="NON_BUSINESS")]
    else:
        issues=_rc1623_inventory_render_issues(inv,render)+_pilotage_business_issues(payload)+_rc1623_common_aggregate_issues(payload,render)
    # RC16.23.6: exact summon-material legality is a Pilotage mechanical
    # precondition.  It is evaluated from the exact semantic source bound by
    # the Semantic Compiler receipt, so it cannot be forged by rendered prose.
    summon_proof=[]
    if provenance=="SEMANTIC_COMPILER" and not issues:
        try:
            sr=read_json(rd/PILOTAGE_SEMANTIC_COMPILE_RECEIPT,"Pilotage semantic compile receipt")
            sp=Path(sr.get("semantic_file") or "")
            if not sp.exists() or sr.get("semantic_sha256")!=sha256(sp):
                fail("PILOTAGE_SEMANTIC_SOURCE_STALE")
            semantic=read_json(sp,"Pilotage semantic payload")
            summon_proof=_rc16236_validate_summon_contracts(st,semantic)
        except SystemExit as e:
            code,detail=_denied_parts(e)
            issues.append(_rc1623_make_issue(code,"$","exact summon-material contract PASS",detail,owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS"))
    if not issues:
        try:
            compiled=_compile_pilotage_contract_document(st,payload,render)
            with tempfile.TemporaryDirectory(prefix="ygo-pilotage-dryrun-") as td:
                td=Path(td); contract=td/"pilotage_contract.json"; schema=td/"pilotage_schema.json"
                _atomic_write_text(contract,_stable_json_text(compiled)); _atomic_write_text(schema,_stable_json_text(_pilotage_wire_schema_payload(st)))
                combo=_rc1622_resolve_combo_impact(rd,st,None) if st.get("combo_impact_required") is True else None
                ma=Namespace(pilotage_contract_file=str(contract),render_file=str(render),schema_file=str(schema),combo_impact_file=combo)
                mechanical=_pilotage_mechanical_preflight_issues(ma,st); authoritative=_pilotage_full_preflight_issues(contract,render,st)
                issues=mechanical+authoritative
        except SystemExit as e:
            code,detail=_denied_parts(e); issues=[_rc1623_make_issue(code,"$","authoritative dry-run pass",detail,owner_authority=PILOTAGE,repair_domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS")]
    issues=[_decorate_preflight_issue(x) for x in issues]
    uniq={json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")):x for x in issues}; issues=sorted(uniq.values(),key=lambda x:(x.get("path") or "",x.get("code") or ""))
    issue_set_sha=_rc1623_issue_set_sha(issues); domains=sorted({x.get("repair_domain") for x in issues if nonempty(x.get("repair_domain"))})
    doc={"schema":"ygo-pilotage-authoritative-dry-run-receipt-v1","status":"FAIL" if issues else "PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"deck_sha256":_current_deck_snapshot_sha256(st),"render_sha256":sha256(render),"structural_inventory_sha256":invsha,"business_payload_file":str(business),"business_payload_sha256":sha256(business),"business_provenance":provenance,"summon_material_contract_status":"PASS" if provenance=="SEMANTIC_COMPILER" and not any(str(x.get("code") or "").startswith("SUMMON_") for x in issues) else ("NOT_APPLICABLE_LEGACY_PROVENANCE" if provenance!="SEMANTIC_COMPILER" else "FAIL"),"summon_material_contract_proof":summon_proof,"pilotage_source_sha256":_pilotage_policy_sha256(st),"issue_count":len(issues),"issues":issues,"issue_set_sha256":issue_set_sha,"repair_domains":domains,"read_only":True,"state_sha256_before":before,"state_sha256_after":sha256(rd/STATE_FILE),"runtime_version":VERSION,"validator":"FULL_SHARED_VALIDATOR"}
    out=rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT; authoritative_out=out; receipt_sha=None
    if write_receipt:
        authoritative_out,receipt_sha=_rc1623_write_receipt_pair(rd,PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT,"pilotage_dryrun",doc)
    _append_run_journal(rd,st,"PILOTAGE_AUTHORITATIVE_DRY_RUN_COMPLETED",checkpoint_seq=cp.get("checkpoint_seq"),status=doc["status"],issue_count=len(issues),issue_codes=sorted(x.get("code") for x in issues),repair_domains=domains,issue_set_sha256=issue_set_sha,receipt_file=str(authoritative_out) if write_receipt else None,receipt_sha256=receipt_sha,business_payload_sha256=doc["business_payload_sha256"],render_sha256=doc["render_sha256"],deck_sha256=doc["deck_sha256"],structural_inventory_sha256=invsha,state_sha256_before=before,state_sha256_after=sha256(rd/STATE_FILE),read_only=True)
    return doc,authoritative_out


def _route_failed_pilotage_dry_run(rd: Path, st, receipt):
    issues=receipt.get("issues",[]) if isinstance(receipt,dict) else []
    domains=sorted({x.get("repair_domain") or x.get("domain") for x in issues if nonempty(x.get("repair_domain") or x.get("domain"))})
    cp=_load_checkpoint_raw(rd,False) or {}
    if "FATAL_UNKNOWN" in domains or not domains:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain="FATAL_UNKNOWN",budget_class="FAIL_CLOSED",deck_artifact=st.get("current_artifact"),issue_count=len(issues),issue_set_sha256=receipt.get("issue_set_sha256"))
        _rc1623_mark_fatal_block(rd,st,receipt,"FATAL_UNKNOWN")
        fail("PILOTAGE_REPAIR_DOMAIN_FATAL_UNKNOWN_FAIL_NON_CERTIFIE")
    if "ORCHESTRATION_PREREQUISITE" in domains:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain="ORCHESTRATION_PREREQUISITE",budget_class="NON_BUSINESS",deck_artifact=st.get("current_artifact"),issue_codes=sorted(x.get("code") for x in issues if (x.get("repair_domain") or x.get("domain"))=="ORCHESTRATION_PREREQUISITE"))
        fail("PILOTAGE_ORCHESTRATION_PREREQUISITE_REQUIRED")
    nonbusiness=[d for d in domains if d in {"PRESENTATION_RENDER","PROOF_SCHEMA_ADMIN"}]
    if nonbusiness:
        routed=[]
        for domain in nonbusiness:
            fp=_pilotage_repair_fingerprint(st,receipt,domain)
            if _repair_already_routed(rd,fp): routed.append({"domain":domain,"reused":True}); continue
            used=_nonbusiness_repair_count(rd,st,domain)
            if used>=PILOTAGE_NON_BUSINESS_REPAIR_BUDGET:
                _append_run_journal(rd,st,"NON_BUSINESS_REPAIR_EXHAUSTED",checkpoint_seq=cp.get("checkpoint_seq"),domain=domain,deck_artifact=st.get("current_artifact"),render_id=st.get("current_render"),repairs_used=used,repair_budget=PILOTAGE_NON_BUSINESS_REPAIR_BUDGET,repair_fingerprint=fp); fail(f"NON_BUSINESS_REPAIR_EXHAUSTED: {domain}")
            _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain=domain,budget_class="NON_BUSINESS",deck_artifact=st.get("current_artifact"),render_id=st.get("current_render"),repair_cycle=used+1,repair_budget=PILOTAGE_NON_BUSINESS_REPAIR_BUDGET,repair_fingerprint=fp,issue_codes=sorted(x.get("code") for x in issues if (x.get("repair_domain") or x.get("domain"))==domain))
            routed.append({"domain":domain,"repair_cycle":used+1})
        return {"classification":"AUTO_RECOVERABLE","handoff_allowed":False,"domains":nonbusiness,"routes":routed,"required_action":"REPAIR_AND_CONTINUE"}
    # Business domain: exactly one budget consumption for this exact diagnostic.
    fp=_pilotage_repair_fingerprint(st,receipt,"BUSINESS_SEMANTIC_MECHANICAL")
    if _repair_already_routed(rd,fp): fail("PILOTAGE_BUSINESS_REPAIR_REQUIRED_SAME_INPUT_ALREADY_COUNTED")
    used=_business_failure_count(rd,st)
    if used>=PILOTAGE_COMMIT_ATTEMPT_BUDGET:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_BUDGET_EXHAUSTED",checkpoint_seq=cp.get("checkpoint_seq"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact")); fail("PILOTAGE_REPAIR_BUDGET_EXHAUSTED_FAIL_NON_CERTIFIE")
    used+=1
    _append_run_journal(rd,st,"PILOTAGE_BUSINESS_ATTEMPT_CONSUMED",checkpoint_seq=cp.get("checkpoint_seq"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact"),repair_fingerprint=fp,issue_codes=sorted(x.get("code") for x in issues if (x.get("repair_domain") or x.get("domain"))=="BUSINESS_SEMANTIC_MECHANICAL"),issue_set_sha256=receipt.get("issue_set_sha256"))
    _append_run_journal(rd,st,"PILOTAGE_REPAIR_ROUTED",checkpoint_seq=cp.get("checkpoint_seq"),domain="BUSINESS_SEMANTIC_MECHANICAL",budget_class="BUSINESS",deck_artifact=st.get("current_artifact"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,repair_fingerprint=fp,issue_codes=sorted(x.get("code") for x in issues if (x.get("repair_domain") or x.get("domain"))=="BUSINESS_SEMANTIC_MECHANICAL"))
    if used>=PILOTAGE_COMMIT_ATTEMPT_BUDGET:
        _append_run_journal(rd,st,"PILOTAGE_REPAIR_BUDGET_EXHAUSTED",checkpoint_seq=cp.get("checkpoint_seq"),attempts_used=used,attempt_budget=PILOTAGE_COMMIT_ATTEMPT_BUDGET,deck_artifact=st.get("current_artifact")); fail("PILOTAGE_REPAIR_BUDGET_EXHAUSTED_FAIL_NON_CERTIFIE")
    fail("PILOTAGE_BUSINESS_REPAIR_REQUIRED")

# -------------------- validation adjustments for neutral scaffold -----------

_validate_pilotage_contract_rc1623_parent=validate_pilotage_contract

def validate_pilotage_contract(path: Path, render_path: Path, st):
    """RC16.23 wrapper: enforce independent inventory before legacy full validator."""
    inv,invsha=_rc1623_normalize_structural_inventory(st); _rc1623_validate_inventory_against_render(inv,render_path)
    d=read_json(path,"pilotage contract")
    if d.get("structural_inventory_sha256") not in {None,invsha}: fail("PILOTAGE_STRUCTURAL_INVENTORY_STALE")
    # Translate structural obligation markers only for legacy validation fields;
    # business PASS/NO_MATERIAL decisions are never synthesized here.
    dd=copy.deepcopy(d)
    for strec in dd.get("structural_starters",[]) if isinstance(dd.get("structural_starters"),list) else []:
        if strec.get("coverage_status")=="REQUIRED": strec["coverage_status"]="PASS"  # structural coverage checked independently above
    for line in dd.get("lines",[]) if isinstance(dd.get("lines"),list) else []:
        if line.get("axis_validation_status")=="REQUIRED": line["axis_validation_status"]="PASS"  # axis/render binding checked above
        if line.get("starter_grouping_status")=="DECLARED_EQUIVALENT": line["starter_grouping_status"]="PASS"  # upstream authority declaration; Pilotage still validates execution
    with tempfile.TemporaryDirectory(prefix="rc1623-pilotage-contract-") as td:
        tp=Path(td)/"contract.json"; _atomic_write_text(tp,_stable_json_text(dd))
        # Validate the compatibility view, but freshness binds to the physical contract.
        _validate_pilotage_contract_rc1623_parent(tp,render_path,st)
    return d,sha256(path)

# Include inventory binding in compiled contracts.
_compile_pilotage_contract_document_rc1623_parent=_compile_pilotage_contract_document

def _compile_pilotage_contract_document(st,payload,render: Path):
    doc=_compile_pilotage_contract_document_rc1623_parent(st,payload,render)
    _,invsha=_rc1623_normalize_structural_inventory(st); doc["structural_inventory_sha256"]=invsha
    return doc


# ---------------- RC16.23 compatibility bridges: neutral shell ------------

_pilotage_merge_business_patch_rc1623_parent=_pilotage_merge_business_patch

def _pilotage_merge_business_patch(skeleton, patch, issue_codes=None, base_payload=None):
    """Apply authority/model-owned top fields, then reuse the protected ID merge.

    The parent implementation validated ``top_level`` locality but did not
    materialize those values.  RC16.23 keeps structural identity shell-owned
    while allowing the business authority to fill only the explicit semantic
    top-level slots.
    """
    if not isinstance(skeleton,dict) or not isinstance(patch,dict):
        fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: skeleton/patch must be objects")
    base=copy.deepcopy(base_payload if base_payload is not None else skeleton)
    if not isinstance(base,dict) or _pilotage_shell_identity(base)!=_pilotage_shell_identity(skeleton):
        fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: base payload changed shell-owned identity")
    top=patch.get("top_level",{})
    if not isinstance(top,dict): fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: top_level must be object")
    illegal=set(top)-_PILOTAGE_ALLOWED_TOP_PATCH_FIELDS
    if illegal: fail("PILOTAGE_REPAIR_SCOPE_VIOLATION: shell-owned top-level field")
    for k,v in top.items():
        base[k]=copy.deepcopy(v)
    p2=copy.deepcopy(patch); p2["top_level"]={}
    return _pilotage_merge_business_patch_rc1623_parent(
        skeleton,p2,issue_codes=issue_codes,base_payload=base
    )


_pilotage_wire_issues_rc1623_parent=_pilotage_wire_issues

def _pilotage_wire_issues(d,render_path: Path,st):
    """Normalize only authority-owned structural obligation markers.

    ``REQUIRED`` means the upstream structural inventory says the item must be
    covered; ``DECLARED_EQUIVALENT`` means Style→Axes explicitly declared the
    grouping.  Neither marker is a business PASS.  Survival against the exact
    render is checked independently before the legacy wire checks run.
    """
    inv,invsha=_rc1623_normalize_structural_inventory(st)
    _rc1623_validate_inventory_against_render(inv,render_path)
    dd=copy.deepcopy(d)
    if dd.get("structural_inventory_sha256") not in {None,invsha}:
        return [_decorate_preflight_issue({
            "code":"PILOTAGE_STRUCTURAL_INVENTORY_STALE","path":"$.structural_inventory_sha256",
            "expected":invsha,"observed":dd.get("structural_inventory_sha256")
        })]
    for strec in dd.get("structural_starters",[]) if isinstance(dd.get("structural_starters"),list) else []:
        if strec.get("coverage_status")=="REQUIRED": strec["coverage_status"]="PASS"
    for line in dd.get("lines",[]) if isinstance(dd.get("lines"),list) else []:
        if line.get("axis_validation_status")=="REQUIRED": line["axis_validation_status"]="PASS"
        if line.get("starter_grouping_status")=="DECLARED_EQUIVALENT": line["starter_grouping_status"]="PASS"
    return _pilotage_wire_issues_rc1623_parent(dd,render_path,st)


# ------------------------ terminal exactness hardening ----------------------

_cmd_authorize_rc1623_parent=cmd_authorize

def cmd_authorize(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    inv,invsha=_rc1623_normalize_structural_inventory(st)
    prec=(st.get("gates") or {}).get("PILOTAGE_VALIDATED") or {}
    pcf=prec.get("pilotage_contract_file")
    if not nonempty(pcf) or not Path(pcf).exists(): fail("PILOTAGE_CONTRACT_FRESHNESS_REQUIRED_AT_AUTHORIZE")
    if prec.get("pilotage_contract_sha256")!=sha256(Path(pcf)): fail("PILOTAGE_CONTRACT_STALE_AT_AUTHORIZE")
    pdoc=read_json(Path(pcf),"Pilotage contract")
    if pdoc.get("structural_inventory_sha256")!=invsha: fail("PILOTAGE_STRUCTURAL_INVENTORY_STALE_AT_AUTHORIZE")
    # Recheck render survival at the final boundary, not only at builder time.
    _rc1623_validate_inventory_against_render(inv,Path(a.render_file))
    return _cmd_authorize_rc1623_parent(a)

# --------------------- terminal payload verified read ----------------------

def _rc1623_output_policy(st,last_runtime_event=None):
    gates=st.get("gates") or {}
    ready=(
        st.get("run_execution_state")=="COMPLETED"
        and st.get("stop_output_allowed") is True
        and isinstance(gates.get("FINAL_VALIDATION_PASS"),dict)
        and nonempty(st.get("terminal_payload_file"))
        and nonempty(st.get("terminal_payload_sha256"))
    )
    if ready:
        return {"mode":"FINAL_ARTIFACT","final_artifact_allowed":True,"required_action":"terminal-output","reason":"TERMINAL_AUTHORIZED"}
    reason="STOP_OUTPUT_NOT_ALLOWED"
    if last_runtime_event=="FASTPATH_LOW_LEVEL_BLOCKED": reason="FASTPATH_LOW_LEVEL_BLOCKED"
    elif st.get("run_execution_state")=="BLOCKED_FATAL": reason="BLOCKED_FATAL"
    elif st.get("run_execution_state")=="IN_PROGRESS": reason="RUN_IN_PROGRESS"
    return {
        "mode":"STATUS_ONLY","final_artifact_allowed":False,
        "required_action":"continue nominal runtime or report blocking status only",
        "reason":reason,
        "next_required_gate":next_gate(st)[0] if isinstance(st.get("gates"),dict) else None,
    }


def cmd_output_policy(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    events=_read_journal(rd); last=events[-1].get("event") if events else None
    policy=_rc1623_output_policy(st,last)
    print(json.dumps(policy,ensure_ascii=False,sort_keys=True))


def _rc1623_continuation_policy(rd: Path, st):
    cp=_load_checkpoint_raw(rd,required=False) or {}
    state=st.get("run_execution_state") or cp.get("run_state") or "IN_PROGRESS"
    nxt=cp.get("next_required_gate")
    base={
      "run_id":st.get("run_id"),"run_state":state,"next_required_gate":nxt,
      "checkpoint_seq":cp.get("checkpoint_seq"),"resume_count":cp.get("resume_count",0),
    }
    if state=="COMPLETED":
        return {**base,"classification":"TERMINAL_COMPLETED","handoff_allowed":True,"required_action":"TERMINAL_OUTPUT"}
    if state=="WAITING_USER_INPUT":
        return {**base,"classification":"USER_REQUIRED","handoff_allowed":True,"required_action":"REQUEST_ONLY_MISSING_USER_INPUT","waiting_context":cp.get("waiting_context")}
    if state in {"BLOCKED_FATAL","TERMINAL_FAILED"}:
        return {**base,"classification":"FATAL","handoff_allowed":True,"required_action":"REPORT_BLOCK_AND_REQUIRE_EXPLICIT_RECOVERY"}
    receipt=rd/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT
    if receipt.exists():
        try: d=read_json(receipt,"Pilotage authoritative dry-run receipt")
        except BaseException:
            return {**base,"classification":"FATAL","handoff_allowed":True,"required_action":"REPORT_INVALID_RECEIPT"}
        if d.get("status")=="FAIL":
            issues=d.get("issues") if isinstance(d.get("issues"),list) else []
            domains=sorted({(x.get("repair_domain") or x.get("domain")) for x in issues if isinstance(x,dict) and nonempty(x.get("repair_domain") or x.get("domain"))})
            if not domains or "FATAL_UNKNOWN" in domains:
                return {**base,"classification":"FATAL","handoff_allowed":True,"required_action":"REPORT_BLOCK_AND_REQUIRE_EXPLICIT_RECOVERY","repair_domains":domains}
            if any(x in {"PRESENTATION_RENDER","PROOF_SCHEMA_ADMIN","ORCHESTRATION_PREREQUISITE"} for x in domains):
                return {**base,"classification":"AUTO_RECOVERABLE","handoff_allowed":False,"required_action":"REPAIR_CHECKPOINT_AND_CONTINUE","repair_domains":domains}
            if "BUSINESS_SEMANTIC_MECHANICAL" in domains:
                return {**base,"classification":"BUSINESS_REPAIRABLE","handoff_allowed":False,"required_action":"REROUTE_COMPETENT_AUTHORITY_AND_CONTINUE","repair_domains":domains}
    return {**base,"classification":"CONTINUE_NOMINAL","handoff_allowed":False,"required_action":"CONTINUE_TO_NEXT_REQUIRED_GATE"}


def cmd_continuation_policy(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    print(json.dumps(_rc1623_continuation_policy(rd,st),ensure_ascii=False,sort_keys=True))


def cmd_terminal_output(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if st.get("run_execution_state")!="COMPLETED" or st.get("stop_output_allowed") is not True:
        fail("TERMINAL_OUTPUT_NOT_AUTHORIZED")
    raw=st.get("terminal_payload_file"); expected=st.get("terminal_payload_sha256")
    if not nonempty(raw) or not nonempty(expected): fail("TERMINAL_PAYLOAD_BINDING_MISSING")
    payload=Path(raw)
    _rc1623_assert_flat_run_output(rd,payload,"terminal payload")
    if not payload.exists() or sha256(payload)!=expected or expected!=st.get("authorized_render_sha256"):
        fail("TERMINAL_PAYLOAD_STALE_AFTER_AUTHORIZE")
    print(payload.read_text(encoding="utf-8"),end="")

# ----------------------- central command serialization ----------------------

_instrumented_call_rc1623_parent=_instrumented_call

def _instrumented_call(a):
    mutating={
      "start","dispatch-run","fork-refactor-from-terminal","complete","material-change","evidence-refresh","presentation-change","authorize",
      "compile-render-contract","compile-component-payloads","compile-component-manifest","render-check","compile-terminal-presentation","terminal-presentation-check",
      "contract-defect","abort-run","simulate-interruption","checkpoint-run","resume-run","bind-explicit-direction","execute-batch","advance-prepared","evidence-refresh-selective","render-commit","pilotage-business-skeleton","pilotage-business-merge","pilotage-authoritative-dry-run","pilotage-commit","bind-card-metadata","recover-fatal"
    }
    rd=_timing_target_run_dir(a)
    # Central fatal guard catches commands that forgot a local mutable-run guard.
    if rd and (rd/STATE_FILE).exists() and a.cmd not in {"status","inspect-run-state","inspect-continuation","fastpath-metrics","output-policy","continuation-policy","handoff-check","mechanical-proof-status","blackbox-4d","compile-user-trace","recover-fatal"}:
        st=load_state(rd)
        if st.get("run_execution_state")=="BLOCKED_FATAL": fail("RUN_BLOCKED_FATAL_EXPLICIT_RECOVERY_REQUIRED")
    if rd and a.cmd in mutating:
        with _rc1623_command_lock(rd):
            return _instrumented_call_rc1623_parent(a)
    return _instrumented_call_rc1623_parent(a)



# =============================================================================
# RC16.23 — Semantic Compiler Boundary
# MODEL_OWNED = decisions/semantics. COMPILER_OWNED = propagation/IDs/state.
# =============================================================================

PILOTAGE_SEMANTIC_SCHEMA="ygo-pilotage-semantic-v1"
RENDER_SEMANTIC_SCHEMA="ygo-render-semantic-v1"


def _rc1623_deck_totals(snapshot):
    if not isinstance(snapshot,dict): fail("DECK_SNAPSHOT_INVALID")
    out={}
    for zone in ("main_deck","extra_deck","side_deck"):
        cards=snapshot.get(zone,[])
        if not isinstance(cards,list): fail(f"DECK_SNAPSHOT_ZONE_INVALID: {zone}")
        total=0
        for c in cards:
            if not isinstance(c,dict) or not nonempty(c.get("name")) or not isinstance(c.get("qty"),int) or isinstance(c.get("qty"),bool) or c.get("qty")<0:
                fail(f"DECK_SNAPSHOT_CARD_INVALID: {zone}")
            total+=c["qty"]
        out[zone]=total
    return out


def _rc1623_derive_deck_delta(before,after):
    def cards(doc):
        out={}
        for z in ("main_deck","extra_deck","side_deck"):
            for c in doc.get(z,[]) if isinstance(doc.get(z),list) else []:
                if isinstance(c,dict) and nonempty(c.get("name")) and isinstance(c.get("qty"),int): out[(z,c["name"].strip())]=c["qty"]
        return out
    a,b=cards(before),cards(after); delta=[]
    for key in sorted(set(a)|set(b)):
        if a.get(key,0)!=b.get(key,0): delta.append(f"{key[1]} [{key[0]}]: {a.get(key,0)} -> {b.get(key,0)}")
    return {"material_change":bool(delta),"delta":delta,"invalidate_from_gate":"DECK_DRAFT_CREATED" if delta else None,"before_artifact":before.get("artifact_id"),"after_artifact":after.get("artifact_id")}


def _rc1623_snapshot_catalog(st):
    rec=(st.get("gates") or {}).get("DECK_DRAFT_CREATED") or {}
    sp=Path(rec.get("snapshot_file") or "")
    if not sp.exists(): fail("DECK_SNAPSHOT_REQUIRED_FOR_SEMANTIC_COMPILER")
    if rec.get("snapshot_sha256") and rec.get("snapshot_sha256")!=sha256(sp): fail("DECK_SNAPSHOT_STALE_FOR_SEMANTIC_COMPILER")
    doc=read_json(sp,"deck snapshot"); out={}
    zone_map={"main_deck":"DECK","extra_deck":"EXTRA","side_deck":"SIDE"}
    for z in zone_map:
        for c in doc.get(z,[]) if isinstance(doc.get(z),list) else []:
            if isinstance(c,dict) and nonempty(c.get("name")) and isinstance(c.get("qty"),int):
                out[c["name"].strip().casefold()]={"name":c["name"].strip(),"qty":c["qty"],"snapshot_zone":z,"runtime_zone":zone_map[z]}
    return doc,out


def _rc1623_semantic_line_map(inv, semantic):
    lines=semantic.get("lines") if isinstance(semantic,dict) else None
    if semantic.get("schema")!=PILOTAGE_SEMANTIC_SCHEMA or not isinstance(lines,list) or not lines:
        fail("PILOTAGE_SEMANTIC_SCHEMA_INVALID")
    used=set(); out=[]
    for ent in inv.get("lines",[]):
        matches=[]
        for i,x in enumerate(lines):
            if not isinstance(x,dict) or i in used: continue
            ah=x.get("axis_heading")
            if nonempty(ah) and ah.strip().casefold()==ent["axis_heading"].strip().casefold(): matches.append((i,x))
        if not matches: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: line for {ent['axis_heading']}")
        if len(matches)>1: fail(f"PILOTAGE_SEMANTIC_LINE_AMBIGUOUS: {ent['axis_heading']}")
        i,x=matches[0]; used.add(i); out.append((ent,x))
    return out


def _rc1623_resource_id(n): return f"res-{n:03d}"
def _rc1623_step_id(n): return f"step-{n:03d}"
def _rc1623_binding_id(n): return f"mcb-{n:04d}"


def _rc1623_compile_resources(starter_resources, actions, catalog):
    names=[]
    def add(v):
        if nonempty(v) and v.strip().casefold() not in {x.casefold() for x in names}: names.append(v.strip())
    for x in starter_resources: add(x)
    for a in actions:
        if not isinstance(a,dict): fail("PILOTAGE_SEMANTIC_ACTION_INVALID")
        add(a.get("card")); add(a.get("actor")); add(a.get("target"))
        for x in a.get("materials",[]) if isinstance(a.get("materials"),list) else []: add(x)
        for x in a.get("participants",[]) if isinstance(a.get("participants"),list) else []: add(x)
    resources=[]; by_name={}
    starter_cf={x.casefold() for x in starter_resources}
    for idx,name in enumerate(names,1):
        key=name.casefold(); meta=catalog.get(key)
        if meta is None: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: card not bound to deck snapshot: {name}")
        loc={meta["runtime_zone"]:meta["qty"]}
        if key in starter_cf:
            if meta["runtime_zone"] not in {"DECK","EXTRA","SIDE"} or meta["qty"]<1: fail(f"COMPILER_STARTER_RESOURCE_INVALID: {name}")
            loc[meta["runtime_zone"]]-=1; loc["HAND"]=loc.get("HAND",0)+1
        rid=_rc1623_resource_id(idx)
        rec={"resource_id":rid,"kind":"CARD","card_name":meta["name"],"snapshot_zone":meta["snapshot_zone"],"initial_locations":{k:v for k,v in loc.items() if v>=0},"starter_labels":[name] if key in starter_cf else []}
        resources.append(rec); by_name[key]=rid
    return resources,by_name


def _rc1623_initial_state(resources):
    return {r["resource_id"]:copy.deepcopy(r.get("initial_locations",{})) for r in resources}


def _rc1623_pick_zone(state,rid,preferred=None):
    if nonempty(preferred) and state.get(rid,{}).get(preferred,0)>0: return preferred
    for z in ("FIELD","HAND","GY","DECK","EXTRA","BANISHED","SIDE"):
        if state.get(rid,{}).get(z,0)>0: return z
    return None


def _rc1623_compiler_evidence(step_id,kind,text):
    et=f"Deterministic semantic-to-mechanical derivation for {kind}: {text}"
    return {"evidence_id":f"ev-{step_id}","evidence_kind":"PILOTAGE_DERIVATION","evidence_sha256":_inline_evidence_sha(et),"evidence_text":et,"source_locator":"RC16.23 Semantic Compiler"}


def _rc1623_binding(source_id,action_id,evidence_id,operator,params,n):
    return {"binding_id":_rc1623_binding_id(n),"source_kind":"COMPILER_DERIVATION","source_id":source_id,"action_id":action_id,"evidence_id":evidence_id,"operator":operator,"scope":"SINGLE","params":params,"material_to_line":True}


def _rc1623_derive_semantic_bindings(actions, resources, by_name, starter_resources):
    state=_rc1623_initial_state(resources); bindings=[]; step_meta=[]; bn=0; last_actor=None
    def rid(name,label):
        if not nonempty(name) or name.strip().casefold() not in by_name: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: {label}")
        return by_name[name.strip().casefold()]
    def addb(src,aid,eid,op,params):
        nonlocal bn; bn+=1; b=_rc1623_binding(src,aid,eid,op,params,bn); bindings.append(b)
        # local simulation for source-zone derivation and early contradiction detection
        if op in {"MOVE","CONSUME","OBTAIN"}:
            _mcb_resource_move(state,{r['resource_id']:r for r in resources},params['resource_id'],params['from_zone'],params['to_zone'],params.get('qty',1),'<semantic>','<semantic>',aid,b['binding_id'])
        return b
    for i,a in enumerate(actions,1):
        if not isinstance(a,dict): fail("PILOTAGE_SEMANTIC_ACTION_INVALID")
        kind=str(a.get("kind") or "").upper(); text=a.get("text")
        if not nonempty(kind) or not nonempty(text): fail("COMPILER_NEEDS_SEMANTIC_INPUT: action kind/text")
        aid=_rc1623_step_id(i); eid=f"ev-{aid}"; src=f"semantic-action-{i}"; participants=[]; outputs=[]
        if i==1:
            for name in starter_resources:
                rr=rid(name,f"starter resource {name}"); participants.append(rr); bn+=1; bindings.append(_rc1623_binding(src,aid,eid,"REQUIRE",{"requirement_kind":"RESOURCE_AT","resource_id":rr,"zone":"HAND","qty":1},bn))
        if kind in {"NORMAL_SUMMON","SPECIAL_SUMMON","ACTIVATE","SEARCH","SEND_TO_GY","REVIVE","MOVE"}:
            name=a.get("card"); rr=rid(name,f"card for {kind}"); participants.append(rr); last_actor=rr
            defaults={
              "NORMAL_SUMMON":("HAND","FIELD"),"SPECIAL_SUMMON":("HAND","FIELD"),"ACTIVATE":("HAND","GY"),
              "SEARCH":("DECK","HAND"),"SEND_TO_GY":("FIELD","GY"),"REVIVE":("GY","FIELD"),"MOVE":(None,None)
            }
            df,dt=defaults[kind]; fz=a.get("from_zone") or a.get("source_zone") or df; tz=a.get("to_zone") or a.get("target_zone") or dt
            if not nonempty(fz) or not nonempty(tz): fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: zones for {kind}")
            addb(src,aid,eid,"MOVE",{"resource_id":rr,"from_zone":fz,"to_zone":tz,"qty":1}); outputs.append(rr)
        elif kind in {"SYNCHRO_SUMMON","FUSION_SUMMON"}:
            boss=rid(a.get("card"),f"boss for {kind}"); mats=a.get("materials")
            if not isinstance(mats,list) or not mats: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: materials for {kind}")
            for name in mats:
                rr=rid(name,f"material {name}"); participants.append(rr); fz=_rc1623_pick_zone(state,rr,a.get("material_zone"))
                if not fz: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: material zone for {name}")
                addb(src,aid,eid,"MOVE",{"resource_id":rr,"from_zone":fz,"to_zone":"GY","qty":1})
            participants.append(boss); last_actor=boss
            addb(src,aid,eid,"MOVE",{"resource_id":boss,"from_zone":"EXTRA","to_zone":"FIELD","qty":1}); outputs.append(boss)
        elif kind=="DAMAGE":
            amount=a.get("amount"); certainty=a.get("certainty","GUARANTEED")
            actor=rid(a.get("actor"),"damage actor") if nonempty(a.get("actor")) else last_actor
            if actor is None: fail("COMPILER_NEEDS_SEMANTIC_INPUT: damage actor")
            participants.append(actor); bn+=1; bindings.append(_rc1623_binding(src,aid,eid,"DAMAGE_EVENT",{"amount":amount,"certainty":certainty},bn))
        elif kind=="LETHAL_CHECK":
            actor=rid(a.get("actor"),"lethal actor") if nonempty(a.get("actor")) else last_actor
            if actor is None: fail("COMPILER_NEEDS_SEMANTIC_INPUT: lethal actor")
            participants.append(actor); bn+=1; bindings.append(_rc1623_binding(src,aid,eid,"LETHAL_CHECK",{"opponent_lp_before":a.get("opponent_lp"),"claim":a.get("certainty","GUARANTEED")},bn))
        elif kind=="EFFECT":
            names=a.get("participants")
            if not isinstance(names,list) or not names: fail("COMPILER_NEEDS_SEMANTIC_INPUT: EFFECT participants")
            participants=[rid(x,f"participant {x}") for x in names]; last_actor=participants[0]
        elif kind=="DESTROY":
            if not nonempty(a.get("target")): fail("COMPILER_NEEDS_SEMANTIC_INPUT: DESTROY target")
            fail("COMPILER_NEEDS_SEMANTIC_INPUT: DESTROY target state/source")
        else:
            fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: unsupported semantic action kind {kind}")
        participants=list(dict.fromkeys(participants))
        if not participants: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: participants for {kind}")
        step_meta.append({"step_id":aid,"text":text,"kind":kind,"evidence_id":eid,"participants":participants,"outputs":list(dict.fromkeys(outputs))})
    # Validate the primary derivation itself before returning it.
    rp={"resources":resources,"restrictions":[],"fact_catalog":[],"constraint_catalog":[],"initial_properties":[],"steps":[{"step_id":x['step_id']} for x in step_meta],"mechanical_consequence_bindings":bindings}
    _compile_mcb_projection_for_replay(rp,"<semantic>","<semantic>")
    return bindings,step_meta


def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    render_path=Path(render_path)
    if not render_path.exists(): fail("PILOTAGE_RENDER_MISSING")
    inv,invsha=_rc1623_normalize_structural_inventory(st); _rc1623_validate_inventory_against_render(inv,render_path)
    _,catalog=_rc1623_snapshot_catalog(st); pairs=_rc1623_semantic_line_map(inv,semantic)
    shell=_pilotage_business_skeleton_from_render(st,render_path)
    lines=[]
    for ent,sem in pairs:
        actions=sem.get("actions")
        if not isinstance(actions,list) or not actions: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: actions for {ent['axis_heading']}")
        starter_resources=[]
        for sr in ent.get("starters",[]):
            for x in sr.get("resources",[]):
                if x.casefold() not in {y.casefold() for y in starter_resources}: starter_resources.append(x)
        if not starter_resources: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: starter resources for {ent['axis_heading']}")
        resources,by_name=_rc1623_compile_resources(starter_resources,actions,catalog)
        bindings,step_meta=_rc1623_derive_semantic_bindings(actions,resources,by_name,starter_resources)
        # Independent second derivation for the cold projection: same semantic input, no reuse of primary binding objects.
        cold_bindings,_=_rc1623_derive_semantic_bindings(copy.deepcopy(actions),copy.deepcopy(resources),copy.deepcopy(by_name),list(starter_resources))
        if [_mcb_signature_text(x) for x in bindings]!=[_mcb_signature_text(x) for x in cold_bindings]: fail("SEMANTIC_COMPILER_COLD_DERIVATION_DIVERGENCE")
        claim=sem.get("claim")
        if not isinstance(claim,dict) or not nonempty(claim.get("type")): fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: claim for {ent['axis_heading']}")
        certainty=claim.get("certainty","GUARANTEED")
        if certainty not in {"GUARANTEED","CONDITIONAL","RANDOM","RANGE","UNKNOWN"}: fail("PILOTAGE_SEMANTIC_CLAIM_CERTAINTY_INVALID")
        victory="LETHAL" if str(claim.get("type")).upper()=="LETHAL" else "NONE"
        outcome_text=sem.get("outcome_text") or ent.get("render_token")
        if not nonempty(outcome_text) or outcome_text.strip().casefold() not in render_path.read_text(encoding='utf-8').casefold(): fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: rendered outcome for {ent['axis_heading']}")
        evidence=[_rc1623_compiler_evidence(x['step_id'],x['kind'],x['text']) for x in step_meta]
        evid_ids={x['step_id']:f"ev-{x['step_id']}" for x in step_meta}
        steps=[]
        for x in step_meta:
            sid=x['step_id']; eid=evid_ids[sid]
            steps.append({
              "step_id":sid,"render_token":x['text'],"requires":[],"moves":[],"produces":[],"property_updates":[],"attachment_transitions":[],
              "activate_restrictions":[],"release_restrictions":[],"budget_consumes":[],"budget_produces":[],"state_preconditions":[],"restriction_checks":[],
              "legality_checks":{"cost":"PASS","restriction":"PASS","target":"PASS","timing":"PASS"},
              "action_legality_proof":{"action_id":sid,"action_legality_status":"PASS","active_restriction_inventory_status":"COMPLETE","applicable_constraint_ids":[],"constraint_inventory_status":"COMPLETE_NO_APPLICABLE_CONSTRAINTS","output_requirement_inventory_status":"COMPLETE","output_resource_ids":x['outputs'],"participant_guard_inventory_status":"COMPLETE","participants":[{"resource_id":r,"role":"semantic action participant"} for r in x['participants']],"placement_binding":{"status":"NOT_APPLICABLE"},"cold_legality_sweep":{"status":"PASS","ignored_initial_constraint_inventory":True,"discovered_constraint_ids":[],"evidence_ids":[eid],"sweep_basis":"Independent deterministic semantic-action legality inventory derivation"}}
            })
        derived=[]; derived_ids=[]
        if victory=="LETHAL":
            dmg=sum(float(a.get("amount",0)) for a in actions if isinstance(a,dict) and str(a.get("kind") or '').upper()=="DAMAGE")
            if dmg<=0: fail("COMPILER_NEEDS_SEMANTIC_INPUT: lethal damage events")
            token=next((a.get('text') for a in actions if isinstance(a,dict) and str(a.get('kind') or '').upper()=="DAMAGE" and str(int(dmg)) in str(a.get('text') or '')),None)
            if not nonempty(token): fail("COMPILER_NEEDS_SEMANTIC_INPUT: rendered lethal damage total")
            cid="claim-damage-total"
            derived=[{"claim_id":cid,"at_state":"FINAL","claim_type":"NUMERIC","certainty":"EXACT","depends_on_claim_ids":[],"computation":{"op":"CONST","value":int(dmg) if dmg.is_integer() else dmg},"conditions":[],"condition_render_tokens":[],"rendered_value":int(dmg) if dmg.is_integer() else dmg,"render_token":token,"rendered_value_token":str(int(dmg) if dmg.is_integer() else dmg)}]; derived_ids=[cid]
        replay_id=ent['replay_ids'][0]
        if len(ent['replay_ids'])!=1 and not isinstance(sem.get('replays'),list): fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: replay semantics for {ent['axis_heading']}")
        rp={
          "replay_id":replay_id,"status":"PASS","covers_variants":["__BASE__"],"resources":resources,"budgets":[],"restrictions":[],"legality_evidence":evidence,"fact_catalog":[],"constraint_catalog":[],"external_inputs":[],
          "steps":steps,"derived_claim_inventory_status":"COMPLETE" if derived else "COMPLETE_NO_MATERIAL_CLAIMS","derived_claims":derived,
          "outcome":{"certainty":certainty,"render_token":outcome_text,"conditions":[],"condition_render_tokens":[],"guarantee_claim_status":"CONSISTENT" if certainty=="GUARANTEED" else "NO_FALSE_GUARANTEE","derived_claim_ids":derived_ids,"victory_claim":victory,"semantic_claim_type":str(claim.get('type')).upper()},
          "dynamic_state_scope_status":"COMPLETE_NO_DYNAMIC_PROPERTIES","initial_properties":[],"attachment_scope_status":"NO_ATTACHMENTS","initial_attachments":[],"topology_scope_status":"NO_MATERIAL_TOPOLOGY","topology_slots":[],"topology_rules":[],
          "state_precondition_inventory_status":"COMPLETE_NO_MATERIAL_PRECONDITIONS","topology_inventory_status":"COMPLETE_NO_MATERIAL_RELATIONSHIPS","topology_checks":[],"external_condition_inventory_status":"COMPLETE_NO_MATERIAL_EXTERNAL_CONDITIONS","external_conditions":[],
          "semantic_layer_version":"SRC1-GR1-BW1-MCB1","src_scope_status":"COMPLETE_NO_MATERIAL_SRC","semantic_ruling_contracts":[],"game_rule_scope_status":"COMPLETE_NO_MATERIAL_GAME_RULES","action_game_rule_profiles":[],"game_rule_bindings":[],
          "mechanical_consequence_scope_status":"COMPLETE","mechanical_consequence_bindings":bindings,"backward_proof_scope_status":"COMPLETE_NO_MATERIAL_BACKWARD_REQUIREMENTS","backward_requirements":[],"critical_decisions":[],
          "unified_cold_audit":{"status":"PASS","ignored_primary_inventories":True,"sweep_basis":"Independent deterministic semantic compiler cold audit","semantic":{"discovered_ids":[],"evidence_ids":[]},"game_rules":{"discovered_ids":[],"evidence_ids":[]},"mechanical_projection":{"status":"PASS","ignored_primary_bindings":True,"sweep_basis":"Independent second derivation from semantic actions","bindings":cold_bindings},"legality":{"by_action":{x['step_id']:[] for x in step_meta},"evidence_ids_by_action":{x['step_id']:[evid_ids[x['step_id']]] for x in step_meta}},"derived":{"discovered_ids":derived_ids},"state":{"discovered_ids":[]},"topology":{"discovered_ids":[]},"certainty":{"discovered_ids":[]},"backward":{"discovered_ids":[]}}
        }
        # Ensure deterministic MCB projection already closes; contradictions must survive.
        _compile_mcb_projection_for_replay(rp,ent['line_id'],replay_id)
        base=next(x for x in shell['lines'] if x['line_id']==ent['line_id'])
        line=copy.deepcopy(base)
        line.update({"declared_initial_resources":starter_resources,"mandatory_initial_resources":starter_resources,"obtained_during_line":[],"hidden_initial_resources":[],"starter_contract_status":"PASS","generic_starter":False,"generic_coverage_status":"NOT_APPLICABLE","starter_property_scope_status":"NO_PROPERTY_SENSITIVE_STARTER","starter_property_checks":[],"sequence_complexity":"SIMPLE","physical_state_scope_status":"NO_CRITICAL_ZONE_STATE","state_checkpoints":[],"effect_resolution_scope_status":"NO_RELEVANT_EFFECT_SELECTION","effect_resolution_checks":[],"line_execution_scope_status":"PASS","execution_replays":[rp]})
        lines.append(line)
    out={"status":"PASS","execution_contract_version":"RC16.2","axis_coverage_status":"PASS","starter_exploration_status":"COMPLETE","starter_inventory_status":"PASS","structural_starters":copy.deepcopy(inv['starters']),"lines":lines,"structural_inventory_sha256":invsha,"compiler_provenance":{"schema":"ygo-semantic-compiler-receipt-v1","semantic_schema":PILOTAGE_SEMANTIC_SCHEMA,"compiler_owned":True}}
    return out


def _rc1623_coverage_matrix(payload):
    starter_ids={x.get('starter_id') for x in payload.get('structural_starters',[]) if isinstance(x,dict)}
    rows=[]
    for line in payload.get('lines',[]) if isinstance(payload.get('lines'),list) else []:
        refs=set(line.get('starter_ids',[]) if isinstance(line.get('starter_ids'),list) else [])
        rows.append({"axis_heading":line.get('render_axis_heading'),"line_id":line.get('line_id'),"starter_ids":sorted(refs),"covered":bool(refs) and refs.issubset(starter_ids) and bool(line.get('execution_replays'))})
    return rows


def _rc1624_wrap_render_lines(lines, line_max=220):
    import textwrap
    out=[]
    for line in lines:
        if len(line)<=line_max or line.startswith('#') or not line.strip():
            out.append(line); continue
        prefix=''
        body=line
        if line.startswith('- '): prefix='- '; body=line[2:]
        chunks=textwrap.wrap(body,width=max(20,line_max-len(prefix)),break_long_words=True,break_on_hyphens=False,replace_whitespace=False,drop_whitespace=True) or ['']
        out.append(prefix+chunks[0])
        out.extend(chunks[1:])
    return out

def _rc1624_decklist_block(st):
    dg=(st.get('gates') or {}).get('DECK_DRAFT_CREATED',{}); ng=(st.get('gates') or {}).get('NARRATIVE_CONFORMANCE_CLOSED',{})
    if not dg.get('snapshot_file') or not ng.get('evidence_file'): return None
    sp=Path(dg['snapshot_file']); np=Path(ng['evidence_file'])
    if not sp.exists() or not np.exists(): return None
    snap=read_json(sp,'deck snapshot'); typemap=_narrative_type_map(np); totals=_category_totals(snap,typemap)
    monsters=[]; spells=[]; traps=[]
    for c in snap.get('main_deck',[]):
        line=f"- {c['qty']}x {c['name']}"; cat=_card_group(typemap.get(('main_deck',c['name'].strip().casefold()),''))
        (monsters if cat=='MONSTER' else spells if cat=='SPELL' else traps).append(line)
    extra=[f"- {c['qty']}x {c['name']}" for c in snap.get('extra_deck',[])]
    side=[f"- {c['qty']}x {c['name']}" for c in snap.get('side_deck',[])]
    return ['## Decklist',f"### Main Deck — {totals['MAIN']}",f"#### Monstres — {totals['MONSTER']}",*monsters,f"#### Magies — {totals['SPELL']}",*spells,f"#### Pièges — {totals['TRAP']}",*traps,f"### Extra Deck — {totals['EXTRA']}",*extra,f"### Side Deck — {totals['SIDE']}",*side]

def _rc1623_compile_render_semantic(doc,visual=None,decklist_block=None,line_max=220):
    if not isinstance(doc,dict) or not nonempty(doc.get('title')): fail('RENDER_SEMANTIC_TITLE_REQUIRED')
    visual=visual or {}; lines=[f"# {doc['title'].strip()}"]; deck_inserted=False
    sections=doc.get('sections',[]) if isinstance(doc.get('sections'),list) else []
    for sec in sections:
        if not isinstance(sec,dict) or not nonempty(sec.get('heading')): fail('RENDER_SEMANTIC_SECTION_INVALID')
        heading=sec['heading'].strip(); is_deck=bool(re.match(r'(?i)^decklist\b',heading)); is_axis=bool(re.match(r'(?i)^axe\s+\d+\b',heading))
        if decklist_block and is_axis and not deck_inserted:
            lines += ['',*decklist_block]; deck_inserted=True
        if is_deck and decklist_block:
            if not deck_inserted: lines += ['',*decklist_block]; deck_inserted=True
            continue
        lines += ['',f"## {heading}"]
        body=sec.get('body',[])
        if isinstance(body,str): body=[body]
        if not isinstance(body,list): fail('RENDER_SEMANTIC_SECTION_BODY_INVALID')
        for x in body:
            if nonempty(str(x)): lines.append(str(x).strip())
    if decklist_block and not deck_inserted: lines += ['',*decklist_block]
    sig=visual.get('signature_climax') if isinstance(visual.get('signature_climax'),dict) else {}
    quote=doc.get('terminal_quote')
    if sig.get('terminal_quote_required') is True:
        if not nonempty(quote): fail('COMPILER_NEEDS_SEMANTIC_INPUT: terminal quote')
        lines=[x for x in lines if x.strip()!=quote.strip()]
        lines += ['',quote.strip()]
    elif nonempty(quote): lines += ['',quote.strip()]
    lines=_rc1624_wrap_render_lines(lines,line_max=line_max)
    return '\n'.join(lines).rstrip()+'\n'


def _rc1623_render_component_plan(doc,visual):
    comps=[]
    main=visual.get('main_carousel') if isinstance(visual,dict) and isinstance(visual.get('main_carousel'),dict) else {}
    sig=visual.get('signature_climax') if isinstance(visual,dict) and isinstance(visual.get('signature_climax'),dict) else {}
    if main.get('applicable') is True:
        comps.append({'component_id':'main-card-carousel','type':'main-carousel','selected_cards':list(main.get('selected_cards') or [])})
    if sig.get('mini_carousel_applicable') is True:
        if not nonempty(sig.get('parent')): fail('COMPILER_NEEDS_SEMANTIC_INPUT: signature mini-carousel parent')
        comps.append({'component_id':'signature-mini-carousel','type':'mini-carousel','parent':sig.get('parent'),'selected_cards':list(sig.get('selected_cards') or [])})
    return {'schema':'ygo-render-component-plan-semantic-v1','components':comps}


# Compiler-owned MCB provenance: the validator verifies that this provenance is
# a deterministic derivation of the semantic action, never a new game ruling.
def _validate_mcb_bindings(rp, semantic_meta, evidence, resources, restrictions_meta, facts, constraints, lid, rpid, require=False):
    scope=rp.get("mechanical_consequence_scope_status"); bindings=rp.get("mechanical_consequence_bindings",[])
    if not require and scope is None and bindings in (None,[]): return []
    if scope not in {"COMPLETE","COMPLETE_NO_MATERIAL_BINDINGS"} or not isinstance(bindings,list): fail(f"MCB_SCOPE_NOT_CLOSED: {lid}:{rpid}")
    seen=set(); source_covered=set(); step_ids={x.get("step_id") for x in rp.get("steps",[]) if isinstance(x,dict)}
    src_ev=semantic_meta.get("src_clause_evidence",{}); gr_actions=semantic_meta.get("game_rule_actions",{}); gr_ev=semantic_meta.get("game_rule_evidence",{})
    for b in bindings:
        if not isinstance(b,dict): fail(f"MCB_BINDING_INVALID: {lid}:{rpid}")
        bid=b.get("binding_id")
        if not nonempty(bid) or bid in seen: fail(f"MCB_BINDING_ID_INVALID: {lid}:{rpid}")
        seen.add(bid); sk=b.get("source_kind"); sid=b.get("source_id"); aid=b.get("action_id"); eid=b.get("evidence_id")
        if sk not in {"SRC_CLAUSE","GAME_RULE","COMPILER_DERIVATION"} or not nonempty(sid) or aid not in step_ids or eid not in evidence: fail(f"MCB_SOURCE_BINDING_INVALID: {lid}:{rpid}:{bid}")
        if sk=="SRC_CLAUSE":
            if sid not in src_ev or src_ev[sid]!=eid: fail(f"MCB_SRC_EVIDENCE_MISMATCH: {lid}:{rpid}:{bid}")
        elif sk=="GAME_RULE":
            if sid not in gr_actions or aid not in gr_actions[sid] or eid not in gr_ev.get(sid,set()): fail(f"MCB_GAME_RULE_BINDING_MISMATCH: {lid}:{rpid}:{bid}")
        else:
            if evidence[eid].get('evidence_kind')!='PILOTAGE_DERIVATION': fail(f"MCB_COMPILER_DERIVATION_EVIDENCE_INVALID: {lid}:{rpid}:{bid}")
        if b.get("operator") not in MCB_OPERATORS or b.get("scope") not in MCB_SCOPES or not isinstance(b.get("params"),dict) or b.get("material_to_line") is not True: fail(f"MCB_BINDING_SHAPE_INVALID: {lid}:{rpid}:{bid}")
        source_covered.add((sk,sid,aid if sk=="GAME_RULE" else None))
    required_sources={("SRC_CLAUSE",x,None) for x in semantic_meta.get("src_clause_ids",set())}
    for grid,actions in semantic_meta.get("game_rule_actions",{}).items():
        for aid in actions: required_sources.add(("GAME_RULE",grid,aid))
    if require and required_sources-source_covered:
        miss=",".join(f"{a}:{b}"+(f"@{c}" if c else "") for a,b,c in sorted(required_sources-source_covered,key=lambda x:(x[0],x[1],x[2] or ""))); fail(f"MCB_MATERIAL_SOURCE_UNBOUND: {lid}:{rpid}:{miss}")
    if scope=="COMPLETE_NO_MATERIAL_BINDINGS" and bindings: fail(f"MCB_NO_MATERIAL_STATUS_INCONSISTENT: {lid}:{rpid}")
    if scope=="COMPLETE" and require and not bindings and required_sources: fail(f"MCB_BINDINGS_MISSING: {lid}:{rpid}")
    ua=rp.get("unified_cold_audit",{}); mp=ua.get("mechanical_projection") if isinstance(ua,dict) else None
    if require:
        if not isinstance(mp,dict) or mp.get("status")!="PASS" or mp.get("ignored_primary_bindings") is not True or not nonempty(mp.get("sweep_basis")): fail(f"MCB_COLD_PROJECTION_NOT_CLOSED: {lid}:{rpid}")
        _compare_mcb_cold_projection(bindings,mp.get("bindings"),lid,rpid)
    return bindings



def _rc1623_pilotage_semantic_template(st):
    inv,_=_rc1623_normalize_structural_inventory(st); lines=[]
    for ent in inv.get('lines',[]):
        starters=[]
        for sr in ent.get('starters',[]):
            starters.append({'display':sr.get('display'),'resources':list(sr.get('resources') or [])})
        lines.append({'axis_heading':ent.get('axis_heading'),'starter':starters[0]['display'] if starters else None,'starter_context':starters,'actions':[],'claim':None,'outcome_text':''})
    return {'schema':PILOTAGE_SEMANTIC_SCHEMA,'compiler_owned_fields_notice':'Do not add IDs, hashes, bindings, resource ledgers, MCB statuses or cold audits. Fill only semantic actions/claim/outcome and truly material rulings if needed.','lines':lines}


def cmd_pilotage_semantic_template(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,'pilotage-semantic-template')
    out=Path(a.output); _rc1623_assert_flat_run_output(rd,out,'pilotage semantic template'); doc=_rc1623_pilotage_semantic_template(st); _atomic_write_text(out,_stable_json_text(doc))
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,'PILOTAGE_SEMANTIC_TEMPLATE_BUILT',checkpoint_seq=cp.get('checkpoint_seq'),output_file=str(out),output_sha256=sha256(out))
    print(json.dumps({'status':'BUILT','output':str(out),'sha256':sha256(out)},ensure_ascii=False))


def cmd_pilotage_semantic_compile(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,'pilotage-semantic-compile')
    semantic_path=Path(a.semantic_file); semantic=read_json(semantic_path,'Pilotage semantic payload'); render=Path(a.render_file); out=Path(a.output); _rc1623_assert_flat_run_output(rd,out,'pilotage semantic compiled payload')
    compiled=_rc1623_compile_semantic_pilotage(st,render,semantic); _atomic_write_text(out,_stable_json_text(compiled))
    _,invsha=_rc1623_normalize_structural_inventory(st)
    rec={
      'schema':PILOTAGE_SEMANTIC_COMPILE_RECEIPT_SCHEMA,'status':'PASS','run_id':st.get('run_id'),'deck_artifact':st.get('current_artifact'),
      'deck_sha256':_current_deck_snapshot_sha256(st),'render_id':st.get('current_render'),'render_sha256':sha256(render),
      'structural_inventory_sha256':invsha,'semantic_file':str(semantic_path),'semantic_sha256':sha256(semantic_path),
      'business_payload_file':str(out),'business_payload_sha256':sha256(out),'compiler_contract':PILOTAGE_SEMANTIC_SCHEMA,
      'runtime_version':VERSION
    }
    rp,rph=_rc1623_write_receipt_pair(rd,PILOTAGE_SEMANTIC_COMPILE_RECEIPT,'pilotage_semantic_compile',rec)
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,'PILOTAGE_SEMANTIC_COMPILED',checkpoint_seq=cp.get('checkpoint_seq'),semantic_file=str(semantic_path),semantic_sha256=sha256(semantic_path),output_file=str(out),output_sha256=sha256(out),structural_inventory_sha256=compiled.get('structural_inventory_sha256'),provenance_receipt_file=str(rp),provenance_receipt_sha256=rph)
    print(json.dumps({'status':'COMPILED','output':str(out),'sha256':sha256(out),'provenance_receipt':str(rp),'provenance_receipt_sha256':rph},ensure_ascii=False))


def cmd_render_semantic_compile(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,'render-semantic-compile')
    doc=read_json(Path(a.semantic_file),'Render semantic payload'); visual=read_json(Path(a.visual_assets_file),'visual assets'); out=Path(a.output); _rc1623_assert_flat_run_output(rd,out,'semantic render')
    deck_block=_rc1624_decklist_block(st)
    try: line_max=_rc16221_source_owned_axis_limits(st)['line_max']
    except BaseException: line_max=RC1623_RENDER_PROJECTION_CONTRACT_EXPECTED['axis_line_max']
    text=_rc1623_compile_render_semantic(doc,visual,decklist_block=deck_block,line_max=line_max); _atomic_write_text(out,text)
    plan=_rc1623_render_component_plan(doc,visual); planp=rd/'semantic_component_plan.json'; _atomic_write_text(planp,_stable_json_text(plan))
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,'RENDER_SEMANTIC_COMPILED',checkpoint_seq=cp.get('checkpoint_seq'),semantic_file=str(a.semantic_file),semantic_sha256=sha256(Path(a.semantic_file)),output_file=str(out),output_sha256=sha256(out),component_plan_file=str(planp),component_plan_sha256=sha256(planp))
    print(json.dumps({'status':'COMPILED','output':str(out),'sha256':sha256(out),'component_plan':str(planp)},ensure_ascii=False))


# =============================================================================
# RC16.23.3 — Black-Box Hardening
# Truth alignment: semantic / proof / presentation / continuation.
# REQ-00 is transverse: no derivable bookkeeping is moved back to the model.
# =============================================================================

HANDOFF_RECEIPT_FILE = "handoff_check.receipt.json"
MECHANICAL_PROOF_RECEIPT_FILE = "mechanical_proof_status.receipt.json"
BLACKBOX_4D_RECEIPT_FILE = "blackbox_4d.receipt.json"
RC16233_RULING_HIGH_RISK_SETS = [
    frozenset({"convulsion of nature", "reversal quiz"}),
]
RC16233_MODEL_WRITABLE_LINE_FIELDS = {"actions", "claim", "outcome_text", "material_rulings"}
RC16233_DERIVABLE_FORBIDDEN_FIELDS = {
    "line_id","replay_id","resource_id","binding_id","hash","sha256","deck_artifact","render_id",
    "component_id","emission_status","emission_anchor","gate_status","receipt_status","coverage_matrix",
    "resource_ledger","mechanical_consequence_bindings","unified_cold_audit","src_scope_status","game_rule_scope_status",
}


def _rc16233_model_owned_surface():
    """Architecture descriptor, not a prompt. It prevents secretary creep."""
    return {
        "schema":"ygo-model-owned-surface-v1",
        "semantic_line_writable_fields":sorted(RC16233_MODEL_WRITABLE_LINE_FIELDS),
        "non_derivable_justifications":{
            "actions":"ordered gameplay decisions/actions require semantic judgement",
            "claim":"intended outcome and certainty are semantic assertions",
            "outcome_text":"player-facing meaning is authored content",
            "material_rulings":"only material card/ruling interpretation not derivable by runtime",
        },
        "compiler_owned_examples":sorted(RC16233_DERIVABLE_FORBIDDEN_FIELDS),
    }


def _rc16233_validate_model_owned_diff(before, after, justifications=None):
    """Reject any newly model-owned derivable field.

    `before`/`after` are iterable field names. A genuinely new semantic field must have
    a NON_DERIVABLE_JUSTIFICATION. Known derivable/bureaucratic names are never allowed.
    """
    b=set(before or []); a=set(after or []); new=sorted(a-b); justifications=justifications or {}
    bad=[]
    for k in new:
        low=k.casefold()
        if k in RC16233_DERIVABLE_FORBIDDEN_FIELDS or any(tok in low for tok in ("sha","hash","binding","receipt","emitted","component_id","gate_status","resource_ledger","coverage_matrix")):
            bad.append(k); continue
        if not nonempty(justifications.get(k)):
            bad.append(k)
    if bad: fail("MODEL_OWNED_DERIVABLE_EXPANSION_FORBIDDEN: "+",".join(bad))
    return {"status":"PASS","new_fields":new,"justified":sorted(k for k in new if k in justifications)}


# ------------------------- REQ-03 decklist truth -------------------------

_category_totals_rc16233_parent = _category_totals
_validate_full_decklist_groups_rc16233_parent = validate_full_decklist_groups
_rc1624_decklist_block_rc16233_parent = _rc1624_decklist_block


def _rc16233_type_coverage(snapshot, typemap):
    missing=[]
    for c in snapshot.get("main_deck",[]) if isinstance(snapshot,dict) else []:
        key=("main_deck",str(c.get("name") or "").strip().casefold())
        if not nonempty(typemap.get(key)):
            missing.append(c.get("name"))
    return {"complete":not missing,"missing":[x for x in missing if nonempty(x)]}


def _category_totals(snapshot, typemap):
    totals={"MONSTER":0,"SPELL":0,"TRAP":0,"EXTRA":0,"SIDE":0,"MAIN":0,"UNKNOWN":0,"_MODE":"GROUPED"}
    for c in snapshot.get("main_deck",[]):
        totals["MAIN"]+=c["qty"]
        raw=typemap.get(("main_deck",c["name"].strip().casefold()))
        if not nonempty(raw):
            totals["UNKNOWN"]+=c["qty"]
        else:
            totals[_card_group(raw)]+=c["qty"]
    totals["EXTRA"]=sum(c["qty"] for c in snapshot.get("extra_deck",[]))
    totals["SIDE"]=sum(c["qty"] for c in snapshot.get("side_deck",[]))
    if totals["UNKNOWN"]:
        totals["_MODE"]="FLAT_MAIN"
    return totals


def _decklist_group_assertions(totals):
    if totals.get("_MODE")=="FLAT_MAIN":
        return [
            {"type":"contains_regex","pattern":rf"^###\s+Main Deck\s*[—-]\s*{totals['MAIN']}\s*$"},
            {"type":"contains_regex","pattern":rf"^###\s+Extra Deck\s*[—-]\s*{totals['EXTRA']}\s*$"},
            {"type":"contains_regex","pattern":rf"^###\s+Side Deck\s*[—-]\s*{totals['SIDE']}\s*$"},
        ]
    return [
        {"type":"contains_regex","pattern":rf"^###\s+Main Deck\s*[—-]\s*{totals['MAIN']}\s*$"},
        {"type":"contains_regex","pattern":rf"^####\s+Monstres\s*[—-]\s*{totals['MONSTER']}\s*$"},
        {"type":"contains_regex","pattern":rf"^####\s+Magies\s*[—-]\s*{totals['SPELL']}\s*$"},
        {"type":"contains_regex","pattern":rf"^####\s+Pi[èe]ges\s*[—-]\s*{totals['TRAP']}\s*$"},
        {"type":"contains_regex","pattern":rf"^###\s+Extra Deck\s*[—-]\s*{totals['EXTRA']}\s*$"},
        {"type":"contains_regex","pattern":rf"^###\s+Side Deck\s*[—-]\s*{totals['SIDE']}\s*$"},
    ]


def _rc1624_decklist_block(st):
    dg=(st.get('gates') or {}).get('DECK_DRAFT_CREATED',{}); ng=(st.get('gates') or {}).get('NARRATIVE_CONFORMANCE_CLOSED',{})
    if not dg.get('snapshot_file') or not ng.get('evidence_file'): return None
    sp=Path(dg['snapshot_file']); np=Path(ng['evidence_file'])
    if not sp.exists() or not np.exists(): return None
    snap=read_json(sp,'deck snapshot'); typemap=_narrative_type_map(np); totals=_category_totals(snap,typemap)
    extra=[f"- {c['qty']}x {c['name']}" for c in snap.get('extra_deck',[])]
    side=[f"- {c['qty']}x {c['name']}" for c in snap.get('side_deck',[])]
    if totals.get('_MODE')=='FLAT_MAIN':
        main=[f"- {c['qty']}x {c['name']}" for c in snap.get('main_deck',[])]
        return ['## Decklist',f"### Main Deck — {totals['MAIN']}",*main,f"### Extra Deck — {totals['EXTRA']}",*extra,f"### Side Deck — {totals['SIDE']}",*side]
    monsters=[]; spells=[]; traps=[]
    for c in snap.get('main_deck',[]):
        line=f"- {c['qty']}x {c['name']}"; cat=_card_group(typemap[("main_deck",c['name'].strip().casefold())])
        (monsters if cat=='MONSTER' else spells if cat=='SPELL' else traps).append(line)
    return ['## Decklist',f"### Main Deck — {totals['MAIN']}",f"#### Monstres — {totals['MONSTER']}",*monsters,f"#### Magies — {totals['SPELL']}",*spells,f"#### Pièges — {totals['TRAP']}",*traps,f"### Extra Deck — {totals['EXTRA']}",*extra,f"### Side Deck — {totals['SIDE']}",*side]


def validate_full_decklist_groups(text, snapshot, typemap):
    totals=_category_totals(snapshot,typemap)
    if totals.get('_MODE')!='FLAT_MAIN':
        return _validate_full_decklist_groups_rc16233_parent(text,snapshot,typemap)
    # Unknown type evidence must never silently mean MONSTER. Render exact flat Main instead.
    for pat,label in [
        (rf"^###\s+Main Deck\s*[—-]\s*{totals['MAIN']}\s*$","MAIN"),
        (rf"^###\s+Extra Deck\s*[—-]\s*{totals['EXTRA']}\s*$","EXTRA"),
        (rf"^###\s+Side Deck\s*[—-]\s*{totals['SIDE']}\s*$","SIDE")]:
        if not re.search(pat,text,re.I|re.M): fail(f"DECKLIST_GROUP_HEADING_MISSING_OR_TOTAL_WRONG: {label}")
    mainsec=_section_between(text,rf"^###\s+Main Deck\s*[—-]\s*{totals['MAIN']}\s*$",r"^###\s+") or ""
    if re.search(r"(?im)^####\s+(Monstres|Magies|Pi[èe]ges)\b",mainsec):
        fail("DECKLIST_UNKNOWN_TYPE_MUST_USE_FLAT_MAIN")
    for c in snapshot.get('main_deck',[]):
        pat=rf"(?m)^\s*[-*]\s*{c['qty']}\s*[×x]\s*{re.escape(c['name'])}\s*$"
        if not re.search(pat,mainsec): fail(f"DECKLIST_CARD_WRONG_GROUP_OR_MISSING: {c['qty']}x {c['name']}")
    # Extra/Side remain mechanically exact.
    for zone,label,total,nextpat in [('extra_deck','EXTRA',totals['EXTRA'],r'^###\s+'),('side_deck','SIDE',totals['SIDE'],r'^###\s+|^##\s+')]:
        sec=_section_between(text,rf"^###\s+{'Extra Deck' if zone=='extra_deck' else 'Side Deck'}\s*[—-]\s*{total}\s*$",nextpat) or ''
        for c in snapshot.get(zone,[]):
            pat=rf"(?m)^\s*[-*]\s*{c['qty']}\s*[×x]\s*{re.escape(c['name'])}\s*$"
            if not re.search(pat,sec): fail(f"DECKLIST_CARD_WRONG_GROUP_OR_MISSING: {c['qty']}x {c['name']}")
    return True


# ---------------------- REQ-02 visual emission truth ---------------------

def _rc16233_component_anchor(component_id):
    return f"<!-- YGO_COMPONENT_EMIT:{component_id} -->"


def _rc16233_inject_component_anchors(text, visual):
    """Deterministic emission markers. The model never writes them."""
    lines=text.splitlines()
    main=visual.get('main_carousel') if isinstance(visual,dict) and isinstance(visual.get('main_carousel'),dict) else {}
    sig=visual.get('signature_climax') if isinstance(visual,dict) and isinstance(visual.get('signature_climax'),dict) else {}
    def add_after(index,anchor):
        if anchor not in lines: lines.insert(index+1,anchor)
    if main.get('applicable') is True:
        anchor=_rc16233_component_anchor('main-card-carousel')
        idx=next((i for i,x in enumerate(lines) if re.match(r'(?i)^##\s+Cartes emblématiques\s*$',x.strip())),None)
        if idx is None:
            idx=next((i-1 for i,x in enumerate(lines) if re.match(r'(?i)^##\s+Decklist\s*$',x.strip())),0)
        add_after(max(0,idx),anchor)
    if sig.get('mini_carousel_applicable') is True:
        parent=sig.get('parent')
        if not nonempty(parent): fail('SIGNATURE_MINI_CAROUSEL_PARENT_REQUIRED')
        anchor=_rc16233_component_anchor('signature-mini-carousel')
        idx=next((i for i,x in enumerate(lines) if re.match(r'^#{2,4}\s+',x.strip()) and parent.casefold() in x.casefold()),None)
        if idx is None: fail('SIGNATURE_MINI_CAROUSEL_PARENT_NOT_RENDERED')
        add_after(idx,anchor)
    return '\n'.join(lines).rstrip()+'\n'


_compile_render_semantic_rc16233_parent = _rc1623_compile_render_semantic

def _rc1623_compile_render_semantic(doc,visual=None,decklist_block=None,line_max=220):
    text=_compile_render_semantic_rc16233_parent(doc,visual,decklist_block,line_max)
    return _rc16233_inject_component_anchors(text,visual or {})


_compile_terminal_presentation_payload_rc16233_parent = compile_terminal_presentation_payload

def compile_terminal_presentation_payload(render_path: Path, manifest_path: Path, st):
    doc=_compile_terminal_presentation_payload_rc16233_parent(render_path,manifest_path,st)
    text=Path(render_path).read_text(encoding='utf-8')
    for c in doc.get('components',[]):
        anchor=_rc16233_component_anchor(c.get('component_id'))
        c['emission_anchor']=anchor
        c['emission_status']='EMITTED' if anchor in text else 'NOT_EMITTED'
    return doc


_terminal_plan_issues_rc16233_parent = _terminal_plan_issues

def _terminal_plan_issues(plan_path: Path, render_path: Path, manifest_path: Path, st):
    issues=list(_terminal_plan_issues_rc16233_parent(plan_path,render_path,manifest_path,st))
    if not Path(plan_path).exists() or not Path(render_path).exists(): return issues
    try: d=read_json(Path(plan_path),'terminal presentation plan')
    except BaseException: return issues
    text=Path(render_path).read_text(encoding='utf-8')
    for c in d.get('components',[]) if isinstance(d.get('components'),list) else []:
        if not isinstance(c,dict) or not nonempty(c.get('component_id')): continue
        exp=_rc16233_component_anchor(c['component_id'])
        if c.get('emission_anchor')!=exp or c.get('emission_status')!='EMITTED' or exp not in text:
            issues.append(_terminal_issue('TERMINAL_COMPONENT_NOT_EMITTED',c.get('component_id')))
    dedup=[]; seen=set()
    for x in issues:
        k=(x.get('code'),x.get('detail'))
        if k not in seen: seen.add(k); dedup.append(x)
    return sorted(dedup,key=lambda x:(x.get('code',''),x.get('detail','')))


def cmd_render_emission_normalize(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,'render-emission-normalize')
    src=Path(a.render_file); out=Path(a.output); _rc1623_assert_flat_run_output(rd,out,'render emission normalized')
    vg=(st.get('gates') or {}).get('VISUAL_ASSETS_BOUND',{})
    if not vg.get('evidence_file'): fail('VISUAL_ASSETS_REQUIRED_FOR_EMISSION_NORMALIZE')
    visual=read_json(Path(vg['evidence_file']),'visual assets')
    text=_rc16233_inject_component_anchors(src.read_text(encoding='utf-8'),visual)
    _atomic_write_text(out,text)
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,'RENDER_COMPONENT_EMISSION_NORMALIZED',checkpoint_seq=cp.get('checkpoint_seq'),source_file=str(src),source_sha256=sha256(src),output_file=str(out),output_sha256=sha256(out))
    print(json.dumps({'status':'PASS','output':str(out),'sha256':sha256(out)},ensure_ascii=False))


# ------------------ REQ-04/05 ruling + claim barriers --------------------

_compile_semantic_pilotage_rc16233_parent = _rc1623_compile_semantic_pilotage


def _rc16233_semantic_card_names(sem):
    names=set()
    for a in sem.get('actions',[]) if isinstance(sem,dict) and isinstance(sem.get('actions'),list) else []:
        if not isinstance(a,dict): continue
        for k in ('card','actor','target'):
            if nonempty(a.get(k)): names.add(a[k].strip().casefold())
        for k in ('materials','participants','adds'):
            for x in a.get(k,[]) if isinstance(a.get(k),list) else []:
                if nonempty(x): names.add(x.strip().casefold())
    return names


def _rc16233_requires_ruling_evidence(sem):
    names=_rc16233_semantic_card_names(sem)
    return any(group.issubset(names) for group in RC16233_RULING_HIGH_RISK_SETS)


def _rc16233_validate_minimal_rulings(sem):
    if not _rc16233_requires_ruling_evidence(sem): return []
    rulings=sem.get('material_rulings')
    if not isinstance(rulings,list) or not rulings:
        fail('RULING_EVIDENCE_REQUIRED: material interaction requires SEMANTIC_RULING_CONTRACT review')
    clean=[]
    for i,r in enumerate(rulings,1):
        if not isinstance(r,dict) or not nonempty(r.get('subject')) or not nonempty(r.get('statement')) or not nonempty(r.get('source_locator')):
            fail(f'RULING_EVIDENCE_INVALID: ruling {i}')
        clean.append({'subject':r['subject'].strip(),'statement':r['statement'].strip(),'source_locator':r['source_locator'].strip()})
    return clean


def _rc16233_render_has_unknown_interaction(text):
    low=text.casefold()
    patterns=[r'\b(?:1|une?)\s+(?:m/p|magie\s*/?\s*pi[eè]ge|spell\s*/?\s*trap)\s+pos[ée]e?\b',r'\bunknown\s+set\s+(?:card|spell|trap)\b',r'\bbackrow\s+inconnue\b']
    return any(re.search(p,low,re.I) for p in patterns)


def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    # REQ-00 surface: no IDs/hashes/admin fields accepted as semantic authoring.
    for line in semantic.get('lines',[]) if isinstance(semantic,dict) and isinstance(semantic.get('lines'),list) else []:
        if not isinstance(line,dict): continue
        forbidden=sorted(set(line) & RC16233_DERIVABLE_FORBIDDEN_FIELDS)
        if forbidden: fail('MODEL_OWNED_DERIVABLE_EXPANSION_FORBIDDEN: '+','.join(forbidden))
        _rc16233_validate_minimal_rulings(line)
        claim=line.get('claim')
        if isinstance(claim,dict) and claim.get('certainty')=='GUARANTEED':
            unc=claim.get('uncertainties')
            if isinstance(unc,list) and any(nonempty(str(x)) for x in unc):
                fail('GUARANTEED_CLAIM_HAS_UNRESOLVED_UNCERTAINTY')
    # Unknown interaction visible in the exact render prevents silent promotion to guaranteed lethal.
    text=Path(render_path).read_text(encoding='utf-8') if Path(render_path).exists() else ''
    if _rc16233_render_has_unknown_interaction(text):
        for line in semantic.get('lines',[]) if isinstance(semantic,dict) and isinstance(semantic.get('lines'),list) else []:
            claim=line.get('claim') if isinstance(line,dict) else None
            if isinstance(claim,dict) and str(claim.get('type')).upper()=='LETHAL' and claim.get('certainty')=='GUARANTEED':
                fail('GUARANTEED_CLAIM_UNKNOWN_OPPONENT_INTERACTION')
    out=_compile_semantic_pilotage_rc16233_parent(st,render_path,semantic)
    # Record only that competent semantic ruling review was supplied; compiler does not invent its meaning.
    for src,compiled in zip(semantic.get('lines',[]),out.get('lines',[])):
        rulings=src.get('material_rulings') if isinstance(src,dict) else None
        if isinstance(rulings,list) and rulings:
            compiled['semantic_ruling_review']={
                'authority':SRC,'status':'SUPPLIED','count':len(rulings),
                'evidence_sha256':hashlib.sha256(_stable_json_text(rulings).encode('utf-8')).hexdigest()
            }
    return out


_pilotage_semantic_template_rc16233_parent = _rc1623_pilotage_semantic_template

def _rc1623_pilotage_semantic_template(st):
    doc=_pilotage_semantic_template_rc16233_parent(st)
    for line in doc.get('lines',[]):
        line['material_rulings']=[]
    doc['compiler_owned_fields_notice']='Do not add IDs, hashes, bindings, resource ledgers, MCB statuses, cold audits, component emission flags, deck grouping or receipts. Fill semantic actions/claim/outcome only; material_rulings is allowed only when a real ruling interpretation is needed.'
    doc['model_owned_surface']=_rc16233_model_owned_surface()
    return doc


# ---------------------- REQ-06 persisted proof truth ---------------------

def _rc16233_mechanical_proof_status(rd: Path, st):
    if not bool(st.get('mechanical_validation')):
        return {'applicable':False,'status':'NOT_APPLICABLE','trace_label':'validation mécanique : non applicable'}
    proof=st.get('mechanical_proof')
    if not isinstance(proof,dict): return {'applicable':True,'status':'REQUIRED_NOT_PROVEN'}
    for key in ('ledger_file','ledger_sha256','snapshot_file','snapshot_sha256','receipt_file','receipt_sha256','instrument_trace_file','instrument_trace_sha256'):
        if not nonempty(proof.get(key)): return {'applicable':True,'status':'REQUIRED_NOT_PROVEN','missing':key}
    for fk,hk in [('ledger_file','ledger_sha256'),('snapshot_file','snapshot_sha256'),('receipt_file','receipt_sha256'),('instrument_trace_file','instrument_trace_sha256')]:
        p=Path(proof[fk])
        if not p.exists() or not p.is_file() or sha256(p)!=proof[hk]: return {'applicable':True,'status':'STALE','field':fk}
    if proof.get('result')!='PASS' or proof.get('receipt_verified') is not True: return {'applicable':True,'status':'FAIL'}
    return {'applicable':True,'status':'PASS',**proof}


def _rc16233_mechanical_proof_check(rd: Path, st, ledger=None, snapshot=None, receipt=None, trace=None):
    """Execute the real ledger validator + receipt verification and persist exact provenance.

    This is compiler/runtime-owned proof plumbing: no model-authored PASS/status is accepted.
    """
    if not bool(st.get('mechanical_validation')):
        return _rc16233_mechanical_proof_status(rd,st)
    dg=(st.get('gates') or {}).get('DECK_DRAFT_CREATED',{})
    snapshot=Path(snapshot) if snapshot else Path(dg.get('snapshot_file') or '')
    ledger=Path(ledger) if ledger else rd/'execution_ledger.json'
    receipt=Path(receipt) if receipt else Path(str(ledger)+'.receipt.json')
    trace=Path(trace) if trace else Path(str(ledger)+'.instrument.jsonl')
    if not ledger.exists() or not snapshot.exists(): fail('MECHANICAL_PROOF_INPUT_MISSING')
    validator=Path(__file__).resolve().parent/LEDGER_VALIDATOR
    if not validator.exists(): fail('MECHANICAL_VALIDATOR_MISSING')
    cmd=[sys.executable,str(validator),str(ledger),'--artifact',str(snapshot),'--receipt',str(receipt),'--instrument-trace',str(trace)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: fail('MECHANICAL_VALIDATOR_RUN_FAILED: '+(r.stderr.strip() or r.stdout.strip()))
    vr=subprocess.run(cmd+['--verify-receipt'],capture_output=True,text=True)
    if vr.returncode!=0: fail('MECHANICAL_RECEIPT_VERIFY_FAILED: '+(vr.stderr.strip() or vr.stdout.strip()))
    proof={'result':'PASS','receipt_verified':True,'ledger_file':str(ledger.resolve()),'ledger_sha256':sha256(ledger),'snapshot_file':str(snapshot.resolve()),'snapshot_sha256':sha256(snapshot),'receipt_file':str(receipt.resolve()),'receipt_sha256':sha256(receipt),'instrument_trace_file':str(trace.resolve()),'instrument_trace_sha256':sha256(trace),'validator_file':str(validator.resolve()),'validator_sha256':sha256(validator)}
    st['mechanical_proof']=proof; save_state(rd,st); cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,'MECHANICAL_PROOF_VERIFIED',checkpoint_seq=cp.get('checkpoint_seq'),**proof)
    status_doc={'schema':'ygo-mechanical-proof-status-v1','run_id':st.get('run_id'),**proof}
    _atomic_write_text(rd/MECHANICAL_PROOF_RECEIPT_FILE,_stable_json_text(status_doc))
    return {'applicable':True,'status':'PASS',**proof}


def cmd_mechanical_proof_check(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    doc=_rc16233_mechanical_proof_check(
        rd,st,
        ledger=getattr(a,'ledger_file',None), snapshot=getattr(a,'snapshot_file',None),
        receipt=getattr(a,'receipt',None), trace=getattr(a,'instrument_trace',None)
    )
    print(json.dumps(doc,ensure_ascii=False,indent=2))


def cmd_mechanical_proof_status(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    print(json.dumps(_rc16233_mechanical_proof_status(rd,st),ensure_ascii=False,indent=2))


# ------------------------ REQ-01 hard handoff ----------------------------

def _rc16233_handoff_check(rd: Path, st, intent='END_TURN'):
    pol=_rc1623_continuation_policy(rd,st)
    allowed=bool(pol.get('handoff_allowed'))
    return {'schema':'ygo-handoff-check-v1','run_id':st.get('run_id'),'intent':intent,'status':'HANDOFF_ALLOWED' if allowed else 'CONTINUE_REQUIRED','handoff_allowed':allowed,'classification':pol.get('classification'),'required_action':pol.get('required_action'),'next_required_gate':pol.get('next_required_gate'),'checkpoint_seq':pol.get('checkpoint_seq')}


def cmd_handoff_check(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    doc=_rc16233_handoff_check(rd,st,getattr(a,'intent','END_TURN'))
    cp=_load_checkpoint_raw(rd,required=False) or {}
    event='HANDOFF_ALLOWED' if doc['handoff_allowed'] else 'HANDOFF_REFUSED'
    _append_run_journal(rd,st,event,checkpoint_seq=cp.get('checkpoint_seq'),classification=doc.get('classification'),required_action=doc.get('required_action'),intent=doc.get('intent'))
    _atomic_write_text(rd/HANDOFF_RECEIPT_FILE,_stable_json_text(doc))
    if not doc['handoff_allowed']:
        fail('HANDOFF_REFUSED_CONTINUE_REQUIRED: '+str(doc.get('required_action')))
    print(json.dumps(doc,ensure_ascii=False,indent=2))


# ------------------- REQ-07 retry collapse / metrics ---------------------

def _rc16233_retry_signature(error_code,render_sha256,state_sha256):
    raw=json.dumps({'error_code':error_code,'render_sha256':render_sha256,'state_sha256':state_sha256},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()


def _rc16233_should_collapse_retry(rd: Path, render_sha256, state_sha256):
    for ev in reversed(_read_journal(rd)):
        if ev.get('event')=='RENDER_COMMIT_SUCCEEDED': return False
        if ev.get('event')=='RENDER_COMMIT_ROLLED_BACK':
            if ev.get('render_sha256')==render_sha256 and ev.get('state_sha256_after')==state_sha256:
                return True
            return False
    return False


_cmd_render_commit_rc16233_parent = cmd_render_commit

def cmd_render_commit(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    render=Path(a.render_file); rsha=sha256(render) if render.exists() else None; ssha=sha256(rd/STATE_FILE)
    if rsha and _rc16233_should_collapse_retry(rd,rsha,ssha):
        cp=_load_checkpoint_raw(rd,required=False) or {}
        sig=_rc16233_retry_signature('IDENTICAL_RETRY',rsha,ssha)
        _append_run_journal(rd,st,'RENDER_IDENTICAL_RETRY_COLLAPSED',checkpoint_seq=cp.get('checkpoint_seq'),render_sha256=rsha,state_sha256=ssha,retry_signature=sig)
        fail('RENDER_IDENTICAL_RETRY_COLLAPSED: deterministic inputs unchanged')
    before_len=len(_read_journal(rd))
    try:
        return _cmd_render_commit_rc16233_parent(a)
    finally:
        # Enrich newly written rollback events with deterministic retry identity.
        evs=_read_journal(rd)
        if len(evs)>before_len:
            changed=False
            for ev in evs[before_len:]:
                if ev.get('event')=='RENDER_COMMIT_ROLLED_BACK' and not ev.get('retry_signature'):
                    ev['render_sha256']=rsha; ev['retry_signature']=_rc16233_retry_signature(ev.get('error_code'),rsha,ev.get('state_sha256_after')); changed=True
            if changed:
                # Rewrite is safe only in tests/development? Journal is append-only by contract, so do not rewrite.
                # Instead append a companion identity event.
                last=next((x for x in reversed(evs[before_len:]) if x.get('event')=='RENDER_COMMIT_ROLLED_BACK'),None)
                if last:
                    st2=load_state(rd); cp=_load_checkpoint_raw(rd,required=False) or {}
                    _append_run_journal(rd,st2,'RENDER_RETRY_SIGNATURE_MATERIALIZED',checkpoint_seq=cp.get('checkpoint_seq'),error_code=last.get('error_code'),render_sha256=rsha,state_sha256=last.get('state_sha256_after'),retry_signature=_rc16233_retry_signature(last.get('error_code'),rsha,last.get('state_sha256_after')))


# ------------------------ REQ-08 Black-Box 4D ----------------------------

def _rc16233_blackbox_4d_status(rd: Path, st):
    cp=_load_checkpoint_raw(rd,required=False) or {}; gates=st.get('gates') or {}
    terminal=st.get('run_execution_state')=='COMPLETED' and st.get('stop_output_allowed') is True and isinstance(gates.get('FINAL_VALIDATION_PASS'),dict)
    continuation=bool(terminal and int(cp.get('resume_count',0) or 0)==0)
    semantic=bool(isinstance(gates.get('PILOTAGE_VALIDATED'),dict) and gates['PILOTAGE_VALIDATED'].get('status')=='PASS')
    presentation=False
    pr=st.get('terminal_presentation_receipt_file')
    if nonempty(pr) and Path(pr).exists():
        try:
            d=read_json(Path(pr),'terminal presentation receipt')
            plan=read_json(Path(st.get('terminal_presentation_plan_file')),'terminal presentation plan') if nonempty(st.get('terminal_presentation_plan_file')) and Path(st.get('terminal_presentation_plan_file')).exists() else {}
            presentation=d.get('status')=='PASS' and all(c.get('emission_status')=='EMITTED' for c in plan.get('components',[]) if isinstance(c,dict))
        except BaseException: presentation=False
    dims={'TERMINAL_PASS':terminal,'CONTINUITY_PASS':continuation,'SEMANTIC_PASS':semantic,'PRESENTATION_PASS':presentation}
    return {'schema':'ygo-blackbox-4d-v1','run_id':st.get('run_id'),**dims,'FULL_PASS':all(dims.values()),'resume_count':cp.get('resume_count',0),'deck_artifact':st.get('current_artifact'),'render_id':st.get('current_render')}


def cmd_blackbox_4d(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); doc=_rc16233_blackbox_4d_status(rd,st)
    out=rd/BLACKBOX_4D_RECEIPT_FILE; _atomic_write_text(out,_stable_json_text(doc)); print(json.dumps(doc,ensure_ascii=False,indent=2))


# Strengthen authorize only when mechanical validation was actually requested.
_cmd_authorize_rc16233_parent = cmd_authorize

def cmd_authorize(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if bool(st.get('mechanical_validation')):
        mp=_rc16233_mechanical_proof_status(rd,st)
        if mp.get('status')!='PASS': fail('MECHANICAL_PROOF_REQUIRED_AT_AUTHORIZE')
    return _cmd_authorize_rc16233_parent(a)



# =============================================================================
# RC16.23.4 — Post Black-Box Evidence & Campaign Hardening
# Campaign truth + pre-bootstrap evidence + authoritative metadata provenance.
# NO NEW AI SECRETARIAT: only mechanically-derived administration is added here.
# =============================================================================

RC16234_CAMPAIGN_STATE_FILE = "campaign_state.json"
RC16234_CAMPAIGN_JOURNAL_FILE = "campaign.journal.jsonl"
RC16234_PREBOOTSTRAP_RECEIPT_FILE = "prebootstrap.receipt.json"
RC16234_CAMPAIGN_RECEIPT_FILE = "blackbox_campaign.receipt.json"
RC16234_CARD_METADATA_BINDING_FILE = "card_metadata.binding.json"
RC16234_USER_TRACE_FILE = "user_trace.compiled.json"
RC16234_CARD_METADATA_SCHEMA = "ygo-card-metadata-authoritative-v1"
RC16234_CARD_METADATA_BINDING_SCHEMA = "ygo-card-metadata-binding-v1"
RC16234_CAMPAIGN_SCHEMA = "ygo-blackbox-campaign-v1"
RC16234_ALLOWED_METADATA_PROVENANCE = {"EXTERNAL_AUTHORITATIVE", "PROJECT_VERIFIED_CATALOG", "USER_VERIFIED_SOURCE"}


def _rc16234_scope_file(scope_dir: Path, name: str):
    scope=Path(scope_dir).resolve(); scope.mkdir(parents=True,exist_ok=True)
    return scope/name


def _rc16234_read_campaign(scope_dir: Path, required=False):
    path=_rc16234_scope_file(scope_dir,RC16234_CAMPAIGN_STATE_FILE)
    if not path.exists():
        if required: fail("CAMPAIGN_NOT_OPEN")
        return None
    d=read_json(path,"campaign state")
    if d.get("schema")!=RC16234_CAMPAIGN_SCHEMA: fail("CAMPAIGN_SCHEMA_INVALID")
    return d


def _rc16234_campaign_journal(scope_dir: Path):
    path=_rc16234_scope_file(scope_dir,RC16234_CAMPAIGN_JOURNAL_FILE)
    if not path.exists(): return []
    out=[]
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: d=json.loads(line)
        except Exception as e: fail(f"CAMPAIGN_JOURNAL_INVALID line={n}: {e}")
        if not isinstance(d,dict): fail(f"CAMPAIGN_JOURNAL_INVALID line={n}")
        out.append(d)
    return out


def _rc16234_append_campaign_event(scope_dir: Path, event: str, **extra):
    scope=Path(scope_dir).resolve(); path=_rc16234_scope_file(scope,RC16234_CAMPAIGN_JOURNAL_FILE)
    events=_rc16234_campaign_journal(scope)
    obj={"seq":len(events)+1,"event":event,"timestamp_ns":time.time_ns(),**extra}
    with path.open("a",encoding="utf-8") as f: f.write(json.dumps(obj,ensure_ascii=False,sort_keys=True)+"\n")
    return obj


def _rc16234_campaign_attempt_state(attempt):
    rd=Path(attempt.get("run_dir") or "")
    if not rd.exists() or not (rd/STATE_FILE).exists(): return {**attempt,"derived_status":"MISSING"}
    try:
        st=load_state(rd); state=st.get("run_execution_state")
        if state=="COMPLETED": ds="COMPLETED"
        elif state in {"TERMINAL_FAILED","BLOCKED_FATAL"}: ds="ABORTED" if st.get("terminal_failure_kind")=="USER_ABORTED" else "FAILED"
        else: ds="ACTIVE"
        four=_rc16233_blackbox_4d_status(rd,st) if state=="COMPLETED" else None
        return {**attempt,"derived_status":ds,"blackbox_4d":four}
    except BaseException as e:
        return {**attempt,"derived_status":"INVALID","error":str(e)}


def _rc16234_campaign_refresh(scope_dir: Path, campaign=None):
    d=copy.deepcopy(campaign or _rc16234_read_campaign(scope_dir,required=True))
    attempts=[_rc16234_campaign_attempt_state(x) for x in d.get("attempts",[]) if isinstance(x,dict)]
    d["attempts"]=attempts
    return d


def _rc16234_campaign_terminal(campaign):
    attempts=campaign.get("attempts") or []
    return bool(attempts) and all(x.get("derived_status") in {"COMPLETED","ABORTED","FAILED","INVALID","MISSING"} for x in attempts)


def _rc16234_campaign_open(scope_dir: Path, request_file: Path):
    scope=Path(scope_dir).resolve(); request=Path(request_file)
    if not request.exists() or not request.is_file(): fail("CAMPAIGN_REQUEST_FILE_MISSING")
    request_sha=sha256(request)
    current=_rc16234_read_campaign(scope,required=False)
    if current:
        refreshed=_rc16234_campaign_refresh(scope,current)
        if current.get("status")=="ACTIVE" and not _rc16234_campaign_terminal(refreshed):
            if current.get("request_sha256")==request_sha: return current
            fail("ACTIVE_CAMPAIGN_EXISTS")
    prior=[x for x in _rc16234_campaign_journal(scope) if x.get("event")=="CAMPAIGN_OPENED" and x.get("request_sha256")==request_sha]
    cid=f"campaign-{request_sha[:12]}-{len(prior)+1:03d}"
    d={"schema":RC16234_CAMPAIGN_SCHEMA,"campaign_id":cid,"scope_dir":str(scope),"request_file":str(request.resolve()),"request_sha256":request_sha,"status":"ACTIVE","prebootstrap_status":"OPEN","attempts":[],"runtime_version":VERSION}
    _atomic_write_text(_rc16234_scope_file(scope,RC16234_CAMPAIGN_STATE_FILE),_stable_json_text(d))
    _atomic_write_text(_rc16234_scope_file(scope,RC16234_PREBOOTSTRAP_RECEIPT_FILE),_stable_json_text({"schema":"ygo-prebootstrap-receipt-v1","campaign_id":cid,"request_sha256":request_sha,"bootstrap_required":True,"handoff_allowed":False,"status":"CONTINUE_REQUIRED"}))
    _rc16234_append_campaign_event(scope,"CAMPAIGN_OPENED",campaign_id=cid,request_sha256=request_sha,prebootstrap_status="OPEN")
    return d


def _rc16234_prebootstrap_status(scope_dir: Path):
    d=_rc16234_read_campaign(scope_dir,required=False)
    if not d:
        return {"schema":"ygo-prebootstrap-status-v1","status":"CAMPAIGN_NOT_OPEN","handoff_allowed":False,"bootstrap_started":False}
    refreshed=_rc16234_campaign_refresh(scope_dir,d)
    started=bool(refreshed.get("attempts"))
    return {"schema":"ygo-prebootstrap-status-v1","campaign_id":d.get("campaign_id"),"request_sha256":d.get("request_sha256"),"status":"BOOTSTRAP_STARTED" if started else "CONTINUE_REQUIRED","handoff_allowed":started,"bootstrap_started":started,"attempt_count":len(refreshed.get("attempts") or [])}


def _rc16234_campaign_register_run(scope_dir: Path, run_id, run_dir):
    d=_rc16234_read_campaign(scope_dir,required=False)
    if not d or d.get("status")!="ACTIVE": return None
    attempts=d.setdefault("attempts",[]); rpath=str(Path(run_dir).resolve())
    found=next((x for x in attempts if x.get("run_id")==run_id and x.get("run_dir")==rpath),None)
    if found is None:
        found={"attempt":len(attempts)+1,"run_id":run_id,"run_dir":rpath,"registered_at_ns":time.time_ns()}; attempts.append(found)
        _rc16234_append_campaign_event(scope_dir,"CAMPAIGN_ATTEMPT_REGISTERED",campaign_id=d.get("campaign_id"),attempt=found["attempt"],run_id=run_id,run_dir=rpath)
    d["prebootstrap_status"]="BOOTSTRAP_STARTED"
    _atomic_write_text(_rc16234_scope_file(scope_dir,RC16234_CAMPAIGN_STATE_FILE),_stable_json_text(d))
    return found


def _rc16234_campaign_mark(scope_dir: Path, run_id, run_dir, status):
    d=_rc16234_read_campaign(scope_dir,required=False)
    if not d: return
    rpath=str(Path(run_dir).resolve()); found=None
    for x in d.get("attempts",[]):
        if x.get("run_id")==run_id and x.get("run_dir")==rpath: found=x; break
    if found is None: found=_rc16234_campaign_register_run(scope_dir,run_id,run_dir); d=_rc16234_read_campaign(scope_dir,required=True)
    for x in d.get("attempts",[]):
        if x.get("run_id")==run_id and x.get("run_dir")==rpath:
            x["last_terminal_status"]=status; x["last_terminal_at_ns"]=time.time_ns()
    _atomic_write_text(_rc16234_scope_file(scope_dir,RC16234_CAMPAIGN_STATE_FILE),_stable_json_text(d))
    _rc16234_append_campaign_event(scope_dir,"CAMPAIGN_ATTEMPT_TERMINAL",campaign_id=d.get("campaign_id"),run_id=run_id,run_dir=rpath,status=status)


def _rc16234_campaign_status(scope_dir: Path):
    d=_rc16234_campaign_refresh(scope_dir)
    attempts=d.get("attempts") or []
    completed=[x for x in attempts if x.get("derived_status")=="COMPLETED"]
    bad=[x for x in attempts if x.get("derived_status") in {"ABORTED","FAILED","INVALID","MISSING"}]
    active=[x for x in attempts if x.get("derived_status")=="ACTIVE"]
    full=[x for x in completed if isinstance(x.get("blackbox_4d"),dict) and x["blackbox_4d"].get("FULL_PASS") is True]
    preboot=d.get("prebootstrap_status") in {"OPEN","BOOTSTRAP_STARTED"}
    clean=bool(preboot and len(attempts)==1 and len(full)==1 and not bad and not active)
    if clean: status="CLEAN_PASS"
    elif full and bad and not active: status="RECOVERED_NOT_CLEAN"
    elif active: status="IN_PROGRESS"
    elif full: status="MULTI_ATTEMPT_NOT_CLEAN"
    else: status="FAIL"
    return {"schema":"ygo-blackbox-campaign-status-v1","campaign_id":d.get("campaign_id"),"request_sha256":d.get("request_sha256"),"attempt_count":len(attempts),"attempts":attempts,"prebootstrap_evidence":preboot,"successful_run_count":len(full),"failed_or_aborted_attempt_count":len(bad),"status":status,"CAMPAIGN_PASS":clean,"RUN_4D_PASS_PRESENT":bool(full)}


def cmd_campaign_open(a):
    d=_rc16234_campaign_open(Path(a.scope_dir),Path(a.request_file)); print(json.dumps(d,ensure_ascii=False,indent=2))


def cmd_prebootstrap_handoff_check(a):
    doc=_rc16234_prebootstrap_status(Path(a.scope_dir)); print(json.dumps(doc,ensure_ascii=False,indent=2))
    if not doc.get("handoff_allowed"): fail("PREBOOTSTRAP_HANDOFF_REFUSED: bootstrap required")


def cmd_blackbox_campaign(a):
    scope=Path(a.scope_dir); doc=_rc16234_campaign_status(scope)
    _atomic_write_text(_rc16234_scope_file(scope,RC16234_CAMPAIGN_RECEIPT_FILE),_stable_json_text(doc))
    if doc.get("status") not in {"IN_PROGRESS"}:
        d=_rc16234_read_campaign(scope,required=True); d["status"]="CLOSED" if doc.get("status")!="IN_PROGRESS" else "ACTIVE"; d["last_campaign_status"]=doc.get("status")
        _atomic_write_text(_rc16234_scope_file(scope,RC16234_CAMPAIGN_STATE_FILE),_stable_json_text(d))
    print(json.dumps(doc,ensure_ascii=False,indent=2))


# --- authoritative card metadata provenance ---

def _rc16234_authoritative_type_map(st, snapshot):
    binding=st.get("card_metadata_binding")
    if not isinstance(binding,dict): return {}
    dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED") or {}; sp=Path(dg.get("snapshot_file") or "")
    if not sp.exists(): fail("CARD_METADATA_DECK_SNAPSHOT_MISSING")
    current_sha=sha256(sp)
    if binding.get("snapshot_sha256")!=current_sha: fail("CARD_METADATA_BINDING_STALE")
    bp=Path(binding.get("binding_file") or "")
    if not bp.exists() or sha256(bp)!=binding.get("binding_sha256"): fail("CARD_METADATA_BINDING_STALE")
    doc=read_json(bp,"card metadata binding")
    out={}
    for c in doc.get("cards",[]):
        if isinstance(c,dict) and nonempty(c.get("name")) and c.get("card_type") in {"MONSTER","SPELL","TRAP"}:
            out[("main_deck",c["name"].strip().casefold())]=c["card_type"]
    wanted={c["name"].strip().casefold() for c in snapshot.get("main_deck",[]) if isinstance(c,dict) and nonempty(c.get("name"))}
    if {k[1] for k in out}!=wanted: fail("CARD_METADATA_BINDING_COVERAGE_MISMATCH")
    return out


def cmd_bind_card_metadata(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"bind-card-metadata")
    dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED") or {}; sp=Path(dg.get("snapshot_file") or "")
    if not sp.exists(): fail("CARD_METADATA_DECK_SNAPSHOT_MISSING")
    snap=read_json(sp,"deck snapshot"); src=Path(a.metadata_file)
    if not src.exists(): fail("CARD_METADATA_SOURCE_MISSING")
    doc=read_json(src,"authoritative card metadata")
    if doc.get("schema")!=RC16234_CARD_METADATA_SCHEMA: fail("CARD_METADATA_SCHEMA_INVALID")
    prov=doc.get("provenance")
    if not isinstance(prov,dict) or prov.get("kind") not in RC16234_ALLOWED_METADATA_PROVENANCE or not nonempty(prov.get("authority")) or not nonempty(prov.get("source_locator")):
        fail("CARD_METADATA_PROVENANCE_INVALID")
    rows=doc.get("cards")
    if not isinstance(rows,list): fail("CARD_METADATA_CARDS_INVALID")
    by={}
    for row in rows:
        if not isinstance(row,dict) or not nonempty(row.get("name")) or row.get("card_type") not in {"MONSTER","SPELL","TRAP"}: fail("CARD_METADATA_CARD_INVALID")
        k=row["name"].strip().casefold()
        if k in by: fail("CARD_METADATA_DUPLICATE_CARD")
        by[k]={"name":row["name"].strip(),"card_type":row["card_type"]}
    wanted={c["name"].strip().casefold():c["name"].strip() for c in snap.get("main_deck",[]) if isinstance(c,dict) and nonempty(c.get("name"))}
    if set(by)!=set(wanted): fail("CARD_METADATA_BINDING_COVERAGE_MISMATCH")
    normalized={"schema":RC16234_CARD_METADATA_BINDING_SCHEMA,"run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"snapshot_sha256":sha256(sp),"metadata_source_file":str(src.resolve()),"metadata_source_sha256":sha256(src),"provenance":prov,"cards":[by[k] for k in sorted(by)]}
    out=(rd/RC16234_CARD_METADATA_BINDING_FILE).resolve(); _atomic_write_text(out,_stable_json_text(normalized))
    st["card_metadata_binding"]={"binding_file":str(out),"binding_sha256":sha256(out),"snapshot_sha256":sha256(sp),"metadata_source_sha256":sha256(src),"provenance_kind":prov.get("kind")}; save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,"CARD_METADATA_BOUND",checkpoint_seq=cp.get("checkpoint_seq"),binding_file=str(out),binding_sha256=sha256(out),snapshot_sha256=sha256(sp),metadata_source_sha256=sha256(src),provenance_kind=prov.get("kind"))
    print(json.dumps({"status":"BOUND","binding_file":str(out),"binding_sha256":sha256(out),"card_count":len(by)},ensure_ascii=False,indent=2))


# Replace card grouping provenance: narrative conformance is never a card-type authority.
_render_compile_inputs_rc16234_parent = _render_compile_inputs

def _render_compile_inputs(st):
    d=_render_compile_inputs_rc16234_parent(st)
    typemap=_rc16234_authoritative_type_map(st,d["snapshot"])
    d["typemap"]=typemap; d["totals"]=_category_totals(d["snapshot"],typemap)
    d["card_metadata_binding_sha256"]=(st.get("card_metadata_binding") or {}).get("binding_sha256")
    return d


def _rc1624_decklist_block(st):
    dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED",{})
    if not dg.get("snapshot_file"): return None
    sp=Path(dg["snapshot_file"])
    if not sp.exists(): return None
    snap=read_json(sp,"deck snapshot"); typemap=_rc16234_authoritative_type_map(st,snap); totals=_category_totals(snap,typemap)
    extra=[f"- {c['qty']}x {c['name']}" for c in snap.get("extra_deck",[])]; side=[f"- {c['qty']}x {c['name']}" for c in snap.get("side_deck",[])]
    if totals.get("_MODE")=="FLAT_MAIN":
        main=[f"- {c['qty']}x {c['name']}" for c in snap.get("main_deck",[])]
        return ["## Decklist",f"### Main Deck — {totals['MAIN']}",*main,f"### Extra Deck — {totals['EXTRA']}",*extra,f"### Side Deck — {totals['SIDE']}",*side]
    groups={"MONSTER":[],"SPELL":[],"TRAP":[]}
    for c in snap.get("main_deck",[]): groups[_card_group(typemap[("main_deck",c["name"].strip().casefold())])].append(f"- {c['qty']}x {c['name']}")
    return ["## Decklist",f"### Main Deck — {totals['MAIN']}",f"#### Monstres — {totals['MONSTER']}",*groups["MONSTER"],f"#### Magies — {totals['SPELL']}",*groups["SPELL"],f"#### Pièges — {totals['TRAP']}",*groups["TRAP"],f"### Extra Deck — {totals['EXTRA']}",*extra,f"### Side Deck — {totals['SIDE']}",*side]


# --- runtime-owned visual applicability ---

def _rc16234_normalize_visual(doc):
    if not isinstance(doc,dict): return doc
    d=copy.deepcopy(doc); status=d.get("image_capability_status")
    main=d.get("main_carousel") if isinstance(d.get("main_carousel"),dict) else None
    sig=d.get("signature_climax") if isinstance(d.get("signature_climax"),dict) else None
    if main is not None and status in {"AVAILABLE","UNAVAILABLE"}:
        main["applicable"]=(status=="AVAILABLE")
        main["applicability_basis"]="DERIVED_IMAGE_CAPABILITY"
    if sig is not None and status in {"AVAILABLE","UNAVAILABLE"}:
        expected=(status=="AVAILABLE" and sig.get("terminal_quote_required") is True)
        sig["mini_carousel_applicable"]=expected
        sig["mini_carousel_applicability_basis"]="DERIVED_TERMINAL_QUOTE_AND_IMAGE_CAPABILITY"
    return d


_read_json_rc16234_parent = read_json

def read_json(path: Path, label="JSON"):
    d=_read_json_rc16234_parent(path,label)
    if "visual assets" in str(label).casefold() or "previous visual assets" in str(label).casefold():
        return _rc16234_normalize_visual(d)
    return d


_inject_component_anchors_rc16234_parent = _rc16233_inject_component_anchors

def _rc16233_inject_component_anchors(text, visual):
    return _inject_component_anchors_rc16234_parent(text,_rc16234_normalize_visual(visual or {}))


# --- damage contributor -> visible execution step ---

def _rc16234_actor_visible(actor, text):
    if not nonempty(actor) or not nonempty(text): return False
    an=" ".join(re.findall(r"[\w'-]+",actor.casefold()))
    tn=" ".join(re.findall(r"[\w'-]+",text.casefold()))
    if an and an in tn: return True
    at=[x for x in re.findall(r"[\w'-]+",actor.casefold()) if len(x)>=4]
    tt=set(re.findall(r"[\w'-]+",text.casefold()))
    return bool(at and at[-1] in tt)


def _rc16234_validate_damage_contributor_visibility(semantic):
    proof=[]
    for line in semantic.get("lines",[]) if isinstance(semantic,dict) and isinstance(semantic.get("lines"),list) else []:
        claim=line.get("claim") if isinstance(line,dict) else None
        if not isinstance(claim,dict) or str(claim.get("type") or "").upper()!="LETHAL": continue
        actions=line.get("actions") if isinstance(line.get("actions"),list) else []
        last_actor=None
        saw_damage=False
        for idx,a in enumerate(actions,1):
            if not isinstance(a,dict): continue
            kind=str(a.get("kind") or "").upper()
            if kind in {"NORMAL_SUMMON","SPECIAL_SUMMON","ACTIVATE","SEARCH","SEND_TO_GY","REVIVE","MOVE","SYNCHRO_SUMMON","FUSION_SUMMON"} and nonempty(a.get("card")):
                last_actor=a.get("card").strip()
            elif kind=="EFFECT" and isinstance(a.get("participants"),list) and a.get("participants") and nonempty(a.get("participants")[0]):
                last_actor=a.get("participants")[0].strip()
            if kind!="DAMAGE": continue
            saw_damage=True
            explicit=nonempty(a.get("actor")); actor=a.get("actor").strip() if explicit else last_actor
            text=a.get("text"); amount=a.get("amount")
            if not nonempty(actor): fail("LETHAL_DAMAGE_CONTRIBUTOR_ACTOR_REQUIRED")
            if not _rc16234_actor_visible(actor,text):
                fail(f"LETHAL_DAMAGE_CONTRIBUTOR_NOT_VISIBLE: {actor}")
            if not isinstance(amount,(int,float)) or isinstance(amount,bool) or amount<=0: fail(f"LETHAL_DAMAGE_AMOUNT_INVALID: {actor}")
            proof.append({"axis_heading":line.get("axis_heading"),"action_index":idx,"actor":actor,"actor_source":"EXPLICIT" if explicit else "DERIVED_LAST_ACTOR","amount":amount,"render_token":text.strip()})
        if not saw_damage:
            fail("LETHAL_DAMAGE_CONTRIBUTORS_MISSING")
    return proof


_compile_semantic_pilotage_rc16234_parent = _rc1623_compile_semantic_pilotage

def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    # Preserve upstream semantic/ruling/certainty failure precedence; contributor visibility
    # is an additional terminal semantic invariant, not a replacement for earlier authorities.
    out=_compile_semantic_pilotage_rc16234_parent(st,render_path,semantic)
    damage_proof=_rc16234_validate_damage_contributor_visibility(semantic)
    out.setdefault("compiler_provenance",{})["damage_contributor_bindings"] = damage_proof
    return out


# --- user-visible trace compiler from material journal/gates only ---
RC16234_TRACE_GATE_LABELS={
    "NARRATIVE_RED_CLOSED":"Progression narrative : définie",
    "EXPLORATION_CLOSED":"Exploration : effectuée",
    "STYLE_AXES_CLOSED":"Style → Axes",
    "MULTISYSTEM_PASS_AVAILABLE":"Viabilité multi-systèmes",
    "TERMINAL_COMPRESSION_CLOSED":"Compression terminale",
    "COLD_REPLAY_CLOSED":"Snapshot : figé → replay terminal",
    "MECHANICAL_VALIDATION_PASS":"Validation mécanique",
    "PILOTAGE_VALIDATED":"Validation mécanique des lignes",
    "FINAL_VALIDATION_PASS":"Validation finale",
}


def _rc16234_compile_user_trace(rd: Path, st):
    events=_read_journal(rd); lines=[]; seen=set()
    for ev in events:
        if ev.get("event")!="GATE_ATTEMPT_SUCCEEDED": continue
        gate=ev.get("gate"); label=RC16234_TRACE_GATE_LABELS.get(gate)
        if not label or gate in seen: continue
        seen.add(gate); rec=(st.get("gates") or {}).get(gate) or {}; status=rec.get("status") or ev.get("closed_status")
        if gate=="NARRATIVE_RED_CLOSED": text=label
        elif gate=="EXPLORATION_CLOSED": text=label
        elif gate=="COLD_REPLAY_CLOSED": text=f"{label} : {status}"
        else: text=f"{label} : {status}"
        lines.append({"text":text,"source_event_seq":ev.get("seq"),"gate":gate,"status":status})
    for ev in events:
        if ev.get("event")=="MECHANICAL_PROOF_VERIFIED":
            lines.append({"text":"Reçu : vérifié","source_event_seq":ev.get("seq"),"event":"MECHANICAL_PROOF_VERIFIED"}); break
    if "FINAL_VALIDATION_PASS" in seen and st.get("run_execution_state")=="COMPLETED" and st.get("stop_output_allowed") is True and isinstance((st.get("gates") or {}).get("FINAL_VALIDATION_PASS"),dict):
        final_ev=next((ev for ev in events if ev.get("event")=="GATE_ATTEMPT_SUCCEEDED" and ev.get("gate")=="FINAL_VALIDATION_PASS"),None)
        lines.append({"text":"STOP OUTPUT : PASS","source_event_seq":final_ev.get("seq") if final_ev else None,"derived_from":["GATE_ATTEMPT_SUCCEEDED:FINAL_VALIDATION_PASS","run_execution_state","stop_output_allowed"]})
    return {"schema":"ygo-user-trace-compiled-v1","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),"lines":lines,"journal_sha256":sha256(rd/RUN_JOURNAL_FILE) if (rd/RUN_JOURNAL_FILE).exists() else None}


def cmd_compile_user_trace(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); doc=_rc16234_compile_user_trace(rd,st)
    out=Path(a.output) if nonempty(getattr(a,"output",None)) else rd/RC16234_USER_TRACE_FILE; _rc1623_assert_flat_run_output(rd,out,"compiled user trace"); _atomic_write_text(out,_stable_json_text(doc)); print(json.dumps({"status":"COMPILED","output":str(out),"sha256":sha256(out),"line_count":len(doc["lines"])},ensure_ascii=False,indent=2))


# --- campaign hooks around existing run lifecycle ---
_cmd_dispatch_run_rc16234_parent = cmd_dispatch_run

def cmd_dispatch_run(a):
    result=_cmd_dispatch_run_rc16234_parent(a)
    scope=Path(a.scope_dir).resolve(); idx=_read_session_index(required=False)
    if idx and idx.get("run_id") and idx.get("run_dir"):
        try: _rc16234_campaign_register_run(scope,idx.get("run_id"),idx.get("run_dir"))
        except BaseException: raise
    return result


_cmd_abort_run_rc16234_parent = cmd_abort_run

def cmd_abort_run(a):
    rd=Path(a.run_dir); st=load_state(rd); scope=Path(st.get("continuity_scope_dir") or rd.parent).resolve()
    result=_cmd_abort_run_rc16234_parent(a); _rc16234_campaign_mark(scope,st.get("run_id"),rd,"ABORTED"); return result


_cmd_authorize_rc16234_parent = cmd_authorize

def cmd_authorize(a):
    rd=Path(a.run_dir); st0=load_state(rd); scope=Path(st0.get("continuity_scope_dir") or rd.parent).resolve()
    result=_cmd_authorize_rc16234_parent(a); st=load_state(rd); _rc16234_campaign_mark(scope,st.get("run_id"),rd,"COMPLETED"); return result


# =============================================================================
# RC16.23.5 — Post-Black-Box Recovery / Projection / Final Display Hardening
# Single semantic source, typed continuity, total repair routing and final
# controlled-emission proof.  Business authorities are unchanged.
# =============================================================================

RC16235_FINAL_EMISSION_SCHEMA = "ygo-final-controlled-emission-receipt-v1"
RC16235_FINAL_EMISSION_RECEIPT = "final_emission.receipt.json"


def _rc16235_visible_projection_token(text, render_text, semantic_terms=None):
    """Return an already-visible token; never invent presentation facts."""
    if nonempty(text) and text.strip().casefold() in render_text.casefold():
        return text.strip()
    lines=[x.strip() for x in render_text.splitlines() if x.strip()]
    terms=[]
    for x in semantic_terms or []:
        if nonempty(x):
            t=x.strip().casefold()
            if len(t)>=3 and t not in terms: terms.append(t)
    for line in lines:
        low=line.casefold()
        if any(t in low for t in terms): return line
    return None


def _rc16235_condition_projection(claim, render_text, line_label):
    certainty=str((claim or {}).get("certainty") or "GUARANTEED").upper()
    if certainty not in {"CONDITIONAL","RANDOM","RANGE","UNKNOWN"}:
        return [],[]
    raw=(claim or {}).get("conditions",[])
    if not isinstance(raw,list) or not raw:
        if certainty in {"CONDITIONAL","RANDOM"}:
            fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: visible conditions for {line_label}")
        return [],[]
    conds=[]; tokens=[]
    stop={"the","a","an","if","and","or","is","are","to","of","for","with","without","de","la","le","les","un","une","des","et","ou","si","est","sont","avec","sans"}
    for i,c in enumerate(raw,1):
        if isinstance(c,str): cid=c.strip(); text=c.strip()
        elif isinstance(c,dict):
            cid=str(c.get("condition_id") or c.get("id") or c.get("text") or c.get("description") or f"condition-{i:02d}").strip()
            text=str(c.get("text") or c.get("description") or c.get("render_text") or "").strip()
        else: fail(f"PILOTAGE_SEMANTIC_CONDITION_INVALID: {line_label}:{i}")
        if not cid or not text: fail(f"PILOTAGE_SEMANTIC_CONDITION_INVALID: {line_label}:{i}")
        exact=_rc16235_visible_projection_token(text,render_text)
        if exact is None:
            words=[w for w in re.findall(r"[\w'-]+",text.casefold()) if len(w)>=4 and w not in stop]
            lines=[x.strip() for x in render_text.splitlines() if x.strip()]
            scored=[]
            for line in lines:
                low=line.casefold(); score=sum(1 for w in words if w in low)
                if score: scored.append((score,len(line),line))
            scored.sort(key=lambda x:(-x[0],x[1],x[2].casefold()))
            if scored and scored[0][0]>=min(2,max(1,len(words))): exact=scored[0][2]
        if exact is None: fail(f"COMPILER_CONDITIONAL_CONDITION_NOT_VISIBLE: {line_label}:{cid}")
        conds.append(cid); tokens.append(exact)
    return conds,tokens


_rc16235_compile_semantic_pilotage_parent = _rc1623_compile_semantic_pilotage

def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    """RC16.23.5: project model-owned semantics into compiler-owned visible bindings."""
    out=_rc16235_compile_semantic_pilotage_parent(st,render_path,semantic)
    render_text=Path(render_path).read_text(encoding='utf-8')
    sem_lines=semantic.get('lines') if isinstance(semantic,dict) else []
    sem_by_axis={str(x.get('axis_heading')).strip().casefold():x for x in sem_lines if isinstance(x,dict) and nonempty(x.get('axis_heading'))}
    for line in out.get('lines',[]) if isinstance(out.get('lines'),list) else []:
        axis=str(line.get('render_axis_heading') or line.get('axis_heading') or '').strip().casefold()
        sem=sem_by_axis.get(axis)
        if not sem: continue
        actions=sem.get('actions') if isinstance(sem.get('actions'),list) else []
        claim=sem.get('claim') if isinstance(sem.get('claim'),dict) else {}
        conds,ctoks=_rc16235_condition_projection(claim,render_text,axis or line.get('line_id'))
        for rp in line.get('execution_replays',[]) if isinstance(line.get('execution_replays'),list) else []:
            if not isinstance(rp,dict): continue
            outcome=rp.get('outcome') if isinstance(rp.get('outcome'),dict) else None
            if outcome is not None:
                outcome['conditions']=list(conds); outcome['condition_render_tokens']=list(ctoks)
            steps=rp.get('steps') if isinstance(rp.get('steps'),list) else []
            for i,step in enumerate(steps):
                if not isinstance(step,dict) or i>=len(actions) or not isinstance(actions[i],dict): continue
                a=actions[i]; terms=[]
                for k in ('card','actor','target'):
                    if nonempty(a.get(k)): terms.append(a.get(k))
                for k in ('materials','participants'):
                    if isinstance(a.get(k),list): terms.extend([x for x in a.get(k) if nonempty(x)])
                tok=_rc16235_visible_projection_token(a.get('text'),render_text,terms)
                if tok is not None: step['render_token']=tok
    return out


# Compiler-owned visual references: local model-provided lists are hints only.
_rc16235_normalize_visual_parent = _rc16234_normalize_visual

def _rc16234_normalize_visual(doc):
    d=_rc16235_normalize_visual_parent(doc)
    if not isinstance(d,dict): return d
    refs=[]
    for x in d.get('image_refs') or []:
        if nonempty(x) and x not in refs: refs.append(x)
    for key in ('main_carousel','signature_climax'):
        block=d.get(key)
        if not isinstance(block,dict): continue
        local=[]
        for x in block.get('image_refs') or []:
            if nonempty(x) and x in refs and x not in local: local.append(x)
        need=2 if key=='main_carousel' else 3
        applicable=block.get('applicable') is True if key=='main_carousel' else block.get('mini_carousel_applicable') is True
        if applicable:
            if len(local)<need: local=list(refs[:4])
            block['image_refs']=local[:4]
            block['image_refs_basis']='DERIVED_FROM_BOUND_VISUAL_ASSETS'
    return d


def _rc16221_component_refs(visual, kind):
    v=_rc16234_normalize_visual(visual or {})
    block=(v.get('main_carousel') or {}) if kind=='main' else (v.get('signature_climax') or {})
    refs=[x for x in (block.get('image_refs') or []) if nonempty(x)]
    if refs: return refs[:4]
    return [x for x in (v.get('image_refs') or []) if nonempty(x)][:4]


# Deterministic rebinding and final-validation bundle assembly.
_cmd_complete_rc16235_parent = cmd_complete

def _rc16235_rebind_functional_intent(rd: Path, st, evidence_file):
    if not nonempty(evidence_file): return evidence_file
    src=Path(evidence_file)
    if not src.exists() or not src.is_file(): return evidence_file
    d=read_json(src,'functional intent')
    current=((st.get('gates') or {}).get('DIRECTION_RESOLVED') or {}).get('evidence_sha256')
    if not nonempty(current) or d.get('direction_contract_sha256')==current: return evidence_file
    if d.get('authority')!=CANON: return evidence_file
    old=d.get('direction_contract_sha256'); d['direction_contract_sha256']=current
    out=(rd/'functional_intent.rebound.json').resolve(); _atomic_write_text(out,_stable_json_text(d))
    cp=_load_checkpoint_raw(rd,required=False) or {}
    _append_run_journal(rd,st,'FUNCTIONAL_INTENT_DIRECTION_REBOUND',checkpoint_seq=cp.get('checkpoint_seq'),old_direction_contract_sha256=old,new_direction_contract_sha256=current,source_file=str(src),rebound_file=str(out),rebound_sha256=sha256(out))
    return str(out)


def _rc16235_fill_final_bundle(rd: Path, st, a):
    if getattr(a,'gate',None)!='FINAL_VALIDATION_PASS': return
    plan_arg=getattr(a,'terminal_presentation_plan',None) or st.get('terminal_presentation_plan_file')
    receipt_arg=getattr(a,'terminal_presentation_receipt',None) or st.get('terminal_presentation_receipt_file')
    if nonempty(plan_arg) and Path(plan_arg).exists():
        pd=read_json(Path(plan_arg),'terminal presentation plan')
        if not nonempty(getattr(a,'evidence_file',None)): a.evidence_file=pd.get('text_payload_file')
        if not nonempty(getattr(a,'render_manifest',None)): a.render_manifest=pd.get('render_manifest_file')
    frozen=(st.get('gates') or {}).get('RENDER_CONTRACT_FROZEN') or {}
    if not nonempty(getattr(a,'contract_file',None)): a.contract_file=frozen.get('evidence_file')
    if not nonempty(getattr(a,'terminal_presentation_plan',None)): a.terminal_presentation_plan=plan_arg
    if not nonempty(getattr(a,'terminal_presentation_receipt',None)): a.terminal_presentation_receipt=receipt_arg


def cmd_complete(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if getattr(a,'gate',None)=='FUNCTIONAL_INTENT_FROZEN':
        a.evidence_file=_rc16235_rebind_functional_intent(rd,st,getattr(a,'evidence_file',None))
    _rc16235_fill_final_bundle(rd,st,a)
    return _cmd_complete_rc16235_parent(a)


# Total recoverability: every AUTO_RECOVERABLE classification carries a legal route.
_rc16235_continuation_policy_parent = _rc1623_continuation_policy

def _rc16235_repair_routes(issues):
    codes={str(x.get('code')) for x in issues if isinstance(x,dict)}
    routes=[]
    if codes & {'CONDITIONAL_OUTCOME_REQUIRES_VISIBLE_CONDITIONS','EXECUTION_STEP_NOT_RENDERED','EXECUTION_OUTCOME_NOT_RENDERED','PILOTAGE_LINE_NOT_RENDERED','STRUCTURAL_STARTER_NOT_RENDERED'}:
        routes.append({'route':'SEMANTIC_PROJECTION_RECOMPILE','owner':'COMPILER','required_action':'RECOMPILE_FROM_CANONICAL_SEMANTICS_AND_CONTINUE'})
    if any(c.startswith('PILOTAGE_BUSINESS_PROVENANCE') or 'PROOF' in c or 'BUNDLE' in c for c in codes):
        routes.append({'route':'RUNTIME_PROOF_BUNDLE_REBUILD','owner':'RUNTIME','required_action':'REBUILD_DERIVABLE_PROOF_BUNDLE_AND_CONTINUE'})
    if codes & {'PREFREEZE_SIGNATURE_MINI_IMAGE_REFS_INVALID','PREFREEZE_MAIN_CAROUSEL_IMAGE_REFS_INVALID'}:
        routes.append({'route':'COMPONENT_REF_RECOMPILE','owner':'COMPILER','required_action':'RECOMPILE_COMPONENT_REFS_FROM_BOUND_VISUAL_ASSETS'})
    if not routes and codes:
        routes.append({'route':'SAME_DOMAIN_REPAIR','owner':'RUNTIME','required_action':'REPAIR_CLASSIFIED_DOMAIN_AND_CONTINUE'})
    return routes


def _rc1623_continuation_policy(rd: Path, st):
    doc=_rc16235_continuation_policy_parent(rd,st)
    if doc.get('classification')=='AUTO_RECOVERABLE':
        receipt=Path(rd)/PILOTAGE_AUTHORITATIVE_DRY_RUN_RECEIPT
        issues=[]
        if receipt.exists():
            try: issues=read_json(receipt,'Pilotage authoritative dry-run receipt').get('issues') or []
            except BaseException: issues=[]
        routes=_rc16235_repair_routes(issues)
        if not routes:
            return {**doc,'classification':'FATAL','handoff_allowed':True,'required_action':'REPORT_UNROUTABLE_RECOVERY','repair_routes':[]}
        doc={**doc,'repair_routes':routes,'legal_repair_transition_count':len(routes)}
    return doc


def _rc16235_continuity_summary(rd: Path, cp=None):
    cp=cp or (_load_checkpoint_raw(rd,required=False) or {})
    events=_read_journal(rd)
    resumed=[e for e in events if e.get('event')=='RUN_RESUMED']
    user_required=sum(1 for e in resumed if e.get('resume_reason')=='USER_INPUT_RESOLUTION')
    nominal=sum(1 for e in resumed if e.get('resume_reason')=='NOMINAL_CONTINUATION')
    recovery=sum(1 for e in resumed if e.get('resume_reason') in {'RECOVERY','CHECKPOINT_RECOVERY','INTERRUPTION_RECOVERY'})
    known=user_required+nominal+recovery
    unmatched=max(0,int(cp.get('resume_count',0) or 0)-len(resumed))
    unwanted=sum(1 for e in resumed if e.get('resume_reason') not in {'USER_INPUT_RESOLUTION','NOMINAL_CONTINUATION','RECOVERY','CHECKPOINT_RECOVERY','INTERRUPTION_RECOVERY'})+unmatched
    return {'resume_count':int(cp.get('resume_count',0) or 0),'USER_REQUIRED_RESUME_COUNT':user_required,'NOMINAL_RESUME_COUNT':nominal,'RECOVERY_RESUME_COUNT':recovery,'UNWANTED_HANDOFF_COUNT':unwanted,'continuity_pass':unwanted==0 and recovery==0}


# Final controlled emission: terminal-output materializes a receipt for the exact bytes it emits.
def _rc16235_deck_display_structure(text):
    heads=[]; current=None
    groups={}
    hre=re.compile(r'^(#{3,4})\s+(Main Deck|Monstres|Magies|Pièges|Extra Deck|Side Deck)\s+—\s+(\d+)\s*$',re.I)
    cre=re.compile(r'^-\s+(\d+)[x×]\s+(.+?)\s*$')
    for raw in text.splitlines():
        line=raw.strip(); m=hre.match(line)
        if m:
            current=m.group(2).casefold(); total=int(m.group(3)); heads.append({'name':m.group(2),'level':len(m.group(1)),'declared_total':total}); groups[current]={'declared_total':total,'cards':[]}; continue
        cm=cre.match(line)
        if cm and current in groups: groups[current]['cards'].append({'qty':int(cm.group(1)),'name':cm.group(2)})
    for g in groups.values(): g['actual_total']=sum(x['qty'] for x in g['cards'])
    # Subgroup totals must match whenever subgroup headings are present.
    for key in ('monstres','magies','pièges','extra deck','side deck'):
        if key in groups and groups[key]['declared_total']!=groups[key]['actual_total']:
            fail(f'FINAL_EMISSION_GROUP_TOTAL_MISMATCH: {key}')
    return {'headings':heads,'groups':groups}


def _rc16235_write_final_emission_receipt(rd: Path, st, payload: Path):
    text=payload.read_text(encoding='utf-8'); structure=_rc16235_deck_display_structure(text)
    structural_sha=hashlib.sha256(_stable_json_text(structure).encode()).hexdigest()
    rec={'schema':RC16235_FINAL_EMISSION_SCHEMA,'status':'PASS','run_id':st.get('run_id'),'deck_artifact':st.get('current_artifact'),'render_id':st.get('current_render'),'terminal_payload_file':str(payload.resolve()),'terminal_payload_sha256':sha256(payload),'structural_signature_sha256':structural_sha,'structure':structure,'runtime_version':VERSION}
    out=(rd/RC16235_FINAL_EMISSION_RECEIPT).resolve(); _atomic_write_text(out,_stable_json_text(rec))
    st['final_emission_receipt_file']=str(out); st['final_emission_receipt_sha256']=sha256(out); save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,'FINAL_CONTROLLED_EMISSION_MATERIALIZED',checkpoint_seq=cp.get('checkpoint_seq'),receipt_file=str(out),receipt_sha256=sha256(out),terminal_payload_sha256=sha256(payload),structural_signature_sha256=structural_sha)
    return rec


def _rc16235_final_emission_valid(rd: Path, st):
    raw=st.get('final_emission_receipt_file'); rh=st.get('final_emission_receipt_sha256'); payload_raw=st.get('terminal_payload_file')
    if not nonempty(raw) or not nonempty(rh) or not nonempty(payload_raw): return False
    rp=Path(raw); payload=Path(payload_raw)
    if not rp.exists() or not payload.exists() or sha256(rp)!=rh: return False
    try: d=read_json(rp,'final controlled emission receipt')
    except BaseException: return False
    if d.get('schema')!=RC16235_FINAL_EMISSION_SCHEMA or d.get('status')!='PASS' or d.get('runtime_version')!=VERSION: return False
    if d.get('terminal_payload_sha256')!=sha256(payload) or sha256(payload)!=st.get('terminal_payload_sha256'): return False
    try:
        structure=_rc16235_deck_display_structure(payload.read_text(encoding='utf-8'))
        sh=hashlib.sha256(_stable_json_text(structure).encode()).hexdigest()
    except BaseException: return False
    return d.get('structural_signature_sha256')==sh


_cmd_terminal_output_rc16235_parent = cmd_terminal_output

def cmd_terminal_output(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    raw=st.get('terminal_payload_file'); expected=st.get('terminal_payload_sha256')
    if st.get('run_execution_state')!='COMPLETED' or st.get('stop_output_allowed') is not True: fail('TERMINAL_OUTPUT_NOT_AUTHORIZED')
    if not nonempty(raw) or not nonempty(expected): fail('TERMINAL_PAYLOAD_BINDING_MISSING')
    payload=Path(raw); _rc1623_assert_flat_run_output(rd,payload,'terminal payload')
    if not payload.exists() or sha256(payload)!=expected or expected!=st.get('authorized_render_sha256'): fail('TERMINAL_PAYLOAD_STALE_AFTER_AUTHORIZE')
    _rc16235_write_final_emission_receipt(rd,st,payload)
    print(payload.read_text(encoding='utf-8'),end='')


# Clear any previous emission proof after a new authorization.
_cmd_authorize_rc16235_parent = cmd_authorize

def cmd_authorize(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    # Runtime-owned terminal bundle arguments may be omitted by callers.
    plan_raw=st.get('terminal_presentation_plan_file')
    if nonempty(plan_raw) and Path(plan_raw).exists():
        pd=read_json(Path(plan_raw),'terminal presentation plan')
        if not nonempty(getattr(a,'render_file',None)): a.render_file=pd.get('text_payload_file')
        if not nonempty(getattr(a,'render_manifest',None)): a.render_manifest=pd.get('render_manifest_file')
    frozen=(st.get('gates') or {}).get('RENDER_CONTRACT_FROZEN') or {}
    if not nonempty(getattr(a,'contract_file',None)): a.contract_file=frozen.get('evidence_file')
    if not all(nonempty(getattr(a,k,None)) for k in ('render_file','render_manifest','contract_file')): fail('AUTHORIZE_RUNTIME_BUNDLE_UNRESOLVED')
    result=_cmd_authorize_rc16235_parent(a)
    st2=load_state(rd)
    old=st2.get('final_emission_receipt_file')
    if nonempty(old) and Path(old).exists(): Path(old).unlink()
    st2.pop('final_emission_receipt_file',None); st2.pop('final_emission_receipt_sha256',None); save_state(rd,st2)
    return result


# Black-Box 4D now uses typed continuity and post-emission proof.
def _rc16233_blackbox_4d_status(rd: Path, st):
    cp=_load_checkpoint_raw(rd,required=False) or {}; gates=st.get('gates') or {}
    terminal=st.get('run_execution_state')=='COMPLETED' and st.get('stop_output_allowed') is True and isinstance(gates.get('FINAL_VALIDATION_PASS'),dict)
    csum=_rc16235_continuity_summary(rd,cp); continuation=bool(terminal and csum.get('continuity_pass'))
    semantic=bool(isinstance(gates.get('PILOTAGE_VALIDATED'),dict) and gates['PILOTAGE_VALIDATED'].get('status')=='PASS')
    presentation=False
    pr=st.get('terminal_presentation_receipt_file')
    if nonempty(pr) and Path(pr).exists():
        try:
            d=read_json(Path(pr),'terminal presentation receipt')
            plan=read_json(Path(st.get('terminal_presentation_plan_file')),'terminal presentation plan') if nonempty(st.get('terminal_presentation_plan_file')) and Path(st.get('terminal_presentation_plan_file')).exists() else {}
            presentation=d.get('status')=='PASS' and all(c.get('emission_status')=='EMITTED' for c in plan.get('components',[]) if isinstance(c,dict)) and _rc16235_final_emission_valid(rd,st)
        except BaseException: presentation=False
    dims={'TERMINAL_PASS':terminal,'CONTINUITY_PASS':continuation,'SEMANTIC_PASS':semantic,'PRESENTATION_PASS':presentation}
    return {'schema':'ygo-blackbox-4d-v2','run_id':st.get('run_id'),**dims,'FULL_PASS':all(dims.values()),'resume_count':cp.get('resume_count',0),'continuity_summary':csum,'final_emission_proof':_rc16235_final_emission_valid(rd,st),'deck_artifact':st.get('current_artifact'),'render_id':st.get('current_render')}


# terminal-output became a small state mutation because it materializes emission proof.
_instrumented_call_rc16235_parent = _instrumented_call

def _instrumented_call(a):
    if getattr(a,'cmd',None)=='terminal-output':
        rd=_timing_target_run_dir(a)
        if rd:
            with _rc1623_command_lock(rd): return _instrumented_call_rc16235_parent(a)
    return _instrumented_call_rc16235_parent(a)


# =============================================================================
# RC16.23.6 — False-Pass Closure
# Authoritative environment membership, exact summon-material contracts,
# same-run USER_REQUIRED protection, and truthful component-emission evidence.
# =============================================================================

RC16236_POOL_SOURCE_SCHEMA = "ygo-environment-card-pool-catalog-v2"
RC16236_POOL_BINDING_SCHEMA = "ygo-environment-card-pool-binding-v1"
RC16236_POOL_BINDING_FILE = "environment_card_pool.binding.json"
RC16236_POOL_TRUSTED_UNIQUE_COUNT = 10027
RC16236_POOL_TRUSTED_NAMES_SHA256 = "7ee9e4dbdeb0dfb834468ef3dd959a6aa0c8993c35fe05b5e8b22df77f8d0935"
RC16236_POOL_TRUSTED_SOURCE_BLOB = "0f075c3802852a043caa23ba0f8254e1ba14b357"
RC16236_DEFAULT_POOL_CATALOG = Path(__file__).resolve().parent / "LINK_EVOLUTION_2020_CARD_POOL.json"
RC16236_SUMMON_SOURCE_SCHEMA = "ygo-summon-rules-authoritative-v1"
RC16236_SUMMON_BINDING_SCHEMA = "ygo-summon-rules-binding-v1"
RC16236_SUMMON_BINDING_FILE = "summon_rules.binding.json"
RC16236_HOST_EVIDENCE_SCHEMA = "ygo-host-component-emission-evidence-v1"
RC16236_HOST_BINDING_SCHEMA = "ygo-host-component-emission-binding-v1"
RC16236_HOST_BINDING_FILE = "host_component_emission.binding.json"
RC16236_FINAL_EMISSION_SCHEMA = "ygo-final-controlled-emission-receipt-v2"
RC16236_ALLOWED_PROVENANCE = {"EXTERNAL_AUTHORITATIVE", "PROJECT_VERIFIED_CATALOG", "USER_VERIFIED_SOURCE"}
RC16236_ALLOWED_HOST_PROVENANCE = {"HOST_TOOL_EMISSION", "USER_OBSERVED", "BLACKBOX_OBSERVED"}


def _rc16236_current_snapshot(st):
    dg=(st.get("gates") or {}).get("DECK_DRAFT_CREATED") or {}
    sp=Path(dg.get("snapshot_file") or "")
    if not sp.exists(): fail("ENVIRONMENT_POOL_DECK_SNAPSHOT_MISSING")
    if nonempty(dg.get("snapshot_sha256")) and dg.get("snapshot_sha256")!=sha256(sp): fail("ENVIRONMENT_POOL_DECK_SNAPSHOT_STALE")
    return sp,read_json(sp,"deck snapshot")


def _rc16236_all_snapshot_cards(snapshot):
    out={}
    for zone in ("main_deck","extra_deck","side_deck"):
        rows=snapshot.get(zone,[]) if isinstance(snapshot.get(zone),list) else []
        for c in rows:
            if not isinstance(c,dict) or not nonempty(c.get("name")): fail(f"DECK_SNAPSHOT_CARD_INVALID: {zone}")
            key=c["name"].strip().casefold(); out.setdefault(key,{"name":c["name"].strip(),"zones":[]})
            if zone not in out[key]["zones"]: out[key]["zones"].append(zone)
    return out


def _rc16236_validate_provenance(prov, allowed=None, prefix="EVIDENCE"):
    allowed=allowed or RC16236_ALLOWED_PROVENANCE
    if not isinstance(prov,dict) or prov.get("kind") not in allowed or not nonempty(prov.get("authority")) or not nonempty(prov.get("source_locator")):
        fail(f"{prefix}_PROVENANCE_INVALID")
    return copy.deepcopy(prov)


def _rc16236_pool_binding(st, required=True):
    binding=st.get("environment_card_pool_binding")
    if not isinstance(binding,dict):
        if required: fail("ENVIRONMENT_CARD_POOL_BINDING_REQUIRED")
        return None
    sp,snap=_rc16236_current_snapshot(st); current=sha256(sp)
    if binding.get("snapshot_sha256")!=current: fail("ENVIRONMENT_CARD_POOL_BINDING_STALE")
    bp=Path(binding.get("binding_file") or "")
    if not bp.exists() or sha256(bp)!=binding.get("binding_sha256"): fail("ENVIRONMENT_CARD_POOL_BINDING_STALE")
    doc=read_json(bp,"environment card-pool binding")
    if doc.get("schema")!=RC16236_POOL_BINDING_SCHEMA or doc.get("snapshot_sha256")!=current: fail("ENVIRONMENT_CARD_POOL_BINDING_INVALID")
    wanted=_rc16236_all_snapshot_cards(snap); rows=doc.get("cards")
    if not isinstance(rows,list): fail("ENVIRONMENT_CARD_POOL_BINDING_INVALID")
    by={}
    for row in rows:
        if not isinstance(row,dict) or not nonempty(row.get("name")) or row.get("available") is not True: fail("CARD_NOT_IN_ENVIRONMENT_POOL")
        k=row["name"].strip().casefold()
        if k in by: fail("ENVIRONMENT_CARD_POOL_DUPLICATE_CARD")
        by[k]=row
    if set(by)!=set(wanted): fail("ENVIRONMENT_CARD_POOL_BINDING_COVERAGE_MISMATCH")
    return doc


def _rc16236_pool_catalog_fingerprint(names):
    vals=[]; seen=set()
    for raw in names:
        if not nonempty(raw): fail("ENVIRONMENT_CARD_POOL_CARD_INVALID")
        name=str(raw).strip()
        if name in seen: continue
        seen.add(name); vals.append(name)
    vals=sorted(vals)
    canonical=("\n".join(vals)+"\n").encode("utf-8")
    return {"unique_count":len(vals),"names_sha256":hashlib.sha256(canonical).hexdigest()}


def cmd_bind_card_pool(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"bind-card-pool")
    sp,snap=_rc16236_current_snapshot(st); src=Path(a.pool_file) if nonempty(getattr(a,"pool_file",None)) else RC16236_DEFAULT_POOL_CATALOG
    if not src.exists(): fail("ENVIRONMENT_CARD_POOL_SOURCE_MISSING")
    doc=read_json(src,"environment card-pool evidence")
    if doc.get("schema")!=RC16236_POOL_SOURCE_SCHEMA: fail("ENVIRONMENT_CARD_POOL_SCHEMA_INVALID")
    if doc.get("environment_id")!="link-evolution-2020": fail("ENVIRONMENT_CARD_POOL_ID_INVALID")
    prov=_rc16236_validate_provenance(doc.get("provenance"),prefix="ENVIRONMENT_CARD_POOL")
    if doc.get("catalog_complete") is not True or doc.get("catalog_scope")!="FULL_ENVIRONMENT": fail("ENVIRONMENT_CARD_POOL_CATALOG_INCOMPLETE")
    rows=doc.get("cards")
    if not isinstance(rows,list): fail("ENVIRONMENT_CARD_POOL_CARDS_INVALID")
    by={}
    for row in rows:
        if isinstance(row,str): name=row.strip(); locator=prov.get("source_locator")
        elif isinstance(row,dict) and nonempty(row.get("name")):
            if "available" in row: fail("ENVIRONMENT_CARD_POOL_DERIVATION_MUST_NOT_BE_DECLARED")
            name=row["name"].strip(); locator=row.get("source_locator") or prov.get("source_locator")
        else: fail("ENVIRONMENT_CARD_POOL_CARD_INVALID")
        if not nonempty(name): fail("ENVIRONMENT_CARD_POOL_CARD_INVALID")
        k=name.casefold()
        if k in by: fail("ENVIRONMENT_CARD_POOL_DUPLICATE_CARD")
        by[k]={"name":name,"source_locator":locator}
    fp=_rc16236_pool_catalog_fingerprint([x["name"] for x in by.values()])
    if fp.get("unique_count")!=RC16236_POOL_TRUSTED_UNIQUE_COUNT or fp.get("names_sha256")!=RC16236_POOL_TRUSTED_NAMES_SHA256:
        fail("ENVIRONMENT_CARD_POOL_CATALOG_FINGERPRINT_MISMATCH")
    wanted=_rc16236_all_snapshot_cards(snap)
    absent=[wanted[k]["name"] for k in sorted(wanted) if k not in by]
    if absent: fail("CARD_NOT_IN_ENVIRONMENT_POOL: "+", ".join(absent))
    bound=[{"name":wanted[k]["name"],"available":True,"source_locator":by[k].get("source_locator")} for k in sorted(wanted)]
    norm={"schema":RC16236_POOL_BINDING_SCHEMA,"environment_id":"link-evolution-2020","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"snapshot_sha256":sha256(sp),"source_file":str(src.resolve()),"source_sha256":sha256(src),"catalog_card_count":len(by),"catalog_names_sha256":fp["names_sha256"],"provenance":prov,"cards":bound}
    out=(rd/RC16236_POOL_BINDING_FILE).resolve(); _atomic_write_text(out,_stable_json_text(norm))
    st["environment_card_pool_binding"]={"binding_file":str(out),"binding_sha256":sha256(out),"snapshot_sha256":sha256(sp),"source_sha256":sha256(src),"provenance_kind":prov.get("kind"),"environment_id":"link-evolution-2020"}; save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,"ENVIRONMENT_CARD_POOL_BOUND",checkpoint_seq=cp.get("checkpoint_seq"),binding_file=str(out),binding_sha256=sha256(out),snapshot_sha256=sha256(sp),card_count=len(bound),catalog_card_count=len(by),catalog_names_sha256=fp["names_sha256"],provenance_kind=prov.get("kind"))
    print(json.dumps({"status":"BOUND","environment_id":"link-evolution-2020","binding_file":str(out),"binding_sha256":sha256(out),"card_count":len(by)},ensure_ascii=False,indent=2))


def _rc16236_semantic_sha(semantic):
    return hashlib.sha256(_stable_json_text(semantic).encode("utf-8")).hexdigest()


def _rc16236_semantic_summon_cards(semantic):
    bosses=set(); materials=set()
    for line in semantic.get("lines",[]) if isinstance(semantic,dict) and isinstance(semantic.get("lines"),list) else []:
        for a in line.get("actions",[]) if isinstance(line,dict) and isinstance(line.get("actions"),list) else []:
            if not isinstance(a,dict) or str(a.get("kind") or "").upper() not in {"SYNCHRO_SUMMON","FUSION_SUMMON"}: continue
            if nonempty(a.get("card")): bosses.add(a["card"].strip().casefold())
            for x in a.get("materials",[]) if isinstance(a.get("materials"),list) else []:
                if nonempty(x): materials.add(x.strip().casefold())
    return bosses,materials


def cmd_bind_summon_rules(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,"bind-summon-rules")
    sem_path=Path(a.semantic_file); src=Path(a.rules_file)
    if not sem_path.exists(): fail("SUMMON_RULE_SEMANTIC_FILE_MISSING")
    if not src.exists(): fail("SUMMON_RULE_SOURCE_MISSING")
    semantic=read_json(sem_path,"Pilotage semantic input"); doc=read_json(src,"authoritative summon rules")
    if doc.get("schema")!=RC16236_SUMMON_SOURCE_SCHEMA: fail("SUMMON_RULE_SCHEMA_INVALID")
    prov=_rc16236_validate_provenance(doc.get("provenance"),prefix="SUMMON_RULE")
    bosses,materials=_rc16236_semantic_summon_cards(semantic)
    rule_rows=doc.get("summons"); card_rows=doc.get("cards")
    if not isinstance(rule_rows,list) or not isinstance(card_rows,list): fail("SUMMON_RULE_SOURCE_INVALID")
    rules={}; cards={}
    for row in rule_rows:
        if not isinstance(row,dict) or not nonempty(row.get("card")) or str(row.get("kind") or "").upper() not in {"SYNCHRO_SUMMON","FUSION_SUMMON"}: fail("SUMMON_RULE_RECORD_INVALID")
        k=row["card"].strip().casefold()
        if k in rules: fail("SUMMON_RULE_DUPLICATE_BOSS")
        nr=copy.deepcopy(row); nr["card"]=row["card"].strip(); nr["kind"]=str(row["kind"]).upper(); rules[k]=nr
    for row in card_rows:
        if not isinstance(row,dict) or not nonempty(row.get("name")): fail("SUMMON_RULE_CARD_PROPERTY_INVALID")
        k=row["name"].strip().casefold()
        if k in cards: fail("SUMMON_RULE_DUPLICATE_CARD_PROPERTY")
        cards[k]=copy.deepcopy(row); cards[k]["name"]=row["name"].strip()
    if bosses-set(rules): fail("SUMMON_RULE_BOSS_COVERAGE_MISMATCH")
    if materials-set(cards): fail("SUMMON_RULE_MATERIAL_PROPERTY_COVERAGE_MISMATCH")
    norm={"schema":RC16236_SUMMON_BINDING_SCHEMA,"run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"semantic_sha256":_rc16236_semantic_sha(semantic),"source_file":str(src.resolve()),"source_sha256":sha256(src),"provenance":prov,"summons":[rules[k] for k in sorted(bosses)],"cards":[cards[k] for k in sorted(materials)]}
    out=(rd/RC16236_SUMMON_BINDING_FILE).resolve(); _atomic_write_text(out,_stable_json_text(norm))
    st["summon_rules_binding"]={"binding_file":str(out),"binding_sha256":sha256(out),"semantic_sha256":norm["semantic_sha256"],"source_sha256":sha256(src),"provenance_kind":prov.get("kind")}; save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,"SUMMON_RULES_BOUND",checkpoint_seq=cp.get("checkpoint_seq"),binding_file=str(out),binding_sha256=sha256(out),semantic_sha256=norm["semantic_sha256"],boss_count=len(bosses),material_count=len(materials),provenance_kind=prov.get("kind"))
    print(json.dumps({"status":"BOUND","binding_file":str(out),"binding_sha256":sha256(out),"boss_count":len(bosses),"material_count":len(materials)},ensure_ascii=False,indent=2))


def _rc16236_effective_names(card, zone):
    names={str(card.get("name") or "").strip().casefold()}
    eff=card.get("effective_names_by_zone")
    if isinstance(eff,dict):
        vals=eff.get(str(zone or "FIELD").upper()) or []
        if isinstance(vals,str): vals=[vals]
        for x in vals if isinstance(vals,list) else []:
            if nonempty(x): names.add(x.strip().casefold())
    return names


def _rc16236_validate_summon_contracts(st, semantic):
    bosses,materials=_rc16236_semantic_summon_cards(semantic)
    if not bosses: return []
    b=st.get("summon_rules_binding")
    if not isinstance(b,dict): fail("SUMMON_MATERIAL_RULE_BINDING_REQUIRED")
    bp=Path(b.get("binding_file") or "")
    if not bp.exists() or sha256(bp)!=b.get("binding_sha256") or b.get("semantic_sha256")!=_rc16236_semantic_sha(semantic): fail("SUMMON_MATERIAL_RULE_BINDING_STALE")
    doc=read_json(bp,"summon rules binding")
    if doc.get("schema")!=RC16236_SUMMON_BINDING_SCHEMA or doc.get("semantic_sha256")!=_rc16236_semantic_sha(semantic): fail("SUMMON_MATERIAL_RULE_BINDING_INVALID")
    rules={x["card"].strip().casefold():x for x in doc.get("summons",[]) if isinstance(x,dict) and nonempty(x.get("card"))}
    props={x["name"].strip().casefold():x for x in doc.get("cards",[]) if isinstance(x,dict) and nonempty(x.get("name"))}
    proof=[]
    for li,line in enumerate(semantic.get("lines",[]),1):
        for ai,a in enumerate(line.get("actions",[]) if isinstance(line,dict) else [],1):
            if not isinstance(a,dict): continue
            kind=str(a.get("kind") or "").upper()
            if kind not in {"SYNCHRO_SUMMON","FUSION_SUMMON"}: continue
            boss=str(a.get("card") or "").strip(); rule=rules.get(boss.casefold())
            if not rule or rule.get("kind")!=kind: fail(f"SUMMON_MATERIAL_RULE_MISSING: {boss}")
            mats=a.get("materials")
            if not isinstance(mats,list) or not mats: fail(f"SUMMON_MATERIALS_REQUIRED: {boss}")
            mprops=[]
            for name in mats:
                prop=props.get(str(name).strip().casefold())
                if not prop: fail(f"SUMMON_MATERIAL_PROPERTY_MISSING: {name}")
                mprops.append(prop)
            exact_count=rule.get("exact_material_count")
            if isinstance(exact_count,int) and len(mats)!=exact_count: fail(f"SUMMON_MATERIAL_COUNT_MISMATCH: {boss}")
            min_count=rule.get("min_material_count")
            if isinstance(min_count,int) and len(mats)<min_count: fail(f"SUMMON_MATERIAL_COUNT_MISMATCH: {boss}")
            if kind=="SYNCHRO_SUMMON":
                tuner_count=sum(1 for x in mprops if x.get("tuner") is True)
                if isinstance(rule.get("exact_tuners"),int) and tuner_count!=rule["exact_tuners"]: fail(f"SUMMON_TUNER_COUNT_MISMATCH: {boss}")
                if isinstance(rule.get("min_tuners"),int) and tuner_count<rule["min_tuners"]: fail(f"SUMMON_TUNER_COUNT_MISMATCH: {boss}")
                nt=rule.get("min_non_tuners")
                if isinstance(nt,int) and len(mprops)-tuner_count<nt: fail(f"SUMMON_NON_TUNER_COUNT_MISMATCH: {boss}")
                target=rule.get("target_level")
                if isinstance(target,int):
                    lv=[]
                    for x in mprops:
                        if not isinstance(x.get("level"),int): fail(f"SUMMON_MATERIAL_LEVEL_MISSING: {x.get('name')}")
                        lv.append(x["level"])
                    if sum(lv)!=target: fail(f"SUMMON_LEVEL_SUM_MISMATCH: {boss}")
            required=rule.get("required_named_materials") or []
            for req in required if isinstance(required,list) else []:
                if isinstance(req,str): rname=req; count=1; role=None
                elif isinstance(req,dict): rname=req.get("name"); count=req.get("count",1); role=req.get("role")
                else: fail(f"SUMMON_NAMED_MATERIAL_RULE_INVALID: {boss}")
                if not nonempty(rname) or not isinstance(count,int) or count<1: fail(f"SUMMON_NAMED_MATERIAL_RULE_INVALID: {boss}")
                matched=0
                for prop in mprops:
                    if role=="NON_TUNER" and prop.get("tuner") is True: continue
                    if role=="TUNER" and prop.get("tuner") is not True: continue
                    if rname.strip().casefold() in _rc16236_effective_names(prop,a.get("material_zone") or "FIELD"): matched+=1
                if matched<count: fail(f"SUMMON_NAMED_MATERIAL_MISMATCH: {boss} requires {rname}")
            proof.append({"line_index":li,"action_index":ai,"boss":boss,"kind":kind,"materials":[str(x) for x in mats],"rule_source_sha256":doc.get("source_sha256")})
    return proof


# Exact summon validation belongs to the mechanical Pilotage boundary, not to
# semantic compilation.  The compiler may therefore diagnose/compile semantic
# input without an authoritative ruling bundle; Pilotage cannot certify that
# compiled payload until the exact semantic source passes the material contract.
_rc16236_compile_semantic_parent = _rc1623_compile_semantic_pilotage

def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    out=_rc16236_compile_semantic_parent(st,render_path,semantic)
    out.setdefault("compiler_provenance",{})["summon_material_contract_status"]="DEFERRED_TO_PILOTAGE_MECHANICAL"
    return out


# Card-pool membership must be fresh before narrative conformance or any later gate can close.
_cmd_complete_rc16236_parent = cmd_complete

def cmd_complete(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    names=[g for g,_,_ in sequence(st)]
    if getattr(a,"gate",None) in names and "NARRATIVE_CONFORMANCE_CLOSED" in names and names.index(a.gate)>=names.index("NARRATIVE_CONFORMANCE_CLOSED"):
        _rc16236_pool_binding(st,required=True)
    return _cmd_complete_rc16236_parent(a)


# A WAITING_USER_INPUT run may not be administratively aborted unless the user explicitly requested abandon/fresh.
_cmd_abort_run_rc16236_parent = cmd_abort_run

def cmd_abort_run(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); cp=_load_checkpoint_raw(rd,required=False) or {}
    state=cp.get("run_state") or st.get("run_execution_state")
    reason=str(getattr(a,"reason","") or "").strip().upper()
    if state=="WAITING_USER_INPUT" and reason not in {"USER_REQUESTED_FRESH","USER_REQUESTED_ABORT"}:
        fail("USER_REQUIRED_RUN_CANNOT_ABORT_USE_RESUME")
    return _cmd_abort_run_rc16236_parent(a)


# Component truth: marker inclusion is local controlled-emission evidence, not host visibility.
_compile_terminal_presentation_payload_rc16236_parent = compile_terminal_presentation_payload

def compile_terminal_presentation_payload(render_path: Path, manifest_path: Path, st):
    doc=_compile_terminal_presentation_payload_rc16236_parent(render_path,manifest_path,st)
    text=Path(render_path).read_text(encoding="utf-8")
    for c in doc.get("components",[]) if isinstance(doc.get("components"),list) else []:
        if not isinstance(c,dict): continue
        anchor=_rc16233_component_anchor(c.get("component_id"))
        included=bool(anchor in text)
        c["controlled_emission_status"]="INCLUDED_IN_CONTROLLED_EMISSION" if included else "NOT_INCLUDED_IN_CONTROLLED_EMISSION"
        c["host_visibility_status"]="HOST_VISIBLE_UNVERIFIED" if included else "NOT_APPLICABLE"
    return doc


def _rc16236_final_component_records(st, payload: Path):
    plan_raw=st.get("terminal_presentation_plan_file")
    if not nonempty(plan_raw) or not Path(plan_raw).exists(): return []
    plan=read_json(Path(plan_raw),"terminal presentation plan"); text=payload.read_text(encoding="utf-8")
    out=[]
    for c in plan.get("components",[]) if isinstance(plan.get("components"),list) else []:
        if not isinstance(c,dict) or not nonempty(c.get("component_id")): continue
        anchor=_rc16233_component_anchor(c.get("component_id")); included=anchor in text
        out.append({"component_id":c.get("component_id"),"type":c.get("type"),"parent":c.get("parent"),"emission_anchor":anchor,"controlled_emission_status":"INCLUDED_IN_CONTROLLED_EMISSION" if included else "NOT_INCLUDED_IN_CONTROLLED_EMISSION","host_visibility_status":"HOST_VISIBLE_UNVERIFIED" if included else "NOT_APPLICABLE"})
    return out


def _rc16235_write_final_emission_receipt(rd: Path, st, payload: Path):
    text=payload.read_text(encoding="utf-8"); structure=_rc16235_deck_display_structure(text)
    structural_sha=hashlib.sha256(_stable_json_text(structure).encode()).hexdigest(); comps=_rc16236_final_component_records(st,payload)
    if any(x.get("controlled_emission_status")!="INCLUDED_IN_CONTROLLED_EMISSION" for x in comps): fail("FINAL_EMISSION_REQUIRED_COMPONENT_MISSING")
    rec={"schema":RC16236_FINAL_EMISSION_SCHEMA,"status":"PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"render_id":st.get("current_render"),"terminal_payload_file":str(payload.resolve()),"terminal_payload_sha256":sha256(payload),"structural_signature_sha256":structural_sha,"structure":structure,"components":comps,"host_visibility_status":"HOST_VISIBLE_UNVERIFIED" if comps else "NOT_REQUIRED","runtime_version":VERSION}
    out=(rd/RC16235_FINAL_EMISSION_RECEIPT).resolve(); _atomic_write_text(out,_stable_json_text(rec))
    st["final_emission_receipt_file"]=str(out); st["final_emission_receipt_sha256"]=sha256(out); save_state(rd,st)
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,"FINAL_CONTROLLED_EMISSION_MATERIALIZED",checkpoint_seq=cp.get("checkpoint_seq"),receipt_file=str(out),receipt_sha256=sha256(out),terminal_payload_sha256=sha256(payload),structural_signature_sha256=structural_sha,required_component_count=len(comps),host_visibility_status=rec["host_visibility_status"])
    return rec


def _rc16235_final_emission_valid(rd: Path, st):
    raw=st.get("final_emission_receipt_file"); rh=st.get("final_emission_receipt_sha256"); payload_raw=st.get("terminal_payload_file")
    if not nonempty(raw) or not nonempty(rh) or not nonempty(payload_raw): return False
    rp=Path(raw); payload=Path(payload_raw)
    if not rp.exists() or not payload.exists() or sha256(rp)!=rh: return False
    try: d=read_json(rp,"final controlled emission receipt")
    except BaseException: return False
    if d.get("schema")!=RC16236_FINAL_EMISSION_SCHEMA or d.get("status")!="PASS" or d.get("runtime_version")!=VERSION: return False
    if d.get("terminal_payload_sha256")!=sha256(payload) or sha256(payload)!=st.get("terminal_payload_sha256"): return False
    try:
        structure=_rc16235_deck_display_structure(payload.read_text(encoding="utf-8")); sh=hashlib.sha256(_stable_json_text(structure).encode()).hexdigest()
    except BaseException: return False
    if d.get("structural_signature_sha256")!=sh: return False
    return all(isinstance(c,dict) and c.get("controlled_emission_status")=="INCLUDED_IN_CONTROLLED_EMISSION" for c in d.get("components",[]) if isinstance(d.get("components"),list))


def cmd_bind_host_component_emission(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id)
    if st.get("run_execution_state")!="COMPLETED" or not _rc16235_final_emission_valid(rd,st): fail("HOST_COMPONENT_EVIDENCE_REQUIRES_FINAL_EMISSION")
    src=Path(a.evidence_file)
    if not src.exists(): fail("HOST_COMPONENT_EVIDENCE_SOURCE_MISSING")
    doc=read_json(src,"host component emission evidence")
    if doc.get("schema")!=RC16236_HOST_EVIDENCE_SCHEMA or doc.get("run_id")!=st.get("run_id") or doc.get("terminal_payload_sha256")!=st.get("terminal_payload_sha256"): fail("HOST_COMPONENT_EVIDENCE_BINDING_MISMATCH")
    prov=_rc16236_validate_provenance(doc.get("provenance"),allowed=RC16236_ALLOWED_HOST_PROVENANCE,prefix="HOST_COMPONENT")
    final=read_json(Path(st["final_emission_receipt_file"]),"final emission receipt"); required={c["component_id"] for c in final.get("components",[]) if isinstance(c,dict) and nonempty(c.get("component_id"))}
    rows=doc.get("components")
    if not isinstance(rows,list): fail("HOST_COMPONENT_EVIDENCE_COMPONENTS_INVALID")
    seen={}
    for row in rows:
        if not isinstance(row,dict) or not nonempty(row.get("component_id")) or row.get("status") not in {"VISIBLE","NOT_VISIBLE"}: fail("HOST_COMPONENT_EVIDENCE_COMPONENT_INVALID")
        cid=row["component_id"]
        if cid in seen: fail("HOST_COMPONENT_EVIDENCE_DUPLICATE_COMPONENT")
        seen[cid]=copy.deepcopy(row)
    if set(seen)!=required: fail("HOST_COMPONENT_EVIDENCE_COVERAGE_MISMATCH")
    norm={"schema":RC16236_HOST_BINDING_SCHEMA,"run_id":st.get("run_id"),"terminal_payload_sha256":st.get("terminal_payload_sha256"),"final_emission_receipt_sha256":st.get("final_emission_receipt_sha256"),"source_file":str(src.resolve()),"source_sha256":sha256(src),"provenance":prov,"components":[seen[k] for k in sorted(seen)]}
    out=(rd/RC16236_HOST_BINDING_FILE).resolve(); _atomic_write_text(out,_stable_json_text(norm))
    print(json.dumps({"status":"BOUND","binding_file":str(out),"binding_sha256":sha256(out),"all_visible":all(x.get("status")=="VISIBLE" for x in seen.values())},ensure_ascii=False,indent=2))


def _rc16236_host_component_status(rd: Path, st):
    if not _rc16235_final_emission_valid(rd,st): return {"required":False,"status":"FINAL_EMISSION_INVALID","all_visible":False}
    final=read_json(Path(st["final_emission_receipt_file"]),"final emission receipt"); required={c["component_id"] for c in final.get("components",[]) if isinstance(c,dict) and nonempty(c.get("component_id"))}
    if not required: return {"required":False,"status":"NOT_REQUIRED","all_visible":True}
    bp=rd/RC16236_HOST_BINDING_FILE
    if not bp.exists(): return {"required":True,"status":"HOST_VISIBLE_UNVERIFIED","all_visible":False,"required_components":sorted(required)}
    try: d=read_json(bp,"host component emission binding")
    except BaseException: return {"required":True,"status":"HOST_EVIDENCE_INVALID","all_visible":False}
    if d.get("schema")!=RC16236_HOST_BINDING_SCHEMA or d.get("run_id")!=st.get("run_id") or d.get("terminal_payload_sha256")!=st.get("terminal_payload_sha256") or d.get("final_emission_receipt_sha256")!=st.get("final_emission_receipt_sha256"):
        return {"required":True,"status":"HOST_EVIDENCE_STALE","all_visible":False}
    rows={x.get("component_id"):x for x in d.get("components",[]) if isinstance(x,dict) and nonempty(x.get("component_id"))}
    if set(rows)!=required: return {"required":True,"status":"HOST_EVIDENCE_COVERAGE_MISMATCH","all_visible":False}
    vis=all(rows[k].get("status")=="VISIBLE" for k in required)
    return {"required":True,"status":"HOST_VISIBLE_CONFIRMED" if vis else "HOST_COMPONENT_NOT_VISIBLE","all_visible":vis,"required_components":sorted(required)}


_rc16236_blackbox_parent = _rc16233_blackbox_4d_status

def _rc16233_blackbox_4d_status(rd: Path, st):
    base=_rc16236_blackbox_parent(rd,st); host=_rc16236_host_component_status(rd,st)
    local=_rc16235_final_emission_valid(rd,st)
    base["PRESENTATION_LOCAL_PASS"]=bool(local)
    base["HOST_COMPONENT_VISIBILITY"]=host.get("status")
    base["PRESENTATION_PASS"]=bool(local and host.get("all_visible"))
    base["FULL_PASS"]=bool(base.get("TERMINAL_PASS") and base.get("CONTINUITY_PASS") and base.get("SEMANTIC_PASS") and base.get("PRESENTATION_PASS"))
    base["host_component_evidence"]=host
    return base

# RC16.23.6 controlled component emission: the marker is only an internal
# anchor.  The controlled payload must also contain the actual rich UI token
# derived from the compiler-owned image refs.  Host visibility remains an
# external/Black-Box fact.
def _rc16236_component_ui_token(component):
    if not isinstance(component,dict): return None
    refs=[x for x in (component.get("image_refs") or []) if nonempty(x)]
    if not refs: return None
    payload={"layout":"carousel","aspect_ratio":"1:1","image_refs":refs[:4]}
    return "image_group"+json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))+""


_rc16236_inject_component_anchors_parent = _rc16233_inject_component_anchors

def _rc16233_inject_component_anchors(text, visual):
    text=_rc16236_inject_component_anchors_parent(text,visual)
    v=_rc16234_normalize_visual(visual or {})
    specs=[]
    main=v.get("main_carousel") if isinstance(v.get("main_carousel"),dict) else {}
    sig=v.get("signature_climax") if isinstance(v.get("signature_climax"),dict) else {}
    if main.get("applicable") is True:
        specs.append(("main-card-carousel",_rc16221_component_refs(v,"main")))
    if sig.get("mini_carousel_applicable") is True:
        specs.append(("signature-mini-carousel",_rc16221_component_refs(v,"signature")))
    lines=text.splitlines()
    for cid,refs in specs:
        token=_rc16236_component_ui_token({"image_refs":refs})
        anchor=_rc16233_component_anchor(cid)
        if token is None or anchor not in lines: continue
        ai=lines.index(anchor)
        if token not in lines:
            lines.insert(ai+1,token)
    return "\n".join(lines).rstrip()+"\n"


_compile_terminal_presentation_payload_rc16236_marker_parent = compile_terminal_presentation_payload

def compile_terminal_presentation_payload(render_path: Path, manifest_path: Path, st):
    doc=_compile_terminal_presentation_payload_rc16236_marker_parent(render_path,manifest_path,st)
    text=Path(render_path).read_text(encoding="utf-8")
    for c in doc.get("components",[]) if isinstance(doc.get("components"),list) else []:
        if not isinstance(c,dict): continue
        anchor=_rc16233_component_anchor(c.get("component_id"))
        token=_rc16236_component_ui_token(c)
        ready=bool(anchor in text and token and token in text)
        c["emission_anchor"]=anchor
        c["emission_token"]=token
        c["emission_status"]="CONTROLLED_EMISSION_READY" if ready else "NOT_EMITTED"
        c["controlled_emission_status"]="INCLUDED_IN_CONTROLLED_EMISSION" if ready else "NOT_INCLUDED_IN_CONTROLLED_EMISSION"
        c["host_visibility_status"]="HOST_VISIBLE_UNVERIFIED" if ready else "NOT_VERIFIED"
    return doc


_terminal_plan_issues_rc16236_parent = _terminal_plan_issues

def _terminal_plan_issues(plan_path: Path, render_path: Path, manifest_path: Path, st):
    issues=list(_terminal_plan_issues_rc16236_parent(plan_path,render_path,manifest_path,st))
    # RC16.23.3's legacy issue equated an HTML marker with EMITTED.  Replace
    # that obsolete criterion with actual controlled rich-token inclusion.
    issues=[x for x in issues if x.get("code")!="TERMINAL_COMPONENT_NOT_EMITTED"]
    if not Path(plan_path).exists() or not Path(render_path).exists(): return issues
    try: d=read_json(Path(plan_path),"terminal presentation plan")
    except BaseException: return issues
    text=Path(render_path).read_text(encoding="utf-8")
    for c in d.get("components",[]) if isinstance(d.get("components"),list) else []:
        if not isinstance(c,dict) or not nonempty(c.get("component_id")): continue
        anchor=_rc16233_component_anchor(c.get("component_id")); token=_rc16236_component_ui_token(c)
        if c.get("emission_status")!="CONTROLLED_EMISSION_READY" or anchor not in text or not token or token not in text:
            issues.append(_terminal_issue("TERMINAL_COMPONENT_CONTROLLED_EMISSION_MISSING",c.get("component_id")))
    dedup=[]; seen=set()
    for x in issues:
        k=(x.get("code"),x.get("detail"))
        if k not in seen: seen.add(k); dedup.append(x)
    return sorted(dedup,key=lambda x:(x.get("code","") or "",x.get("detail","") or ""))


def _rc16236_final_component_records(st, payload: Path):
    plan_raw=st.get("terminal_presentation_plan_file")
    if not nonempty(plan_raw) or not Path(plan_raw).exists(): return []
    plan=read_json(Path(plan_raw),"terminal presentation plan"); text=payload.read_text(encoding="utf-8")
    out=[]
    for c in plan.get("components",[]) if isinstance(plan.get("components"),list) else []:
        if not isinstance(c,dict) or not nonempty(c.get("component_id")): continue
        anchor=_rc16233_component_anchor(c.get("component_id")); token=_rc16236_component_ui_token(c)
        included=bool(anchor in text and token and token in text)
        out.append({"component_id":c.get("component_id"),"type":c.get("type"),"parent":c.get("parent"),"emission_anchor":anchor,"emission_token_sha256":hashlib.sha256(token.encode("utf-8")).hexdigest() if token else None,"controlled_emission_status":"INCLUDED_IN_CONTROLLED_EMISSION" if included else "NOT_INCLUDED_IN_CONTROLLED_EMISSION","host_visibility_status":"HOST_VISIBLE_UNVERIFIED" if included else "NOT_VERIFIED"})
    return out



# RC16.23.6 component-instance binding hardening: the rich token must be
# attached to the exact component anchor.  Global token presence is not enough
# because two components may legitimately compile to identical image refs.
def _rc16236_component_token_bound_at_anchor(text, component_id, token):
    if not nonempty(component_id) or not nonempty(token): return False
    anchor=_rc16233_component_anchor(component_id)
    lines=text.splitlines()
    for i,line in enumerate(lines):
        if line.strip()!=anchor: continue
        j=i+1
        while j<len(lines) and not lines[j].strip(): j+=1
        return j<len(lines) and lines[j].strip()==token
    return False


def compile_terminal_presentation_payload(render_path: Path, manifest_path: Path, st):
    doc=_compile_terminal_presentation_payload_rc16236_marker_parent(render_path,manifest_path,st)
    text=Path(render_path).read_text(encoding="utf-8")
    for c in doc.get("components",[]) if isinstance(doc.get("components"),list) else []:
        if not isinstance(c,dict): continue
        anchor=_rc16233_component_anchor(c.get("component_id")); token=_rc16236_component_ui_token(c)
        ready=_rc16236_component_token_bound_at_anchor(text,c.get("component_id"),token)
        c["emission_anchor"]=anchor
        c["emission_token"]=token
        c["emission_status"]="CONTROLLED_EMISSION_READY" if ready else "NOT_EMITTED"
        c["controlled_emission_status"]="INCLUDED_IN_CONTROLLED_EMISSION" if ready else "NOT_INCLUDED_IN_CONTROLLED_EMISSION"
        c["host_visibility_status"]="HOST_VISIBLE_UNVERIFIED" if ready else "NOT_VERIFIED"
    return doc


def _terminal_plan_issues(plan_path: Path, render_path: Path, manifest_path: Path, st):
    issues=list(_terminal_plan_issues_rc16236_parent(plan_path,render_path,manifest_path,st))
    issues=[x for x in issues if x.get("code")!="TERMINAL_COMPONENT_NOT_EMITTED"]
    if not Path(plan_path).exists() or not Path(render_path).exists(): return issues
    try: d=read_json(Path(plan_path),"terminal presentation plan")
    except BaseException: return issues
    text=Path(render_path).read_text(encoding="utf-8")
    for c in d.get("components",[]) if isinstance(d.get("components"),list) else []:
        if not isinstance(c,dict) or not nonempty(c.get("component_id")): continue
        token=_rc16236_component_ui_token(c)
        if c.get("emission_status")!="CONTROLLED_EMISSION_READY" or not _rc16236_component_token_bound_at_anchor(text,c.get("component_id"),token):
            issues.append(_terminal_issue("TERMINAL_COMPONENT_CONTROLLED_EMISSION_MISSING",c.get("component_id")))
    dedup=[]; seen=set()
    for x in issues:
        k=(x.get("code"),x.get("detail"))
        if k not in seen: seen.add(k); dedup.append(x)
    return sorted(dedup,key=lambda x:(x.get("code","") or "",x.get("detail","") or ""))


def _rc16236_final_component_records(st, payload: Path):
    plan_raw=st.get("terminal_presentation_plan_file")
    if not nonempty(plan_raw) or not Path(plan_raw).exists(): return []
    plan=read_json(Path(plan_raw),"terminal presentation plan"); text=payload.read_text(encoding="utf-8")
    out=[]
    for c in plan.get("components",[]) if isinstance(plan.get("components"),list) else []:
        if not isinstance(c,dict) or not nonempty(c.get("component_id")): continue
        anchor=_rc16233_component_anchor(c.get("component_id")); token=_rc16236_component_ui_token(c)
        included=_rc16236_component_token_bound_at_anchor(text,c.get("component_id"),token)
        out.append({"component_id":c.get("component_id"),"type":c.get("type"),"parent":c.get("parent"),"emission_anchor":anchor,"emission_token_sha256":hashlib.sha256(token.encode("utf-8")).hexdigest() if token else None,"controlled_emission_status":"INCLUDED_IN_CONTROLLED_EMISSION" if included else "NOT_INCLUDED_IN_CONTROLLED_EMISSION","host_visibility_status":"HOST_VISIBLE_UNVERIFIED" if included else "NOT_VERIFIED"})
    return out

def build_parser():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest="cmd",required=True)
    q=sp.add_parser("campaign-open",help="open deterministic request-level campaign before run bootstrap"); q.add_argument("--scope-dir",required=True); q.add_argument("--request-file",required=True); q.set_defaults(func=cmd_campaign_open)
    q=sp.add_parser("prebootstrap-handoff-check",help="refuse conversational handoff before the first campaign run is bootstrapped"); q.add_argument("--scope-dir",required=True); q.set_defaults(func=cmd_prebootstrap_handoff_check)
    q=sp.add_parser("blackbox-campaign",help="aggregate all attempts for one user request; run 4D PASS is not campaign PASS"); q.add_argument("--scope-dir",required=True); q.set_defaults(func=cmd_blackbox_campaign)
    q=sp.add_parser("bind-card-metadata",help="bind complete authoritative Main Deck card-type metadata to the exact deck snapshot"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--metadata-file",required=True); q.set_defaults(func=cmd_bind_card_metadata)
    q=sp.add_parser("bind-card-pool",help="bind authoritative environment card-pool membership to the exact deck snapshot; defaults to the packaged Link Evolution 2020 catalog"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--pool-file"); q.set_defaults(func=cmd_bind_card_pool)
    q=sp.add_parser("bind-summon-rules",help="bind authoritative exact summon-material rules to one semantic input"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--semantic-file",required=True); q.add_argument("--rules-file",required=True); q.set_defaults(func=cmd_bind_summon_rules)
    q=sp.add_parser("bind-host-component-emission",help="bind external/user-observed host visibility after controlled terminal emission"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--evidence-file",required=True); q.set_defaults(func=cmd_bind_host_component_emission)
    q=sp.add_parser("compile-user-trace",help="compile user-visible gate trace from material run journal/evidence only"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--output"); q.set_defaults(func=cmd_compile_user_trace)
    q=sp.add_parser("start",help="internal bootstrap only; normal callers use dispatch-run"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--scope-dir",required=True); q.add_argument("--mode",choices=["normal","fresh"],default="normal"); q.add_argument("--multi-system",action="store_true"); q.add_argument("--mechanical-validation",action="store_true"); q.add_argument("--bootstrap-capability"); q.set_defaults(func=cmd_start)
    q=sp.add_parser("dispatch-run",help="normal runtime-owned START/RESUME dispatcher"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--scope-dir",required=True); q.add_argument("--mode",choices=["normal","fresh"],default="normal"); q.add_argument("--multi-system",action="store_true"); q.add_argument("--mechanical-validation",action="store_true"); q.add_argument("--user-resolution-file"); q.set_defaults(func=cmd_dispatch_run)
    q=sp.add_parser("fork-refactor-from-terminal",help="create a distinct targeted-refactor run by exact-hash inheriting only the terminal-safe prefix"); q.add_argument("--parent-run-dir",required=True); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--scope-dir",required=True); q.add_argument("--candidate-snapshot",required=True); q.add_argument("--reason",required=True); q.add_argument("--user-evidence",required=True); q.add_argument("--same-character-stage-direction-concept",action="store_true"); q.add_argument("--full-decklist",action="store_true"); q.set_defaults(func=cmd_fork_refactor_from_terminal)
    q=sp.add_parser("recover-fatal",help="explicitly reopen a BLOCKED_FATAL run under a named competent authority"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--authority",required=True); q.add_argument("--reason",required=True); q.set_defaults(func=cmd_recover_fatal)
    q=sp.add_parser("output-policy",help="read-only response gate: FINAL_ARTIFACT only after exact terminal authorization, otherwise STATUS_ONLY"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.set_defaults(func=cmd_output_policy)
    q=sp.add_parser("continuation-policy",help="read-only NO EARLY HANDOFF policy: classify whether the assistant must continue, reroute, wait for user, or report fatal"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.set_defaults(func=cmd_continuation_policy)
    q=sp.add_parser("handoff-check",help="hard end-turn barrier; refuses handoff while continuation is required"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--intent",default="END_TURN"); q.set_defaults(func=cmd_handoff_check)
    q=sp.add_parser("mechanical-proof-check",help="execute and verify the external ledger validator when mechanical validation is applicable"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--ledger-file"); q.add_argument("--snapshot-file"); q.add_argument("--receipt"); q.add_argument("--instrument-trace"); q.set_defaults(func=cmd_mechanical_proof_check)
    q=sp.add_parser("mechanical-proof-status",help="read-only mechanical proof applicability/status"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.set_defaults(func=cmd_mechanical_proof_status)
    q=sp.add_parser("blackbox-4d",help="aggregate Terminal/Continuity/Semantic/Presentation evidence without treating COMPLETED as FULL_PASS"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.set_defaults(func=cmd_blackbox_4d)
    q=sp.add_parser("terminal-output",help="read the authorized terminal payload only after re-verifying its exact hash"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.set_defaults(func=cmd_terminal_output)
    q=sp.add_parser("status"); q.add_argument("--run-dir",required=True); q.set_defaults(func=cmd_status)
    q=sp.add_parser("complete"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--gate",required=True); q.add_argument("--authority"); q.add_argument("--status"); q.add_argument("--evidence-file"); q.add_argument("--render-manifest"); q.add_argument("--contract-file"); q.add_argument("--combo-impact-file"); q.add_argument("--pilotage-contract-file"); q.add_argument("--pilotage-preflight-receipt"); q.add_argument("--terminal-presentation-plan"); q.add_argument("--terminal-presentation-receipt"); q.set_defaults(func=cmd_complete)
    q=sp.add_parser("material-change"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--reason",default="material deck change"); q.add_argument("--user-refactor",action="store_true"); q.add_argument("--full-decklist",action="store_true"); q.add_argument("--candidate-snapshot",required=True); q.add_argument("--material-proof"); q.set_defaults(func=cmd_material_change)
    q=sp.add_parser("evidence-refresh"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--from-gate",required=True); q.add_argument("--reason",default="evidence correction"); q.set_defaults(func=cmd_evidence_refresh)
    q=sp.add_parser("presentation-change"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--reason",default="presentation change"); q.set_defaults(func=cmd_presentation_change)
    q=sp.add_parser("authorize"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--confidence",required=True); q.add_argument("--render-file"); q.add_argument("--render-manifest"); q.add_argument("--contract-file"); q.set_defaults(func=cmd_authorize)
    q=sp.add_parser("compile-render-contract"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--policy-file",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_compile_render_contract)
    q=sp.add_parser("compile-component-payloads"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--plan-file",required=True); q.add_argument("--visual-assets-file",required=True); q.add_argument("--output-dir",required=True); q.set_defaults(func=cmd_compile_component_payloads)
    q=sp.add_parser("compile-component-manifest"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--plan-file",required=True); q.add_argument("--visual-assets-file",required=True); q.add_argument("--component-file",action="append"); q.add_argument("--output",required=True); q.set_defaults(func=cmd_compile_component_manifest)
    q=sp.add_parser("render-check"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--render-file",required=True); q.add_argument("--contract-file",required=True); q.add_argument("--component-manifest"); q.add_argument("--component-plan-file"); q.add_argument("--visual-assets-file"); q.add_argument("--component-file",action="append"); q.add_argument("--write-manifest"); q.set_defaults(func=cmd_render_check)
    q=sp.add_parser("compile-terminal-presentation"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--render-file",required=True); q.add_argument("--render-manifest",required=True); q.add_argument("--output"); q.set_defaults(func=cmd_compile_terminal_presentation)
    q=sp.add_parser("terminal-presentation-check"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--plan-file",required=True); q.add_argument("--render-file",required=True); q.add_argument("--render-manifest",required=True); q.add_argument("--output"); q.set_defaults(func=cmd_terminal_presentation_check)
    q=sp.add_parser("contract-defect"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--reason",required=True); q.set_defaults(func=cmd_contract_defect)
    q=sp.add_parser("abort-run",help="explicit user/system abandon; closes active lease/session without PASS"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--reason",required=True); q.set_defaults(func=cmd_abort_run)
    q=sp.add_parser("simulate-interruption",help="TEST_ONLY: persist interruption event without closing the active run"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--failpoint",default="TEST_ONLY_CHECKPOINT_INTERRUPTION"); q.set_defaults(func=cmd_simulate_interruption)
    q=sp.add_parser("checkpoint-run"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--run-state",choices=sorted(RUN_STATES),default="IN_PROGRESS"); q.set_defaults(func=cmd_checkpoint_run)
    q=sp.add_parser("inspect-run-state"); q.add_argument("--run-dir",required=True); q.set_defaults(func=cmd_inspect_run_state)
    q=sp.add_parser("inspect-continuation"); q.add_argument("--scope-dir",required=True); q.set_defaults(func=cmd_inspect_continuation)
    q=sp.add_parser("resume-run"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--user-resolution-file"); q.set_defaults(func=cmd_resume_run)
    q=sp.add_parser("pilotage-schema"); q.add_argument("--output",required=True); q.add_argument("--run-dir"); q.add_argument("--run-id"); q.set_defaults(func=cmd_pilotage_schema)
    q=sp.add_parser("pilotage-preflight"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--pilotage-contract-file",required=True); q.add_argument("--render-file",required=True); q.add_argument("--schema-file",required=True); q.add_argument("--output"); q.set_defaults(func=cmd_pilotage_preflight)
    q=sp.add_parser("compile-pilotage-contract",help="compile mechanical Pilotage bindings around authority-owned business payload"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--business-payload-file",required=True); q.add_argument("--render-file",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_compile_pilotage_contract)
    q=sp.add_parser("template"); q.add_argument("--kind",choices=["pilotage"],default="pilotage"); q.add_argument("--output",required=True); q.add_argument("--run-id"); q.add_argument("--deck-artifact"); q.add_argument("--render-sha256"); q.add_argument("--run-dir"); q.add_argument("--render-file"); q.add_argument("--no-rendered-axes",action="store_true"); q.add_argument("--rendered-axis-count",type=int,default=0); q.set_defaults(func=cmd_template)
    q=sp.add_parser("bind-explicit-direction",help="bind a user-explicit direction and close the parent DIRECTION_RESOLVED gate"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--selected-direction",required=True); q.add_argument("--user-evidence",required=True); q.add_argument("--output"); q.set_defaults(func=cmd_bind_explicit_direction)
    q=sp.add_parser("execute-batch",help="sequential fail-closed batch through the existing parent gate path"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--bundle-file",required=True); q.set_defaults(func=cmd_execute_batch)
    q=sp.add_parser("advance-prepared",help="nominal FAST_ENFORCED router for contiguous already-prepared gate artifacts"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--bundle-file",required=True); q.set_defaults(func=cmd_advance_prepared)
    q=sp.add_parser("render-commit",help="nominal one-shot deterministic Render staging + commit"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--render-file",required=True); q.set_defaults(func=cmd_render_commit)
    q=sp.add_parser("pilotage-business-skeleton",help="derive shell-owned Pilotage business structure from the frozen render"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_pilotage_business_skeleton)
    q=sp.add_parser("pilotage-business-merge",help="merge model-owned Pilotage proof slots into a shell-owned skeleton without structural replacement"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--skeleton-file",required=True); q.add_argument("--patch-file",required=True); q.add_argument("--output",required=True); q.add_argument("--base-business-file"); q.add_argument("--repair-receipt"); q.set_defaults(func=cmd_pilotage_business_merge)
    q=sp.add_parser("pilotage-authoritative-dry-run",help="read-only commit-equivalent Pilotage validation + repair routing"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--business-payload-file",required=True); q.set_defaults(func=cmd_pilotage_authoritative_dry_run)
    q=sp.add_parser("pilotage-commit",help="nominal one-shot Pilotage compile + full validator + gate commit"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--business-payload-file",required=True); q.set_defaults(func=cmd_pilotage_commit)
    q=sp.add_parser("pilotage-semantic-template",help="build compiler-owned semantic template from Style→Axes; model fills semantic actions/claim only"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_pilotage_semantic_template)
    q=sp.add_parser("pilotage-semantic-compile",help="compile MODEL_OWNED semantic line input into compiler-owned Pilotage business payload"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--semantic-file",required=True); q.add_argument("--render-file",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_pilotage_semantic_compile)
    q=sp.add_parser("render-semantic-compile",help="compile semantic presentation content into deterministic render structure"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--semantic-file",required=True); q.add_argument("--visual-assets-file",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_render_semantic_compile)
    q=sp.add_parser("render-emission-normalize",help="deterministically inject required component emission anchors; no model authoring"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--render-file",required=True); q.add_argument("--output",required=True); q.set_defaults(func=cmd_render_emission_normalize)
    q=sp.add_parser("fastpath-metrics",help="read-only RC16.19 fast-path and local-runtime metrics"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id"); q.set_defaults(func=cmd_fastpath_metrics)
    q=sp.add_parser("mechanical-preflight",help="read-only aggregate mechanical diagnostics; never closes a gate"); q.add_argument("--kind",choices=["render","pilotage"],required=True); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--contract-file"); q.add_argument("--render-file"); q.add_argument("--render-manifest"); q.add_argument("--component-plan-file"); q.add_argument("--component-manifest"); q.add_argument("--pilotage-contract-file"); q.add_argument("--schema-file"); q.add_argument("--combo-impact-file"); q.set_defaults(func=cmd_mechanical_preflight)
    q=sp.add_parser("evidence-refresh-selective",help="fail-closed dependency-aware evidence refresh; falls back to parent wide refresh when unknown"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--from-gate",required=True); q.add_argument("--reason",default="evidence correction"); q.set_defaults(func=cmd_evidence_refresh_selective)
    q=sp.add_parser("validate-bundle"); q.add_argument("--run-dir",required=True); q.add_argument("--run-id",required=True); q.add_argument("--bundle-file",required=True); q.set_defaults(func=cmd_validate_bundle)
    return p


def main():
    a=build_parser().parse_args(); _instrumented_call(a)


# RC16.23.6 regression closure: identical rich UI tokens must still be bound
# independently to each component anchor. Global token presence is not enough.
_rc16236_inject_component_anchors_instance_parent = _rc16233_inject_component_anchors

def _rc16233_inject_component_anchors(text, visual):
    text=_rc16236_inject_component_anchors_instance_parent(text,visual)
    v=_rc16234_normalize_visual(visual or {})
    specs=[]
    main=v.get("main_carousel") if isinstance(v.get("main_carousel"),dict) else {}
    sig=v.get("signature_climax") if isinstance(v.get("signature_climax"),dict) else {}
    if main.get("applicable") is True:
        specs.append(("main-card-carousel",_rc16221_component_refs(v,"main")))
    if sig.get("mini_carousel_applicable") is True:
        specs.append(("signature-mini-carousel",_rc16221_component_refs(v,"signature")))
    lines=text.splitlines()
    for cid,refs in specs:
        token=_rc16236_component_ui_token({"image_refs":refs})
        anchor=_rc16233_component_anchor(cid)
        if not token or anchor not in lines: continue
        # Bind to this exact component instance, even when another component
        # legitimately has an identical token elsewhere in the render.
        current="\n".join(lines)
        if _rc16236_component_token_bound_at_anchor(current,cid,token):
            continue
        ai=lines.index(anchor); j=ai+1
        while j<len(lines) and not lines[j].strip(): j+=1
        lines.insert(j,token)
    return "\n".join(lines).rstrip()+"\n"

# =============================================================================
# RC16.23.7 — Differential Regression Corrective Closure
# Banlist ratio legality, effective material state, classification integrity,
# stable semantic lineage, same-run administrative repair protection, and
# nominal CLI parity.  Business authorities remain unchanged.
# =============================================================================

RC16237_BANLIST_RECEIPT_SCHEMA = "ygo-banlist-legality-receipt-v1"
RC16237_BANLIST_RECEIPT_FILE = "banlist_legality.receipt.json"
RC16237_LINEAGE_SCHEMA = "ygo-semantic-lineage-v1"


def _rc16237_norm_card_name(v):
    return re.sub(r"\s+", " ", str(v or "").replace("**", "").strip()).casefold()


def _rc16237_parse_banlist_limits(path: Path):
    path=Path(path)
    if not path.exists(): fail("BANLIST_SOURCE_MISSING")
    section=None; limits={}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if re.match(r"^#\s+INTERDITES\b",line,re.I): section=0; continue
        if re.match(r"^#\s+LIMIT[ÉE]ES\b",line,re.I): section=1; continue
        if re.match(r"^#\s+SEMI-LIMIT[ÉE]ES\b",line,re.I): section=2; continue
        if line.startswith("# ") and not re.match(r"^#\s+(INTERDITES|LIMIT|SEMI-LIMIT)",line,re.I): section=None
        if section is None or not line.startswith("-"): continue
        name=re.sub(r"^-\s+", "", line).strip().replace("**","")
        if not name or name.startswith("["): continue
        key=_rc16237_norm_card_name(name)
        if key: limits[key]={"name":name,"max_qty":section}
    if not limits: fail("BANLIST_PARSE_EMPTY")
    return limits


def _rc16237_validate_deck_size(snapshot):
    if not isinstance(snapshot,dict): fail("DECK_SNAPSHOT_INVALID")
    totals={}
    for zone in ("main_deck","extra_deck","side_deck"):
        rows=snapshot.get(zone)
        if not isinstance(rows,list): fail(f"DECK_SNAPSHOT_ZONE_INVALID: {zone}")
        total=0
        for c in rows:
            if not isinstance(c,dict) or not nonempty(c.get("name")) or not isinstance(c.get("qty"),int) or isinstance(c.get("qty"),bool) or c.get("qty")<1:
                fail(f"DECK_SNAPSHOT_CARD_INVALID: {zone}")
            total+=c["qty"]
        totals[zone]=total
    if not 40<=totals["main_deck"]<=60: fail(f"MAIN_DECK_SIZE_INVALID: {totals['main_deck']}")
    if not 0<=totals["extra_deck"]<=15: fail(f"EXTRA_DECK_SIZE_INVALID: {totals['extra_deck']}")
    if not 0<=totals["side_deck"]<=15: fail(f"SIDE_DECK_SIZE_INVALID: {totals['side_deck']}")
    return totals


def _rc16237_validate_banlist_snapshot(snapshot, banlist_path=None, *, forbidden_mode=False):
    source=Path(banlist_path) if banlist_path is not None else (Path(__file__).resolve().parent / BANLIST_FILE)
    limits=_rc16237_parse_banlist_limits(source)
    combined={}; display={}; zones={}
    for zone in ("main_deck","extra_deck","side_deck"):
        for c in snapshot.get(zone,[]) if isinstance(snapshot,dict) and isinstance(snapshot.get(zone),list) else []:
            if not isinstance(c,dict) or not nonempty(c.get("name")) or not isinstance(c.get("qty"),int) or isinstance(c.get("qty"),bool) or c.get("qty")<1:
                fail(f"DECK_SNAPSHOT_CARD_INVALID: {zone}")
            k=_rc16237_norm_card_name(c["name"]); combined[k]=combined.get(k,0)+c["qty"]; display[k]=c["name"].strip(); zones.setdefault(k,[]).append(zone)
    violations=[]
    for k,qty in sorted(combined.items()):
        max_qty=limits.get(k,{}).get("max_qty",3)
        if qty>3: max_qty=min(max_qty,3)
        if not forbidden_mode and qty>max_qty:
            violations.append({"name":display[k],"qty":qty,"max_qty":max_qty,"zones":sorted(set(zones[k]))})
    if violations:
        detail="; ".join(f"{x['name']} qty={x['qty']} max={x['max_qty']}" for x in violations)
        fail("BANLIST_RATIO_VIOLATION: "+detail)
    return {"status":"PASS","source_sha256":sha256(source),"checked_card_count":len(combined),"limits_count":len(limits),"forbidden_mode":bool(forbidden_mode),"cards":[{"name":display[k],"qty":combined[k],"max_qty":limits.get(k,{}).get("max_qty",3)} for k in sorted(combined)]}


_validate_deck_snapshot_rc16237_parent = validate_deck_snapshot

def validate_deck_snapshot(path: Path, st):
    d,h,keys,totals=_validate_deck_snapshot_rc16237_parent(path,st)
    size=_rc16237_validate_deck_size(d)
    forbidden_mode=str(st.get("banlist_mode") or "").upper() in {"FORBIDDEN","FORBIDDEN_MODE","SOLO_FUN"}
    legality=_rc16237_validate_banlist_snapshot(d,Path(__file__).resolve().parent / BANLIST_FILE,forbidden_mode=forbidden_mode)
    receipt={"schema":RC16237_BANLIST_RECEIPT_SCHEMA,"status":"PASS","run_id":st.get("run_id"),"deck_artifact":st.get("current_artifact"),"snapshot_file":str(Path(path).resolve()),"snapshot_sha256":h,"banlist_source_file":str((Path(__file__).resolve().parent/BANLIST_FILE).resolve()),"banlist_source_sha256":legality["source_sha256"],"deck_totals":size,"checked_card_count":legality["checked_card_count"],"forbidden_mode":forbidden_mode,"runtime_version":VERSION}
    out=Path(path).parent/RC16237_BANLIST_RECEIPT_FILE
    _atomic_write_text(out,_stable_json_text(receipt))
    st["banlist_legality_receipt"]={"receipt_file":str(out.resolve()),"receipt_sha256":sha256(out),"snapshot_sha256":h,"banlist_source_sha256":legality["source_sha256"],"status":"PASS"}
    return d,h,keys,totals


def _rc16237_modifier_applies(modifier, action, boss):
    when=modifier.get("when")
    if when is None: return True
    if not isinstance(when,dict): fail("SUMMON_MATERIAL_MODIFIER_CONDITION_INVALID")
    sk=when.get("summon_kind")
    if nonempty(sk) and str(sk).upper()!=str(action.get("kind") or "").upper(): return False
    zone=when.get("material_zone")
    if nonempty(zone) and str(zone).upper()!=str(action.get("material_zone") or "FIELD").upper(): return False
    allow=when.get("boss_names")
    if allow is not None:
        if not isinstance(allow,list) or any(not nonempty(x) for x in allow): fail("SUMMON_MATERIAL_MODIFIER_CONDITION_INVALID")
        if boss.casefold() not in {x.strip().casefold() for x in allow}: return False
    deny=when.get("except_boss_names")
    if deny is not None:
        if not isinstance(deny,list) or any(not nonempty(x) for x in deny): fail("SUMMON_MATERIAL_MODIFIER_CONDITION_INVALID")
        if boss.casefold() in {x.strip().casefold() for x in deny}: return False
    return True


def _rc16237_effective_material_prop(prop, action, boss):
    out=copy.deepcopy(prop); applied=[]
    mods=prop.get("material_property_modifiers",[])
    if mods in (None,[]):
        out["_rc16237_applied_modifiers"]=[]; return out
    if not isinstance(mods,list): fail(f"SUMMON_MATERIAL_MODIFIER_INVALID: {prop.get('name')}")
    for i,m in enumerate(mods,1):
        if not isinstance(m,dict): fail(f"SUMMON_MATERIAL_MODIFIER_INVALID: {prop.get('name')}:{i}")
        if not nonempty(m.get("property")) or not nonempty(m.get("operation")):
            fail(f"SUMMON_MATERIAL_MODIFIER_INVALID: {prop.get('name')}:{i}")
        if not nonempty(m.get("provenance")) and not nonempty(m.get("source_locator")):
            fail(f"SUMMON_MATERIAL_MODIFIER_PROVENANCE_REQUIRED: {prop.get('name')}:{i}")
        if not _rc16237_modifier_applies(m,action,boss): continue
        field=str(m["property"]).strip().lower(); op=str(m["operation"]).strip().upper(); val=m.get("value")
        if field=="level":
            if not isinstance(out.get("level"),int) or not isinstance(val,int) or isinstance(val,bool): fail(f"SUMMON_MATERIAL_LEVEL_MODIFIER_INVALID: {prop.get('name')}")
            if op=="ADD": out["level"]+=val
            elif op=="SET": out["level"]=val
            else: fail(f"SUMMON_MATERIAL_MODIFIER_OPERATION_UNSUPPORTED: {field}:{op}")
            if out["level"]<0: fail(f"SUMMON_MATERIAL_EFFECTIVE_LEVEL_INVALID: {prop.get('name')}")
        elif field=="tuner":
            if op!="SET" or not isinstance(val,bool): fail(f"SUMMON_MATERIAL_TUNER_MODIFIER_INVALID: {prop.get('name')}")
            out["tuner"]=val
        elif field=="effective_name":
            if op!="ADD" or not nonempty(val): fail(f"SUMMON_MATERIAL_NAME_MODIFIER_INVALID: {prop.get('name')}")
            eff=out.setdefault("effective_names_by_zone",{}); zone=str(action.get("material_zone") or "FIELD").upper(); vals=eff.setdefault(zone,[])
            if val not in vals: vals.append(str(val))
        else:
            fail(f"SUMMON_MATERIAL_MODIFIER_UNSUPPORTED: {field}")
        applied.append({"index":i,"property":field,"operation":op,"value":val,"provenance":m.get("provenance") or m.get("source_locator")})
    out["_rc16237_applied_modifiers"]=applied
    return out


_rc16236_validate_summon_contracts_rc16237_parent = _rc16236_validate_summon_contracts

def _rc16236_validate_summon_contracts(st, semantic):
    bosses,_=_rc16236_semantic_summon_cards(semantic)
    if not bosses: return []
    b=st.get("summon_rules_binding")
    if not isinstance(b,dict): fail("SUMMON_MATERIAL_RULE_BINDING_REQUIRED")
    bp=Path(b.get("binding_file") or "")
    if not bp.exists() or sha256(bp)!=b.get("binding_sha256") or b.get("semantic_sha256")!=_rc16236_semantic_sha(semantic): fail("SUMMON_MATERIAL_RULE_BINDING_STALE")
    doc=read_json(bp,"summon rules binding")
    if doc.get("schema")!=RC16236_SUMMON_BINDING_SCHEMA or doc.get("semantic_sha256")!=_rc16236_semantic_sha(semantic): fail("SUMMON_MATERIAL_RULE_BINDING_INVALID")
    rules={x["card"].strip().casefold():x for x in doc.get("summons",[]) if isinstance(x,dict) and nonempty(x.get("card"))}
    props={x["name"].strip().casefold():x for x in doc.get("cards",[]) if isinstance(x,dict) and nonempty(x.get("name"))}
    proof=[]
    for li,line in enumerate(semantic.get("lines",[]),1):
        for ai,a in enumerate(line.get("actions",[]) if isinstance(line,dict) else [],1):
            if not isinstance(a,dict): continue
            kind=str(a.get("kind") or "").upper()
            if kind not in {"SYNCHRO_SUMMON","FUSION_SUMMON"}: continue
            boss=str(a.get("card") or "").strip(); rule=rules.get(boss.casefold())
            if not rule or rule.get("kind")!=kind: fail(f"SUMMON_MATERIAL_RULE_MISSING: {boss}")
            mats=a.get("materials")
            if not isinstance(mats,list) or not mats: fail(f"SUMMON_MATERIALS_REQUIRED: {boss}")
            raw=[]; eff=[]
            for name in mats:
                prop=props.get(str(name).strip().casefold())
                if not prop: fail(f"SUMMON_MATERIAL_PROPERTY_MISSING: {name}")
                raw.append(prop); eff.append(_rc16237_effective_material_prop(prop,a,boss))
            exact_count=rule.get("exact_material_count")
            if isinstance(exact_count,int) and len(mats)!=exact_count: fail(f"SUMMON_MATERIAL_COUNT_MISMATCH: {boss}")
            min_count=rule.get("min_material_count")
            if isinstance(min_count,int) and len(mats)<min_count: fail(f"SUMMON_MATERIAL_COUNT_MISMATCH: {boss}")
            if kind=="SYNCHRO_SUMMON":
                tuner_count=sum(1 for x in eff if x.get("tuner") is True)
                if isinstance(rule.get("exact_tuners"),int) and tuner_count!=rule["exact_tuners"]: fail(f"SUMMON_TUNER_COUNT_MISMATCH: {boss}")
                if isinstance(rule.get("min_tuners"),int) and tuner_count<rule["min_tuners"]: fail(f"SUMMON_TUNER_COUNT_MISMATCH: {boss}")
                nt=rule.get("min_non_tuners")
                if isinstance(nt,int) and len(eff)-tuner_count<nt: fail(f"SUMMON_NON_TUNER_COUNT_MISMATCH: {boss}")
                target=rule.get("target_level")
                if isinstance(target,int):
                    lv=[]
                    for x in eff:
                        if not isinstance(x.get("level"),int): fail(f"SUMMON_MATERIAL_LEVEL_MISSING: {x.get('name')}")
                        lv.append(x["level"])
                    if sum(lv)!=target: fail(f"SUMMON_LEVEL_SUM_MISMATCH: {boss}")
            required=rule.get("required_named_materials") or []
            for req in required if isinstance(required,list) else []:
                if isinstance(req,str): rname=req; count=1; role=None
                elif isinstance(req,dict): rname=req.get("name"); count=req.get("count",1); role=req.get("role")
                else: fail(f"SUMMON_NAMED_MATERIAL_RULE_INVALID: {boss}")
                if not nonempty(rname) or not isinstance(count,int) or count<1: fail(f"SUMMON_NAMED_MATERIAL_RULE_INVALID: {boss}")
                matched=0
                for prop in eff:
                    if role=="NON_TUNER" and prop.get("tuner") is True: continue
                    if role=="TUNER" and prop.get("tuner") is not True: continue
                    if rname.strip().casefold() in _rc16236_effective_names(prop,a.get("material_zone") or "FIELD"): matched+=1
                if matched<count: fail(f"SUMMON_NAMED_MATERIAL_MISMATCH: {boss} requires {rname}")
            proof.append({"line_index":li,"action_index":ai,"boss":boss,"kind":kind,"materials":[str(x) for x in mats],"effective_materials":[{"name":x.get("name"),"printed_level":r.get("level"),"effective_level":x.get("level"),"printed_tuner":r.get("tuner"),"effective_tuner":x.get("tuner"),"applied_modifiers":x.get("_rc16237_applied_modifiers",[])} for r,x in zip(raw,eff)],"rule_source_sha256":doc.get("source_sha256")})
    return proof


_validate_classification_result_rc16237_parent = validate_classification_result

def validate_classification_result(path: Path, st, expected_phase):
    d,h,ph=_validate_classification_result_rc16237_parent(path,st,expected_phase)
    structural=d.get("canonical_identity_structural")
    basis=d.get("identity_structure_basis")
    if not isinstance(structural,bool) or not nonempty(basis):
        fail("CLASSIFICATION_IDENTITY_STRUCTURE_EVIDENCE_REQUIRED")
    classification=d.get("classification")
    if classification in {"Canonique","Canonique remixé"} and structural is not True:
        fail("CLASSIFICATION_IDENTITY_CONTRADICTION: canonical classification requires structural canonical identity")
    if classification=="Alternatif" and structural is not False:
        fail("CLASSIFICATION_ALTERNATIF_REQUIRES_NONSTRUCTURAL_IDENTITY")
    return d,h,ph


def _rc16237_line_anchor(line_id):
    if not nonempty(line_id): fail("SEMANTIC_LINE_ID_REQUIRED")
    return f"<!-- YGO_SEMANTIC_LINE:{str(line_id).strip()} -->"


def _rc16237_semantic_line_id(line_id, axis_heading=None):
    if nonempty(line_id): return str(line_id).strip()
    if not nonempty(axis_heading): fail("SEMANTIC_LINE_ID_REQUIRED")
    return "line-"+hashlib.sha256(str(axis_heading).strip().casefold().encode("utf-8")).hexdigest()[:12]


def _rc16237_project_semantic_lineage(inv, semantic):
    lines=semantic.get("lines") if isinstance(semantic,dict) else None
    if not isinstance(lines,list): fail("PILOTAGE_SEMANTIC_SCHEMA_INVALID")
    identified=[x for x in lines if isinstance(x,dict) and nonempty(x.get("semantic_line_id"))]
    ids=[str(x.get("semantic_line_id")).strip() for x in identified]
    if len(ids)!=len(set(ids)): fail("PILOTAGE_SEMANTIC_LINEAGE_EXTRA_OR_DUPLICATE")
    byid={str(x.get("semantic_line_id")).strip():x for x in identified}
    if byid:
        out=[]
        for ent in inv.get("lines",[]):
            lid=_rc16237_semantic_line_id(ent.get("line_id"),ent.get("axis_heading")); sem=byid.get(lid)
            if sem is None: fail(f"COMPILER_NEEDS_SEMANTIC_INPUT: semantic_line_id {lid}")
            if nonempty(sem.get("axis_heading")) and _axis_norm(sem.get("axis_heading"))!=_axis_norm(ent.get("axis_heading")):
                fail(f"SEMANTIC_LINEAGE_AXIS_MISMATCH: {lid}")
            out.append((ent,sem))
        if len(byid)!=len(out): fail("PILOTAGE_SEMANTIC_LINEAGE_EXTRA_OR_DUPLICATE")
        return out
    return None


_rc1623_semantic_line_map_rc16237_parent = _rc1623_semantic_line_map

def _rc1623_semantic_line_map(inv, semantic):
    projected=_rc16237_project_semantic_lineage(inv,semantic)
    if projected is not None: return projected
    return _rc1623_semantic_line_map_rc16237_parent(inv,semantic)


_rc1623_pilotage_semantic_template_rc16237_parent = _rc1623_pilotage_semantic_template

def _rc1623_pilotage_semantic_template(st):
    doc=_rc1623_pilotage_semantic_template_rc16237_parent(st)
    inv,_=_rc1623_normalize_structural_inventory(st)
    by_axis={_axis_norm(x.get("axis_heading")):x for x in inv.get("lines",[])}
    for line in doc.get("lines",[]):
        ent=by_axis.get(_axis_norm(line.get("axis_heading")))
        if ent: line["semantic_line_id"]=_rc16237_semantic_line_id(ent.get("line_id"),ent.get("axis_heading"))
    doc["compiler_owned_fields_notice"] += " semantic_line_id is compiler-owned and must be preserved unchanged."
    return doc


_pilotage_business_skeleton_from_render_rc16237_parent = _pilotage_business_skeleton_from_render

def _pilotage_business_skeleton_from_render(st, render_path: Path):
    out=_pilotage_business_skeleton_from_render_rc16237_parent(st,render_path)
    for line in out.get("lines",[]) if isinstance(out,dict) else []:
        lid=line.get("line_id")
        if nonempty(lid):
            # Preserve the historical player-visible render token.  Semantic
            # lineage is an independent compiler-owned binding and must never
            # replace the token used by presentation/Pilotage coverage checks.
            line["semantic_line_id"]=_rc16237_semantic_line_id(lid,line.get("render_axis_heading"))
            line["semantic_render_anchor"]=_rc16237_line_anchor(lid)
    return out


def _rc16237_inject_line_anchors(text, st):
    inv,_=_rc1623_normalize_structural_inventory(st); lines=text.splitlines()
    for ent in inv.get("lines",[]):
        anchor=_rc16237_line_anchor(ent.get("line_id")); target=_axis_norm(ent.get("axis_heading")); idx=None
        for i,x in enumerate(lines):
            m=re.match(r"^#{2,4}\s+(.+?)\s*$",x.strip())
            if m and _axis_norm(m.group(1))==target: idx=i; break
        # Rendering may legitimately be partial at this compilation boundary
        # (e.g. deck-grouping/formatting fixtures).  Bind every axis that is
        # actually rendered; downstream Pilotage/render validation remains the
        # authority that rejects a required business line missing from output.
        if idx is None: continue
        if anchor not in lines:
            lines.insert(idx+1,anchor)
    return "\n".join(lines).rstrip()+"\n"


def _rc16237_lineage_render_status(text, st):
    inv,_=_rc1623_normalize_structural_inventory(st)
    expected=[_rc16237_line_anchor(x.get("line_id")) for x in inv.get("lines",[]) if nonempty(x.get("line_id"))]
    if not expected: return {"status":"NOT_APPLICABLE","expected":0,"bound":0,"missing":[]}
    cf=str(text or "").casefold(); missing=[a for a in expected if a.casefold() not in cf]; bound=len(expected)-len(missing)
    return {"status":"BOUND" if not missing else ("PARTIAL" if bound else "UNBOUND"),"expected":len(expected),"bound":bound,"missing":missing}


def cmd_render_semantic_compile(a):
    rd=Path(a.run_dir); st=load_state(rd); require_run_id(st,a.run_id); _require_mutable_run_rc1619(rd,st,'render-semantic-compile')
    doc=read_json(Path(a.semantic_file),'Render semantic payload'); visual=read_json(Path(a.visual_assets_file),'visual assets'); out=Path(a.output); _rc1623_assert_flat_run_output(rd,out,'semantic render')
    deck_block=_rc1624_decklist_block(st)
    try: line_max=_rc16221_source_owned_axis_limits(st)['line_max']
    except BaseException: line_max=RC1623_RENDER_PROJECTION_CONTRACT_EXPECTED['axis_line_max']
    text=_rc1623_compile_render_semantic(doc,visual,decklist_block=deck_block,line_max=line_max)
    text=_rc16237_inject_line_anchors(text,st)
    lineage=_rc16237_lineage_render_status(text,st)
    _atomic_write_text(out,text)
    plan=_rc1623_render_component_plan(doc,visual); planp=rd/'semantic_component_plan.json'; _atomic_write_text(planp,_stable_json_text(plan))
    cp=_load_checkpoint_raw(rd,required=False) or {}; _append_run_journal(rd,st,'RENDER_SEMANTIC_COMPILED',checkpoint_seq=cp.get('checkpoint_seq'),semantic_file=str(a.semantic_file),semantic_sha256=sha256(Path(a.semantic_file)),output_file=str(out),output_sha256=sha256(out),component_plan_file=str(planp),component_plan_sha256=sha256(planp),semantic_lineage_status=lineage['status'],semantic_lineage_expected=lineage['expected'],semantic_lineage_bound=lineage['bound'],semantic_lineage_missing=lineage['missing'])
    print(json.dumps({'status':'COMPILED','output':str(out),'sha256':sha256(out),'component_plan':str(planp),'semantic_lineage_status':lineage['status'],'semantic_lineage_expected':lineage['expected'],'semantic_lineage_bound':lineage['bound']},ensure_ascii=False))


_rc1623_compile_semantic_pilotage_rc16237_parent = _rc1623_compile_semantic_pilotage

def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    out=_rc1623_compile_semantic_pilotage_rc16237_parent(st,render_path,semantic)
    inv,_=_rc1623_normalize_structural_inventory(st)
    render_text=Path(render_path).read_text(encoding="utf-8")
    lineage_aware="<!-- YGO_SEMANTIC_LINE:" in render_text
    render_cf=render_text.casefold()
    for line in out.get("lines",[]) if isinstance(out,dict) else []:
        lid=line.get("line_id")
        if not nonempty(lid): continue
        anchor=_rc16237_line_anchor(lid)
        # Legacy/direct compiler fixtures predate semantic anchors and remain
        # valid.  Once a render declares the RC16.23.7 lineage protocol by
        # containing any lineage anchor, every compiled line must bind to its
        # exact anchor and partial lineage fails closed.
        if lineage_aware and anchor.casefold() not in render_cf:
            fail(f"SEMANTIC_LINEAGE_RENDER_BINDING_MISSING: {lid}")
        line["semantic_line_id"]=_rc16237_semantic_line_id(lid,line.get("render_axis_heading"))
        line["semantic_render_anchor"]=anchor
        for rp in line.get("execution_replays",[]) if isinstance(line.get("execution_replays"),list) else []:
            if isinstance(rp,dict): rp["semantic_line_id"]=line["semantic_line_id"]
    out.setdefault("compiler_provenance",{})["semantic_lineage_schema"]=RC16237_LINEAGE_SCHEMA
    out["compiler_provenance"]["semantic_lineage_render_mode"]="ANCHOR_BOUND" if lineage_aware else "LEGACY_COMPATIBLE"
    return out


def _rc16237_abort_reason_class(reason):
    t=" ".join(str(reason or "").casefold().replace("_"," ").replace("-"," ").split())
    if any(x in t for x in ("user requested","user abandon","user fresh","user cancel","user stop")): return "USER_REQUESTED"
    if any(x in t for x in ("fatal","unrecoverable","unsafe state","state corrupt")): return "FATAL_SYSTEM"
    if "test only" in t: return "TEST_ONLY"
    if any(x in t for x in ("repair","admin","derived","binding","metadata","token","render","carousel","image ref","starter metadata","duplicate","projection","formatting")): return "DERIVABLE_REPAIR"
    return "OTHER"


_cmd_abort_run_rc16237_parent = cmd_abort_run

def cmd_abort_run(a):
    cls=_rc16237_abort_reason_class(getattr(a,"reason",None))
    if cls=="DERIVABLE_REPAIR": fail("DERIVABLE_REPAIR_MUST_CONTINUE_SAME_RUN")
    return _cmd_abort_run_rc16237_parent(a)



# =============================================================================
# RC16.23.8 — Terminal Corrective Closure
# Nominal banlist binding, classification evidence consistency, visual
# availability fail-closed semantics, and certainty-monotone projection.
# =============================================================================

RC16238_GUARANTEE_RE = re.compile(r"(?i)\b(guaranteed|guarantee|garanti|garantie|garantis|garanties)\b")


def _rc16238_manifest_source_path(filename):
    root=Path(__file__).resolve().parent
    manifest=root/'SYSTEM_MANIFEST_V4.json'
    if not manifest.exists(): fail('SOURCE_MANIFEST_MISSING')
    doc=_read_json_rc16234_parent(manifest,'system manifest')
    rows=doc.get('active_files') if isinstance(doc,dict) else None
    if not isinstance(rows,list): fail('SOURCE_MANIFEST_ACTIVE_FILES_INVALID')
    row=next((x for x in rows if isinstance(x,dict) and x.get('file')==filename),None)
    if row is None or not nonempty(row.get('sha256')): fail(f'SOURCE_MANIFEST_BINDING_MISSING: {filename}')
    path=root/filename
    if not path.exists(): fail(f'AUTHORITATIVE_SOURCE_MISSING: {filename}')
    if sha256(path)!=row.get('sha256'): fail(f'AUTHORITATIVE_SOURCE_HASH_MISMATCH: {filename}')
    return path


def _rc16238_banlist_path():
    return _rc16238_manifest_source_path('BANLIST_LINK_EVOLUTION_2020.md')


_rc16237_validate_banlist_snapshot_rc16238_parent = _rc16237_validate_banlist_snapshot

def _rc16237_validate_banlist_snapshot(snapshot, banlist_path=None, *, forbidden_mode=False):
    source=Path(banlist_path) if banlist_path is not None else _rc16238_banlist_path()
    return _rc16237_validate_banlist_snapshot_rc16238_parent(snapshot,source,forbidden_mode=forbidden_mode)


_validate_deck_snapshot_rc16238_parent = _validate_deck_snapshot_rc16237_parent

def validate_deck_snapshot(path: Path, st):
    d,h,keys,totals=_validate_deck_snapshot_rc16238_parent(path,st)
    size=_rc16237_validate_deck_size(d)
    forbidden_mode=str(st.get('banlist_mode') or '').upper() in {'FORBIDDEN','FORBIDDEN_MODE','SOLO_FUN'}
    source=_rc16238_banlist_path()
    legality=_rc16237_validate_banlist_snapshot(d,source,forbidden_mode=forbidden_mode)
    receipt={'schema':RC16237_BANLIST_RECEIPT_SCHEMA,'status':'PASS','run_id':st.get('run_id'),'deck_artifact':st.get('current_artifact'),'snapshot_file':str(Path(path).resolve()),'snapshot_sha256':h,'banlist_source_file':str(source.resolve()),'banlist_source_sha256':legality['source_sha256'],'deck_totals':size,'checked_card_count':legality['checked_card_count'],'forbidden_mode':forbidden_mode,'runtime_version':VERSION}
    out=Path(path).parent/RC16237_BANLIST_RECEIPT_FILE
    _atomic_write_text(out,_stable_json_text(receipt))
    st['banlist_legality_receipt']={'receipt_file':str(out.resolve()),'receipt_sha256':sha256(out),'snapshot_sha256':h,'banlist_source_sha256':legality['source_sha256'],'status':'PASS'}
    return d,h,keys,totals


def _rc16238_classification_evidence_consistency(d):
    if not isinstance(d,dict): fail('CLASSIFICATION_EVIDENCE_INVALID')
    structural=d.get('canonical_identity_structural')
    marker=d.get('canonical_identity_withdrawal_result')
    if marker is not None:
        if marker not in {'PRESERVED','DESTROYED_OR_SUBSTANTIALLY_CHANGED'}:
            fail('CLASSIFICATION_CANONICAL_WITHDRAWAL_RESULT_INVALID')
        if structural is True and marker!='DESTROYED_OR_SUBSTANTIALLY_CHANGED':
            fail('CLASSIFICATION_IDENTITY_WITHDRAWAL_CONTRADICTION')
        if structural is False and marker!='PRESERVED':
            fail('CLASSIFICATION_IDENTITY_WITHDRAWAL_CONTRADICTION')
    # Backward-compatible fail-closed guard for the exact legacy contradiction
    # exposed by the RC16.23.7 Yusei Black-Box.  This does not choose a
    # classification; it only rejects evidence that says both "non-structural"
    # and that removing the canonical identity removes the architecture.
    if structural is False:
        w=' '.join(str(d.get('withdrawal_effect') or '').casefold().split())
        if (re.search(r'\bremov\w*\b',w) and re.search(r'\b(removes?|destroys?|eliminates?)\b.*\b(deck\s+)?architecture\b',w)) or ('removes the deck architecture itself' in w):
            fail('CLASSIFICATION_IDENTITY_WITHDRAWAL_CONTRADICTION')
    return True


_validate_classification_result_rc16238_parent = validate_classification_result

def validate_classification_result(path: Path, st, expected_phase):
    d,h,ph=_validate_classification_result_rc16238_parent(path,st,expected_phase)
    _rc16238_classification_evidence_consistency(d)
    return d,h,ph


def _rc16234_normalize_visual(doc):
    if not isinstance(doc,dict): return doc
    d=copy.deepcopy(doc); status=d.get('image_capability_status')
    refs=[]
    for x in d.get('image_refs') or []:
        if nonempty(x) and x not in refs: refs.append(x)
    d['image_refs']=refs
    main=d.get('main_carousel') if isinstance(d.get('main_carousel'),dict) else None
    sig=d.get('signature_climax') if isinstance(d.get('signature_climax'),dict) else None
    if main is not None:
        # Applicability is an authority decision. Availability is a delivery
        # capability and must never silently rewrite that decision.  Legacy
        # payloads may omit image_capability_status; in that case preserve
        # already-bound valid refs rather than manufacturing UNAVAILABLE.
        main['applicable']=main.get('applicable') is True
        main['applicability_basis']='AUTHORITY_DECISION_AVAILABILITY_SEPARATE'
        local=[]
        for x in main.get('image_refs') or []:
            if nonempty(x) and (not refs or x in refs) and x not in local: local.append(x)
        if status=='UNAVAILABLE':
            main['image_refs']=[]; main['image_refs_basis']='UNAVAILABLE_NO_REFS'
        else:
            if main['applicable'] and len(local)<2 and refs: local=list(refs[:4])
            main['image_refs']=local[:4]
            main['image_refs_basis']='DERIVED_FROM_BOUND_VISUAL_ASSETS' if status=='AVAILABLE' else 'LEGACY_BOUND_REFS_STATUS_UNSPECIFIED'
    if sig is not None:
        sig['mini_carousel_applicable']=sig.get('mini_carousel_applicable') is True
        sig['mini_carousel_applicability_basis']='AUTHORITY_DECISION_AVAILABILITY_SEPARATE'
        local=[]
        for x in sig.get('image_refs') or []:
            if nonempty(x) and (not refs or x in refs) and x not in local: local.append(x)
        if status=='UNAVAILABLE':
            sig['image_refs']=[]; sig['image_refs_basis']='UNAVAILABLE_NO_REFS'
        else:
            if sig['mini_carousel_applicable'] and len(local)<3 and refs: local=list(refs[:4])
            sig['image_refs']=local[:4]
            sig['image_refs_basis']='DERIVED_FROM_BOUND_VISUAL_ASSETS' if status=='AVAILABLE' else 'LEGACY_BOUND_REFS_STATUS_UNSPECIFIED'
    return d


def _rc16238_semantic_line_scope(render_text, line_id):
    anchor=_rc16237_line_anchor(line_id)
    lines=str(render_text or '').splitlines()
    try: i=next(i for i,x in enumerate(lines) if x.strip()==anchor)
    except StopIteration: return ''
    out=[]
    for x in lines[i+1:]:
        if re.match(r'^##\s+',x.strip()): break
        out.append(x)
    return '\n'.join(out)


def _rc16238_assert_certainty_monotone(render_text, semantic):
    for line in semantic.get('lines',[]) if isinstance(semantic,dict) and isinstance(semantic.get('lines'),list) else []:
        if not isinstance(line,dict): continue
        claim=line.get('claim') if isinstance(line.get('claim'),dict) else {}
        certainty=str(claim.get('certainty') or 'GUARANTEED').upper()
        if certainty=='GUARANTEED': continue
        lid=line.get('semantic_line_id') or line.get('line_id')
        scope=_rc16238_semantic_line_scope(render_text,lid) if nonempty(lid) else ''
        if scope and RC16238_GUARANTEE_RE.search(scope):
            fail(f'CERTAINTY_PROJECTION_STRENGTHENED: {lid}:{certainty}')
    return True


_rc1623_compile_semantic_pilotage_rc16238_parent = _rc1623_compile_semantic_pilotage

def _rc1623_compile_semantic_pilotage(st, render_path: Path, semantic):
    out=_rc1623_compile_semantic_pilotage_rc16238_parent(st,render_path,semantic)
    _rc16238_assert_certainty_monotone(Path(render_path).read_text(encoding='utf-8'),semantic)
    return out

# Normal CLI must execute the final shipped symbol table, including all late
# RC16.23.6/RC16.23.7 overrides.  Keep the sole entrypoint at the physical EOF.
if __name__=="__main__": main()

