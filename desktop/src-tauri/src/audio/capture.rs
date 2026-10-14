use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;

use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{SampleFormat, StreamConfig};
use parking_lot::Mutex;
use serde::Serialize;
use tauri::{AppHandle, Emitter};

use super::frame::{FrameAccumulator, SAMPLE_RATE};

#[derive(Clone, Serialize)]
pub struct AudioDeviceInfo {
    pub index: u32,
    pub name: String,
}

pub struct AudioCaptureState {
    stop_flag: Arc<AtomicBool>,
    thread: Option<thread::JoinHandle<()>>,
}

impl Default for AudioCaptureState {
    fn default() -> Self {
        Self {
            stop_flag: Arc::new(AtomicBool::new(true)),
            thread: None,
        }
    }
}

pub fn list_input_devices() -> Result<Vec<AudioDeviceInfo>, String> {
    let host = cpal::default_host();
    let devices: Vec<_> = host
        .input_devices()
        .map_err(|e| format!("input_devices: {e}"))?
        .collect();
    Ok(devices
        .into_iter()
        .enumerate()
        .map(|(index, device)| AudioDeviceInfo {
            index: index as u32,
            name: device.name().unwrap_or_else(|_| format!("Device {index}")),
        })
        .collect())
}

pub fn start_capture(
    app: AppHandle,
    state: &mut AudioCaptureState,
    device_index: Option<u32>,
) -> Result<(), String> {
    stop_capture(state)?;

    let host = cpal::default_host();
    let devices: Vec<_> = host
        .input_devices()
        .map_err(|e| format!("input_devices: {e}"))?
        .collect();
    let device = match device_index {
        Some(idx) => devices
            .into_iter()
            .nth(idx as usize)
            .ok_or_else(|| format!("No input device at index {idx}"))?,
        None => host
            .default_input_device()
            .ok_or_else(|| "No default input device".to_string())?,
    };

    let supported = device
        .default_input_config()
        .map_err(|e| format!("default_input_config: {e}"))?;
    let sample_format = supported.sample_format();
    let config: StreamConfig = supported.config().into();
    let input_rate = config.sample_rate.0;
    let channels = config.channels as usize;

    let stop_flag = Arc::new(AtomicBool::new(false));
    state.stop_flag = Arc::clone(&stop_flag);

    let app_handle = app.clone();
    let handle = thread::spawn(move || {
        let accumulator = Arc::new(Mutex::new(FrameAccumulator::default()));
        let acc_emit = accumulator.clone();
        let stop = stop_flag.clone();

        let err_fn = |err| eprintln!("audio stream error: {err}");

        let stream = match sample_format {
            SampleFormat::F32 => device.build_input_stream(
                &config,
                move |data: &[f32], _| {
                    if stop.load(Ordering::Relaxed) {
                        return;
                    }
                    let mono: Vec<f32> = if channels == 1 {
                        data.to_vec()
                    } else {
                        data.chunks(channels)
                            .map(|c| c.iter().sum::<f32>() / channels as f32)
                            .collect()
                    };
                    let resampled = super::frame::resample_mono(&mono, input_rate, SAMPLE_RATE);
                    let mut frames = acc_emit.lock().push_samples(&resampled);
                    for frame in frames.drain(..) {
                        let _ = app_handle.emit("audio-frame", frame);
                    }
                },
                err_fn,
                None,
            ),
            SampleFormat::I16 => device.build_input_stream(
                &config,
                move |data: &[i16], _| {
                    if stop.load(Ordering::Relaxed) {
                        return;
                    }
                    let mono: Vec<f32> = if channels == 1 {
                        data.iter().map(|&s| s as f32 / i16::MAX as f32).collect()
                    } else {
                        data.chunks(channels)
                            .map(|c| {
                                c.iter().map(|&s| s as f32).sum::<f32>()
                                    / (channels as f32 * i16::MAX as f32)
                            })
                            .collect()
                    };
                    let resampled = super::frame::resample_mono(&mono, input_rate, SAMPLE_RATE);
                    let mut frames = acc_emit.lock().push_samples(&resampled);
                    for frame in frames.drain(..) {
                        let _ = app_handle.emit("audio-frame", frame);
                    }
                },
                err_fn,
                None,
            ),
            other => {
                eprintln!("Unsupported sample format: {other:?}");
                return;
            }
        };

        let stream = match stream {
            Ok(s) => s,
            Err(e) => {
                eprintln!("build_input_stream: {e}");
                return;
            }
        };
        if let Err(e) = stream.play() {
            eprintln!("stream.play: {e}");
            return;
        }
        while !stop_flag.load(Ordering::Relaxed) {
            thread::sleep(std::time::Duration::from_millis(50));
        }
        drop(stream);
    });

    state.thread = Some(handle);
    Ok(())
}

pub fn stop_capture(state: &mut AudioCaptureState) -> Result<(), String> {
    state.stop_flag.store(true, Ordering::Relaxed);
    if let Some(handle) = state.thread.take() {
        let _ = handle.join();
    }
    Ok(())
}
