import tensorflow as tf
from pickle import load
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.utils import plot_model
from keras.models import Model, Sequential
from keras.layers import Input
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding
from keras.layers import Dropout
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from keras.layers import concatenate
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam
# from embedding import word_index, embedding_matrix
import numpy as np
from gensim.models import Word2Vec
import importlib
from keras.layers import Layer
# import keras-layer-zoo from parent directory
from  CapGenerator.attention import AttentionModel
import sys

from kulc.attention import ExternalAttentionRNNWrapper

sys.path.append("./..")
from kulc import attention, layer_normalization

# MAX_VOCAB = 4238
# WORDEMBED_SIZE = 200
#
EMBEDDING_DIM = 600

lstm_layers = 2
dropout_rate = 0.2
learning_rate = 0.001
import os


def get_embedding_matrix(MAX_VOCAB, word2idx):
    w2v_model = Word2Vec.load('../600D_model_cbow/word2vec_model_600_cbow.model')
    w2v_vocab = w2v_model.wv.vocab
    word_embedding_matrix = np.zeros((MAX_VOCAB, EMBEDDING_DIM))
    c = 0
    for word in word2idx.keys():
        if word in w2v_vocab:
            c += 1
            word_vector = w2v_model[word]
            word_embedding_matrix[word2idx[word]] = word_vector
    print("added", c, "vectors")
    print(word_embedding_matrix)
    return word_embedding_matrix


# convert a dictionary of clean descriptions to a list of descriptions
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
    print(tokenizer)
    return tokenizer


# calculate the length of the description with the most words
def max_length(descriptions):
    lines = to_lines(descriptions)
    return max(len(d.split()) for d in lines)


# create sequences of images, input sequences and output words for an image
def create_sequences(tokenizer, max_length, desc_list, photo):
    vocab_size = len(tokenizer.word_index) + 1

    X1, X2, y = [], [], []
    # walk through each description for the image
    for desc in desc_list:
        # encode the sequence
        seq = tokenizer.texts_to_sequences([desc])[0]
        # split one sequence into multiple X,y pairs
        for i in range(1, len(seq)):
            # split into input and output pair
            in_seq, out_seq = seq[:i], seq[i]
            # pad input sequence
            in_seq = pad_sequences([in_seq], maxlen=max_length)[0]
            # encode output sequence
            out_seq = to_categorical([out_seq], num_classes=vocab_size)[0]
            # store
            X1.append(photo)
            X2.append(in_seq)
            y.append(out_seq)
    return np.array(X1), np.array(X2), np.array(y)


# data generator, intended to be used in a call to model.fit_generator()
def data_generator(descriptions, photos, tokenizer, max_length, n_step=1):
    # loop for ever over images
    while 1:
        # loop over photo identifiers in the dataset
        keys = list(descriptions.keys())
        for i in range(0, len(keys), n_step):
            Ximages, XSeq, y = list(), list(), list()
            for j in range(i, min(len(keys), i + n_step)):
                image_id = keys[j]
                # retrieve the photo feature
                photo = photos[image_id][0]
                desc_list = descriptions[image_id]
                in_img, in_seq, out_word = create_sequences(tokenizer, max_length, desc_list, photo)
                for k in range(len(in_img)):
                    Ximages.append(in_img[k])
                    XSeq.append(in_seq[k])
                    y.append(out_word[k])
            yield [[np.array(Ximages), np.array(XSeq)], np.array(y)]


def categorical_crossentropy_from_logits(y_true, y_pred):
    y_true = y_true[:, :-1, :]  # Discard the last timestep
    y_pred = y_pred[:, :-1, :]  # Discard the last timestep
    loss = tf.nn.softmax_cross_entropy_with_logits(labels=y_true,
                                                   logits=y_pred)
    return loss


def categorical_accuracy_with_variable_timestep(y_true, y_pred):
    y_true = y_true[:, :-1, :]  # Discard the last timestep
    y_pred = y_pred[:, :-1, :]  # Discard the last timestep

    # Flatten the timestep dimension
    shape = tf.shape(y_true)
    y_true = tf.reshape(y_true, [-1, shape[-1]])
    y_pred = tf.reshape(y_pred, [-1, shape[-1]])

    # Discard rows that are all zeros as they represent padding words.
    is_zero_y_true = tf.equal(y_true, 0)
    is_zero_row_y_true = tf.reduce_all(is_zero_y_true, axis=-1)
    y_true = tf.boolean_mask(y_true, ~is_zero_row_y_true)
    y_pred = tf.boolean_mask(y_pred, ~is_zero_row_y_true)

    accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(y_true, axis=1),
                                               tf.argmax(y_pred, axis=1)),
                                      dtype=tf.float32))
    return accuracy


# embedding_matrix = get_embedding_matrix(word2idx)


# define the captioning model
def define_model(vocab_size, max_length, embedding_matrix):
    # feature extractor (encoder)
    inputs1 = Input(shape=(4096,))

    fe1 = Dropout(0.5)(inputs1)
    fe2 = Dense(EMBEDDING_DIM, activation='relu')(fe1)
    fe3 = RepeatVector(max_length)(fe2)

    # embedding
    inputs2 = Input(shape=(max_length,))
    emb2 = Embedding(vocab_size, EMBEDDING_DIM, weights=[embedding_matrix], mask_zero=True, trainable=False)(inputs2)

    image_features = TimeDistributed(Dense(EMBEDDING_DIM, activation="relu"))(inputs1)
    # merge inputs
    merged = concatenate([fe3, emb2])
    # language model (decoder)
    lm2 = LSTM(500, return_sequences=False)(merged)
    # lm3 = Dense(500, activation='relu')(lm2)
    attented_encoder = ExternalAttentionRNNWrapper(lm2, return_attention=True)

    outputs = TimeDistributed(Dense(vocab_size, activation='softmax'))(lm2)

    attented_encoder_training_data, _, _ , _= attented_encoder([emb2, image_features])
    training_output_data = outputs(attented_encoder_training_data)

    # tie it together [image, seq] [word]
    model = Model(inputs=[inputs1, inputs2], outputs=training_output_data)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    plot_model(model, show_shapes=True, to_file='model.png')
    return model

#
# def get_w2v_matrix(MAX_VOCAB, word_index):
#     embeddings_index = {}
#     f = open(os.path.join('../600D_model_cbow/word2vec_model_600_cbow.model'))
#     for line in f:
#         values = line.split()
#         word = values[0]
#         coefs = np.asarray(values[1:], dtype='float32')
#         embeddings_index[word] = coefs
#     f.close()
#
#     print('Found %s word vectors.' % len(embeddings_index))
#
#     embedding_matrix = np.zeros((MAX_VOCAB, EMBEDDING_DIM))
#     for word, i in word_index.items():
#         embedding_vector = embeddings_index.get(word)
#         if embedding_vector is not None:
#             # words not found in embedding index will be all-zeros.
#             embedding_matrix[i] = embedding_vector
#     print(word_index)
#     print(len(embedding_matrix))
#     return embedding_matrix
