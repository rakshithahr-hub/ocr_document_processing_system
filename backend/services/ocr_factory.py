# services/ocr_factory.py

import os
import sys
from typing import Dict, List, Optional, Any

# ===============================
# LAZY IMPORTS - Only import when needed
# ===============================

def get_tesseract_engine():
    try:
        from services.tesseract.engine import TesseractEngine
        return TesseractEngine
    except ImportError as e:
        print(f"⚠️ Tesseract not available: {e}")
        return None

def get_surya_engine():
    try:
        from services.surya.engine import SuryaEngine
        return SuryaEngine
    except ImportError as e:
        print(f"⚠️ Surya not available: {e}")
        return None

def get_paddle_engine():
    try:
        from services.paddle.engine import PaddleEngine
        return PaddleEngine
    except ImportError as e:
        print(f"⚠️ Paddle not available: {e}")
        return None

def get_easyocr_engine():
    """Lazy import for EasyOCR engine"""
    try:
        from services.easyocr.engine import EasyOCREngine
        return EasyOCREngine
    except ImportError as e:
        print(f"⚠️ EasyOCR not available: {e}")
        return None


class OCRFactory:
    """
    Factory class for creating OCR engine instances.
    Uses lazy loading to avoid import errors when engines are not installed.
    """
    
    _ENGINE_REGISTRY = {
        "tesseract": {
            "loader": get_tesseract_engine,
            "name": "Tesseract OCR",
            "description": "Open-source OCR engine by Google",
            "languages": "100+ languages",
            "requires_install": False,
            "install_cmd": None,
            "_class": None,
            "_available": None
        },
        "surya": {
            "loader": get_surya_engine,
            "name": "Surya OCR",
            "description": "State-of-the-art OCR with 90+ languages",
            "languages": "90+ languages",
            "requires_install": True,
            "install_cmd": "pip install surya-ocr",
            "_class": None,
            "_available": None
        },
        "paddle": {
            "loader": get_paddle_engine,
            "name": "PaddleOCR",
            "description": "Deep learning-based OCR by Baidu",
            "languages": "80+ languages",
            "requires_install": True,
            "install_cmd": "pip install paddlepaddle paddleocr",
            "_class": None,
            "_available": None
        },
        "easyocr": {  # ✅ ADDED
            "loader": get_easyocr_engine,
            "name": "EasyOCR",
            "description": "Deep learning based OCR (80+ languages)",
            "languages": "80+ languages",
            "requires_install": True,
            "install_cmd": "pip install easyocr",
            "_class": None,
            "_available": None
        }
    }
    
    # Cache for engine instances
    _engine_instances: Dict[str, Any] = {}
    
    @classmethod
    def _get_engine_class(cls, engine_name: str):
        if engine_name not in cls._ENGINE_REGISTRY:
            return None
        
        engine_info = cls._ENGINE_REGISTRY[engine_name]
        
        if engine_info["_class"] is not None:
            return engine_info["_class"]
        
        try:
            engine_class = engine_info["loader"]()
            engine_info["_class"] = engine_class
            engine_info["_available"] = engine_class is not None
            return engine_class
        except Exception as e:
            print(f"❌ Error loading {engine_name}: {str(e)}")
            engine_info["_available"] = False
            return None
    
    @classmethod
    def get_engine(cls, engine_name: str = "tesseract", **kwargs):
        engine_name = engine_name.lower()
        
        if engine_name not in cls._ENGINE_REGISTRY:
            available_engines = ', '.join(cls._ENGINE_REGISTRY.keys())
            raise ValueError(
                f"OCR Engine '{engine_name}' is not supported. "
                f"Available engines: {available_engines}"
            )
        
        engine_info = cls._ENGINE_REGISTRY[engine_name]
        engine_class = cls._get_engine_class(engine_name)
        
        if engine_class is None:
            install_cmd = engine_info.get("install_cmd", "pip install <engine>")
            raise ImportError(
                f"OCR Engine '{engine_name}' is not installed.\n"
                f"Please install it using: {install_cmd}"
            )
        
        cache_key = f"{engine_name}_{str(sorted(kwargs.items()))}"
        
        if cache_key in cls._engine_instances:
            return cls._engine_instances[cache_key]
        
        try:
            instance = engine_class(**kwargs)
            cls._engine_instances[cache_key] = instance
            print(f"✅ Created {engine_info['name']} instance successfully")
            return instance
        except Exception as e:
            raise RuntimeError(
                f"Failed to create {engine_info['name']} instance: {str(e)}"
            )
    
    @classmethod
    def is_engine_available(cls, engine_name: str) -> bool:
        engine_name = engine_name.lower()
        if engine_name not in cls._ENGINE_REGISTRY:
            return False
        
        engine_info = cls._ENGINE_REGISTRY[engine_name]
        
        if engine_info["_available"] is not None:
            return engine_info["_available"]
        
        engine_class = cls._get_engine_class(engine_name)
        return engine_class is not None
    
    @classmethod
    def get_available_engines(cls) -> List[str]:
        available = []
        for name in cls._ENGINE_REGISTRY:
            if cls.is_engine_available(name):
                available.append(name)
        return available
    
    @classmethod
    def get_all_engines(cls) -> List[str]:
        return list(cls._ENGINE_REGISTRY.keys())
    
    @classmethod
    def get_engine_info(cls, engine_name: str) -> Dict[str, Any]:
        engine_name = engine_name.lower()
        if engine_name not in cls._ENGINE_REGISTRY:
            return {
                "name": engine_name,
                "description": "Unknown engine",
                "available": False
            }
        
        info = cls._ENGINE_REGISTRY[engine_name].copy()
        info.pop("loader", None)
        info.pop("_class", None)
        info.pop("_available", None)
        info["available"] = cls.is_engine_available(engine_name)
        return info
    
    @classmethod
    def clear_cache(cls):
        cls._engine_instances.clear()
        print("🧹 Engine cache cleared")