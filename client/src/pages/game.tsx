import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { PlayCircle, RefreshCw, Calendar, Book } from "lucide-react";
import { useGameContext } from "@/context/GameContext";
import { GameProvider } from "@/context/GameContext";

function GameSelection() {
  const { toast } = useToast();
  const { setGameState } = useGameContext();
  const [selectedGameId, setSelectedGameId] = useState<string | null>(null);

  // Query for available games
  const { data: games, isLoading, refetch } = useQuery({
    queryKey: ['/api/games'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/game/list');
        if (!response.ok) {
          throw new Error('Failed to fetch games');
        }
        return response.json();
      } catch (error) {
        console.error("Error fetching games:", error);
        return [];
      }
    }
  });

  // Start a new test game
  const createNewGame = async () => {
    try {
      const response = await fetch('/api/game/test', {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to create test game');
      }
      
      const gameData = await response.json();
      toast({
        title: "Success",
        description: "Created a new test game",
      });
      
      // Refresh the games list
      refetch();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create test game",
        variant: "destructive",
      });
    }
  };

  // Load a game
  const loadGame = async (gameId: string) => {
    try {
      const response = await fetch(`/api/game/${gameId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load game');
      }
      
      const gameData = await response.json();
      setGameState({ type: 'START_GAME', payload: gameData });
      
      toast({
        title: "Success",
        description: "Game loaded successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load game",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="container py-10 max-w-4xl">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold mb-2">Domain RPG</h1>
        <p className="text-muted-foreground">A text-based RPG with advanced domain-based character progression</p>
      </div>
      
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Available Games</CardTitle>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => refetch()}
                  disabled={isLoading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
                <Button 
                  size="sm" 
                  onClick={createNewGame}
                >
                  Create Test Game
                </Button>
              </div>
            </div>
            <CardDescription>Select a game to continue your adventure</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-4 text-muted-foreground">Loading available games...</p>
              </div>
            ) : games && games.length > 0 ? (
              <div className="space-y-2">
                {games.map((game: any) => (
                  <div 
                    key={game.id} 
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedGameId === game.id 
                        ? 'border-primary bg-primary/5' 
                        : 'border-border hover:border-primary/50'
                    }`}
                    onClick={() => setSelectedGameId(game.id)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-medium">{game.name || 'Adventure Game'}</h3>
                        <div className="flex items-center gap-x-4 mt-1 text-sm text-muted-foreground">
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {new Date(game.updatedAt).toLocaleDateString()}
                          </span>
                          <span className="flex items-center">
                            <Book className="w-3 h-3 mr-1" />
                            ID: {game.id.substring(0, 8)}...
                          </span>
                        </div>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => loadGame(game.id)}
                      >
                        <PlayCircle className="w-5 h-5 mr-1" />
                        Play
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No games available. Create a new test game to begin!</p>
              </div>
            )}
          </CardContent>
          <CardFooter className="border-t px-6 py-4">
            <div className="flex justify-between items-center w-full">
              <p className="text-sm text-muted-foreground">
                {games ? `${games.length} game${games.length !== 1 ? 's' : ''} available` : 'Loading...'}
              </p>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

export default function Game() {
  return (
    <GameProvider>
      <GameSelection />
    </GameProvider>
  );
}
