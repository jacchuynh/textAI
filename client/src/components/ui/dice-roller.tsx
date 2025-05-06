import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useGameContext } from "@/context/GameContext";

export interface DiceRollerProps {
  className?: string;
}

export function DiceRoller({ className }: DiceRollerProps) {
  const [diceResult, setDiceResult] = useState<{ value: number; type: string } | null>(null);
  const [isRolling, setIsRolling] = useState(false);
  const { setGameState } = useGameContext();

  const rollDice = (sides: number, type: string) => {
    setIsRolling(true);
    
    // Simulate dice roll
    const result = Math.floor(Math.random() * sides) + 1;
    
    // Show rolling animation
    setTimeout(() => {
      setDiceResult({ value: result, type });
      setIsRolling(false);
      
      // Add roll result to narrative
      setGameState({
        type: 'APPEND_NARRATIVE',
        payload: {
          type: 'system',
          content: `<div class="italic text-dark-300">You rolled a ${type} and got <span class="text-primary-400 font-medium">${result}</span>.</div>`
        }
      });
    }, 600);
  };

  // Define dice types
  const diceTypes = [
    { type: "D20", sides: 20 },
    { type: "D12", sides: 12 },
    { type: "D6", sides: 6 },
    { type: "D4", sides: 4 },
  ];

  return (
    <div className={cn("mt-2", className)}>
      <div className="flex gap-2">
        {diceTypes.map((dice) => (
          <Button
            key={dice.type}
            variant="outline"
            className="bg-dark-600 hover:bg-dark-500 text-dark-100 flex-grow"
            onClick={() => rollDice(dice.sides, dice.type)}
            disabled={isRolling}
          >
            {dice.type}
          </Button>
        ))}
      </div>
      
      {diceResult && (
        <div className={cn(
          "mt-3 bg-dark-600/50 rounded-md p-3 text-center",
          isRolling && "animate-roll"
        )}>
          <div className="text-xs text-dark-300">Result</div>
          <div className="text-2xl font-bold font-display text-primary-400 mt-1">
            {diceResult.value}
          </div>
          <div className="text-xs text-dark-400 mt-1">{diceResult.type} Roll</div>
        </div>
      )}
    </div>
  );
}

/* Add this to your CSS */
// @keyframes roll {
//   0% { transform: rotateX(0deg) rotateY(0deg); }
//   100% { transform: rotateX(720deg) rotateY(360deg); }
// }
// .animate-roll {
//   animation: roll 1s ease-out;
// }
