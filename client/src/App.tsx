import React from 'react';
import { Route, Switch } from 'wouter';
import { ThemeProvider } from '@/components/theme-provider';
import HomePage from './pages/HomePage';
import CreateCharacter from './pages/CreateCharacter';
import PlayerView from './pages/PlayerView';
import NotFound from './pages/NotFound';

function App() {
  return (
    <ThemeProvider defaultTheme="dark">
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
        <Switch>
          <Route path="/" component={HomePage} />
          <Route path="/create-character" component={CreateCharacter} />
          <Route path="/player/:userId" component={PlayerView} />
          <Route component={NotFound} />
        </Switch>
      </div>
    </ThemeProvider>
  );
}

export default App;