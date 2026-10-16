# P7-003: ASR Inference Image and ECR

| Field | Value |
|-------|-------|
| **ID** | P7-003 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-003-asr-image-ecr` |

## Spec References

- [Model Serving](../architecture/model-serving.md)
- [dev-step-p6-001](dev-step-p6-001-ecr-image-push.md)
- [AWS Deployment](../operations/aws-deployment.md) — Container Images

## Scope

One verifiable behavior: **`voragon/asr-inference` image builds and pushes to ECR; image runs faster-whisper (or documented GPU backend) with `/health`.**

- Dockerfile under `docker/` (CUDA runtime base per aws-deployment.md)
- ECR repo Terraform (extend [infra/ecr](../../infra/ecr/) or documented second repo)
- Minimal HTTP health server or reuse pattern from backend ASR warmup

## Out of Scope

- Full transcribe HTTP API (P7-004 if split) — define in same step if one service image
- EKS Deployment (P7-004)

## Acceptance Criteria

- [ ] `docker build` succeeds locally or in CI doc
- [ ] Push to ECR documented; `aws ecr describe-images` shows tag (operator)
- [ ] Container `/health` responds when model loaded (operator smoke)

## Manual Test

1. Build and push per README
2. Optional: `docker run --gpus all` smoke on GPU host

## Automated Tests

```bash
cd backend && pytest -q
# Add image build smoke test if step touches backend packaging
```

## Spec Changes

Expected: [infra/ecr/README.md](../../infra/ecr/README.md), [aws-deployment.md](../operations/aws-deployment.md).

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
