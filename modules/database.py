"""
Database Module
Handles local storage of part information and processing history
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, db_path: str = "ebay_lister.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                part_name TEXT,
                category TEXT,
                condition TEXT,
                vehicles TEXT,
                part_numbers TEXT,
                features TEXT,
                estimated_price REAL,
                ebay_title TEXT,
                ebay_description TEXT,
                compatibility_notes TEXT,
                confidence TEXT,
                seo_keywords TEXT,
                shipping_weight REAL,
                shipping_cost REAL,
                processed_image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # eBay listings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ebay_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER,
                ebay_item_id TEXT,
                listing_status TEXT,
                listing_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES parts (id)
            )
        ''')
        
        # Price history table for market analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT,
                category TEXT,
                price REAL,
                source TEXT,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_part_info(self, filename: str, part_info: Dict) -> int:
        """Store part information and return record ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract shipping info
        shipping_info = part_info.get("shipping_info", {})
        
        cursor.execute('''
            INSERT INTO parts (
                filename, part_name, category, condition, vehicles, part_numbers,
                features, estimated_price, ebay_title, ebay_description,
                compatibility_notes, confidence, seo_keywords, shipping_weight,
                shipping_cost, processed_image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            part_info.get("part_name"),
            part_info.get("category"),
            part_info.get("condition"),
            part_info.get("vehicles"),
            part_info.get("part_numbers"),
            part_info.get("features"),
            part_info.get("estimated_price"),
            part_info.get("seo_title", part_info.get("ebay_title")),
            part_info.get("ebay_description"),
            part_info.get("compatibility_notes"),
            part_info.get("confidence"),
            json.dumps(part_info.get("seo_keywords", [])),
            shipping_info.get("weight", 5),
            shipping_info.get("cost", 15.00),
            part_info.get("processed_image_path")
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def store_part_info_with_images(self, processed_images: list, part_info: Dict) -> str:
        """Store part information with multiple images and return record ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract shipping info
        shipping_info = part_info.get("shipping_info", {})
        
        # Use the first image filename as the primary filename
        primary_filename = processed_images[0]['original'] if processed_images else 'unknown.jpg'
        
        cursor.execute('''
            INSERT INTO parts (
                filename, part_name, category, condition, vehicles, part_numbers,
                features, estimated_price, ebay_title, ebay_description,
                compatibility_notes, confidence, seo_keywords, shipping_weight,
                shipping_cost, processed_image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            primary_filename,
            part_info.get("name", part_info.get("part_name")),
            part_info.get("category"),
            part_info.get("condition"),
            part_info.get("vehicles"),
            part_info.get("part_numbers", part_info.get("part_number")),
            part_info.get("features"),
            part_info.get("estimated_price", part_info.get("price")),
            part_info.get("seo_title", part_info.get("ebay_title")),
            part_info.get("ebay_description", part_info.get("description")),
            part_info.get("compatibility_notes", part_info.get("compatibility")),
            part_info.get("confidence", "High"),
            json.dumps(part_info.get("seo_keywords", [])),
            shipping_info.get("weight", part_info.get("weight", 5)),
            shipping_info.get("cost", 15.00),
            json.dumps([img['processed'] for img in processed_images])  # Store all processed image paths
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return str(record_id)
    
    def get_part_info(self, part_id: int) -> Optional[Dict]:
        """Retrieve part information by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM parts WHERE id = ?', (part_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            part_data = dict(zip(columns, row))
            
            # Parse JSON fields
            if part_data.get('seo_keywords'):
                try:
                    part_data['seo_keywords'] = json.loads(part_data['seo_keywords'])
                except:
                    part_data['seo_keywords'] = []
            
            return part_data
        
        return None
    
    def get_all_parts(self) -> List[Dict]:
        """Get all parts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM parts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        parts = []
        for row in rows:
            part_data = dict(zip(columns, row))
            
            # Parse JSON fields
            if part_data.get('seo_keywords'):
                try:
                    part_data['seo_keywords'] = json.loads(part_data['seo_keywords'])
                except:
                    part_data['seo_keywords'] = []
            
            parts.append(part_data)
        
        return parts
    
    def update_part_price(self, part_id: int, new_price: float):
        """Update part price"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE parts 
            SET estimated_price = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_price, part_id))
        
        conn.commit()
        conn.close()
    
    def store_ebay_listing(self, part_id: int, ebay_item_id: str, listing_data: Dict):
        """Store eBay listing information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ebay_listings (part_id, ebay_item_id, listing_status, listing_data)
            VALUES (?, ?, ?, ?)
        ''', (part_id, ebay_item_id, 'draft', json.dumps(listing_data)))
        
        conn.commit()
        conn.close()
    
    def record_price_data(self, part_name: str, category: str, price: float, source: str):
        """Record price data for market analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_history (part_name, category, price, source)
            VALUES (?, ?, ?, ?)
        ''', (part_name, category, price, source))
        
        conn.commit()
        conn.close()
    
    def get_price_history(self, part_name: str, days: int = 30) -> List[Dict]:
        """Get price history for a part"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM price_history 
            WHERE part_name LIKE ? 
            AND date_recorded >= datetime('now', '-{} days')
            ORDER BY date_recorded DESC
        '''.format(days), (f'%{part_name}%',))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total parts processed
        cursor.execute('SELECT COUNT(*) FROM parts')
        total_parts = cursor.fetchone()[0]
        
        # Average price by category
        cursor.execute('''
            SELECT category, AVG(estimated_price) as avg_price, COUNT(*) as count
            FROM parts 
            WHERE category IS NOT NULL 
            GROUP BY category
        ''')
        category_stats = cursor.fetchall()
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM parts 
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        recent_parts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_parts": total_parts,
            "recent_parts": recent_parts,
            "category_stats": [
                {"category": row[0], "avg_price": row[1], "count": row[2]}
                for row in category_stats
            ]
        }
