import os
import json
import logging
import pandas as pd
import faiss
import numpy as np
import random
from typing import List, Dict, Any
from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from config.model_config import MODEL_CONFIG, SEARCH_CONFIG, RESPONSE_TEMPLATES
from utils.database_manager import DatabaseManager
from utils.model_manager import ModelManager
from utils.text_processor import TextProcessor
from utils.menu_searcher import MenuSearcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
try:
    model_manager = ModelManager()
    menu_searcher = MenuSearcher()
    logger.info("Successfully initialized managers")
except Exception as e:
    logger.error(f"Error initializing managers: {e}")
    model_manager = None
    menu_searcher = None

class ActionIngestMenus(Action):
    """Enhanced menu ingestion with comprehensive feedback"""
    
    def name(self) -> str:
        return "action_ingest_menus"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> List[Dict]:
        dispatcher.utter_message(text="Memulai ingest data menu dengan Enhanced Multi-Value + Fixed Seafood Detection...")
        
        try:
            if not model_manager or not menu_searcher:
                dispatcher.utter_message(text="Error: Model manager tidak tersedia.")
                return []
            
            available_menus_df = DatabaseManager.load_available_menus()
            
            if available_menus_df.empty:
                dispatcher.utter_message(text="Tidak ada menu yang tersedia di database.")
                return []
            
            # Create enhanced search text
            available_menus_df['search_text'] = available_menus_df.apply(
                lambda row: TextProcessor.create_search_text(row) or "makanan", axis=1
            )
            
            texts = available_menus_df['search_text'].tolist()
            dispatcher.utter_message(text="Membuat enhanced embeddings untuk multi-value search...")
            
            embeddings = model_manager.embed_texts(texts)
            
            if embeddings.size == 0:
                dispatcher.utter_message(text="Gagal membuat embeddings!")
                return []
            
            # Create and save FAISS index
            try:
                index = faiss.IndexFlatIP(embeddings.shape[1])
                index.add(embeddings)
                
                os.makedirs(MODEL_CONFIG['models_dir'], exist_ok=True)
                faiss.write_index(index, f"{MODEL_CONFIG['models_dir']}/menu_index.faiss")
                available_menus_df.to_pickle(f"{MODEL_CONFIG['models_dir']}/available_menus.pkl")
                
                # Enhanced metadata
                metadata = {
                    'approach': 'ENHANCED_MULTI_VALUE_SEAFOOD_v5.0',
                    'version': '5.0_enhanced_multi_value',
                    'total_menus': len(available_menus_df),
                    'last_updated': datetime.now().isoformat(),
                    'model_info': model_manager.get_model_info(),
                    'multi_value_strict_matching': True,
                    'seafood_detection_enhanced': True,
                    'features': {
                        'enhanced_multi_value_scoring': True,
                        'strict_requirement_matching': True,
                        'comprehensive_seafood_patterns': True,
                        'improved_vegetarian_filtering': True
                    }
                }
                
                with open(f"{MODEL_CONFIG['models_dir']}/metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                logger.error(f"Error saving index: {e}")
                dispatcher.utter_message(text=f"Error menyimpan index: {str(e)}")
                return []
            
            # Generate database statistics
            stats = DatabaseManager.get_database_stats(available_menus_df)
            
            dispatcher.utter_message(
                text=f"✅ Enhanced Multi-Value System berhasil diinisialisasi!\n\n"
                     f"📊 Total Menu: {stats['total_menus']} menu\n"
                     f"🤖 Model: {model_manager.model_name}\n"
                     f"🎯 Max Results: {SEARCH_CONFIG.get('max_results', 8)}\n\n"
                     f"🔍 Fitur Enhanced:\n"
                     f"• Strict multi-value requirement matching\n"
                     f"• Comprehensive seafood detection\n"
                     f"• Enhanced vegetarian filtering\n"
                     f"• Database statistics ready\n\n"
                     f"Ketik 'show stats' untuk melihat statistik lengkap!"
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced ingest: {e}")
            dispatcher.utter_message(text=f"Terjadi kesalahan: {str(e)}")
        
        return []

class ActionRecommendMenu(Action):
    """Enhanced menu recommendation with strict multi-value matching"""
    
    def name(self) -> str:
        return "action_recommend_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> List[Dict]:
        try:
            query = self._extract_enhanced_query(tracker)
            
            if not query:
                response = random.choice(RESPONSE_TEMPLATES.get('greeting', ['Silakan sebutkan menu yang Anda inginkan.']))
                dispatcher.utter_message(text=response)
                return []
            
            if not self._check_knowledge_base():
                dispatcher.utter_message(text="Database belum siap. Silakan tunggu proses ingest selesai.")
                return []
            
            if not menu_searcher:
                dispatcher.utter_message(text="Search engine tidak tersedia.")
                return []
            
            # Load menus
            try:
                available_menus_df = pd.read_pickle(f"{MODEL_CONFIG['models_dir']}/available_menus.pkl")
            except Exception as e:
                logger.error(f"Error loading menus: {e}")
                dispatcher.utter_message(text="Error loading menu database.")
                return []
            
            if available_menus_df.empty:
                dispatcher.utter_message(text="Tidak ada menu yang tersedia di database.")
                return []
            
            # Enhanced feature extraction
            query_expanded = TextProcessor.expand_with_synonyms(query)
            query_features = TextProcessor.extract_features(query_expanded)
            
            logger.info(f"Enhanced search query: '{query}' -> Features: {query_features}")
            
            # Analyze query type
            is_vegetarian = self._is_vegetarian_query(query_features)
            is_seafood = self._is_seafood_query(query_features)
            is_multi_value = self._is_multi_value_query(query_features)
            
            logger.info(f"Query analysis: vegetarian={is_vegetarian}, seafood={is_seafood}, multi_value={is_multi_value}")
            
            # Enhanced search
            menu_recommendations = menu_searcher.search_menus(query, available_menus_df)
            
            if menu_recommendations:
                # Generate enhanced response
                category = TextProcessor.get_category_from_multiple_features(query_features)
                
                if is_vegetarian:
                    response_text = f"Menemukan {len(menu_recommendations)} menu vegetarian {category} terbaik!"
                elif is_seafood:
                    response_text = f"Menemukan {len(menu_recommendations)} menu seafood {category} yang sesuai!"
                elif is_multi_value:
                    response_text = f"Menemukan {len(menu_recommendations)} menu {category} yang memenuhi semua kriteria Anda!"
                else:
                    success_templates = RESPONSE_TEMPLATES.get('success', ['Menemukan {count} menu {category} terbaik!'])
                    response_text = random.choice(success_templates).format(
                        count=len(menu_recommendations),
                        category=category
                    )
                
                dispatcher.utter_message(text=response_text)
                
                # Prepare enhanced menu data
                menu_data = self._prepare_enhanced_menu_data(
                    menu_recommendations, query_features, is_vegetarian, is_seafood, is_multi_value
                )
                return [SlotSet("recommended_menus", menu_data)]
            
            else:
                # Enhanced failure handling
                category = TextProcessor.get_category_from_multiple_features(query_features) if query_features else query
                failure_templates = RESPONSE_TEMPLATES.get('failure', ['Maaf, tidak menemukan menu {query}.'])
                response_text = random.choice(failure_templates).format(query=category)
                
                # Add specific suggestions based on query type
                if is_seafood:
                    response_text += "\n\nUntuk menu seafood, coba kata kunci:\n"
                    response_text += "• 'ikan bakar pedas'\n• 'udang goreng tepung'\n• 'cumi rica-rica'\n• 'kepiting asam manis'"
                elif is_vegetarian:
                    response_text += "\n\nUntuk menu vegetarian, coba:\n"
                    response_text += "• 'tahu goreng crispy'\n• 'tempe bakar pedas'\n• 'cap cay sayuran'\n• 'sayur lodeh'"
                elif is_multi_value:
                    response_text += "\n\nUntuk pencarian multi-kriteria:\n"
                    response_text += "• Coba kurangi jumlah kriteria\n• Gunakan sinonim yang berbeda"
                
                response_text += "\n\nKetik 'menu random' untuk eksplorasi atau 'show stats' untuk melihat kategori tersedia."
                
                dispatcher.utter_message(text=response_text)
                return []
                
        except Exception as e:
            logger.error(f"Error in enhanced menu recommendation: {e}")
            dispatcher.utter_message(text="Terjadi kesalahan saat mencari menu. Silakan coba lagi dengan kata kunci yang berbeda.")
        
        return []
    
    def _extract_enhanced_query(self, tracker: Tracker) -> str:
        """Enhanced query extraction with multi-entity support"""
        try:
            query_parts = []
            entities = ['menu_type', 'flavor', 'cooking_method', 'region', 'dish_type', 'texture', 'protein']
            
            for entity in entities:
                try:
                    values = list(tracker.get_latest_entity_values(entity))
                    if values:
                        query_parts.extend(values)
                except Exception:
                    continue
            
            return ' '.join(query_parts) if query_parts else tracker.latest_message.get('text', '')
            
        except Exception as e:
            logger.error(f"Error in enhanced query extraction: {e}")
            return tracker.latest_message.get('text', '') if tracker.latest_message else ''
    
    def _check_knowledge_base(self) -> bool:
        """Check if knowledge base exists"""
        try:
            required_files = [
                f"{MODEL_CONFIG['models_dir']}/menu_index.faiss",
                f"{MODEL_CONFIG['models_dir']}/available_menus.pkl",
                f"{MODEL_CONFIG['models_dir']}/metadata.json"
            ]
            return all(os.path.exists(file) for file in required_files)
        except Exception:
            return False
    
    def _is_vegetarian_query(self, query_features: Dict) -> bool:
        """Check if query is vegetarian"""
        try:
            proteins = query_features.get('protein', [])
            return 'vegetarian' in proteins
        except Exception:
            return False
    
    def _is_seafood_query(self, query_features: Dict) -> bool:
        """Enhanced seafood query detection"""
        try:
            proteins = query_features.get('protein', [])
            seafood_proteins = ['seafood', 'ikan', 'udang', 'cumi', 'kepiting', 'kerang', 'lobster']
            return any(protein in seafood_proteins for protein in proteins)
        except Exception:
            return False
    
    def _is_multi_value_query(self, query_features: Dict) -> bool:
        """Check if query has multiple values or categories"""
        try:
            if not query_features:
                return False
            
            # Multiple categories
            if len(query_features) > 1:
                return True
            
            # Multiple values in any category
            return any(len(values) > 1 for values in query_features.values())
        except Exception:
            return False
    
    def _prepare_enhanced_menu_data(self, recommendations: List[pd.Series], query_features: Dict, 
                                   is_vegetarian: bool = False, is_seafood: bool = False, 
                                   is_multi_value: bool = False) -> List[Dict]:
        """Prepare enhanced menu data with detailed matching information"""
        menu_data = []
        
        try:
            for i, menu in enumerate(recommendations, 1):
                try:
                    # Calculate match quality
                    menu_text = f"{menu.get('title', '')} {menu.get('ingredients', '')} {menu.get('description', '')}"
                    menu_features = TextProcessor.extract_features(menu_text)
                    
                    # Calculate satisfaction metrics
                    total_required = sum(len(values) for values in query_features.values()) if query_features else 1
                    satisfied = 0
                    
                    if query_features and menu_features:
                        for feature_type, query_values in query_features.items():
                            if query_values:
                                menu_values = set(menu_features.get(feature_type, []))
                                satisfied += len(set(query_values).intersection(menu_values))
                    
                    match_ratio = satisfied / max(total_required, 1)
                    
                    # Enhanced quality labels
                    if is_seafood:
                        if match_ratio >= 0.8:
                            quality_label = f"Perfect Seafood Match (Rank #{i})"
                            accuracy_level = "Perfect Seafood"
                        else:
                            quality_label = f"Good Seafood Match (Rank #{i})"
                            accuracy_level = "Good Seafood"
                    elif is_vegetarian:
                        if match_ratio >= 0.8:
                            quality_label = f"Perfect Vegetarian Match (Rank #{i})"
                            accuracy_level = "Perfect Vegetarian"
                        else:
                            quality_label = f"Good Vegetarian Match (Rank #{i})"
                            accuracy_level = "Good Vegetarian"
                    elif is_multi_value:
                        if match_ratio >= 0.9:
                            quality_label = f"Excellent Multi-Criteria Match (Rank #{i})"
                            accuracy_level = "Excellent Multi-Value"
                        elif match_ratio >= 0.7:
                            quality_label = f"Good Multi-Criteria Match (Rank #{i})"
                            accuracy_level = "Good Multi-Value"
                        else:
                            quality_label = f"Partial Multi-Criteria Match (Rank #{i})"
                            accuracy_level = "Partial Multi-Value"
                    else:
                        quality_label = f"Perfect Match (Rank #{i})" if match_ratio >= 0.8 else f"Good Match (Rank #{i})"
                        accuracy_level = "Perfect" if match_ratio >= 0.8 else "Good"
                    
                    menu_data.append({
                        'id': int(menu.get('id', 0)) if pd.notna(menu.get('id')) else 0,
                        'title': str(menu.get('title', '')),
                        'ingredients': str(menu.get('ingredients', '')),
                        'description': str(menu.get('description', '')),
                        'price': TextProcessor.format_price(menu.get('price', 0)),
                        'numericPrice': int(menu.get('numeric_price', 0)) if pd.notna(menu.get('numeric_price')) else 0,
                        'image': str(menu.get('image', '')),
                        'source': 'Restaurant Menu',
                        'category': TextProcessor.extract_category_from_title(menu.get('title', '')),
                        'available': True,
                        'quality_score': quality_label,
                        'criteria_satisfied': satisfied,
                        'total_criteria': total_required,
                        'match_ratio': match_ratio,
                        'ranking': i,
                        'accuracy_level': accuracy_level,
                        'is_vegetarian': is_vegetarian,
                        'is_seafood': is_seafood,
                        'is_multi_value': is_multi_value
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing menu item {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error preparing enhanced menu data: {e}")
        
        return menu_data

class ActionShowStats(Action):
    """Show comprehensive database statistics"""
    
    def name(self) -> str:
        return "action_show_stats"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> List[Dict]:
        try:
            # Check if database is available
            if not os.path.exists(f"{MODEL_CONFIG['models_dir']}/available_menus.pkl"):
                dispatcher.utter_message(text="Database belum tersedia. Silakan lakukan ingest data terlebih dahulu.")
                return []
            
            # Load menu data
            try:
                available_menus_df = pd.read_pickle(f"{MODEL_CONFIG['models_dir']}/available_menus.pkl")
                metadata_path = f"{MODEL_CONFIG['models_dir']}/metadata.json"
                
                metadata = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                
            except Exception as e:
                logger.error(f"Error loading database stats: {e}")
                dispatcher.utter_message(text="Error mengakses database statistics.")
                return []
            
            if available_menus_df.empty:
                dispatcher.utter_message(text="Database kosong. Tidak ada menu yang tersedia.")
                return []
            
            # Generate comprehensive statistics
            stats = DatabaseManager.get_database_stats(available_menus_df)
            
            # Format statistics response
            stats_text = "DATABASE STATISTICS\n"
            stats_text += "=" * 30 + "\n\n"
            
            # Basic stats
            stats_text += f"Total Menu: {stats['total_menus']} items\n"
            stats_text += f"Status: {stats['availability']['available']} available, {stats['availability']['unavailable']} unavailable\n\n"
            
            # System info
            if metadata:
                stats_text += f"System Version: {metadata.get('version', 'Unknown')}\n"
                stats_text += f"Last Updated: {metadata.get('last_updated', 'Unknown')[:19]}\n"
                if 'model_info' in metadata:
                    model_info = metadata['model_info']
                    stats_text += f"AI Model: {model_info.get('model_name', 'Unknown')}\n"
                stats_text += "\n"
            
            # Category breakdown
            if 'categories' in stats:
                categories = stats['categories']
                
                if 'by_protein' in categories and categories['by_protein']:
                    stats_text += "PROTEIN CATEGORIES:\n"
                    protein_stats = categories['by_protein']
                    for protein, count in sorted(protein_stats.items(), key=lambda x: x[1], reverse=True):
                        if protein == 'vegetarian':
                            stats_text += f"• Vegetarian: {count} menu\n"
                        elif protein == 'ikan':
                            stats_text += f"• Ikan/Fish: {count} menu\n"
                        elif protein == 'seafood':
                            stats_text += f"• Seafood: {count} menu\n"
                        else:
                            stats_text += f"• {protein.title()}: {count} menu\n"
                    stats_text += "\n"
                
                if 'by_dish_type' in categories and categories['by_dish_type']:
                    stats_text += "DISH TYPES:\n"
                    dish_stats = categories['by_dish_type']
                    for dish, count in sorted(dish_stats.items(), key=lambda x: x[1], reverse=True)[:8]:
                        stats_text += f"• {dish.title()}: {count} menu\n"
                    stats_text += "\n"
            
            # Price statistics
            if 'price_stats' in stats and stats['price_stats']:
                price_stats = stats['price_stats']
                stats_text += "PRICE RANGE:\n"
                stats_text += f"• Minimum: Rp {price_stats['min']:,}\n"
                stats_text += f"• Maximum: Rp {price_stats['max']:,}\n"
                stats_text += f"• Average: Rp {price_stats['avg']:,}\n"
                stats_text += f"• Median: Rp {price_stats['median']:,}\n\n"
            
            # Search tips
            stats_text += "SEARCH TIPS:\n"
            stats_text += "• Single: 'ikan bakar', 'ayam goreng'\n"
            stats_text += "• Multi-value: 'ikan bakar pedas', 'ayam rica manado'\n"
            stats_text += "• Vegetarian: 'menu vegetarian', 'tahu crispy'\n"
            stats_text += "• Seafood: 'udang goreng', 'cumi rica'\n"
            stats_text += "• Random: 'menu random' untuk eksplorasi\n"
            
            dispatcher.utter_message(text=stats_text)
            
        except Exception as e:
            logger.error(f"Error showing database stats: {e}")
            dispatcher.utter_message(text="Terjadi kesalahan saat mengakses statistik database.")
        
        return []

class ActionGetRandomMenu(Action):
    """Enhanced random menu with improved variety"""
    
    def name(self) -> str:
        return "action_get_random_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> List[Dict]:
        try:
            if not os.path.exists(f"{MODEL_CONFIG['models_dir']}/available_menus.pkl"):
                dispatcher.utter_message(text="Database belum tersedia.")
                return []
            
            try:
                available_menus_df = pd.read_pickle(f"{MODEL_CONFIG['models_dir']}/available_menus.pkl")
            except Exception as e:
                logger.error(f"Error loading menus for random selection: {e}")
                dispatcher.utter_message(text="Error loading menu database.")
                return []
            
            if available_menus_df.empty:
                dispatcher.utter_message(text="Belum ada menu yang tersedia.")
                return []
            
            # Enhanced variety selection
            sample_size = min(SEARCH_CONFIG.get('max_results', 8), len(available_menus_df))
            random_selection = available_menus_df.sample(n=sample_size)

            dispatcher.utter_message(text="Berikut pilihan menu acak dari berbagai kategori!")
            
            # Prepare random menu data
            menu_data = []
            for i, (_, menu) in enumerate(random_selection.iterrows(), 1):
                try:
                    menu_text = f"{menu.get('title', '')} {menu.get('ingredients', '')} {menu.get('description', '')}".lower()
                    is_vegetarian = any(indicator in menu_text for indicator in ['tahu', 'tempe', 'sayur', 'vegetarian'])
                    is_seafood = any(indicator in menu_text for indicator in ['ikan', 'udang', 'cumi', 'seafood'])
                    
                    if is_vegetarian:
                        quality_label = f"Random Vegetarian #{i}"
                    elif is_seafood:
                        quality_label = f"Random Seafood #{i}"
                    else:
                        quality_label = f"Random Selection #{i}"
                    
                    menu_data.append({
                        'id': int(menu.get('id', 0)) if pd.notna(menu.get('id')) else 0,
                        'title': str(menu.get('title', '')),
                        'ingredients': str(menu.get('ingredients', '')),
                        'description': str(menu.get('description', '')),
                        'price': TextProcessor.format_price(menu.get('price', 0)),
                        'numericPrice': int(menu.get('numeric_price', 0)) if pd.notna(menu.get('numeric_price')) else 0,
                        'image': str(menu.get('image', '')),
                        'source': 'Restaurant Menu',
                        'category': TextProcessor.extract_category_from_title(menu.get('title', '')),
                        'available': True,
                        'quality_score': quality_label,
                        'ranking': i,
                        'accuracy_level': 'Random',
                        'is_vegetarian': is_vegetarian,
                        'is_seafood': is_seafood,
                        'is_multi_value': False
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing random menu item {i}: {e}")
                    continue
            
            return [SlotSet("recommended_menus", menu_data)]
            
        except Exception as e:
            logger.error(f"Error in random menu selection: {e}")
            dispatcher.utter_message(text="Gagal mengambil menu acak.")
            return []