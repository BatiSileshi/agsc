from django.shortcuts import render
from api import utils, serializers
import joblib
from api.spell_dict import dictionary
from api.spell import spell_checker_before
import re
import os
from difflib import get_close_matches
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tf_keras.preprocessing.sequence import pad_sequences
from tf_keras.preprocessing.text import Tokenizer

current_dir = os.path.dirname(__file__)

model_file_path = os.path.join(current_dir, 'agsc_model.sav')
model = joblib.load(model_file_path)
# featurizer = CountVectorizer(decode_error='ignore')
# featurizer.fit(data_train)

#? Spell checker only
@api_view(['POST'])
def spell_checker(request):
    serializer = serializers.TextSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    input_text = serializer.validated_data.get('text', '')   
    dict = dictionary
    
    if serializer.is_valid():
        punctuation_pattern = r'[^\w\s\']'
        clean_text = re.sub(punctuation_pattern, ' ', input_text)
        
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
        response_data = {'message:': messages, 
                'corrected_spell': corrected_text}
        return Response(response_data)


#? Grammar checker only
@api_view(['POST'])
def check_grammar(request):
    serializer = serializers.TextSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    sentence = serializer.validated_data.get('text', '')  
    cleaned_sentence = utils.clean_data(str(sentence))
    print(cleaned_sentence)
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(cleaned_sentence)
    max_sequence_length = 100

    sequence = tokenizer.texts_to_sequences([cleaned_sentence])
    padded_sequence = pad_sequences(sequence, maxlen=max_sequence_length, padding="pre")
    
    # Load model and tokenizer
    model = joblib.load(model_file_path)
    # tokenizer = model.tokenizer
    # max_sequence_length = model.max_sequence_length

    # Convert text to numerical sequence
    sequence = tokenizer.texts_to_sequences([cleaned_sentence])
    padded_sequence = pad_sequences(sequence, maxlen=max_sequence_length, padding="pre")

    prediction = model.predict(padded_sequence)

    # Prediction score
    print("Prediction:", prediction)

    # Map the prediction to 'correct' or 'incorrect'
    result = 'correct' if prediction >= 0.5 else 'incorrect'
    highlighted_text = ''

    if result == 'incorrect':
        # Identify positions where errors found
        error_positions = [i for i, word in enumerate(cleaned_sentence.split()) if model.predict(tokenizer.texts_to_sequences([word]))[0] == 0]

        # Print the original text with error positions marked
        highlighted_text = ' '.join(f'[{word}]' if i in error_positions else word for i, word in enumerate(cleaned_sentence.split()))
        g_message = "The text contains errors. Error positions marked in square brackets:"
    else:
        g_message = "The text is correct."

    return Response({'message': g_message, 'highlighted_text': highlighted_text})
        

#? Check spell then grammar
@api_view(['POST'])
def check_spell_grammar(request):
    pass
    serializer = serializers.TextSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    sentence = serializer.validated_data.get('text', '')
    cleaned_sentence = utils.clean_data(str(sentence))
    corrected_spell = spell_checker_before(cleaned_sentence)
    print(corrected_spell)
    
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(cleaned_sentence)
    max_sequence_length = 100

    sequence = tokenizer.texts_to_sequences([cleaned_sentence])
    padded_sequence = pad_sequences(sequence, maxlen=max_sequence_length, padding="pre")
    
    # Load model and tokenizer
    model = joblib.load(model_file_path)
    # tokenizer = model.tokenizer
    # max_sequence_length = model.max_sequence_length

    # Convert text to numerical sequence
    sequence = tokenizer.texts_to_sequences([cleaned_sentence])
    padded_sequence = pad_sequences(sequence, maxlen=max_sequence_length, padding="pre")

    prediction = model.predict(padded_sequence)
    
    result = 'correct' if prediction >= 0.5 else 'incorrect'
    highlighted_text = ''

    if result == 'incorrect':
        # Identify positions where errors found
        error_positions = [i for i, word in enumerate(cleaned_sentence.split()) if model.predict(tokenizer.texts_to_sequences([word]))[0] == 0]

        # Print the original text with error positions marked
        highlighted_text = ' '.join(f'[{word}]' if i in error_positions else word for i, word in enumerate(cleaned_sentence.split()))
        g_message = "The text contains errors. Error positions marked in square brackets:"
    else:
        g_message = "The text is correct."

    return Response({'message': g_message, 'highlighted_text': highlighted_text})

