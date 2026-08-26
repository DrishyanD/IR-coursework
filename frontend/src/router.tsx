import { createBrowserRouter, Navigate } from "react-router";
import { AppLayout } from "./layouts/AppLayout";
import { HomePage } from "./pages/HomePage";
import { SearchPage } from "./pages/SearchPage";
import { PublicationsPage } from "./pages/PublicationsPage";
import { PublicationDetailPage } from "./pages/PublicationDetailPage";
import { ClusteringPage } from "./pages/ClusteringPage";
import { DataManagementPage } from "./pages/DataManagementPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/search", element: <SearchPage /> },
      { path: "/advanced-search", element: <Navigate to="/search" replace /> },
      { path: "/publications", element: <PublicationsPage /> },
      { path: "/publications/:publicationId", element: <PublicationDetailPage /> },
      { path: "/clustering", element: <ClusteringPage /> },
      { path: "/data", element: <DataManagementPage /> },
      { path: "/evaluation", element: <Navigate to="/data" replace /> },
      { path: "/system", element: <Navigate to="/data" replace /> },
      { path: "/about", element: <Navigate to="/" replace /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
