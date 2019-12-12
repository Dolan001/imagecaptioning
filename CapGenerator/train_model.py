import load_data as ld
import generate_model as gen
from keras.callbacks import ModelCheckpoint
from pickle import dump


def train_model(weight=None, epochs=10):
    # load dataset
    data = ld.prepare_dataset('train')
    train_features, train_descriptions = data[0]
    test_features, test_descriptions = data[1]
    print(len(train_descriptions))

    # prepare tokenizer
    tokenizer = gen.create_tokenizer(train_descriptions)
    # save the tokenizer
    dump(tokenizer, open('../att_model/tokenizer.pkl', 'wb'))
    # index_word dict
    index_word = {v: k for k, v in tokenizer.word_index.items()}
    print(index_word , 'index word')
    # save dict
    dump(index_word, open('../att_model/index_word.pkl', 'wb'))

    vocab_size = len(index_word) + 1

    print('Vocabulary Size: %d' % vocab_size)

    # determine the maximum sequence length
    max_length = gen.max_length(train_descriptions)
    print('Description Length: %d' % max_length)
    embedding_matrix = gen.get_embedding_matrix(vocab_size, tokenizer.word_index)

    # generate model
    model = gen.define_model(vocab_size, max_length, embedding_matrix)

    # Check if pre-trained weights to be used
    if weight != None:
        model.load_weights(weight)

    # define checkpoint callback
    filepath = '../att_model/model-ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5'
    checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1,
                                 save_best_only=True, mode='min')

    steps = len(train_descriptions)
    val_steps = len(test_descriptions)
    # create the data generator
    train_generator = gen.data_generator(train_descriptions, train_features, tokenizer, max_length)
    val_generator = gen.data_generator(test_descriptions, test_features, tokenizer, max_length)

    # fit model
    model.fit_generator(train_generator, epochs=epochs, steps_per_epoch=steps, verbose=1,
                        callbacks=[checkpoint], validation_data=val_generator, validation_steps=val_steps)

    try:
        model.save('../att_model/wholeModel.h5', overwrite=True)
        model.save_weights('../att_model/weights.h5', overwrite=True)
    except:
        print("Error in saving model.")
    print("Training complete...\n")


if __name__ == '__main__':
    train_model(epochs=20)
