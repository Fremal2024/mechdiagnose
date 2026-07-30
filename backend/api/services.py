import re
from difflib import SequenceMatcher
from .models import Fault, SymptomKeyword

class FaultMatcher:
    def __init__(self, symptoms, machine_type=None):
        self.symptoms = symptoms.lower()
        self.machine_type = machine_type
        self.symptom_words = self._extract_words(symptoms)
    
    def _extract_words(self, text):
        """Extract individual words from text, removing punctuation"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def _similar(self, word1, word2):
        """Check if two words are similar"""
        if len(word1) < 3 or len(word2) < 3:
            return False
        if word1 in word2 or word2 in word1:
            return True
        if SequenceMatcher(None, word1, word2).ratio() > 0.7:
            return True
        return False
    
    def match(self):
        faults = Fault.objects.all()
        if self.machine_type:
            faults = faults.filter(machine_type__name__iexact=self.machine_type)
        
        results = []
        
        for fault in faults:
            # Get all keywords for this fault
            keywords = SymptomKeyword.objects.filter(fault=fault)
            keyword_texts = [kw.keyword.lower() for kw in keywords]
            
            if not keyword_texts:
                continue
            
            matched_keywords = []
            
            # Check each keyword against the user's symptoms
            for keyword in keyword_texts:
                # 🔍 NEW: Check if the keyword is in the raw symptoms (not just individual words)
                if keyword in self.symptoms:
                    matched_keywords.append(keyword)
                    continue
                
                # Check if keyword matches any individual word
                for word in self.symptom_words:
                    if self._similar(keyword, word):
                        matched_keywords.append(keyword)
                        break
            
            # Calculate confidence
            if keyword_texts:
                confidence = len(matched_keywords) / len(keyword_texts)
            else:
                confidence = 0
            
            if confidence > 0:
                results.append({
                    'fault': fault,
                    'confidence': confidence,
                    'matches': matched_keywords
                })
        
        # Sort by confidence (highest first)
        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results