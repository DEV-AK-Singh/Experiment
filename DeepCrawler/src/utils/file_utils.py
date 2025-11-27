# src/utils/file_utils.py
import json
import os
from typing import Dict, Any, List
from config import Config

class FileUtils:
    """Handles file operations for the crawler"""
    
    @staticmethod
    def save_report(report: Dict[str, Any], domain: str) -> str:
        """Save crawl report to file"""
        filename = Config.get_report_filename(domain)
        filepath = os.path.join(Config.REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    @staticmethod
    def save_export(data: Dict[str, Any], domain: str) -> str:
        """Save data export to file"""
        filename = Config.get_export_filename(domain)
        filepath = os.path.join(Config.EXPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    @staticmethod
    def load_report(filename: str) -> Dict[str, Any]:
        """Load crawl report from file"""
        filepath = os.path.join(Config.REPORTS_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def get_available_reports() -> List[str]:
        """Get list of available report files"""
        return [f for f in os.listdir(Config.REPORTS_DIR) if f.endswith('.json')]
    
    @staticmethod
    def cleanup_old_reports(max_age_days: int = 7):
        """Clean up reports older than specified days"""
        # Implementation for cleaning old files
        pass