import React from 'react';
import { Route, Switch } from 'wouter';
import { Toaster } from '@/components/ui/toaster';
import { ThemeProvider } from '@/components/theme-provider';

// Pages
import HomePage from './pages/HomePage';
import CreateCharacter from './pages/CreateCharacter';
import PlayerView from './pages/PlayerView';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <ThemeProvider defaultTheme="dark">
      <div className="min-h-screen bg-background text-foreground">
        <Switch>
          <Route path="/" component={HomePage} />
          <Route path="/create-character" component={CreateCharacter} />
          <Route path="/play/:userId" component={PlayerView} />
          <Route component={NotFound} />
        </Switch>
      </div>
      <Toaster />
    </ThemeProvider>
  );
}