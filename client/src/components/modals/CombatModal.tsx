import { useState, useEffect } from "react";
import { useGameContext } from "@/context/GameContext";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Skull } from "lucide-react";

export default function CombatModal() {
  const { gameState, toggleShowCombat, setGameState } = useGameContext();
  const { combat, character } = gameState;
  const { toast } = useToast();
  
  const [combatLog, setCombatLog] = useState<string[]>([]);

  // Update combat log when combat state changes
  useEffect(() => {
    if (combat?.log && Array.isArray(combat.log)) {
      setCombatLog(combat.log);
    }
  }, [combat]);

  const combatActionMutation = useMutation({
    mutationFn: async (action: string) => {
      return await apiRequest("POST", "/api/game/combat-action", {
        gameId: gameState.gameId,
        action
      });
    },
    onSuccess: async (response) => {
      const data = await response.json();
      
      // Add new log entries to the combat log
      if (data.log) {
        setCombatLog(prev => [...prev, ...data.log]);
      }
      
      // Update combat state
      setGameState({
        type: 'UPDATE_COMBAT',
        payload: data
      });
      
      // Check if combat has ended
      if (data.status === 'ended') {
        setTimeout(() => {
          toggleShowCombat(false);
          
          // Add combat result to narrative
          setGameState({
            type: 'APPEND_NARRATIVE',
            payload: {
              type: 'system',
              content: `<div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm">
                <h4 class="text-primary-400 font-medium mb-2">Combat Result</h4>
                <p class="text-dark-200">${data.result}</p>
              </div>`
            }
          });
        }, 2000);
      }
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to perform combat action. Please try again.",
        variant: "destructive",
      });
    }
  });

  const handleCombatAction = (action: string) => {
    combatActionMutation.mutate(action);
  };

  if (!combat) return null;

  const enemyHealthPercentage = combat.enemy ? 
    (combat.enemy.currentHealth / combat.enemy.maxHealth) * 100 : 0;
  
  const playerHealthPercentage = character ? 
    (character.currentHealth / character.maxHealth) * 100 : 0;

  return (
    <Dialog 
      open={gameState.showCombat} 
      onOpenChange={(open) => toggleShowCombat(open)}
    >
      <DialogContent className="bg-dark-700 border-dark-600 text-dark-100 max-w-md" aria-describedby="combat-encounter-description">
        <DialogHeader>
          <DialogTitle className="text-xl font-display text-danger flex items-center">
            <Skull className="w-5 h-5 mr-2" />
            Combat Encounter
          </DialogTitle>
          <p id="combat-encounter-description" className="text-dark-300 text-sm mt-1">
            Face your enemy in battle. Choose actions wisely to defeat your opponent.
          </p>
        </DialogHeader>
        
        {/* Enemy Info */}
        <div className="mb-4">
          <h3 className="text-accent-400 font-display text-lg">
            {combat.enemy?.name || "Unknown Enemy"}
          </h3>
          
          {/* Enemy Health Bar */}
          <div className="mt-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-dark-200">Enemy Health</span>
              <span className="text-dark-300">
                {combat.enemy?.currentHealth || 0}/{combat.enemy?.maxHealth || 0}
              </span>
            </div>
            <Progress 
              value={enemyHealthPercentage} 
              className="h-2 bg-dark-800" 
              indicatorClassName="bg-danger" 
            />
          </div>
        </div>
        
        {/* Combat Log */}
        <div className="bg-dark-800 border border-dark-600 rounded-md p-3 h-40 overflow-y-auto scrollbar-themed text-sm">
          {combatLog.map((entry, index) => (
            <p key={index} className="text-dark-200">
              {entry}
            </p>
          ))}
        </div>
        
        {/* Combat Actions */}
        <div className="mt-4">
          <h4 className="text-dark-300 text-sm font-medium mb-2">Actions</h4>
          <div className="grid grid-cols-2 gap-2">
            <Button
              onClick={() => handleCombatAction('attack')}
              className="bg-primary-600 hover:bg-primary-700 text-white"
              disabled={combatActionMutation.isPending}
            >
              Attack
            </Button>
            <Button
              onClick={() => handleCombatAction('defend')}
              className="bg-dark-600 hover:bg-dark-500 text-dark-100"
              disabled={combatActionMutation.isPending}
            >
              Defend
            </Button>
            <Button
              onClick={() => handleCombatAction('use-item')}
              className="bg-dark-600 hover:bg-dark-500 text-dark-100"
              disabled={combatActionMutation.isPending || !(gameState.inventory?.items?.length)}
            >
              Use Item
            </Button>
            <Button
              onClick={() => handleCombatAction('flee')}
              className="bg-dark-600 hover:bg-dark-500 text-dark-100"
              disabled={combatActionMutation.isPending}
            >
              Flee
            </Button>
          </div>
        </div>
        
        {/* Player Health Summary */}
        <div className="mt-4 bg-dark-800/50 rounded-md p-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-dark-200">Your Health</span>
            <span className="text-dark-300">
              {character?.currentHealth || 0}/{character?.maxHealth || 0}
            </span>
          </div>
          <Progress 
            value={playerHealthPercentage} 
            className="h-2 bg-dark-700" 
            indicatorClassName="bg-danger" 
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
