from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from realtime_cli.audio_source import iter_microphone_frames, iter_pcm_frames_from_file_async
from realtime_cli.client import run_session


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minimal Voragon realtime test client (microphone or PCM/WAV file → transcript)",
    )
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/v1/realtime",
        help="Realtime WebSocket URL",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="BCP-47 language code for audio.start",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Replay mono 16 kHz s16le PCM or WAV instead of microphone",
    )
    parser.add_argument(
        "--device",
        type=int,
        help="Sounddevice input device index (microphone mode)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Stop after N seconds (microphone mode only)",
    )
    parser.add_argument(
        "--realtime",
        action="store_true",
        help="Pace file frames at 20 ms intervals (default for file: send as fast as possible)",
    )
    parser.add_argument(
        "--tail",
        type=float,
        help="Seconds to wait for late transcripts after streaming (default: 60 file, 5 mic)",
    )
    return parser


async def _run(args: argparse.Namespace) -> None:
    if args.file is not None:
        if not args.file.exists():
            raise FileNotFoundError(args.file)
        frame_source = iter_pcm_frames_from_file_async(args.file)
        realtime_pacing = args.realtime
        tail_wait_s = 60.0 if args.tail is None else args.tail
        send_stop_after_stream = True
    else:
        frame_source = iter_microphone_frames(device=args.device, duration_s=args.duration)
        realtime_pacing = True
        tail_wait_s = 5.0 if args.tail is None else args.tail
        send_stop_after_stream = False

    await run_session(
        args.url,
        frame_source,
        language=args.language,
        realtime_pacing=realtime_pacing,
        tail_wait_s=tail_wait_s,
        send_stop_after_stream=send_stop_after_stream,
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        asyncio.run(_run(args))
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
