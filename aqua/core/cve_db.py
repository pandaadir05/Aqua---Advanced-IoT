"""
CVE Database Integration Module for NexGuard.
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import sqlite3
import gzip
import shutil
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console

console = Console()

class CVEDatabase:
    """Class for managing CVE database and vulnerability information."""
    
    def __init__(self, db_path: str = "cve.db"):
        self.db_path = db_path
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database for CVE storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cves (
                cve_id TEXT PRIMARY KEY,
                description TEXT,
                severity TEXT,
                cvss_score REAL,
                published_date TEXT,
                last_modified_date TEXT,
                affected_products TEXT,
                references TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT,
                product TEXT,
                version TEXT,
                cve_id TEXT,
                FOREIGN KEY (cve_id) REFERENCES cves(cve_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def update_database(self):
        """Update CVE database from NVD."""
        try:
            # Download latest CVE data
            url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                # Save gzipped file
                gz_path = self.cache_dir / "recent_cves.json.gz"
                with open(gz_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract and parse JSON
                with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
                    cve_data = json.load(f)
                
                # Process and store CVEs
                self._process_cves(cve_data)
                logger.info("CVE database updated successfully")
            else:
                logger.error(f"Failed to download CVE data: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error updating CVE database: {e}")
            
    def _process_cves(self, cve_data: Dict):
        """Process and store CVE data in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for cve_item in cve_data.get('CVE_Items', []):
            cve_id = cve_item['cve']['CVE_data_meta']['ID']
            description = cve_item['cve']['description']['description_data'][0]['value']
            
            # Get CVSS score if available
            cvss_score = None
            severity = "UNKNOWN"
            if 'baseMetricV3' in cve_item['impact']:
                cvss_score = cve_item['impact']['baseMetricV3']['cvssV3']['baseScore']
                severity = cve_item['impact']['baseMetricV3']['cvssV3']['baseSeverity']
            
            # Get affected products
            affected_products = []
            for node in cve_item['configurations']['nodes']:
                for cpe in node.get('cpe_match', []):
                    if cpe['vulnerable']:
                        affected_products.append(cpe['cpe23Uri'])
            
            # Get references
            references = []
            for ref in cve_item['cve']['references']['reference_data']:
                references.append(ref['url'])
            
            # Insert CVE data
            cursor.execute('''
                INSERT OR REPLACE INTO cves 
                (cve_id, description, severity, cvss_score, published_date, 
                 last_modified_date, affected_products, references)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cve_id,
                description,
                severity,
                cvss_score,
                cve_item['publishedDate'],
                cve_item['lastModifiedDate'],
                json.dumps(affected_products),
                json.dumps(references)
            ))
            
            # Insert product data
            for product in affected_products:
                parts = product.split(':')
                if len(parts) >= 5:
                    vendor = parts[3]
                    product_name = parts[4]
                    version = parts[5] if len(parts) > 5 else ''
                    
                    cursor.execute('''
                        INSERT INTO products (vendor, product, version, cve_id)
                        VALUES (?, ?, ?, ?)
                    ''', (vendor, product_name, version, cve_id))
        
        conn.commit()
        conn.close()
        
    def search_cves(self, 
                   product: Optional[str] = None,
                   vendor: Optional[str] = None,
                   severity: Optional[str] = None,
                   min_cvss: Optional[float] = None) -> List[Dict]:
        """Search for CVEs based on criteria."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM cves WHERE 1=1"
        params = []
        
        if product:
            query += " AND cve_id IN (SELECT cve_id FROM products WHERE product LIKE ?)"
            params.append(f"%{product}%")
            
        if vendor:
            query += " AND cve_id IN (SELECT cve_id FROM products WHERE vendor LIKE ?)"
            params.append(f"%{vendor}%")
            
        if severity:
            query += " AND severity = ?"
            params.append(severity)
            
        if min_cvss is not None:
            query += " AND cvss_score >= ?"
            params.append(min_cvss)
            
        cursor.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'cve_id': row[0],
                'description': row[1],
                'severity': row[2],
                'cvss_score': row[3],
                'published_date': row[4],
                'last_modified_date': row[5],
                'affected_products': json.loads(row[6]),
                'references': json.loads(row[7])
            })
            
        conn.close()
        return results
        
    def get_cve_details(self, cve_id: str) -> Optional[Dict]:
        """Get detailed information about a specific CVE."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cves WHERE cve_id = ?
        ''', (cve_id,))
        
        row = cursor.fetchone()
        if row:
            result = {
                'cve_id': row[0],
                'description': row[1],
                'severity': row[2],
                'cvss_score': row[3],
                'published_date': row[4],
                'last_modified_date': row[5],
                'affected_products': json.loads(row[6]),
                'references': json.loads(row[7])
            }
            
            # Get affected products
            cursor.execute('''
                SELECT vendor, product, version 
                FROM products 
                WHERE cve_id = ?
            ''', (cve_id,))
            
            result['products'] = [
                {'vendor': row[0], 'product': row[1], 'version': row[2]}
                for row in cursor.fetchall()
            ]
            
            conn.close()
            return result
            
        conn.close()
        return None 