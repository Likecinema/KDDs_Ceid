from .File_Handler import Corpus, CorpusDocument
import pandas as pd

class Kd_tree:
    depth = -1
    i = -1
    leaves = []
    def __init__(self,*args):
        points = {}
        self.right = None
        self.left = None
        Kd_tree.depth += 1
        if len(args) == 2:
            corpus = args[0]
            dims = args[1]
            Kd_tree.i = Kd_tree.depth % dims
            for doc in corpus.documents:
                if sum(corpus.documents[doc].tf_idf_vector) != 0:
                    points[doc] = corpus.documents[doc].tf_idf_vector
            corp_df = pd.DataFrame(points)
            corp_df = corp_df.T
            self.KdTreeBuilder(corp_df, corpus, dims, self.i, self.depth)
        elif len(args) == 3:
            corp_df = args[0]
            corpus = args[1]
            dims = args[2]
            self.KdTreeBuilder(corp_df, corpus, dims, self.i, self.depth)
        else:
            print("Wrong number of arguments")

    def KdTreeBuilder(self, points_df, corpus, dims, i, depth):
        if depth < 100:
            if len(points_df.index) > 1:
                med = points_df[i].median()
                points_df1 = points_df[points_df[i] <= med]
                points_df2 = points_df[points_df[i] > med]
                self.left = Kd_tree(points_df1, corpus, dims)
                self.right = Kd_tree(points_df2, corpus, dims)
            elif len(points_df.index) == 1:
                doc = points_df.index[0]
                print(doc)
                self.leaves.append(corpus.documents[doc])
        else:
            for doc in points_df.index:
                self.leaves.append(corpus.documents[doc])
            return self.right, self.left
