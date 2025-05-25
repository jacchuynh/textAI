import { Route, Switch } from 'wouter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';

import HomePage from './pages/HomePage';
import CreateCharacter from './pages/CreateCharacter';
import PlayerView from './pages/PlayerView';

// Create a new query client instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <Switch>
          <Route path="/" component={HomePage} />
          <Route path="/create-character" component={CreateCharacter} />
          <Route path="/player/:id" component={PlayerView} />
          <Route>404 - Not Found</Route>
        </Switch>
      </div>
      <Toaster />
    </QueryClientProvider>
  );
}