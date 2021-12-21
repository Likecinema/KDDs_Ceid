from typing import OrderedDict, Type
from os import listdir
from os.path import isfile, join
from random import randint
import math
from os import error
import collections


class Document:
    """
    Represents a document.
    """
    def __init__(self, file_path: str):
        """Constructor. Example usage: test_doc = Document('/path/to/file)"""
        try:
            self.text = open(file_path,'r').read()
            self.text = self.text.lower() #sanitize
        except error:
            raise ValueError("File does not exist or is not readable")
        self.tf: dict = collections.defaultdict(int)
        """ A dictionary which has the term as a key and its term frequency as a value"""
        self.words = self.text.split()
        """list of unique words the document has."""
        self.words = [word.strip('.,!;:()|~\-@#$%^&*[]>\{\}?<') for word in self.words]
        self.words = [word.replace('\'s', '') for word in self.words]
        for word in self.words:
            self.tf[word] += 1
    def unique(self) -> list:
        """
        Returns all unique words as a list
        """
        return list(self.tf.keys())
    
class CorpusDocument(Document):
    """
    Extends the Document class. Adds `keyword` and `id` attributes which is something you might wanna use in search
    You can also append tf_idf values for every word in document by calling set_tfidf in Corpus
    This class supports `>` , `<` , `==` , `>=` , `<=` , `+` operator overloading
    """
    def __init__(self, path, keyword=None, id=None):
        super().__init__(path)
        self.vector: list = []
        self.keyword = keyword
        self.tf_idf = None
        self.id = id
    def __gt__(self, other: object):
        if (isinstance(other, self.__class__)):
            if self.tf_idf > other.tf_idf:
                return True
            return False
        elif (isinstance(other, list)):
            trues = 0
            for item in other:
                if self.tf_idf > item.tf_idf:
                    trues += 1
            if trues == len(other):
                return True
            return False
        elif (isinstance(other, float)):
            if (self.tf_idf > other):
                return True
            return False
    def __lt__(self, other: object):
        if (isinstance(other, self.__class__)):
            if self.tf_idf < other.tf_idf:
                return True
            return False
        elif (isinstance(other, list)):
            trues = 0
            for item in other:
                if self.tf_idf< item.tf_idf:
                    trues += 1
            if trues == len(other):
                return True
            return False
    def __eq__(self, other: object):
        if (isinstance(other, self.__class__)):
            if self.tf_idf == other.tf_idf:
                return True
            return False
        elif (isinstance(other, list)):
            trues = 0
            for item in other:
                if self.tf_idf == item.tf_idf:
                    trues += 1
            if trues == len(other):
                return True
            return False
    def __ge__(self, other: object):
        if (isinstance(other, self.__class__)):
            if self.tf_idf >= other.tf_idf:
                return True
            return False
        elif (isinstance(other, list)):
            trues = 0
            for item in other:
                if self.tf_idf >= item.tf_idf:
                    trues += 1
            if trues == len(other):
                return True
            return False
    def __le__(self, other: object):
        if (isinstance(other, self.__class__)):
            if self.tf_idf <= other.tf_idf:
                return True
            return False
        elif (isinstance(other, list)):
            trues = 0
            for item in other:
                if self.tf_idf <= item.tf_idf:
                    trues += 1
            if trues == len(other):
                return True
            return False
    def __add__(self, other: object):
        if isinstance(other, CorpusDocument):
            return self.tf_idf + other.tf_idf
        elif isinstance(other, float):
            return self.tf_idf + other
        else: 
            return TypeError("CorpusDocument add only support float and CorpusDocument")
    def __sub__(self, other:object):
        if isinstance(other, CorpusDocument):
            return self.tf_idf - other.tf_idf
        elif isinstance(other, float):
            return self.tf_idf - other
        else:
            raise TypeError("CorpusDocument sub only supports float and CorpusDocument")

class Corpus:
    """
    Represents a set of Documents.
    ### How to use:
        test_var = Corpus('path/to/file') #simple as that
        - This object supports operator [] overloading. test_var[4] will return the 5th CorpusDocument
    """
    def __init__(self,folder_path):
        self.search_upper_bound:int = None
        """Used for get_random_keywords()"""
        self.search_lower_bound:int = None
        """Used for get_random_keywords()"""
        self.documents: list = collections.defaultdict(Document)
        """List of documents in CorpusDocument format"""
        filenames : list = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
        for file in filenames:
            self.documents[file] = CorpusDocument(join(folder_path, file), id=file)
        self.df: dict = collections.defaultdict(int)
        for item in self.documents.items():
            for newitem  in item[1].unique():
                self.df[newitem] += 1
    def __getitem__(self, key:int) -> list:
        return list(self.documents.items())[key][1]
    def get_by_name(self, name: str) -> Document:
        """Returns a corpusDocument by name"""
        return self.documents[name]
    def get_sorted_dfs(self) -> OrderedDict:
        """Returns Document frequences sorted highest-lowest"""
        return OrderedDict(sorted(self.df.items(),key=lambda item: item[1], reverse=True))
    def get_random_keywords(self,amount) -> list:
        """Returns random keywords within 
            (search_upper_bound %, search_lower_bound %) based on document frequency"""
        keywords = []
        sorted_dfs = list(self.get_sorted_dfs().items())
        if (self.search_upper_bound is None):
            self.search_upper_bound = 0.0
        if (self.search_lower_bound is None):
            self.search_lower_bound = len(sorted_dfs)
        for _ in range(amount):
            random_int = randint(self.search_upper_bound, self.search_lower_bound-1)
            keyword = sorted_dfs[random_int][0]
            if keyword not in keywords:
                keywords.append(keyword)
            else:
                amount += 1
        return keywords
    def set_keyword(self, keyword):
        """Checks on every CorpusDocument. If keyword in question exists, it adds it
            on the keyword attribute. Else adds ''."""
        for doc in self.documents:
            if keyword in self.documents[doc].unique():
                self.documents[doc].keyword = keyword
            else:
                self.documents[doc].keyword = ''
    def set_tfidf(self, keyword:str):
        """Sets tf_idf value for a given keyword in every CorpusDocument 
            (obviously 0 if keyword does not) exist"""
        df_log = math.log2(len(self.documents)/self.df[keyword])
        for doc in self.documents:
            fetched_doc = self.documents[doc].tf
            self.documents[doc].tf_idf = fetched_doc[keyword]*df_log
    def set_upper_bound(self,value: int):
        """Self explanatory"""
        sorted_dfs = list(self.get_sorted_dfs().items())
        self.search_upper_bound = round(len(sorted_dfs) * value )
    def set_lower_bound(self, value:int):
        """Self explanatory"""
        sorted_dfs = list(self.get_sorted_dfs().items())
        self.search_lower_bound = round(len(sorted_dfs) * value )




