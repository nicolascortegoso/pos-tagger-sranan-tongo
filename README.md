# A POS-tagger for modern Sranan-Tongo

This project presents a prototype of a stochastic part-of-speech tagger for Sranan-Tongo. Typically, stochastic taggers are trained on large corpora that are only available for a few hundred languages.
The approach taken here assumes that a stochastic POS-tagger could still be trained with a limited amount of annotated data, as long as some external linguistic knowledge is provided.
This knowledge is provided in the form of a lexicon, which encodes some word forms and their respective part-of-speech tags.
Since this is a prototype intended for research purposes, users can define their own set of part-of-speech tags, modify and extend the vocabulary, or train the model on their annotated data. 
The tagger could also be adapted to tag others creoles or languages with similar features.

The ready-to-use tagger employs a set of 31 tags. It was trained on the following samples:
1. *apics1 165_sentences 1381_tokens.xml* (Winford Donald; Plag Ingo, Sranan structure dataset. APiCS. 2013)
2. *apics2 164_sentences 1472_tokens.xml* (Winford Donald; Plag Ingo, Sranan structure dataset. APiCS. 2013)
3. *sil1 111_sentences 827_tokens.xml* (Nickel Marilyn; Wilner John, Papers on Sranan Tongo, Summer Institute of Linguistics. 1984)
4. *sil1 110_sentences 833_tokens.xml* (Nickel Marilyn; Wilner John, Papers on Sranan Tongo, Summer Institute of Linguistics. 1984)

These samples contain manually annotated example sentences extracted from the APiCS database (Winford; Plag, 2013) and from a language description "Papers on Sranan Tongo" (Nickel; Wilner, 1984). It was assued that the examples from the APiCS database and those given by Nickel and Wilner could account for most
of the part-of-speech combination sequences in Sranan Tongo, since they are part of works that pursue to describe most of the morphsyntactic features of the language. These samples are located in the *corpus* folder of this project, along with a few others.

The model trained on this samples and tested on *wilner 70_sentences 613_tokens.xml* showed an average precision, recall and f-score of 0.81, 0.81 and 0.79, respectively. These scores can potentially be improved with more training data and a broader lexicon.

The file with the compiled lexicon contains 346 entries.

## Default tag set

The usefulness of a set of tags depends on how much information is required to complete a specific task. For prediction purposes, it would be ideal to give distinctive tags to words that have different distributions. If the tags are too general, as in the classical distinction: noun, verb, adjective, adverb, pronoun, preposition, conjunction, interjection, numeral, article, they will not be very good predictors. More subtle distinctions, such as knowing whether a word is a possessive or a personal pronoun, can predict better which words may occur next to it (possessive pronouns are likely to be followed by a noun, personal pronouns by a verb). However, if the tags are too specific, more training data is going to be needed. The nomenclature of the tags are based on those from the Brown Corpus. The following table describes the tag set that was used to annotate the sentences:

Tag|Description|Example
---|-----------|-------
AP|quantifier|moro, ala
AP|specifier|srefi, alamala
AT|article|a, den, wan
CC|coordinating conjunction|èn, nanga
COMP|comparative|moro, p(a)sa
COMPL|complementizer|taki, dati
COP|copula|a, na
CS|subordinating conjunction|awinsi, te
DT|demostrative pronoun|dati, disi
EX|existential copula|de
FOC|focus marker|na
IN|preposition|te, abra
INL|preposition of place|ini, ondro
JJ|attributive adjective|bigi, redi
LOC|locational preposition|na
MD|modal|musu,sa
NEG|negation|no
NN|noun|boi, alen, oto
NP|proper noun|Sranan Tongo, Akuba
NUMB|numeral|twarfu, fosi, 
OF|possessive linker|fu
PRN|pronoun|mi, den
PPL|reflexive pronoun|ensrefi, yusrefi
PP$|possessive pronoun|mi, yu, en
RB|adverb|moro, agen
RN|nominal adverb|tamara, mamanten
REL|relative pronoun|di, san, pe
TAM|time and aspect marker|ben, e, o
VB|verb|go, taki, sabi
UH|interjection|ei, we
WP|question word|san, suma


## Configuration

The POS-tagger requires the following files to work:

* *compound_words.txt*: contains a list of lexical items that consist of more than one token but still must be considered as a unit. For example: "Sranan Tongo", "no wan"; 
* *lexicon.json*: contains a set of word forms with the possible tags that they can assume;
* *tag_frequencies.json*: contains the frequency of the tags in the training sample;
* *transition_probabilities.json*: contains the conditional probabilities of observing tag *ti* in a sentence, provided that before it appear tags *ti-2* and *ti-1*.

These files are located on the *data* folder of this project.

## Example code

The script below shows how to import and initialize the classes, define the general parameters and employ the methods to parse a text in Sranan-Tongo.   

```
# import classes
from pos_tagger import Tokenizer, Emission, Transition

# path to source folder
root_folder = '/IMPORTANT: use your path to the project folder'  
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
    print(disambiguated_sequence, '\n')```
```

## How it works

The parsing of a text takes place in three separate but consecutive processes:
1. text segmentation;
2. assigning tags and probabilities to word forms;
3. finding the most likely tag sequence.

### Text segmentation

Before beginning with the tagging process, it is necessary to divide the written text into meaningful units such as sentences, words, punctuation marks, etc. This process is known as tokenization. The tokenization algorithm divides the written language string into sentences and their elements. The implementation of the algorithm takes three steps:
1. identification of tokens;
2. segmentation of sentences;
3. joining the tokens of compound words.

The tokens are extracted employing regular expressions. The rules identify four general classes: "word", "acronym", "number" and punctuation marks. The "acronym" class includes strings like "U.S.A." and "T.M.".
The text is split into sentences based on newlines, periods, or exclamation points, question marks. Finally, a dictionary look-up joins the separate tokens that forms a compound word.


The tokenization algorithm is implemented in the *Tokenizer* class from the *pos_tagger.py* file. When initializing the class object, the text file *compound_words.txt* with compound words is passed as the single argument. The tokenize method of object of the Tokenizer class takes a text string as an argument and returns a list of lists (one for each segmented sentence) with tuples of the token and their class.

### Assigning tags and probabilities to word forms

After tokenization, the algorithm will assign possible tags for each token and their probabilities. The implementation of the algorithm takes three steps:
1. filters the words from other types of tokens;
2. assigns possible tags for one word form;
3. calculates the probabilities for each of the assigned tags.

The tokens that during the tokenization phase have been classified as "number" or as a punctuation mark are immediately tagged with their correspondig tag and receive a probability of 1. If the token has been classified as "word" or as "acronym", the algorithm adopts a dictionary(lexicon)-based approach for tagging:
* First, a word from is pre-assigned with the list of defaul tags that was passed as argument. This list contains typically "nouns", "attributive djectives", "adverbs" and "verbs".
* Then the algorithm looks for the word form in the lexicon. If the given word form is found, then the pre-assigned tags are replaced by the tags that were specified in the lexicon.
* If the search in the lexicon is unsuccessful, the algorithm checks if the word starts with a capital letter. Provided that condition is not met, the algorithm understands that the list with the pre-assigned tags is the best guess and returns it. In case that the word does start with a capital letter, the algorithm looks at its position in the sentence. If the word is not at the very beginning of the sentence, then it assumes that the capitalized word is a proper name and, therefore, the pre-assigned tags are replaced by the list for proper names that was passed as argument. If the word appears at the very beginning of the sentence, then the algorithm cannot accept the capital letter as a conclusive indicator that the word form corresponds to a proper noun (the first letter of any word in the begging of a sentence if often capitalized). In this case, the algorithm returns the preliminary pre-assigned tags plus the tags for proper names.

If only one tag is unambiguously assigned for a given word form, then its probability equals 1. Otherwise, the probabilities of the assigned tags are calculated using a metric. If no metric is specified, then all assigned tags get the same likelihood. The sum of all tags probabilities for a given word form is always equal to 1.
Metrics:
* *'frec'*: sets the probabilities of the assigned tags based on the counts from the training data. Tags with higher frequencies in the training data get proportionally higher probabilities and vice versa;
* *'ln'*: is basically the same as the previous metric, with the addition of the natural logarithm to smooth out the tag counts from the training data, so that the differences in the assigned  probabilities are less extreme; 
* *'itf'*: penalizes tags with higher frequencies in the training data in order to make more likely those tags with lower counts.

The tagging algorithm is implemented in the "Emission" class from the "pos_tagger.py" file. When initializing a class object, the following arguments are passed in the specified order:
1. the file "tag_frequencies.json" with the count of tags in the training set;
2. the file "lexicon.json" containing pairs of word forms and the tags they can take;
3. a list with the default tags to pre-assign to the word forms before the lexicon look-up; 
4. a list with tags to apply when a word form is capitalized;
5. a single tag to label numbers;
6. a single tag to label punctuation marks.

The method *get_emission_probabilities* of the *Emission* class takes as arguments a list with a tokenized sentence and a metric for calculating the probabilities of the tags. The method returns a list containing a set of tags and their corresponding probabilities for each word form in the sentence.

### Finding the most likely tag sequence

After individually assigning the possible tags to the word forms, the POS-tagger seeks to determine the most likely tag for each word form in the context of the sentence. 
The input data for the algorithm is the list with all the possible tags for a given word form and their probabilities. The algorithm selects as the most likely tag sequence the one that maximizes the product of two terms: the probability that the tag is assigned to the word form and the tag sequence. The output is one tag for each word form.

The algorithm is implemented in the *Transition* class from the *pos_tagger.py* file. The object is initialized with the file *transition_probabilities.json* and a tag for specifying punctuation marks as arguments.
The method *get_sequence* of the *Transition* class takes as an argument a list containing tags and their corresponding probabilities for each word form in the sentence. The method returns a list of tuples containing the predicted tag for each word form in the sentence. This method is an implementation of the Viterbi decoding algorithm.

## Training the POS-tagger with own parameters

The users have the option of retrain the model using their own parameters. This includes the ability to:
* use a modified / different tag set
* expand / modify the data encoded in the lexicon
* train the model with a different training set

The first two modifications are introduced by manually creating/editing two "csv" (comma-separated values) files. After introducing changes in the "csv" files, for the changes to take effect, the files must be (re)compiled with the help of a script written in Python3. The script does not only compiles the file, but also checks for data integrity.

### (Re)defining the tagset

In a POS tagger, parts of speech are specified by a tag, so the first step is to define a set of tags in the "tagset.csv" file. The file must meet the following specifications:
* each line of the file contains one tag and the corresponding description;
* the tag and its description are separated by a comma, no space between them.
For example:

```
PRN_1sg,singular first person pronoun
PRN_2sg,singular second person pronoun
PRN_3sg,singular third person pronoun
PRN_1pl,plural first person pronoun
PRN_1+2pl,plural first-second person pronoun
PRN_3pl,plural third person pronoun
```

The file can be created using a spreadsheet application. The size of the table must be *nx2* (n rows and 2 columns), where *n* is the number of tags. Tags are listed in rows: the first column specifies the a tag, and the second one specifies the tag description.
When saving the file, the "csv" format must be specified and verified that the "field delimiter" parameter contains a comma "," and the "line delimiter" parameter – nothing.

The nomenclature of a tag can contain any combination of characters. Only the *_* character is reserved to separate the main element from the accessory one in the nomenclature. The main element of the tag’s nomenclature is used to train the model and make the predictions. The *_* character introduces ancillary information after the main element. This information is optional and may be absent, since the model takes into account only the main element and ignores the rest. This is so to avoid the use of overly specific tags and to keep the set of tags used to train the model to a reasonable size. For example, in the case of the category "personal pronoun", since all personal pronouns, regardless of number and person, have the same distribution, specifying person and number in the main element will increase the number of tag without improving the model’s predictions.

The content from the "tagset.csv" table is converted into a "json" file using the "compile_tagset.py" script. The data in the "tagset.json" file is required in the the following steps of compiling the lexicon and training the model.

### The lexicon

The lexicon should contain as many lexical elements as possible from the so-called closed classes of words, like articles, prepositions, pronouns, time and aspect markers, etc. Nouns, attributive adjectives, adverbs, interjections and verbs belong to the so-called open class words, because new elements are constantly being created or borrowed from other languages. By the same definition of this category, it is impossible to create a lexicon (no matter how large) to contain all the words within this class. Word forms from the open class are included in the lexicon only if they have a homonym within the closed class words. For example, the noun “musu” (beret) has a homonym in the modals  modal “musu” (must), hence, the lexicon contains both "musu" as modal, and as noun.
The compiled lexicon for this project also covers most of the more commom conjunctions, interjections and nominal adverbs.
It is a good idea to include a word form from the open class in the lexicon if exist certitude about the tags that it can assume.
The lexicon is also saved in the "csv" format. The "csv" file must meet the following specifications:
* each of the lines contains one lexical element and a corresponding tag;
* the lexical element and its tag are separated by a comma without a space;
* if a lexical element has more than one tag, then a new line is created for this lexical element with each of the tags;
* a lexical element can consist of more than one word (token). For example, "Sranan Tongo".

Нere is an example a "csv" file containing the lexicon:

```
a,AT_sg
a,COP
a,PRN_3sg
de,EX
den,AT_pl
den,PRN_3pl
den,PP$_3pl
en,PRN_3sg
en,PP$_3sg
na,COP
mi,PRN_1sg
mi,PP$_1sg
unu,PRN_1+2pl
unu,PP$_1+2pl
wan,AT_ind
wi,PRN_1pl
wi,PP$_1pl
yu,PRN_2sg
yu,PP$_2sg
```

The same content can be distribuited in different "csv" files. This does not affect the compilation process and allows to keep the lexicon data more organized.

Just like when working with the tag set, "csv" files can be created / modified using a spreadsheet application. The size of the table must be *nx2* (*n* rows and 2 columns), where *n* is the number of lexical items. For example: the first column must contain lexical items and the second must contain the corresponding labels. When saving the file, follow the same procedure as in the previous section.


The script “compile_lexicon.py” takes as input all the *csv* files in the lexicon folder to create two files:
* *lexicon.json*: the compiled lexicon;
* *compound_words.txt*: the list of lexical elements consisting of more than one token
The compiled lexicon consists of a hash-table, where each key is each unique word form and its corresponding value is a list of all tags that this word form can take. Homonyms gather around the same key. For example, the word form “a” in the examples belongs to the word class “article”, “personal pronoun” and “link”. Therefore, the key “a” in the compiled lexicon contains a list of all the above parts of speech:

```
"a": ["AT_sg", "COP", "PN_3sg"]
```
The word list with the composed lexical items is used during the tokenization process to concatenate those tokens given in the list. For example, a sequence of tokens "no" (no) and "wan" (one) must become one "no wan" (nobody), because according to Sranan-Tongo’s grammar, negation can only precede verbs.
The script also checks for invalid tags. It will inform if a tag given in the *csv* lexicon files has not been previously specified in the file *tagset.csv*.

### (Re)training the model

The annotated data must be in *xml* format. It needs to be split in sentences between *<sentence> </sentence>* tags. The tokens inside the sentence are contained between the *<token> </token>* tags. Each token must contain the following attributes:
* *word=* the word form;
* *type=*  the main element of the tag (before the *_* symbol);
* *tag=* the full form of the tag's nomenclature.
    
All other content between tags is optional. Examples of annotated data are in the folder "corpus" of the project. The annotated data can be used to train or to test the model. 
The training algorithm calculates the probability of occurrence of a tag *ti*, provided that it is preceded by the tags *ti-2* and *ti-1*. For this calculation, the algorithm considers just the main element of the tag's nomenclature as defined in the file "tagset.json".

The script *train_model.py* reads all the *xml* files from a specified folder and takes as input those that the user chooses to train the model with. As output, the algorithm creates two files with the same content, but in different formats ("csv" and "json"). These files contain the calculations of the transition probabilities. The file in "json" format is required by the POS-tagger during the disambiguation process. The one in "csv" format is intended for human readability.

To (re)train the model the following python libraries are required: numpy, pandas, beautifulsoup4.

## Testing the model

The trained model can be tested with the script *test_model.py*. The testing script reads all the *xml* files from a specified folder and takes as input those that the user chooses to test the model with. The script calculates the accuracy, recall and the f-score of the model predictions for each of the labels and takes an average of all of them. The results are presented in a *csv* file.

To test the model the following python libraries are required: sklearn and beautifulsoup4.

