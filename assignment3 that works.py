from collections import defaultdict
from pathlib import Path
import autograder
import unittest
import numpy as np
import tkinter as tk
from tkinter import simpledialog
import sys
from tkinter import ttk



'''
TO DO: 
- User interface (Tkinter?)

'''





class NullDict(defaultdict):
	# Class that initialises a default empty dictionary to which we can add the counts of each word without throwing an IndexError
	# In this case, we pass the arguments of the built-in dict unchanged via our Class
	def __init__(self, *args, **kwargs):
		super(NullDict, self).__init__(*args, **kwargs)
		self.default_factory = lambda:0

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




def check_for_digit(text):
	for char in text: 
		if char.isdigit() == True:
			return char
	return False


def index_positions(name):
	counts = NullDict()
	counts["unigram"] = 1
	counts["bigram"] = 2
	counts["trigram"] = 3
	counts["quadgram"] = 4
	no_of_grams = counts[name]
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
			# ngram = ', '.join(ngram)
			ngram = tuple(ngram)
			model_name = inverted_counts[num+1]
			counts[model_name][ngram] += 1
		# print(counts)
	# To abstract the calculation of probabilities when creating the n-gram probability dictionary 
	try: 
		previous_model = inverted_counts[no_of_grams-1]
	except:
		previous_model = False
	return previous_model



def make_counts(name, sentences):
	total_words = 0
	counts, no_of_grams, inverted_counts = initialise_dicts(name)
	for sentence in sentences:
		index_position = 0 
		while index_position < len(sentence):
			previous_model = make_ngrams(no_of_grams, sentence, index_position, inverted_counts, counts)
			total_words += 1
			index_position += 1
	return counts, total_words, previous_model, no_of_grams




def fetch_start_term(counts, total_words):
	start_term_unigram = NullDict()
	for key, count in counts["bigram"].items():
		first_word = key[0]
		denom = counts["unigram"][("<s>",)]
		if first_word == "<s>":
			start_term_unigram[key[1]] = count/denom
	return start_term_unigram    




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
	counts, total_words, previous_model, no_of_grams = make_counts(name, sentences)
	ngrams = NullDict()
	if no_of_grams > 2:
		start_terms = fetch_start_term(counts, total_words)
		ngrams["<s>"] = start_terms
	for ngram, count in counts[name].items():
		key = []
		for i in range(no_of_grams-1):
			key.append(ngram[i])
		key = tuple(key)
		term = ngram[-1]
		if ngrams[key] == 0:
			ngrams[key] = NullDict()
	# Here, ngram is the whole ngram, and count = P(whole ngram | first n-1 words in the ngram), while denom = P(first n-1 words in the ngram), and we use these
	# later to calculate the conditional probability of the ngram
		denom = counts[previous_model][key] if previous_model != False else total_words
		ngrams[key][term] = count/denom
	return ngrams






def set_history(history, new_word, name):
	"""
	This function should return a new history depending on the model that is used and the new_word.
	name could be three values: unigram, bigram or trigram.
	This function should be the only place where the three models have different code.
	See grading scheme *dry code*.

	If history is None, initialize the history correctly depending on the model.

	This function is optional to use. However, highly recommended to keep your code dry.
	"""
	if name == "unigram":
		history = [] 
	elif len(history) == 0 or "</s>" in history:
		history = ["<s>"]
	else:
		history.pop(0)
		history.append(new_word)
	return history


def set_probabilities(model, history):
	if len(history) > 0:
		history = tuple(history)
		choice_of_words = [word for word in model[history].keys()]
		probabilities = [word for word in model[history].values()]
	else:
		choice_of_words = [word for word in model.keys()]
		probabilities = [word for word in model.values()]
	return choice_of_words, probabilities



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
	produced_sentences = []
	history = []
	# Initialise the history  
	max_sentence_len = max_sentence_len + len(history) + 1
	# Start the loop so it continues until all the desired sentences are created
	for i in range(n_sentences):
		history = set_history(history, None, name)
		print("number of sentences: ", i)
		sentence = []
		print("sentence at the start: ", sentence)
		sentence.extend(history)
		print("sentence after appending history: ", sentence)
		# Keep going until we have either appended the ending character or reached the desired sentence length
		condition_dictionary = True if sentence[-1] != "</s>" else False
		condition_length = True if len(sentence) < max_sentence_len else False
		while condition_dictionary and condition_length:
		# while sentence[-1] != "</s>" and len(sentence) < max_sentence_len:
			choice_of_words, probabilities = set_probabilities(model, history)
			pick_word = np.random.choice(choice_of_words, 1, p=probabilities)
			next_word = str(pick_word[0])
			print("next word: ", next_word)
			sentence.append(next_word)
			print("sentence after appending new word: ", sentence)
			history = set_history(history, next_word, name)
			print("history: ", history)
			condition_dictionary = True if sentence[-1] != "</s>" else False
			condition_length = True if len(sentence) < max_sentence_len else False

		if "</s>" not in sentence:
			sentence.append("</s>")
		print("condition length: ", condition_length, "condition dictionary: ", condition_dictionary)
		produced_sentences.append(sentence)
		print(produced_sentences)
		# Initialise new history for each new sentence
		history = []
	print("all the sentences at the conclusion of the function: ", produced_sentences)
	return produced_sentences


def main(model_name, corpus_filename, n_sentences, max_sentence_len):
	# TO-DO: CHANGE "TEXT.TXT" TO CORPUS_FILENAME IF IMPLEMENTING READING IN OTHER FILES!!    
	corpus = parse_text_file("text.txt")
	ngrams = make_ngram_model(corpus, model_name)
	predict_sentence(ngrams, model_name, n_sentences, max_sentence_len)



def check_filename(filename):
	forbidden_chars = ["/", "\\", "?", "%", "*", ":", "|", "<", ">", ".", ",", ";", "="]
	type_filename = str(type(filename))
	match type_filename:
		case "<class 'str'>":
			for i in forbidden_chars:
				if i in filename:
					return False
				else:
					return True
		case "<class 'NoneType'>":
			return False


def check_numerical_inputs(input, field):
	numeric = input.isdigit()
	match numeric:
		case True:
			number = int(numeric)
		case False:
			error_message = "Your requested number of " + field + "is not recognised or unsupported. Please specify a number from 1 and up"
			input_nondigit = tk.Label(instructions_frame, text = error_message, fg = 'red')
			input_nondigit.pack()
	return numeric
	


	
def collect_inputs_from_gui():
	go_ahead = False
	# If the user closes the window without inputting anything, end the program
	try:
		print("tried")
		model_name = model_entry.get()
		max_sentence_len = number_of_words.get()
		n_sentences = number_of_sentences.get()
		filename = filename_entry.get()
		print("tried")
	except:
		print("exception occurred")
		sys.exit()
	go_ahead = check_filename(filename) and check_numerical_inputs(n_sentences, "sentences") and check_numerical_inputs(max_sentence_len, "words")
	print(go_ahead)
	if go_ahead == True:
		main(model_name, "text.txt", n_sentences, max_sentence_len)

	



# Start the graphical interface
window = tk.Tk()
window.title("Train an NLP model")

# Make an inner frame to keep the interface tidy
frame = tk.Frame(window, padx = 20, pady = 20)
# Any time we add graphics to the user interface, .pack() method is needed to make them appear
frame.pack()

# Splitting the gui into smaller frames per input
instructions_frame = tk.LabelFrame(frame, text = "How this works")
instructions_frame.grid(row=0, column=0, padx = 20, pady=20)
instructions_label = tk.Label(instructions_frame, text = '''In this application, you can train a simple natural language processing model using unigrams, bigrams, trigrams or quadgrams. 
							  The reason for not going above a quadgram is that it reduces the effectiveness of the model, resulting in sentences that are mostly duplicates of ones found in the corpus.
							  Using one of these models, the application will then output a number of sentences in a text file.
							  
							  To start, please select which of the four models you wish to train. Then, choose which corpus you would like to train it on. Select your desired length of sentences to produce, 
							  and the maximum number of words you want each sentence to have. Please note: some sentences might end up shorter, but never longer than the maximum sentence length. 
							  Finally, specify the filename for the text file.
							  Once you're ready to begin generating, hit the start button.
							  ''')
instructions_label.pack()

# New frame for model details
model_details_frame = tk.LabelFrame(frame, text = "Model details")
model_details_frame.grid(row = 1, column = 0, padx = 20, pady = 20)
pick_model = tk.Label (model_details_frame, text = "Type of ngram to train")
pick_model.pack()
model_entry = ttk.Combobox(model_details_frame, values = ["unigram","bigram","trigram","quadgram"], state = "readonly")
model_entry.pack()
ask_number_of_words = tk.Label (model_details_frame, text = "Max. number of words per sentence")
ask_number_of_words.pack()
number_of_words = ttk.Spinbox(model_details_frame, from_=1, to=50)
number_of_words.pack()
ask_number_of_sentences = tk.Label (model_details_frame, text = "Number of sentences to be written to the file")
ask_number_of_sentences.pack()
number_of_sentences = ttk.Spinbox(model_details_frame, from_=1, to=50)
number_of_sentences.pack()

# New frame for file details
file_details_frame = tk.LabelFrame(frame, text = "File Details")
file_details_frame.grid(row=2, column=0, padx = 20, pady = 20)
ask_filename = tk.Label(file_details_frame, text = "What should the output file be titled? ")
ask_filename.pack()
filename_entry = tk.Entry(file_details_frame, bg="white")
filename_entry.pack()

# Add padding to all frames to make the window neater
for widget in frame.winfo_children():
	widget.grid_configure(padx=10, pady=5)
	
# Add the Button and pass in arguments to it
button = tk.Button(frame, text = "Start", command = collect_inputs_from_gui)
button.grid(row = 3, column = 0, padx=20, pady=5)
window.mainloop()


			


	
	 

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