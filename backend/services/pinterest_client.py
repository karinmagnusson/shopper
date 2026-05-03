"""Pinterest API v5 client wrapper."""
import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PinterestClient:
    """Client for interacting with Pinterest API v5."""
    
    BASE_URL = "https://api.pinterest.com/v5"
    
    def __init__(self, access_token: str):
        """Initialize Pinterest client with user's access token."""
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_info(self) -> Dict:
        """Get authenticated user's account information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/user_account",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_boards(self, page_size: int = 25, bookmark: Optional[str] = None) -> Dict:
        """
        Get user's boards.
        
        Args:
            page_size: Number of boards to return (max 100)
            bookmark: Pagination cursor
            
        Returns:
            Dict with 'items' (list of boards) and 'bookmark' for next page
        """
        params = {"page_size": page_size}
        if bookmark:
            params["bookmark"] = bookmark
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_board_pins(
        self, 
        board_id: str, 
        page_size: int = 25, 
        bookmark: Optional[str] = None
    ) -> Dict:
        """
        Get pins from a specific board.
        
        Args:
            board_id: Board ID
            page_size: Number of pins to return (max 100)
            bookmark: Pagination cursor
            
        Returns:
            Dict with 'items' (list of pins) and 'bookmark' for next page
        """
        params = {"page_size": page_size}
        if bookmark:
            params["bookmark"] = bookmark
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards/{board_id}/pins",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_all_user_pins(self, max_pins: Optional[int] = None) -> List[Dict]:
        """
        Get all pins from all user's boards.
        
        Args:
            max_pins: Maximum number of pins to fetch (None for all)
            
        Returns:
            List of pin objects
        """
        all_pins = []
        
        # Get all boards
        boards_data = await self.get_boards(page_size=100)
        boards = boards_data.get("items", [])
        
        logger.info(f"Found {len(boards)} boards")
        
        # Fetch pins from each board
        for board in boards:
            board_id = board.get("id")
            board_name = board.get("name")
            
            logger.info(f"Fetching pins from board: {board_name}")
            
            bookmark = None
            while True:
                pins_data = await self.get_board_pins(
                    board_id=board_id,
                    page_size=100,
                    bookmark=bookmark
                )
                
                pins = pins_data.get("items", [])
                for pin in pins:
                    pin["board_name"] = board_name  # Add board name to pin data
                
                all_pins.extend(pins)
                
                # Check if we've reached max_pins
                if max_pins and len(all_pins) >= max_pins:
                    return all_pins[:max_pins]
                
                # Check for more pages
                bookmark = pins_data.get("bookmark")
                if not bookmark:
                    break
            
            logger.info(f"Total pins fetched so far: {len(all_pins)}")
        
        return all_pins
    
    async def get_pin(self, pin_id: str) -> Dict:
        """Get a specific pin by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/pins/{pin_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
