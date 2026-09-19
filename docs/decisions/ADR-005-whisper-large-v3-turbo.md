# ADR-005: Whisper Large-v3 Turbo as Initial ASR Model

## Status

Accepted

## Context

Voragon's initial product is realtime English speech-to-text. The ASR model must support realtime partial transcription, run on both local development hardware and cloud GPU instances, and serve as the foundation for a model-agnostic architecture that can be replaced later.

## Problem

Select the initial ASR model for Voragon.

## Decision

Use **OpenAI Whisper Large-v3 Turbo** (`large-v3-turbo`) as the initial ASR model, accessed through a model-agnostic ASR abstraction interface.

## Alternatives Considered

### Whisper Large-v3 (non-turbo)

| Pros | Cons |
|------|------|
| Highest accuracy in Whisper family | Slower inference than turbo variant |
| Well-benchmarked | Higher GPU memory and compute requirements |
| | Latency may exceed realtime targets |

### Whisper Small / Medium

| Pros | Cons |
|------|------|
| Faster inference | Lower accuracy, especially for complex speech |
| Lower resource requirements | May not meet accuracy expectations |
| Good for `asr.fast` alias (future) | |

### Whisper Large-v3 Turbo

| Pros | Cons |
|------|------|
| Near Large-v3 accuracy | Still ~809M parameters (not lightweight) |
| Significantly faster than Large-v3 | Requires GPU for acceptable realtime performance |
| Supported by whisper.cpp and faster-whisper | English-optimized; other languages may need evaluation |
| 99 language support | |
| Active community and tooling | |

### Custom / Fine-tuned Models

| Pros | Cons |
|------|------|
| Domain-specific accuracy | Requires training data and infrastructure |
| Smaller model size possible | Out of scope for initial product |
| | Premature optimization |

### Commercial ASR APIs (Deepgram, AssemblyAI, etc.)

| Pros | Cons |
|------|------|
| Managed, optimized for realtime | Vendor lock-in |
| No infrastructure to manage | Per-minute pricing at scale |
| | Conflicts with self-hosted requirement |
| | Not model-agnostic (external dependency) |

## Trade-offs

- **Model size**: 809M parameters requires GPU for realtime performance. CPU-only inference is possible for development but not production.
- **Re-transcription for partials**: Whisper processes full audio chunks; partial transcription requires re-transcribing growing audio segments. This is computationally wasteful but simple.
- **English-first**: While Whisper supports 99 languages, Voragon initially targets English. Other languages are supported by the same model but may need dedicated evaluation and potentially language-specific models via AI Gateway aliases.

## Consequences

- ASR adapters must support Whisper Large-v3 Turbo model format
- GPU required for production inference (see [AWS GPU Strategy](../architecture/aws.md))
- Model weights must be downloaded and cached at service startup
- Partial transcription uses periodic re-transcription of accumulated audio
- Model is referenced by capability alias `asr.default` in the AI Gateway, not hardcoded in application logic

## Future Reconsideration

Reconsider if:
- Benchmarking shows Large-v3 Turbo cannot meet latency targets on target hardware
- A smaller model (Small/Medium) provides sufficient accuracy for the use case
- A specialized realtime ASR model (e.g., optimized streaming architecture) becomes available
- Fine-tuning on domain-specific data provides measurable accuracy improvement
