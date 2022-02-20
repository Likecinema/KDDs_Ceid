from .File_Handler import Corpus, CorpusDocument
from typing import OrderedDict
from sklearn.decomposition import PCA

class Rectangle():
    def __init__(self, center:list=[0, 0], half_dim:float=0):
        self.center:list = center
        self.half_dim:float = half_dim
    def contains_point(self,point:list)->bool:
        return (
                point[0] >= (self.center[0] - self.half_dim) and
                point[0] <= (self.center[0] + self.half_dim) and
                point[1] >= (self.center[1] - self.half_dim) and
                point[1] <= (self.center[1] + self.half_dim)
                )
    def intersects(self, rect:'Rectangle')->bool:
        return (not 
        (
            rect.center[0] - rect.half_dim > self.center[0] + self.half_dim or
            rect.center[0] + rect.half_dim < self.center[0] - self.half_dim or
            rect.center[1] - rect.half_dim > self.center[1] + self.half_dim or
            rect.center[1] - rect.half_dim > self.center[1] + self.half_dim))
class Quad_tree():
    """Represents a Quad tree. Quad trees have to have a 2d point as input"""
    #def __init__(self,corpusDocument:CorpusDocument=None, keywords:list=None, max_capacity:int = 8, corpus:Corpus=None):
    def __init__(self, max_capacity=4, boundary:Rectangle = Rectangle(), corpus:Corpus= None, keywords:list = None):
        self.max_capacity = max_capacity
        self.max_value = None
        self.south_east:Quad_tree = None
        self.south_west:Quad_tree = None
        self.north_east:Quad_tree = None
        self.north_west:Quad_tree = None
        self.corpus = corpus
        self.keywords = keywords
        self.docs = []
        self.boundary:Rectangle = boundary

    def insert(self, val: CorpusDocument)->bool:
        if not self.boundary.contains_point(val.tf_idf_vector):
            return False
        if len(self.docs) < self.max_capacity:
            self.docs.append(val)
            return True
        if self.north_west == None:
            self.subdivide()
        if (self.north_west.insert(val)):
            return True
        if (self.north_east.insert(val)):
            return True
        if (self.south_west.insert(val)):
            return True
        if (self.south_east.insert(val)):
            return True
    
    def subdivide(self):
        x = self.boundary.center[0]
        y = self.boundary.center[1]
        half_dim = self.boundary.half_dim
        self.north_west=Quad_tree(boundary=Rectangle([x+half_dim/2, half_dim/2], half_dim/2))
        self.north_east=Quad_tree(boundary=Rectangle([x-half_dim/2, half_dim/2], half_dim/2))
        self.south_west=Quad_tree(boundary=Rectangle([y+half_dim/2, half_dim/2], half_dim/2))
        self.south_east=Quad_tree(boundary=Rectangle([y-half_dim/2, half_dim/2], half_dim/2))

    def query(self, range_val = Rectangle([1,1],2), docs = [])->list:
        docs = []
        if (not (self.boundary.intersects(range_val))):
            return docs
        for item in self.docs:
            if range_val.contains_point(item.tf_idf_vector):
                docs.append(item)
        if self.north_west == None:
            return docs
        docs = docs + self.north_west.query(range_val, docs)
        docs = docs + self.north_east.query(range_val, docs)
        docs = docs + self.south_west.query(range_val, docs)
        docs = docs + self.south_east.query(range_val, docs)
        return docs

    def mass_insert(self)->bool:
        self.corpus.set_tf_idf_vector(self.keywords,2)
        min_value = 100000
        max_value = -10
        for i in range(len(self.corpus.documents)):
            for item in self.corpus[i].tf_idf_vector:
                if item > max_value:
                    max_value = item
                if item < min_value:
                    min_value = item
        self.max_value=max_value
        self.boundary = Rectangle([min_value,min_value], max_value)
        for i in range(len(self.corpus.documents)):
            self.insert(self.corpus[i])
