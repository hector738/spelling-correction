"""Manager data preprocess"""

import re
import html
import string
import unicodedata
import numpy as np


def text_standardize(txt):
    """Organize/add spaces around punctuation marks"""

    if txt is None:
        return ""

    txt = html.unescape(txt).replace("\\n", "").replace("\\t", "")
    txt = txt.translate(str.maketrans({c: f" {c} " for c in string.punctuation}))
    txt = " " + " ".join(txt.split()) + " "

    # replace contractions and simple quotes (preserve order)
    keys = [["«", ""], ["»", ""], ["�", ""],
            ["”", " \" "], ["“", " \" "],
            [" ' ' ", " ' "], [". '", ".  '"],
            ["' s ", "'s "], [" 's", "'s"],
            ["' d ", "'d "], [" 'd", "'d"],
            ["' m ", "'m "], [" 'm", "'m"],
            ["' ll ", "'ll "], [" 'll", "'ll"],
            ["' ve ", "'ve "], [" 've", "'ve"],
            ["' re ", "'re "], [" 're", "'re"],
            ["n ' t ", "n't "], [" n't", "n't"],
            ["o ' c ", "o'c "], [" o'c", "o'c"],
            [" ' ", " "], ["''", "'"],
            [" '", ""], ["' ", ""]]

    for i in range(len(keys)):
        txt = txt.replace(keys[i][0], keys[i][1])

    txt = " ".join(txt.strip("'").split())

    return txt


def split_by_max_length(sentence, max_text_length=128):
    """Standardize n_sentences: split long n_sentences into max_text_length"""

    tolerance = 5
    new_n_sentences = []

    if len(sentence) < max_text_length - tolerance:
        new_n_sentences.append(sentence)
    else:
        splitted = sentence.split()
        text = []

        for x in splitted:
            text_temp = " ".join(text)

            if len(text_temp) + len(x) < max_text_length:
                text.append(x)
            else:
                new_n_sentences.append(text_temp)
                text = [x]

        text_temp = " ".join(text)

        if len(text_temp) > tolerance:
            new_n_sentences.append(text_temp)

    return new_n_sentences


def add_noise(sentences, max_text_length, amount_noise=0.8):
    """Generate some artificial spelling mistakes (or not) in the sentences"""

    chars = list(" " + string.ascii_letters + string.digits)
    n_sentences = []

    assert(0.0 <= amount_noise <= 1.0)

    for x in sentences:
        if len(x) > 2:
            prob = 0.1 if len(x) <= 5 else amount_noise

            if np.random.rand() <= prob:
                # Delete characters...
                delete_rand = np.random.rand()
                sentence = x

                if delete_rand <= 0.8:
                    # by repeat characters
                    x = re.compile(r'(.)\1{1,}', re.IGNORECASE).sub(r'\1', x)

                if sentence == x:
                    # by random characters
                    random_index = np.random.randint(len(x))
                    x = x[:random_index] + x[random_index + 1:]

            if np.random.rand() <= prob:
                # Replace characters...
                add_rand = np.random.rand()
                sentence = x

                # if add_rand <= 0.1:
                if add_rand <= 0.2:
                    # by accentuation
                    x = unicodedata.normalize("NFKD", x).encode("ASCII", "ignore").decode("ASCII")

                # if sentence == x and add_rand <= 0.2:
                if sentence == x and add_rand > 0.2:
                    # by random characters
                    random_index = np.random.randint(len(x))
                    x = x[:random_index] + np.random.choice(chars) + x[random_index + 1:]

            if np.random.rand() <= prob:
                # Add a random character
                random_index = np.random.randint(len(x))
                x = x[:random_index] + np.random.choice(chars) + x[random_index:]

            if np.random.rand() <= prob:
                # Transpose 2 random characters
                random_index = np.random.randint(len(x) - 1)
                x = x[:random_index] + x[random_index + 1] + x[random_index] + x[random_index + 2:]

        x = text_standardize(x)
        n_sentences.append(x)

    return n_sentences
