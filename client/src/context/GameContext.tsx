import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { GameState, Character, Location, Inventory, Quest, Enemy, Combat, NarrativeEntry } from '@shared/types';

interface GameContextType {
  gameState: GameStateInternal;
  setGameState: (action: GameStateAction) => void;
  appendNarrativeContent: (entry: NarrativeEntry) => void;
  toggleShowCombat: (show: boolean) => void;
}

interface GameStateInternal {
  gameId: string | null;
  character: Character | null;
  location: Location | null;
  inventory: Inventory | null;
  quests: Quest[] | null;
  narrativeContent: NarrativeEntry[];
  choices: string[] | null;
  combat: Combat | null;
  showCombat: boolean;
}

type GameStateAction = 
  | { type: 'START_GAME'; payload: GameState }
  | { type: 'UPDATE_GAME'; payload: Partial<GameState> }
  | { type: 'APPEND_NARRATIVE'; payload: NarrativeEntry }
  | { type: 'SET_CHOICES'; payload: string[] }
  | { type: 'NEW_GAME' }
  | { type: 'TOGGLE_COMBAT'; payload: boolean }
  | { type: 'UPDATE_COMBAT'; payload: Combat };

const initialGameState: GameStateInternal = {
  gameId: null,
  character: null,
  location: null,
  inventory: null,
  quests: null,
  narrativeContent: [],
  choices: null,
  combat: null,
  showCombat: false
};

const GameContext = createContext<GameContextType | undefined>(undefined);

export function GameProvider({ children }: { children: ReactNode }) {
  const [gameState, setGameStateInternal] = useState<GameStateInternal>(initialGameState);

  // Load game state from the server on initial load
  const { data: gameData, isLoading } = useQuery({
    queryKey: ['/api/game'],
    enabled: false // Only load when explicitly requested
  });

  useEffect(() => {
    if (gameData) {
      setGameStateInternal(prevState => ({
        ...prevState,
        ...gameData,
        narrativeContent: [
          ...prevState.narrativeContent,
          { 
            type: 'ai-response', 
            content: gameData.narrativeContent || 'Your adventure begins in the realm of Eldoria...'
          }
        ]
      }));
    }
  }, [gameData]);

  // State reducer
  const setGameState = (action: GameStateAction) => {
    switch (action.type) {
      case 'START_GAME':
        setGameStateInternal(prevState => ({
          ...prevState,
          gameId: action.payload.gameId || null,
          character: action.payload.character || null,
          location: action.payload.location || null,
          inventory: action.payload.inventory || null,
          quests: action.payload.quests || [],
          narrativeContent: [
            ...prevState.narrativeContent,
            { 
              type: 'system', 
              content: `<div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm text-dark-200">
                <p>Welcome to <span class="text-primary-400 font-semibold">Chronicles</span>, ${action.payload.character?.name}!</p>
                <p class="text-xs mt-2">Your adventure begins in the realm of Eldoria...</p>
              </div>`
            },
            { 
              type: 'ai-response', 
              content: action.payload.narrativeContent || 'Your adventure begins in the realm of Eldoria...'
            }
          ],
          choices: action.payload.choices || null
        }));
        break;

      case 'UPDATE_GAME':
        setGameStateInternal(prevState => ({
          ...prevState,
          character: action.payload.character || prevState.character,
          location: action.payload.location || prevState.location,
          inventory: action.payload.inventory || prevState.inventory,
          quests: action.payload.quests || prevState.quests,
          choices: action.payload.choices || prevState.choices
        }));
        break;

      case 'APPEND_NARRATIVE':
        setGameStateInternal(prevState => ({
          ...prevState,
          narrativeContent: [...prevState.narrativeContent, action.payload]
        }));
        break;

      case 'SET_CHOICES':
        setGameStateInternal(prevState => ({
          ...prevState,
          choices: action.payload
        }));
        break;

      case 'NEW_GAME':
        setGameStateInternal(initialGameState);
        break;

      case 'TOGGLE_COMBAT':
        setGameStateInternal(prevState => ({
          ...prevState,
          showCombat: action.payload
        }));
        break;

      case 'UPDATE_COMBAT':
        setGameStateInternal(prevState => ({
          ...prevState,
          combat: action.payload,
          character: action.payload.character || prevState.character
        }));
        break;

      default:
        break;
    }
  };

  const appendNarrativeContent = (entry: NarrativeEntry) => {
    setGameState({ type: 'APPEND_NARRATIVE', payload: entry });
  };

  const toggleShowCombat = (show: boolean) => {
    setGameState({ type: 'TOGGLE_COMBAT', payload: show });
  };

  return (
    <GameContext.Provider value={{ 
      gameState, 
      setGameState, 
      appendNarrativeContent,
      toggleShowCombat
    }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGameContext() {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGameContext must be used within a GameProvider');
  }
  return context;
}
