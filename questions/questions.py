
import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)
 
    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    topics = dict()
    direc = str(directory)
    path = os.path.join(direc)
    
    for file in os.listdir(path):
        file_loc = os.path.join(path, file)
        with open(file_loc, 'r', encoding='utf8') as f:
            val = f.read()
        topics[str(file)] = val        
    return topics


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    punctuation = string.punctuation
    stop_words = nltk.corpus.stopwords.words("english")

    words = nltk.word_tokenize(document.lower())
    words = [word for word in words if word not in punctuation and word not in stop_words]

    return words
        

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    total_documents = len(documents)
    counter = dict()
    
    for key, val in documents.items():
        for word in set(val):
            if word in counter:
                counter[word] += 1
            else:
                counter[word] = 1
            
    idf = dict()
    for ele in counter.keys():
        x = total_documents/counter[ele]
        idf[ele] = 0.001 + math.log(x)
    
    return idf                   


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = dict()  # dict with file names and sum of their idf values
    
    for key, val in files.items():
        tf_idfs[key] = 0
        for ele in query:
            if ele in val:
                count = val.count(ele) + 0.001
            else:
                count = 0.001
            tf = count / len(val)
            if ele in idfs.keys():
                idf = idfs[ele]
            else:
                idf = 0.001
            tf_idfs[key] += idf * tf    
                    
    sorted_dict = dict(sorted(tf_idfs.items(), key=lambda item: item[1],reverse=True))    
    tf_idf = list(sorted_dict.keys())
    
    return tf_idf[:n]                  
                        
                            
def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_scores = dict()
    
    for key, val in sentences.items():
        sentence_scores[key] = 0
        for ele in query:
            if ele in val:
                sentence_scores[key] += idfs[ele]
                
    s = sorted(sentence_scores, key=lambda x: (sentence_scores[x], density(x, query)), reverse=True)
    return s[:n]          
                

def density(s, q):
    count = 0
    for ele in s.split():
        if ele in q:
            count += 1
    
    return count/len(s.split())             


if __name__ == "__main__":
    main()

