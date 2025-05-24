
"""
Economy API endpoints.

This module handles API routes for economic interactions, such as
buying/selling items, managing businesses, and market activities.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ..game_engine.economy_system import economy_system

router = APIRouter(prefix="/economy", tags=["economy"])

# Request models
class MarketEntryRequest(BaseModel):
    character_id: str
    market_name: str

class ShopBrowseRequest(BaseModel):
    character_id: str
    shop_name: str

class ItemTransactionRequest(BaseModel):
    character_id: str
    shop_name: str
    item_name: str
    quantity: int = 1

class BusinessCreationRequest(BaseModel):
    character_id: str
    business_name: str
    business_type: str
    city: str

class BusinessCheckRequest(BaseModel):
    character_id: str
    business_name: str

class WorkerHireRequest(BaseModel):
    character_id: str
    business_name: str
    worker_name: str
    worker_class: str

class CaravanRequest(BaseModel):
    character_id: str
    origin_city: str
    destination_city: str
    goods: List[Dict[str, Any]]

class MarketReportRequest(BaseModel):
    character_id: str
    city: str

class MarketManipulationRequest(BaseModel):
    character_id: str
    city: str
    action: str
    target: str

# Routes
@router.post("/enter-market")
async def enter_market(request: MarketEntryRequest):
    """Enter a market in a city."""
    result = economy_system.enter_market(request.character_id, request.market_name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/browse-shop")
async def browse_shop(request: ShopBrowseRequest):
    """Browse items in a shop."""
    result = economy_system.browse_shop(request.character_id, request.shop_name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/buy-item")
async def buy_item(request: ItemTransactionRequest):
    """Buy an item from a shop."""
    result = economy_system.buy_item(
        request.character_id, 
        request.shop_name, 
        request.item_name, 
        request.quantity
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/sell-item")
async def sell_item(request: ItemTransactionRequest):
    """Sell an item to a shop."""
    result = economy_system.sell_item(
        request.character_id, 
        request.shop_name, 
        request.item_name, 
        request.quantity
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/open-business")
async def open_business(request: BusinessCreationRequest):
    """Open a new business."""
    result = economy_system.open_business(
        request.character_id,
        request.business_name,
        request.business_type,
        request.city
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/check-business")
async def check_business(request: BusinessCheckRequest):
    """Check status of a business."""
    result = economy_system.check_business(request.character_id, request.business_name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/hire-worker")
async def hire_worker(request: WorkerHireRequest):
    """Hire a worker for a business."""
    result = economy_system.hire_worker(
        request.character_id,
        request.business_name,
        request.worker_name,
        request.worker_class
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/send-caravan")
async def send_caravan(request: CaravanRequest):
    """Send a caravan between cities."""
    result = economy_system.send_caravan(
        request.character_id,
        request.origin_city,
        request.destination_city,
        request.goods
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/market-report")
async def view_market_report(request: MarketReportRequest):
    """View market report for a city."""
    result = economy_system.view_market_report(request.character_id, request.city)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/manipulate-market")
async def manipulate_market(request: MarketManipulationRequest):
    """Attempt to manipulate a market."""
    result = economy_system.manipulate_market(
        request.character_id,
        request.city,
        request.action,
        request.target
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
