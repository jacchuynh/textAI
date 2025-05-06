// Game State Types
export interface GameState {
  gameId: string;
  character: Character | null;
  location: Location | null;
  inventory: Inventory | null;
  quests: Quest[] | null;
  narrativeContent?: string;
  choices?: string[] | null;
  combat?: Combat | null;
}

// Domain System Types
export enum DomainType {
  BODY = "BODY",         // Physical health, stamina, manual labor, illness resistance
  MIND = "MIND",         // Logic, learning, memory, magic theory, problem solving
  SPIRIT = "SPIRIT",     // Willpower, luck, intuition, empathy, divine favor
  SOCIAL = "SOCIAL",     // Persuasion, negotiation, reputation, manipulation
  CRAFT = "CRAFT",       // Practical skills, making, fixing, performance under time pressure
  AUTHORITY = "AUTHORITY", // Leadership, command, strategy, decree enforcement
  AWARENESS = "AWARENESS" // Perception, reaction time, timing in social or combat interactions
}

export enum GrowthTier {
  NOVICE = "NOVICE",       // Range 0-2
  SKILLED = "SKILLED",     // Range 3-4
  EXPERT = "EXPERT",       // Range 5-7
  MASTER = "MASTER",       // Range 8-9
  PARAGON = "PARAGON"      // Range 10+
}

export enum TagCategory {
  COMBAT = "COMBAT",     // Combat-related tags
  CRAFTING = "CRAFTING", // Crafting-related tags
  SOCIAL = "SOCIAL",     // Social interaction tags
  MAGIC = "MAGIC",       // Magic-related tags
  SURVIVAL = "SURVIVAL", // Survival and wilderness tags
  KINGDOM = "KINGDOM",   // Kingdom management tags
  GENERAL = "GENERAL"    // General purpose tags
}

export interface Domain {
  type: DomainType;
  value: number;
  growthPoints: number;
  growthRequired: number;
  usageCount: number;
  growthLog: GrowthLogEntry[];
  levelUpsRequired: number;
}

export interface GrowthLogEntry {
  date: string;
  domain: DomainType;
  action: string;
  success: boolean;
}

export interface Tag {
  id: string;
  name: string;
  category: TagCategory;
  description: string;
  domains: DomainType[];
  rank: number;
  xp: number;
  xpRequired: number;
}

export interface ShadowProfile {
  characterId: string;
  domainUsage: Record<DomainType, number>;
  recentTags: string[];
  timeTracking: {
    recent: Record<DomainType, number>;
    weekly: Record<DomainType, number>;
    monthly: Record<DomainType, number>;
  };
  preferences: Record<DomainType, number>;
}

// Character Types
export interface Character {
  id: number;
  name: string;
  class: string;
  background: string;
  level: number;
  xp: number;
  stats: CharacterStats;
  maxHealth: number;
  currentHealth: number;
  maxMana: number;
  currentMana: number;
  // Domain system additions
  domains?: Record<DomainType, Domain>;
  tags?: Record<string, Tag>;
  shadowProfile?: ShadowProfile;
  domainHistory?: Record<DomainType, number[]>;
}

export interface CharacterStats {
  strength: number;
  dexterity: number;
  intelligence: number;
  charisma: number;
}

// Location Types
export interface Location {
  id: number;
  name: string;
  description: string;
  type: string;
  connections?: number[];
  npcs?: NPC[];
}

// Inventory Types
export interface Inventory {
  maxWeight: number;
  currentWeight: number;
  items: InventoryItem[];
}

export interface InventoryItem {
  id: number;
  name: string;
  description?: string;
  quantity: number;
  weight: number;
  type: string;
  properties?: ItemProperties;
}

export interface ItemProperties {
  damage?: number;
  defense?: number;
  effects?: ItemEffect[];
}

export interface ItemEffect {
  type: string;
  value: number;
  duration?: number;
}

// Quest Types
export interface Quest {
  id: number;
  title: string;
  description: string;
  status: "active" | "completed" | "failed";
}

// NPC Types
export interface NPC {
  id: number;
  name: string;
  description: string;
  attitude: "friendly" | "neutral" | "hostile";
  dialogue?: DialogueEntry[];
  // Domain system additions
  domainBias?: Partial<Record<DomainType, number>>;
  knownInteractions?: string[];
  firstEncounter?: boolean;
}

export interface DialogueEntry {
  id: string;
  text: string;
  responses?: DialogueResponse[];
}

export interface DialogueResponse {
  id: string;
  text: string;
  nextDialogueId?: string;
  action?: string;
}

// Combat Types
export interface Combat {
  enemy: Enemy;
  status: "active" | "won" | "lost" | "fled" | "ended";
  log: string[];
  round: number;
  character?: Character;
  result?: string;
}

export interface Enemy {
  id: number;
  name: string;
  level: number;
  maxHealth: number;
  currentHealth: number;
  stats: EnemyStats;
  attacks: Attack[];
}

export interface EnemyStats {
  strength: number;
  dexterity: number;
  intelligence: number;
}

export interface Attack {
  name: string;
  damage: number;
  type: string;
}

// Memory Types
export interface MemoryEntry {
  id: number;
  type: "world_event" | "npc_interaction" | "player_action";
  content: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

// Narrative Types
export interface NarrativeEntry {
  type: "system" | "player-input" | "ai-response";
  content: string;
}

// API Response Types
export interface StartGameResponse {
  gameId: string;
  character: Character;
  location: Location;
  narrativeContent: string;
  choices?: string[];
}

export interface SendInputResponse {
  narrativeContent: string;
  gameState: Partial<GameState>;
  choices?: string[];
  combat?: Combat;
}

// AI Response Types
export interface AIResponseData {
  narrative: string;
  worldUpdates?: {
    location?: number;
    inventory?: {
      addItems?: Partial<InventoryItem>[];
      removeItems?: string[];
    };
    character?: {
      health?: number;
      mana?: number;
      xp?: number;
    };
    quests?: {
      addQuests?: Partial<Quest>[];
      updateQuests?: { id: number; status: "active" | "completed" | "failed" }[];
    };
    combat?: {
      enemyId?: number;
      surprise?: boolean;
    };
  };
  choices?: string[];
  shouldRemember: boolean;
}
