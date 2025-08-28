import logging
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Set
from config.model_config import SEARCH_CONFIG, SCORING_CONFIG
from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class MenuSearcher:
    """Fixed menu search with balanced single/multi-value accuracy"""
    
    def search_menus(self, query: str, available_menus_df: pd.DataFrame) -> List[pd.Series]:
        """Fixed search with proper single-value and multi-value handling"""
        try:
            if available_menus_df.empty or not query.strip():
                return []
                
            query_clean = TextProcessor.preprocess_text(query)
            query_features = TextProcessor.extract_features(query_clean)
            
            logger.info(f"Fixed search: '{query}' -> Features: {query_features}")
            
            filtered_df = self._apply_smart_filtering(query_features, available_menus_df, query_clean)
            logger.info(f"After smart filtering: {len(filtered_df)} menus remain")
            
            if filtered_df.empty:
                logger.warning("No menus passed smart filtering")
                filtered_df = available_menus_df.copy()
            
            matches = []
            query_requirements = self._analyze_query_requirements(query_features)
            
            for idx, menu in filtered_df.iterrows():
                try:
                    score_data = self._calculate_balanced_score(
                        menu, query_features, query_requirements, query_clean
                    )
                    
                    if score_data['should_include']:
                        matches.append((
                            score_data['total_score'],
                            menu,
                            score_data['satisfaction_ratio'],
                            score_data['relevance_score'],
                            score_data['match_details']
                        ))
                        
                except Exception as e:
                    logger.error(f"Error processing menu {menu.get('title', 'Unknown')}: {e}")
                    continue
            
            matches.sort(key=lambda x: (x[0], x[3]), reverse=True)
            
            self._log_detailed_results(query, matches[:SEARCH_CONFIG.get('max_results', 8)])
            
            return [match[1] for match in matches[:SEARCH_CONFIG.get('max_results', 8)]]
            
        except Exception as e:
            logger.error(f"Critical error in fixed search: {e}")
            return []
    
    def _apply_smart_filtering(self, query_features: Dict, available_menus_df: pd.DataFrame, query_clean: str) -> pd.DataFrame:
        """Smart filtering that's less aggressive for single-value queries"""
        try:
            if not query_features:
                return available_menus_df
            
            is_vegetarian = self._is_strict_vegetarian_query(query_features)
            is_seafood = self._is_strict_seafood_query(query_features)
            
            if is_vegetarian and 'vegetarian' in query_clean.lower():
                logger.info("Applying strict vegetarian filtering")
                return self._filter_vegetarian_menus(available_menus_df)
            elif is_seafood and any(word in query_clean.lower() for word in ['seafood', 'laut']):
                logger.info("Applying strict seafood filtering") 
                return self._filter_seafood_menus_enhanced(available_menus_df)
            
            return available_menus_df
            
        except Exception as e:
            logger.error(f"Error in smart filtering: {e}")
            return available_menus_df
    
    def _calculate_balanced_score(self, menu: pd.Series, query_features: Dict, 
                                 query_requirements: Dict, query_clean: str) -> Dict:
        """Balanced scoring that works well for both single and multi-value queries"""
        try:
            score_data = {
                'total_score': 0,
                'requirements_met': 0,
                'total_requirements': query_requirements['total_values'],
                'satisfaction_ratio': 0.0,
                'relevance_score': 0.0,
                'should_include': False,
                'match_details': {}
            }
            
            title = str(menu.get('title', ''))
            ingredients = str(menu.get('ingredients', ''))
            description = str(menu.get('description', ''))
            menu_text = f"{title} {ingredients} {description}".lower()
            
            menu_features = TextProcessor.extract_features(menu_text)
            
            text_relevance_score = self._calculate_text_relevance(query_clean, title, ingredients, description)
            score_data['relevance_score'] = text_relevance_score
            score_data['total_score'] += text_relevance_score
            
            feature_score = 0
            categories_satisfied = 0
            
            for feature_type, required_values in query_features.items():
                if not required_values:
                    continue
                    
                menu_values = set(menu_features.get(feature_type, []))
                required_set = set(required_values)
                matched_values = required_set.intersection(menu_values)
                
                score_data['match_details'][feature_type] = {
                    'required': list(required_values),
                    'found': list(menu_values),
                    'matched': list(matched_values),
                    'match_ratio': len(matched_values) / len(required_values) if required_values else 0
                }
                
                if matched_values:
                    score_data['requirements_met'] += len(matched_values)
                    
                    if feature_type == 'protein':
                        if 'vegetarian' in matched_values:
                            feature_score += SCORING_CONFIG['vegetarian_bonus']
                        elif any(seafood in matched_values for seafood in ['seafood', 'ikan', 'udang', 'cumi']):
                            feature_score += SCORING_CONFIG['seafood_bonus']
                        elif 'sapi' in matched_values:
                            feature_score += SCORING_CONFIG['protein_bonus'] + 20 
                        else:
                            feature_score += SCORING_CONFIG['protein_bonus']
                            
                    elif feature_type == 'flavor':
                        for matched_flavor in matched_values:
                            if matched_flavor in ['pedas', 'manis', 'asam', 'gurih']:
                                feature_score += SCORING_CONFIG['flavor_bonus']
                            elif matched_flavor in ['berkuah', 'kering']:
                                feature_score += SCORING_CONFIG['flavor_bonus'] * 0.7
                            
                    elif feature_type == 'cooking_method':
                        feature_score += SCORING_CONFIG['cooking_method_bonus']
                    elif feature_type == 'dish_type':
                        feature_score += SCORING_CONFIG['dish_type_bonus']
                    elif feature_type == 'region':
                        for matched_region in matched_values:
                            if matched_region == 'padang':
                                feature_score += SCORING_CONFIG['region_bonus'] + 15  
                            else:
                                feature_score += SCORING_CONFIG['region_bonus']
                    else:
                        feature_score += 20  
                    
                    categories_satisfied += 1
                
                elif query_requirements['is_multi_value']:
                    feature_score -= SCORING_CONFIG['missing_value_penalty'] * len(required_values - matched_values)
            
            score_data['total_score'] += feature_score
            
            if score_data['total_requirements'] > 0:
                score_data['satisfaction_ratio'] = score_data['requirements_met'] / score_data['total_requirements']
            else:
                score_data['satisfaction_ratio'] = 1.0
            
            if categories_satisfied == len(query_features) and categories_satisfied > 0:
                score_data['total_score'] += SCORING_CONFIG['perfect_category_bonus']
            
            min_threshold = SEARCH_CONFIG.get('min_score_threshold', 30)
            
            if query_requirements['is_multi_value'] or query_requirements['is_multi_category']:
                required_satisfaction = 0.75  
                score_data['should_include'] = (
                    score_data['satisfaction_ratio'] >= required_satisfaction and
                    score_data['total_score'] >= min_threshold
                )
            else:
                score_data['should_include'] = (
                    (score_data['satisfaction_ratio'] >= 0.3 or score_data['relevance_score'] >= 40) and
                    score_data['total_score'] >= (min_threshold * 0.7)  
                )
            
            return score_data
            
        except Exception as e:
            logger.error(f"Error calculating balanced score: {e}")
            return {
                'total_score': 0, 'requirements_met': 0, 'total_requirements': 0,
                'satisfaction_ratio': 0.0, 'relevance_score': 0.0, 
                'should_include': False, 'match_details': {}
            }
    
    def _calculate_text_relevance(self, query_clean: str, title: str, ingredients: str, description: str) -> float:
        """Calculate direct text relevance score"""
        try:
            relevance_score = 0
            query_words = query_clean.lower().split()
            
            title_lower = title.lower()
            ingredients_lower = ingredients.lower()  
            description_lower = description.lower()
            
            for word in query_words:
                if len(word) > 2:  
                    if word in title_lower:
                        relevance_score += 50
                    elif word in ingredients_lower:
                        relevance_score += 25
                    elif word in description_lower:
                        relevance_score += 10
                    
                    if len(word) > 4:
                        for text, weight in [(title_lower, 30), (ingredients_lower, 15)]:
                            for text_word in text.split():
                                if len(text_word) > 4 and word in text_word:
                                    relevance_score += weight * 0.5
            
            return relevance_score
            
        except Exception as e:
            logger.warning(f"Error calculating text relevance: {e}")
            return 0.0
    
    def _analyze_query_requirements(self, query_features: Dict) -> Dict:
        """Analyze query requirements with better detection"""
        requirements = {
            'total_categories': len(query_features),
            'total_values': sum(len(values) for values in query_features.values()),
            'categories': query_features,
            'is_multi_value': False,
            'is_multi_category': False
        }
        
        requirements['is_multi_category'] = len(query_features) > 1
        requirements['is_multi_value'] = any(len(values) > 1 for values in query_features.values())
        
        return requirements
    
    def _filter_seafood_menus_enhanced(self, available_menus_df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced seafood filtering with comprehensive patterns"""
        try:
            seafood_indicators = [
                r'\bikan\b', r'\bfish\b', r'\bseafood\b',
                r'\budang\b', r'\bshrimp\b', r'\bprawn\b',
                r'\bcumi\b', r'\bsquid\b', r'\bsotong\b',
                r'\bkepiting\b', r'\bcrab\b', r'\brajungan\b',
                r'\bkerang\b', r'\bmussel\b', r'\bclam\b',
                r'\blobster\b', r'\bmakanan\s+laut\b',
                
                r'\bsalmon\b', r'\btuna\b', r'\bkakap\b', r'\bgurame\b',
                r'\blele\b', r'\bnila\b', r'\bbandeng\b', r'\btenggiri\b',
                r'\bmujair\b', r'\bpatin\b', r'\bbawal\b', r'\bdori\b'
            ]
            
            exclusion_patterns = [
                r'\bayam\b', r'\bchicken\b', r'\bsapi\b', r'\bbeef\b',
                r'\bkambing\b', r'\bgoat\b', r'\bbebek\b', r'\bduck\b',
                r'\btelur\b', r'\begg\b', r'\btahu\b', r'\btempe\b'
            ]
            
            seafood_menus = []
            
            for idx, menu in available_menus_df.iterrows():
                try:
                    full_text = f"{menu.get('title', '')} {menu.get('ingredients', '')} {menu.get('description', '')}".lower()
                    
                    has_seafood = any(re.search(pattern, full_text, re.IGNORECASE) 
                                    for pattern in seafood_indicators)
                    has_exclusion = any(re.search(pattern, full_text, re.IGNORECASE) 
                                      for pattern in exclusion_patterns)
                    
                    if has_seafood and not has_exclusion:
                        seafood_menus.append(menu)
                    
                except Exception as e:
                    logger.debug(f"Error processing seafood menu: {e}")
                    continue
            
            if seafood_menus:
                logger.info(f"Enhanced seafood filtering: {len(seafood_menus)} seafood menus found")
                return pd.DataFrame(seafood_menus).reset_index(drop=True)
            else:
                logger.warning("No seafood menus found")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error in enhanced seafood filtering: {e}")
            return available_menus_df
    
    def _filter_vegetarian_menus(self, available_menus_df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced vegetarian filtering"""
        try:
            vegetarian_indicators = [
                r'\btahu\b', r'\btofu\b', r'\btempe\b', r'\btempeh\b',
                r'\bvegetarian\b', r'\bvegan\b', r'\bnabati\b',
                r'\bsayur\b', r'\bjamur\b', r'\bmushroom\b'
            ]
            
            animal_exclusions = [
                r'\bayam\b', r'\bchicken\b', r'\bikan\b', r'\bfish\b',
                r'\bsapi\b', r'\bbeef\b', r'\budang\b', r'\bshrimp\b',
                r'\bcumi\b', r'\bsquid\b', r'\bdaging\b', r'\bmeat\b'
            ]
            
            vegetarian_menus = []
            
            for idx, menu in available_menus_df.iterrows():
                try:
                    full_text = f"{menu.get('title', '')} {menu.get('ingredients', '')} {menu.get('description', '')}".lower()
                    
                    has_vegetarian = any(re.search(pattern, full_text, re.IGNORECASE) 
                                       for pattern in vegetarian_indicators)
                    has_animal = any(re.search(pattern, full_text, re.IGNORECASE) 
                                   for pattern in animal_exclusions)
                    
                    if has_vegetarian and not has_animal:
                        vegetarian_menus.append(menu)
                        
                except Exception as e:
                    logger.debug(f"Error processing vegetarian menu: {e}")
                    continue
            
            if vegetarian_menus:
                logger.info(f"Vegetarian filtering: {len(vegetarian_menus)} vegetarian menus found")
                return pd.DataFrame(vegetarian_menus).reset_index(drop=True)
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error in vegetarian filtering: {e}")
            return available_menus_df
    
    def _is_strict_vegetarian_query(self, query_features: Dict) -> bool:
        """Strict vegetarian detection"""
        try:
            proteins = query_features.get('protein', [])
            return 'vegetarian' in proteins
        except:
            return False
    
    def _is_strict_seafood_query(self, query_features: Dict) -> bool:
        """Enhanced seafood detection"""
        try:
            proteins = query_features.get('protein', [])
            seafood_proteins = ['seafood', 'ikan', 'udang', 'cumi', 'kepiting', 'kerang', 'lobster']
            return any(protein in seafood_proteins for protein in proteins)
        except:
            return False
    
    def _log_detailed_results(self, query: str, matches: List) -> None:
        """Log detailed search results with match information"""
        logger.info(f"FIXED SEARCH RESULTS for '{query}':")
        for i, match in enumerate(matches):
            try:
                score, menu, satisfaction, relevance, match_details = match
                title = menu.get('title', 'Unknown')
                logger.info(f"  {i+1}. {title}")
                logger.info(f"     Score: {score}, Satisfaction: {satisfaction:.2f}, Relevance: {relevance:.1f}")
                
                if match_details:
                    for feature_type, details in match_details.items():
                        if details['matched']:
                            logger.debug(f"     {feature_type}: {details['matched']} (matched from {details['required']})")
                            
            except Exception as e:
                logger.warning(f"Error logging match {i+1}: {e}")