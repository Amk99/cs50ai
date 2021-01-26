import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    
    model = dict()
    n = len(corpus)
    random_choice = (1 - damping_factor)/n
    for item in corpus[page]:
        probablity = damping_factor/len(corpus[page]) + random_choice
        model[item] = probablity
    for k in corpus.keys():
        if k in model.keys():
            continue
        else:
            probablity = (1 - damping_factor)/n
            model[k] = probablity              
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    main = list(corpus.keys())
    sample_corpus = transition_model(corpus, random.choice(main), DAMPING)
    sample = list(sample_corpus.keys())
    sample_weights = list(sample_corpus.values())
    corpus_list = []
    
    for _ in range(10000):
        draw = random.choices(sample, sample_weights, k=1)
        corpus_list.append(draw[0])
        sample_corpus = transition_model(corpus, draw[0], DAMPING)
        sample = list(sample_corpus.keys())
        sample_weights = list(sample_corpus.values())
        
    pagerank = dict()
    
    for ele in corpus_list:
        if ele in pagerank.keys():
            pagerank[ele] += 1
        else:
            pagerank[ele] = 1
            
    for ele in pagerank.keys():
        pagerank[ele] = pagerank[ele]/n
    
    return pagerank
        

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    fixed = (1 - damping_factor)/len(corpus)   
    
    """
    assign pagerank of 1/N to each page in corpus
    """
    for key in corpus.keys():
        pagerank[key] = 1/len(corpus)
            
    for i, j in corpus.items():
        if len(j) == 0:
            for a in corpus.keys():
                corpus[i].add(a)      
       
    for _ in range(1000):
        for ele in corpus.keys():
            #  calculate summation term
            summation = 0
            for i in Numlinks(corpus, ele):
                summation += pagerank[i]/len(corpus[i])
            pagerank[ele] = fixed + damping_factor * summation    
            
    return pagerank   
            
        
def Numlinks(corpus, page):
    numlink = [key for key, val in corpus.items() if page in val]
   
    return numlink     


if __name__ == "__main__":
    main()
