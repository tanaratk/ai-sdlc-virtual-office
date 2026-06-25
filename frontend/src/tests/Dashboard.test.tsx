import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";
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
    const { getByText } = render(<Dashboard />, { wrapper });
    expect(getByText("Control the SDLC pipeline from requirement intake to deploy-ready output.")).toBeTruthy();
  });

  it("shows new project link", () => {
    const { getByText } = render(<Dashboard />, { wrapper });
    expect(getByText("New project")).toBeTruthy();
  });
});
