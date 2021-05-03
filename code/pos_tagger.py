import re
import json

# emission probabilities
class Emission(object):
    def __init__(self, tag_frequencies, lexicon, openclass_taglist, propername_taglist, number_tag, punctuation_tag='PNCT'):
        self.openclass_tags = []
        self.propername_tags = []
        self.number_tag = number_tag
        self.punctuation_tag = punctuation_tag
        with open(tag_frequencies) as frequencies_json:
            self.tag_frequencies = json.load(frequencies_json)
        with open(lexicon) as lexicon_json:
            self.lexicon = json.load(lexicon_json)
        for tag in openclass_taglist:
            if tag in self.tag_frequencies.keys() and tag not in self.openclass_tags:
                self.openclass_tags.append(tag)
        for tag in propername_taglist:
            if tag in self.tag_frequencies.keys() and tag not in self.propername_tags:
                self.propername_tags.append(tag)
        self.D = 0
        for k, v in self.tag_frequencies.items():
            self.D += v

    def __get_tags(self, token, position):
        word = token.lower()
        tags = self.openclass_tags
        if word in self.lexicon.keys():
            tags = self.lexicon[word]
        elif token[0].isupper():
            tags = self.propername_tags
            if position == 0:
                tags = tags + self.openclass_tags
        return tags

    def __frec(self, tag_list, metric):
        emission_probabilities = {}
        total_frequencies = 0
        for tag in tag_list:
            base_tag = tag.split('_')[0]
            frequency = self.tag_frequencies[base_tag]
            if metric == 'ln':
                frequency = self.__ln(frequency) + 0.00000001
            total_frequencies += frequency
            emission_probabilities[tag] = frequency
        for k,v in emission_probabilities.items():
            emission_probabilities[k] = v / total_frequencies
        sorted_p = sorted(emission_probabilities.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_p

    def __itf(self, tag_list):
        emission_probabilities = {}
        total_frequencies = 0
        for tag in tag_list:
            base_tag = tag.split('_')[0]
            frequency = self.tag_frequencies[base_tag]
            total_frequencies += frequency
            emission_probabilities[tag] = frequency
        for k,v in emission_probabilities.items():
            emission_probabilities[k] = (total_frequencies - v) / (total_frequencies * (len(emission_probabilities) -1))
        sorted_p = sorted(emission_probabilities.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_p


    def get_emission_probabilities(self, token_list, metric=None):
        methods = ['frec', 'ln', 'itf']
        tags = []
        for i, token in enumerate(token_list):
            entry = token[0]
            if token[1] in ["word", "acronym"]:
                retreived_tags = self.__get_tags(token[0], i)
                if metric in methods and len(retreived_tags) > 1:
                    if metric == 'itf':
                        probabilities = self.__itf(retreived_tags)
                    elif metric == 'frec' or metric == 'ln':
                        probabilities = self.__frec(retreived_tags, metric)
                    t = (token[0],probabilities)
                else:
                    probabilities = [(tag,1) for tag in retreived_tags]
                    t = (token[0],probabilities)
            elif token[1] == 'number':
                t = (token[0],[(self.number_tag,1)])
            else:
                t = (token[0],[(self.punctuation_tag,1)])
            tags.append(t)
        return tags

    def __ln(self, x):
        val = x
        return 99999999*(x**(1/99999999)-1)

# Transition probabilities
class Transition(object):
    def __init__(self, transition_probabilities, punctuation_tag='PNCT'):
        self.punctuation_tag = punctuation_tag
        with open(transition_probabilities) as json_file:
            self.data = json.load(json_file)

    def get_transition_probabilities(self, tag, previous_tag):
        try:
            probability = self.data[tag][previous_tag]
            return probability
        except:
            return 'One of the tags do not have a valid form'

    def __separate_punctuation_marks(self, sentence):
        sentence_without_punctuation_marks = []
        punctuation_marks_positions = {}
        for i, token in enumerate(sentence):
            if token[1][0][0] == self.punctuation_tag:
                punctuation_marks_positions[i] = token[0]   # stores the punctuation sign in a hash-table with their position as key for later retrieval
            else:
                sentence_without_punctuation_marks.append(token)
        return sentence_without_punctuation_marks, punctuation_marks_positions

    def get_sequence(self, pos_tags):
        tagged_tokens = pos_tags    # undesambiguated sentence
        sentence_without_punctuation_marks, punctuation_marks_positions = self.__separate_punctuation_marks(tagged_tokens) # separate punctuation marks and save their positions
        error_in_desambiguation_process = False
        desambiguated_sentence = []
        token_counter = 1
        end_of_sentence = ('EOS', [('<E>',1)])
        sentence_without_punctuation_marks.append(end_of_sentence)

        previous_states = [{'<S>': [1, '<*>']}]
        for token in sentence_without_punctuation_marks:
            current_states = []
            dict_pos = {}
            token_counter += 1
            possible_tags = token[1]
            for tag in possible_tags:
                main_pos = tag[0].split('_')
                t = main_pos[0]
                dict_pos[t] = [0, '']#'NP']
                for key,value in previous_states[-1].items():
                    previous_state_prob = value[0]
                    emission_prob = tag[1]
                    u_v = '{}_{}'.format(value[1],key)
                    transition_prob = self.data[t][u_v]
                    probability = previous_state_prob * emission_prob * transition_prob
                    if probability > dict_pos[t][0]:
                        dict_pos[t][0] = probability
                        dict_pos[t][1] = key
            previous_states.append(dict_pos)

        highest_score = '<E>'
        desambiguated_tag_list = []
        for i in previous_states[::-1]:
            try:
                highest_score = i[highest_score][1]
                desambiguated_tag_list.append(highest_score)
            except:
                error_in_desambiguation_process = True

        desambiguated_tag_list_reversed = desambiguated_tag_list[::-1][2:]
        desambiguated_sentence = []
        punctuation_marks_counter = 0
        for i, token in enumerate(tagged_tokens):
            if i in punctuation_marks_positions.keys():
                punct_mark_list = (punctuation_marks_positions[i])
                pair = (punct_mark_list, self.punctuation_tag)
                desambiguated_sentence.append(pair)
                punctuation_marks_counter += 1
            else:
                desambiguated_pos = desambiguated_tag_list_reversed[i-punctuation_marks_counter]
                alternatives = tagged_tokens[i][1]
                for j, alternative in enumerate(alternatives):
                    base_tag = alternative[0].split('_')
                    if base_tag[0] == desambiguated_pos:
                        pair = (tagged_tokens[i][0], tagged_tokens[i][1][j][0])
                        desambiguated_sentence.append(pair)
                        break
        if error_in_desambiguation_process:
            return False
        else:
            return desambiguated_sentence


class Tokenizer():
    def __init__(self, filename=False):
        self.composed_tokens = {}
        if filename:
            try:
                f = open(filename, 'r', encoding='UTF-8')
                for row in f:
                    composed_token_elements = self.__validate_form(row)
                    key = ''
                    for i,j in enumerate(composed_token_elements):
                        if len(composed_token_elements) -1 > i:
                            key = '{} {}'.format(key, j).strip()
                            if key not in self.composed_tokens.keys():
                                self.composed_tokens[key] = []
                            next = composed_token_elements[i+1].strip()
                            if next not in self.composed_tokens[key]:
                                self.composed_tokens[key].append(next)
            except:
                print('File with composed tokens not found')

    def __validate_form(self, row):
        composed_token = row.strip().split(' ')[::-1]
        return composed_token

    def __unify_tokens(self, sentences):
        new_sentences = []
        for sentence in sentences:
            new_sentence = []
            reversed_sentence = sentence[::-1]
            sentence_length = len(sentence)
            i = 0
            while i < sentence_length:
                key = reversed_sentence[i][0].lower()
                if key in self.composed_tokens.keys():
                    chunk = key
                    while key in self.composed_tokens.keys():
                        value = self.composed_tokens[key]
                        next = reversed_sentence[i+1][0].lower()
                        if next in value:
                            chunk = next + ' ' + key
                            key = key + ' ' + next
                        else:
                            break
                        i += 1
                    new_sentence.append((chunk, 'word'))
                else:
                    new_sentence.append(reversed_sentence[i])
                i += 1
            new_sentences.append(new_sentence[::-1])
        return new_sentences

    def __separate_sentences(self, token_list):
        token_list = token_list
        end_of_sentence_markers = ['exclamation mark', 'question mark', 'period', 'new line']
        sentences = []
        current_sentence = []
        open_citation = False
        ignore_token = False
        if token_list[-1][1] not in end_of_sentence_markers:
            pair = ('\n', 'new line')
            token_list.append(pair)
        for i, token in enumerate(token_list):
            if ignore_token:
                ignore_token = False
            else:
                if token[0] == '"':
                    open_citation = True
                current_sentence.append(token)
                if token[1] in end_of_sentence_markers:
                    try:
                        if token_list[i+1][0] == '"' and open_citation:
                            current_sentence.append(token_list[i+1])
                            open_citation = False
                            ignore_token = True
                    except:
                        pass
                    if len(current_sentence) > 1:
                        sentences.append(current_sentence)
                    current_sentence = []
        return sentences

    def tokenize(self, text):
        scanner=re.Scanner([    # regex rules to extract tokens // правила регулярных выражений для извлечения токенов
        (r"\n", lambda scanner,token:(token, "new line")),
        (r'[„”"“”‘’‹›«»]', lambda scanner,token:(token, "quotation mark")),
        (r"(?:[a-zA-Z]\.){2,}", lambda scanner, token:(token, "acronym")),
        (r"[A-zA-ZÀ-ža-zà-ž’'-]+", lambda scanner,token:(token, "word")),
        (r"(\d+(?:[\.,]\d+)?)+", lambda scanner,token:(token, "number")),
        (r"[0-9]+", lambda scanner,token:(token, "number")),
        (r"\.+(!?|\??)", lambda scanner,token:(token, "period")),
        (r",", lambda scanner,token:(token, "comma")),
        (r":", lambda scanner,token:(token, "colon")),
        (r";", lambda scanner,token:(token, "semicolon")),
        (r'[()]', lambda scanner,token:(token, "bracket")),
        (r"<>/+//-", lambda scanner,token:(token, "operator")),
        (r'\?+\.?', lambda scanner,token:(token, "question mark")),
        (r'!+\.?', lambda scanner,token:(token, "exclamation mark")),
        (r'[−/-—]', lambda scanner,token:(token, "hypen")),
        (r'[$€]', lambda scanner,token:(token, "symbol")),
        (r'[&\*•\|²]', lambda scanner,token:(token, "other")),
        (r"\s+", None),                                         # space // пробелы
        (r".", lambda scanner, token:(token, "notMatched")),    # ignore unmatched tokens // игнорировать нераспознанные токены
        ])
        token_list = scanner.scan(text)                         # word segmentation // выделение слов
        sentences = self.__separate_sentences(token_list[0])    # sentence segmentation // сегментация предложений
        unified_tokens = self.__unify_tokens(sentences)         # unifies composed tokens // объединяет составные токены
        return unified_tokens
