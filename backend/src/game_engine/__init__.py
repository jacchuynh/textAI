"""
Game Engine module that handles game mechanics and simulation.
"""

from .domain_system import domain_system
# Import other systems as they're implemented
# from .combat_system import combat_system
# from .crafting_system import crafting_system
# from .economy_system import economy_system
# from .basebuilding_system import basebuilding_system
# from .kingdom_system import kingdom_system

__all__ = ["domain_system"]