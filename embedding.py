import os
from keras.preprocessing.text import Tokenizer

import numpy as np
from gensim.models import Word2Vec
import string1

EMBEDDING_DIM = 100
MAX_VOCAB = 5171

word_arr = []
word_index = {}
embeddings_index = {}


def to_lines(descriptions):
    all_desc = list()
    for key in descriptions.keys():
        [all_desc.append(d) for d in descriptions[key]]
    return all_desc


# fit a tokenizer given caption descriptions
def create_tokenizer(descriptions):
    lines = to_lines(descriptions)
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(lines)
    print("test")
    return tokenizer


# load doc into memory
def load_doc(filename):
    # open the file as read only
    file = open(filename, 'r')
    # read all text
    text = file.read()
    # close the file
    file.close()
    return text


# extract descriptions for images
def load_descriptions(doc):
    word_index = []
    mapping = dict()
    # process lines
    for line in doc.split('\n'):
        # split line by white space
        tokens = line.split()
        # print(tokens)
        if len(line) < 2:
            continue
        # take the first token as the image id, the rest as the description
        image_id, image_desc = tokens[0], tokens[1:]
        # for x in image_desc:
        #     word_index.append(x)
        # print(len(word_index))

        # remove filename from image id
        image_id = image_id.split('.')[0]
        # convert description tokens back to string
        image_desc = ' '.join(image_desc)
        # print(image_desc)
        # create the list if needed
        if image_id not in mapping:
            mapping[image_id] = list()
        # store description
        mapping[image_id].append(image_desc)
        # print(mapping)
    return mapping


def clean_descriptions(descriptions):
    # prepare translation table for removing punctuation
    table = str.maketrans('', '', string1.punctuation)
    for key, desc_list in descriptions.items():
        for i in range(len(desc_list)):
            desc = desc_list[i]
            # tokenize
            desc = desc.split()
            # convert to lower case
            # desc = [word.lower() for word in desc]
            # remove punctuation from each token
            desc = [w.translate(table) for w in desc]
            # remove hanging 's' and 'a'
            # desc = [word for word in desc if len(word) > 1]
            # remove tokens with numbers in them
            # desc = [word for word in desc if word.isalpha()]
            # desc = {x.replace('।', '') for x in desc}
            # print(desc)
            # store as string
            desc_list[i] = ' '.join(desc)
            # print(desc_list[i])


# convert the loaded descriptions into a vocabulary of words
def to_vocabulary(descriptions):
    # build a list of all description strings
    all_desc = set()
    for key in descriptions.keys():
        [all_desc.update(d.split()) for d in descriptions[key]]
    for x in all_desc:
        word_arr.append(x)
    for i in range(len(word_arr)):
        word_index[word_arr[i]] = i
    return all_desc


# save descriptions to file, one per line
def save_descriptions(descriptions, filename):
    lines = list()
    for key, desc_list in descriptions.items():
        for desc in desc_list:
            lines.append(key + ' ' + desc)
    data = '\n'.join(lines)
    file = open(filename, 'w')
    file.write(data)
    file.close()


# extract features from all images

# directory = '../Flickr8k_Dataset'
# features = extract_features(directory)
# print('Extracted Features: %d' % len(features))
# # save to file
# dump(features, open('../models/features.pkl', 'wb'))

# prepare descriptions

filename = '../Flickr8k_text/Flickr_8k.token.txt'
# load descriptions
doc = load_doc(filename)
# parse descriptions
descriptions = load_descriptions(doc)
print('Loaded: %d ' % len(descriptions))
# clean descriptions

# summarize vocabulary
vocabulary = to_vocabulary(descriptions)
print('Vocabulary Size: %d' % len(vocabulary))

# save to file
# save_descriptions(descriptions, '../att_model/descriptions.txt')

#
# def get_embedding_matrix(word2idx):
#     w2v_model = Word2Vec.load('../600D_model_cbow/word2vec_model_600_cbow.model')
#     w2v_vocab = w2v_model.wv.vocab
#     print(w2v_vocab)
#     word_embedding_matrix = np.zeros((MAX_VOCAB, WORDEMBED_SIZE))
#     c = 0
#     for word in word2idx.keys():
#         if word in w2v_vocab:
#             c += 1
#             word_vector = w2v_model[word]
#             word_embedding_matrix[word2idx[word]] = word_vector
#     print("added", c, "vectors")
#     print(word_embedding_matrix)
#     return word_embedding_matrix
#
# get_embedding_matrix(word2idx)

# EMBEDDING_DIM = 256
# MAX_NB_WORDS = 5741
#
# tokenizer = Tokenizer(nb_words=MAX_NB_WORDS)
# tokenizer.fit_on_texts(texts)
# sequences = tokenizer.texts_to_sequences(texts)
# word_index = tokenizer.word_index
# print('Found %s unique tokens.' % len(word_index))
#

f = open(os.path.join('../600D_model_cbow/word2vec_model.txt'))
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print('Found %s word vectors.' % len(embeddings_index))

embedding_matrix = np.zeros((MAX_VOCAB, EMBEDDING_DIM))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector
print(word_index)
print(len(embedding_matrix))
