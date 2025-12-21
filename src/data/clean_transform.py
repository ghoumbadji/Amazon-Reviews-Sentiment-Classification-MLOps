"""
Download raw data from S3 and clean it locally.
"""

import string
import pandas as pd
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import boto3


# Download stopwords
nltk.download("stopwords")

# Download packages for lemmatization purposes
nltk.download("punkt_tab")
nltk.download("wordnet")
nltk.download("omw-1.4")
nltk.download("averaged_perceptron_tagger_eng")

# Initialize Lemmatizer
lemmatizer = WordNetLemmatizer()

# Load stopwords once (keep negation)
stop_words = set(stopwords.words("english"))
stop_words.discard("not")

# Define translator to use for punctuation
translator = str.maketrans("", "", string.punctuation)



def get_wordnet_pos(tag):
    """Map NLTK POS tags to WordNet POS tags"""
    if tag.startswith("J"):
        return wordnet.ADJ
    if tag.startswith("V"):
        return wordnet.VERB
    if tag.startswith("N"):
        return wordnet.NOUN
    if tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN  # default fallback


def lemmatize(tokens):
    """Lemmatization with POS tagging"""
    pos_tags = nltk.pos_tag(tokens)
    return [
        lemmatizer.lemmatize(word, get_wordnet_pos(tag))
        for word, tag in pos_tags
    ]


def clean_text(text):
    """Full preprocessing pipeline for a given text"""
    # 1. Lowercase
    text = text.lower()
    # 2. Remove punctuation
    text = text.translate(translator)
    # 3. Tokenize
    tokens = word_tokenize(text)
    # 4. Lemmatize
    tokens = lemmatize(tokens)
    # 5. Remove stopwords (except "not")
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)


def process_data(bucket_name, input_key, local_input, local_output):
    """Get raw data from S3 and clean it."""
    s3 = boto3.client("s3")
    # 1. Download from S3
    print(f"Downloading raw data from S3 bucket {bucket_name}...")
    s3.download_file(bucket_name, input_key, local_input)
    # 2. Load and Clean
    print("Loading data...")
    df = pd.read_parquet(local_input)
    df["content"] = df["title"] + " " + df["content"]
    df.drop("title", axis=1, inplace=True)
    df["content"] = df["content"].apply(clean_text)
    # 3. Save locally as Parquet
    df.to_parquet(local_output, index=False)
    print(f"Cleaned data saved locally: {local_output}")
    print(f"Preview:\n{df.head()}")
