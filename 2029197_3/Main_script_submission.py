from collections import defaultdict
from pathlib import Path
import numpy as np
import tkinter as tk
from tkinter import simpledialog
import sys
from tkinter import ttk
# Import the custom_parser as a callable function to allow the user to pick which corpus they would prefer to train their model on
from custom_parser import produce_corpus


'''
PLEASE NOTE: 
1) The custom_parser.py file needs nltk.punkt, nltk.abc, nltk.brown to run correctly. If you are getting an NLTK 
	resource error when trying to run the assignment, please use:
		>>>import nltk
		>>>nltk.download()
	via a terminal to download the required resources (from corpora: abc, brown -- my computer also asked for punkt but my friend's did not)
2) In order to make the program shorter to run, the custom_parser.py checks whether a corpus has already been stored with the 
	specified filename on your computer. However, if the program is interrupted during runtime before finishing, the corpus could be 
	stored incorrectly. For this reason, if the corpus (or corpus file) is suspiciously short after a runtime interruption, please delete
	the associated corpus file and try again

	Thank you, I hope it works :) 
'''



class NullDict(defaultdict):
	'''Class that initialises a default empty dictionary to which we can add the counts of each word without throwing an IndexError
	In this case, we pass the arguments of the built-in dict unchanged via our Class'''
	def __init__(self, *args, **kwargs):
		super(NullDict, self).__init__(*args, **kwargs)
		self.default_factory = lambda:0

# This function is not used, in favour of the class NullDict()
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

	'''Reading the text file character by character, and creating words by appending non-space characters; once a space is encountered, append the word to the sentence. 
	Once a newline is encountered, append the sentence to the list of sentences'''
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


def index_positions(name):
	'''
	HELPER FUNCTION FOR initialise_dicts()
    Determines how many nested dictionaries should be initialised for the counts
	'''
	counts = NullDict()
	counts["unigram"] = 1
	counts["bigram"] = 2
	counts["trigram"] = 3
	no_of_grams = counts[name]
	return no_of_grams, counts


def initialise_dicts(name):
	'''
	HELPER FUNCTION for make_counts()
	Initialise "counts" nested dictionary, which contains only the counts of the models required. E.g.: if making unigrams, 
	will not initialise bigrams and trigrams
	'''
	no_of_grams, counts = index_positions(name)
	inverted_counts = {value:key for key, value in counts.items()}
	for i in range(1, no_of_grams+1):
		key = inverted_counts[i]
		counts[key] = NullDict()
	return counts, no_of_grams, inverted_counts


def make_ngrams(no_of_grams, sentence, index_position, inverted_counts, counts):
	'''
	HELPER FUNCTION for make_counts()
	Using this function, we abstract away how many words are in an n-gram, meaning that all n-grams can use the same code to be created
	'''
	for num in range(no_of_grams):
		positions_to_follow = num + 1
		ngram = []
		for i in range(positions_to_follow):
			'''i is the index position of the current word in the sentence, and according to the n-gram we are assembling, 
			we grab the current position and a corresponding number of words following it (if there are enough words left in 
			the sentence to make this possible)'''
			if index_position + i < len(sentence):
				ngram.append(sentence[index_position + i])
		
		if len(ngram) == positions_to_follow:
			ngram = tuple(ngram)
			model_name = inverted_counts[num+1]
			counts[model_name][ngram] += 1
	# To abstract the calculation of probabilities when creating the n-gram probability dictionary, any model greater than a unigram will be assigned a previous_model, unigram has False
	previous_model = False
	try: 
		previous_model = inverted_counts[no_of_grams-1]
	except:
		previous_model = False
	return previous_model



def make_counts(name, sentences):
	'''
	Count the total words in the corpus, as well as the occurence of every:
	- word if unigram
	- bigram and word if bigram
	- trigram and bigram if trigram 
	We use the counts of the previous model in the probability calculation for the current n-gram (see make_ngram_model)
	'''
	total_words = 0
	counts, no_of_grams, inverted_counts = initialise_dicts(name)
	for sentence in sentences:
		index_position = 0 
		while index_position < len(sentence):
			previous_model = make_ngrams(no_of_grams, sentence, index_position, inverted_counts, counts)
			if sentence[index_position]!= "<s>":
				total_words += 1
			index_position += 1
	return counts, total_words, previous_model, no_of_grams


def fetch_start_term(counts):
	'''
	HELPER FUNCTION FOR make_ngram_model()
	While not the most elegant solution, I could not find another way to start my sentences in the trigram model, 
	and I was already many weeks' work into this way of making the models so it seemed too late to turn back.

	This function returns the probabilities of the first word in a sentence as calculated in the unigram model, in order to
	add it to the trigram model.
	'''
	start_term = NullDict()
	for key, count in counts["bigram"].items():
		first_word = key[0]
		denom = counts["unigram"][("<s>",)]
		if first_word == "<s>":
			start_term[key[1]] = count/denom
	return start_term    

def make_ngram_model(sentences, name):
	"""
	I know this is not the suggested way of achieving this, but once I realised that, I was already working on the project for more than a few days, 
	so I stuck with this solution -- the reason for originally attempting it this way was that I was under the impression that only having to loop through
	the corpus once for the counts, and then through the counts once for the probabilities at the beginning VS traversing the corpus anew for every word in the history/sentence
	would be faster. I don't know if my thinking on this is correct.

	This function: 
	- Makes the counts of the current n-gram, and the one before it, and counts the total words in the corpus
	- Appends the start term for the trigram if working on a trigram
	- Calculates the probability of a given ngram by:
		CASE: BIGRAM/TRIGRAM
		- Taking the count of the whole ngram (for ngram, count in counts[name].items:) and setting it as the numerator
		- Taking the count of the first n-1 terms of the ngram (counts[previous_model][current_key]) and setting it as the denominator
		- The resulting fraction (here, float) is stored in the nested null-dictionary ngrams, using the first n-1 terms as the key, and a null dictionary as a value
		- This null_dictionary uses the last term in the ngram as a key, and the probability of the ngram as a value 
		CASE UNIGRAM:
		- Taking the count of the word as the numerator
		- Taking the total words as the denominator
		- Storing the resulting fraction (here, float) in the ngrams null-dictionary, with the word as the key and the probability as the value
	- Returns the n-grams and the n of the n-gram

	"""
	counts, total_words, previous_model, no_of_grams = make_counts(name, sentences)
	ngrams = NullDict()
	if name == "trigram":
		start_terms = fetch_start_term(counts)
		ngrams[("<s>",)] = start_terms
	for ngram, count in counts[name].items():
		key = []
		for i in range(no_of_grams-1):
			key.append(ngram[i])
		if no_of_grams == 1: 
			key = ngram
		current_key = tuple(key)
		term = ngram[-1]
		if ngrams[current_key] == 0:
			if no_of_grams > 1:
				ngrams[current_key] = NullDict()
	# Here, ngram is the whole ngram, and count = P(whole ngram | first n-1 words in the ngram), while denom = P(first n-1 words in the ngram), and we use these
	# to calculate the conditional probability of the ngram
		denom = counts[previous_model][current_key] if previous_model != False else total_words
		if type(ngrams[current_key]) != int:
			ngrams[current_key][term] = count/denom
		else:
			ngrams[current_key] = count/denom
	return ngrams, no_of_grams


def set_history(history, new_word, name, no_of_grams):
	"""
	HELPER FUNCTION FOR predict_sentence()
	When generating sentences, we want to keep the history of the last n terms depending on the ngram we are using. When using a unigram, we 
	do not wish to store a history, since any word could follow any word.
	"""
	if name == "unigram":
		history = [] 
	elif len(history) == 0 or "</s>" in history:
		history = ["<s>"]
	elif len(history) >= no_of_grams-1:
		history.pop(0)
		history.append(new_word)
	else:
		history.append(new_word)
	return history


def set_probabilities(model, history):
	'''
	HELPER FUNCTION FOR predict_sentence()
	Glean the model according to the length of the history. If bigram or trigram, need to go inside the nested null_dicts to 
	acquire the choice_of_words and probabilities vectors. Otherwise, go into the simple null_dict
	'''
	if len(history) > 0:
		history = tuple(history)
		choice_of_words = [word for word in model[history].keys()]
		probabilities = [word for word in model[history].values()]
	else:
		choice_of_words = [str(word[0]) for word in model.keys()]
		probabilities = [word for word in model.values()]
	return choice_of_words, probabilities



def predict_sentence(model, name, n_sentences, max_sentence_len, no_of_grams):
	"""
	Explained in chunks
	"""
	produced_sentences = []
	history = []
	max_sentence_len = max_sentence_len + len(history) + 1
	# Start the loop so it continues until all the desired sentences are created
	for i in range(n_sentences):
		history = set_history(history, None, name, no_of_grams)
		sentence = []
		sentence.append("<s>")
		# Keep going until we have either appended the ending character or reached the desired sentence length
		# Condition_dictionary is defined later to keep track of whether a sentence ended because of the ending token being encountered in the ngrams. 
		# Condition_length is defined to keep track of whether a sentence ended because the maximum number of words was reached
		condition_dictionary = True
		condition_length = True
		while condition_dictionary and condition_length:
			choice_of_words, probabilities = set_probabilities(model, history)
			# pick words based on the probabilities found in the ngrams dictionary
			pick_word = np.random.choice(choice_of_words, 1, p=probabilities)
			next_word = str(pick_word[0])
			sentence.append(next_word)
			history = set_history(history, next_word, name, no_of_grams)
			condition_dictionary = True if sentence[-1] != "</s>" else False
			condition_length = True if len(sentence) < max_sentence_len else False
		# If we reached the end of the sentence by reaching the max sentence length, we will need to append the ending character
		if "</s>" not in sentence:
			sentence.append("</s>")
		produced_sentences.append(sentence)
		# Initialise new history for each new sentence
		history = []
	return produced_sentences


def join_text(list_of_sentences):
	"""
	HELPER FUNCTION FOR main() to ensure that the first letter of the first word of a sentence is capitalised, and that 
	every sentence ends with a period.
	"""
	sentences_text = []
	for sentence in list_of_sentences:
		if sentence[0] == "<s>" and sentence[-1] == "</s>":
			sentence.pop(0)
			sentence.pop(-1)
		string_sentence = ' '.join(sentence)
		string_sentence = string_sentence.capitalize()
		finished_sentence = string_sentence + "."
		sentences_text.append(finished_sentence)
	return sentences_text


	

def main(model_name, corpus_name, n_sentences, max_sentence_len, filename):
	"""
	This function: 
	- Calls the custom parser function which we imported at the head of the document, to fetch the filename where the corpus is stored (either created for the first time now, 
	or during previously running the script)
	- Parses the corpus into a list of lists (sentences)
	- Creates the ngrams, and removes the sentence start token from the unigram model (so that it doesn't show up in the middle of sentences)
	- Produces sentences, and then formats them 
	- Writes the sentences to the file with the name specified by the user

	"""
	print("STATUS: Generating the corpus...")
	corpus_filename = produce_corpus(corpus_name)
	print("STATUS: Parsing the corpus...")
	corpus = parse_text_file(corpus_filename)
	print("STATUS: Training the model...")
	ngrams, no_of_grams = make_ngram_model(corpus, model_name)
	if model_name == "unigram":
		del ngrams[("<s>",)]
	print("STATUS: Generating sentences...")
	produced_sentences = predict_sentence(ngrams, model_name, n_sentences, max_sentence_len, no_of_grams)
	produced_sentences_str = join_text(produced_sentences)
	print("STATUS: Writing the sentences to a file...")
	with open(filename, 'w') as f:
		f.write("\n".join(produced_sentences_str))
	print("STATUS: Finished! You can view your file")
	




def check_filename(filename):
	"""
	HELPER FUNCTION FOR collect_inputs_from_gui()
	- Ensures that there are no reserved characters for an OS in the specified filename, and warns the user if this is the case
	- Tells the execution to go ahead or blocks it based on the return value
	"""
	forbidden_chars = ["/", "\\", "?", "%", "*", ":", "|", "<", ">", ".", ",", ";", "="]
	forbidden_chars_in_filename = []
	type_filename = str(type(filename))
	match type_filename:
		case "<class 'str'>":
			for i in filename:
				if i in forbidden_chars:
					forbidden_chars_in_filename.append(i)
					forbidden_chars_in_filename = ", ".join(forbidden_chars_in_filename)
					filename_error_message = "Your requested filename contained the special character " +"'"+ forbidden_chars_in_filename + "'"+ ". Please specify a filename without special characters."
					filename_error_field = tk.Label(instructions_frame, text = filename_error_message, fg = 'red')
					filename_error_field.pack()
					return False
				else:
					return True
		case "<class 'NoneType'>":
			return False


def check_numerical_inputs(input, field):
	"""
	HELPER FUNCTION FOR collect_inputs_from_gui()
	- Ensures that the inputs in the typing dialogues are numeric
	- Tells the execution to go ahead or blocks it based on the return value
	"""

	numeric = input.isdigit()
	match numeric:
		case True:
			number = int(numeric)
		case False:
			error_message = "Your requested number of " + field + " is not recognised or unsupported. Please specify a number from 1 and up"
			input_nondigit = tk.Label(instructions_frame, text = error_message, fg = 'red')
			input_nondigit.pack()
	return numeric
	


	
def collect_inputs_from_gui():
	"""
	- Grabs the user inputs and starts the program if the checks are passed by calling main(); waits otherwise. 
	- Stops the GUI loop if the user exits out of the GUI window
	"""
	go_ahead = False
	# If the user closes the window without inputting anything, end the program
	try:
		model_name = model_entry.get()
		max_sentence_len = number_of_words.get()
		n_sentences = number_of_sentences.get()
		filename = filename_entry.get()
		corpus_name = corpus_entry.get()
	except:
		sys.exit()
	go_ahead = check_filename(filename) and check_numerical_inputs(n_sentences, "sentences") and check_numerical_inputs(max_sentence_len, "words")
	if go_ahead == True:
		n_sentences = int(n_sentences)
		max_sentence_len = int(max_sentence_len)
		filename_full = filename + ".txt"
		main(model_name, corpus_name, n_sentences, max_sentence_len, filename_full)

	



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
instructions_label = tk.Label(instructions_frame, text = '''In this application, you can train a simple natural language processing model using unigrams, bigrams, or trigrams. 
Using one of these models, the application will then output your desired number of sentences in a text file. Please note: a large number of sentences or words per sentence can affect runtime.
							  
To start, please select which of the three models you wish to train from the drop-down menu. Then, choose which corpus you would like to train it on. Select your desired length of sentences to produce, 
and the maximum number of words you want each sentence to have. Please note: some sentences might end up shorter, but never longer than the maximum sentence length. 
Finally, specify the filename for the text file, without the file extension.

Once you're ready to begin generating, hit the start button.''')
instructions_label.pack()

# New frame for model details
model_details_frame = tk.LabelFrame(frame, text = "Model details")
model_details_frame.grid(row = 1, column = 0, padx = 20, pady = 20)
pick_model = tk.Label (model_details_frame, text = "Type of ngram to train")
pick_model.pack()
model_entry = ttk.Combobox(model_details_frame, values = ["unigram","bigram","trigram"], state = "readonly")
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
ask_corpus = tk.Label(file_details_frame, text = "Which corpus should the model be trained on? ")
ask_corpus.pack()
corpus_entry = ttk.Combobox(file_details_frame, values = ["abc","brown"], state = "readonly")
corpus_entry.pack()


# Add padding to all frames to make the window neater
for widget in frame.winfo_children():
	widget.grid_configure(padx=10, pady=5)
	
# Add the Button and pass in arguments to it
button = tk.Button(frame, text = "Start", command = collect_inputs_from_gui)
button.grid(row = 3, column = 0, padx=20, pady=5)
window.mainloop()


			
