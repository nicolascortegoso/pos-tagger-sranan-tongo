# import classes
from pos_tagger import Tokenizer, Emission, Transition

# path to source folder
root_folder = 'HERE GOES THE PATH TO THE PROJECT MAIN FOLDER'
source_folder = root_folder + '/data/'

# required files
compound_list = source_folder + 'compound_words.txt'
tag_frequencies = source_folder + 'tag_frequencies.json'
lexicon = source_folder + 'lexicon.json'
transition_probabilities = source_folder + 'transition_probabilities.json'

# tag specification parameters
default_tags = ['NN', 'JJ', 'RB', 'VB']
propername_tags = ['NP']
number_tag = 'NUMB_cd'
punctuation_tag = 'PNCT'

# object initialization
tokenizer = Tokenizer(compound_list)
emission = Emission(tag_frequencies, lexicon, default_tags, propername_tags, number_tag, punctuation_tag)
transition = Transition(transition_probabilities, punctuation_tag)

# sample text
txt = 'A boi lobi a umapikin'

# metric to calculate the tags' probabilities
metric = 'itf'

# separates the text string into a list of sentences and tokens
tokenized_sentences = tokenizer.tokenize(txt)
# processes each sentence separately
for sentence in tokenized_sentences:
    tagged_tokens = emission.get_emission_probabilities(sentence, metric) # assigns the possible tags to a word form
    disambiguated_sequence = transition.get_sequence(tagged_tokens) # disambiguates the assigned tags in the context of the sentence
    print(disambiguated_sequence, '\n')
