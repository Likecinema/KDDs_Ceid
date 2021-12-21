from .File_Handler import CorpusDocument
from typing import OrderedDict

class Tree():
    def __init__(self):
        self.leaves = None
        self.nodes = None
        self.left = None
        self.right = None
        self.keywords = None
        self.value = None
    def __add__(self, other):
        if isinstance(other, Tree):
            return self.value + other.value
        elif isinstance(other, float):
            return self.value + other
        elif isinstance(other, CorpusDocument):
            return self.value + other.tf_idf
        elif isinstance(other, list):
            return self.value + other[0].value
        else:
            return TypeError("RTNode add supports only RTNode. CorpusDocument and float")
    def __lt__(self, other):
        if (isinstance(other, Tree)):
            return True if self.value < other.value else False
    def __gt__(self, other):
        if (isinstance(other, float)):
            return True if float(self.value) > float(other) else False
        if (isinstance(other, int)):
            return True if float(self.value) > float(other) else False
    def __ge__(self, other):
        if (isinstance(other, Tree)):
            return True if self.value >= other.value else False
    def __sub__(self, other:object):
        if (isinstance (other, Tree)):
            return self.value - other.value


class Range_tree(Tree):
    """
    Range Tree implementation.
    - Consists of multiple Binary search trees, that consist of multiple BSTNodes. (more info on BSTNode class)
    - This tree is not balanced in any way
    """
    def __init__(self,corpus, keywords, reverse=False):
        super().__init__()
        BSTs = []
        self.corpus = corpus
        """The corpus in question"""
        self.keywords = keywords
        """ An array of keywords needed to create the Range Tree"""
        for keyword in keywords:
            test3 = RTNode(keyword=keyword)
            corpus.set_keyword(keyword)
            corpus.set_tfidf(keyword)
            test2 = OrderedDict(sorted(corpus.documents.items(),key=lambda item: item[1].tf_idf, reverse=reverse))
            test2 = [test2[x] for x in test2]
            test3 = test3.bottom_up_create(test2)
            tree_leaves = []
            test3.get_leaves(tree_leaves)
            test3.set_leaves(sorted(tree_leaves, key=lambda item: item.tf_idf))
            BSTs.append(test3)
        for i in range(len(BSTs)-1):
            BSTs[i].replace_leaves(BSTs[i+1])
        self.leaves = BSTs[0].leaves
        self.left = BSTs[0].left
        self.right = BSTs[0].right
        self.keyword = BSTs[0].keyword
        self.value = BSTs[0].value


    def query(self) -> list:
        """Queries all the keywords used to create the Range Tree. Basically finds CorpusDocuments
        That have all "keywords" in common."""
        leaf_arr = []
        self._hidden_query(self, leaf_arr, self.keywords)
        self.leaves_after_query = leaf_arr
        return leaf_arr

    def _hidden_query(self, node: Tree, arr:list, keywords: list):
        if isinstance(node.left, Tree)  and node.left > 0:
            self._hidden_query(node.left, arr, keywords)
        if isinstance(node.right, Tree) and (node.right > 0):
            self._hidden_query(node.right, arr, keywords)
        if type(node.left) is CorpusDocument and node.left > 0.00:
            if (node.left.keyword in keywords) and node.left.id not in [x.id for x in iter(arr)]:
                arr.append(node.left)
        if (type(node.right) is CorpusDocument) and (node.right > 0.00):
            if (node.right.keyword in keywords) and node.right.id not in [x.id for x in iter(arr)]:
                arr.append(node.right)

class RTNode(Range_tree):
    """
    Represents a Range Tree node, basically a Binary Search Tree node. Smaller tf_idf values go to the left, greater go to the right
    For all intents and purposes, a leaf is a node that's a CorpusDocument
    """
    def __init__(self,nodes = None, keyword = None):
        self.leaves = []
        """All the leaves of the current node."""
        self.nodes = nodes
        self.left = None
        """Node to the left"""
        self.right = None
        """Node to the right"""
        if (isinstance(self.nodes, list)):
            self.left = self.nodes[0]
            self.right = self.nodes[len(self.nodes)-1]
        self.keyword = keyword
        """Based on what keyword this node was created for"""
        if (self.left is not None and self.right is not None):
            self.value = self.right + (self.left -self.left) if self.right >= self.left else self.left + (self.right - self.right)
        elif self.left is not None:
            if (isinstance(self.left, (CorpusDocument))):
                self.value = self.left.tf_idf
                return
            self.value = self.left
        elif self.right is not None:
            if(isinstance(self.right, CorpusDocument)):
                self.value = self.right.tf_idf
                return
            self.value = self.right

    def bottom_up_create(self, li: list):
        """ Takes a list of sorted CorpusDocuments and creates what is finally a Binary Search tree from the bottom up.
            Much faster than inserting
        """
        while len(li)>1:
            first = li.pop(0)
            second = li.pop(0)

            #if even number of docs
            if (type(first) ==  type(second)):
                li.append(RTNode([first,second], keyword=self.keyword))
            else: #if odd number of docs
                li.append(RTNode([first], keyword=self.keyword))
                li.insert(0,second)
        return li[0]
    
    def get_leaves(self, vals):
        """
        Returns all leaves. Takes advantage of pythons "passed-by-refference" attitude on parameters, so output is the argument "vals"
        """
        if type(self.left) is not CorpusDocument and type(self.left) is not None:
            self.left.get_leaves(vals)
        if (type(self.right) is not CorpusDocument) and (self.right != None):
            self.right.get_leaves(vals)
        if type(self.left) is CorpusDocument:
            vals.append(self.left)
        if type(self.right) is CorpusDocument:
            vals.append(self.right)
    def set_leaves(self, vals):
        self.leaves = vals
    def replace_leaves(self, tree):
        """
        Replaces the leaves with a given Tree. Basically turns a Binary Search Tree into a range tree.
        """
        if type(self.left) is not CorpusDocument and type(self.left) is not None:
            self.left.replace_leaves(tree)
        if (type(self.right) is not CorpusDocument) and (self.right is not None):
            self.right.replace_leaves(tree)
        if type(self.left) is CorpusDocument:
            self.left = tree
        if type(self.right) is CorpusDocument:
            self.right = tree