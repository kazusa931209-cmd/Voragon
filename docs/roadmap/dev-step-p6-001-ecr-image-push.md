# P6-001: ECR Repository and Image Push

| Field | Value |
|-------|-------|
| **ID** | P6-001 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-001-ecr-image-push` |

## Spec References

- [AWS Deployment](../operations/aws-deployment.md) — Container Images, Phase 6 steps
- [Kubernetes Architecture](../architecture/kubernetes.md) — Production Architecture
- [docker/realtime-backend/Dockerfile](../../docker/realtime-backend/Dockerfile)
- [dev-step-p4-001](dev-step-p4-001-backend-dockerfile.md)

## Scope

One verifiable behavior: **the P4 `realtime-backend` image can be built locally and pushed to a dedicated ECR repository with a documented, repeatable tag flow for EKS pulls.**

- ECR repository for `voragon/realtime-backend` (or documented naming convention)
- Repo-root build + `docker tag` + `aws ecr get-login-password` push commands in ops docs
- Image tag convention for dev/staging (e.g. `git sha` or `v0.x`) documented for P6-003 Deployment

## Out of Scope

- EKS cluster (P6-002)
- CI pipeline for ECR push
- `asr-inference` / `ai-gateway` images (Phase 7–8)

## Acceptance Criteria

- [ ] ECR repository defined (Terraform, eksctl addon doc, or `infra/ecr/` + README — pick one approach in implementation)
- [ ] Documented build and push from repo root using `docker/realtime-backend/Dockerfile`
- [ ] Operator can `docker pull` the pushed tag from ECR (same account/region)
- [ ] [aws-deployment.md](../operations/aws-deployment.md) references ECR setup and links to repo docs

## Manual Test

1. Create or use existing ECR repo per docs
2. `docker build -f docker/realtime-backend/Dockerfile -t <ecr-uri>:test .`
3. Push `test` tag; verify in AWS console or `aws ecr describe-images`
4. Optional: pull on a clean machine with ECR auth

## Automated Tests

```bash
cd backend && pytest -q
```

## Spec Changes

Expected: [aws-deployment.md](../operations/aws-deployment.md) — ECR section status and commands.

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
