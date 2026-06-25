import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import ProjectLayout from "@/components/layout/ProjectLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AdminRoute } from "@/components/auth/AdminRoute";
import Dashboard from "@/pages/Dashboard";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProfilePage from "@/pages/ProfilePage";
import UserManagementPage from "@/pages/UserManagementPage";
import AdminProjectsPage from "@/pages/AdminProjectsPage";
import PipelineMonitorPage from "@/pages/PipelineMonitorPage";
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
import FigmaPage from "@/pages/FigmaPage";
import GitHubPage from "@/pages/GitHubPage";
import PMPage from "@/pages/PMPage";
import McpPage from "@/pages/McpPage";
import RAGPage from "@/pages/RAGPage";
import Settings from "@/pages/Settings";
import MonitoringPage from "@/pages/MonitoringPage";
import GeneratedCodePage from "@/pages/GeneratedCodePage";
import QAPage from "@/pages/QAPage";
import DeployPage from "@/pages/DeployPage";

export const router = createBrowserRouter([
  { path: "/login",    element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },

  {
    path: "/",
    element: <ProtectedRoute><AppLayout /></ProtectedRoute>,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "profile", element: <ProfilePage /> },

      // ── Administration (admin-only) ──────────────────────────────────────────
      { path: "users",          element: <AdminRoute><UserManagementPage /></AdminRoute> },
      { path: "admin/projects", element: <AdminRoute><AdminProjectsPage /></AdminRoute> },

      // ── Projects list + new ──────────────────────────────────────────────────
      { path: "projects",     element: <ProjectsList /> },
      { path: "projects/new", element: <NewProject /> },

      // ── Project workspace (tabs via ProjectLayout) ───────────────────────────
      {
        path: "projects/:projectId",
        element: <ProjectLayout />,
        children: [
          { index: true,              element: <ProjectWorkspace /> },
          { path: "intake",           element: <RequirementIntake /> },
          { path: "agents",           element: <AgentConsolePage /> },
          { path: "documents",        element: <DocumentReview /> },
          { path: "generated-code",   element: <GeneratedCodePage /> },
          { path: "qa",               element: <QAPage /> },
          { path: "deploy",           element: <DeployPage /> },
          { path: "traceability",     element: <TraceabilityPage /> },
          { path: "office",           element: <VirtualOfficePage /> },
          { path: "change-impact",    element: <ChangeImpactPage /> },
          { path: "documentation",    element: <DocumentationPage /> },
          { path: "pm",               element: <PMPage /> },
          { path: "github",           element: <GitHubPage /> },
          { path: "figma",            element: <FigmaPage /> },
          { path: "mcp",              element: <McpPage /> },
          { path: "rag",              element: <RAGPage /> },
        ],
      },

      // ── Delivery (global / cross-project) ───────────────────────────────────
      { path: "pipeline-runs", element: <PipelineMonitorPage /> },
      { path: "documents",     element: <DocumentReview /> },
      { path: "code-workspace",element: <Navigate to="/projects" replace /> },
      { path: "traceability",  element: <TraceabilityPage /> },
      { path: "office",        element: <VirtualOfficePage /> },
      { path: "monitoring",    element: <MonitoringPage /> },

      // ── AI Platform ──────────────────────────────────────────────────────────
      { path: "agents",   element: <AgentManagerPage /> },
      { path: "rag",      element: <RAGPage /> },
      { path: "mcp",      element: <McpPage /> },
      { path: "settings", element: <Settings /> },

      // ── Legacy / convenience aliases ─────────────────────────────────────────
      { path: "intake", element: <RequirementIntake /> },
    ],
  },
]);
