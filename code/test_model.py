import glob
from bs4 import BeautifulSoup
import csv
from os import system, name
import json
from sklearn.metrics import multilabel_confusion_matrix

from pos_tagger import Emission, Transition

# path to source folder // путь к исходной папке
root_folder = '/HERE GOES THE PATH TO THE PROJECT MAIN FOLDER'
source_folder = root_folder + '/corpus/'

# required files // необходимые файлы
tag_frequencies = root_folder + '/data/tag_frequencies.json'
lexicon = root_folder + '/data/lexicon.json'
transition_probabilities = root_folder + '/data/transition_probabilities.json'

# tagset specification parameters // параметры спецификации набора тегов
openclass_tags = ['NN', 'JJ', 'RB', 'VB']
propername_tags = ['NP']
number_tag = 'NUMB_cd'
punctuation_tag = 'PNCT'

# metrics
metrics = {'0':['[0] no metric (False)', None], '1':['[1] tag frequencies (frec)', 'frec'], '2':['[2] smoothed tag frequencies (ln)','ln'], '3':['[3] inversed tag frequencies (itf)', 'itf']}
selected_metric = False
csv_file_name = False


while selected_metric is False:
	print("Select one metric to calculate tag's probabilities:")
	for key, value in metrics.items():
		print(value[0])
	input_metric = str(input("Enter the corresponding number: "))
	if input_metric in metrics.keys():
		selected_metric = metrics[input_metric][1]
		print("Selected metric '{}'".format(selected_metric))
	else:
		print('Not a valid option')

while csv_file_name is False:
	input_name = input('Enter a name for the file to save the results: ')
	if len(input_name) > 0:
		csv_file_name = input_name

file_name = '{}_{}.csv'.format(csv_file_name, selected_metric)

print('Test results to be saved in file {}'.format(file_name))


emission = Emission(tag_frequencies, lexicon, openclass_tags, propername_tags, number_tag, punctuation_tag)
transition = Transition(transition_probabilities, punctuation_tag)


print('Uploading xml files...')
all_files = glob.glob(source_folder + '*.xml')
training_corpus = ''
for filename in all_files:
	user_response = False
	valid_responses = ['y', 'n']
	while user_response == False:
		response = input('Use subcorpus {}? [y/n]'.format(filename.split('/')[-1]))
		if response in valid_responses:
			if response == 'y':
				with open(filename) as open_file:
					training_corpus += open_file.read()
			user_response = True
		else:
			print('Response not valid')

if len(training_corpus) == 0:
	print('No selected corpus')
	exit()

soup = BeautifulSoup(training_corpus, 'html.parser')

true_tags = []
predicted_tags = []
tag_list = []

for sentence in soup.find_all('sentence'):
	tagged_sentence = []
	for entry in sentence.find_all('token'):
		pair = (entry.attrs['word'], entry.attrs['tag'])
		if pair[1] != punctuation_tag:
			tagged_sentence.append(pair)
			tag = pair[1]
			tag = tag.split('_')[0]
			true_tags.append(tag)
			if tag not in tag_list:
				tag_list.append(tag)
	tokenized_sentence = [(token[0], 'number') if token[0].isnumeric() else (token[0], 'word') for token in tagged_sentence]
	tokenized_sentence.append(('.', 'PNCT'))
	pos_tags = emission.get_emission_probabilities(tokenized_sentence, selected_metric)
	disambiguated = transition.get_sequence(pos_tags)

	for tag in disambiguated:
		if tag[1] != punctuation_tag:
			tag = tag[1]
			tag = tag.split('_')[0]
			predicted_tags.append(tag)
			if tag not in tag_list:
				tag_list.append(tag)

print('Processing results metric {}...'.format(selected_metric))

def divide(numerator, denominator):
	denom = numerator + denominator
	if denom == 0:
		return 0
	else:
		return round(numerator / denom, 2)

def f_1(precision, recall):
	numerator = 2*(precision * recall)
	denominator = precision + recall
	try:
		return round(numerator/denominator,2)
	except:
		return 0

def calculate_precision_recall_f(conf_matrix, filename):
	with open(root_folder + '/' + filename, 'w') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(['Tег', 'TN', 'FP (I err)', 'FN (II err)', 'TP', 'Precision', 'Recall', 'F-score'])
		precision_list = []
		recall_list = []
		f_list = []
		for i, matrix in enumerate(conf_matrix):
			tp = int(matrix[1][1])
			fp = int(matrix[0][1])
			fn = int(matrix[1][0])
			precision = divide(tp, fp)
			precision_list.append(precision)
			recall = divide(tp, fn)
			recall_list.append(recall)
			f = f_1(precision, recall)
			f_list.append(f)
			writer.writerow([tag_list[i], matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1], precision, recall, f])
		average_precision = round(sum(precision_list) / len(precision_list),2)
		average_recall = round(sum(recall_list) / len(recall_list),2)
		average_f = round(sum(f_list) / len(f_list),2)
		writer.writerow(['Average', '', '', '', '', average_precision, average_recall, average_f])


confusion_matrix = multilabel_confusion_matrix(true_tags, predicted_tags, labels=tag_list)
calculate_precision_recall_f(confusion_matrix, file_name)

print('File {} created with the testing results'.format(file_name))
