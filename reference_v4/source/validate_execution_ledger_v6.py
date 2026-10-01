#!/usr/bin/env python3
"""Validator for the project execution ledger, v6.
Checks structural invariants only; never judges deck viability or whether a
terminal-compression business decision is substantively correct.

V6.1 keeps V6 business-neutral checks and adds RC15 explicit STALE-event
materialization for PASS_REFACTOR. It still never judges whether the refactor,
compression decision or dependency set is substantively correct.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import os
import time
import fcntl

VERSION = "v6.1"
REQ = {
    "authority", "input_artifact", "output_artifact", "status",
    "material_change", "current_artifact", "artifact_snapshot_file",
    "artifact_snapshot_sha256", "execution_trace"
}
REF_REQ = {"before_artifact", "after_artifact", "defect_targeted", "delta", "retest_artifact"}
PASS_STATUSES = {"PASS_DIRECT", "PASS_REFACTOR"}
PROOF_REQ = {
    "relation_final", "test_applied", "refactor_materialized",
    "compression_terminal", "rerouting_after_refactor", "exact_version"
}


def fail(msg):
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def nonempty_str(v):
    return isinstance(v, str) and bool(v.strip())


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()




def _atomic_write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.time_ns()}")
    try:
        with tmp.open("w", encoding="utf-8", newline="\n") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try: tmp.unlink()
            except OSError: pass


class _FileLock:
    def __init__(self,path: Path): self.path=path
    def __enter__(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.f=self.path.open("a+")
        fcntl.flock(self.f.fileno(),fcntl.LOCK_EX)
        return self
    def __exit__(self,*_):
        try: fcntl.flock(self.f.fileno(),fcntl.LOCK_UN)
        finally: self.f.close()


def validate_terminal_attempt(d):
    if d.get("status") not in PASS_STATUSES:
        return
    t = d.get("terminal_compression_attempt")
    if not isinstance(t, dict):
        fail("PASS missing terminal_compression_attempt")
    if t.get("artifact") != d.get("output_artifact"):
        fail("terminal_compression_attempt.artifact must equal output_artifact")
    candidates = t.get("candidate_changes")
    if not isinstance(candidates, list) or len(candidates) < 2 or not all(nonempty_str(x) for x in candidates):
        fail("terminal_compression_attempt.candidate_changes must contain at least two concrete entries")
    if len(set(c.strip() for c in candidates)) != len(candidates):
        fail("terminal_compression_attempt.candidate_changes must be distinct")
    losses = t.get("protected_function_losses")
    if not isinstance(losses, list) or not losses or not all(nonempty_str(x) for x in losses):
        fail("terminal_compression_attempt.protected_function_losses must be a non-empty list")
    if t.get("outcome") != "FERMÉE":
        fail("PASS requires terminal_compression_attempt.outcome == FERMÉE")


def validate_terminal_replay(d):
    if d.get("status") not in PASS_STATUSES:
        return
    r = d.get("terminal_compression_replay")
    if not isinstance(r, dict):
        fail("PASS missing terminal_compression_replay")
    if r.get("artifact") != d.get("output_artifact"):
        fail("terminal_compression_replay.artifact must equal output_artifact")
    if r.get("artifact_snapshot_sha256") != d.get("artifact_snapshot_sha256"):
        fail("terminal_compression_replay snapshot SHA256 must equal ledger snapshot SHA256")
    if r.get("ignored_prior_outcome") is not True:
        fail("terminal_compression_replay.ignored_prior_outcome must be true")
    if r.get("ignored_prior_candidates") is not True:
        fail("terminal_compression_replay.ignored_prior_candidates must be true")
    candidates = r.get("candidate_changes")
    if not isinstance(candidates, list) or len(candidates) < 2 or not all(nonempty_str(x) for x in candidates):
        fail("terminal_compression_replay.candidate_changes must contain at least two concrete entries")
    if len(set(c.strip() for c in candidates)) != len(candidates):
        fail("terminal_compression_replay.candidate_changes must be distinct")
    prior = d.get("terminal_compression_attempt", {}).get("candidate_changes", [])
    prior_norm = {c.strip() for c in prior if isinstance(c, str)}
    replay_norm = {c.strip() for c in candidates}
    if prior_norm & replay_norm:
        fail("terminal_compression_replay candidates must not repeat prior terminal candidates")
    losses = r.get("protected_function_losses")
    if not isinstance(losses, list) or not losses or not all(nonempty_str(x) for x in losses):
        fail("terminal_compression_replay.protected_function_losses must be a non-empty list")
    if r.get("outcome") != "FERMÉE":
        fail("PASS requires terminal_compression_replay.outcome == FERMÉE")


def validate_business_proof_shape(d):
    if d.get("status") not in PASS_STATUSES:
        return
    p = d.get("business_proof")
    if not isinstance(p, dict):
        fail("PASS missing business_proof")
    missing = PROOF_REQ - p.keys()
    if missing:
        fail("business_proof missing fields: " + ", ".join(sorted(missing)))
    if p.get("compression_terminal") != "FERMÉE":
        fail("PASS requires business_proof.compression_terminal == FERMÉE")
    if p.get("exact_version") != d.get("output_artifact"):
        fail("business_proof.exact_version must equal output_artifact")
    if not nonempty_str(p.get("relation_final")) or not nonempty_str(p.get("test_applied")):
        fail("business_proof relation_final and test_applied must be non-empty")
    if d.get("status") == "PASS_REFACTOR" and p.get("refactor_materialized") != "OUI":
        fail("PASS_REFACTOR requires business_proof.refactor_materialized == OUI")
    if d.get("status") == "PASS_DIRECT" and p.get("refactor_materialized") != "NON REQUIS":
        fail("PASS_DIRECT requires business_proof.refactor_materialized == NON REQUIS")
    if p.get("rerouting_after_refactor") not in {"EFFECTUÉ", "NON NÉCESSAIRE"}:
        fail("PASS requires valid rerouting_after_refactor")


def validate_snapshot(snapshot_path: Path, raw: bytes, d: dict):
    if snapshot_path.name != d.get("artifact_snapshot_file"):
        fail("artifact snapshot filename must equal ledger artifact_snapshot_file")
    actual = sha256(raw)
    if actual != d.get("artifact_snapshot_sha256"):
        fail("artifact snapshot SHA256 does not match ledger")
    try:
        snap = json.loads(raw.decode("utf-8"))
    except Exception as e:
        fail(f"invalid artifact snapshot JSON: {e}")
    if snap.get("artifact_id") != d.get("output_artifact"):
        fail("snapshot artifact_id must equal output_artifact")
    for zone in ("main_deck", "extra_deck", "side_deck"):
        cards = snap.get(zone)
        if not isinstance(cards, list):
            fail(f"snapshot {zone} must be a list")
        seen = set()
        for i, card in enumerate(cards):
            if not isinstance(card, dict):
                fail(f"snapshot {zone}[{i}] must be an object")
            name = card.get("name")
            qty = card.get("qty")
            if not nonempty_str(name):
                fail(f"snapshot {zone}[{i}].name must be non-empty")
            if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
                fail(f"snapshot {zone}[{i}].qty must be a positive integer")
            key = name.strip().casefold()
            if key in seen:
                fail(f"snapshot {zone} contains duplicate card entry: {name}")
            seen.add(key)
    totals = {
        "main_total": sum(c["qty"] for c in snap["main_deck"]),
        "extra_total": sum(c["qty"] for c in snap["extra_deck"]),
        "side_total": sum(c["qty"] for c in snap["side_deck"]),
    }
    for k, v in totals.items():
        if k in snap and snap[k] != v:
            fail(f"snapshot {k} does not match card quantities")
    return snap, actual


def validate_execution_trace(d):
    trace = d.get("execution_trace")
    if not isinstance(trace, list) or not trace:
        fail("missing or empty execution_trace")
    seqs = []
    for i, ev in enumerate(trace):
        if not isinstance(ev, dict):
            fail(f"execution_trace[{i}] must be an object")
        seq = ev.get("seq")
        event = ev.get("event")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq <= 0:
            fail(f"execution_trace[{i}].seq must be a positive integer")
        if not nonempty_str(event):
            fail(f"execution_trace[{i}].event must be non-empty")
        seqs.append(seq)
    if seqs != list(range(1, len(seqs) + 1)):
        fail("execution_trace seq must be unique, contiguous, and start at 1")

    def first_index(name, predicate=lambda e: True):
        for i, ev in enumerate(trace):
            if ev.get("event") == name and predicate(ev):
                return i, ev
        return None, None

    status = d.get("status")
    out = d.get("output_artifact")
    inp = d.get("input_artifact")

    vi, _ = first_index("VIABILITY_TEST_COMPLETED", lambda e: e.get("artifact") == (inp if status == "PASS_REFACTOR" else out))
    ti, tev = first_index("TERMINAL_COMPRESSION_ATTEMPT_COMPLETED", lambda e: e.get("artifact") == out)
    si, sev = first_index("TERMINAL_SNAPSHOT_FROZEN", lambda e: e.get("artifact") == out)
    ci, cev = first_index("TERMINAL_COMPRESSION_REPLAY_COMPLETED", lambda e: e.get("artifact") == out)
    if status in PASS_STATUSES:
        if vi is None:
            fail("execution_trace missing VIABILITY_TEST_COMPLETED on required artifact")
        if ti is None:
            fail("execution_trace missing TERMINAL_COMPRESSION_ATTEMPT_COMPLETED on output_artifact")
        if si is None:
            fail("execution_trace missing TERMINAL_SNAPSHOT_FROZEN on output_artifact")
        if ci is None:
            fail("execution_trace missing TERMINAL_COMPRESSION_REPLAY_COMPLETED on output_artifact")
        if not (vi < ti < si < ci):
            fail("execution_trace order invalid: viability test, terminal attempt, snapshot freeze, then cold replay required")
        if tev.get("result") != "FERMÉE":
            fail("execution_trace terminal compression result must be FERMÉE for PASS")
        if sev.get("snapshot_file") != d.get("artifact_snapshot_file"):
            fail("execution_trace snapshot_file mismatch")
        if sev.get("snapshot_sha256") != d.get("artifact_snapshot_sha256"):
            fail("execution_trace snapshot_sha256 mismatch")
        if cev.get("snapshot_sha256") != d.get("artifact_snapshot_sha256"):
            fail("execution_trace terminal replay snapshot_sha256 mismatch")
        if cev.get("result") != "FERMÉE":
            fail("execution_trace terminal replay result must be FERMÉE for PASS")

    if status == "PASS_REFACTOR":
        ri, rev = first_index(
            "REFACTOR_MATERIALIZED",
            lambda e: e.get("before_artifact") == d.get("before_artifact") and e.get("after_artifact") == d.get("after_artifact"),
        )
        sti, stev = first_index(
            "DEPENDENT_STATUSES_STALE",
            lambda e: e.get("artifact") == d.get("before_artifact") and e.get("caused_by_artifact") == d.get("after_artifact"),
        )
        xi, xev = first_index("RETEST_COMPLETED", lambda e: e.get("artifact") == d.get("after_artifact"))
        if ri is None:
            fail("execution_trace missing REFACTOR_MATERIALIZED for before/after artifacts")
        if sti is None:
            fail("execution_trace missing DEPENDENT_STATUSES_STALE for before/after artifacts")
        stale_ids=stev.get("stale_status_ids")
        if not isinstance(stale_ids,list) or not stale_ids or not all(nonempty_str(x) for x in stale_ids) or len(stale_ids)!=len(set(stale_ids)):
            fail("DEPENDENT_STATUSES_STALE requires distinct non-empty stale_status_ids")
        if xi is None:
            fail("execution_trace missing RETEST_COMPLETED on after_artifact")
        if not (vi < ri < sti < xi < ti < si < ci):
            fail("execution_trace PASS_REFACTOR order invalid: STALE must be materialized before retest")
        if xev.get("result") != "PASS_REFACTOR":
            fail("execution_trace RETEST_COMPLETED result must equal PASS_REFACTOR")


def read_instrument_trace(path: Path):
    if not path.exists():
        return []
    events = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except Exception as e:
            fail(f"invalid instrument trace JSON at line {lineno}: {e}")
        if not isinstance(ev, dict):
            fail(f"instrument trace line {lineno} must be an object")
        events.append(ev)
    for i, ev in enumerate(events, start=1):
        if ev.get("seq") != i:
            fail("instrument trace seq must be unique, contiguous, and start at 1")
    return events


def append_instrument_event(path: Path, event: str, ledger_raw: bytes, snapshot_raw: bytes, d: dict, **extra):
    with _FileLock(path.with_name(path.name+".lock")):
        events = read_instrument_trace(path)
        obj = {
            "seq": len(events) + 1,
            "event": event,
            "validator_version": VERSION,
            "ledger_sha256": sha256(ledger_raw),
            "artifact_snapshot_sha256": sha256(snapshot_raw),
            "output_artifact": d.get("output_artifact"),
            "status": d.get("status"),
        }
        obj.update(extra)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n"); f.flush(); os.fsync(f.fileno())
        return obj


def require_prior_instrument_events(path: Path, ledger_raw: bytes, snapshot_raw: bytes, d: dict):
    events = read_instrument_trace(path)
    expected = {
        "ledger_sha256": sha256(ledger_raw),
        "artifact_snapshot_sha256": sha256(snapshot_raw),
        "output_artifact": d.get("output_artifact"),
        "status": d.get("status"),
    }
    names = []
    for ev in events:
        if all(ev.get(k) == v for k, v in expected.items()):
            names.append(ev.get("event"))
    try:
        a = names.index("VALIDATOR_RUN_PASS")
        b = names.index("RECEIPT_WRITTEN")
    except ValueError:
        fail("instrument trace missing prior VALIDATOR_RUN_PASS and/or RECEIPT_WRITTEN for exact artifacts")
    if not a < b:
        fail("instrument trace order invalid: VALIDATOR_RUN_PASS must precede RECEIPT_WRITTEN")


def validate(d):
    missing = REQ - d.keys()
    if missing:
        fail("missing fields: " + ", ".join(sorted(missing)))
    if d.get("status") in PASS_STATUSES and d.get("current_artifact") != d.get("output_artifact"):
        fail("status is STALE: current_artifact != output_artifact")
    if d.get("status") == "PASS_REFACTOR":
        missing = REF_REQ - d.keys()
        if missing:
            fail("PASS_REFACTOR missing fields: " + ", ".join(sorted(missing)))
        if d["before_artifact"] == d["after_artifact"]:
            fail("before_artifact and after_artifact must differ")
        if d.get("material_change") is not True:
            fail("PASS_REFACTOR requires material_change == true")
        if not isinstance(d["delta"], list) or not d["delta"] or not all(nonempty_str(x) for x in d["delta"]):
            fail("delta must be a non-empty list of concrete entries")
        if d["retest_artifact"] != d["after_artifact"]:
            fail("retest_artifact must equal after_artifact")
        if d["output_artifact"] != d["after_artifact"]:
            fail("output_artifact must equal after_artifact")
    elif d.get("status") == "PASS_DIRECT":
        if d.get("material_change") is not False:
            fail("PASS_DIRECT requires material_change == false")
    validate_terminal_attempt(d)
    validate_terminal_replay(d)
    validate_business_proof_shape(d)
    validate_execution_trace(d)


def write_receipt(ledger_path: Path, ledger_raw: bytes, snapshot_path: Path, snapshot_raw: bytes, d: dict, receipt_path: Path):
    receipt = {
        "validator": Path(__file__).name,
        "validator_version": VERSION,
        "ledger_file": ledger_path.name,
        "ledger_sha256": sha256(ledger_raw),
        "artifact_snapshot_file": snapshot_path.name,
        "artifact_snapshot_sha256": sha256(snapshot_raw),
        "output_artifact": d.get("output_artifact"),
        "status": d.get("status"),
        "result": "PASS",
    }
    _atomic_write_text(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return receipt


def verify_receipt(ledger_path: Path, ledger_raw: bytes, snapshot_path: Path, snapshot_raw: bytes, d: dict, receipt_path: Path):
    if not receipt_path.exists():
        fail("receipt file does not exist")
    try:
        r = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"invalid receipt JSON: {e}")
    checks = {
        "validator_version": VERSION,
        "ledger_file": ledger_path.name,
        "ledger_sha256": sha256(ledger_raw),
        "artifact_snapshot_file": snapshot_path.name,
        "artifact_snapshot_sha256": sha256(snapshot_raw),
        "output_artifact": d.get("output_artifact"),
        "status": d.get("status"),
        "result": "PASS",
    }
    for k, v in checks.items():
        if r.get(k) != v:
            fail(f"receipt mismatch for {k}")
    print("PASS: receipt matches exact ledger and artifact snapshot")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--artifact", required=True, help="serialized terminal deck snapshot JSON")
    ap.add_argument("--receipt", help="receipt path; defaults to <ledger>.receipt.json")
    ap.add_argument("--instrument-trace", help="append-only instrument trace; defaults to <ledger>.instrument.jsonl")
    ap.add_argument("--verify-receipt", action="store_true", help="verify an existing receipt instead of writing one")
    args = ap.parse_args()

    ledger_path = Path(args.ledger)
    snapshot_path = Path(args.artifact)
    ledger_raw = ledger_path.read_bytes()
    snapshot_raw = snapshot_path.read_bytes()
    try:
        d = json.loads(ledger_raw.decode("utf-8"))
    except Exception as e:
        fail(f"invalid ledger JSON: {e}")

    validate(d)
    validate_snapshot(snapshot_path, snapshot_raw, d)

    receipt_path = Path(args.receipt) if args.receipt else ledger_path.with_suffix(ledger_path.suffix + ".receipt.json")
    instrument_trace_path = Path(args.instrument_trace) if args.instrument_trace else ledger_path.with_suffix(ledger_path.suffix + ".instrument.jsonl")
    if args.verify_receipt:
        require_prior_instrument_events(instrument_trace_path, ledger_raw, snapshot_raw, d)
        verify_receipt(ledger_path, ledger_raw, snapshot_path, snapshot_raw, d, receipt_path)
        append_instrument_event(instrument_trace_path, "RECEIPT_VERIFY_PASS", ledger_raw, snapshot_raw, d, receipt_file=receipt_path.name)
        print(f"INSTRUMENT_TRACE: {instrument_trace_path}")
    else:
        append_instrument_event(instrument_trace_path, "VALIDATOR_RUN_PASS", ledger_raw, snapshot_raw, d)
        write_receipt(ledger_path, ledger_raw, snapshot_path, snapshot_raw, d, receipt_path)
        append_instrument_event(instrument_trace_path, "RECEIPT_WRITTEN", ledger_raw, snapshot_raw, d, receipt_file=receipt_path.name)
        print("PASS: ledger structural invariants, execution trace, and artifact binding satisfied")
        print(f"RECEIPT: {receipt_path}")
        print(f"INSTRUMENT_TRACE: {instrument_trace_path}")


if __name__ == "__main__":
    main()
