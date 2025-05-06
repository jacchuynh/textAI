import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer } from "ws";
import { storage } from "./storage";
import { GameEngine } from "./game-engine";
import { AIService } from "./ai-service";
import { MemoryManager } from "./memory";
import * as schema from "@shared/types";
import { z } from "zod";
import { 
  autoTagAction, 
  calculateNpcAffinity, 
  generateFirstEncounterResponse,
  generateNpcResponse,
  updateShadowProfile 
} from "./npc-reaction";
import { addTestGameRoute } from "./test-game-generator";

const gameEngine = new GameEngine();
const aiService = new AIService();
const memoryManager = new MemoryManager();

export async function registerRoutes(app: Express): Promise<Server> {
  // Add debug routes
  addTestGameRoute(app);
  
  // Initialize the API
  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
  });
  
  // Get list of available games
  app.get("/api/game/list", async (_req, res) => {
    try {
      const games = await storage.getSavedGames();
      res.status(200).json(games);
    } catch (error) {
      console.error("Error getting game list:", error);
      res.status(500).json({ error: "Failed to get game list" });
    }
  });

  // Start new game
  app.post("/api/game/start", async (req, res) => {
    try {
      const startGameSchema = z.object({
        name: z.string().min(2, "Name must be at least 2 characters"),
        characterClass: z.string().min(1, "Character class is required"),
        background: z.string().min(1, "Background is required")
      });

      const validatedData = startGameSchema.parse(req.body);
      
      // Create new game session
      const gameState = await gameEngine.createNewGame(
        validatedData.name,
        validatedData.characterClass,
        validatedData.background
      );
      
      // Generate initial narrative
      const initialPrompt = `You are a ${validatedData.characterClass} named ${validatedData.name} with a ${validatedData.background} background. 
        You find yourself in a small village called Willowbrook at the edge of the kingdom of Valoria. 
        Describe how you arrived here and what you see around you.`;
      
      const aiResponse = await aiService.generateResponse(initialPrompt, [], gameState);
      
      // Store the initial memory
      await memoryManager.addMemory(
        gameState.gameId, 
        "world_event", 
        `Game started with character ${validatedData.name}, a ${validatedData.characterClass} with ${validatedData.background} background.`
      );
      
      // Save the game state with narrative
      const updatedGameState = {
        ...gameState,
        narrativeContent: aiResponse.narrative,
        choices: aiResponse.choices || []
      };
      
      console.log('Starting new game with choices:', updatedGameState.choices);
      
      await storage.saveGameState(updatedGameState);
      
      res.status(200).json(updatedGameState);
    } catch (error) {
      console.error("Error starting game:", error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      
      res.status(500).json({ error: "Failed to start game" });
    }
  });

  // Send player input
  app.post("/api/game/send-input", async (req, res) => {
    try {
      console.log('Received input request:', req.body);
      
      const inputSchema = z.object({
        gameId: z.string(),
        input: z.string().min(1, "Input cannot be empty")
      });

      const validatedData = inputSchema.parse(req.body);
      console.log('Validated input data:', validatedData);
      
      // Get current game state
      console.log('Attempting to get game state for ID:', validatedData.gameId);
      const gameState = await storage.getGameState(validatedData.gameId);
      
      if (!gameState) {
        console.error('Game not found with ID:', validatedData.gameId);
        return res.status(404).json({ error: "Game not found" });
      }
      
      console.log('Found game state:', {
        gameId: gameState.gameId,
        characterName: gameState.character?.name,
        locationName: gameState.location?.name
      });
      
      // Get recent memory for context
      const recentMemories = await memoryManager.getRecentMemories(validatedData.gameId, 5);
      
      // Process the input through the game engine (for commands, combat, etc.)
      const { shouldSendToAI, processedInput, gameUpdate } = await gameEngine.processPlayerInput(
        validatedData.input,
        gameState
      );
      
      // If this is a game command that doesn't need AI response
      if (!shouldSendToAI) {
        res.status(200).json({
          response: {
            narrative: processedInput,
            ...gameUpdate
          }
        });
        return;
      }
      
      // Get AI response
      const aiResponse = await aiService.generateResponse(
        processedInput || validatedData.input,
        recentMemories,
        gameState
      );
      
      // Store the player input in memory
      await memoryManager.addMemory(
        validatedData.gameId,
        "player_action",
        validatedData.input
      );
      
      // Store the AI response in memory if significant
      if (aiResponse.shouldRemember) {
        await memoryManager.addMemory(
          validatedData.gameId,
          "world_event",
          aiResponse.narrative
        );
      }
      
      // Process AI response for game state updates
      const updatedGameState = await gameEngine.processAIResponse(
        aiResponse,
        gameState
      );
      
      // Save updated game state
      await storage.saveGameState(updatedGameState);
      
      const responseData = {
        response: {
          narrative: aiResponse.narrative,
          choices: aiResponse.choices || [],
          combat: updatedGameState.combat
        }
      };
      
      console.log('Sending response with choices:', responseData.response.choices);
      res.status(200).json(responseData);
    } catch (error) {
      console.error("Error processing input:", error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      
      res.status(500).json({ error: "Failed to process input" });
    }
  });

  // Get game state
  app.get("/api/game/:gameId", async (req, res) => {
    try {
      const gameId = req.params.gameId;
      const gameState = await storage.getGameState(gameId);
      
      if (!gameState) {
        return res.status(404).json({ error: "Game not found" });
      }
      
      res.status(200).json(gameState);
    } catch (error) {
      console.error("Error getting game state:", error);
      res.status(500).json({ error: "Failed to get game state" });
    }
  });

  // Save game
  app.post("/api/game/save", async (req, res) => {
    try {
      const saveSchema = z.object({
        gameId: z.string()
      });

      const validatedData = saveSchema.parse(req.body);
      
      // Get current game state
      const gameState = await storage.getGameState(validatedData.gameId);
      
      if (!gameState) {
        return res.status(404).json({ error: "Game not found" });
      }
      
      // Save to database
      await storage.saveGameState(gameState);
      
      res.status(200).json({ success: true, message: "Game saved successfully" });
    } catch (error) {
      console.error("Error saving game:", error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      
      res.status(500).json({ error: "Failed to save game" });
    }
  });

  // Load game
  app.post("/api/game/load", async (req, res) => {
    try {
      const loadSchema = z.object({
        gameId: z.string()
      });

      const validatedData = loadSchema.parse(req.body);
      
      // Load from database
      const gameState = await storage.getGameState(validatedData.gameId);
      
      if (!gameState) {
        return res.status(404).json({ error: "Game not found" });
      }
      
      res.status(200).json(gameState);
    } catch (error) {
      console.error("Error loading game:", error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      
      res.status(500).json({ error: "Failed to load game" });
    }
  });

  // Combat action
  app.post("/api/game/combat-action", async (req, res) => {
    try {
      const actionSchema = z.object({
        gameId: z.string(),
        action: z.string().min(1, "Action cannot be empty")
      });

      const validatedData = actionSchema.parse(req.body);
      
      // Get current game state
      const gameState = await storage.getGameState(validatedData.gameId);
      
      if (!gameState) {
        return res.status(404).json({ error: "Game not found" });
      }
      
      if (!gameState.combat) {
        return res.status(400).json({ error: "No active combat" });
      }
      
      // Process combat action
      const updatedCombat = await gameEngine.processCombatAction(
        validatedData.action,
        gameState
      );
      
      // Update game state
      const updatedGameState = {
        ...gameState,
        combat: updatedCombat,
        character: updatedCombat.character || gameState.character
      };
      
      // Save updated game state
      await storage.saveGameState(updatedGameState);
      
      res.status(200).json(updatedCombat);
    } catch (error) {
      console.error("Error processing combat action:", error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      
      res.status(500).json({ error: "Failed to process combat action" });
    }
  });

  // Get NPC interaction
  app.post("/api/game/npc-interaction", async (req, res) => {
    try {
      const interactionSchema = z.object({
        gameId: z.string(),
        npcId: z.number(),
        playerAction: z.string().min(1, "Player action cannot be empty"),
        model: z.string().optional()
      });

      const validatedData = interactionSchema.parse(req.body);
      
      // Get current game state
      const gameState = await storage.getGameState(validatedData.gameId);
      
      if (!gameState) {
        return res.status(404).json({ error: "Game not found" });
      }
      
      if (!gameState.location || !gameState.location.npcs) {
        return res.status(400).json({ error: "No NPCs in current location" });
      }
      
      // Find the NPC
      const npc = gameState.location.npcs.find(npc => npc.id === validatedData.npcId);
      
      if (!npc) {
        return res.status(404).json({ error: "NPC not found in current location" });
      }
      
      // Auto-tag the player action to detect domains and tags
      const detectedTags = autoTagAction(validatedData.playerAction);
      
      // Get or initialize character shadow profile
      if (!gameState.character?.shadowProfile) {
        if (!gameState.character) {
          return res.status(400).json({ error: "Character not found in game state" });
        }
        
        // Initialize shadow profile for a new character
        gameState.character.shadowProfile = {
          characterId: gameState.character.id.toString(),
          domainUsage: {
            [schema.DomainType.BODY]: 0,
            [schema.DomainType.MIND]: 0,
            [schema.DomainType.SPIRIT]: 0,
            [schema.DomainType.SOCIAL]: 0,
            [schema.DomainType.CRAFT]: 0,
            [schema.DomainType.AUTHORITY]: 0,
            [schema.DomainType.AWARENESS]: 0
          },
          recentTags: [],
          timeTracking: {
            recent: {
              [schema.DomainType.BODY]: 0,
              [schema.DomainType.MIND]: 0,
              [schema.DomainType.SPIRIT]: 0,
              [schema.DomainType.SOCIAL]: 0,
              [schema.DomainType.CRAFT]: 0,
              [schema.DomainType.AUTHORITY]: 0,
              [schema.DomainType.AWARENESS]: 0
            },
            weekly: {
              [schema.DomainType.BODY]: 0,
              [schema.DomainType.MIND]: 0,
              [schema.DomainType.SPIRIT]: 0,
              [schema.DomainType.SOCIAL]: 0,
              [schema.DomainType.CRAFT]: 0,
              [schema.DomainType.AUTHORITY]: 0,
              [schema.DomainType.AWARENESS]: 0
            },
            monthly: {
              [schema.DomainType.BODY]: 0,
              [schema.DomainType.MIND]: 0,
              [schema.DomainType.SPIRIT]: 0,
              [schema.DomainType.SOCIAL]: 0,
              [schema.DomainType.CRAFT]: 0,
              [schema.DomainType.AUTHORITY]: 0,
              [schema.DomainType.AWARENESS]: 0
            }
          },
          preferences: {
            [schema.DomainType.BODY]: 0,
            [schema.DomainType.MIND]: 0,
            [schema.DomainType.SPIRIT]: 0,
            [schema.DomainType.SOCIAL]: 0,
            [schema.DomainType.CRAFT]: 0,
            [schema.DomainType.AUTHORITY]: 0,
            [schema.DomainType.AWARENESS]: 0
          }
        };
      }
      
      if (!gameState.character.shadowProfile) {
        return res.status(500).json({ error: "Failed to initialize shadow profile" });
      }
      
      // Check if this is the first interaction with this NPC
      const isFirstEncounter = !npc.knownInteractions || npc.knownInteractions.length === 0 || npc.firstEncounter === true;
      
      // Prepare shadow profile for NPC interaction
      const npcShadowProfile = {
        domains: gameState.character.shadowProfile.domainUsage,
        recentTags: [...detectedTags, ...(gameState.character.shadowProfile.recentTags || [])].slice(0, 5),
        firstEncounter: isFirstEncounter
      };
      
      // Generate NPC response based on character's domain usage
      const npcResponse = await generateNpcResponse(
        npc.name,
        npcShadowProfile,
        validatedData.playerAction,
        validatedData.model
      );
      
      // Update shadow profile with new tags and interactions
      const updatedShadowProfile = {
        ...gameState.character.shadowProfile,
        recentTags: [
          ...detectedTags.slice(0, 2),
          ...(gameState.character.shadowProfile.recentTags || [])
        ].slice(0, 10) // Keep only the 10 most recent tags
      };
      
      // Update NPC interaction history
      const updatedNpc = {
        ...npc,
        knownInteractions: [
          ...(npc.knownInteractions || []),
          validatedData.playerAction
        ],
        firstEncounter: false // Mark as not first encounter anymore
      };
      
      // Get the domain preferences from detected tags
      if (detectedTags.length > 0) {
        const inferredDomains = [];
        
        for (const tag of detectedTags) {
          // Look up domains for this tag in our mapping
          const domains = [];
          
          // This is a simplified example - in a real implementation,
          // you would use the full tag to domain mapping
          if (tag.includes("craft") || tag.includes("make") || tag.includes("build")) {
            domains.push(schema.DomainType.CRAFT);
          } else if (tag.includes("talk") || tag.includes("persuade") || tag.includes("convince")) {
            domains.push(schema.DomainType.SOCIAL);
          } else if (tag.includes("fight") || tag.includes("strength") || tag.includes("endure")) {
            domains.push(schema.DomainType.BODY);
          } else if (tag.includes("think") || tag.includes("study") || tag.includes("analyze")) {
            domains.push(schema.DomainType.MIND);
          } else if (tag.includes("feel") || tag.includes("sense") || tag.includes("spirit")) {
            domains.push(schema.DomainType.SPIRIT);
          } else if (tag.includes("command") || tag.includes("lead") || tag.includes("order")) {
            domains.push(schema.DomainType.AUTHORITY);
          } else if (tag.includes("notice") || tag.includes("see") || tag.includes("observe")) {
            domains.push(schema.DomainType.AWARENESS);
          }
          
          inferredDomains.push(...domains);
        }
        
        // Increment domain usage based on inferred domains
        if (updatedShadowProfile.domainUsage) {
          for (const domain of inferredDomains) {
            updatedShadowProfile.domainUsage = updateShadowProfile(
              updatedShadowProfile.domainUsage,
              domain,
              1
            );
          }
        }
      }
      
      // Update the game state with new shadow profile
      const updatedGameState: schema.GameState = {
        ...gameState,
        character: {
          ...gameState.character,
          shadowProfile: updatedShadowProfile as schema.ShadowProfile
        },
        location: {
          ...gameState.location,
          npcs: gameState.location.npcs.map(currentNpc => 
            currentNpc.id === npc.id ? updatedNpc : currentNpc
          )
        }
      };
      
      // Save updated game state
      await storage.saveGameState(updatedGameState);
      
      // Store the interaction in memory
      await memoryManager.addMemory(
        validatedData.gameId,
        "npc_interaction",
        `Interaction with ${npc.name}: ${validatedData.playerAction} → ${npcResponse}`
      );
      
      res.status(200).json({
        npcId: npc.id,
        npcName: npc.name,
        response: npcResponse,
        detectedTags,
        firstEncounter: isFirstEncounter,
        dominantDomains: Object.entries(updatedShadowProfile.domainUsage)
          .sort(([, valueA], [, valueB]) => valueB - valueA)
          .slice(0, 3)
          .map(([domain]) => domain)
      });
    } catch (error) {
      console.error("Error processing NPC interaction:", error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      
      res.status(500).json({ error: "Failed to process NPC interaction" });
    }
  });

  // WebSocket setup for real-time updates
  const httpServer = createServer(app);
  
  // Setup WebSocket server on a separate path from Vite's WebSocket
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  
  // Extend WebSocket with gameId property
  interface GameWebSocket extends WebSocket {
    gameId?: string;
  }
  
  wss.on('connection', (ws: WebSocket) => {
    const gameSocket = ws as GameWebSocket;
    console.log('WebSocket client connected');
    
    ws.addEventListener('message', async (event) => {
      try {
        const data = JSON.parse(event.data.toString());
        
        if (data.type === 'subscribe_game') {
          // Subscribe to game updates
          gameSocket.gameId = data.gameId;
          ws.send(JSON.stringify({ type: 'subscribed', gameId: data.gameId }));
        } else if (data.type === 'domain_action') {
          // Process domain-based action
          const { gameId, domain, tag, action, difficulty } = data;
          
          // Get current game state
          const gameState = await storage.getGameState(gameId);
          
          if (!gameState || !gameState.character) {
            ws.send(JSON.stringify({ 
              type: 'error', 
              message: 'Game or character not found' 
            }));
            return;
          }
          
          // Safely access domain value with proper type checking
          let domainValue = 0;
          if (gameState.character.domains && 
              typeof domain === 'string' && 
              domain in gameState.character.domains) {
            domainValue = gameState.character.domains[domain as schema.DomainType]?.value || 0;
          }
          
          // Simulate domain check (in real implementation, this would call the Python backend)
          const roll = Math.floor(Math.random() * 20) + 1; // d20 roll
          const tagValue = tag && gameState.character.tags && tag in gameState.character.tags 
            ? (gameState.character.tags[tag]?.rank || 0) 
            : 0;
          const total = roll + domainValue + tagValue;
          const success = total >= (difficulty || 10);
          
          // Update shadow profile domain usage if it exists
          if (gameState.character.shadowProfile && gameState.character.shadowProfile.domainUsage) {
            if (typeof domain === 'string' && Object.values(schema.DomainType).includes(domain as schema.DomainType)) {
              const typedDomain = domain as schema.DomainType;
              
              const updatedDomainUsage = updateShadowProfile(
                gameState.character.shadowProfile.domainUsage,
                typedDomain,
                1
              );
              
              // Update shadow profile
              gameState.character.shadowProfile.domainUsage = updatedDomainUsage;
              
              // Add to recent tags if a tag was used
              if (tag) {
                gameState.character.shadowProfile.recentTags = [
                  tag,
                  ...(gameState.character.shadowProfile.recentTags || [])
                ].slice(0, 10);
              }
              
              // Save game state with updated shadow profile
              await storage.saveGameState(gameState);
            }
          }
          
          // Send the result back to the client
          ws.send(JSON.stringify({
            type: 'domain_action_result',
            domain,
            tag,
            action,
            roll,
            domainValue,
            tagValue,
            total,
            difficulty: difficulty || 10,
            success,
            timestamp: new Date().toISOString()
          }));
        }
      } catch (error) {
        console.error('WebSocket message processing error:', error);
        ws.send(JSON.stringify({ type: 'error', message: 'Failed to process message' }));
      }
    });
    
    ws.addEventListener('close', () => {
      console.log('WebSocket client disconnected');
    });
  });
  
  // Broadcast game updates to subscribed clients
  const broadcastGameUpdate = (gameId: string, update: any) => {
    wss.clients.forEach(client => {
      if (client.readyState === 1 && (client as any).gameId === gameId) {
        client.send(JSON.stringify({
          type: 'game_update',
          gameId,
          update
        }));
      }
    });
  };

  return httpServer;
}
