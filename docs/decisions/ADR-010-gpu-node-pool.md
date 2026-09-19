# ADR-010: Dedicated GPU Node Pool

## Status

Accepted

## Context

Voragon's ASR inference requires GPU acceleration for realtime performance. In a Kubernetes deployment, GPU workloads must be scheduled on nodes with GPU hardware, isolated from CPU-only services.

## Problem

How should GPU inference workloads be scheduled and isolated in the Kubernetes cluster?

## Decision

Use a **dedicated GPU node pool** in EKS with node selectors, taints, and tolerations to ensure GPU workloads run only on GPU-equipped nodes and CPU workloads do not compete for GPU resources.

## Alternatives Considered

### Shared Node Pool (GPU + CPU Workloads)

| Pros | Cons |
|------|------|
| Simpler cluster management | CPU workloads compete for GPU node resources |
| Fewer node types to manage | GPU nodes are expensive; wasteful for CPU-only pods |
| | Noisy neighbor problems (inference latency affected by CPU workloads) |

### GPU Time-Slicing (Single GPU, Multiple Pods)

| Pros | Cons |
|------|------|
| Higher GPU utilization | Inference latency becomes unpredictable |
| Lower cost per concurrent session | Not suitable for realtime latency requirements |
| | Complex scheduling configuration |

### Dedicated GPU Node Pool

| Pros | Cons |
|------|------|
| Clean resource isolation | Higher cost (GPU nodes idle when no inference load) |
| Predictable inference latency | Two node types to manage |
| Independent scaling (CPU and GPU) | |
| Standard Kubernetes pattern | |
| NVIDIA device plugin well-supported | |

### Serverless GPU (No Node Pool)

| Pros | Cons |
|------|------|
| No node management | Limited availability and instance types |
| Auto-scaling | Cold start latency unacceptable for realtime |
| | Not mature enough for production realtime inference |

## Trade-offs

- **Cost**: GPU nodes (g5.xlarge) are significantly more expensive than CPU nodes. HPA must scale GPU nodes based on demand to avoid idle cost.
- **Scaling latency**: Adding a GPU node takes 2–5 minutes (EC2 launch + model load). Pre-warming or maintaining a minimum GPU node count is recommended.
- **Single GPU per pod**: Initially, one inference pod per GPU. GPU sharing (MIG, time-slicing) is deferred until concurrency requirements justify the complexity.

## Consequences

- EKS cluster has two node groups: CPU (m6i) and GPU (g5)
- GPU nodes have taint `nvidia.com/gpu=true:NoSchedule`
- ASR pods have toleration and node selector for GPU nodes
- GPU resource request: `nvidia.com/gpu: 1` per ASR pod
- HPA scales ASR pods based on GPU utilization or inference queue depth
- CPU services (realtime-service, ai-gateway) never scheduled on GPU nodes

## Future Reconsideration

Reconsider if:
- GPU utilization is consistently low (< 20%) and cost optimization is needed
- Multi-model inference (ASR + LLM) on the same GPU justifies GPU sharing
- G6e (L40S) instances provide better price/performance at scale
