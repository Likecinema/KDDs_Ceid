from kdds_project.File_Handler import Corpus
from kdds_project.LSH import LSH
from kdds_project.Range_tree import Range_tree
import time

start = time.time()
dims = 3
corpus: Corpus = Corpus("./rec.autos")
corpus.set_upper_bound(0.01)
corpus.set_lower_bound(0.1)
keywords = corpus.get_random_keywords(dims)
print("my random keywords are :", keywords)
my_rt = Range_tree(corpus, keywords)
my_lsh: LSH = LSH(my_rt, threshold=0.0001,num_hashes=15)
arr = my_rt.query()
data = my_lsh.run(arr)
end = time.time()
print("Time to run:", end-start)

