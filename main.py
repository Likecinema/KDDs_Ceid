from kdds_project.File_Handler import Corpus, CorpusDocument
from kdds_project.LSH import LSH
from kdds_project.Quad_tree import Quad_tree, Rectangle
from kdds_project.Range_tree import Range_tree
from kdds_project.R_tree import R_tree, Bounding_box
from kdds_project.Kd_tree import Kd_tree
import time

#Για πληροφορίες configuration του αρχείου δείτε το demo_HowToRun.txt

#start
start = time.time()
corpus: Corpus = Corpus("./rec.autos")
rect_to_avoid = 1
corpus.set_upper_bound(0.01)
corpus.set_lower_bound(0.1)

keywords = ['geico', 'lidar', 'claim', 'history']
try: 
    dims = len(keywords)
except:
    dims = 4
    keywords = corpus.get_random_keywords(dims)

print("my random keywords are :", keywords)
corpus.set_tf_idf_vector(keywords, len(keywords)) 

#tree and LSH initialization
my_qt = Quad_tree(corpus=corpus, keywords=keywords)
my_range_tree = Range_tree(corpus, keywords)
my_lsh: LSH = LSH(my_range_tree, threshold=0.5,num_hashes=15)
#my_r_tree: R_tree = R_tree(corpus=corpus, keywords=keywords)
my_kd_tree: Kd_tree = Kd_tree(corpus, dims)

#insertions
#my_r_tree.mass_insert()
my_qt.mass_insert() #this has to be the last insert
val = (my_qt.max_value/2) + rect_to_avoid

#queries
arr4 = my_kd_tree.leaves
#arr3 = my_r_tree.query(Bounding_box([0.5, 0.5, 0.5, 0.5], [500,500,5000,500]))
arr = my_range_tree.query()
arr2 = my_qt.query(range_val=Rectangle([val, val], val))

#LSH runs
print('Jaccard Similarities using range tree + LSH:')
data = my_lsh.run(arr)
print('Jaccard Similarities using quad tree + LSH:')
data2 = my_lsh.run(arr2)
#data3 = my_lsh.run(arr3)
print('Jaccard Similarities using Kd tree + LSH:')
data4 = my_lsh.run(arr4)
end = time.time()
print("Time to run:", end-start)

