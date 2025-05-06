import { useState } from "react";
import { useGameContext } from "@/context/GameContext";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { GAME_CLASSES, GAME_BACKGROUNDS } from "@/lib/utils";
import { useMutation } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";

interface CharacterCreationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CharacterCreationModal({ isOpen, onClose }: CharacterCreationModalProps) {
  const { setGameState } = useGameContext();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    name: "",
    characterClass: "",
    background: "commoner"
  });
  
  const createCharacterMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      return await apiRequest("POST", "/api/game/start", data);
    },
    onSuccess: async (response) => {
      const data = await response.json();
      console.log("Game start response:", data);
      
      // Make sure gameId is properly set
      if (!data.gameId) {
        console.error("No gameId returned from server", data);
        toast({
          title: "Error",
          description: "Failed to create character. No game ID returned.",
          variant: "destructive",
        });
        return;
      }
      
      setGameState({
        type: 'START_GAME',
        payload: data
      });
      
      // Store gameId in localStorage for persistence
      localStorage.setItem('gameId', data.gameId);
      
      queryClient.invalidateQueries({ queryKey: ['/api/game'] });
      toast({
        title: "Character Created",
        description: `Welcome to the world of Eldoria, ${formData.name}!`,
      });
      
      onClose();
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create character. Please try again.",
        variant: "destructive",
      });
    }
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.characterClass) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }
    
    createCharacterMutation.mutate(formData);
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-dark-700 border-dark-600 text-dark-100 max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl font-display text-primary-400">Create Your Character</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div>
            <Label htmlFor="characterName" className="text-dark-200">Character Name</Label>
            <Input 
              id="characterName"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="bg-dark-800 border-dark-500 text-dark-100"
              placeholder="Enter name..."
            />
          </div>
          
          <div>
            <Label className="text-dark-200 block mb-2">Character Class</Label>
            <div className="grid grid-cols-2 gap-3">
              {GAME_CLASSES.map((classOption) => (
                <div key={classOption.id} className="relative">
                  <input 
                    type="radio" 
                    id={`class-${classOption.id}`}
                    name="characterClass"
                    value={classOption.id}
                    checked={formData.characterClass === classOption.id}
                    onChange={() => setFormData({ ...formData, characterClass: classOption.id })}
                    className="peer absolute opacity-0"
                  />
                  <label 
                    htmlFor={`class-${classOption.id}`} 
                    className="block border border-dark-500 bg-dark-800 rounded-md p-3 cursor-pointer peer-checked:border-primary-500 peer-checked:bg-primary-900/30 transition-colors"
                  >
                    <div className="text-center">
                      <div className="font-display text-dark-100">{classOption.name}</div>
                      <div className="text-xs mt-1 text-dark-300">{classOption.description}</div>
                    </div>
                  </label>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <Label htmlFor="characterBackground" className="text-dark-200">Background</Label>
            <Select 
              value={formData.background} 
              onValueChange={(value) => setFormData({ ...formData, background: value })}
            >
              <SelectTrigger id="characterBackground" className="bg-dark-800 border-dark-500 text-dark-100">
                <SelectValue placeholder="Select a background" />
              </SelectTrigger>
              <SelectContent className="bg-dark-800 border-dark-600">
                {GAME_BACKGROUNDS.map((background) => (
                  <SelectItem key={background.id} value={background.id} className="text-dark-100 focus:bg-dark-700 focus:text-primary-400">
                    {background.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex gap-x-3 pt-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose}
              className="flex-grow bg-dark-600 hover:bg-dark-500 text-dark-100 border-dark-500"
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              className="flex-grow bg-primary-600 hover:bg-primary-700 text-white"
              disabled={createCharacterMutation.isPending}
            >
              Create Character
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
