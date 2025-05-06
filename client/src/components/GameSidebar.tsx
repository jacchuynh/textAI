import { useState, useEffect } from "react";
import { useGameContext } from "@/context/GameContext";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { DiceRoller } from "@/components/ui/dice-roller";
import { MapPin, Zap, Package, ScrollText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { calculateMaxXp } from "@/lib/utils";
import CharacterCreationModal from "@/components/modals/CharacterCreationModal";

export default function GameSidebar() {
  const { gameState } = useGameContext();
  const { character, inventory, location, quests } = gameState || {};
  const [showCharacterCreation, setShowCharacterCreation] = useState(false);

  const healthPercentage = character ? (character.currentHealth / character.maxHealth) * 100 : 100;
  const manaPercentage = character ? (character.currentMana / character.maxMana) * 100 : 100;
  const xpPercentage = character ? (character.xp / calculateMaxXp(character.level)) * 100 : 0;

  return (
    <>
      <aside className="w-80 bg-dark-700 border-l border-dark-600 overflow-y-auto scrollbar-themed">
        {/* Sidebar Header with Character Info */}
        <div className="p-4 border-b border-dark-600 bg-dark-700/70">
          {character ? (
            // Character Created View
            <div>
              <div className="flex items-center gap-x-3">
                <div className="w-12 h-12 rounded-full bg-primary-900 flex items-center justify-center text-primary-300 border border-primary-700">
                  <span className="font-display text-lg">{character.name.charAt(0)}</span>
                </div>
                <div>
                  <h3 className="font-display text-lg text-primary-400">{character.name}</h3>
                  <div className="flex items-center text-xs text-dark-300 gap-x-2">
                    <span>{character.class}</span>
                    <span className="w-1 h-1 rounded-full bg-dark-400"></span>
                    <span>Level {character.level}</span>
                  </div>
                </div>
              </div>
              
              {/* Character XP Bar */}
              <div className="mt-3">
                <Progress value={xpPercentage} className="h-2 bg-dark-800" indicatorClassName="bg-primary-600" />
              </div>
              <div className="flex justify-between text-xs text-dark-400 mt-1">
                <span>XP: {character.xp}/{calculateMaxXp(character.level)}</span>
                <span>Level {character.level}</span>
              </div>
            </div>
          ) : (
            // Character Not Created Yet View
            <div className="text-center py-4">
              <h3 className="font-display text-lg text-primary-400">Create Your Character</h3>
              <p className="text-dark-300 text-sm mt-1">Begin your journey by creating a character</p>
              <Button 
                className="mt-3 bg-primary-600 hover:bg-primary-700 text-white"
                onClick={() => setShowCharacterCreation(true)}
              >
                New Game
              </Button>
            </div>
          )}
        </div>
        
        {/* Game Status Sections */}
        {character && (
          <div>
            {/* Location Section */}
            <div className="border-b border-dark-600">
              <div className="p-4">
                <h4 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  Location
                </h4>
                <div className="mt-2">
                  <h5 className="text-accent-400 font-medium">{location?.name || "Unknown"}</h5>
                  <p className="text-sm text-dark-200 mt-1">{location?.description || "No description available."}</p>
                </div>
              </div>
            </div>
            
            {/* Stats Section */}
            <div className="border-b border-dark-600">
              <div className="p-4">
                <h4 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center">
                  <Zap className="w-4 h-4 mr-1" />
                  Stats
                </h4>
                <div className="mt-2 grid grid-cols-2 gap-2">
                  {/* Health Bar */}
                  <div className="col-span-2">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-dark-200">Health</span>
                      <span className="text-dark-300">{character.currentHealth}/{character.maxHealth}</span>
                    </div>
                    <Progress value={healthPercentage} className="h-2 bg-dark-800" indicatorClassName="bg-danger" />
                  </div>
                  
                  {/* Mana Bar */}
                  <div className="col-span-2">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-dark-200">Mana</span>
                      <span className="text-dark-300">{character.currentMana}/{character.maxMana}</span>
                    </div>
                    <Progress value={manaPercentage} className="h-2 bg-dark-800" indicatorClassName="bg-info" />
                  </div>
                  
                  {/* Core Stats */}
                  <div>
                    <div className="text-xs text-dark-300">Strength</div>
                    <div className="text-dark-100 font-medium">{character.stats.strength}</div>
                  </div>
                  <div>
                    <div className="text-xs text-dark-300">Dexterity</div>
                    <div className="text-dark-100 font-medium">{character.stats.dexterity}</div>
                  </div>
                  <div>
                    <div className="text-xs text-dark-300">Intelligence</div>
                    <div className="text-dark-100 font-medium">{character.stats.intelligence}</div>
                  </div>
                  <div>
                    <div className="text-xs text-dark-300">Charisma</div>
                    <div className="text-dark-100 font-medium">{character.stats.charisma}</div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Inventory Section */}
            <div className="border-b border-dark-600">
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center">
                    <Package className="w-4 h-4 mr-1" />
                    Inventory
                  </h4>
                  <span className="text-xs text-dark-400">{inventory?.currentWeight || 0}/{inventory?.maxWeight || 50} lbs</span>
                </div>
                <div className="mt-2">
                  {inventory?.items && inventory.items.length > 0 ? (
                    <div className="space-y-1">
                      {inventory.items.map((item, index) => (
                        <div key={index} className="flex items-center gap-x-2 py-1 text-sm text-dark-200">
                          <span className="text-xs text-accent-400 font-mono">{item.quantity}×</span>
                          <span>{item.name}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-dark-400 text-sm italic">
                      Your inventory is empty.
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Quests Section */}
            <div className="border-b border-dark-600">
              <div className="p-4">
                <h4 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center">
                  <ScrollText className="w-4 h-4 mr-1" />
                  Quests
                </h4>
                <div className="mt-2">
                  {quests && quests.length > 0 ? (
                    <div className="space-y-2">
                      {quests.map((quest, index) => (
                        <div key={index} className="py-1">
                          <div className="flex items-center gap-x-1">
                            <span className="w-2 h-2 rounded-full bg-accent-500"></span>
                            <h5 className="text-dark-100 font-medium text-sm">{quest.title}</h5>
                          </div>
                          <p className="text-dark-300 text-xs ml-3 mt-1">{quest.description}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-dark-400 text-sm italic">
                      No active quests.
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Dice Roller Section */}
            <div>
              <div className="p-4">
                <h4 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-4 h-4 mr-1">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M14.25 6.087c0-.355.186-.676.401-.959.221-.29.349-.634.349-1.003 0-1.036-1.007-1.875-2.25-1.875s-2.25.84-2.25 1.875c0 .369.128.713.349 1.003.215.283.401.604.401.959v0a.64.64 0 01-.657.643 48.39 48.39 0 01-4.163-.3c.186 1.613.293 3.25.315 4.907a.656.656 0 01-.658.663v0c-.355 0-.676-.186-.959-.401a1.647 1.647 0 00-1.003-.349c-1.036 0-1.875 1.007-1.875 2.25s.84 2.25 1.875 2.25c.369 0 .713-.128 1.003-.349.283-.215.604-.401.959-.401v0c.31 0 .555.26.532.57a48.039 48.039 0 01-.642 5.056c1.518.19 3.058.309 4.616.354a.64.64 0 00.657-.643v0c0-.355-.186-.676-.401-.959a1.647 1.647 0 01-.349-1.003c0-1.035 1.008-1.875 2.25-1.875 1.243 0 2.25.84 2.25 1.875 0 .369-.128.713-.349 1.003-.215.283-.4.604-.4.959v0c0 .333.277.599.61.58a48.1 48.1 0 005.427-.63 48.05 48.05 0 00.582-4.717.532.532 0 00-.533-.57v0c-.355 0-.676.186-.959.401-.29.221-.634.349-1.003.349-1.035 0-1.875-1.007-1.875-2.25s.84-2.25 1.875-2.25c.37 0 .713.128 1.003.349.283.215.604.401.96.401v0a.656.656 0 00.658-.663 48.422 48.422 0 00-.37-5.36c-1.886.342-3.81.574-5.766.689a.578.578 0 01-.61-.58v0z" />
                  </svg>
                  Dice Roller
                </h4>
                <DiceRoller />
              </div>
            </div>
          </div>
        )}
      </aside>
      
      <CharacterCreationModal 
        isOpen={showCharacterCreation} 
        onClose={() => setShowCharacterCreation(false)} 
      />
    </>
  );
}
