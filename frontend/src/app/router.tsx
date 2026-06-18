import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import Dashboard from "@/pages/Dashboard";
import ProjectWorkspace from "@/pages/ProjectWorkspace";
import RequirementIntake from "@/pages/RequirementIntake";
import AgentConsolePage from "@/pages/AgentConsolePage";
import DocumentReview from "@/pages/DocumentReview";
import TraceabilityPage from "@/pages/TraceabilityPage";
import VirtualOfficePage from "@/pages/VirtualOfficePage";
import ChangeImpactPage from "@/pages/ChangeImpactPage";
import GitHubPage from "@/pages/GitHubPage";
import McpPage from "@/pages/McpPage";
import Settings from "@/pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "projects", element: <Dashboard /> },
      { path: "projects/:projectId", element: <ProjectWorkspace /> },
      { path: "projects/:projectId/intake", element: <RequirementIntake /> },
      { path: "projects/:projectId/agents", element: <AgentConsolePage /> },
      { path: "projects/:projectId/documents", element: <DocumentReview /> },
      { path: "projects/:projectId/traceability", element: <TraceabilityPage /> },
      { path: "projects/:projectId/office", element: <VirtualOfficePage /> },
      { path: "projects/:projectId/change-impact", element: <ChangeImpactPage /> },
      { path: "projects/:projectId/github", element: <GitHubPage /> },
      { path: "projects/:projectId/mcp", element: <McpPage /> },
      { path: "mcp", element: <McpPage /> },
      { path: "intake", element: <RequirementIntake /> },
      { path: "agents", element: <AgentConsolePage /> },
      { path: "documents", element: <DocumentReview /> },
      { path: "traceability", element: <TraceabilityPage /> },
      { path: "office", element: <VirtualOfficePage /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);
