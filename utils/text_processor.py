import re
import pandas as pd
import logging
from typing import Dict, List
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config.food_keywords import FOOD_KEYWORDS, FOOD_SYNONYMS

logger = logging.getLogger(__name__)

class TextProcessor:
    """Enhanced text processing with fixed flavor and regional detection"""
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """Clean and preprocess Indonesian text with error handling"""
        try:
            if pd.isna(text) or not text:
                return ""
            
            text = str(text).lower().strip()
            text = re.sub(r'[^\w\s-]', ' ', text)
            text = re.sub(r'[\s-]+', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            logger.warning(f"Error preprocessing text: {e}")
            return ""
    
    @staticmethod
    def expand_with_synonyms(text: str) -> str:
        """Enhanced synonym expansion with better context awareness"""
        try:
            if not text:
                return ""
                
            words = text.lower().split()
            expanded_words = []
            
            for word in words:
                expanded_words.append(word)
                if word in FOOD_SYNONYMS:
                    expanded_words.extend(FOOD_SYNONYMS[word])
                
                if word == 'manis':
                    expanded_words.extend(['sweet', 'gula'])
                elif word == 'pedas':
                    expanded_words.extend(['spicy', 'hot', 'cabai', 'sambal'])
                elif word == 'padang':
                    expanded_words.extend(['minang', 'sumatera barat', 'rendang'])
                elif word == 'manado':
                    expanded_words.extend(['sulawesi utara', 'rica', 'woku'])
            
            return ' '.join(expanded_words)
        except Exception as e:
            logger.warning(f"Error expanding synonyms: {e}")
            return text or ""
    
    @staticmethod
    def extract_features(text: str) -> Dict[str, List[str]]:
        """Enhanced feature extraction with improved detection"""
        try:
            if not text:
                return {}
            
            text_lower = TextProcessor.preprocess_text(text)
            if not text_lower:
                return {}
                
            features = {}
            
            for category, subcategories in FOOD_KEYWORDS.items():
                found_features = []
                
                for subcategory, keywords in subcategories.items():
                    try:
                        sorted_keywords = sorted(keywords, key=len, reverse=True)
                        
                        for keyword in sorted_keywords:
                            if TextProcessor._is_keyword_match(keyword, text_lower):
                                found_features.append(subcategory)
                                break
                                
                    except Exception as e:
                        logger.warning(f"Error processing subcategory {subcategory}: {e}")
                        continue
                
                if found_features:
                    features[category] = list(set(found_features))
            
            features = TextProcessor._apply_enhanced_detection_logic(text_lower, features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    @staticmethod
    def _is_keyword_match(keyword: str, text: str) -> bool:
        """Enhanced keyword matching with context awareness"""
        try:
            keyword_lower = keyword.lower()
            
            if ' ' in keyword_lower:
                if keyword_lower in text:
                    return True
                keyword_words = keyword_lower.split()
                return all(word in text for word in keyword_words if len(word) > 2)
            
            if len(keyword_lower) > 3:
                return keyword_lower in text
            else:
                return bool(re.search(rf'\b{re.escape(keyword_lower)}\b', text))
                
        except Exception as e:
            logger.warning(f"Error in keyword matching: {e}")
            return False
    
    @staticmethod
    def _apply_enhanced_detection_logic(text_lower: str, features: Dict) -> Dict:
        """Enhanced detection logic with fixed protein, flavor, and regional detection"""
        try:
            features = TextProcessor._enhance_protein_detection(text_lower, features)
            
            features = TextProcessor._enhance_flavor_detection(text_lower, features)
            
            features = TextProcessor._enhance_regional_detection(text_lower, features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error applying enhanced detection logic: {e}")
            return features
    
    @staticmethod
    def _enhance_protein_detection(text_lower: str, features: Dict) -> Dict:
        """Enhanced protein detection with comprehensive seafood patterns"""
        try:
            if 'protein' not in features:
                features['protein'] = []
            
            seafood_patterns = [
                r'\bikan\s+\w+', r'\bikan\b', r'\bfish\b',
                r'\budang\s+\w+', r'\budang\b', r'\bshrimp\b', r'\bprawn\b',
                r'\bcumi\s+\w+', r'\bcumi\b', r'\bsquid\b', r'\bsotong\b',
                r'\bkepiting\b', r'\bcrab\b', r'\brajungan\b',
                r'\bkerang\b', r'\bmussel\b', r'\bclam\b',
                r'\blobster\b', r'\bseafood\b', r'\bmakanan\s+laut\b',
                r'\bsalmon\b', r'\btuna\b', r'\bkakap\b', r'\bgurame\b',
                r'\blele\b', r'\bnila\b', r'\bbandeng\b', r'\btenggiri\b'
            ]
            
            land_animal_patterns = [
                r'\bayam\b', r'\bchicken\b', r'\bsapi\b', r'\bbeef\b',
                r'\bkambing\b', r'\bgoat\b', r'\bbebek\b', r'\bduck\b',
                r'\btelur\b', r'\begg\b', r'\bdaging\b'
            ]
            
            vegetarian_patterns = [
                r'\bvegetarian\b', r'\bvegan\b', r'\bnabati\b',
                r'\btahu\b', r'\btofu\b', r'\btempe\b', r'\btempeh\b',
                r'\bjamur\b', r'\bmushroom\b'
            ]
            
            has_seafood = any(re.search(pattern, text_lower, re.IGNORECASE) 
                            for pattern in seafood_patterns)
            has_land_animal = any(re.search(pattern, text_lower, re.IGNORECASE) 
                                for pattern in land_animal_patterns)
            has_vegetarian = any(re.search(pattern, text_lower, re.IGNORECASE) 
                               for pattern in vegetarian_patterns)
            
            detected_proteins = []
            
            if has_vegetarian and not has_land_animal and not has_seafood:
                detected_proteins.append('vegetarian')
                
            elif has_seafood:
                if re.search(r'\bikan\b', text_lower):
                    detected_proteins.append('ikan')
                if re.search(r'\budang\b', text_lower):
                    detected_proteins.append('udang')
                if re.search(r'\bcumi\b', text_lower):
                    detected_proteins.append('cumi')
                if re.search(r'\bkepiting\b', text_lower):
                    detected_proteins.append('kepiting')
                if re.search(r'\bkerang\b', text_lower):
                    detected_proteins.append('kerang')
                if re.search(r'\blobster\b', text_lower):
                    detected_proteins.append('lobster')
                    
                if not detected_proteins and has_seafood:
                    detected_proteins.append('seafood')
                    
            elif has_land_animal:
                if re.search(r'\bsapi\b|beef\b|daging\b', text_lower):
                    detected_proteins.append('sapi')
                if re.search(r'\bayam\b|chicken\b', text_lower):
                    detected_proteins.append('ayam')
                if re.search(r'\bkambing\b|goat\b', text_lower):
                    detected_proteins.append('kambing')
                if re.search(r'\bbebek\b|duck\b', text_lower):
                    detected_proteins.append('bebek')
                if re.search(r'\btelur\b|egg\b', text_lower):
                    detected_proteins.append('telur')
            
            if detected_proteins:
                all_proteins = list(set(features['protein'] + detected_proteins))
                features['protein'] = all_proteins
            
            return features
            
        except Exception as e:
            logger.error(f"Error enhancing protein detection: {e}")
            return features
    
    @staticmethod
    def _enhance_flavor_detection(text_lower: str, features: Dict) -> Dict:
        """FIXED flavor detection with comprehensive patterns"""
        try:
            if 'flavor' not in features:
                features['flavor'] = []
            
            flavor_patterns = {
                'pedas': [r'\bpedas\b', r'\bspicy\b', r'\bhot\b', r'\bcabai\b', r'\bchili\b', 
                         r'\bsambal\b', r'\bcabe\b', r'\brica\b', r'\bbalado\b', r'\blevel\b'],
                'manis': [r'\bmanis\b', r'\bsweet\b', r'\bgula\b', r'\bkecap\s+manis\b', 
                         r'\bgula\s+jawa\b', r'\bpalm\s+sugar\b', r'\bmanis\s+gurih\b'],
                'gurih': [r'\bgurih\b', r'\bsavory\b', r'\basin\b', r'\bsalty\b', r'\bumami\b', r'\bsedap\b'],
                'asam': [r'\basin\b', r'\bsour\b', r'\btamarind\b', r'\bbelimbing\b', r'\bjeruk\b', 
                        r'\blime\b', r'\basem\b', r'\bkecut\b'],
                'berkuah': [r'\bkuah\b', r'\bberkuah\b', r'\bsoup\b', r'\bbroth\b', r'\bsoto\b', 
                           r'\bsup\b', r'\bkaldu\b', r'\bsauce\b'],
                'kering': [r'\bkering\b', r'\bdry\b', r'\btanpa\s+kuah\b', r'\btidak\s+berkuah\b'],
                'segar': [r'\bsegar\b', r'\bfresh\b', r'\bsejuk\b', r'\bdingin\b'],
                'sehat': [r'\bsehat\b', r'\bhealthy\b', r'\bdiet\b', r'\blow\s+fat\b']
            }
            
            detected_flavors = []
            
            for flavor_name, patterns in flavor_patterns.items():
                if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns):
                    detected_flavors.append(flavor_name)
            
            if detected_flavors:
                all_flavors = list(set(features['flavor'] + detected_flavors))
                features['flavor'] = all_flavors
            
            return features
            
        except Exception as e:
            logger.error(f"Error enhancing flavor detection: {e}")
            return features
    
    @staticmethod
    def _enhance_regional_detection(text_lower: str, features: Dict) -> Dict:
        """FIXED regional detection with comprehensive patterns"""
        try:
            if 'region' not in features:
                features['region'] = []
            
            regional_patterns = {
                'padang': [r'\bpadang\b', r'\bminang\b', r'\bsumatera\s+barat\b', r'\brendang\b', 
                          r'\bgulai\b', r'\bminangkabau\b', r'\bmasakan\s+padang\b'],
                'manado': [r'\bmanado\b', r'\bsulawesi\s+utara\b', r'\bwoku\b', r'\brica\b', 
                          r'\bminahasa\b', r'\bmasakan\s+manado\b'],
                'jawa': [r'\bjawa\b', r'\bjavanese\b', r'\bjogja\b', r'\bsolo\b', r'\bsemarang\b', 
                        r'\bgudeg\b', r'\brawon\b', r'\byogyakarta\b', r'\bmasakan\s+jawa\b'],
                'sunda': [r'\bsunda\b', r'\bbandung\b', r'\bpriangan\b', r'\bkaredok\b', 
                         r'\bpepes\b', r'\bsundanese\b', r'\bmasakan\s+sunda\b'],
                'bali': [r'\bbali\b', r'\bbalinese\b', r'\bbetutu\b', r'\bbumbu\s+bali\b', 
                        r'\bmasakan\s+bali\b'],
                'aceh': [r'\baceh\b', r'\bacehnese\b', r'\bmie\s+aceh\b', r'\bkuah\s+pliek\b', 
                        r'\bmasakan\s+aceh\b'],
                'betawi': [r'\bbetawi\b', r'\bjakarta\b', r'\bkerak\s+telor\b', r'\bketoprak\b'],
                'palembang': [r'\bpalembang\b', r'\bsumatera\s+selatan\b', r'\bpempek\b', 
                             r'\btekwan\b', r'\bsumsel\b'],
                'lombok': [r'\blombok\b', r'\bsasak\b', r'\bplecing\b', r'\bayam\s+taliwang\b'],
                'medan': [r'\bmedan\b', r'\bbatak\b', r'\bbika\s+ambon\b', r'\bsoto\s+medan\b'],
            }
            
            detected_regions = []
            
            for region_name, patterns in regional_patterns.items():
                if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns):
                    detected_regions.append(region_name)
            
            if detected_regions:
                all_regions = list(set(features['region'] + detected_regions))
                features['region'] = all_regions
            
            return features
            
        except Exception as e:
            logger.error(f"Error enhancing regional detection: {e}")
            return features
    
    @staticmethod
    def create_search_text(row: pd.Series) -> str:
        """Enhanced searchable text creation with better feature weighting"""
        try:
            title = TextProcessor.preprocess_text(str(row.get('title', '')))
            ingredients = TextProcessor.preprocess_text(str(row.get('ingredients', '')))
            description = TextProcessor.preprocess_text(str(row.get('description', '')))
            
            search_parts = []
            
            if title:
                search_parts.extend([title] * 10)
            if ingredients:
                search_parts.extend([ingredients] * 5)
            if description:
                search_parts.extend([description] * 2)
            
            try:
                title_features = TextProcessor.extract_features(title) if title else {}
                ingredient_features = TextProcessor.extract_features(ingredients) if ingredients else {}
                
                for features in [title_features, ingredient_features]:
                    for feature_list in features.values():
                        if feature_list:
                            search_parts.extend(feature_list * 3)
            except Exception as e:
                logger.warning(f"Error extracting features for search text: {e}")
            
            result = ' '.join(filter(None, search_parts))
            return result if result.strip() else "makanan"
            
        except Exception as e:
            logger.error(f"Error creating search text: {e}")
            return "makanan"
    
    @staticmethod
    def calculate_similarity_ratio(s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings with error handling"""
        try:
            if not s1 or not s2:
                return 0.0
            return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            return 0.0
    
    @staticmethod
    def calculate_tfidf_score(query: str, menu_text: str, all_menu_texts: List[str]) -> float:
        """Calculate TF-IDF based relevance score with error handling"""
        try:
            if not query or not menu_text or not all_menu_texts:
                return 0.0
                
            documents = [query] + all_menu_texts + [menu_text]
            
            vectorizer = TfidfVectorizer(
                lowercase=True,
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=None
            )
            
            tfidf_matrix = vectorizer.fit_transform(documents)
            query_vector = tfidf_matrix[0]
            menu_vector = tfidf_matrix[-1]
            
            similarity = cosine_similarity(query_vector, menu_vector)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"TF-IDF calculation error: {e}")
            return 0.0
    
    @staticmethod
    def extract_numeric_price(price_text) -> int:
        """Extract numeric value from price text with error handling"""
        try:
            if pd.isna(price_text) or price_text == "":
                return 0
            
            price_clean = re.sub(r'[^\d.]', '', str(price_text))
            return int(float(price_clean)) if price_clean else 0
        except Exception as e:
            logger.warning(f"Error extracting price: {e}")
            return 0
    
    @staticmethod
    def format_price(price) -> str:
        """Format price to Indonesian Rupiah with error handling"""
        try:
            if pd.isna(price) or price == "" or price == 0:
                return "Harga belum tersedia"
            
            if isinstance(price, str):
                price_clean = re.sub(r'[^\d]', '', str(price))
                price_num = float(price_clean) if price_clean else 0
            else:
                price_num = float(price)
            
            return f"Rp {price_num:,.0f}".replace(',', '.')
        except Exception as e:
            logger.warning(f"Error formatting price: {e}")
            return str(price) if price else "Harga belum tersedia"
    
    @staticmethod
    def extract_category_from_query(query: str) -> str:
        """Extract category description from query with error handling"""
        try:
            features = TextProcessor.extract_features(query)
            return TextProcessor.get_category_from_multiple_features(features)
        except Exception as e:
            logger.warning(f"Error extracting category from query: {e}")
            return "pilihan"
    
    @staticmethod
    def extract_category_from_title(title: str) -> str:
        """Extract category from menu title with error handling"""
        try:
            if not title:
                return "makanan"
                
            features = TextProcessor.extract_features(title)
            
            if 'protein' in features and features['protein']:
                proteins = features['protein']
                if 'vegetarian' in proteins:
                    return 'vegetarian'
                elif any(seafood in proteins for seafood in ['seafood', 'ikan', 'udang', 'cumi']):
                    return 'seafood'
                else:
                    return proteins[0]
            elif 'dish_type' in features and features['dish_type']:
                return features['dish_type'][0]
            else:
                return "makanan"
                
        except Exception as e:
            logger.warning(f"Error extracting category from title: {e}")
            return "makanan"
    
    @staticmethod
    def get_category_from_multiple_features(features: Dict) -> str:
        """Generate natural category description with enhanced multi-value support"""
        try:
            if not features:
                return "pilihan"
                
            parts = []
            
            priority_order = ['dish_type', 'protein', 'cooking_method', 'flavor', 'region', 'texture']
            
            for feature_type in priority_order:
                if feature_type in features and features[feature_type]:
                    feature_values = features[feature_type]
                    if not feature_values:
                        continue
                        
                    if feature_type == 'protein':
                        protein = feature_values[0]
                        if protein == 'vegetarian':
                            parts.append('vegetarian')
                        elif protein in ['seafood', 'ikan', 'udang', 'cumi', 'kepiting']:
                            parts.append('seafood')
                        else:
                            parts.append(protein)
                    elif feature_type == 'cooking_method':
                        parts.append(feature_values[0])
                    elif feature_type == 'flavor':
                        flavors = feature_values
                        for flavor in flavors:
                            if flavor in ['berkuah', 'kering']:
                                parts.append(flavor)
                            elif flavor in ['pedas', 'manis', 'asam', 'gurih']:
                                parts.append(f"rasa {flavor}")
                            else:
                                parts.append(flavor)
                    elif feature_type == 'dish_type':
                        dish = feature_values[0]
                        if dish == 'vegetarian_dish':
                            parts.append('sayuran')
                        else:
                            parts.append(dish)
                    elif feature_type == 'region':
                        parts.append(f"khas {feature_values[0]}")
                    elif feature_type == 'texture':
                        parts.append(f"{feature_values[0]}")
            
            if parts:
                if len(parts) == 1:
                    return parts[0]
                elif len(parts) == 2:
                    return f"{parts[0]} yang {parts[1]}"
                else:
                    return f"{parts[0]} yang {' dan '.join(parts[1:])}"
            else:
                return 'pilihan'
                
        except Exception as e:
            logger.error(f"Error generating category description: {e}")
            return 'pilihan'