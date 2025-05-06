import { useState, useRef, useEffect } from "react";
import { useGameContext } from "@/context/GameContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiRequest } from "@/lib/queryClient";
import { useMutation } from "@tanstack/react-query";
import { HelpCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import CombatModal from "@/components/modals/CombatModal";

export default function GameContent() {
  const { gameState, appendNarrativeContent, toggleShowCombat } = useGameContext();
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const narrativeRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Auto-scroll to bottom when narrative content updates
  useEffect(() => {
    if (narrativeRef.current) {
      narrativeRef.current.scrollTop = narrativeRef.current.scrollHeight;
    }
  }, [gameState.narrativeContent]);

  const sendInputMutation = useMutation({
    mutationFn: async (input: string) => {
      return await apiRequest("POST", "/api/game/send-input", {
        gameId: gameState.gameId,
        input
      });
    },
    onSuccess: async (response) => {
      const data = await response.json();
      
      // Add AI response to narrative
      appendNarrativeContent({
        type: 'ai-response',
        content: data.response.narrative
      });
      
      // Check if there's a combat event to show
      if (data.response.combat) {
        toggleShowCombat(true);
      }
      
      setIsLoading(false);
    },
    onError: (error) => {
      console.error("Error sending input:", error);
      toast({
        title: "Error",
        description: "Failed to process your input. Please try again.",
        variant: "destructive",
      });
      setIsLoading(false);
    }
  });

  const handlePlayerInput = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;
    
    // Add player input to narrative
    appendNarrativeContent({
      type: 'player-input',
      content: inputValue
    });
    
    setIsLoading(true);
    
    // Process commands starting with /
    if (inputValue.startsWith("/")) {
      handleCommand(inputValue);
    } else {
      // Send to AI for processing
      sendInputMutation.mutate(inputValue);
    }
    
    setInputValue("");
  };

  const handleCommand = (command: string) => {
    const cmd = command.toLowerCase();
    
    if (cmd === "/help") {
      appendNarrativeContent({
        type: 'system',
        content: `
          <div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm text-dark-200">
            <h4 class="text-primary-400 font-medium mb-2">Available Commands</h4>
            <ul class="list-disc pl-4 space-y-1">
              <li>/help - Show this help message</li>
              <li>/roll d20 - Roll a d20 die</li>
              <li>/stats - Show character stats</li>
              <li>/inventory - Show inventory</li>
              <li>/quests - Show active quests</li>
            </ul>
          </div>
        `
      });
      setIsLoading(false);
    } else if (cmd.startsWith("/roll")) {
      const diceMatch = cmd.match(/d(\d+)/);
      if (diceMatch && diceMatch[1]) {
        const max = parseInt(diceMatch[1]);
        const result = Math.floor(Math.random() * max) + 1;
        appendNarrativeContent({
          type: 'system',
          content: `<div class="italic text-dark-300">You rolled a d${max} and got <span class="text-primary-400 font-medium">${result}</span>.</div>`
        });
      }
      setIsLoading(false);
    } else {
      // Send command to the server
      sendInputMutation.mutate(inputValue);
    }
  };

  const handleSelectChoice = (choice: string) => {
    setInputValue(choice);
    handlePlayerInput({ preventDefault: () => {} } as React.FormEvent);
  };

  return (
    <div className="flex-grow flex flex-col h-full overflow-hidden">
      {/* Narrative Display Window */}
      <div className="relative flex-grow overflow-hidden flex flex-col">
        {/* Progress Indicator */}
        {isLoading && (
          <div className="absolute top-0 left-0 right-0 h-1 bg-dark-600">
            <div className="h-full bg-primary-500 w-1/3 animate-pulse"></div>
          </div>
        )}
      
        {/* Narrative Text Area */}
        <div 
          ref={narrativeRef}
          className="flex-grow overflow-y-auto scrollbar-themed p-4 md:p-6 narrative-text"
          id="narrativeDisplay"
        >
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Initial System Message */}
            {gameState.narrativeContent.length === 0 && (
              <div className="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm text-dark-200">
                <p>Welcome to <span className="text-primary-400 font-semibold">Chronicles</span>, an AI-driven text RPG. Your adventure awaits!</p>
                <p className="text-xs mt-2">To begin, choose a character type below or click New Game.</p>
              </div>
            )}

            {/* Narrative Content */}
            {gameState.narrativeContent.map((entry, index) => (
              <div key={index} className="narrative-entry">
                {entry.type === 'system' ? (
                  <div dangerouslySetInnerHTML={{ __html: entry.content }} />
                ) : entry.type === 'player-input' ? (
                  <div className="player-input text-primary-300 italic">
                    &gt; {entry.content}
                  </div>
                ) : (
                  <div className="ai-response">
                    {entry.content.split('\n').map((paragraph, i) => (
                      <p key={i} className={i === 0 ? 'text-lg' : ''}>{paragraph}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Choice Options */}
            {gameState.choices && gameState.choices.length > 0 && (
              <div className="flex flex-col sm:flex-row flex-wrap gap-3 mt-4">
                {gameState.choices.map((choice, index) => (
                  <Button
                    key={index}
                    className="bg-dark-700 hover:bg-dark-600 text-dark-100 border border-dark-500 rounded-md px-4 py-2 text-left transition-colors flex-grow sm:flex-grow-0 h-auto"
                    onClick={() => handleSelectChoice(choice)}
                  >
                    {choice}
                  </Button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Player Input Area */}
      <div className="border-t border-dark-600 bg-dark-700 p-4">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handlePlayerInput}>
            <div className="flex items-center gap-x-2">
              <div className="relative flex-grow">
                <Input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="w-full bg-dark-800 border border-dark-500 rounded-md py-2 px-4 text-dark-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  placeholder="Enter your action or type '/help' for commands..."
                  disabled={isLoading}
                />
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-dark-400 hover:text-primary-400"
                      >
                        <HelpCircle className="w-5 h-5" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="bg-dark-800 border-dark-600 text-dark-100">
                      <p>Type '/help' for available commands</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <Button
                type="submit"
                className="bg-primary-600 hover:bg-primary-700 text-white rounded-md py-2 px-4 flex items-center gap-x-1 transition-colors"
                disabled={isLoading}
              >
                <span>Send</span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
              </Button>
            </div>
          </form>
        </div>
      </div>
      
      {/* Combat Modal */}
      <CombatModal />
    </div>
  );
}
