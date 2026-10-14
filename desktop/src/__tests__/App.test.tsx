import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "../App";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn().mockResolvedValue([]),
}));

vi.mock("@tauri-apps/api/event", () => ({
  listen: vi.fn().mockResolvedValue(() => undefined),
}));

vi.mock("@tauri-apps/plugin-store", () => ({
  LazyStore: class {
    async get(key: string) {
      if (key === "backendUrl") return "ws://localhost:8000/v1/realtime";
      return null;
    }
    async set() {}
    async save() {}
  },
}));

describe("App", () => {
  it("renders Voragon title", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Voragon" })).toBeDefined();
  });
});
