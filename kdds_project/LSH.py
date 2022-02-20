from collections import namedtuple
from random import randint
from .Range_tree import Tree
from .File_Handler import CorpusDocument
import binascii
#a good portion if this implementation is a modified version of
#code shown in article https://mccormickml.com/2015/06/12/minhash-tutorial-with-python-code/
#and github repo https://github.com/chrisjmccormick/MinHash/tree/master/ . It is MIT Licenced
class LSH:
    """
    LSH implemantation in python. If you dont care just construct and then LSH.run()"""
    def __init__(self, tree: Tree, threshold=0.5, num_hashes = 10):
        """        
        - `tree: Tree`
            any type of tree
        - `num_hashes`
            Number of unique hash functions (default 10)
        - `threhold`: threshold for comparisons
        """
        self.data = tree
        self.keywords = tree.keywords
        self.leaves_after_query = None
        self.num_hashes = num_hashes
        self.threshold = threshold
        self.estJSim = None


    def calculate_shingles(self, item: CorpusDocument,k:int=2):
        """ Calculates all k-gram shingles for a given CorpusDocument.Returns it as a list"""
        text = item.words
        return ((binascii.crc32(' '.join(text[i:i+k]).encode('utf8')) & 0xffffffff for i in range(len(text) - k + 1)))

    def min_hash(self, num_hashes:int = 5):
        """
        Takes a CorpusDocument list, then calculates min_hash value for all 
        the k-gram shingles for it. num_hashes is the number of unique
        hash functions min_hash will use"""
        shingle_dict = {}
        signatures = []
        for item in self.leaves_after_query:
            shingle_dict[item.id] = self.calculate_shingles(item)
        max_shingle_id = 2**32-1
        next_prime = 4294967311
        if (max_shingle_id < len(self.leaves_after_query)):
            raise ValueError("Too many documents")
        coeff_a = self.pick_random_coeffs(self.num_hashes, len(shingle_dict))
        coeff_b = self.pick_random_coeffs(self.num_hashes, len(shingle_dict))
        for key in shingle_dict.keys():
            signature = []
            for i in range(0, num_hashes):
                min_hash_code = next_prime+1
                shingle_id_set = shingle_dict[key]
                shingle_id_set = list(dict.fromkeys(shingle_id_set))
                for shingle_id in shingle_id_set:
                    hash_code = (coeff_a * shingle_id + coeff_b) % next_prime
                    if hash_code < min_hash_code:
                        min_hash_code = hash_code
                    signature.append(min_hash_code)
            signatures.append(signature)
        return signatures

    def pick_random_coeffs(self, x, max_shingle_id):
        """Picks random coefficients for h(x) = ax+b"""
        rand_list = []
        while x > 0:
            rand_index = randint(0, max_shingle_id)
            while rand_index in rand_list:
                rand_index = randint(0, max_shingle_id)
            rand_list.append(rand_index)
            x = x - 1
            return rand_list[0]

    def get_triangle_index(self, i:int, j:int):
        """An 1D representation of a 2D array."""
        if i == j:
            return ValueError("Triangle matrix cant have i == j")
        if j < i:
            temp = i
            i = j
            j = temp
        leave_len = len(self.leaves_after_query)
        k = int(i * (leave_len - (i + 1) / 2.0) + j - i) - 1
        return k
    def compare_signatures(self, arr):
        """Checks if a signature on a given document matches an input signature (arr)"""
        self.estJSim = [0 for _ in range(len(self.leaves_after_query)**2)]
        signatures = arr
        for i in range(0,len(self.leaves_after_query)-1):
            signature1 = signatures[i]
            for j in range(i+1, len(self.leaves_after_query)-1):
                signature2 = signatures[j]
                count = 0
                for k in range(0, self.num_hashes):
                    count = count + (signature1[k] == signature2[k])
                test = self.get_triangle_index(i,j)
                if float(count) != 0.0:
                    self.estJSim[test] = float(count/self.num_hashes)
    
    def find_similarities(self):
        """Finds and prints similarities between documents. If a given similarity is above the threshold, calculates intersection/union"""
        if (len(self.leaves_after_query) == 0):
            print("No matches found")
            return
        if all([v == 0 for v in self.estJSim]):
            print("No similar documents")
            return
        no_threshold = []
        print("\nList of Document Pairs with J(d1,d2) more than", self.threshold)
        print("Values shown are the estimated Jaccard similarity and the actual")
        print("Jaccard similarity.\n")
        print("                   Est. J   Act. J")
        for i in range(0, len(self.leaves_after_query)):  
            for j in range(i + 1, len(self.leaves_after_query)):
                # Retrieve the estimated similarity value for this pair.
                estJ = self.estJSim[self.get_triangle_index(i, j)]
                # If the similarity is above the threshold...
                #if estJ < self.threshold and estJ is not 0:
                #    no_threshold.append(str(self.leaves_after_query[i].id) +" ---> "+ str(self.leaves_after_query[j].id) + 
                #    " has similarity but not over threshold. Similarity is " + str(estJ))
                if estJ > self.threshold:
                # Calculate the actual Jaccard similarity for validation.
                    s1 = set(self.calculate_shingles(self.leaves_after_query[i]))
                    s2 = set(self.calculate_shingles(self.leaves_after_query[j]))
                    test = s1.intersection(s2)
                    test2 = s1.union(s2)
                    J = (len(s1.intersection(s2)) / len(s1.union(s2)))
                    # Print out the match and similarity values with pretty spacing.
                    print(str(self.leaves_after_query[i].id)+" -->  "+str(self.leaves_after_query[j].id)+"   "+str(round(estJ,2))+"     "+str(round(J,2)))
        for item in no_threshold:
            print(item)         
      

    def run(self, arr):
        self.leaves_after_query = arr
        arr2 = self.min_hash()
        self.compare_signatures(arr2)
        self.find_similarities()
    

# Display true positive and false positive counts.
