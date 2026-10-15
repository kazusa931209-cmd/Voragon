import { describe, expect, it } from "vitest";
import { formatDurationHms } from "../utils/formatDuration";

describe("formatDurationHms", () => {
  it("formats hours, minutes, and seconds", () => {
    expect(formatDurationHms(3661000)).toBe("01:01:01");
  });

  it("pads single-digit parts", () => {
    expect(formatDurationHms(5000)).toBe("00:00:05");
  });
});
