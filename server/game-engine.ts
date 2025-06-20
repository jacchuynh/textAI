import { Player, MagicProfile } from '@shared/schema';
import axios from 'axios';

/**
 * Game Engine - Now bridges to Python AI GM Brain system
 */

interface GameCommandResult {
  success: boolean;
  message: string;
  data?: any;
  playerUpdates?: Partial<Player>;
  magicProfileUpdates?: Partial<MagicProfile>;
}

interface PlayerWithMagicProfile extends Player {
  magicProfile?: MagicProfile | null;
}

// Configuration for AI GM Brain service
const AI_GM_BRAIN_URL = process.env.AI_GM_BRAIN_URL || 'http://localhost:8000';

/**
 * Process a game command through the AI GM Brain system
 */
export async function processGameCommand(
  player: PlayerWithMagicProfile, 
  command: string
): Promise<GameCommandResult> {
  try {
    // First, try the advanced AI GM Brain system
    const aiResponse = await processCommandWithAIGMBrain(player, command);
    if (aiResponse) {
      return aiResponse;
    }
    
    // Fallback to basic parsing if AI GM Brain is unavailable
    return processCommandBasic(player, command);
    
  } catch (error) {
    console.error('Error processing game command:', error);
    return {
      success: false,
      message: "An error occurred while processing your command."
    };
  }
}

/**
 * Process command using the AI GM Brain system
 */
async function processCommandWithAIGMBrain(
  player: PlayerWithMagicProfile,
  command: string
): Promise<GameCommandResult | null> {
  try {
    // Call the Python AI GM Brain API
    const response = await axios.post(`${AI_GM_BRAIN_URL}/api/ai-gm/process-input`, {
      player_id: player.userId,
      game_id: `game_${player.id}`,
      input_text: command,
      player_context: {
        name: player.name,
        level: player.level,
        location_region: player.locationRegion,
        location_area: player.locationArea,
        health: { current: player.healthCurrent, max: player.healthMax },
        magic_profile: player.magicProfile
      }
    }, {
      timeout: 10000, // 10 second timeout
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.data && response.data.response_text) {
      return {
        success: true,
        message: response.data.response_text,
        data: {
          processing_mode: response.data.metadata?.processing_mode,
          complexity: response.data.metadata?.complexity,
          parsed_successfully: response.data.metadata?.parsed_successfully,
          requires_llm: response.data.requires_llm,
          llm_used: response.data.llm_used
        }
      };
    }

    return null;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.warn('AI GM Brain unavailable, falling back to basic parsing:', errorMessage);
    return null;
  }
}

/**
 * Basic fallback command processing (existing logic)
 */
function processCommandBasic(
  player: PlayerWithMagicProfile, 
  command: string
): GameCommandResult {
  const normalizedCommand = command.toLowerCase().trim();
  
  // Basic command routing - existing logic
  if (normalizedCommand.startsWith('look') || normalizedCommand === 'l') {
    return handleLookCommand(player);
  }
  
  if (normalizedCommand.startsWith('inventory') || normalizedCommand === 'i') {
    return handleInventoryCommand(player);
  }
  
  if (normalizedCommand.startsWith('status') || normalizedCommand === 'stat') {
    return handleStatusCommand(player);
  }
  
  if (normalizedCommand.startsWith('cast ')) {
    const spellName = normalizedCommand.substring(5);
    return handleCastSpellCommand(player, spellName);
  }
  
  if (normalizedCommand.startsWith('move ') || normalizedCommand.startsWith('go ')) {
    const direction = normalizedCommand.split(' ')[1];
    return handleMoveCommand(player, direction);
  }
  
  if (normalizedCommand.startsWith('help')) {
    return handleHelpCommand();
  }
  
  // Enhanced default response with suggestions
  return {
    success: false,
    message: "I don't understand that command. Try commands like 'look around', 'inventory', 'cast [spell name]', or ask questions like 'what spells can I cast?'. Type 'help' for more options."
  };
}

/**
 * Handle the 'look' command - describe current location
 */
function handleLookCommand(player: PlayerWithMagicProfile): GameCommandResult {
  const locationDescription = getLocationDescription(player);
  
  return {
    success: true,
    message: locationDescription
  };
}

/**
 * Handle the 'inventory' command - show player's items
 */
function handleInventoryCommand(player: PlayerWithMagicProfile): GameCommandResult {
  // This would query the actual inventory from the database
  return {
    success: true,
    message: `Your inventory contains basic starting equipment. You have ${player.gold} gold coins.`,
    data: {
      gold: player.gold,
      // Additional inventory data would be fetched here
    }
  };
}

/**
 * Handle the 'status' command - show player stats
 */
function handleStatusCommand(player: PlayerWithMagicProfile): GameCommandResult {
  const magicProfile = player.magicProfile;
  
  let statusMessage = `
**${player.name}** - Level ${player.level} Mage
Health: ${player.healthCurrent}/${player.healthMax}
Experience: ${player.experience}
Gold: ${player.gold}
Location: ${player.locationArea}, ${player.locationRegion}
`;

  if (magicProfile) {
    statusMessage += `
Magic Affinity: ${magicProfile.magicAffinity}
Mana: ${magicProfile.manaCurrent}/${magicProfile.manaCapacity}
Spell Power: ${magicProfile.spellPower}
Known Aspects: ${magicProfile.knownAspects.join(', ')}
`;
  }

  return {
    success: true,
    message: statusMessage.trim()
  };
}

/**
 * Handle spell casting commands
 */
function handleCastSpellCommand(player: PlayerWithMagicProfile, spellName: string): GameCommandResult {
  const magicProfile = player.magicProfile;
  
  if (!magicProfile) {
    return {
      success: false,
      message: "You don't have a magic profile yet. Visit the academy to register your magical abilities."
    };
  }
  
  // Basic spell casting simulation
  const manaCost = 10; // This would be looked up from the spell database
  
  if (magicProfile.manaCurrent < manaCost) {
    return {
      success: false,
      message: `You don't have enough mana to cast ${spellName}. You need ${manaCost} mana but only have ${magicProfile.manaCurrent}.`
    };
  }
  
  // Simulate spell casting
  const newMana = Math.max(0, magicProfile.manaCurrent - manaCost);
  
  return {
    success: true,
    message: `You cast ${spellName}! Magical energy flows through you as the spell takes effect.`,
    magicProfileUpdates: {
      manaCurrent: newMana
    }
  };
}

/**
 * Handle movement commands
 */
function handleMoveCommand(player: PlayerWithMagicProfile, direction: string): GameCommandResult {
  // This would integrate with the world system to handle actual movement
  const validDirections = ['north', 'south', 'east', 'west', 'up', 'down'];
  
  if (!validDirections.includes(direction)) {
    return {
      success: false,
      message: `You can't go ${direction}. Valid directions are: ${validDirections.join(', ')}.`
    };
  }
  
  // Simulate movement (in a real implementation, this would check valid exits)
  return {
    success: true,
    message: `You move ${direction}. The magical energies shift around you as you enter a new area.`
  };
}

/**
 * Handle help command
 */
function handleHelpCommand(): GameCommandResult {
  const helpText = `
**Available Commands:**
- **look** (or 'l') - Examine your surroundings
- **inventory** (or 'i') - Check your inventory
- **status** (or 'stat') - View your character status
- **cast [spell]** - Cast a spell (e.g., 'cast fireball')
- **move [direction]** - Move in a direction (north, south, east, west)
- **help** - Show this help message

**Game Tips:**
- Your mana regenerates over time
- Different areas have different magical properties
- Level up by completing quests and gaining experience
- Visit the academy to learn new spells
`;

  return {
    success: true,
    message: helpText.trim()
  };
}

/**
 * Get description of player's current location
 */
function getLocationDescription(player: PlayerWithMagicProfile): string {
  // This would fetch from the areas/regions database in a real implementation
  const locationDescriptions: Record<string, Record<string, string>> = {
    'Arcadia': {
      'Novice_Quarter': 'You stand in the Novice Quarter of Arcadia. Around you, apprentice mages practice their spells, creating small bursts of colorful magic. The air hums with magical energy, and you can see the towering spires of the Grand Academy in the distance.',
      'Grand_Academy': 'You are within the Grand Academy of Magic. Ancient stones pulse with arcane energy, and floating books drift through the air. Statues of great mages seem to watch your every move with their enchanted eyes.'
    },
    'Shadowvale': {
      'Twilight_Entrance': 'You stand at the edge of Shadowvale. The ancient trees loom overhead, their branches blocking out most of the sunlight. Strange whispers echo through the forest, and you sense powerful magic lurking in the shadows.',
      'Heart_of_Shadows': 'Deep within Shadowvale, you feel the weight of ancient magic pressing down upon you. The trees here are massive and seem almost alive, their roots pulsing with dark energy.'
    },
    'Emberhold': {
      'Ash_Roads': 'The volcanic road stretches before you, covered in a fine layer of ash. Heat radiates from the ground, and you can see rivers of lava flowing in the distance. The air shimmers with fire magic.',
      'Molten_Core': 'You stand at the heart of the volcano. Lava flows all around you, and the very air burns with intense heat. Fire elementals dance in the molten streams, their forms shifting and beautiful.'
    },
    'Crystalshore': {
      'Harbor_District': 'The crystal formations along the shore refract the sunlight into brilliant rainbows. The sound of waves mingles with the musical chiming of the crystals, creating a symphony of water and light magic.',
      'Crystal_Caverns': 'Inside the luminescent caverns, crystals of every color imaginable line the walls. Their glow provides a soft, ethereal light, and you can feel water magic flowing through the underground streams.'
    }
  };
  
  const regionDescriptions = locationDescriptions[player.locationRegion];
  if (regionDescriptions && regionDescriptions[player.locationArea]) {
    return regionDescriptions[player.locationArea];
  }
  
  return `You are in ${player.locationArea} within the ${player.locationRegion} region. The magical energies here feel different from other places you've visited.`;
}