import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { registerSpec } from "./fixtures";
import { SchemaForm } from "./SchemaForm";

const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, refresh: vi.fn() }), usePathname: () => "/" }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

afterEach(cleanup);

describe("SchemaForm", () => {
  it("renders every field in spec order with labels and required markers", () => {
    render(<SchemaForm spec={registerSpec} />);
    expect(screen.getByLabelText(/First name/)).toBeTruthy();
    expect(screen.getByLabelText(/Email/).getAttribute("type")).toBe("email");
    expect(screen.getByLabelText(/Password/).getAttribute("type")).toBe("password");
    expect(screen.getByText("Experience")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Create account" })).toBeTruthy();
  });

  it("blocks submission and shows validation errors", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    render(<SchemaForm spec={registerSpec} />);
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    await waitFor(() => expect(screen.getAllByRole("alert").length).toBeGreaterThanOrEqual(3));
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("submits valid values to the action URL and redirects", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}", { status: 201 }));
    render(<SchemaForm spec={registerSpec} action="/api/session?mode=register" redirectTo="/dashboard" />);
    fireEvent.change(screen.getByLabelText(/First name/), { target: { value: "Zara" } });
    fireEvent.change(screen.getByLabelText(/Email/), { target: { value: "zara@example.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "longenough" } });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
    const [url, init] = fetchSpy.mock.calls[0];
    expect(url).toBe("/api/session?mode=register");
    expect(JSON.parse(String(init?.body))).toEqual({ f_name: "Zara", email: "zara@example.com", password: "longenough" });
  });
});
