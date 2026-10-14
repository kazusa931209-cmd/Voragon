pub const SAMPLE_RATE: u32 = 16_000;
pub const SAMPLES_PER_FRAME: usize = 320;
pub const BYTES_PER_FRAME: usize = SAMPLES_PER_FRAME * 2;

pub fn f32_to_s16le(samples: &[f32]) -> Vec<u8> {
    let mut out = Vec::with_capacity(samples.len() * 2);
    for &sample in samples {
        let clamped = sample.clamp(-1.0, 1.0);
        let scaled = (clamped * i16::MAX as f32) as i16;
        out.extend_from_slice(&scaled.to_le_bytes());
    }
    out
}

pub fn resample_mono(input: &[f32], input_rate: u32, output_rate: u32) -> Vec<f32> {
    if input.is_empty() {
        return Vec::new();
    }
    if input_rate == output_rate {
        return input.to_vec();
    }
    let ratio = input_rate as f64 / output_rate as f64;
    let out_len = ((input.len() as f64) / ratio).floor() as usize;
    let mut out = Vec::with_capacity(out_len.max(1));
    let mut pos = 0.0;
    while (pos as usize) < input.len() && out.len() < out_len {
        let idx = pos as usize;
        let frac = pos - idx as f64;
        let a = input[idx];
        let b = input.get(idx + 1).copied().unwrap_or(a);
        out.push(a + (b - a) * frac as f32);
        pos += ratio;
    }
    out
}

#[derive(Default)]
pub struct FrameAccumulator {
    buffer: Vec<f32>,
}

impl FrameAccumulator {
    pub fn push_samples(&mut self, samples: &[f32]) -> Vec<Vec<u8>> {
        self.buffer.extend_from_slice(samples);
        let mut frames = Vec::new();
        while self.buffer.len() >= SAMPLES_PER_FRAME {
            let chunk: Vec<f32> = self.buffer.drain(..SAMPLES_PER_FRAME).collect();
            let pcm = f32_to_s16le(&chunk);
            debug_assert_eq!(pcm.len(), BYTES_PER_FRAME);
            frames.push(pcm);
        }
        frames
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accumulator_emits_640_byte_frames() {
        let mut acc = FrameAccumulator::default();
        let samples = vec![0.0_f32; SAMPLES_PER_FRAME];
        let frames = acc.push_samples(&samples);
        assert_eq!(frames.len(), 1);
        assert_eq!(frames[0].len(), BYTES_PER_FRAME);
    }

    #[test]
    fn resample_halves_length_when_halving_rate() {
        let input: Vec<f32> = (0..100).map(|i| i as f32).collect();
        let out = resample_mono(&input, 32_000, 16_000);
        assert!(out.len() >= 45 && out.len() <= 55);
    }
}
