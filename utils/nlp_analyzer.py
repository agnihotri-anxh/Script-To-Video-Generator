import spacy
import subprocess
from config import Config

class NLPAnalyzer:
    """Natural Language Processing analyzer for script analysis"""
    
    def __init__(self):
        self.nlp = self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model, download if not available"""
        try:
            return spacy.load(Config.SPACY_MODEL)
        except OSError:
            print(f"Downloading spaCy model: {Config.SPACY_MODEL}")
            subprocess.run(["python", "-m", "spacy", "download", Config.SPACY_MODEL])
            return spacy.load(Config.SPACY_MODEL)
    
    def analyze_script(self, script):
        """Analyze script and extract keywords from each sentence"""
        doc = self.nlp(script)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        
        analysis = []
        for sentence in sentences:
            sent_doc = self.nlp(sentence)
            
            # Extract nouns, verbs, and adjectives as keywords
            keywords = []
            for token in sent_doc:
                if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and not token.is_stop:
                    keywords.append(token.lemma_.lower())
            
            # Also extract noun phrases
            noun_phrases = [chunk.text.lower() for chunk in sent_doc.noun_chunks]
            
            # Combine and deduplicate
            all_keywords = list(set(keywords + noun_phrases))
            
            analysis.append({
                'sentence': sentence,
                'keywords': all_keywords[:Config.MAX_KEYWORDS_PER_SENTENCE]
            })
        
        return analysis
    
    def extract_keywords(self, text):
        """Extract keywords from a single text"""
        doc = self.nlp(text)
        keywords = []
        
        for token in doc:
            if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and not token.is_stop:
                keywords.append(token.lemma_.lower())
        
        return list(set(keywords)) 