import re
from collections import Counter

class SemanticCorrector:
    def __init__(self, language="ASL"):
        self.language = language
        # Default small dictionaries for demonstration. 
        # In production, these should be loaded from larger corpus files.
        self.dictionaries = {
            "ASL": {"HELLO", "WORLD", "LOVE", "PEACE", "PLEASE", "THANK", "YOU", "GOOD", "MORNING", "NAME", "IS", "WHAT"},
            "ISL": {"NAMASTE", "INDIA", "FOOD", "WATER", "HOME", "SCHOOL", "FRIEND", "FAMILY", "EAT", "SLEEP"},
            "TSL": {"VANAKKAM", "NANDRI", "TAMIL", "AMMA", "APPA", "PALLI", "VEEDU", "UNAVU"}
        }
        self.vocab = self.dictionaries.get(language, set())
        
    def load_vocab(self, vocab_list):
        """Update vocabulary with a custom list of words"""
        self.vocab = set(word.upper() for word in vocab_list)
        
    def correct_word(self, word):
        """
        Find the closest word in the vocabulary using Levenshtein distance.
        If word is in vocab, return it.
        If word is not in vocab, return the closest match if distance is small.
        """
        word = word.upper()
        if not word or word in self.vocab:
            return word
            
        # Find closest match
        best_match = None
        min_dist = float('inf')
        
        for candidate in self.vocab:
            dist = self._levenshtein(word, candidate)
            if dist < min_dist:
                min_dist = dist
                best_match = candidate
                
        # Only correct if the distance is reasonable relative to word length
        # e.g., max 2 edits for a 5-letter word
        threshold = max(1, len(word) // 2)
        if min_dist <= threshold:
            return best_match
        
        return word
    
    def correct_sentence(self, sentence):
        """Correct an entire sentence word by word"""
        if not sentence:
            return ""
            
        words = sentence.split()
        corrected_words = [self.correct_word(w) for w in words]
        return " ".join(corrected_words)
        
    def _levenshtein(self, s1, s2):
        """Calculates Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

if __name__ == "__main__":
    # Test
    corrector = SemanticCorrector("ASL")
    print(corrector.correct_word("HELO"))      # -> HELLO
    print(corrector.correct_word("WRLD"))      # -> WORLD
    print(corrector.correct_sentence("HELO WRLD")) # -> HELLO WORLD
