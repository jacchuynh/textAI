# Magic System Implementation Plan
## Comprehensive AI Assistant Implementation Guide

### Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Magic System Architecture](#magic-system-architecture)
4. [Integration Points](#integration-points)
5. [Implementation Phases](#implementation-phases)
6. [Technical Specifications](#technical-specifications)
7. [Development Timeline](#development-timeline)

---

## Overview

This document outlines a comprehensive implementation plan for building a dynamic, engaging magic system that integrates seamlessly with the existing domain system, combat system, crafting system, and NPC system. The magic system will feature three distinct tiers of magical practice, domain-based progression, and rich narrative integration.

### Key Features
- **Three-Tier Magic System**: Spiritual Utility, Mana Infusion, Arcane Mastery
- **Domain Integration**: Magic skills tied to the 7-domain progression system
- **Dynamic Effects**: Context-aware magical abilities that respond to world state
- **Combat Integration**: Magical combat moves and enchanted items
- **Crafting Synergy**: Enchantment recipes and magical item creation
- **NPC Magic**: NPCs with their own magical abilities and reactions
- **Narrative Integration**: AI GM Brain enhancement for magical storytelling

---

## Project Structure

```
app/
├── models/
│   ├── magic_models.py           # Core Pydantic models
│   └── magic_enums.py           # Magic-specific enumerations
├── services/
│   └── magic/
│       ├── __init__.py
│       ├── magic_service.py      # Core magic operations
│       ├── spell_service.py      # Spell casting and effects
│       ├── enchantment_service.py # Item enchantment
│       └── mana_service.py       # Mana heart and energy management
├── db/
│   └── magic_models.py          # SQLAlchemy database models
├── api/
│   └── magic_api.py             # API endpoints for magic operations
├── events/
│   └── magic_events.py          # Magic-specific event types
└── storage/
    └── magic_storage.py         # Magic data persistence

ai_gm_brain/
├── magic_integration.py         # AI GM Brain magic integration
└── templates/
    └── magic_templates.py       # Magic narrative templates

game_engine/
└── magic_combat/
    ├── magic_moves.py           # Magical combat moves
    └── magic_effects.py         # Combat magic effects
```

---

## Magic System Architecture

### Core Enums

```python
class MagicSource(str, Enum):
    """Sources of magical power"""
    DOMAIN_RESONANCE = "domain_resonance"    # Tied to domain system
    MANA_HEART = "mana_heart"               # Internal energy cultivation
    ARCANE_STUDY = "arcane_study"           # Academic magical knowledge
    DIVINE_FAVOR = "divine_favor"           # Spirit domain enhancement
    ELEMENTAL_PACT = "elemental_pact"       # Environmental magic
    ARTIFACT_CHANNEL = "artifact_channel"    # Magic through items

class MagicTier(str, Enum):
    """Tiers of magical practice"""
    SPIRITUAL_UTILITY = "spiritual_utility"  # Tier 1: Basic life enhancement
    MANA_INFUSION = "mana_infusion"         # Tier 2: Energy manipulation
    ARCANE_MASTERY = "arcane_mastery"       # Tier 3: Reality manipulation

class MagicSchool(str, Enum):
    """Schools of magical practice"""
    # Tier 1 - Spiritual Utility
    ENHANCEMENT = "enhancement"              # Body/performance improvements
    DIVINATION = "divination"               # Information gathering
    COMMUNION = "communion"                 # Social/spiritual connections
    
    # Tier 2 - Mana Infusion
    ELEMENTAL = "elemental"                 # Fire, ice, lightning, earth
    TRANSMUTATION = "transmutation"         # Matter manipulation
    WARD = "ward"                          # Protection and barriers
    
    # Tier 3 - Arcane Mastery
    REALITY_WEAVING = "reality_weaving"     # Fundamental reality changes
    TEMPORAL = "temporal"                   # Time manipulation
    DIMENSIONAL = "dimensional"             # Space and plane shifting

class ManaHeartStage(str, Enum):
    """Stages of mana heart development"""
    DORMANT = "dormant"                     # No mana heart
    AWAKENING = "awakening"                 # Initial development
    FLOWING = "flowing"                     # Basic mana circulation
    RESERVOIR = "reservoir"                 # Expanded capacity
    TORRENT = "torrent"                     # High-power output
    TRANSCENDENT = "transcendent"           # Beyond normal limits
```

### Core Models

```python
class MagicProfile(BaseModel):
    """Base magic profile for characters"""
    character_id: str
    magic_tier: MagicTier = MagicTier.SPIRITUAL_UTILITY
    mana_heart_stage: ManaHeartStage = ManaHeartStage.DORMANT
    
    # Magic sources and their strength
    magic_sources: Dict[MagicSource, float] = Field(default_factory=dict)
    
    # School proficiencies (0.0 to 1.0)
    school_proficiencies: Dict[MagicSchool, float] = Field(default_factory=dict)
    
    # Current magical state
    current_mana: int = 0
    max_mana: int = 0
    mana_regeneration_rate: float = 1.0
    
    # Known spells and abilities
    known_spells: List[str] = Field(default_factory=list)
    active_effects: Dict[str, "ActiveMagicEffect"] = Field(default_factory=dict)
    
    # Magical corruption and limitations
    corruption_level: float = 0.0
    corruption_effects: List[str] = Field(default_factory=list)

class Spell(BaseModel):
    """Individual spell definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    school: MagicSchool
    tier: MagicTier
    
    # Requirements
    required_domain_levels: Dict[DomainType, int] = Field(default_factory=dict)
    required_sources: Dict[MagicSource, float] = Field(default_factory=dict)
    mana_cost: int = 0
    
    # Effects and mechanics
    effect_type: str  # "enhancement", "damage", "utility", "social"
    base_power: float = 1.0
    duration_seconds: Optional[int] = None
    range_meters: Optional[float] = None
    
    # Domain scaling
    domain_scaling: Dict[DomainType, float] = Field(default_factory=dict)
    
    # Special properties
    requires_components: List[str] = Field(default_factory=list)
    has_verbal_component: bool = True
    has_somatic_component: bool = True
    corruption_risk: float = 0.0

class EnchantmentRecipe(BaseModel):
    """Recipe for enchanting items"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Requirements
    required_craft_level: int = 1
    required_schools: Dict[MagicSchool, float] = Field(default_factory=dict)
    required_items: List[str] = Field(default_factory=list)  # Item IDs
    
    # Output
    enchantment_effects: List[str] = Field(default_factory=list)
    success_rate_base: float = 0.7
    
    # Domain influences
    primary_domains: List[DomainType] = Field(default_factory=list)
```

---

## Integration Points

### 1. Domain System Integration

The magic system will tie directly into the existing domain system:

**Magic-Domain Mappings:**
- **Body Domain**: Enhancement magic, physical transmutation, healing
- **Mind Domain**: Divination, mental effects, complex spell patterns
- **Spirit Domain**: Divine magic, mana heart development, communion
- **Social Domain**: Charm effects, group magic, social divination
- **Craft Domain**: Enchantment, magical item creation, alchemical magic
- **Authority Domain**: Command magic, ward creation, protective spells
- **Awareness Domain**: Detection magic, environmental sensing, combat timing

**Domain Check Integration:**
```python
def cast_spell(character: Character, spell: Spell, target=None) -> Dict[str, Any]:
    """Cast a spell using domain checks"""
    # Determine primary domain for the spell
    primary_domain = get_spell_primary_domain(spell)
    
    # Calculate difficulty based on spell tier and character progression
    base_difficulty = 10 + (spell.tier.value * 3)
    
    # Perform domain check
    result = character.roll_check(
        domain_type=primary_domain,
        tag_name=f"magic_{spell.school.value}",
        difficulty=base_difficulty
    )
    
    # Apply magic-specific modifiers
    magic_profile = get_character_magic_profile(character.id)
    school_bonus = magic_profile.school_proficiencies.get(spell.school, 0) * 5
    
    final_success = result["total"] + school_bonus >= base_difficulty
    
    return execute_spell_effect(spell, character, target, final_success, result["margin"])
```

### 2. Combat System Integration

Magic will integrate with the existing combat system through specialized combat moves:

```python
class MagicCombatMove(CombatMove):
    """Combat move that uses magic"""
    spell_id: str
    mana_cost: int
    corruption_risk: float = 0.0
    
    # Override domains to include magic-relevant ones
    magic_domains: List[DomainType] = Field(default_factory=list)
    
    def can_use(self, character: Character) -> Tuple[bool, str]:
        """Check if character can use this magic move"""
        magic_profile = get_character_magic_profile(character.id)
        
        if magic_profile.current_mana < self.mana_cost:
            return False, "Insufficient mana"
            
        if not self.spell_id in magic_profile.known_spells:
            return False, "Spell not known"
            
        return super().can_use(character)

class MagicalCombatEffect(BaseModel):
    """Magical effects that persist during combat"""
    effect_id: str
    source_spell: str
    duration_rounds: int
    
    # Effect modifiers
    damage_modifier: float = 1.0
    defense_modifier: float = 1.0
    speed_modifier: float = 1.0
    
    # Special properties
    prevents_actions: List[str] = Field(default_factory=list)
    grants_abilities: List[str] = Field(default_factory=list)
```

### 3. Event Bus Integration

Magic events will integrate with the existing event system:

```python
class MagicEventType(str, Enum):
    SPELL_CAST = "spell_cast"
    SPELL_LEARNED = "spell_learned"
    MANA_HEART_ADVANCED = "mana_heart_advanced"
    ENCHANTMENT_CREATED = "enchantment_created"
    MAGIC_CORRUPTION_GAINED = "magic_corruption_gained"
    MAGICAL_DISCOVERY = "magical_discovery"

# Example event publishing
event_bus.publish(GameEvent(
    type=MagicEventType.SPELL_CAST,
    actor=character.id,
    context={
        "spell_id": spell.id,
        "spell_name": spell.name,
        "success": cast_result["success"],
        "mana_spent": spell.mana_cost,
        "school": spell.school.value
    },
    tags=["magic", spell.school.value, "spellcasting"]
))
```

### 4. AI GM Brain Integration

The magic system will enhance the AI GM Brain with magical context:

```python
class MagicNarrativeIntegration:
    """Integrates magic system with AI GM narrative generation"""
    
    def enhance_narrative_context(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Add magical context to narrative generation"""
        character = base_context.get("character")
        if not character:
            return base_context
            
        magic_profile = get_character_magic_profile(character.id)
        
        enhanced_context = base_context.copy()
        enhanced_context["magic_context"] = {
            "tier": magic_profile.magic_tier.value,
            "mana_heart_stage": magic_profile.mana_heart_stage.value,
            "active_effects": list(magic_profile.active_effects.keys()),
            "known_schools": [school.value for school, prof in 
                            magic_profile.school_proficiencies.items() if prof > 0.1],
            "corruption_level": magic_profile.corruption_level
        }
        
        return enhanced_context
    
    def generate_magical_ambient_content(self, location_context: Dict[str, Any]) -> Optional[str]:
        """Generate ambient magical content based on location"""
        magic_density = location_context.get("magic_density", 0.0)
        
        if magic_density > 0.7:
            return random.choice([
                "The air shimmers with barely contained magical energy.",
                "You feel the ebb and flow of mana currents around you.",
                "Wisps of ethereal light dance at the edge of your vision."
            ])
        elif magic_density > 0.3:
            return random.choice([
                "There's a subtle tingle in the air that suggests magical presence.",
                "You sense faint magical resonances in the area."
            ])
        
        return None
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Deliverables:**
- Core magic models and enums
- Basic magic profile system
- Magic-domain integration framework
- Initial database schema

**Key Tasks:**
1. Create `magic_models.py` with all core Pydantic models
2. Implement `MagicService` with basic profile management
3. Set up database models in `magic_models.py` (SQLAlchemy)
4. Create basic magic-domain integration functions
5. Write unit tests for core functionality

**Code Example - Core Service:**
```python
class MagicService:
    def __init__(self):
        self.magic_profiles: Dict[str, MagicProfile] = {}
        
    def get_or_create_magic_profile(self, character_id: str) -> MagicProfile:
        """Get existing magic profile or create new one"""
        if character_id not in self.magic_profiles:
            self.magic_profiles[character_id] = MagicProfile(
                character_id=character_id
            )
        return self.magic_profiles[character_id]
    
    def can_advance_tier(self, character_id: str) -> Tuple[bool, str]:
        """Check if character can advance to next magic tier"""
        profile = self.get_or_create_magic_profile(character_id)
        character = get_character(character_id)
        
        if profile.magic_tier == MagicTier.SPIRITUAL_UTILITY:
            # Require Mind 3+ and Spirit 3+ for Mana Infusion
            if character.domains[DomainType.MIND].value >= 3 and \
               character.domains[DomainType.SPIRIT].value >= 3:
                return True, "Ready to advance to Mana Infusion"
            return False, "Requires Mind 3+ and Spirit 3+"
            
        elif profile.magic_tier == MagicTier.MANA_INFUSION:
            # Require multiple high domains for Arcane Mastery
            high_domains = sum(1 for d in character.domains.values() if d.value >= 5)
            if high_domains >= 3:
                return True, "Ready to advance to Arcane Mastery"
            return False, "Requires 3+ domains at level 5+"
            
        return False, "Already at maximum tier"
```

### Phase 2: Domain Integration (Weeks 3-4)
**Deliverables:**
- Domain-magic synergy system
- Spell learning mechanics
- Basic spell casting framework
- Magic progression tracking

**Key Tasks:**
1. Implement domain-based spell learning
2. Create spell effectiveness calculations
3. Build magic progression system
4. Integrate with existing domain growth mechanics
5. Add magic-specific growth log entries

### Phase 3: Spell System (Weeks 5-6)
**Deliverables:**
- Complete spell database
- Spell casting mechanics
- Effect duration and stacking system
- Mana management

**Key Tasks:**
1. Create comprehensive spell library
2. Implement spell effect system
3. Build mana heart progression
4. Add spell failure and corruption mechanics
5. Create spell combination system

### Phase 4: Combat Integration (Weeks 7-8)
**Deliverables:**
- Magical combat moves
- Combat magic effects
- Magic-enhanced weapons/armor
- Combat spell targeting

**Key Tasks:**
1. Extend combat system with magic moves
2. Implement magical combat effects
3. Add spell resistance and counterspells
4. Create tactical magic combat options
5. Balance magical vs non-magical combat

### Phase 5: Enchantment System (Weeks 9-10)
**Deliverables:**
- Item enchantment mechanics
- Enchantment recipes
- Magical item creation
- Enchantment degradation

**Key Tasks:**
1. Build enchantment crafting system
2. Create magical item effects
3. Implement enchantment failure mechanics
4. Add temporary vs permanent enchantments
5. Integrate with existing crafting system

### Phase 6: NPC Magic (Weeks 11-12)
**Deliverables:**
- NPC magic profiles
- Magic-using NPCs
- Magical creature abilities
- Magic-based social interactions

**Key Tasks:**
1. Create NPC magic profile system
2. Implement magical NPCs and creatures
3. Add magic-based dialogue and social effects
4. Create magical faction systems
5. Build magic-influenced NPC behaviors

### Phase 7: AI GM Integration (Weeks 13-14)
**Deliverables:**
- Magic narrative integration
- Magical world events
- Dynamic magic environments
- Magic-enhanced storytelling

**Key Tasks:**
1. Integrate magic with AI GM Brain
2. Create magical narrative templates
3. Implement dynamic magical environments
4. Add magic-triggered world events
5. Build magical lore and discovery system

### Phase 8: Polish and Balance (Weeks 15-16)
**Deliverables:**
- Balanced magic system
- Performance optimization
- Complete documentation
- Integration testing

**Key Tasks:**
1. Balance all magical abilities
2. Optimize performance and caching
3. Add comprehensive error handling
4. Create admin tools for magic management
5. Write complete documentation

---

## Technical Specifications

### Database Schema

```sql
-- Core magic profiles table
CREATE TABLE magic_profiles (
    character_id VARCHAR PRIMARY KEY,
    magic_tier VARCHAR NOT NULL DEFAULT 'spiritual_utility',
    mana_heart_stage VARCHAR NOT NULL DEFAULT 'dormant',
    current_mana INTEGER DEFAULT 0,
    max_mana INTEGER DEFAULT 0,
    mana_regeneration_rate FLOAT DEFAULT 1.0,
    corruption_level FLOAT DEFAULT 0.0,
    magic_sources JSON,  -- Dict[MagicSource, float]
    school_proficiencies JSON,  -- Dict[MagicSchool, float]
    known_spells JSON,  -- List[str]
    corruption_effects JSON,  -- List[str]
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Active magic effects table
CREATE TABLE active_magic_effects (
    id VARCHAR PRIMARY KEY,
    character_id VARCHAR NOT NULL,
    effect_name VARCHAR NOT NULL,
    source_spell VARCHAR,
    duration_remaining INTEGER,
    effect_data JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (character_id) REFERENCES magic_profiles(character_id)
);

-- Spell library table
CREATE TABLE spells (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    school VARCHAR NOT NULL,
    tier VARCHAR NOT NULL,
    mana_cost INTEGER DEFAULT 0,
    effect_type VARCHAR NOT NULL,
    base_power FLOAT DEFAULT 1.0,
    duration_seconds INTEGER,
    range_meters FLOAT,
    required_domain_levels JSON,
    required_sources JSON,
    domain_scaling JSON,
    special_properties JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

magic_router = APIRouter(prefix="/magic", tags=["magic"])

@magic_router.get("/profile/{character_id}")
async def get_magic_profile(character_id: str) -> MagicProfile:
    """Get character's magic profile"""
    profile = magic_service.get_magic_profile(character_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Magic profile not found")
    return profile

@magic_router.post("/cast-spell")
async def cast_spell(
    character_id: str,
    spell_id: str,
    target_id: Optional[str] = None
) -> Dict[str, Any]:
    """Cast a spell"""
    result = magic_service.cast_spell(character_id, spell_id, target_id)
    return result

@magic_router.post("/learn-spell")
async def learn_spell(character_id: str, spell_id: str) -> Dict[str, Any]:
    """Attempt to learn a new spell"""
    result = magic_service.learn_spell(character_id, spell_id)
    return result

@magic_router.get("/available-spells/{character_id}")
async def get_available_spells(character_id: str) -> List[Spell]:
    """Get spells character can potentially learn"""
    return magic_service.get_learnable_spells(character_id)

@magic_router.post("/enchant-item")
async def enchant_item(
    character_id: str,
    item_id: str,
    recipe_id: str
) -> Dict[str, Any]:
    """Enchant an item"""
    result = enchantment_service.enchant_item(character_id, item_id, recipe_id)
    return result
```

### Performance Considerations

1. **Caching Strategy:**
   - Cache frequently accessed magic profiles in Redis
   - Cache spell definitions and effects
   - Implement cache invalidation for profile updates

2. **Background Tasks:**
   - Mana regeneration handled by background tasks
   - Effect duration countdown in background
   - Corruption level adjustments over time

3. **Database Optimization:**
   - Index on character_id for magic_profiles
   - Index on effect expiration times
   - Batch updates for effect duration countdown

---

## Development Timeline

### Week 1-2: Foundation
- [ ] Core models and enums
- [ ] Database schema creation
- [ ] Basic service architecture
- [ ] Unit tests for core functionality

### Week 3-4: Domain Integration  
- [ ] Magic-domain synergy system
- [ ] Spell learning mechanics
- [ ] Progression tracking integration
- [ ] Domain check modifications

### Week 5-6: Spell System
- [ ] Spell database and definitions
- [ ] Casting mechanics
- [ ] Effect system implementation
- [ ] Mana heart progression

### Week 7-8: Combat Integration
- [ ] Magic combat moves
- [ ] Combat effect system
- [ ] Spell resistance mechanics
- [ ] Combat balance testing

### Week 9-10: Enchantment System
- [ ] Item enchantment mechanics
- [ ] Recipe system
- [ ] Crafting integration
- [ ] Magical item effects

### Week 11-12: NPC Magic
- [ ] NPC magic profiles
- [ ] Magical creature implementation
- [ ] Magic-based social interactions
- [ ] Faction magic systems

### Week 13-14: AI GM Integration
- [ ] Narrative enhancement
- [ ] Magic event generation
- [ ] Dynamic environments
- [ ] Lore and discovery system

### Week 15-16: Polish and Balance
- [ ] System balancing
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Final integration testing

---

## Conclusion

This implementation plan provides a comprehensive roadmap for building a sophisticated magic system that integrates seamlessly with your existing game architecture. The modular approach allows for iterative development while maintaining system consistency and performance.

The magic system will enhance player engagement through:
- **Progressive Complexity**: Three tiers allow natural character growth
- **Domain Integration**: Leverages existing progression mechanics
- **Rich Narrative**: AI GM integration for dynamic storytelling
- **Tactical Depth**: Combat and crafting applications
- **Social Dynamics**: NPC interactions and faction relationships

Each phase builds upon the previous ones, ensuring a stable foundation while gradually adding complexity and features. The final system will provide a rich, engaging magical experience that enhances all aspects of the game world.
