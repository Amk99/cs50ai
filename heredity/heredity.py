import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]
    
       
def get_parents(people, child, one_gene, two_gene):
    """
    Calculates number of genes parents have
    Returns a dictionary with 'mom' and 'dad' as keys and number of genes as value
    """    
    x = dict()
    if people[child]['mother'] != None:
        if people[child]['mother'] in one_gene:
            x['mom'] = (people[child]['mother'], 1)
        elif people[child]['mother']  in two_gene:
            x['mom'] = (people[child]['mother'], 2)
        else:
            x['mom'] = (people[child]['mother'], 0)   
    else:
        x['mom'] = (None, 0)
    
    if people[child]['father'] != None:
        if people[child]['father'] in one_gene:
            x['dad'] = (people[child]['father'], 1)
        elif people[child]['father'] in two_gene:
            x['dad'] = (people[child]['father'], 2)
        else:
            x['dad'] = (people[child]['father'], 0)          
    else:
        x['dad'] = (None, 0)
    
    return x   


def no_gene_probablity(person, parent_gene):
    """
    calculates probablity that a aperson has 0 copies of genes
    parent_gene is a tuple containing number of mother and father genes
    """
    if parent_gene == (None, None):
        return PROBS['gene'][0]
    if parent_gene == (0, 0):
        return (1 - PROBS['mutation']) * (1 - PROBS['mutation'])
    if parent_gene == (1, 0) or parent_gene == (0, 1):
        return 0.5 * (1 - PROBS['mutation'])
    if parent_gene == (1, 1):
        return 0.5 * 0.5
    if parent_gene == (2, 2):
        return (PROBS['mutation']) * (PROBS['mutation'])
    if parent_gene == (2, 0) or parent_gene == (0, 2):
        return 0.01 * 0.99  
    if parent_gene == (2, 1) or parent_gene == (1, 2):
        return PROBS['mutation'] * 0.5


def one_gene_probablity(person,parent_gene):
    """
    calculates probablity that a aperson has 1 copies of genes
    """
    if parent_gene == (None,None):
        return PROBS['gene'][1]
    if parent_gene == (0, 0):
        return ((1 - PROBS['mutation']) * (PROBS['mutation']))*2
    if parent_gene == (1, 0) or parent_gene == (0, 1):
        return 0.5*PROBS['mutation'] + 0.5 * (1 - PROBS['mutation'])
    if parent_gene == (1, 1):
        return 0.5 * 0.5 + 0.5 * 0.5
    if parent_gene == (2, 2):
        return ((PROBS['mutation']) * (1 - PROBS['mutation']))*2
    if parent_gene == (2, 0) or parent_gene == (0, 2):
        return (1 - PROBS['mutation']) * 0.99 + (PROBS['mutation'] * PROBS['mutation'])   
    if parent_gene == (2, 1) or parent_gene == (1, 2):
        return (1 - PROBS['mutation'])*0.5 + PROBS['mutation'] * 0.5

                
def two_gene_probablity(person, parent_gene):
    """
    calculates probablity that a aperson has 2 copies of genes
    """
    if parent_gene == (None, None):
        return PROBS['gene'][2]
    if parent_gene == (0, 0):
        return (PROBS['mutation']) * (PROBS['mutation'])
    if parent_gene == (1, 0) or parent_gene == (0, 1):
        return  0.5 * (PROBS['mutation'])
    if parent_gene == (1, 1):
        return 0.5 * 0.5
    if parent_gene == (2, 2):
        return (1 - PROBS['mutation']) * (1 - PROBS['mutation'])
    if parent_gene == (2, 0) or parent_gene == (0, 2):
        return (1 - PROBS['mutation']) * PROBS['mutation']  
    if parent_gene == (2, 1) or parent_gene == (1, 2):
        return (1 - PROBS['mutation']) * 0.5 

  
def get_parent_gene(x):
    if x['mom'][0] != None and x['dad'][0] != None:
        return (x['mom'][1], x['dad'][1])
    elif x['mom'][0] == None and x['dad'][0] == None:
        return (None, None)
    else:
        return (x['mom'][1], x['dad'][1])                              
                
 
    

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    result = 1
    for ele in people.keys():
        x = get_parents(people, ele, one_gene, two_genes)
        parent_gene = get_parent_gene(x)
        if ele in one_gene:
            a = one_gene_probablity(ele, parent_gene)
            if ele in have_trait:
                p = a * PROBS['trait'][1][True]
            else:
                p = a * PROBS['trait'][1][False]   
            result = result * p     
                
        elif ele in two_genes:
            a = two_gene_probablity(ele, parent_gene)
            if ele in have_trait:
                q = a * PROBS['trait'][2][True]
            else:
                q = a * PROBS['trait'][2][False]    
            result = result * q  
            
        else:
            a = no_gene_probablity(ele, parent_gene) 
            if ele in have_trait:
                r = a * PROBS['trait'][0][True]
            else:
                r = a * PROBS['trait'][0][False]       
            result = result * r
    
    return result


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for ele in probabilities.keys():
        if ele in one_gene:
            probabilities[ele]['gene'][1] += p
        elif ele in two_genes:
            probabilities[ele]['gene'][2] += p
        elif ele not in one_gene and ele not in two_genes:
            probabilities[ele]['gene'][0] += p    
            
        if ele in have_trait:
            probabilities[ele]['trait'][True] += p 
        else:
            probabilities[ele]['trait'][False] += p 


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for ele in probabilities:
        gene_sum = probabilities[ele]['gene'][0] + probabilities[ele]['gene'][1] + probabilities[ele]['gene'][2]
        trait_sum = probabilities[ele]['trait'][True] + probabilities[ele]['trait'][False]
        probabilities[ele]['gene'][0] /= gene_sum
        probabilities[ele]['gene'][1] /= gene_sum
        probabilities[ele]['gene'][2] /= gene_sum
        probabilities[ele]['trait'][True] /= trait_sum
        probabilities[ele]['trait'][False] /= trait_sum

if __name__ == "__main__":
    main()
