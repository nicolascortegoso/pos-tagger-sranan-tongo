import numpy as np
import pandas as pd
import glob
from bs4 import BeautifulSoup
import csv
from os import system, name
import json

# path to the root folder // ввестите Ваш путь в папку проекта
root_folder = '/HERE GOES THE PATH TO THE PROJECT MAIN FOLDER'
source_folder = root_folder + '/corpus/'
target_folder = root_folder + '/data/'

# loads the tagset // загружается набор тегов
with open(target_folder + 'tagset.json') as json_file:
	tags = json.load(json_file)
	json_file.close()##check
tag_set = {}
for k,v in tags.items():
	t = v[0]
	if t not in tag_set.keys():
		tag_set[t] = 0

# do not consider the following tags // не учитаемые следующие теги
tokens_to_ignore = ['PNCT', 'SYMB']

# load xml files // загружается файлы xml
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

# just a function to clear the screen // функция для очистки экрана
def clear():
	if name == 'nt': 		# for windows
		_ = system('cls')
	else:					# for mac and linux(here, os.name is 'posix')
		_ = system('clear')
clear()


# function for calculating the transition probabilities // функция для вычисления вероятности переходов
def t_given_uv(t, u, v, train_bag):
    tags = [pair[1] for pair in train_bag] 	#only tags are selected // выбераем только теги
    count_uv = 0
    count_t_uv = 0
    for index in range(len(tags)-1):
        if tags[index]==u and tags[index+1] == v:
            count_uv += 1
    for index in range(len(tags)-2):
        if tags[index]==u and tags[index+1] == v and tags[index+2] == t:
            count_t_uv += 1
    return (count_t_uv, count_uv)

# extract word forms and tags from the training set // извлекаются словоформы и части речи из обучающего выборки
subcorpus = []
total_tokens = 0
soup = BeautifulSoup(training_corpus, 'html.parser')
for sentence in soup.find_all('sentence'):
	sent = [('<*>', '<*>'), ('<S>', '<S>')]
	for entry in sentence.find_all('token'):
		word = entry.attrs['word']
		tag = entry.attrs['type']
		if tag in tag_set.keys():
			total_tokens += 1
			tag_set[tag] += 1
			token_pos = (word, tag)
			sent.append(token_pos)
	end_of_sentence = ('<E>', '<E>')
	sent.append(end_of_sentence)
	subcorpus.append(sent)

# creates lists of training and test words with POS tags // создаем списки обучающих и тестовых слов с POS тегами
train_tagged_words = [ tup for sent in subcorpus for tup in sent ]	# list of tuples // список кортежов
tags = {tag for word,tag in train_tagged_words} # unique tags form the training set // уникальные теги в обучающих данных

# creates the possible tags bigrams, excluding those not needed // создает возможные биграммы тегов, исключая ненужные
combined_tags = ['<*>_<S>']
for u in list(tags):
	if u not in ['<*>', '<E>']:
		for v in list(tags):
			if v not in ['<*>', '<S>', '<E>'] :
				comb_tag = '{}_{}'.format(u,v)
				combined_tags.append(comb_tag)

# creates the tag matrix // создает матрицу тегов
tags.remove('<S>')
tags.remove('<*>')
tags_matrix = np.zeros((len(combined_tags), len(tags)), dtype='float32')

# training algorithm // алгоритм обучения
cp_counter = 1
for i, u_v in enumerate(combined_tags):
	for j, t in enumerate(list(tags)):
		uv = u_v.split('_')
		try:
			probability = t_given_uv(t, uv[0], uv[1], train_tagged_words)[0]/(t_given_uv(t, uv[0], uv[1], train_tagged_words)[1])
		except:
			probability = 0
		tags_matrix[i, j] = probability
		print('[{}] t:{} / u:{} x v:{} = {}'.format(cp_counter, t, uv[0], uv[1], probability))
		cp_counter += 1
		if probability > 0:
			tags_matrix[i, j] = probability
		else:
			tags_matrix[i, j] = 0.000000001

		tags_df = pd.DataFrame(tags_matrix, columns = list(tags), index=combined_tags)

# creates the files with the probabilities // создаются файлы с вероятностей переходов
tags_df.index = combined_tags
print(tags_matrix.shape)
print(tags_df)
df1_transposed = tags_df.T
df_sorted = df1_transposed.sort_index(axis=1)
df_sorted_index = df_sorted.sort_index()
df_sorted_index.to_csv(target_folder + 'transition_probabilities.csv')
tags_df.to_json(target_folder + 'transition_probabilities.json', indent=4)

# creates a file with the tags frequencies on the training data // создается файл с частотом тегов в обучающих выборке
with open(target_folder + 'tag_frequencies.json', 'w') as outfile:
    json.dump(tag_set, outfile, indent=4, sort_keys=True)

print('Ready. Created files "transition_probabilities.json and transition_probabilities.csv"')
print('Tokens processed:',total_tokens)
