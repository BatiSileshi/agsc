from api.spell_dict import dictionary
from difflib import get_close_matches
import re

def spell_checker_before(text):
    dict = dictionary

    punctuation_pattern = r'[^\w\s\']'
    clean_text = re.sub(punctuation_pattern, ' ', text)
    
    words = clean_text.split()
    messages = []

    corrected_words = []
    for word in words:
        if word.lower() not in dict:
            message = f"Word '{word}' is incorrect. Possible corrections:"
            
            #find similar words
            similar_words = get_close_matches(word.lower(), dict, n=3, cutoff=0.8)
            suggestions = similar_words if similar_words else [word]
            message += ", ".join(suggestions)
            messages.append(message)
            
            corrected_words.append(suggestions[0])  # Replace with the appropriate logic for correction
        else:
            message = f"Word '{word}' is correct."
            messages.append(message)
            corrected_words.append(word)

    corrected_text = ' '.join(corrected_words)
    return corrected_text