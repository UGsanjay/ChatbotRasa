"""Indonesian food keywords for feature extraction - FIXED logic with proper separation"""

FOOD_KEYWORDS = {
    'protein': {
        'ayam': ['ayam', 'chicken', 'dada ayam', 'paha ayam', 'ayam kampung', 'ayam broiler', 'ayam potong', 'ayam fillet', 'ayam ungkep'],
        'sapi': ['sapi', 'daging sapi', 'beef', 'dendeng', 'has dalam', 'has luar', 'sirloin', 'tenderloin', 'daging'],
        'kambing': ['kambing', 'goat', 'daging kambing', 'kambing muda'],
        'bebek': ['bebek', 'duck', 'bebek panggang', 'bebek goreng', 'itik'],
        'babi': ['babi', 'pork', 'daging babi'],
        'telur': ['telur', 'egg', 'telor', 'telur dadar', 'telur mata sapi', 'telur rebus', 'telur ceplok', 'telur puyuh'],
        
        # SEAFOOD 
        'ikan': ['ikan', 'fish', 'salmon', 'tuna', 'kakap', 'bandeng', 'lele', 'nila', 'tenggiri', 'gurame', 'mujair', 'patin', 'baronang', 'kembung', 'tongkol', 'cakalang', 'gabus', 'mas', 'cupang', 'bawal', 'dori'],
        'udang': ['udang', 'shrimp', 'prawn', 'udang windu', 'udang vannamei', 'udang galah', 'udang rebon', 'udang kering', 'ebi'],
        'cumi': ['cumi', 'squid', 'sotong', 'cumi-cumi', 'cumi asin', 'cumi basah'],
        'kepiting': ['kepiting', 'crab', 'rajungan', 'ketam'],
        'kerang': ['kerang', 'mussel', 'clam', 'kerang hijau', 'kerang darah', 'remis'],
        'lobster': ['lobster', 'udang galah besar'],
        
        # VEGETARIAN 
        'vegetarian': [
            'vegetarian', 'vegan', 'nabati', 'plant based', 'tanpa daging', 'non meat',
            'tahu', 'tofu', 'tahoo', 'tahu putih', 'tahu kuning', 'tahu goreng', 'tahu bacem',
            'tempe', 'tempeh', 'tempe mendoan', 'tempe bacem', 'tempe goreng',
            'jamur', 'mushroom', 'jamur kuping', 'jamur merang', 'jamur shiitake'
        ]
    },
    'cooking_method': {
        'goreng': ['goreng', 'fried', 'digoreng', 'crispy', 'garing', 'renyah', 'deep fry', 'pan fry'],
        'bakar': ['bakar', 'grilled', 'panggang', 'dibakar', 'dipanggang', 'barbecue', 'bbq', 'grill'],
        'rebus': ['rebus', 'boiled', 'direbus', 'tim', 'dikukus air'],
        'kukus': ['kukus', 'steamed', 'dikukus', 'steam'],
        'tumis': ['tumis', 'stir-fry', 'ditumis', 'menumis', 'stir fry', 'cah'],
        'oseng': ['oseng', 'dioseng', 'oseng-oseng'],
        'rica': ['rica', 'rica-rica', 'dirica'],
        'balado': ['balado', 'dibalado', 'sambal balado'],
        'gulai': ['gulai', 'curry', 'kari', 'santan', 'berkuah santan'],
        'woku': ['woku', 'diwoku'],
        'rendang': ['rendang', 'kalio', 'randang'],
        'pop': ['pop', 'dipop'],
        'pepes': ['pepes', 'dipepes', 'wrapped'],
        'asap': ['asap', 'diasap', 'smoked'],
        'presto': ['presto', 'dipresto'],
        'serundeng': ['serundeng', 'diserudeng'],
        'ungkep': ['ungkep', 'diungkep'],
        'crispy': ['crispy', 'krispi', 'renyah', 'garing'],
        'karage': ['karage', 'japanese fried'],
        'teriyaki': ['teriyaki', 'teriyaki sauce'],
        'katsu': ['katsu', 'breaded fried']
    },
    'flavor': {
        'pedas': ['pedas', 'spicy', 'hot', 'cabai', 'chili', 'sambal', 'cabe', 'rica', 'balado', 'level', 'pedes', 'nyelekit', 'panas'],
        'manis': ['manis', 'sweet', 'gula', 'kecap manis', 'gula jawa', 'palm sugar', 'gula aren', 'manis gurih'],
        'gurih': ['gurih', 'savory', 'asin', 'salty', 'umami', 'sedap'],
        'asam': ['asam', 'sour', 'tamarind', 'belimbing', 'jeruk', 'lime', 'asem', 'kecut'],
        'berkuah': ['kuah', 'berkuah', 'soup', 'broth', 'soto', 'sup', 'kaldu', 'sauce', 'air', 'gravy'],
        'kering': ['kering', 'dry', 'tanpa kuah', 'tidak berkuah', 'sambal kering'],
        'original': ['original', 'ori', 'plain', 'biasa', 'standar', 'polos'],
        'segar': ['segar', 'fresh', 'sejuk', 'dingin'],
        'sehat': ['sehat', 'healthy', 'diet', 'low fat', 'rendah lemak'],
        'bumbu_bali': ['bumbu bali', 'bali', 'base genep'],
        'bumbu_rujak': ['bumbu rujak', 'rujak', 'petis'],
        'kelapa': ['kelapa', 'coconut', 'parut', 'santan'],
        'mentega': ['mentega', 'butter', 'margarin']
    },
    'dish_type': {
        'sup': ['sup', 'soup', 'soto', 'bakso'],
        'soto': ['soto', 'soup', 'sup', 'coto', 'sroto'],
        'nasi': ['nasi', 'rice', 'beras', 'nasi putih', 'nasi merah', 'nasi goreng', 'nasi campur'],
        'mie': ['mie', 'mi', 'noodle', 'bakmi', 'mee', 'noodles', 'pasta', 'kwetiau', 'bihun'],
        'rujak': ['rujak', 'fruit salad', 'asinan', 'rujak buah'],
        'pecel': ['pecel', 'vegetable salad', 'lalapan'],
        'sate': ['sate', 'satay', 'tusuk', 'sate ayam', 'sate kambing'],
        'pempek': ['pempek', 'empek-empek', 'pempek kapal selam'],
        'gudeg': ['gudeg', 'nangka muda'],
        'rawon': ['rawon', 'rawon daging'],
        'bakso': ['bakso', 'baso', 'meatball'],
        'siomay': ['siomay', 'somay', 'dimsum'],
        'martabak': ['martabak', 'terang bulan'],
        'kerak_telor': ['kerak telor', 'kerak telur'],
        'ketoprak': ['ketoprak'],
        'lotek': ['lotek'],
        'karedok': ['karedok'],
        'lalapan': ['lalapan', 'lalap', 'fresh vegetables'],
        'kerupuk': ['kerupuk', 'krupuk', 'crackers'],
        'salad': ['salad', 'vegetable salad', 'fruit salad'],
        
        # VEGETARIAN DISHES 
        'vegetarian_dish': [
            'cap cay', 'capcay', 'sayur asem', 'sayur sop', 'sayur bayam', 
            'kangkung', 'terong', 'toge', 'tahu isi', 'tempe orek', 'sayur lodeh', 
            'urap', 'plecing kangkung', 'tumis kangkung', 'cah kangkung',
            'tumis tahu', 'tempe bacem', 'oseng tempe', 'gudangan', 'karedok',
            'pecel sayur', 'gado gado', 'asinan sayur', 'tumis jamur'
        ]
    },
    'region': {
        'padang': ['padang', 'minang', 'sumatera barat', 'rendang', 'gulai', 'minangkabau'],
        'manado': ['manado', 'sulawesi utara', 'woku', 'rica', 'minahasa'],
        'jawa': ['jawa', 'javanese', 'jogja', 'solo', 'semarang', 'gudeg', 'rawon', 'yogyakarta'],
        'sunda': ['sunda', 'bandung', 'priangan', 'karedok', 'pepes', 'sundanese'],
        'bali': ['bali', 'balinese', 'betutu', 'bumbu bali'],
        'aceh': ['aceh', 'acehnese', 'mie aceh', 'kuah pliek'],
        'betawi': ['betawi', 'jakarta', 'kerak telor', 'ketoprak'],
        'palembang': ['palembang', 'sumatera selatan', 'pempek', 'tekwan', 'sumsel'],
        'madura': ['madura', 'madurese', 'sate madura'],
        'lombok': ['lombok', 'sasak', 'plecing', 'ayam taliwang'],
        'medan': ['medan', 'batak', 'bika ambon', 'soto medan'],
        'makassar': ['makassar', 'bugis', 'coto makassar', 'konro'],
        'solo': ['solo', 'surakarta', 'serabi', 'gudeg solo'],
        'chinese': ['chinese', 'cina', 'tionghoa', 'hakka', 'hokkien', 'hong kong'],
        'japanese': ['japanese', 'jepang', 'sushi', 'teriyaki', 'katsu'],
        'western': ['western', 'barat', 'american', 'italian']
    },
    'texture': {
        'crispy': ['crispy', 'krispi', 'renyah', 'garing'],
        'tender': ['tender', 'empuk', 'lembut'],
        'chewy': ['chewy', 'kenyal', 'alot'],
        'creamy': ['creamy', 'krim', 'lembut creamy'],
        'crunchy': ['crunchy', 'kriuk', 'berbunyi'],
        'juicy': ['juicy', 'berair', 'segar']
    },
    'serving_style': {
        'sambal': ['sambal', 'cabe', 'lombok', 'sauce pedas'],
        'kerupuk': ['kerupuk', 'krupuk', 'crackers'],
        'lalapan': ['lalapan', 'lalap', 'raw vegetables'],
        'nasi_putih': ['nasi putih', 'nasi', 'steamed rice'],
        'kuah_terpisah': ['kuah terpisah', 'dipping sauce'],
        'set_meal': ['paket', 'set meal', 'combo']
    }
}

FOOD_SYNONYMS = {
    'ayam': ['ayam', 'chicken'],
    'sapi': ['sapi', 'beef', 'daging sapi'],
    'kambing': ['kambing', 'goat'],
    'bebek': ['bebek', 'duck', 'itik'],
    'babi': ['babi', 'pork'],
    'telur': ['telur', 'egg', 'telor'],
    
    'ikan': ['ikan', 'fish'],  
    'udang': ['udang', 'shrimp', 'prawn'],
    'cumi': ['cumi', 'squid', 'sotong'],
    'kepiting': ['kepiting', 'crab', 'rajungan'],
    'kerang': ['kerang', 'mussel', 'clam'],
    
    'vegetarian': ['vegetarian', 'vegan', 'nabati', 'plant based'],
    'tahu': ['tahu', 'tofu', 'bean curd'],
    'tempe': ['tempe', 'tempeh'],
    'jamur': ['jamur', 'mushroom'],
    
    # COOKING METHODS
    'pedas': ['pedas', 'pedes', 'hot', 'spicy'],
    'manis': ['manis', 'sweet'],
    'gurih': ['gurih', 'savory', 'asin'],
    'goreng': ['goreng', 'fried', 'fry'],
    'rebus': ['rebus', 'boiled'],
    'bakar': ['bakar', 'grilled', 'grill'],
    'tumis': ['tumis', 'stir-fry', 'cah'],
    'kukus': ['kukus', 'steamed'],
    
    # DISH TYPES
    'soto': ['soto', 'coto', 'sroto'],
    'bakso': ['bakso', 'baso'],
    'mie': ['mie', 'mi', 'mee', 'noodle'],
    'nasi': ['nasi', 'rice'],
    'rendang': ['rendang', 'kalio'],
    'sambal': ['sambal', 'cabe', 'cabai'],
    
    # VEGETABLES
    'kangkung': ['kangkung', 'water spinach'],
    'bayam': ['bayam', 'spinach'],
    'terong': ['terong', 'eggplant'],
    'toge': ['toge', 'bean sprouts', 'tauge'],
    'wortel': ['wortel', 'carrot'],
    'buncis': ['buncis', 'green beans'],
    'jagung': ['jagung', 'corn'],
    'kentang': ['kentang', 'potato']
}