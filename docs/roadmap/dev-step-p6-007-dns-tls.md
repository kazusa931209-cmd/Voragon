# P6-007: DNS and TLS (Route 53 + ACM)

| Field | Value |
|-------|-------|
| **ID** | P6-007 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-007-dns-tls` |

## Spec References

- [AWS Deployment](../operations/aws-deployment.md) — DNS and TLS
- [architecture/overview.md](../architecture/overview.md) — `wss://api.voragon.example`
- [dev-step-p6-004](dev-step-p6-004-alb-ingress-websocket.md), [dev-step-p6-005](dev-step-p6-005-api-gateway-auth.md)

## Scope

One verifiable behavior: **the production WebSocket URL uses a stable hostname with valid TLS (ACM); DNS points to API Gateway or ALB as documented.**

- ACM certificate for staging/production hostname (exact domain documented — placeholder `api.voragon.example` OK if noted)
- Route 53 (or documented external DNS) alias to API Gateway / ALB
- Final client URL: `wss://<host>/v1/realtime` matches desktop settings docs

## Out of Scope

- Multi-region DNS
- mTLS
- CDN in front of WebSocket

## Acceptance Criteria

- [ ] Browser/curl trusts HTTPS endpoint (no cert warnings for intended hostname)
- [ ] DNS resolution documented and verified (`dig` / `nslookup`)
- [ ] API Gateway / ALB uses ACM cert on listener

## Manual Test

1. Open `https://<host>/health` — valid cert chain
2. Desktop connects via `wss://<host>/v1/realtime` (with auth from P6-005)
3. Document rollback if cert renewal fails

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [aws-deployment.md](../operations/aws-deployment.md) — DNS/TLS tables updated with real hostnames.

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
