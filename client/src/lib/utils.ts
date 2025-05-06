import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  return num.toString();
}

export const GAME_CLASSES = [
  {
    id: 'warrior',
    name: 'Warrior',
    description: 'Strength-based melee fighter',
    stats: {
      strength: 14,
      dexterity: 10,
      intelligence: 8,
      charisma: 10
    },
    health: 30,
    mana: 10
  },
  {
    id: 'rogue',
    name: 'Rogue',
    description: 'Dexterity-based thief',
    stats: {
      strength: 10,
      dexterity: 14,
      intelligence: 10,
      charisma: 12
    },
    health: 25,
    mana: 15
  },
  {
    id: 'mage',
    name: 'Mage',
    description: 'Intelligence-based spellcaster',
    stats: {
      strength: 8,
      dexterity: 10,
      intelligence: 14,
      charisma: 12
    },
    health: 20,
    mana: 30
  },
  {
    id: 'cleric',
    name: 'Cleric',
    description: 'Wisdom-based healer',
    stats: {
      strength: 10,
      dexterity: 8,
      intelligence: 12,
      charisma: 14
    },
    health: 25,
    mana: 25
  }
];

export const GAME_BACKGROUNDS = [
  { id: 'noble', name: 'Noble - Born to privilege' },
  { id: 'commoner', name: 'Commoner - Humble beginnings' },
  { id: 'outcast', name: 'Outcast - Life on the fringes' },
  { id: 'traveler', name: 'Traveler - Wanderer from afar' }
];

export function calculateMaxXp(level: number): number {
  return level * 1000;
}

export function rollDice(sides: number): number {
  return Math.floor(Math.random() * sides) + 1;
}

export function formatDate(date: Date | string | null | undefined): string {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj instanceof Date && !isNaN(dateObj.getTime())
      ? dateObj.toISOString().split('T')[0]
      : '';
  } catch {
    return '';
  }
}
