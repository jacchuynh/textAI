import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiRequest } from '@/lib/queryClient';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { Icons } from '@/components/ui/icons';

// Domain icons
import { Dumbbell, Brain, Hammer, Eye, Users, Crown, Heart } from 'lucide-react';
import { Flame, Droplet, Mountain, Wind, Sun, Moon, Music } from 'lucide-react';

// Types
interface Domain {
  id: string;
  name: string;
  value: number;
  icon: React.ReactNode;
}

interface CombatMove {
  id: string;
  name: string;
  description: string;
  moveType: string;
  domains: string[];
  baseDamage: number;
  staminaCost: number;
  focusCost: number;
  spiritCost: number;
  effects: string[];
}

interface Combatant {
  id: string;
  name: string;
  description?: string;
  domains: Record<string, number>;
  maxHealth: number;
  currentHealth: number;
  maxStamina: number;
  currentStamina: number;
  maxFocus: number;
  currentFocus: number;
  maxSpirit: number;
  currentSpirit: number;
  image?: string;
}

interface CombatResult {
  actorRoll: number;
  targetRoll: number;
  actorDamageDealt: number;
  actorDamageTaken: number;
  actorOutcome: string;
  targetOutcome: string;
  narrative: string;
  round: number;
}

interface CombatLog {
  type: 'info' | 'attack' | 'result' | 'special' | 'flee' | 'victory' | 'defeat';
  message: string;
  round?: number;
}

// Domain mapping
const domainIcons: Record<string, React.ReactNode> = {
  BODY: <Dumbbell className="h-4 w-4" />,
  MIND: <Brain className="h-4 w-4" />,
  CRAFT: <Hammer className="h-4 w-4" />,
  AWARENESS: <Eye className="h-4 w-4" />,
  SOCIAL: <Users className="h-4 w-4" />,
  AUTHORITY: <Crown className="h-4 w-4" />,
  SPIRIT: <Heart className="h-4 w-4" />,
  FIRE: <Flame className="h-4 w-4" />,
  WATER: <Droplet className="h-4 w-4" />,
  EARTH: <Mountain className="h-4 w-4" />,
  AIR: <Wind className="h-4 w-4" />,
  LIGHT: <Sun className="h-4 w-4" />,
  DARKNESS: <Moon className="h-4 w-4" />,
  SOUND: <Music className="h-4 w-4" />,
};

// Move type colors
const moveTypeColors: Record<string, string> = {
  FORCE: 'bg-red-600',
  FOCUS: 'bg-blue-600',
  TRICK: 'bg-purple-600',
  DEFEND: 'bg-green-600',
  UTILITY: 'bg-yellow-600',
};

// Helper functions
const getDomainColor = (value: number) => {
  if (value >= 8) return 'bg-gradient-to-r from-purple-600 to-indigo-600';
  if (value >= 6) return 'bg-gradient-to-r from-blue-600 to-indigo-500';
  if (value >= 4) return 'bg-gradient-to-r from-blue-500 to-teal-400';
  if (value >= 2) return 'bg-gradient-to-r from-green-500 to-teal-400';
  return 'bg-gray-400';
};

const CombatGame: React.FC = () => {
  const { toast } = useToast();
  const [combatStarted, setCombatStarted] = useState(false);
  const [player, setPlayer] = useState<Combatant | null>(null);
  const [playerMoves, setPlayerMoves] = useState<CombatMove[]>([]);
  const [selectedMove, setSelectedMove] = useState<string | null>(null);
  const [monster, setMonster] = useState<Combatant | null>(null);
  const [monsterMoves, setMonsterMoves] = useState<CombatMove[]>([]);
  const [combatLogs, setCombatLogs] = useState<CombatLog[]>([]);
  const [combatRound, setCombatRound] = useState(1);
  const [diceRolling, setDiceRolling] = useState(false);
  const [playerDiceResult, setPlayerDiceResult] = useState<number | null>(null);
  const [monsterDiceResult, setMonsterDiceResult] = useState<number | null>(null);
  const [gameOver, setGameOver] = useState(false);
  
  const regionChoices = ['Verdant Forest', 'Ember Plains'];
  const [selectedRegion, setSelectedRegion] = useState(regionChoices[0]);
  
  // Mock API functions - these would connect to your Python backend in a real implementation
  const fetchPlayer = async () => {
    // This would be an API call in a real implementation
    const playerData: Combatant = {
      id: 'player-1',
      name: 'Hero',
      domains: {
        BODY: 4,
        MIND: 3,
        CRAFT: 2,
        AWARENESS: 3,
        SOCIAL: 2,
        AUTHORITY: 1,
        SPIRIT: 2,
        FIRE: 1,
        WATER: 1,
        EARTH: 1,
        AIR: 1,
        LIGHT: 1,
        DARKNESS: 1,
        SOUND: 1,
      },
      maxHealth: 50,
      currentHealth: 50,
      maxStamina: 30,
      currentStamina: 30,
      maxFocus: 25,
      currentFocus: 25,
      maxSpirit: 20,
      currentSpirit: 20,
    };
    
    const playerMovesData: CombatMove[] = [
      {
        id: 'move-1',
        name: 'Sword Strike',
        description: 'A basic attack with your sword',
        moveType: 'FORCE',
        domains: ['BODY'],
        baseDamage: 5,
        staminaCost: 2,
        focusCost: 0,
        spiritCost: 0,
        effects: [],
      },
      {
        id: 'move-2',
        name: 'Precise Thrust',
        description: 'A carefully aimed stab seeking a weak point',
        moveType: 'FOCUS',
        domains: ['BODY', 'AWARENESS'],
        baseDamage: 4,
        staminaCost: 1,
        focusCost: 2,
        spiritCost: 0,
        effects: [],
      },
      {
        id: 'move-3',
        name: 'Feint',
        description: 'A deceptive move to catch your opponent off-guard',
        moveType: 'TRICK',
        domains: ['MIND', 'BODY'],
        baseDamage: 3,
        staminaCost: 1,
        focusCost: 1,
        spiritCost: 1,
        effects: [],
      },
      {
        id: 'move-4',
        name: 'Defensive Stance',
        description: 'Adopt a defensive posture to ward off attacks',
        moveType: 'DEFEND',
        domains: ['BODY'],
        baseDamage: 1,
        staminaCost: 1,
        focusCost: 1,
        spiritCost: 0,
        effects: [],
      },
      {
        id: 'move-5',
        name: 'Battle Meditation',
        description: 'A quick focusing technique to recover your spirit and focus',
        moveType: 'UTILITY',
        domains: ['MIND', 'SPIRIT'],
        baseDamage: 0,
        staminaCost: 0,
        focusCost: 0,
        spiritCost: 1,
        effects: ['Recover 5 focus and 5 spirit'],
      },
    ];
    
    return { player: playerData, moves: playerMovesData };
  };

  const fetchMonster = async (region: string, tier: string = 'STANDARD') => {
    // In a real implementation, this would call your backend to get a monster from the YAML files
    const isVerdant = region.includes('Verdant');
    const isElite = Math.random() > 0.8; // 20% chance for an elite monster
    
    let monsterData: Combatant;
    let monsterMovesData: CombatMove[];
    
    if (isVerdant) {
      if (isElite) {
        // Moss Guardian (Elite from Verdant)
        monsterData = {
          id: 'monster-1',
          name: 'Moss Guardian',
          description: 'A humanoid figure composed entirely of moss, lichen, and small plants. It protects sacred groves from intruders.',
          domains: {
            BODY: 5,
            MIND: 1,
            CRAFT: 2,
            AWARENESS: 3,
            SOCIAL: 2,
            AUTHORITY: 2,
            SPIRIT: 5,
            FIRE: 1,
            WATER: 3,
            EARTH: 6,
            AIR: 2,
            LIGHT: 2,
            DARKNESS: 2,
            SOUND: 2,
          },
          maxHealth: 75,
          currentHealth: 75,
          maxStamina: 40,
          currentStamina: 40,
          maxFocus: 30,
          currentFocus: 30,
          maxSpirit: 40,
          currentSpirit: 40,
        };
        
        monsterMovesData = [
          {
            id: 'monster-move-1',
            name: 'Moss Slam',
            description: 'A powerful slam attack using mossy limbs',
            moveType: 'FORCE',
            domains: ['BODY'],
            baseDamage: 7,
            staminaCost: 3,
            focusCost: 0,
            spiritCost: 0,
            effects: [],
          },
          {
            id: 'monster-move-2',
            name: 'Root Grab',
            description: 'Tangles the target in root systems from the ground',
            moveType: 'TRICK',
            domains: ['EARTH'],
            baseDamage: 4,
            staminaCost: 2,
            focusCost: 2,
            spiritCost: 0,
            effects: ['May entangle opponent'],
          },
          {
            id: 'monster-move-3',
            name: 'Sacred Ward',
            description: 'Calls upon forest spirits for protection',
            moveType: 'DEFEND',
            domains: ['SPIRIT'],
            baseDamage: 0,
            staminaCost: 1,
            focusCost: 0,
            spiritCost: 3,
            effects: ['Increases defense'],
          },
          {
            id: 'monster-move-4',
            name: 'Rejuvenation',
            description: 'Heals when standing in sunlight',
            moveType: 'UTILITY',
            domains: ['SPIRIT', 'EARTH'],
            baseDamage: 0,
            staminaCost: 0, 
            focusCost: 2,
            spiritCost: 2,
            effects: ['Recovers health'],
          },
        ];
      } else {
        // Vine Weasel (Standard from Verdant)
        monsterData = {
          id: 'monster-2',
          name: 'Vine Weasel',
          description: 'A small, quick creature with vines growing from its fur. It uses these vines to ensnare prey and swing through the forest canopy.',
          domains: {
            BODY: 4,
            MIND: 2,
            CRAFT: 2,
            AWARENESS: 3,
            SOCIAL: 2,
            AUTHORITY: 2,
            SPIRIT: 2,
            FIRE: 2,
            WATER: 2,
            EARTH: 3,
            AIR: 2,
            LIGHT: 2,
            DARKNESS: 2,
            SOUND: 2,
          },
          maxHealth: 30,
          currentHealth: 30,
          maxStamina: 25,
          currentStamina: 25,
          maxFocus: 20,
          currentFocus: 20,
          maxSpirit: 15,
          currentSpirit: 15,
        };
        
        monsterMovesData = [
          {
            id: 'monster-move-1',
            name: 'Vine Whip',
            description: 'Lashes out with vine tendrils',
            moveType: 'FORCE',
            domains: ['EARTH'],
            baseDamage: 4,
            staminaCost: 2,
            focusCost: 0,
            spiritCost: 0,
            effects: ['May entangle opponent'],
          },
          {
            id: 'monster-move-2',
            name: 'Quick Bite',
            description: 'A rapid bite attack',
            moveType: 'FORCE',
            domains: ['BODY'],
            baseDamage: 3,
            staminaCost: 1,
            focusCost: 0,
            spiritCost: 0,
            effects: [],
          },
          {
            id: 'monster-move-3',
            name: 'Forest Camouflage',
            description: 'Blends into the surroundings',
            moveType: 'DEFEND',
            domains: ['AWARENESS'],
            baseDamage: 0,
            staminaCost: 1,
            focusCost: 2,
            spiritCost: 0,
            effects: ['Harder to hit'],
          },
          {
            id: 'monster-move-4',
            name: 'Regrowth',
            description: 'Regenerates health when in contact with soil',
            moveType: 'UTILITY',
            domains: ['BODY', 'EARTH'],
            baseDamage: 0,
            staminaCost: 0,
            focusCost: 1,
            spiritCost: 2,
            effects: ['Recovers health'],
          },
        ];
      }
    } else {
      // Ember region monsters
      if (isElite) {
        // Flameshell Tortoise (Elite from Ember)
        monsterData = {
          id: 'monster-3',
          name: 'Flameshell Tortoise',
          description: 'A large tortoise with a shell made of hardened volcanic rock. Cracks in its shell reveal the molten core within.',
          domains: {
            BODY: 5,
            MIND: 2,
            CRAFT: 2,
            AWARENESS: 1,
            SOCIAL: 1,
            AUTHORITY: 2,
            SPIRIT: 3,
            FIRE: 6,
            WATER: 1,
            EARTH: 5,
            AIR: 1,
            LIGHT: 2,
            DARKNESS: 2,
            SOUND: 1,
          },
          maxHealth: 85,
          currentHealth: 85,
          maxStamina: 35,
          currentStamina: 35,
          maxFocus: 20,
          currentFocus: 20,
          maxSpirit: 25,
          currentSpirit: 25,
        };
        
        monsterMovesData = [
          {
            id: 'monster-move-1',
            name: 'Magma Shell',
            description: 'Superheats its shell to damage attackers',
            moveType: 'DEFEND',
            domains: ['EARTH', 'FIRE'],
            baseDamage: 3,
            staminaCost: 1,
            focusCost: 0,
            spiritCost: 2,
            effects: ['Damages attackers'],
          },
          {
            id: 'monster-move-2',
            name: 'Flame Breath',
            description: 'Exhales a jet of intense flame',
            moveType: 'FOCUS',
            domains: ['FIRE'],
            baseDamage: 7,
            staminaCost: 2,
            focusCost: 3,
            spiritCost: 0,
            effects: ['May cause burning'],
          },
          {
            id: 'monster-move-3',
            name: 'Shell Slam',
            description: 'Rams the target with its heavy shell',
            moveType: 'FORCE',
            domains: ['BODY'],
            baseDamage: 6,
            staminaCost: 3,
            focusCost: 0,
            spiritCost: 0,
            effects: [],
          },
          {
            id: 'monster-move-4',
            name: 'Molten Core',
            description: 'When injured, releases gouts of lava',
            moveType: 'UTILITY',
            domains: ['FIRE', 'EARTH'],
            baseDamage: 4,
            staminaCost: 0,
            focusCost: 0,
            spiritCost: 3,
            effects: ['Area damage'],
          },
        ];
      } else {
        // Cinderwolf (Standard from Ember)
        monsterData = {
          id: 'monster-4',
          name: 'Cinderwolf',
          description: 'A wolf-like predator with fur that glows like embers. It leaves small flames in its footprints and hunts in packs.',
          domains: {
            BODY: 4,
            MIND: 2,
            CRAFT: 1,
            AWARENESS: 3,
            SOCIAL: 2,
            AUTHORITY: 1,
            SPIRIT: 2,
            FIRE: 4,
            WATER: 1,
            EARTH: 2,
            AIR: 2,
            LIGHT: 2,
            DARKNESS: 2,
            SOUND: 2,
          },
          maxHealth: 35,
          currentHealth: 35,
          maxStamina: 25,
          currentStamina: 25,
          maxFocus: 20,
          currentFocus: 20,
          maxSpirit: 15,
          currentSpirit: 15,
        };
        
        monsterMovesData = [
          {
            id: 'monster-move-1',
            name: 'Ember Bite',
            description: 'A bite attack infused with fire',
            moveType: 'FORCE',
            domains: ['FIRE', 'BODY'],
            baseDamage: 5,
            staminaCost: 2,
            focusCost: 0,
            spiritCost: 0,
            effects: ['May cause burning'],
          },
          {
            id: 'monster-move-2',
            name: 'Pack Hunt',
            description: 'Uses pack tactics to outmaneuver prey',
            moveType: 'TRICK',
            domains: ['BODY', 'AWARENESS'],
            baseDamage: 3,
            staminaCost: 1,
            focusCost: 2,
            spiritCost: 0,
            effects: ['Harder to defend against'],
          },
          {
            id: 'monster-move-3',
            name: 'Heat Sense',
            description: 'Detects body heat to track prey',
            moveType: 'FOCUS',
            domains: ['AWARENESS', 'FIRE'],
            baseDamage: 2,
            staminaCost: 0,
            focusCost: 3,
            spiritCost: 0,
            effects: ['Increases accuracy'],
          },
          {
            id: 'monster-move-4',
            name: 'Fire Trail',
            description: 'Leaves a trail of fire when running at full speed',
            moveType: 'UTILITY',
            domains: ['FIRE'],
            baseDamage: 3,
            staminaCost: 3,
            focusCost: 0,
            spiritCost: 1,
            effects: ['Area damage'],
          },
        ];
      }
    }
    
    return { monster: monsterData, moves: monsterMovesData };
  };

  const resolveCombatExchange = async (playerMoveId: string) => {
    if (!player || !monster) return null;
    
    const playerMove = playerMoves.find(m => m.id === playerMoveId);
    if (!playerMove) return null;
    
    // Check if player has enough resources
    if (
      player.currentStamina < playerMove.staminaCost ||
      player.currentFocus < playerMove.focusCost ||
      player.currentSpirit < playerMove.spiritCost
    ) {
      toast({
        title: "Not enough resources!",
        description: `You need more ${playerMove.staminaCost > player.currentStamina ? 'stamina' : 
          playerMove.focusCost > player.currentFocus ? 'focus' : 'spirit'} to use this move.`,
        variant: "destructive"
      });
      return null;
    }
    
    // Randomly select a monster move
    const validMonsterMoves = monsterMoves.filter(m => 
      monster.currentStamina >= m.staminaCost &&
      monster.currentFocus >= m.focusCost &&
      monster.currentSpirit >= m.spiritCost
    );
    
    if (validMonsterMoves.length === 0) {
      // Monster has no valid moves
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `${monster.name} is too exhausted to continue fighting!`,
        round: combatRound
      }]);
      
      setGameOver(true);
      setCombatLogs(prev => [...prev, {
        type: 'victory',
        message: `Victory! You have defeated the ${monster.name}!`,
        round: combatRound
      }]);
      
      return null;
    }
    
    const monsterMove = validMonsterMoves[Math.floor(Math.random() * validMonsterMoves.length)];
    
    // Log the moves
    setCombatLogs(prev => [...prev, {
      type: 'info',
      message: `Round ${combatRound}: You use ${playerMove.name}!`,
      round: combatRound
    }]);
    
    setCombatLogs(prev => [...prev, {
      type: 'info',
      message: `${monster.name} responds with ${monsterMove.name}!`,
      round: combatRound
    }]);
    
    // Apply resource costs
    const updatedPlayer = { 
      ...player,
      currentStamina: player.currentStamina - playerMove.staminaCost,
      currentFocus: player.currentFocus - playerMove.focusCost,
      currentSpirit: player.currentSpirit - playerMove.spiritCost
    };
    
    const updatedMonster = {
      ...monster,
      currentStamina: monster.currentStamina - monsterMove.staminaCost,
      currentFocus: monster.currentFocus - monsterMove.focusCost,
      currentSpirit: monster.currentSpirit - monsterMove.spiritCost
    };
    
    // Special handling for Battle Meditation
    if (playerMove.name === 'Battle Meditation') {
      updatedPlayer.currentFocus = Math.min(updatedPlayer.maxFocus, updatedPlayer.currentFocus + 5);
      updatedPlayer.currentSpirit = Math.min(updatedPlayer.maxSpirit, updatedPlayer.currentSpirit + 5);
      
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `You recover focus and spirit through meditation.`,
        round: combatRound
      }]);
    }
    
    // Special handling for Regrowth
    if (monsterMove.name === 'Regrowth') {
      const healAmount = Math.floor(monsterMove.baseDamage + Math.random() * 3);
      updatedMonster.currentHealth = Math.min(updatedMonster.maxHealth, updatedMonster.currentHealth + healAmount);
      
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `${monster.name} recovers ${healAmount} health through ${monsterMove.name}.`,
        round: combatRound
      }]);
    }
    
    // Roll dice
    setDiceRolling(true);
    await new Promise(resolve => setTimeout(resolve, 1000));  // Simulate dice rolling animation
    
    const playerRoll = Math.floor(Math.random() * 20) + 1;  // 1-20
    const monsterRoll = Math.floor(Math.random() * 20) + 1;  // 1-20
    
    setPlayerDiceResult(playerRoll);
    setMonsterDiceResult(monsterRoll);
    
    // Calculate domain bonus
    const getAverageDomainValue = (combatant: Combatant, move: CombatMove) => {
      if (move.domains.length === 0) return 1.0;
      
      let totalValue = 0;
      for (const domain of move.domains) {
        totalValue += combatant.domains[domain] || 0;
      }
      
      const avgValue = totalValue / move.domains.length;
      return 0.8 + (Math.min(10, avgValue) * 0.12);  // From 0.8 to 2.0 based on domain value
    };
    
    const playerDomainBonus = getAverageDomainValue(player, playerMove);
    const monsterDomainBonus = getAverageDomainValue(monster, monsterMove);
    
    // Calculate base damage
    let playerBaseDamage = Math.floor(playerMove.baseDamage * playerDomainBonus) + Math.floor(playerRoll / 5);
    let monsterBaseDamage = Math.floor(monsterMove.baseDamage * monsterDomainBonus) + Math.floor(monsterRoll / 5);
    
    // Apply move type advantages
    if (playerMove.moveType === 'FORCE' && monsterMove.moveType === 'DEFEND') {
      // Defense reduces damage
      playerBaseDamage = Math.max(0, playerBaseDamage - 3);
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `${monster.name}'s ${monsterMove.name} reduces incoming damage!`,
        round: combatRound
      }]);
    } else if (playerMove.moveType === 'FOCUS' && monsterMove.moveType === 'FORCE') {
      // Focus beats force
      playerBaseDamage += 2;
      monsterBaseDamage -= 1;
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `Your focused attack counters ${monster.name}'s forceful approach!`,
        round: combatRound
      }]);
    } else if (playerMove.moveType === 'TRICK' && monsterMove.moveType === 'FOCUS') {
      // Tricks work well against focus
      playerBaseDamage += 2;
      monsterBaseDamage -= 1;
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `Your trickery disrupts ${monster.name}'s concentration!`,
        round: combatRound
      }]);
    } else if (playerMove.moveType === 'DEFEND' && monsterMove.moveType === 'TRICK') {
      // Defense works well against tricks
      playerBaseDamage -= 1;
      monsterBaseDamage -= 2;
      setCombatLogs(prev => [...prev, {
        type: 'special',
        message: `Your defenses are tough to trick!`,
        round: combatRound
      }]);
    }
    
    // Calculate final damage
    const playerDamage = Math.max(0, playerBaseDamage);
    const monsterDamage = Math.max(0, monsterBaseDamage);
    
    // Apply damage
    updatedPlayer.currentHealth = Math.max(0, updatedPlayer.currentHealth - monsterDamage);
    updatedMonster.currentHealth = Math.max(0, updatedMonster.currentHealth - playerDamage);
    
    // Generate outcome descriptions
    const getOutcomeDescription = (name: string, damageDealt: number, damageTaken: number) => {
      if (damageDealt > damageTaken * 2) {
        return `${name} overwhelmed their opponent`;
      } else if (damageDealt > damageTaken) {
        return `${name} gained the upper hand`;
      } else if (damageDealt === damageTaken) {
        return `${name} traded blows evenly`;
      } else if (damageTaken > damageDealt * 2) {
        return `${name} was overwhelmed`;
      } else {
        return `${name} was at a disadvantage`;
      }
    };
    
    const playerOutcome = getOutcomeDescription(player.name, playerDamage, monsterDamage);
    const monsterOutcome = getOutcomeDescription(monster.name, monsterDamage, playerDamage);
    
    // Generate narrative
    const narrativeTemplates = [
      `You used ${playerMove.name}, while ${monster.name} responded with ${monsterMove.name}. The exchange ended with you dealing ${playerDamage} damage and taking ${monsterDamage} damage.`,
      `As you unleashed ${playerMove.name}, ${monster.name} countered with ${monsterMove.name}. You inflicted ${playerDamage} damage, while suffering ${monsterDamage} in return.`,
      `Your ${playerMove.name} clashed with ${monster.name}'s ${monsterMove.name} in the ${selectedRegion}. When the dust settled, you had dealt ${playerDamage} damage and received ${monsterDamage}.`
    ];
    
    // Add special narration for high and low damage scenarios
    if (playerDamage > 8) {
      narrativeTemplates.push(
        `You executed a powerful ${playerMove.name}, catching ${monster.name} off guard despite their ${monsterMove.name}. The devastating attack dealt ${playerDamage} damage while you only suffered ${monsterDamage} in return.`
      );
    }
    
    if (playerDamage < 3 && monsterDamage > 5) {
      narrativeTemplates.push(
        `You struggled while attempting ${playerMove.name}, giving ${monster.name} an opening with ${monsterMove.name}. The mistake resulted in only ${playerDamage} damage dealt while taking ${monsterDamage} damage.`
      );
    }
    
    const narrative = narrativeTemplates[Math.floor(Math.random() * narrativeTemplates.length)];
    
    // Add combat result to log
    setCombatLogs(prev => [...prev, {
      type: 'result',
      message: narrative,
      round: combatRound
    }]);
    
    // Check for victory/defeat
    if (updatedMonster.currentHealth <= 0) {
      updatedMonster.currentHealth = 0;
      setGameOver(true);
      setCombatLogs(prev => [...prev, {
        type: 'victory',
        message: `Victory! You have defeated the ${monster.name}!`,
        round: combatRound
      }]);
    }
    
    if (updatedPlayer.currentHealth <= 0) {
      updatedPlayer.currentHealth = 0;
      setGameOver(true);
      setCombatLogs(prev => [...prev, {
        type: 'defeat',
        message: `Defeat! The ${monster.name} has bested you in combat.`,
        round: combatRound
      }]);
    }
    
    // Update state
    setPlayer(updatedPlayer);
    setMonster(updatedMonster);
    setCombatRound(prev => prev + 1);
    setDiceRolling(false);
    
    // Resource recovery each round
    if (!gameOver) {
      const recoveredPlayer = {
        ...updatedPlayer,
        currentStamina: Math.min(updatedPlayer.maxStamina, updatedPlayer.currentStamina + 2),
        currentFocus: Math.min(updatedPlayer.maxFocus, updatedPlayer.currentFocus + 1),
        currentSpirit: Math.min(updatedPlayer.maxSpirit, updatedPlayer.currentSpirit + 1)
      };
      
      const recoveredMonster = {
        ...updatedMonster,
        currentStamina: Math.min(updatedMonster.maxStamina, updatedMonster.currentStamina + 2),
        currentFocus: Math.min(updatedMonster.maxFocus, updatedMonster.currentFocus + 1),
        currentSpirit: Math.min(updatedMonster.maxSpirit, updatedMonster.currentSpirit + 1)
      };
      
      // Delay the recovery update to make it feel more natural
      setTimeout(() => {
        setPlayer(recoveredPlayer);
        setMonster(recoveredMonster);
      }, 2000);
    }
    
    const result: CombatResult = {
      actorRoll: playerRoll,
      targetRoll: monsterRoll,
      actorDamageDealt: playerDamage,
      actorDamageTaken: monsterDamage,
      actorOutcome: playerOutcome,
      targetOutcome: monsterOutcome,
      narrative,
      round: combatRound
    };
    
    return result;
  };

  const attemptToFlee = async () => {
    if (!player || !monster) return;
    
    setCombatLogs(prev => [...prev, {
      type: 'flee',
      message: `You attempt to flee from the ${monster.name}!`,
      round: combatRound
    }]);
    
    // Roll for fleeing success
    setDiceRolling(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const fleeRoll = Math.floor(Math.random() * 20) + 1;
    const awarenessBonus = player.domains.AWARENESS || 0;
    const fleeSuccess = fleeRoll + awarenessBonus >= 15;
    
    setPlayerDiceResult(fleeRoll);
    setMonsterDiceResult(null);
    setDiceRolling(false);
    
    if (fleeSuccess) {
      setCombatLogs(prev => [...prev, {
        type: 'flee',
        message: `You successfully escape from the ${monster.name}!`,
        round: combatRound
      }]);
      
      setGameOver(true);
    } else {
      setCombatLogs(prev => [...prev, {
        type: 'flee',
        message: `You fail to escape! The ${monster.name} blocks your path!`,
        round: combatRound
      }]);
      
      // Monster gets a free attack
      const validMonsterMoves = monsterMoves.filter(m => 
        m.moveType === 'FORCE' && 
        monster.currentStamina >= m.staminaCost
      );
      
      const monsterAttack = validMonsterMoves.length > 0 
        ? validMonsterMoves[Math.floor(Math.random() * validMonsterMoves.length)]
        : monsterMoves[Math.floor(Math.random() * monsterMoves.length)];
      
      const domainBonus = monster.domains[monsterAttack.domains[0]] || 1;
      const baseDamage = Math.floor(monsterAttack.baseDamage * (0.8 + (Math.min(10, domainBonus) * 0.12)));
      
      const updatedPlayer = {
        ...player,
        currentHealth: Math.max(0, player.currentHealth - baseDamage)
      };
      
      setCombatLogs(prev => [...prev, {
        type: 'attack',
        message: `The ${monster.name} catches you as you try to flee and deals ${baseDamage} damage with ${monsterAttack.name}!`,
        round: combatRound
      }]);
      
      setPlayer(updatedPlayer);
      
      if (updatedPlayer.currentHealth <= 0) {
        setGameOver(true);
        setCombatLogs(prev => [...prev, {
          type: 'defeat',
          message: `Defeat! The ${monster.name} has struck you down as you tried to flee.`,
          round: combatRound
        }]);
      }
    }
    
    setCombatRound(prev => prev + 1);
  };

  const startCombat = async () => {
    try {
      setCombatLogs([]);
      setDiceRolling(false);
      setPlayerDiceResult(null);
      setMonsterDiceResult(null);
      setCombatRound(1);
      setGameOver(false);
      
      // Fetch player data
      const playerData = await fetchPlayer();
      setPlayer(playerData.player);
      setPlayerMoves(playerData.moves);
      
      // Fetch monster data based on selected region
      const monsterData = await fetchMonster(selectedRegion);
      setMonster(monsterData.monster);
      setMonsterMoves(monsterData.moves);
      
      setCombatStarted(true);
      
      // Add initial log entry
      setCombatLogs([
        {
          type: 'info',
          message: `You've encountered a ${monsterData.monster.name} in the ${selectedRegion}!`,
          round: 0
        },
        {
          type: 'info',
          message: monsterData.monster.description || `The ${monsterData.monster.name} looks dangerous!`,
          round: 0
        }
      ]);
    } catch (error) {
      console.error("Error starting combat:", error);
      toast({
        title: "Error",
        description: "Failed to start combat. Please try again.",
        variant: "destructive"
      });
    }
  };

  const restartCombat = () => {
    setCombatStarted(false);
    setGameOver(false);
    setPlayer(null);
    setMonster(null);
    setPlayerMoves([]);
    setMonsterMoves([]);
    setCombatLogs([]);
  };

  const CombatLogItem = ({ log }: { log: CombatLog }) => {
    let bgColor = 'bg-gray-800';
    let textColor = 'text-white';
    
    switch (log.type) {
      case 'info':
        bgColor = 'bg-gray-800';
        break;
      case 'attack':
        bgColor = 'bg-red-900';
        break;
      case 'result':
        bgColor = 'bg-blue-900';
        break;
      case 'special':
        bgColor = 'bg-purple-900';
        break;
      case 'flee':
        bgColor = 'bg-yellow-900';
        textColor = 'text-gray-100';
        break;
      case 'victory':
        bgColor = 'bg-green-900';
        break;
      case 'defeat':
        bgColor = 'bg-red-950';
        break;
    }
    
    return (
      <div className={`p-2 mb-2 rounded ${bgColor} ${textColor}`}>
        {log.round !== undefined && log.round > 0 && (
          <Badge variant="outline" className="mr-2">Round {log.round}</Badge>
        )}
        {log.message}
      </div>
    );
  };

  const DomainList = ({ combatant }: { combatant: Combatant }) => {
    const domainList = Object.entries(combatant.domains).map(([domainKey, value]) => ({
      id: domainKey,
      name: domainKey.charAt(0) + domainKey.slice(1).toLowerCase(),
      value,
      icon: domainIcons[domainKey] || <div className="h-4 w-4" />
    }));
    
    // Sort domains by value
    domainList.sort((a, b) => b.value - a.value);
    
    return (
      <div className="grid grid-cols-2 gap-2">
        {domainList.map(domain => (
          <TooltipProvider key={domain.id}>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-2">
                  <div className={`w-1 h-5 ${getDomainColor(domain.value)}`} />
                  <div className="font-bold w-5 h-5 flex items-center justify-center">
                    {domain.icon}
                  </div>
                  <div className="text-sm">{domain.name}</div>
                  <div className="ml-auto font-bold">{domain.value}</div>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>{domain.name} domain value: {domain.value}</p>
                {domain.value >= 8 && <p>Paragon level</p>}
                {domain.value >= 6 && domain.value < 8 && <p>Master level</p>}
                {domain.value >= 4 && domain.value < 6 && <p>Expert level</p>}
                {domain.value >= 3 && domain.value < 4 && <p>Skilled level</p>}
                {domain.value < 3 && <p>Novice level</p>}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ))}
      </div>
    );
  };

  const MoveList = ({ moves, onSelectMove, selectedMove, disabled }: { 
    moves: CombatMove[], 
    onSelectMove: (moveId: string) => void, 
    selectedMove: string | null,
    disabled: boolean
  }) => {
    return (
      <div className="space-y-2">
        {moves.map(move => {
          const moveSelected = selectedMove === move.id;
          const moveAvailable = !disabled && (
            player?.currentStamina >= move.staminaCost &&
            player?.currentFocus >= move.focusCost &&
            player?.currentSpirit >= move.spiritCost
          );
          
          return (
            <div
              key={move.id}
              className={`p-2 rounded cursor-pointer transition-all ${
                moveSelected ? 'ring-2 ring-blue-500' : ''
              } ${
                moveAvailable ? 'hover:bg-gray-700' : 'opacity-50 cursor-not-allowed'
              } ${
                moveAvailable ? 'bg-gray-800' : 'bg-gray-900'
              }`}
              onClick={() => moveAvailable && onSelectMove(move.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge className={moveTypeColors[move.moveType]}>{move.moveType.charAt(0) + move.moveType.slice(1).toLowerCase()}</Badge>
                  <span className="font-bold">{move.name}</span>
                </div>
                <div className="flex items-center gap-1 text-sm">
                  {move.staminaCost > 0 && (
                    <Badge variant="outline" className="text-yellow-400">
                      {move.staminaCost} STA
                    </Badge>
                  )}
                  {move.focusCost > 0 && (
                    <Badge variant="outline" className="text-blue-400">
                      {move.focusCost} FOC
                    </Badge>
                  )}
                  {move.spiritCost > 0 && (
                    <Badge variant="outline" className="text-purple-400">
                      {move.spiritCost} SPR
                    </Badge>
                  )}
                </div>
              </div>
              <div className="text-sm text-gray-400">{move.description}</div>
              
              <div className="mt-1 flex flex-wrap gap-1">
                {move.domains.map(domain => (
                  <Badge key={domain} variant="secondary" className="text-xs">
                    {domain.charAt(0) + domain.slice(1).toLowerCase()}
                  </Badge>
                ))}
                
                {move.baseDamage > 0 && (
                  <Badge variant="destructive" className="text-xs">
                    {move.baseDamage} Damage
                  </Badge>
                )}
                
                {move.effects.map((effect, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {effect}
                  </Badge>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const DiceDisplay = ({ roll, label }: { roll: number | null, label: string }) => {
    if (roll === null) return null;
    
    let rollQuality = 'normal';
    if (roll >= 18) rollQuality = 'critical';
    else if (roll >= 15) rollQuality = 'great';
    else if (roll <= 3) rollQuality = 'fumble';
    else if (roll <= 6) rollQuality = 'poor';
    
    const qualityColors = {
      critical: 'text-green-500 animate-pulse',
      great: 'text-green-400',
      normal: 'text-white',
      poor: 'text-red-300',
      fumble: 'text-red-500 animate-pulse'
    };
    
    return (
      <div className="text-center">
        <div className="text-sm text-gray-400">{label}</div>
        <div className={`text-2xl font-bold ${qualityColors[rollQuality]}`}>{roll}</div>
      </div>
    );
  };

  if (!combatStarted) {
    return (
      <div className="container mx-auto p-4 max-w-4xl">
        <div className="space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500">
                Crimson Accord Combat
              </span>
            </h1>
            <p className="text-lg text-gray-400">
              Test your skills in domain-based combat against fearsome creatures
            </p>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Select Combat Region</CardTitle>
              <CardDescription>Choose where your battle will take place</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue={selectedRegion} onValueChange={setSelectedRegion}>
                <TabsList className="grid w-full grid-cols-2">
                  {regionChoices.map(region => (
                    <TabsTrigger key={region} value={region}>
                      {region}
                    </TabsTrigger>
                  ))}
                </TabsList>
                <TabsContent value="Verdant Forest" className="mt-4">
                  <div className="flex gap-4">
                    <div className="w-1/3 h-48 bg-gradient-to-b from-green-900 to-green-700 rounded-md flex items-center justify-center">
                      <Icons.forest className="w-24 h-24 text-green-300" />
                    </div>
                    <div className="w-2/3">
                      <h3 className="text-xl font-bold mb-2">Verdant Forest</h3>
                      <p className="text-gray-400 mb-4">
                        Lush, vibrant forests teeming with life. Home to plant-based creatures and beasts that have adapted to the dense foliage. The environment might provide cover, healing properties, or entangling hazards.
                      </p>
                      <p className="text-gray-500 text-sm">
                        Typical monsters: Vine Weasel, Moss Guardian, Dusk Stalker, Whispering Willow
                      </p>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="Ember Plains" className="mt-4">
                  <div className="flex gap-4">
                    <div className="w-1/3 h-48 bg-gradient-to-b from-red-900 to-orange-700 rounded-md flex items-center justify-center">
                      <Icons.fire className="w-24 h-24 text-orange-300" />
                    </div>
                    <div className="w-2/3">
                      <h3 className="text-xl font-bold mb-2">Ember Plains</h3>
                      <p className="text-gray-400 mb-4">
                        Scorched landscapes dotted with volcanic activity. Creatures here are adapted to extreme heat and often use fire in their attacks. The environment might include lava pools, heat vents, or ashen terrain.
                      </p>
                      <p className="text-gray-500 text-sm">
                        Typical monsters: Cinderwolf, Flameshell Tortoise, Ashweaver, Molten Monarch
                      </p>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
            <CardFooter>
              <Button 
                className="w-full" 
                onClick={startCombat}
                disabled={!selectedRegion}
              >
                Begin Combat
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      {/* Combat Arena */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Left column - Player */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle>
              {player?.name}
            </CardTitle>
            <div className="space-y-1">
              {/* Health bar */}
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Health</span>
                <span className="text-sm text-gray-400">
                  {player?.currentHealth}/{player?.maxHealth}
                </span>
              </div>
              <Progress value={(player?.currentHealth / player?.maxHealth) * 100} className="h-2 bg-gray-700">
                <div className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-md" />
              </Progress>
              
              {/* Resources */}
              <div className="grid grid-cols-3 gap-2 mt-2">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">Stamina</span>
                    <span className="text-xs text-gray-400">{player?.currentStamina}/{player?.maxStamina}</span>
                  </div>
                  <Progress value={(player?.currentStamina / player?.maxStamina) * 100} className="h-1.5 bg-gray-700">
                    <div className="h-full bg-yellow-500 rounded-md" />
                  </Progress>
                </div>
                
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">Focus</span>
                    <span className="text-xs text-gray-400">{player?.currentFocus}/{player?.maxFocus}</span>
                  </div>
                  <Progress value={(player?.currentFocus / player?.maxFocus) * 100} className="h-1.5 bg-gray-700">
                    <div className="h-full bg-blue-500 rounded-md" />
                  </Progress>
                </div>
                
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">Spirit</span>
                    <span className="text-xs text-gray-400">{player?.currentSpirit}/{player?.maxSpirit}</span>
                  </div>
                  <Progress value={(player?.currentSpirit / player?.maxSpirit) * 100} className="h-1.5 bg-gray-700">
                    <div className="h-full bg-purple-500 rounded-md" />
                  </Progress>
                </div>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="pb-2">
            <Accordion type="single" collapsible defaultValue="domains">
              <AccordionItem value="domains">
                <AccordionTrigger>Domains</AccordionTrigger>
                <AccordionContent>
                  {player && <DomainList combatant={player} />}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
          
          <CardFooter className="flex flex-col space-y-4">
            <div className="w-full">
              <h3 className="font-semibold mb-2">Combat Moves</h3>
              <MoveList 
                moves={playerMoves} 
                onSelectMove={setSelectedMove} 
                selectedMove={selectedMove} 
                disabled={diceRolling || gameOver}
              />
            </div>
            
            <div className="flex justify-between w-full gap-2">
              <Button
                variant="outline"
                className="w-1/2"
                onClick={attemptToFlee}
                disabled={diceRolling || gameOver || combatRound < 3}
              >
                {combatRound < 3 ? `Flee (Round ${combatRound}/3)` : 'Attempt to Flee'}
              </Button>
              
              <Button
                disabled={!selectedMove || diceRolling || gameOver}
                className="w-1/2"
                onClick={() => selectedMove && resolveCombatExchange(selectedMove)}
              >
                Execute Move
              </Button>
            </div>
            
            {gameOver && (
              <Button
                variant="secondary"
                className="w-full"
                onClick={restartCombat}
              >
                New Combat
              </Button>
            )}
          </CardFooter>
        </Card>
        
        {/* Middle column - Combat log */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="flex justify-between items-center">
              <span>Combat Log</span>
              <Badge variant="outline">Round {combatRound}</Badge>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="h-[600px] overflow-hidden">
            {diceRolling ? (
              <div className="flex flex-col items-center justify-center h-full space-y-4">
                <div className="text-2xl font-bold animate-pulse">Rolling dice...</div>
                <div className="bg-gray-800 p-6 rounded-md flex items-center justify-center">
                  <div className="animate-spin text-6xl">🎲</div>
                </div>
              </div>
            ) : (
              <>
                {playerDiceResult !== null && monsterDiceResult !== null && (
                  <div className="bg-gray-800 p-3 mb-4 rounded-md flex justify-around">
                    <DiceDisplay roll={playerDiceResult} label="Your Roll" />
                    <DiceDisplay roll={monsterDiceResult} label="Monster Roll" />
                  </div>
                )}
                
                <ScrollArea className="h-[530px] pr-4">
                  <div className="space-y-1">
                    {combatLogs.map((log, index) => (
                      <CombatLogItem key={index} log={log} />
                    ))}
                  </div>
                </ScrollArea>
              </>
            )}
          </CardContent>
        </Card>
        
        {/* Right column - Monster */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle>
              {monster?.name}
            </CardTitle>
            <div className="space-y-1">
              {/* Health bar */}
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Health</span>
                <span className="text-sm text-gray-400">
                  {monster?.currentHealth}/{monster?.maxHealth}
                </span>
              </div>
              <Progress value={(monster?.currentHealth / monster?.maxHealth) * 100} className="h-2 bg-gray-700">
                <div className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-md" />
              </Progress>
              
              {/* Resources */}
              <div className="grid grid-cols-3 gap-2 mt-2">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">Stamina</span>
                    <span className="text-xs text-gray-400">{monster?.currentStamina}/{monster?.maxStamina}</span>
                  </div>
                  <Progress value={(monster?.currentStamina / monster?.maxStamina) * 100} className="h-1.5 bg-gray-700">
                    <div className="h-full bg-yellow-500 rounded-md" />
                  </Progress>
                </div>
                
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">Focus</span>
                    <span className="text-xs text-gray-400">{monster?.currentFocus}/{monster?.maxFocus}</span>
                  </div>
                  <Progress value={(monster?.currentFocus / monster?.maxFocus) * 100} className="h-1.5 bg-gray-700">
                    <div className="h-full bg-blue-500 rounded-md" />
                  </Progress>
                </div>
                
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">Spirit</span>
                    <span className="text-xs text-gray-400">{monster?.currentSpirit}/{monster?.maxSpirit}</span>
                  </div>
                  <Progress value={(monster?.currentSpirit / monster?.maxSpirit) * 100} className="h-1.5 bg-gray-700">
                    <div className="h-full bg-purple-500 rounded-md" />
                  </Progress>
                </div>
              </div>
            </div>
            {monster?.description && (
              <CardDescription className="mt-2 text-gray-400">
                {monster.description}
              </CardDescription>
            )}
          </CardHeader>
          
          <CardContent className="pb-2">
            <Accordion type="single" collapsible defaultValue="domains">
              <AccordionItem value="domains">
                <AccordionTrigger>Domains</AccordionTrigger>
                <AccordionContent>
                  {monster && <DomainList combatant={monster} />}
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="moves">
                <AccordionTrigger>Known Moves</AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-2">
                    {monsterMoves.map(move => (
                      <div key={move.id} className="p-2 rounded bg-gray-800">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge className={moveTypeColors[move.moveType]}>{move.moveType.charAt(0) + move.moveType.slice(1).toLowerCase()}</Badge>
                            <span className="font-bold">{move.name}</span>
                          </div>
                        </div>
                        <div className="text-sm text-gray-400">{move.description}</div>
                        
                        <div className="mt-1 flex flex-wrap gap-1">
                          {move.domains.map(domain => (
                            <Badge key={domain} variant="secondary" className="text-xs">
                              {domain.charAt(0) + domain.slice(1).toLowerCase()}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
          
          <CardFooter>
            <div className="w-full text-center">
              <div className="text-sm text-gray-400">{selectedRegion}</div>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default CombatGame;