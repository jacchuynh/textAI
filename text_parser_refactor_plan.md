# Implementation Plan: Modular Text Parser & Intent Execution System

This plan outlines the steps to refactor the existing text parsing system in `backend/src/text_parser/parser_engine.py` to remove LangChain agents and implement a new modular architecture.

**Overall Architecture:**

```mermaid
graph TD
    A[Player Input] --> B(Phase 1: Text Parser);
    B -- ParsedCommand --> C(Phase 2: Intent Router);
    C -- Intent + ParsedCommand + GameContext --> D(Phase 3: Manual Tool Execution);
    D -- Tool Result + GameContext --> E(Phase 4: Prompt Injection);
    E -- Crafted Prompt --> F(Phase 5: LLM Call for Roleplay);
    F -- LLM Response --> G[AI Narration Output];

    subgraph Game Systems & Data
        H[Game Logic/State (PostgreSQL/JSON)];
        I[spaCy + Custom Rules];
        J[RAG System (FAISS/ChromaDB + Embeddings)];
        K[GameContext];
        L[Action Executor (e.g., expanded parser_integrator.py)];
    end

    B --> I;
    D --> H;
    D --> K;
    D --> L;
    E --> K;
    E --> J; 
```

---

### **Phase 0: Preparation & Setup**

1.  **Backup:** Create a backup or branch of the current `backend/src/text_parser/` directory.
2.  **New Files (Placeholders):**
    *   Create `backend/src/text_parser/intent_router.py`.
    *   Create `backend/src/text_parser/prompt_builder.py` (for Phase 4).
    *   Create `backend/src/text_parser/llm_roleplayer.py` (for Phase 5).
    *   The existing `backend/src/text_parser/parser_integrator.py` will be expanded to serve as the "Action Executor" or a new module like `action_executor.py` will be created.
3.  **Constants/Configuration:** Define a place for core intents and sub-intents (e.g., in `intent_router.py` or a shared constants file).

---

### **Phase 1: Text Parser Layer (spaCy + Rules)**

**Location:** Primarily `backend/src/text_parser/parser_engine.py` (modifying `ParserEngine.parse` method).

**Tasks:**

1.  **Modify `ParserEngine.parse()` method:**
    *   **Remove LangChain Agent Invocation:** Delete the fallback logic that uses `self.agent_executor.invoke()` and `self._convert_langchain_to_parsed_command()`.
    *   **Remove `LangChainParserEnhancer` Usage:** The current `self.langchain_enhancer` (using `FantasyLLM`) will be removed as primary parsing will shift to spaCy and rules.
    *   **Focus on spaCy + EntityRuler + Regex:**
        *   Leverage existing spaCy initialization (`self.nlp`, `self.ruler`).
        *   Enhance `_init_entity_ruler_patterns()` and `_init_patterns()` to cover more actions, entities, and command structures.
        *   Populate the `ParsedCommand` object robustly using these rule-based methods.
    *   **Output:** The `parse()` method should return a `ParsedCommand` object.
        *   Specific parameters like "topic," "location," etc., will be stored in `ParsedCommand.modifiers`.
        *   Example: `ParsedCommand(action="ask", target="tavern keeper", modifiers={"topic": "room cost", "location": "tavern"}, raw_text="ask the tavern keeper about the room cost", confidence=0.85, context={...})`
    *   **GameContext Integration:** Utilize the global `game_context` for disambiguation.
2.  **`ParsedCommand` Dataclass:** The existing `ParsedCommand` dataclass is suitable.
3.  **RAG Integration (Initial):**
    *   Review existing RAG integration (`_init_rag_components()`, `_extract_intents_with_rag()`).
    *   The RAG system's role will shift to providing contextual information for prompt building (Phase 4) and memory (Phase 6).
    *   The logic in `enhanced_rag_optimizer.py` and `enhanced_rag_parser_integration.py` will be adapted. RAG enrichment might occur after initial spaCy/rules parsing to augment `ParsedCommand.context`.

---

### **Phase 2: Intent Router**

**Location:** New file `backend/src/text_parser/intent_router.py`.

**Tasks:**

1.  **Create `IntentRouter` class:**
    *   **Input:** `ParsedCommand` object (from Phase 1) and `GameContext` object.
    *   **Hierarchical Intents:** Define primary intents and more specific sub-intents (e.g., `P_INTERACT` -> `S_INTERACT_NPC_TALK`, `S_INTERACT_ITEM_USE_ON_TARGET`).
    *   **Routing Logic:** Implement `route_intent(parsed_command: ParsedCommand, game_context: GameContext) -> str`.
        *   Use `parsed_command.action`, `target`, `modifiers`, and `game_context` to map to a specific sub-intent string.
        *   Employ context-aware rules and prioritized matching.
        *   Handle disambiguation, potentially routing to a `REQUEST_DISAMBIGUATION` intent if needed.
        *   Consider simple stateful routing for multi-turn interactions using `GameContext`.
    *   **Output:** A specific sub-intent string (e.g., `"S_INTERACT_NPC_TALK"`).

---

### **Phase 3: Manual Tool Execution**

**Location:** Logic consolidated into an expanded `backend/src/text_parser/parser_integrator.py` (or a new module like `action_executor.py`). `GameSystemsManager` will be a key dependency.

**Tasks:**

1.  **Decompose `parser_engine.py` Tool Classes & Centralize Logic:**
    *   Remove `BaseTool` subclasses from `parser_engine.py`.
    *   Extract their core logic into standalone functions within the expanded `parser_integrator.py` (or `action_executor.py`).
    *   **Function Signature:** `def execute_action_xyz(parsed_command: ParsedCommand, game_context: GameContext, services: ServiceBundle) -> Dict[str, Any]:`
        *   `services` will bundle dependencies like `GameSystemsManager` and economic services.
    *   Functions return a Python dictionary ("Tool Result").
2.  **Refactor `ParserIntegrator` Economic Logic:**
    *   Adapt existing economic handlers (e.g., `_handle_crafting_command`) to the new function signature, becoming part of the central tool function registry.
    *   Regex patterns in `ParserIntegrator._initialize_command_patterns()` become redundant.
3.  **Tool Function Dispatch:**
    *   The `IntentRouter` (or a dedicated dispatcher class/module) will use a mapping to call the appropriate tool function from `parser_integrator.py` based on the sub-intent string.
    *   It passes `ParsedCommand`, `GameContext`, and the `services` bundle to the tool function.

---

### **Phase 4: Prompt Injection (Context Building)**

**Location:** New file `backend/src/text_parser/prompt_builder.py`.

**Tasks:**

1.  **Create `PromptBuilder` class:**
    *   **Input:** "Tool Result" (from Phase 3), `ParsedCommand`, `GameContext`.
    *   **Logic:**
        *   Access relevant info from `GameContext`, "Tool Result", and `ParsedCommand`.
        *   **RAG Integration for Memory:** Query RAG system for relevant NPC memory, player history, or world lore based on current context.
        *   Use Jinja2 or f-string templates to construct the final LLM prompt.
    *   **Output:** Fully formed string prompt.

---

### **Phase 5: LLM Roleplay Output**

**Location:** New file `backend/src/text_parser/llm_roleplayer.py`.

**Tasks:**

1.  **Create `LLMRoleplayer` class:**
    *   **Input:** Crafted prompt string from Phase 4.
    *   **LLM Interaction:**
        *   Use `httpx` for direct OpenRouter API calls.
        *   Refactor and reuse connection/model selection logic from the existing `OpenRouterLLM` class in `parser_engine.py` (without LangChain agent wrappers).
    *   **Output:** Raw LLM text response.

---

### **Phase 6: Optimization & Memory**

**Location:** Enhancements to RAG system (`parser_engine.py`, `enhanced_rag_optimizer.py`, `enhanced_rag_parser_integration.py`) and caching.

**Tasks:**

1.  **Cache Recent Tool Results:** Implement caching for frequently called tools.
2.  **Refine RAG System for Recall:**
    *   Ensure robustness of RAG components.
    *   `EnhancedRAGOptimizer` and `EnhancedRAGParserIntegration` logic will be adapted.
    *   `PromptBuilder` (Phase 4) will query RAG for relevant memories/lore.
    *   Focus RAG indexing on NPC dialogue, player actions, and world lore.
    *   Ensure only contextually relevant memory is injected.

---

### **Key Removals/Deprecations in `parser_engine.py`:**

*   All `BaseTool` subclasses (logic moved to `parser_integrator.py` or `action_executor.py`).
*   `_setup_langchain_agent()` method.
*   `self.agent_executor` attribute and its usage.
*   `_convert_langchain_to_parsed_command()` method.
*   `FantasyLLM` class (direct LLM calls handled in Phase 5).
*   `LangChainParserEnhancer` class.
*   `create_enhanced_langchain_tools()` function.
*   LangChain-specific imports related to agents.
*   `GameSystemsManager` might be instantiated at a higher level and passed as a dependency.

---