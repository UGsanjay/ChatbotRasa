"""Model and search configuration with enhanced error handling"""

MODEL_CONFIG = {
    'primary_model': 'all-MiniLM-L6-v2',
    'backup_model': 'all-MiniLM-L12-v2',
    'models_dir': 'models',
    'cache_size': 1000,
    'batch_size': 32
}

SEARCH_CONFIG = {
    'max_results': 8,
    'similarity_threshold': 0.3,
    'min_score_threshold': 30,
    'fuzzy_match_threshold': 0.85,
    'semantic_weight': 0.4,
    'keyword_weight': 0.6
}

SCORING_CONFIG = {
    'exact_title_bonus': 70,
    'protein_bonus': 50,
    'vegetarian_bonus': 60,
    'seafood_bonus': 55,
    'cooking_method_bonus': 35,
    'flavor_bonus': 30,
    'dish_type_bonus': 25,
    'region_bonus': 20,
    'missing_value_penalty': 12,
    'perfect_category_bonus': 35
}

RESPONSE_TEMPLATES = {
    'greeting': [
        'Halo! Saya siap membantu mencari menu makanan. Apa yang ingin Anda cari hari ini?',
        'Selamat datang! Silakan sebutkan menu yang Anda inginkan.',
        'Halo! Ada menu khusus yang ingin Anda cari?'
    ],
    'success': [
        'Menemukan {count} menu {category} terbaik untuk Anda!',
        'Berikut {count} rekomendasi menu {category} pilihan!',
        'Saya menemukan {count} menu {category} yang cocok!'
    ],
    'failure': [
        'Maaf, tidak menemukan menu {query} yang sesuai.',
        'Tidak ada hasil untuk "{query}". Coba kata kunci lain?',
        'Menu {query} tidak ditemukan. Ada alternatif lain?'
    ],
    'error': [
        'Terjadi kesalahan saat mencari menu.',
        'Ada masalah teknis. Silakan coba lagi.',
        'Error dalam pencarian. Coba kata kunci yang berbeda.'
    ]
}