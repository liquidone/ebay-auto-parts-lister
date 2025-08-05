"""
eBay API Integration Module
Handles authentication, image upload, and draft listing creation for auto parts
"""

import requests
import base64
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

class eBayAPI:
    def __init__(self):
        """Initialize eBay API client with credentials from environment"""
        
        # eBay API Credentials (from .env file)
        self.app_id = os.getenv('EBAY_APP_ID')
        self.dev_id = os.getenv('EBAY_DEV_ID') 
        self.cert_id = os.getenv('EBAY_CERT_ID')
        self.user_token = os.getenv('EBAY_USER_TOKEN')
        self.sandbox = os.getenv('EBAY_SANDBOX', 'true').lower() == 'true'
        
        # eBay API Endpoints
        if self.sandbox:
            self.trading_api_url = "https://api.sandbox.ebay.com/ws/api.dll"
            self.finding_api_url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"
            self.shopping_api_url = "https://open.api.sandbox.ebay.com/shopping"
        else:
            self.trading_api_url = "https://api.ebay.com/ws/api.dll"
            self.finding_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
            self.shopping_api_url = "https://open.api.ebay.com/shopping"
        
        # API Version and Site ID
        self.api_version = "1193"
        self.site_id = "0"  # US eBay site
        
        # Demo mode flag
        self.demo_mode = not all([self.app_id, self.dev_id, self.cert_id, self.user_token])
        
        if self.demo_mode:
            print("eBay API running in DEMO MODE - no API keys configured")
        else:
            print(f"eBay API initialized - Sandbox: {self.sandbox}")
    
    def test_connection(self) -> Dict:
        """Test eBay API connection and authentication"""
        if self.demo_mode:
            return {
                "success": True,
                "demo_mode": True,
                "message": "Demo mode - eBay API connection simulated",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Test with GeteBayOfficialTime call
            xml_request = f"""<?xml version="1.0" encoding="utf-8"?>
            <GeteBayOfficialTimeRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                <RequesterCredentials>
                    <eBayAuthToken>{self.user_token}</eBayAuthToken>
                </RequesterCredentials>
            </GeteBayOfficialTimeRequest>"""
            
            headers = {
                'X-EBAY-API-COMPATIBILITY-LEVEL': self.api_version,
                'X-EBAY-API-DEV-NAME': self.dev_id,
                'X-EBAY-API-APP-NAME': self.app_id,
                'X-EBAY-API-CERT-NAME': self.cert_id,
                'X-EBAY-API-CALL-NAME': 'GeteBayOfficialTime',
                'X-EBAY-API-SITEID': self.site_id,
                'Content-Type': 'text/xml'
            }
            
            response = requests.post(self.trading_api_url, data=xml_request, headers=headers)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ack = root.find('.//{urn:ebay:apis:eBLBaseComponents}Ack').text
                
                if ack == 'Success':
                    official_time = root.find('.//{urn:ebay:apis:eBLBaseComponents}Timestamp').text
                    return {
                        "success": True,
                        "demo_mode": False,
                        "message": "eBay API connection successful",
                        "ebay_time": official_time,
                        "sandbox": self.sandbox
                    }
                else:
                    errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}ShortMessage')
                    error_messages = [error.text for error in errors]
                    return {
                        "success": False,
                        "message": f"eBay API error: {', '.join(error_messages)}"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
    
    def upload_images_to_ebay(self, image_paths: List[str]) -> Dict:
        """Upload images to eBay Picture Services (EPS)"""
        if self.demo_mode:
            return {
                "success": True,
                "demo_mode": True,
                "image_urls": [f"https://i.ebayimg.com/demo/auto-part-{i+1}.jpg" for i in range(len(image_paths))],
                "message": f"Demo mode - {len(image_paths)} images simulated upload"
            }
        
        try:
            uploaded_urls = []
            
            for i, image_path in enumerate(image_paths):
                # Read image file
                with open(image_path, 'rb') as img_file:
                    image_data = img_file.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # Upload to eBay Picture Services
                xml_request = f"""<?xml version="1.0" encoding="utf-8"?>
                <UploadSiteHostedPicturesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                    <RequesterCredentials>
                        <eBayAuthToken>{self.user_token}</eBayAuthToken>
                    </RequesterCredentials>
                    <PictureData>
                        <Data>{image_base64}</Data>
                        <DataFormat>JPG</DataFormat>
                        <PictureName>{os.path.basename(image_path)}</PictureName>
                    </PictureData>
                </UploadSiteHostedPicturesRequest>"""
                
                headers = {
                    'X-EBAY-API-COMPATIBILITY-LEVEL': self.api_version,
                    'X-EBAY-API-DEV-NAME': self.dev_id,
                    'X-EBAY-API-APP-NAME': self.app_id,
                    'X-EBAY-API-CERT-NAME': self.cert_id,
                    'X-EBAY-API-CALL-NAME': 'UploadSiteHostedPictures',
                    'X-EBAY-API-SITEID': self.site_id,
                    'Content-Type': 'text/xml'
                }
                
                response = requests.post(self.trading_api_url, data=xml_request, headers=headers)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    ack = root.find('.//{urn:ebay:apis:eBLBaseComponents}Ack').text
                    
                    if ack == 'Success':
                        full_url = root.find('.//{urn:ebay:apis:eBLBaseComponents}FullURL').text
                        uploaded_urls.append(full_url)
                        print(f"Uploaded image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
                    else:
                        errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}ShortMessage')
                        error_messages = [error.text for error in errors]
                        return {
                            "success": False,
                            "message": f"Image upload failed: {', '.join(error_messages)}"
                        }
                else:
                    return {
                        "success": False,
                        "message": f"HTTP error during image upload: {response.status_code}"
                    }
            
            return {
                "success": True,
                "demo_mode": False,
                "image_urls": uploaded_urls,
                "message": f"Successfully uploaded {len(uploaded_urls)} images to eBay"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Image upload error: {str(e)}"
            }
    
    def get_auto_parts_category_id(self, part_name: str) -> str:
        """Get appropriate eBay category ID for auto parts"""
        # Common auto parts category mappings
        category_mappings = {
            'brake': '33567',      # Brake System
            'engine': '33615',     # Engine & Components
            'transmission': '33738', # Transmission & Drivetrain
            'suspension': '33567',  # Suspension & Steering
            'electrical': '33567',  # Electrical Components
            'body': '33567',       # Body Parts
            'interior': '33567',   # Interior Parts
            'exhaust': '33567',    # Exhaust System
            'fuel': '33567',       # Fuel System
            'cooling': '33567',    # Cooling System
            'headlight': '33567',  # Lighting
            'tail light': '33567', # Lighting
            'alternator': '33567', # Electrical
            'starter': '33567',    # Electrical
        }
        
        part_name_lower = part_name.lower()
        for keyword, category_id in category_mappings.items():
            if keyword in part_name_lower:
                return category_id
        
        # Default to general auto parts category
        return '33567'  # Auto Parts & Accessories > Car & Truck Parts
    
    def create_draft_listing(self, part_info: Dict, image_urls: List[str]) -> Dict:
        """Create a draft eBay listing for an auto part"""
        if self.demo_mode:
            return {
                "success": True,
                "demo_mode": True,
                "item_id": "DEMO123456789",
                "listing_url": "https://www.ebay.com/itm/demo-auto-part-listing",
                "message": "Demo mode - draft listing creation simulated"
            }
        
        try:
            # Get category ID
            category_id = self.get_auto_parts_category_id(part_info.get('name', ''))
            
            # Prepare listing data
            title = part_info.get('name', 'Auto Part')[:80]  # eBay title limit
            description = self._build_html_description(part_info)
            
            # Build XML request for AddItem
            xml_request = f"""<?xml version="1.0" encoding="utf-8"?>
            <AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                <RequesterCredentials>
                    <eBayAuthToken>{self.user_token}</eBayAuthToken>
                </RequesterCredentials>
                <Item>
                    <Title>{title}</Title>
                    <Description><![CDATA[{description}]]></Description>
                    <PrimaryCategory>
                        <CategoryID>{category_id}</CategoryID>
                    </PrimaryCategory>
                    <StartPrice>{part_info.get('price', 25.00)}</StartPrice>
                    <CategoryMappingAllowed>true</CategoryMappingAllowed>
                    <Country>US</Country>
                    <Currency>USD</Currency>
                    <DispatchTimeMax>3</DispatchTimeMax>
                    <ListingDuration>Days_7</ListingDuration>
                    <ListingType>FixedPriceItem</ListingType>
                    <PaymentMethods>PayPal</PaymentMethods>
                    <PayPalEmailAddress>your-paypal@email.com</PayPalEmailAddress>
                    <PictureDetails>
                        {''.join([f'<PictureURL>{url}</PictureURL>' for url in image_urls[:12]])}
                    </PictureDetails>
                    <PostalCode>12345</PostalCode>
                    <Quantity>1</Quantity>
                    <ReturnPolicy>
                        <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
                        <RefundOption>MoneyBack</RefundOption>
                        <ReturnsWithinOption>Days_30</ReturnsWithinOption>
                        <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
                    </ReturnPolicy>
                    <ShippingDetails>
                        <ShippingType>Flat</ShippingType>
                        <ShippingServiceOptions>
                            <ShippingServicePriority>1</ShippingServicePriority>
                            <ShippingService>USPSPriority</ShippingService>
                            <ShippingServiceCost>15.00</ShippingServiceCost>
                        </ShippingServiceOptions>
                    </ShippingDetails>
                    <Site>US</Site>
                    <ItemSpecifics>
                        <NameValueList>
                            <Name>Brand</Name>
                            <Value>{part_info.get('make', 'Generic')}</Value>
                        </NameValueList>
                        <NameValueList>
                            <Name>Part Number</Name>
                            <Value>{part_info.get('part_number', 'Unknown')}</Value>
                        </NameValueList>
                        <NameValueList>
                            <Name>Condition</Name>
                            <Value>Used</Value>
                        </NameValueList>
                    </ItemSpecifics>
                </Item>
            </AddItemRequest>"""
            
            headers = {
                'X-EBAY-API-COMPATIBILITY-LEVEL': self.api_version,
                'X-EBAY-API-DEV-NAME': self.dev_id,
                'X-EBAY-API-APP-NAME': self.app_id,
                'X-EBAY-API-CERT-NAME': self.cert_id,
                'X-EBAY-API-CALL-NAME': 'AddItem',
                'X-EBAY-API-SITEID': self.site_id,
                'Content-Type': 'text/xml'
            }
            
            response = requests.post(self.trading_api_url, data=xml_request, headers=headers)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ack = root.find('.//{urn:ebay:apis:eBLBaseComponents}Ack').text
                
                if ack == 'Success':
                    item_id = root.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID').text
                    listing_url = f"https://www.ebay.com/itm/{item_id}"
                    
                    return {
                        "success": True,
                        "demo_mode": False,
                        "item_id": item_id,
                        "listing_url": listing_url,
                        "message": "Draft listing created successfully"
                    }
                else:
                    errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}ShortMessage')
                    error_messages = [error.text for error in errors]
                    return {
                        "success": False,
                        "message": f"Listing creation failed: {', '.join(error_messages)}"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP error during listing creation: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Listing creation error: {str(e)}"
            }
    
    def _build_html_description(self, part_info: Dict) -> str:
        """Build HTML description for eBay listing"""
        description = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px;">
            <h2 style="color: #0066cc;">{part_info.get('name', 'Auto Part')}</h2>
            
            <div style="background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3>Part Details:</h3>
                <ul>
                    <li><strong>Part Number:</strong> {part_info.get('part_number', 'See title')}</li>
                    <li><strong>Condition:</strong> {part_info.get('condition', 'Used')}</li>
                    <li><strong>Compatible Vehicles:</strong> {part_info.get('vehicles', 'See title for fitment')}</li>
                    <li><strong>Weight:</strong> {part_info.get('weight', 'TBD')}</li>
                    <li><strong>Dimensions:</strong> {part_info.get('dimensions', 'TBD')}</li>
                </ul>
            </div>
            
            <div style="margin: 15px 0;">
                <h3>Description:</h3>
                <p>{part_info.get('description', 'Quality used auto part in good working condition.')}</p>
            </div>
            
            <div style="background: #e8f4f8; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3>Shipping & Returns:</h3>
                <ul>
                    <li>Fast shipping within 1-3 business days</li>
                    <li>Secure packaging to prevent damage</li>
                    <li>30-day return policy</li>
                    <li>Professional auto parts seller</li>
                </ul>
            </div>
            
            <p style="text-align: center; color: #666; font-size: 12px;">
                Listed with AutoParts Pro - Professional eBay Auto Parts Lister
            </p>
        </div>
        """
        return description.strip()
