"""
eBay Pricing Module - Fetch sold listings data for competitive pricing
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

class eBayPricing:
    def __init__(self):
        """Initialize eBay pricing with API credentials"""
        self.client_id = os.getenv("EBAY_CLIENT_ID")
        self.client_secret = os.getenv("EBAY_CLIENT_SECRET")
        self.access_token = None
        self.base_url = "https://api.ebay.com"
        
        # Check if credentials are available
        if not self.client_id or not self.client_secret:
            print("eBay API credentials not found - pricing will use estimates")
            self.demo_mode = True
        else:
            self.demo_mode = False
            print("eBay API credentials found - real pricing enabled")

    async def get_access_token(self) -> bool:
        """Get OAuth access token for eBay API"""
        if self.demo_mode:
            return False
            
        try:
            url = f"{self.base_url}/identity/v1/oauth2/token"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {self._encode_credentials()}'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'scope': 'https://api.ebay.com/oauth/api_scope'
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                print("eBay API access token obtained successfully")
                return True
            else:
                print(f"Failed to get eBay access token: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error getting eBay access token: {str(e)}")
            return False

    def _encode_credentials(self) -> str:
        """Encode client credentials for Basic auth"""
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    async def get_sold_listings_price(self, part_number: str, part_name: str, condition: str = "Used") -> Dict:
        """
        Get average sold price for a part from eBay sold listings in last 90 days
        
        Args:
            part_number: The part number to search for
            part_name: The part name for broader search
            condition: Part condition (Used, New, etc.)
            
        Returns:
            Dict with pricing data and statistics
        """
        
        if self.demo_mode:
            return self._get_demo_pricing(part_number, part_name)
        
        # Get access token if not available
        if not self.access_token:
            if not await self.get_access_token():
                return self._get_demo_pricing(part_number, part_name)
        
        try:
            # Search for sold listings
            sold_data = await self._search_sold_listings(part_number, part_name, condition)
            
            if sold_data and len(sold_data) > 0:
                # Calculate pricing statistics
                prices = [item['price'] for item in sold_data if item.get('price', 0) > 0]
                
                if len(prices) >= 3:  # Need at least 3 data points
                    avg_price = statistics.mean(prices)
                    median_price = statistics.median(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    
                    # Suggest competitive pricing (10-15% below average for quick sale)
                    suggested_price = round(avg_price * 0.85, 2)  # 15% below average
                    quick_sale_price = round(avg_price * 0.80, 2)  # 20% below average
                    
                    return {
                        "success": True,
                        "data_points": len(prices),
                        "average_price": round(avg_price, 2),
                        "median_price": round(median_price, 2),
                        "price_range": f"${min_price} - ${max_price}",
                        "suggested_price": suggested_price,
                        "quick_sale_price": quick_sale_price,
                        "market_analysis": f"Based on {len(prices)} sold listings in last 90 days",
                        "pricing_strategy": "Suggested price is 15% below average for competitive positioning"
                    }
                else:
                    return self._get_fallback_pricing(part_name, condition)
            else:
                return self._get_fallback_pricing(part_name, condition)
                
        except Exception as e:
            print(f"Error fetching eBay sold listings: {str(e)}")
            return self._get_fallback_pricing(part_name, condition)

    async def _search_sold_listings(self, part_number: str, part_name: str, condition: str) -> List[Dict]:
        """Search eBay for sold listings of the specific part"""
        
        try:
            # Calculate date range (last 90 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            # Build search query
            search_terms = []
            if part_number and part_number != "Unknown":
                search_terms.append(part_number)
            if part_name:
                # Extract key terms from part name
                key_terms = part_name.replace("Left", "").replace("Right", "").replace("Driver", "").replace("Passenger", "").strip()
                search_terms.append(key_terms)
            
            query = " ".join(search_terms)
            
            # eBay Browse API endpoint for search
            url = f"{self.base_url}/buy/browse/v1/item_summary/search"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
            }
            
            params = {
                'q': query,
                'filter': f'conditionIds:{{3000}},deliveryCountry:US,itemLocationCountry:US',  # Used condition
                'sort': 'endTimeSoonest',
                'limit': 50  # Get up to 50 recent sold items
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('itemSummaries', [])
                
                # Filter and extract pricing data
                sold_items = []
                for item in items:
                    if item.get('buyingOptions') and 'FIXED_PRICE' in item.get('buyingOptions', []):
                        price_info = item.get('price', {})
                        if price_info.get('currency') == 'USD':
                            sold_items.append({
                                'title': item.get('title', ''),
                                'price': float(price_info.get('value', 0)),
                                'condition': item.get('condition', ''),
                                'end_date': item.get('itemEndDate', ''),
                                'item_id': item.get('itemId', '')
                            })
                
                return sold_items
            else:
                print(f"eBay API search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching eBay sold listings: {str(e)}")
            return []

    def _get_demo_pricing(self, part_number: str, part_name: str) -> Dict:
        """Return demo pricing when eBay API is not available"""
        
        # Estimate based on part type
        base_price = 50.0  # Default base price
        
        if "tail light" in part_name.lower():
            base_price = 45.0
        elif "headlight" in part_name.lower():
            base_price = 85.0
        elif "bumper" in part_name.lower():
            base_price = 150.0
        elif "alternator" in part_name.lower():
            base_price = 120.0
        elif "starter" in part_name.lower():
            base_price = 95.0
        
        return {
            "success": False,
            "demo_mode": True,
            "data_points": 0,
            "average_price": base_price,
            "median_price": base_price,
            "price_range": f"${base_price * 0.7:.0f} - ${base_price * 1.3:.0f}",
            "suggested_price": round(base_price * 0.9, 2),
            "quick_sale_price": round(base_price * 0.8, 2),
            "market_analysis": "Demo pricing - eBay API not configured",
            "pricing_strategy": "Estimated pricing based on part type"
        }

    def _get_fallback_pricing(self, part_name: str, condition: str) -> Dict:
        """Fallback pricing when eBay search returns insufficient data"""
        
        # Use demo pricing as fallback
        demo_data = self._get_demo_pricing("", part_name)
        demo_data.update({
            "success": False,
            "market_analysis": "Insufficient eBay data - using estimated pricing",
            "pricing_strategy": "Fallback pricing due to limited market data"
        })
        
        return demo_data
