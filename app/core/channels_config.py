"""
Configuration for Ethiopian Medical Telegram Channels
"""
from typing import List, Dict, Any

# Ethiopian Medical Telegram Channels
ETHIOPIAN_MEDICAL_CHANNELS = [
    {
        "name": "lobelia4cosmetics",
        "url": "https://t.me/lobelia4cosmetics",
        "description": "Lobelia Cosmetics - Beauty and skincare products",
        "category": "cosmetics",
        "active": True,
        "priority": "high"
    },
    {
        "name": "tikvahpharma",
        "url": "https://t.me/tikvahpharma",
        "description": "Tikvah Pharmaceuticals - Medical supplies and pharmaceuticals",
        "category": "pharmaceuticals",
        "active": True,
        "priority": "high"
    },
    {
        "name": "chemed_ethiopia",
        "url": "https://t.me/chemed_ethiopia",
        "description": "Chemed Ethiopia - Chemical and medical supplies",
        "category": "medical_supplies",
        "active": True,
        "priority": "high"
    },
    {
        "name": "ethiopian_pharmacy",
        "url": "https://t.me/ethiopian_pharmacy",
        "description": "Ethiopian Pharmacy Network",
        "category": "pharmacy",
        "active": True,
        "priority": "medium"
    },
    {
        "name": "medical_supplies_ethiopia",
        "url": "https://t.me/medical_supplies_ethiopia",
        "description": "Medical Supplies Ethiopia",
        "category": "medical_supplies",
        "active": True,
        "priority": "medium"
    },
    {
        "name": "healthcare_ethiopia",
        "url": "https://t.me/healthcare_ethiopia",
        "description": "Healthcare Ethiopia",
        "category": "healthcare",
        "active": True,
        "priority": "medium"
    },
    {
        "name": "pharmaceutical_ethiopia",
        "url": "https://t.me/pharmaceutical_ethiopia",
        "description": "Pharmaceutical Ethiopia",
        "category": "pharmaceuticals",
        "active": True,
        "priority": "medium"
    }
]

# Additional channels from et.tgstat.com/medicine
ADDITIONAL_MEDICAL_CHANNELS = [
    {
        "name": "ethiopia_medicine",
        "url": "https://t.me/ethiopia_medicine",
        "description": "Ethiopia Medicine",
        "category": "general",
        "active": True,
        "priority": "low"
    },
    {
        "name": "addis_pharmacy",
        "url": "https://t.me/addis_pharmacy",
        "description": "Addis Ababa Pharmacy",
        "category": "pharmacy",
        "active": True,
        "priority": "low"
    },
    {
        "name": "ethiopia_health",
        "url": "https://t.me/ethiopia_health",
        "description": "Ethiopia Health",
        "category": "healthcare",
        "active": True,
        "priority": "low"
    },
    {
        "name": "ethiopian_pharmaceuticals",
        "url": "https://t.me/ethiopian_pharmaceuticals",
        "description": "Ethiopian Pharmaceuticals",
        "category": "pharmaceuticals",
        "active": True,
        "priority": "medium"
    },
    {
        "name": "medical_ethiopia",
        "url": "https://t.me/medical_ethiopia",
        "description": "Medical Ethiopia",
        "category": "healthcare",
        "active": True,
        "priority": "medium"
    },
    {
        "name": "pharmacy_ethiopia",
        "url": "https://t.me/pharmacy_ethiopia",
        "description": "Pharmacy Ethiopia",
        "category": "pharmacy",
        "active": True,
        "priority": "medium"
    },
    {
        "name": "health_ethiopia",
        "url": "https://t.me/health_ethiopia",
        "description": "Health Ethiopia",
        "category": "healthcare",
        "active": True,
        "priority": "low"
    },
    {
        "name": "medicine_ethiopia",
        "url": "https://t.me/medicine_ethiopia",
        "description": "Medicine Ethiopia",
        "category": "pharmaceuticals",
        "active": True,
        "priority": "low"
    },
    {
        "name": "ethiopian_healthcare",
        "url": "https://t.me/ethiopian_healthcare",
        "description": "Ethiopian Healthcare",
        "category": "healthcare",
        "active": True,
        "priority": "low"
    },
    {
        "name": "addis_medicine",
        "url": "https://t.me/addis_medicine",
        "description": "Addis Medicine",
        "category": "pharmaceuticals",
        "active": True,
        "priority": "low"
    }
]

def get_all_channels() -> List[Dict[str, Any]]:
    """Get all configured channels"""
    return ETHIOPIAN_MEDICAL_CHANNELS + ADDITIONAL_MEDICAL_CHANNELS

def get_active_channels() -> List[Dict[str, Any]]:
    """Get only active channels"""
    return [channel for channel in get_all_channels() if channel.get("active", True)]

def get_channels_by_category(category: str) -> List[Dict[str, Any]]:
    """Get channels by category"""
    return [channel for channel in get_active_channels() if channel.get("category") == category]

def get_channels_by_priority(priority: str) -> List[Dict[str, Any]]:
    """Get channels by priority"""
    return [channel for channel in get_active_channels() if channel.get("priority") == priority]

def get_channel_names() -> List[str]:
    """Get list of channel names"""
    return [channel["name"] for channel in get_active_channels()]

def get_high_priority_channels() -> List[str]:
    """Get high priority channel names"""
    return [channel["name"] for channel in get_channels_by_priority("high")]

# Channel categories for analysis
CHANNEL_CATEGORIES = {
    "cosmetics": "Beauty and skincare products",
    "pharmaceuticals": "Pharmaceutical drugs and medicines",
    "medical_supplies": "Medical equipment and supplies",
    "pharmacy": "Pharmacy services and products",
    "healthcare": "General healthcare information",
    "general": "General medical information"
}

# Keywords for medical product detection
MEDICAL_KEYWORDS = [
    # Pharmaceuticals
    "antibiotic", "antibiotics", "painkiller", "painkillers", "tablet", "tablets",
    "capsule", "capsules", "syrup", "injection", "vaccine", "vaccines",
    "medicine", "medicines", "drug", "drugs", "pharmaceutical", "pharmaceuticals",
    
    # Medical supplies
    "bandage", "bandages", "gauze", "surgical", "surgery", "equipment",
    "thermometer", "stethoscope", "syringe", "syringes", "needle", "needles",
    "gloves", "mask", "masks", "sanitizer", "disinfectant",
    
    # Cosmetics and personal care
    "cream", "creams", "lotion", "lotions", "soap", "shampoo", "conditioner",
    "makeup", "cosmetic", "cosmetics", "beauty", "skincare", "moisturizer",
    
    # Ethiopian medical terms (Amharic/English)
    "medhanit", "medhanite", "tibeb", "tibeboch", "seret", "seretoch",
    "medicine", "medicines", "drug", "drugs", "pharmacy", "pharmacies"
]

# Price patterns for extraction
PRICE_PATTERNS = [
    r"(\d+)\s*(?:birr|ETB|ብር)",
    r"(\d+)\s*(?:dollar|USD|\$)",
    r"(\d+)\s*(?:euro|EUR|€)",
    r"price[:\s]*(\d+)",
    r"cost[:\s]*(\d+)",
    r"(\d+)\s*(?:price|cost)"
] 