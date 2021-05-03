import glob
import json
import csv

# root folder //  корневая папка 
root_folder = '/HERE GOES THE PATH TO THE PROJECT MAIN FOLDER'
source_folder = root_folder + '/lexicon/'
target_folder = root_folder + '/data/'
data_folder = root_folder + '/data/'

composed_words = []
lexicon = {}


with open(data_folder + 'tagset.json') as json_file:
    valid_tags = json.load(json_file)


# loading csv files // загружаются csv файлы
print('Loading csv files with the lexical entries ...')
all_files = glob.glob(source_folder + '*.csv')
li = []
for filename in all_files:
    print(filename)
    try:
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            row_counter = 0
            for row in csv_reader:
                row_counter += 1
                entry = row[0].strip()
                tag = row[1].strip()
                if ' ' in entry:
                    composed_words.append(entry)
                if entry not in lexicon.keys():
                    lexicon[entry] = []
                if tag in valid_tags.keys():
                    if tag not in lexicon[entry]:
                        lexicon[entry].append(tag)
                else:
                    raise Exception('ERROR not in defined tagset\ntag: "{}"\nentry word: "{}"\nrow: {}'.format(tag, entry, row_counter))
        # the file "lexicon.json" is created with a hash table (key -> word form: value -> [list of tags]  создается файл "lexicon.json" с хеш-таблицей (ключ -> словоформа: значение -> [список тегов]
        with open(target_folder + 'lexicon.json', 'w') as fp:
            json.dump(lexicon, fp, indent=2)

        # file "compound_words.txt" is created with lexical entries consisting of more than one token  // создается файл "compound_words.txt" с записями, состоящими из более чем одного токена
        with open(target_folder + 'compound_words.txt', 'w') as file:
            for item in composed_words:
                line = '{}\n'.format(item)
                file.write(line)

    except Exception as ex:
        print(ex)