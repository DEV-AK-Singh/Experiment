import re
from collections import Counter
from typing import Dict, List, Any

class TextAnalyzer:
    @staticmethod
    def count_words(text: str) -> int:
        """Count total words in text"""
        words = text.split()
        return len(words)
    
    @staticmethod
    def count_characters(text: str) -> Dict[str, int]:
        """Count characters (with and without spaces)"""
        return {
            "with_spaces": len(text),
            "without_spaces": len(text.replace(" ", "")),
            "letters_only": len(re.findall(r'[a-zA-Z]', text)),
            "digits": len(re.findall(r'\d', text)),
            "punctuation": len(re.findall(r'[^\w\s]', text))
        }
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences (improved approach)"""
        # Count . ! ? as sentence endings, but avoid abbreviations
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        # Filter out empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    @staticmethod
    def find_most_common_words(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find most common words (excluding stop words)"""
        # Simple stop words list
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        
        # Filter out stop words
        filtered_words = [word for word in words if word not in stop_words]
        
        if not filtered_words:
            # If all words are stop words, use original words
            filtered_words = words
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get top N words
        common_words = []
        for word, count in word_counts.most_common(top_n):
            common_words.append({
                "word": word,
                "count": count,
                "percentage": round((count / len(words)) * 100, 2)
            })
        
        return common_words
    
    @staticmethod
    def calculate_readability(text: str) -> Dict[str, float]:
        """Enhanced readability scores"""
        words = text.split()
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) == 0 or len(words) == 0:
            return {
                "average_sentence_length": 0, 
                "average_word_length": 0,
                "reading_time_minutes": 0
            }
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Average word length (characters per word)
        total_chars = sum(len(word) for word in words)
        avg_word_length = total_chars / len(words)
        
        # Estimate reading time (200 words per minute)
        reading_time = len(words) / 200
        
        return {
            "average_sentence_length": round(avg_sentence_length, 2),
            "average_word_length": round(avg_word_length, 2),
            "words_per_sentence": round(avg_sentence_length, 2),
            "reading_time_minutes": round(reading_time, 1)
        }
    
    @staticmethod
    def find_longest_words(text: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Find longest words in text"""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        if not words:
            return []
        
        # Get unique words and their lengths
        unique_words = set(words)
        word_lengths = [{"word": word, "length": len(word)} for word in unique_words]
        
        # Sort by length (descending) and get top N
        word_lengths.sort(key=lambda x: x["length"], reverse=True)
        
        return word_lengths[:top_n]
    
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """Comprehensive text analysis"""
        analysis = {
            "word_count": TextAnalyzer.count_words(text),
            "character_counts": TextAnalyzer.count_characters(text),
            "sentence_count": TextAnalyzer.count_sentences(text),
            "common_words": TextAnalyzer.find_most_common_words(text),
            "readability": TextAnalyzer.calculate_readability(text),
            "paragraph_count": text.count('\n\n') + 1,
            "longest_words": TextAnalyzer.find_longest_words(text),
            "unique_words": len(set(re.findall(r'\b[a-zA-Z]+\b', text.lower())))
        }
        
        return analysis