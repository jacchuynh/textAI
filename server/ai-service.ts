import axios from 'axios';
import * as types from '@shared/types';

interface AIResponse {
  narrative: string;
  choices?: string[];
  worldUpdates?: any;
  shouldRemember: boolean;
}

export class AIService {
  private apiKey: string;
  private apiEndpoint: string;
  private modelName: string;

  constructor() {
    // Get API key from environment variable
    this.apiKey = process.env.OPENROUTER_API_KEY || '';
    
    if (!this.apiKey) {
      console.warn('WARNING: OPENROUTER_API_KEY not set. AI responses will be limited.');
    }
    
    this.apiEndpoint = 'https://openrouter.ai/api/v1/chat/completions';
    this.modelName = process.env.OPENROUTER_MODEL || 'openai/gpt-3.5-turbo';
  }

  async generateResponse(
    input: string,
    recentMemories: types.MemoryEntry[],
    gameState: types.GameState
  ): Promise<AIResponse> {
    try {
      // Format the context for the AI
      const prompt = this.formatPrompt(input, recentMemories, gameState);
      
      // Check if API key is available
      if (!this.apiKey) {
        return this.getFallbackResponse(input, gameState);
      }
      
      // Make API call to OpenRouter
      const response = await axios.post(
        this.apiEndpoint,
        {
          model: this.modelName,
          messages: [
            {
              role: 'system',
              content: this.getSystemPrompt(gameState)
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.7,
          max_tokens: 500
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`,
            'HTTP-Referer': 'https://rpg-chronicles.app',
            'X-Title': 'Chronicles RPG'
          }
        }
      );
      
      // Extract and parse the response
      const aiContent = response.data.choices[0]?.message?.content || '';
      
      return this.parseAIResponse(aiContent);
    } catch (error) {
      console.error('Error calling OpenRouter API:', error);
      return this.getFallbackResponse(input, gameState);
    }
  }

  private getSystemPrompt(gameState: types.GameState): string {
    const character = gameState.character;
    
    return `
      You are the game master for a text-based RPG called "Chronicles". You craft immersive, descriptive narratives based on player actions.
      
      Game world: The realm of Eldoria - a fantasy world with five kingdoms, magic, monsters, and adventure.
      
      Current character: ${character ? `${character.name}, a level ${character.level} ${character.class} with a ${character.background} background.` : 'Not yet created'}
      
      Rules:
      1. Provide rich, evocative descriptions that bring the world to life.
      2. Balance narrative with opportunities for player agency.
      3. Keep responses under 3 paragraphs to maintain engagement.
      4. Remember past player choices and reference them appropriately.
      5. Suggest 2-4 possible actions the player might take next, formatted as an array at the end of your response.
      6. You can suggest world updates including: location changes, inventory changes, character changes, quest updates, and combat initiation.
      7. For any significant world event, set shouldRemember to true.
      
      Format your response with a narrative section followed by any world updates and suggested choices as a JSON object.
      Example:
      {
        "narrative": "Your narrative text here...",
        "worldUpdates": {
          "location": 2,
          "inventory": {
            "addItems": [{"name": "Ancient Map", "description": "A weathered map showing an unmarked location", "quantity": 1, "weight": 1, "type": "misc"}],
            "removeItems": ["Torch"]
          },
          "character": {
            "health": 25,
            "mana": 15,
            "xp": 150
          },
          "quests": {
            "addQuests": [{"id": 1, "title": "The Missing Shipment", "description": "Investigate the missing goods for the merchant", "status": "active"}],
            "updateQuests": [{"id": 1, "status": "completed"}]
          },
          "combat": {
            "enemyId": 1,
            "surprise": true
          }
        },
        "choices": ["Examine the ancient map", "Ask the merchant about the map", "Head to the marked location", "Ignore the map and continue your journey"],
        "shouldRemember": true
      }
    `;
  }

  private formatPrompt(
    input: string,
    recentMemories: types.MemoryEntry[],
    gameState: types.GameState
  ): string {
    const character = gameState.character;
    const location = gameState.location;
    
    // Format recent memories
    const memoriesContext = recentMemories.map(memory => 
      `- ${memory.type === 'player_action' ? 'PLAYER: ' : ''}${memory.content}`
    ).join('\n');
    
    return `
      CONTEXT:
      ${character ? `You are playing as ${character.name}, a level ${character.level} ${character.class} with a ${character.background} background.` : 'Character not yet created.'}
      ${location ? `Current location: ${location.name} - ${location.description}` : ''}
      
      ${recentMemories.length > 0 ? 'RECENT EVENTS:\n' + memoriesContext : 'No recent events.'}
      
      CHARACTER STATE:
      ${character ? `Health: ${character.currentHealth}/${character.maxHealth}, Mana: ${character.currentMana}/${character.maxMana}` : ''}
      ${gameState.inventory ? `Inventory: ${gameState.inventory.items.map(item => `${item.quantity}x ${item.name}`).join(', ') || 'Empty'}` : ''}
      ${gameState.quests && gameState.quests.length > 0 ? `Active Quests: ${gameState.quests.filter(q => q.status === 'active').map(q => q.title).join(', ')}` : 'No active quests.'}
      
      PLAYER INPUT:
      ${input}
      
      Respond with narrative description and choices. Remember to include any world updates in your response.
    `;
  }

  private parseAIResponse(content: string): AIResponse {
    try {
      // Try to parse the response as JSON
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      
      if (jsonMatch) {
        const jsonContent = jsonMatch[0];
        const parsedResponse = JSON.parse(jsonContent);
        
        // If we successfully parsed the JSON, use the structure
        return {
          narrative: parsedResponse.narrative || "I'm not sure what happens next...",
          choices: parsedResponse.choices || [],
          worldUpdates: parsedResponse.worldUpdates || {},
          shouldRemember: parsedResponse.shouldRemember || false
        };
      }
      
      // If we couldn't match JSON, just use the text as narrative
      return {
        narrative: content,
        choices: [], // Always include an empty array for choices
        shouldRemember: false
      };
    } catch (error) {
      console.error('Error parsing AI response:', error);
      
      // If there was a JSON error, we probably have something that looks like JSON but isn't valid
      // Check if the content appears to be in JSON format (has curly braces)
      if (content.includes('{') && content.includes('}')) {
        // This is likely malformed JSON - extract just the narrative part if possible
        const narrativeMatch = content.match(/"narrative"\s*:\s*"([^"]+)"/i);
        if (narrativeMatch && narrativeMatch[1]) {
          return {
            narrative: narrativeMatch[1],
            choices: [],
            shouldRemember: false
          };
        }
        
        // If we can't extract the narrative, return a fallback message
        return {
          narrative: "The story continues, though the details are hazy...",
          choices: [],
          shouldRemember: false
        };
      }
      
      // For any other error, return the content as narrative
      return {
        narrative: content,
        choices: [],
        shouldRemember: false
      };
    }
  }

  private getFallbackResponse(input: string, gameState: types.GameState): AIResponse {
    // Simple fallback responses when the API is unavailable
    const fallbacks = [
      "As you venture forth, you notice the surroundings change subtly. What would you like to do?",
      "The path ahead seems uncertain, but your instincts guide you forward. How do you proceed?",
      "You consider your options carefully, aware that each choice shapes your destiny in this realm.",
      "The adventure continues, with new challenges awaiting around every corner."
    ];
    
    // Very basic contextual responses
    let narrative = '';
    
    if (input.includes('talk') || input.includes('speak') || input.includes('ask')) {
      narrative = "You attempt to engage in conversation, but receive only vague responses. Perhaps more information is needed.";
    } else if (input.includes('fight') || input.includes('attack') || input.includes('combat')) {
      narrative = "You prepare for battle, your hand moving to your weapon. The situation grows tense.";
    } else if (input.includes('search') || input.includes('look') || input.includes('examine')) {
      narrative = "You carefully examine your surroundings, looking for anything of interest. A thorough search might reveal hidden secrets.";
    } else if (input.includes('go') || input.includes('travel') || input.includes('move')) {
      narrative = "You travel onward, the path stretching before you through the varied landscapes of Eldoria.";
    } else {
      // Pick a random fallback
      narrative = fallbacks[Math.floor(Math.random() * fallbacks.length)];
    }
    
    // Generate some relevant choices
    const choices = [
      "Continue exploring",
      "Look for items",
      "Check your surroundings",
      "Rest for a while"
    ];
    
    return {
      narrative,
      choices,
      shouldRemember: false
    };
  }
}
