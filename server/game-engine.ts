import { v4 as uuidv4 } from 'uuid';
import { storage } from './storage';
import * as types from '@shared/types';
import { GAME_CLASSES } from '../client/src/lib/utils';

export class GameEngine {
  private enemyTemplates: types.Enemy[] = [
    {
      id: 1,
      name: "Forest Wolf",
      level: 1,
      maxHealth: 20,
      currentHealth: 20,
      stats: {
        strength: 8,
        dexterity: 12,
        intelligence: 3
      },
      attacks: [
        { name: "Bite", damage: 4, type: "physical" },
        { name: "Claw", damage: 3, type: "physical" }
      ]
    },
    {
      id: 2,
      name: "Goblin Scout",
      level: 2,
      maxHealth: 15,
      currentHealth: 15,
      stats: {
        strength: 6,
        dexterity: 14,
        intelligence: 8
      },
      attacks: [
        { name: "Dagger Strike", damage: 5, type: "physical" },
        { name: "Throw Rock", damage: 3, type: "physical" }
      ]
    }
  ];

  constructor() {}

  async createNewGame(
    characterName: string,
    characterClass: string,
    background: string
  ): Promise<types.GameState> {
    // Find the character class template
    const classTemplate = GAME_CLASSES.find(c => c.id === characterClass);
    
    if (!classTemplate) {
      throw new Error(`Invalid character class: ${characterClass}`);
    }
    
    // Create character
    const character: types.Character = {
      id: 1, // Would normally be from database
      name: characterName,
      class: classTemplate.name,
      background,
      level: 1,
      xp: 0,
      stats: classTemplate.stats,
      maxHealth: classTemplate.health,
      currentHealth: classTemplate.health,
      maxMana: classTemplate.mana,
      currentMana: classTemplate.mana
    };
    
    // Get starting location
    const startLocation = await storage.getLocationById(1); // Willowbrook Village
    
    // Create inventory
    const inventory: types.Inventory = {
      maxWeight: 50,
      currentWeight: 0,
      items: []
    };
    
    // Create game state
    const gameState: types.GameState = {
      gameId: uuidv4(),
      character,
      location: startLocation,
      inventory,
      quests: [],
      choices: [
        "Explore the village",
        "Speak with the village elder",
        "Visit the merchant's shop",
        "Head into the surrounding wilderness"
      ]
    };
    
    return gameState;
  }

  async processPlayerInput(
    input: string,
    gameState: types.GameState
  ): Promise<{
    shouldSendToAI: boolean;
    processedInput?: string;
    gameUpdate?: Partial<types.GameState>;
  }> {
    // Check for special commands
    if (input.startsWith('/')) {
      return this.handleCommand(input, gameState);
    }
    
    // Process regular input before sending to AI
    // Maybe the player is trying to travel, attack, etc.
    
    // For now, just pass through to AI
    return {
      shouldSendToAI: true
    };
  }

  private handleCommand(
    command: string,
    gameState: types.GameState
  ): {
    shouldSendToAI: boolean;
    processedInput?: string;
    gameUpdate?: Partial<types.GameState>;
  } {
    const cmd = command.toLowerCase();
    
    // Stats command
    if (cmd === '/stats') {
      const character = gameState.character;
      if (!character) {
        return {
          shouldSendToAI: false,
          processedInput: "You don't have a character yet."
        };
      }
      
      return {
        shouldSendToAI: false,
        processedInput: `
          <div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm">
            <h4 class="text-primary-400 font-medium mb-2">Character Stats</h4>
            <p><strong>Name:</strong> ${character.name}</p>
            <p><strong>Class:</strong> ${character.class}</p>
            <p><strong>Level:</strong> ${character.level} (XP: ${character.xp})</p>
            <p><strong>Health:</strong> ${character.currentHealth}/${character.maxHealth}</p>
            <p><strong>Mana:</strong> ${character.currentMana}/${character.maxMana}</p>
            <div class="mt-2">
              <p><strong>Strength:</strong> ${character.stats.strength}</p>
              <p><strong>Dexterity:</strong> ${character.stats.dexterity}</p>
              <p><strong>Intelligence:</strong> ${character.stats.intelligence}</p>
              <p><strong>Charisma:</strong> ${character.stats.charisma}</p>
            </div>
          </div>
        `
      };
    }
    
    // Inventory command
    if (cmd === '/inventory') {
      const inventory = gameState.inventory;
      if (!inventory) {
        return {
          shouldSendToAI: false,
          processedInput: "You don't have an inventory yet."
        };
      }
      
      const itemsList = inventory.items.length > 0
        ? inventory.items.map(item => `<p>${item.quantity}× ${item.name}${item.description ? ` - ${item.description}` : ''}</p>`).join('')
        : '<p class="text-dark-300 italic">Your inventory is empty.</p>';
      
      return {
        shouldSendToAI: false,
        processedInput: `
          <div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm">
            <h4 class="text-primary-400 font-medium mb-2">Inventory</h4>
            <p><strong>Weight:</strong> ${inventory.currentWeight}/${inventory.maxWeight} lbs</p>
            <div class="mt-2">
              ${itemsList}
            </div>
          </div>
        `
      };
    }
    
    // Quests command
    if (cmd === '/quests') {
      const quests = gameState.quests;
      if (!quests || quests.length === 0) {
        return {
          shouldSendToAI: false,
          processedInput: "You don't have any active quests."
        };
      }
      
      const questsList = quests.map(quest => `
        <div class="mb-2">
          <p><strong class="text-accent-400">${quest.title}</strong> (${quest.status})</p>
          <p class="text-dark-200">${quest.description}</p>
        </div>
      `).join('');
      
      return {
        shouldSendToAI: false,
        processedInput: `
          <div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm">
            <h4 class="text-primary-400 font-medium mb-2">Active Quests</h4>
            ${questsList}
          </div>
        `
      };
    }
    
    // Location command
    if (cmd === '/location') {
      const location = gameState.location;
      if (!location) {
        return {
          shouldSendToAI: false,
          processedInput: "You don't know where you are."
        };
      }
      
      return {
        shouldSendToAI: false,
        processedInput: `
          <div class="bg-dark-700/50 border border-dark-600 rounded-lg p-4 text-sm">
            <h4 class="text-primary-400 font-medium mb-2">Current Location</h4>
            <p><strong>${location.name}</strong></p>
            <p class="text-dark-200">${location.description}</p>
          </div>
        `
      };
    }
    
    // Test combat command
    if (cmd === '/combat') {
      const enemy = this.createEnemy(1); // Forest Wolf
      
      const combat: types.Combat = {
        enemy,
        status: "active",
        log: [`You encounter a ${enemy.name}!`],
        round: 1
      };
      
      return {
        shouldSendToAI: false,
        processedInput: `You encounter a ${enemy.name}! Prepare for combat!`,
        gameUpdate: {
          combat
        }
      };
    }
    
    // Unknown command, pass to AI
    return {
      shouldSendToAI: true,
      processedInput: `The player tried to use a command: ${command}`
    };
  }

  async processAIResponse(
    aiResponse: {
      narrative: string;
      choices?: string[];
      worldUpdates?: any;
      shouldRemember: boolean;
    },
    gameState: types.GameState
  ): Promise<types.GameState> {
    const updatedGameState = { ...gameState };
    
    // Update choices if provided
    if (aiResponse.choices && aiResponse.choices.length > 0) {
      updatedGameState.choices = aiResponse.choices;
    }
    
    // Process world updates if provided
    if (aiResponse.worldUpdates) {
      // Handle location changes
      if (aiResponse.worldUpdates.location) {
        const newLocationId = aiResponse.worldUpdates.location;
        const newLocation = await storage.getLocationById(newLocationId);
        if (newLocation) {
          updatedGameState.location = newLocation;
        }
      }
      
      // Handle inventory changes
      if (aiResponse.worldUpdates.inventory) {
        const { addItems, removeItems } = aiResponse.worldUpdates.inventory;
        
        if (addItems && Array.isArray(addItems)) {
          for (const item of addItems) {
            this.addItemToInventory(updatedGameState, item);
          }
        }
        
        if (removeItems && Array.isArray(removeItems)) {
          for (const itemName of removeItems) {
            this.removeItemFromInventory(updatedGameState, itemName);
          }
        }
      }
      
      // Handle character changes
      if (aiResponse.worldUpdates.character) {
        const { health, mana, xp } = aiResponse.worldUpdates.character;
        
        if (updatedGameState.character) {
          if (typeof health === 'number') {
            updatedGameState.character.currentHealth = Math.min(
              health,
              updatedGameState.character.maxHealth
            );
          }
          
          if (typeof mana === 'number') {
            updatedGameState.character.currentMana = Math.min(
              mana,
              updatedGameState.character.maxMana
            );
          }
          
          if (typeof xp === 'number') {
            updatedGameState.character.xp = xp;
            // Check for level up
            this.checkForLevelUp(updatedGameState);
          }
        }
      }
      
      // Handle quest changes
      if (aiResponse.worldUpdates.quests) {
        const { addQuests, updateQuests } = aiResponse.worldUpdates.quests;
        
        if (addQuests && Array.isArray(addQuests)) {
          for (const quest of addQuests) {
            updatedGameState.quests = [...(updatedGameState.quests || []), quest];
          }
        }
        
        if (updateQuests && Array.isArray(updateQuests)) {
          for (const update of updateQuests) {
            const { id, status } = update;
            const questIndex = updatedGameState.quests?.findIndex(q => q.id === id);
            
            if (questIndex !== undefined && questIndex !== -1 && updatedGameState.quests) {
              updatedGameState.quests[questIndex].status = status;
            }
          }
        }
      }
      
      // Handle combat initiation
      if (aiResponse.worldUpdates.combat) {
        const { enemyId, surprise } = aiResponse.worldUpdates.combat;
        
        if (enemyId) {
          const enemy = this.createEnemy(enemyId);
          
          const combat: types.Combat = {
            enemy,
            status: "active",
            log: [`You encounter a ${enemy.name}!`],
            round: 1
          };
          
          updatedGameState.combat = combat;
        }
      }
    }
    
    // Check for combat from narrative
    if (!updatedGameState.combat && this.detectCombatInNarrative(aiResponse.narrative)) {
      // Default to Forest Wolf encounter if combat is detected but not specified
      const enemy = this.createEnemy(1);
      
      const combat: types.Combat = {
        enemy,
        status: "active",
        log: [`You encounter a ${enemy.name}!`],
        round: 1
      };
      
      updatedGameState.combat = combat;
    }
    
    return updatedGameState;
  }

  async processCombatAction(
    action: string,
    gameState: types.GameState
  ): Promise<types.Combat> {
    if (!gameState.combat || !gameState.character) {
      throw new Error("No active combat or character");
    }
    
    const combat = { ...gameState.combat };
    const character = { ...gameState.character };
    const enemy = { ...combat.enemy };
    
    // Handle different actions
    switch (action) {
      case "attack":
        // Player attacks
        const playerDamage = this.calculateDamage(character);
        enemy.currentHealth = Math.max(0, enemy.currentHealth - playerDamage);
        combat.log.push(`You attack the ${enemy.name} and deal ${playerDamage} damage.`);
        
        // Check if enemy is defeated
        if (enemy.currentHealth <= 0) {
          combat.status = "won";
          combat.log.push(`You have defeated the ${enemy.name}!`);
          
          // Award XP
          const xpGained = enemy.level * 100;
          character.xp += xpGained;
          combat.log.push(`You gained ${xpGained} XP!`);
          
          // Check for level up
          const leveledUp = this.checkForLevelUp({ ...gameState, character });
          if (leveledUp) {
            combat.log.push(`Congratulations! You've reached level ${character.level}!`);
          }
          
          combat.character = character;
          combat.enemy = enemy;
          combat.result = `You defeated the ${enemy.name} and gained ${xpGained} XP.`;
          
          return combat;
        }
        
        // Enemy attacks
        const enemyDamage = this.calculateEnemyDamage(enemy);
        character.currentHealth = Math.max(0, character.currentHealth - enemyDamage);
        combat.log.push(`The ${enemy.name} attacks you and deals ${enemyDamage} damage.`);
        
        // Check if player is defeated
        if (character.currentHealth <= 0) {
          combat.status = "lost";
          combat.log.push("You have been defeated!");
          combat.result = `You were defeated by the ${enemy.name}.`;
        }
        
        break;
        
      case "defend":
        // Player defends, reducing enemy damage
        const reducedEnemyDamage = Math.floor(this.calculateEnemyDamage(enemy) * 0.5);
        character.currentHealth = Math.max(0, character.currentHealth - reducedEnemyDamage);
        combat.log.push(`You take a defensive stance against the ${enemy.name}.`);
        combat.log.push(`The ${enemy.name} attacks but you block some damage, taking ${reducedEnemyDamage} damage.`);
        
        // Check if player is defeated
        if (character.currentHealth <= 0) {
          combat.status = "lost";
          combat.log.push("You have been defeated!");
          combat.result = `You were defeated by the ${enemy.name} despite your defensive efforts.`;
        }
        
        break;
        
      case "flee":
        // Attempt to flee based on dexterity
        const fleeChance = character.stats.dexterity / (character.stats.dexterity + enemy.stats.dexterity);
        const fleeRoll = Math.random();
        
        if (fleeRoll < fleeChance) {
          combat.status = "fled";
          combat.log.push("You successfully flee from combat!");
          combat.result = `You managed to escape from the ${enemy.name}.`;
        } else {
          combat.log.push("You failed to flee!");
          
          // Enemy gets a free attack
          const fleeDamage = this.calculateEnemyDamage(enemy);
          character.currentHealth = Math.max(0, character.currentHealth - fleeDamage);
          combat.log.push(`The ${enemy.name} strikes as you try to flee, dealing ${fleeDamage} damage.`);
          
          // Check if player is defeated
          if (character.currentHealth <= 0) {
            combat.status = "lost";
            combat.log.push("You have been defeated!");
            combat.result = `You were defeated by the ${enemy.name} while trying to flee.`;
          }
        }
        
        break;
        
      case "use-item":
        // For now, just have a simple healing potion
        const healAmount = 10;
        character.currentHealth = Math.min(character.maxHealth, character.currentHealth + healAmount);
        combat.log.push(`You use a healing potion and recover ${healAmount} health.`);
        
        // Enemy still attacks
        const itemDamage = this.calculateEnemyDamage(enemy);
        character.currentHealth = Math.max(0, character.currentHealth - itemDamage);
        combat.log.push(`The ${enemy.name} attacks you and deals ${itemDamage} damage.`);
        
        // Check if player is defeated
        if (character.currentHealth <= 0) {
          combat.status = "lost";
          combat.log.push("You have been defeated!");
          combat.result = `You were defeated by the ${enemy.name} despite using a healing potion.`;
        }
        
        break;
        
      default:
        throw new Error(`Invalid combat action: ${action}`);
    }
    
    // Update combat state
    combat.character = character;
    combat.enemy = enemy;
    combat.round += 1;
    
    return combat;
  }

  private createEnemy(enemyId: number): types.Enemy {
    const template = this.enemyTemplates.find(e => e.id === enemyId);
    
    if (!template) {
      throw new Error(`Enemy template not found: ${enemyId}`);
    }
    
    // Clone the template
    return {
      ...template,
      currentHealth: template.maxHealth // Reset health
    };
  }

  private calculateDamage(character: types.Character): number {
    // Simple damage formula based on strength
    const baseDamage = character.stats.strength / 2;
    const variation = Math.random() * 4 - 2; // -2 to +2 variation
    return Math.max(1, Math.floor(baseDamage + variation));
  }

  private calculateEnemyDamage(enemy: types.Enemy): number {
    // Use a random attack from the enemy's attacks
    const attack = enemy.attacks[Math.floor(Math.random() * enemy.attacks.length)];
    const variation = Math.random() * 3 - 1; // -1 to +2 variation
    return Math.max(1, Math.floor(attack.damage + variation));
  }

  private checkForLevelUp(gameState: types.GameState): boolean {
    if (!gameState.character) return false;
    
    const character = gameState.character;
    const requiredXp = character.level * 1000;
    
    if (character.xp >= requiredXp) {
      character.level += 1;
      
      // Increase stats
      character.stats.strength += 1;
      character.stats.dexterity += 1;
      character.stats.intelligence += 1;
      character.stats.charisma += 1;
      
      // Increase health and mana
      character.maxHealth += 5;
      character.currentHealth = character.maxHealth;
      character.maxMana += 5;
      character.currentMana = character.maxMana;
      
      return true;
    }
    
    return false;
  }

  private addItemToInventory(gameState: types.GameState, item: Partial<types.InventoryItem>): void {
    if (!gameState.inventory) return;
    
    const inventory = gameState.inventory;
    const existingItem = inventory.items.find(i => i.name === item.name);
    
    if (existingItem) {
      existingItem.quantity += item.quantity || 1;
    } else {
      inventory.items.push({
        id: Date.now(), // Simple unique ID
        name: item.name || "Unknown Item",
        description: item.description,
        quantity: item.quantity || 1,
        weight: item.weight || 1,
        type: item.type || "misc",
        properties: item.properties
      });
    }
    
    // Recalculate weight
    inventory.currentWeight = inventory.items.reduce(
      (total, item) => total + (item.weight * item.quantity),
      0
    );
  }

  private removeItemFromInventory(gameState: types.GameState, itemName: string): void {
    if (!gameState.inventory) return;
    
    const inventory = gameState.inventory;
    const itemIndex = inventory.items.findIndex(i => i.name === itemName);
    
    if (itemIndex !== -1) {
      const item = inventory.items[itemIndex];
      
      if (item.quantity > 1) {
        item.quantity -= 1;
      } else {
        inventory.items.splice(itemIndex, 1);
      }
      
      // Recalculate weight
      inventory.currentWeight = inventory.items.reduce(
        (total, item) => total + (item.weight * item.quantity),
        0
      );
    }
  }

  private detectCombatInNarrative(narrative: string): boolean {
    const combatTriggers = [
      "attack", "combat", "fight", "battle", "enemy", "monster", "creature",
      "lunges at you", "charges at you", "threatens you", "approaches menacingly"
    ];
    
    const narrativeLower = narrative.toLowerCase();
    
    return combatTriggers.some(trigger => narrativeLower.includes(trigger));
  }
}
