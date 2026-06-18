import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Dashboard from "@/pages/Dashboard";

vi.mock("@/services/projectApi", () => ({
  projectApi: {
    list: vi.fn().mockResolvedValue({ total: 0, page: 1, page_size: 20, items: [] }),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Dashboard", () => {
  it("renders heading", () => {
    render(<Dashboard />, { wrapper });
    expect(screen.getByText("Projects")).toBeTruthy();
  });

  it("shows new project link", () => {
    render(<Dashboard />, { wrapper });
    expect(screen.getByText("New Project")).toBeTruthy();
  });
});
