import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AdminRoute } from "@/components/auth/AdminRoute";
import Dashboard from "@/pages/Dashboard";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProfilePage from "@/pages/ProfilePage";
import UserManagementPage from "@/pages/UserManagementPage";
import ProjectsList from "@/pages/ProjectsList";
import NewProject from "@/pages/NewProject";
import ProjectWorkspace from "@/pages/ProjectWorkspace";
import RequirementIntake from "@/pages/RequirementIntake";
import AgentConsolePage from "@/pages/AgentConsolePage";
import AgentManagerPage from "@/pages/AgentManagerPage";
import DocumentReview from "@/pages/DocumentReview";
import TraceabilityPage from "@/pages/TraceabilityPage";
import VirtualOfficePage from "@/pages/VirtualOfficePage";
import ChangeImpactPage from "@/pages/ChangeImpactPage";
import DocumentationPage from "@/pages/DocumentationPage";
import GitHubPage from "@/pages/GitHubPage";
import PMPage from "@/pages/PMPage";
import McpPage from "@/pages/McpPage";
import RAGPage from "@/pages/RAGPage";
import Settings from "@/pages/Settings";
import MonitoringPage from "@/pages/MonitoringPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },

  {
    path: "/",
    element: <ProtectedRoute><AppLayout /></ProtectedRoute>,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "profile", element: <ProfilePage /> },
      {
        path: "users",
        element: <AdminRoute><UserManagementPage /></AdminRoute>,
      },
      { path: "projects", element: <ProjectsList /> },
      { path: "projects/new", element: <NewProject /> },
      { path: "projects/:projectId", element: <ProjectWorkspace /> },
      { path: "projects/:projectId/intake", element: <RequirementIntake /> },
      { path: "projects/:projectId/agents", element: <AgentConsolePage /> },
      { path: "projects/:projectId/documents", element: <DocumentReview /> },
      { path: "projects/:projectId/traceability", element: <TraceabilityPage /> },
      { path: "projects/:projectId/office", element: <VirtualOfficePage /> },
      { path: "projects/:projectId/change-impact", element: <ChangeImpactPage /> },
      { path: "projects/:projectId/documentation", element: <DocumentationPage /> },
      { path: "projects/:projectId/pm", element: <PMPage /> },
      { path: "projects/:projectId/github", element: <GitHubPage /> },
      { path: "projects/:projectId/mcp", element: <McpPage /> },
      { path: "projects/:projectId/rag", element: <RAGPage /> },
      { path: "mcp", element: <McpPage /> },
      { path: "intake", element: <RequirementIntake /> },
      { path: "agents", element: <AgentManagerPage /> },
      { path: "documents", element: <DocumentReview /> },
      { path: "traceability", element: <TraceabilityPage /> },
      { path: "office", element: <VirtualOfficePage /> },
      { path: "monitoring", element: <MonitoringPage /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);
