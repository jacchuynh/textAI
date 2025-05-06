import { Switch, Route, Link } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import NotFound from "@/pages/not-found";
import Game from "@/pages/game";
import DomainTest from "@/pages/domain-test";

function Navigation() {
  return (
    <nav className="bg-secondary py-2 px-4 mb-4">
      <div className="container flex gap-4">
        <Link href="/" className="text-primary hover:underline">Game</Link>
        <Link href="/domain-test" className="text-primary hover:underline">Domain Test</Link>
      </div>
    </nav>
  );
}

function Router() {
  return (
    <>
      <Navigation />
      <Switch>
        <Route path="/" component={Game} />
        <Route path="/domain-test" component={DomainTest} />
        <Route component={NotFound} />
      </Switch>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router />
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
