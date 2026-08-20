# to process user input and forming it to simple form

import re

def preprocess(txt):

    # Lowercase
    txt = txt.lower()

    # Remove punctuation
    txt = re.sub(r'[^a-zA-Z0-9\s]', '', txt)

    # Remove extra spaces
    txt = re.sub(r"\s+", " ", txt).strip()

    return txt


# for testing purpose
# print(preprocess("Need Passport!!"))