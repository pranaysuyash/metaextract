import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider, useAuth } from "@/lib/auth";
import { OnboardingProvider } from "@/lib/onboarding";
import { ThemeProvider } from "@/lib/theme-provider";
import { AccessibilityProvider } from "@/lib/accessibility-context";
import { TutorialOverlay, useTutorialOverlay } from "@/components/tutorial-overlay";
import { ContextAdapterProvider } from "@/context/ContextAdapter";
import { ErrorBoundary } from "@/components/error-boundary";
import Home from "@/pages/home";
import BatchResultsPage from "@/pages/batch-results";
import TimelineViewPage from "@/pages/timeline-view";
import ImagesMvpLanding from "@/pages/images-mvp";
import ImagesMvpResults from "@/pages/images-mvp/results";
import ImagesMvpCreditsSuccess from "@/pages/images-mvp/credits-success";
import ImagesMvpAnalytics from "@/pages/images-mvp/analytics";
import DashboardImproved from "@/pages/dashboard-improved";
import CheckoutSuccess from "@/pages/checkout-success";
import CreditsSuccess from "@/pages/credits-success";
import CreditsPage from "@/pages/credits";
import PrivacyPolicy from "@/pages/privacy-policy";
import TermsOfService from "@/pages/terms-of-service";
import GDPRCompliance from "@/pages/gdpr-compliance";
import ResetPasswordPage from "@/pages/reset-password";

// Protected Route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function AppRouter() {
  const { isOpen, close } = useTutorialOverlay();

  return (
    <>
      {/* Skip Links for Keyboard Navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded focus:focus-visible:outline-none focus:focus-visible:ring-2 focus:focus-visible:ring-primary/50"
      >
        Skip to main content
      </a>
      <a
        href="#main-navigation"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-64 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded focus:focus-visible:outline-none focus:focus-visible:ring-2 focus:focus-visible:ring-primary/50"
      >
        Skip to navigation
      </a>

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/images_mvp" replace />} />
          <Route path="/home" element={<Home />} />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <DashboardImproved />
              </ProtectedRoute>
            }
          />
          <Route
            path="/credits"
            element={
              <ProtectedRoute>
                <CreditsPage />
              </ProtectedRoute>
            }
          />
          <Route path="/dashboard" element={<Navigate to="/settings" replace />} />
          <Route
            path="/batch-results"
            element={
              <ProtectedRoute>
                <BatchResultsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/timeline-view"
            element={
              <ProtectedRoute>
                <TimelineViewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/checkout/success"
            element={
              <ProtectedRoute>
                <CheckoutSuccess />
              </ProtectedRoute>
            }
          />
          <Route
            path="/credits/success"
            element={<CreditsSuccess />}
          />
          <Route path="/images_mvp" element={<ImagesMvpLanding />} />
          <Route path="/images_mvp/results" element={<ImagesMvpResults />} />
          <Route path="/images_mvp/credits/success" element={<ImagesMvpCreditsSuccess />} />
          <Route
            path="/images_mvp/analytics"
            element={
              <ProtectedRoute>
                <ImagesMvpAnalytics />
              </ProtectedRoute>
            }
          />
          <Route path="/images-mvp" element={<Navigate to="/images_mvp" replace />} />
          <Route path="/images-mvp/results" element={<Navigate to="/images_mvp/results" replace />} />
          <Route path="/images-mvp/credits/success" element={<Navigate to="/images_mvp/credits/success" replace />} />
          <Route path="/images-mvp/analytics" element={<Navigate to="/images_mvp/analytics" replace />} />

          {/* Legal Compliance Routes */}
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/gdpr" element={<GDPRCompliance />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          <Route path="*" element={<Navigate to="/images_mvp" replace />} />
        </Routes>
      </BrowserRouter>

      {/* Tutorial Overlay */}
      <TutorialOverlay isOpen={isOpen} onClose={close} />
    </>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultMode="dark" injectCssVars={true}>
        <AccessibilityProvider>
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              <OnboardingProvider>
                <ContextAdapterProvider>
                  <TooltipProvider>
                    <Toaster />
                    <AppRouter />
                  </TooltipProvider>
                </ContextAdapterProvider>
              </OnboardingProvider>
            </AuthProvider>
          </QueryClientProvider>
        </AccessibilityProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
