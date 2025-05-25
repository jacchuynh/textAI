"""
Crafting API Package

This package provides access to the crafting system API.
"""

from backend.src.crafting.api.crafting_api import CraftingAPI, crafting_api

# Export the API class and instance
__all__ = ["CraftingAPI", "crafting_api"]