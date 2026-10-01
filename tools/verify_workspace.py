from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ident=json.loads((ROOT/'control/PARENT_IDENTITY.json').read_text())
base=ROOT/'baseline_v5/source'; work=ROOT/'worktree/source'
errors=[]
target=(ROOT/'control/TARGET_VERSION.txt').read_text().strip()
go=(ROOT/'control/GO_AUTHORIZATION.txt').read_text().strip()
gate=(ROOT/'control/CURRENT_GATE.txt').read_text().strip()
changed=[]; added=[]; deleted=[]
bnames={p.name for p in base.iterdir() if p.is_file()}; wnames={p.name for p in work.iterdir() if p.is_file()}
for n in sorted(bnames & wnames):
    if sha(base/n)!=sha(work/n): changed.append(n)
added=sorted(wnames-bnames); deleted=sorted(bnames-wnames)
for n in sorted(bnames-wnames): errors.append('worktree_missing:'+n)
if gate=='PRE_GO' and (changed or added or deleted): errors.append('product_diff_before_go')
print('parent_sha256='+ident['parent_sha256'])
print('target_version='+target)
print('go_authorization='+go)
print('current_gate='+gate)
print('worktree_changed='+json.dumps(changed))
print('worktree_added='+json.dumps(added))
print('worktree_deleted='+json.dumps(deleted))
if '--require-go' in sys.argv:
    if target=='NOT_ASSIGNED' or not target: errors.append('target_not_assigned')
    if go!='YES': errors.append('go_not_yes')
if errors:
    for e in errors: print('ERROR:'+e)
    raise SystemExit(1)
print('workspace_status=PASS')
