import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider, useAuth } from "@/lib/auth";
import { OnboardingProvider } from "@/lib/onboarding";
import { ThemeProvider } from "@/lib/theme-provider";
import { TutorialOverlay, useTutorialOverlay } from "@/components/tutorial-overlay";
import { ContextAdapterProvider } from "@/context/ContextAdapter";
import { ErrorBoundary } from "@/components/error-boundary";
import NotFound from "@/pages/not-found";
import Home from "@/pages/home";
import Results from "@/pages/results";
import Dashboard from "@/pages/dashboard";
import CheckoutSuccess from "@/pages/checkout-success";
import CreditsSuccess from "@/pages/credits-success";

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
          <Route path="/" element={<Home />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/results" element={<Results />} />
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
            element={
              <ProtectedRoute>
                <CreditsSuccess />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
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
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
