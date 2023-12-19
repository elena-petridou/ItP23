import nltk  # This is a major NLP library
import contractions
from nltk.tag import pos_tag
import os



nltk.download('punkt')

from nltk.corpus import abc, brown, gutenberg


# Dictionary of junk terms I encountered throughout making the project
junk_terms = ["ntilde", "changes'exciting'Major", "''"]

def clean_contractions(sentence):
    return contractions.fix(sentence)



def tag_proper_nouns(sentence):
    tagged_sentence = pos_tag(sentence)
    proper_nouns = [i[0] for i in tagged_sentence if i[1] == "NNP"]
    return proper_nouns


def make_lower(sentence, proper_nouns):
    #If a word is not a proper noun, make it lowercase. If it is, keep the first letter capitalised
    lower_sentence = []
    for word in sentence:
        if word in proper_nouns:
            lower_sentence.append(word)
        elif len(lower_sentence) == 0:
            lower_sentence.append(word)
        elif word == "I":
            lower_sentence.append(word)
        else:
            lower_sentence.append(word.lower())
    return lower_sentence




def clean_sentence(sentence):
    cleaned_words = []
    
    for word in sentence:
        cleaned_word = "".join([char for char in word if char.isalnum() or char == "'"])

        if cleaned_word != '' and cleaned_word not in junk_terms:
            cleaned_words.append(cleaned_word)
    
    proper_nouns = tag_proper_nouns(cleaned_words)
    lowered = make_lower(cleaned_words, proper_nouns)
    new_sentence = " ".join(lowered)
    new_sentence = new_sentence.replace(" ' ", "'").strip() + "."
    
    return clean_contractions(new_sentence)


def produce_corpus(user_input):

    match user_input:
        case "abc":
            nltk.download('abc')
            sample_corpus = abc
            corpus_filename = "custom_abc.txt"
        case "brown":
            nltk.download('brown')
            sample_corpus = brown
            corpus_filename = "custom_brown.txt"
        case "gutenberg":
            nltk.download('gutenberg')
            sample_corpus = gutenberg
            corpus_filename = "custom_gutenberg.txt"
    if not os.path.exists(corpus_filename):
        cleaned_sentences = []
        for sentence in sample_corpus.sents():
            cleaned_sentence = clean_sentence(sentence)
            if (len(cleaned_sentence) > 1):
                cleaned_sentences.append(cleaned_sentence)
        with open(corpus_filename, 'w') as f:
            f.write("\n".join(cleaned_sentences))
    return corpus_filename

