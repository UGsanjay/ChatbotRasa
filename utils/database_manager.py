import logging
import pandas as pd
import mysql.connector
from typing import Optional
from config.database_config import MYSQL_CONFIG 
from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database operations with enhanced error handling"""
    
    @staticmethod
    def get_connection() -> Optional[mysql.connector.connection.MySQLConnection]:
        """Create MySQL connection with comprehensive error handling"""
        try:
            connection = mysql.connector.connect(**MYSQL_CONFIG)
            return connection
        except mysql.connector.Error as e:
            logger.error(f"MySQL connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            return None
    
    @staticmethod
    def load_available_menus() -> pd.DataFrame:
        """Load available menus from MySQL database with enhanced processing"""
        connection = None
        try:
            connection = DatabaseManager.get_connection()
            if not connection:
                logger.error("Failed to connect to MySQL database")
                return pd.DataFrame()
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            logger.info("MySQL connection successful")
            
            cursor.execute("SHOW TABLES LIKE 'makanan'")
            if not cursor.fetchone():
                logger.error("Table 'makanan' does not exist")
                return pd.DataFrame()
            
            query = "SELECT id, title, price, image, ingredients, description FROM makanan ORDER BY id ASC"
            df = pd.read_sql(query, connection)
            logger.info(f"Loaded {len(df)} menu items from MySQL database")
            
            if df.empty:
                logger.warning("MySQL table is empty")
                return df
            
            original_count = len(df)
            
            df = df.dropna(subset=['title'])
            df = df[df['title'].astype(str).str.len() > 2]
            
            df['numeric_price'] = df['price'].apply(
                lambda x: TextProcessor.extract_numeric_price(x) if pd.notna(x) else 0
            )
            
            for col in ['ingredients', 'description', 'image']:
                if col not in df.columns:
                    df[col] = ''
                else:
                    df[col] = df[col].fillna('')
            
            df['source'] = 'MySQL'
            df['is_available'] = True
            
            cleaned_count = len(df)
            logger.info(f"Available menus: {original_count} → {cleaned_count} restaurant menu items")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data from MySQL: {e}")
            return pd.DataFrame()
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @staticmethod
    def get_database_stats(df: pd.DataFrame) -> dict:
        """Generate comprehensive database statistics"""
        if df.empty:
            return {"total_menus": 0, "error": "No data available"}
        
        try:
            stats = {
                "total_menus": len(df),
                "categories": {},
                "price_stats": {},
                "availability": {
                    "available": len(df[df.get('is_available', True) == True]),
                    "unavailable": len(df[df.get('is_available', True) == False])
                }
            }
            
            # Category analysis
            category_counts = {}
            protein_counts = {}
            
            for _, menu in df.iterrows():
                try:
                    title = str(menu.get('title', ''))
                    ingredients = str(menu.get('ingredients', ''))
                    description = str(menu.get('description', ''))
                    full_text = f"{title} {ingredients} {description}".lower()
                    
                    features = TextProcessor.extract_features(full_text)
                    
                    # Count proteins
                    if 'protein' in features:
                        for protein in features['protein']:
                            protein_counts[protein] = protein_counts.get(protein, 0) + 1
                    
                    # Count dish types
                    if 'dish_type' in features:
                        for dish in features['dish_type']:
                            category_counts[dish] = category_counts.get(dish, 0) + 1
                    
                except Exception as e:
                    logger.warning(f"Error analyzing menu: {e}")
                    continue
            
            stats["categories"]["by_protein"] = protein_counts
            stats["categories"]["by_dish_type"] = category_counts
            
            # Price statistics
            if 'numeric_price' in df.columns:
                price_data = df['numeric_price'][df['numeric_price'] > 0]
                if not price_data.empty:
                    stats["price_stats"] = {
                        "min": int(price_data.min()),
                        "max": int(price_data.max()),
                        "avg": int(price_data.mean()),
                        "median": int(price_data.median())
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating database stats: {e}")
            return {"total_menus": len(df), "error": str(e)}