# ADR-009: Kubernetes / EKS for Production

## Status

Accepted

## Context

Voragon's production deployment requires horizontally scalable services, GPU workload scheduling, health management, rolling deployments, and observability integration. The initial development phase runs on a single machine without orchestration.

## Problem

Select a production deployment platform that supports GPU workloads, horizontal scaling, and operational best practices.

## Decision

Use **Amazon EKS** (Elastic Kubernetes Service) for production deployment. Use **Kind** (Kubernetes in Docker) for local Kubernetes validation. Use **Docker Compose** as the intermediate step between single-process and Kubernetes.

## Alternatives Considered

### Docker Compose Only (No Kubernetes)

| Pros | Cons |
|------|------|
| Simple, well-understood | No horizontal scaling |
| Sufficient for single-machine deployment | No GPU scheduling |
| Low operational overhead | No rolling deployments |
| | Not suitable for production scale |

### AWS ECS / Fargate

| Pros | Cons |
|------|------|
| Simpler than Kubernetes | GPU support is more limited |
| AWS-native, less operational overhead | Less portable (AWS-specific) |
| Good for containerized workloads | Weaker ecosystem for ML/GPU workloads |
| | No standardized GPU device plugin |

### Self-Managed Kubernetes

| Pros | Cons |
|------|------|
| Full control | High operational burden |
| No EKS management fee | Must manage control plane, upgrades, security |
| | Not justified for initial team size |

### Amazon EKS

| Pros | Cons |
|------|------|
| Managed control plane | EKS management fee (~$0.10/hr per cluster) |
| GPU node pool support (G5, G6e) | Kubernetes complexity |
| NVIDIA device plugin ecosystem | Steeper learning curve than ECS |
| HPA, rolling deployments, health probes | |
| Portable workloads (same containers locally and in cloud) | |
| Industry standard for ML inference serving | |
| Kind for local validation | |

## Trade-offs

- **Complexity**: Kubernetes introduces concepts (Deployments, Services, ConfigMaps, HPA, node pools) that Docker Compose does not. Mitigated by phased introduction (Compose first, then Kind, then EKS).
- **Cost**: EKS management fee plus EC2 instances. Justified when horizontal scaling and GPU scheduling are required.
- **Not needed initially**: Kubernetes is introduced in Phase 5 (local) and Phase 6 (AWS). Phases 1–4 do not require it.

## Consequences

- Phase 1–3: Single process, no containers
- Phase 4: Docker Compose for multi-container local development
- Phase 5: Kind cluster for Kubernetes validation
- Phase 6: EKS for production deployment
- Container images built and stored in ECR
- GPU workloads scheduled via NVIDIA device plugin on dedicated node pools
- Observability via Prometheus + Grafana (or Amazon Managed Prometheus)

## Future Reconsideration

Reconsider if:
- Team size remains one engineer and Kubernetes operational burden is too high
- AWS introduces a simpler GPU inference platform that meets scaling requirements
- Serverless GPU (e.g., AWS Lambda with GPU) becomes viable for inference workloads
