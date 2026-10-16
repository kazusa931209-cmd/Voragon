# P7-005: Model Weights on GPU Pods

| Field | Value |
|-------|-------|
| **ID** | P7-005 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-005-model-weights-gpu` |

## Spec References

- [Model Serving](../architecture/model-serving.md)
- [dev-step-p6-003](dev-step-p6-003-eks-realtime-manifests.md) — model cache PVC pattern
- [dev-step-p7-004](dev-step-p7-004-asr-service-deploy.md)

## Scope

One verifiable behavior: **ASR model weights persist across asr-service pod restarts without re-downloading on every schedule event.**

- PVC or documented init-container download to shared volume (reuse `gp2` / model-cache pattern where applicable)
- Config for model id/path documented for operators

## Out of Scope

- Multi-model registry (Phase 8)
- Changing Whisper model family (unless required for GPU path)

## Acceptance Criteria

- [ ] First pod start downloads or mounts weights; readiness becomes true
- [ ] Delete pod → replacement Ready faster (cached weights) (operator)
- [ ] Document disk size and cache path in k8s README

## Manual Test

1. Deploy asr-service with empty PVC → wait Ready
2. `kubectl delete pod` for asr-service → new pod Ready with shorter startup
3. Verify PVC bound and used

## Automated Tests

```bash
cd backend && pytest -q
```

## Spec Changes

Expected: [k8s/eks/README.md](../../k8s/eks/README.md), [aws-deployment.md](../operations/aws-deployment.md) Configuration Management.

---

## Completion

### Summary

- …

### Spec Changes

- …

### Automated Tests Run

```bash
# paste command and result
```

### Manual Test Result

- [ ] Pass — date, notes

### Commit

- **Hash:** —

### PR

- **URL:** —
