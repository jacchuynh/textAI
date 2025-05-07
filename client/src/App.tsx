import { Switch, Route, Link } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import NotFound from "@/pages/not-found";
import Game from "@/pages/game";
import DomainTest from "@/pages/domain-test";
import DomainTestAlternate from "@/pages/domain-test-alternate";

function Navigation() {
  return (
    <nav className="bg-background border-b border-border py-3 px-4 mb-6 shadow-sm">
      <div className="container flex items-center justify-between">
        <div className="flex items-center">
          <span className="text-lg font-bold text-primary mr-6">Domain RPG</span>
          <div className="flex gap-6">
            <Link href="/" className="text-foreground hover:text-primary transition-colors">
              Game
            </Link>
            <Link href="/domain-test" className="text-foreground hover:text-primary transition-colors">
              Domain Test
            </Link>
            <Link href="/domain-test-alternate" className="text-foreground hover:text-primary transition-colors">
              Domain Test (REST)
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
            Alpha Version
          </span>
        </div>
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
        <Route path="/domain-test-alternate" component={DomainTestAlternate} />
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
