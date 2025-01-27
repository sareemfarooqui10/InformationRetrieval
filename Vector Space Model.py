# -*- coding: utf-8 -*-
"""IR Assignment 02 21K-3381

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17CvzER3yqxmrAu0R4d8q_mFdbFDwiQAQ
"""

import os
import math
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from google.colab import drive
drive.mount('/content/drive')
import nltk
nltk.download("stopwords")
import pandas as pd
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
# Function to preprocess text
def preprocess_text(text):
    # Tokenization, case folding, stop-words removal, and stemming
    tokens = word_tokenize(text.lower())
    filtered_tokens = [stemmer.stem(token) for token in tokens if token.isalnum() and token not in stop_words]
    return filtered_tokens
# Function to calculate TF-IDF values
def calculate_tfidf(documents):
    tf = defaultdict(lambda: defaultdict(int))
    idf = defaultdict(int)
    N = len(documents)
    # Calculate term frequencies (TF)
    for doc_id, document in enumerate(documents):
        term_freq = defaultdict(int)
        for term in document:
            term_freq[term] += 1

        max_freq = max(term_freq.values())

        for term, freq in term_freq.items():
            tf[doc_id][term] = 0.5 + 0.5 * (freq / max_freq)  # Normalize TF
    # Calculate inverse document frequency (IDF)
    for doc_id, document in enumerate(documents):
        for term in set(document):
            idf[term] += 1

    for term, doc_freq in idf.items():
        idf[term] = math.log(N / doc_freq)

    return tf, idf
# Function to convert documents into TF-IDF vectors
def create_tfidf_vectors(documents, tf, idf):
    vectors = []
    for doc_id, document in enumerate(documents):
        vector = []
        for term in sorted(set(document)):
            vector.append(tf[doc_id][term] * idf[term])
        vectors.append(vector)
    return vectors
# Function to calculate cosine similarity
def cosine_similarity(vector1, vector2):
    dot_product = sum(x * y for x, y in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(x ** 2 for x in vector1))
    magnitude2 = math.sqrt(sum(y ** 2 for y in vector2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)
# Function to filter results based on threshold
def filter_results(results, threshold):
    return [result for result in results if result[1] >= threshold]
# Read documents from drive
def read_documents_from_directory(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r", encoding="latin-1") as file:
                text = file.read()
                documents.append(preprocess_text(text))
    return documents

# Main function
def main():
    # Directory containing documents
    documents_directory = "/content/ResearchPapers"
    documents = read_documents_from_directory(documents_directory)
    tf, idf = calculate_tfidf(documents)
    document_vectors = create_tfidf_vectors(documents, tf, idf)

    query = input("Enter your query: ")
    preprocessed_query = preprocess_text(query)

    # Create TF-IDF vector for query
    query_vector = []
    for term in sorted(set(preprocessed_query)):
        if term in idf:
            query_vector.append((0.5 + 0.5 * (preprocessed_query.count(term) / len(preprocessed_query))) * idf[term])
        else:
            query_vector.append(0)

    # Calculate cosine similarity between query and documents
    results = [(i, cosine_similarity(query_vector, document_vectors[i])) for i in range(len(document_vectors))]
    threshold = 0.05
    filtered_results = filter_results(results, threshold)
    print("Filtered results:")
    for doc_id, similarity in filtered_results:
        print(f"Document {doc_id}: Similarity = {similarity}")

if __name__ == "__main__":
    main()