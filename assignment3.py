from collections import defaultdict
from pathlib import Path
import autograder
import unittest
import numpy as np
import copy


class NullDict(defaultdict):
    # Class that initialises a default empty dictionary to which we can add the counts of each word without throwing an IndexError
    # In this case, we pass the arguments of the built-in dict unchanged via our Class
    def __init__(self, *args, **kwargs):
        super(NullDict, self).__init__(*args, **kwargs)
        self.default_factory = lambda:0


'''
In this assignment, you will implement a word n-gram.
This is a earlier natural language processing (NLP) model that "learns" and "predicts" words from a corpus.
Corpus is just a fancy word for a (set of) file(s) that contain text which is used to train language models.
For the full explanation see the assignment.
'''
def main():
    corpus = parse_text_file("text.txt")
    bigram = make_ngram_model(corpus, 'bigram')
    trigram = make_ngram_model(corpus, "trigram")
    bigram_sentences = predict_sentence(bigram, "bigram", n_sentences = 10, max_sentence_len=15)
    trigram_sentences = predict_sentence(trigram, "trigram", n_sentences= 10, max_sentence_len=15)
    print("amount of bigram sentences generated: ", len(bigram_sentences))
    print("amount of trigram sentences generated: ", len(trigram_sentences))
        #example_trigrams = make_ngram_model(corpus, 'trigram')
    # for key,value in example_bigrams.items():
    #     for i,j in value.items():
    #         print(key, i, j)

    #print("trigram: ", example_trigrams)




def parse_text_file(file):
    """
    This function should parse a text file and return a list of sentences,
    where a sentence consists of list of words and should start
    with a special word "\<s>" and end with "</s>".
    """
    txt_file = open(file,"r")
    text = txt_file.read()
    sentence_list = []
    word = []
    sentence = ["<s>"]
    for char in text:
        if char != " ":
            word.append(char)
        elif char == " ":
            word = ''.join(word)
            sentence.append(word)
            word = []
        if char == '\n':
            sentence.append("</s>")
            if len(sentence) > 2:
                sentence_list.append(sentence)
            word = []
            sentence = ["<s>"]
    return sentence_list



def create_defaultdict(type):
    """
    This is an optional function that returns a function that returns a defaultdict with as default type.

    EXPLANTION (see grading):
    default_dict is a type of dictionary from the collections module. It does not raise a KeyError, because it initialises the dictionary with a default value (via the parameter default_factory)
    which is returned if/when the user tries to access a key which is not present. As such, we can pass a default_factory argument into the default_dict function to ensure that our dictionary 
    never returns a KeyError.

    Since default_factory is a callable function, we cannot simply pass an object to defaultdict() as an argument for its default value, we would need to pass in a function which returns our desired
    default value.  A lambda function is a way of avoiding the creation of an explicit, named function when we only need it as an argument to be passed into another function. 
    In our case here: default_factory is a parameter for the default_dict() function, but since this is its only use in the program, there's no point making a named function of it. As such, we use lambda: 0, to pass
    in the default value of the dictionary (0) implicitly. 
    """
    def return_defaultdict():
        defaultdict(lambda: 0)

    return return_defaultdict




''' NOTE ON THE FOLLOWING FUNCTIONS: From what I understood about the assignment, the task was to set the history, then based on that
history, traverse the corpus and calculate the probability of a word following our history, and append that to a dictionary of probabilities

I realised that pretty late when coding the assignment, at which point I was already pretty committed to this solution:
- Traverse the whole corpus only once
- While doing this, count the occurence of any given ngram up to the desired one:
    For example: 
        - If we are training a trigram, then we count the unigrams, bigrams and trigrams (all at the same time via make_ngrams) in the whole corpus
        - Then, use this dictionary of counts to compute the probability of any given ngram and store them in a dictionary
        - Then build the sentences at the very end using this one dictionary of probabilities; not interacting with a corpus again
- The reason I stuck with this version after realising that most likely this was not the way the solution was envisioned when writing the instructions
  (besides the sunk-cost fallacy lol) is that I believed this model would be faster given we only have to loop through the entirety of the corpus once. 
  This might be counteracted, however,by the fact that we need to store every combination of ngrams (up to the desired amount) in the original counts dictionary -- which might be slower?
- I hope this solution is still acceptable, however, given that it has the required functionality, and is pretty "dry".

'''


def check_for_digit(text):
    for char in text: 
        if char.isdigit() == True:
            return char
    return False


def index_positions(name):
    counts = {"unigram": 1, "bigram": 2, "trigram": 3, "quadgram": 4}
    if name in counts.keys():
        no_of_grams = counts[name]
    else:
        no_of_grams = check_for_digit(name)
        type_input = str(type(no_of_grams))
        match type_input:
            case "<class 'bool'>":
                print("Your desired n-gram type was not recognised. Please specify unigram, bigram, trigram or quadgram")
            case "<class 'str'>":
                if no_of_grams.isalnum():
                    print('''Training higher order n-grams can result in too few counts per n-gram. 
                      As such, please specify one of the following: unigram, bigram, trigram or quadgram''')
    return no_of_grams, counts

    
def initialise_dicts(name):
    no_of_grams, counts = index_positions(name)
    inverted_counts = {value:key for key, value in counts.items()}
    for i in range(1, no_of_grams+1):
        key = inverted_counts[i]
        counts[key] = NullDict()
    return counts, no_of_grams, inverted_counts


def make_ngrams(no_of_grams, sentence, index_position, inverted_counts, counts):
    for num in range(no_of_grams):
        positions_to_follow = num + 1
        ngram = []
        for i in range(positions_to_follow):
            if index_position + i < len(sentence):
                ngram.append(sentence[index_position + i])
        if len(ngram) == positions_to_follow:
            ngram = ', '.join(ngram)
            model_name = inverted_counts[num+1]
            counts[model_name][ngram] += 1



def make_counts(name, sentences):
    total_words = 0
    counts, no_of_grams, inverted_counts = initialise_dicts(name)
    for sentence in sentences:
        index_position = 0 
        while index_position < len(sentence):
            make_ngrams(no_of_grams, sentence, index_position, inverted_counts, counts)
            total_words += 1
            index_position += 1
    return counts, total_words



def make_ngram_model(sentences, name):
    """
    To make a ngram model we need to translate all the sentences into
    a prediction model that tells us the chance for a random word.

    Each model will be stored in a dictionary that looks as follows.
    The keys of this dictionary is the history which are the previous word(s) in the sentence.
    The values are a dictionary on their own with as keys all the possible words and
    as values the probability of that word following the history (previous words).

    For more details, see the exercise description.

    Tip 1: Before making the dictionary with all probabilities, make a similar dictionary with the counts.
    Tip 2: To make the code cleaner, you can use a `defaultdict` instead of a `dict`.
           This adds the benefit that if a key does not exist the value will be a default value
           and not throw the error KeyError. To make a defaultdict of defaultdict with int values.
           You can use defaultdict(create_defaultdict(int)), where create_defaultdict is a function that
           returns a defaultdict, This defaultdict has as default the input of the function `create_defaultdict`.
    Tip 3: If you want to loop over the keys of a dict you can type `for key in dict:`,
           If you want to loop over the values add .values() thus `for value in dict.values:`
           and for both you can use `for key, value in dict.items():`
    """
    # Make a dictionary with counts of the words, bigrams, trigrams, and/or quadgrams respectively (the last three if applicable based on the specified model). 
    # Count the total words in the corpus at the same time
    counts, total_words = make_counts("bigram", sentences)
    ngrams = copy.deepcopy(counts)
    for word, count in ngrams[""]




    # For a unigram, the probability of a word, is just the probability of that word showing up in the text in general. 
    # Thus, divide the count of a specific word by the total words in the corpus
    match name:
        case "unigram":
            unigrams = NullDict()
            for word, count in word_counts.items():
                unigrams[word] = count/total_words
            ngram = unigrams


    # The probability of a bigram is the same as dividing the count of the whole bigram by the count of the first
        case "bigram":
            bigrams = NullDict()
            for bigram, count in bigram_counts.items():
                bigram_key = bigram[0]
                bigram_term = bigram[1]
                if bigrams[bigram_key] == 0:
                    bigrams[bigram_key] = NullDict()
                # if bigram_key == "<s>":
                    # print("numerator: ", count, "denominator: ",word_counts[bigram_key] )
                bigrams[bigram_key][bigram_term] = count/word_counts[bigram_key]
            bigrams_start_terms = 0 
            for i in bigrams["<s>"].keys():
                bigrams_start_terms += 1
            # print(bigrams_start_terms)
            ngram = bigrams



    # The probability of a trigram is the same as dividing the count of the whole trigram by the count of the first two words (the count of that bigram)
        case 'trigram':
            start_terms = {}
            trigrams = NullDict()
            for trigram, count in trigram_counts.items():
                trigram_key = (trigram[0], trigram[1])
                trigram_term = trigram[2]
                if trigram_key[0] == "<s>":
                #     print("numerator: ",bigram_counts[trigram_key], "denominator: ", word_counts["<s>"])
                    start_terms[trigram_key[1]] = bigram_counts[trigram_key]/(word_counts['<s>'])
                if trigrams[trigram_key] == 0:
                    trigrams[trigram_key] = NullDict()
                trigrams[trigram_key][trigram_term] = count/bigram_counts[trigram_key]
            trigrams_start_terms = 0
            for i in trigrams.keys():
                if i[0] == "<s>":
                    trigrams_start_terms += 1
            # print("trigrams start terms :", trigrams_start_terms)
            trigrams[("<s>","<s>")] = start_terms
            ngram = trigrams
    return ngram





def set_history(history, new_word, name):
    """
    This function should return a new history depending on the model that is used and the new_word.
    name could be three values: unigram, bigram or trigram.
    This function should be the only place where the three models have different code.
    See grading scheme *dry code*.

    If history is None, initialize the history correctly depending on the model.

    This function is optional to use. However, highly recommended to keep your code dry.
    """
    if name != "unigram":
        history.pop(0)
        history.append(new_word)
    else:
        history = [] 
    return history


# Can use this function either once at the very beginning for a unigram, or at every iteration for higher-order
# n-grams
def set_probabilities(model, history, name):
    word_probability = {}
    global list1, list2, empty_words
    match name:
        case "unigram":
            word_probability = model
        case "bigram":
            word_probability = model[history[-1]]
        case "trigram":
            term = tuple(history)
            # print(term)
            word_probability = model[term]
            # print(model)
    choice_of_words = []
    probabilities = []
    for word, probability in word_probability.items():
        choice_of_words.append(str(word))
        probabilities.append(probability)
    return choice_of_words, probabilities
        

def initialise_history(name):
    match name:
        case "unigram":
            history = []
        case "bigram":
            history = ["<s>"]
        case "trigram":
            history = ["<s>", "<s>"]
    return history


def predict_sentence(model, name, n_sentences, max_sentence_len):
    """
    Here, you will implement a sentence predictor.

    To generate a sentence using a n-gram model, follow these guidelines:

    1. Initialize the history by appending an appropriate number of start tokens `"<s>"`,
       see the model descriptions above. For the unigram model,
       you do not add the start token `"<s>"`. The history always begins with `"<any>"`.
    2. Now, you can use the history in the model-dictionary to get the word-dictionary.
       The keys of this word-dictionary are the possible next words and their values are
       the probability of that word. Hint: Just using `np.random.choice(word-dictionary.keys())`
       will not work as now each word has the same chance to get chosen.
    3. When, you have your next word, update the history and go back to step 2, unless step 4 applies.
    4. The sentence prediction process will halt when it encounters the `"</s>"` token or
       reaches the maximum sentence length (given by `max_sentence_len`).
    5. Each generated sentence should conclude with a period ".".
    6. Once you have generated the desired number of sentences (given by `n_sentences`),
       save them to a text file named `"generated_{name}_sentences.txt"`, here name is the name of the model.
       Each sentence should occupy its own line in the text file.

    Tip: use np.random.choice
    """
    sentences = []
    # Initialise the history based on the model 
    history = initialise_history(name)
    max_sentence_len = max_sentence_len + len(history)
    # Start the loop so it continues until all the desired sentences are created
    for i in range(n_sentences):
        print("number of sentences: ", i)
        sentence = []
        sentence.extend(history)
        print("sentence at the start: ", sentence)
        print("sentence after appending history: ", sentence)
        while sentence[-1] != "</s>" and len(sentence) < max_sentence_len:
            choice_of_words, probabilities = set_probabilities(model, history, name)
            pick_word = np.random.choice(choice_of_words, 1, p=probabilities)
            print(pick_word)
            next_word = str(pick_word[0])
            print("next word: ", next_word)
            sentence.append(next_word)
            print("sentence after appending new word: ", sentence)
            history = set_history(history, next_word, name)
            print("history: ", history)
        if "</s>" not in sentence:
            sentence.append("</s>")
        sentences.append(sentence)
        # Initialise new history for each new sentence
        history = initialise_history(name)
        print("all the sentences after appending the first done sentence: ", sentences)
    print("all the sentences at the conclusion of the function: ", sentences)
    return sentences
    
     

if __name__ == '__main__':
    main()





            


    
     

# TODO finish the script here,
#  if you want you can also use a main function and the if __name__ == "__main__": control flow.


# raise NotImplementedError("Complete the code for the script")




'''

"""
DO NOT CHANGE THE CODE BELOW!
THESE TEST ARE VERY BASIC TEST TO GIVE AN IDEA IF YOU ARE ON THE RIGHT TRACK!
"""

class TestUnigram(unittest.TestCase):
    pass

path = Path.cwd()
path = path.glob('**/test.txt').__next__()

parse_text_file_tests = [
    (path, [['<s>', 'This', 'is', 'a', 'test', 'sentence', '</s>']])
]

make_model_tests = [
    (([['<s>', 'This', 'is', 'a', 'sentence', '</s>']], "unigram"),
     {'<any>': {'This': 0.2,
                'a': 0.2,
                'is': 0.2,
                'sentence': 0.2,
                '</s>': 0.2}}),
]

autograder.create_tests(TestUnigram, parse_text_file, parse_text_file_tests)
autograder.create_tests(TestUnigram, make_ngram_model, make_model_tests)

"""
Here the test suite are made, each suite has its own class
"""
suite = unittest.TestLoader().loadTestsFromTestCase(TestUnigram)
unittest.TextTestRunner(verbosity=2).run(suite)

'''