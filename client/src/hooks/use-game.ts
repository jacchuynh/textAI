import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import { GameState, Character, Location, Inventory, Quest, Enemy, Combat } from '@shared/types';

export function useGame() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  // Get current game state
  const { 
    data: gameState, 
    isLoading, 
    isError 
  } = useQuery<GameState>({
    queryKey: ['/api/game/state'],
    retry: false
  });
  
  // Start a new game
  const startGame = useMutation({
    mutationFn: async (characterData: { name: string, characterClass: string, background: string }) => {
      const response = await apiRequest('POST', '/api/game/start', characterData);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/game/state'] });
      toast({
        title: 'Game Started',
        description: 'Your new adventure begins!',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to start a new game. Please try again.',
        variant: 'destructive',
      });
    },
  });
  
  // Send player input
  const sendInput = useMutation({
    mutationFn: async (input: string) => {
      const response = await apiRequest('POST', '/api/game/send-input', { input });
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['/api/game/state'] });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to process your input. Please try again.',
        variant: 'destructive',
      });
    },
  });
  
  // Save game
  const saveGame = useMutation({
    mutationFn: async () => {
      const response = await apiRequest('POST', '/api/game/save', {});
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Game Saved',
        description: 'Your progress has been saved.',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to save the game. Please try again.',
        variant: 'destructive',
      });
    },
  });
  
  // Load game
  const loadGame = useMutation({
    mutationFn: async (gameId: string) => {
      const response = await apiRequest('POST', '/api/game/load', { gameId });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/game/state'] });
      toast({
        title: 'Game Loaded',
        description: 'Your adventure continues...',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to load the game. Please try again.',
        variant: 'destructive',
      });
    },
  });
  
  // Combat action
  const performCombatAction = useMutation({
    mutationFn: async (action: string) => {
      const response = await apiRequest('POST', '/api/game/combat-action', { action });
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['/api/game/state'] });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to perform combat action. Please try again.',
        variant: 'destructive',
      });
    },
  });
  
  return {
    gameState,
    isLoading,
    isError,
    startGame,
    sendInput,
    saveGame,
    loadGame,
    performCombatAction
  };
}
