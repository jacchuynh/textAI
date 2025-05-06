import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { GameEngine } from "./game-engine";
import { AIService } from "./ai-service";
import { MemoryManager } from "./memory";
import * as schema from "@shared/types";
import { z } from "zod";

const gameEngine = new GameEngine();
const aiService = new AIService();
const memoryManager = new MemoryManager();

export async function registerRoutes(app: Express): Promise<Server> {
  // Initialize the API
  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
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

  const httpServer = createServer(app);

  return httpServer;
}
