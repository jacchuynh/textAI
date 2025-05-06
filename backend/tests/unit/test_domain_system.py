import pytest
from backend.src.shared.models import Character, DomainType, Domain, Tag, TagCategory
from backend.src.game_engine.core import GameEngine


def test_character_creation():
    """Test basic character creation"""
    # Create a game engine
    engine = GameEngine()
    
    # Create a character
    character = engine.create_character("Test Character")
    
    # Verify the character has the correct structure
    assert character.name == "Test Character"
    assert len(character.domains) == 7  # All 7 domains should be initialized
    assert character.domains[DomainType.BODY].value == 2  # Starting value for BODY
    assert character.domains[DomainType.MIND].value == 2  # Starting value for MIND
    assert character.domains[DomainType.SOCIAL].value == 1  # Starting value for SOCIAL
    assert character.domains[DomainType.AWARENESS].value == 1  # Starting value for AWARENESS
    
    # Check if character has the default tags
    assert "melee" in character.tags
    assert "persuasion" in character.tags


def test_domain_check():
    """Test domain check mechanic"""
    # Create a character manually for controlled testing
    character = Character(name="Test Character")
    
    # Set fixed domain values
    character.domains[DomainType.BODY].value = 3
    
    # Add a tag
    character.tags["melee"] = Tag(
        name="Melee",
        category=TagCategory.COMBAT,
        description="Close-quarters combat with weapons",
        domains=[DomainType.BODY, DomainType.AWARENESS],
        rank=2  # Rank 2 in melee
    )
    
    # Mock the random roll to a fixed value for testing
    import random
    original_randint = random.randint
    random.randint = lambda a, b: 10  # Always roll a 10
    
    # Perform a check
    result = character.roll_check(DomainType.BODY, "melee", 15)
    
    # Restore the original randint function
    random.randint = original_randint
    
    # Verify the result
    assert result["roll"] == 10
    assert result["domain_bonus"] == 3
    assert result["tag_bonus"] == 2
    assert result["total"] == 15  # 10 (roll) + 3 (body) + 2 (melee)
    assert result["success"] == True  # Total equals the DC
    assert result["margin"] == 0


def test_domain_drift():
    """Test domain drift mechanic"""
    character = Character(name="Test Character")
    
    # Set initial domain values
    character.domains[DomainType.BODY].value = 3
    character.domains[DomainType.MIND].value = 1
    
    # Track usage
    for _ in range(10):
        character.domains[DomainType.BODY].use(True)
    
    for _ in range(2):
        character.domains[DomainType.MIND].use(True)
    
    # Get drift candidates
    drift_candidates = character.get_domain_drift_candidates()
    
    # Verify that MIND is not in the least used (since we used it less)
    assert DomainType.MIND not in drift_candidates
    
    # Apply drift
    result = character.drift_domain(DomainType.BODY, DomainType.MIND)
    
    # Verify the drift worked
    assert result == True
    assert character.domains[DomainType.BODY].value == 2  # Decreased by 1
    assert character.domains[DomainType.MIND].value == 2  # Increased by 1