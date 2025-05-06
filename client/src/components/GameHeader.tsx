import { useState } from "react";
import { Link } from "wouter";
import { useGameContext } from "@/context/GameContext";
import { useToast } from "@/hooks/use-toast";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Bookmark, Settings, ChevronDown } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { queryClient } from "@/lib/queryClient";

export default function GameHeader() {
  const { gameState, setGameState } = useGameContext();
  const { toast } = useToast();

  const handleSaveGame = async () => {
    try {
      await apiRequest("POST", "/api/game/save", {
        gameId: gameState.gameId
      });
      
      toast({
        title: "Game Saved",
        description: "Your progress has been saved successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save game.",
        variant: "destructive",
      });
    }
  };

  return (
    <header className="bg-dark-700 border-b border-dark-600 p-4 md:px-6 flex items-center justify-between">
      <div className="flex items-center">
        <Link href="/">
          <h1 className="text-xl md:text-2xl font-display font-bold text-primary-400 text-fx-shadow cursor-pointer">
            Chronicles
          </h1>
        </Link>
        <span className="ml-3 text-xs md:text-sm bg-dark-600 text-dark-200 px-2 py-1 rounded font-mono">
          Alpha v0.1
        </span>
      </div>
      <div className="flex items-center gap-x-4">
        <button 
          onClick={handleSaveGame}
          className="text-dark-200 hover:text-primary-400 transition-colors"
        >
          <Bookmark className="w-5 h-5" />
        </button>
        
        <button 
          onClick={() => toast({
            title: "Coming Soon",
            description: "Settings will be available in a future update."
          })}
          className="text-dark-200 hover:text-primary-400 transition-colors"
        >
          <Settings className="w-5 h-5" />
        </button>
        
        <DropdownMenu>
          <DropdownMenuTrigger className="flex items-center gap-x-1 text-dark-200 hover:text-primary-400">
            <span className="hidden md:inline">Player</span>
            <ChevronDown className="w-5 h-5" />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-dark-700 border border-dark-600 text-dark-200">
            <DropdownMenuItem className="hover:bg-dark-600 hover:text-primary-400">
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['/api/game/start'] });
                setGameState({ type: 'NEW_GAME' });
              }}
              className="hover:bg-dark-600 hover:text-primary-400"
            >
              New Game
            </DropdownMenuItem>
            <DropdownMenuItem className="hover:bg-dark-600 hover:text-primary-400">
              Load Game
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-dark-600" />
            <DropdownMenuItem className="hover:bg-danger/20 hover:text-danger">
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
