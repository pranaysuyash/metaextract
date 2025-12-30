import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/lib/auth";
import { ContextAdapterProvider } from "@/context/ContextAdapter";
import { ErrorBoundary } from "@/components/error-boundary";
import NotFound from "@/pages/not-found";
import Home from "@/pages/home";
import Results from "@/pages/results";
import CheckoutSuccess from "@/pages/checkout-success";
import CreditsSuccess from "@/pages/credits-success";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home}/>
      <Route path="/results" component={Results}/>
      <Route path="/checkout/success" component={CheckoutSuccess}/>
      <Route path="/credits/success" component={CreditsSuccess}/>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ContextAdapterProvider>
            <TooltipProvider>
              <Toaster />
              <Router />
            </TooltipProvider>
          </ContextAdapterProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
