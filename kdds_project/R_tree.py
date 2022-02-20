from kdds_project.File_Handler import Corpus, CorpusDocument
#To R tree exei ena lathos me thn ylopoihsh tou mazi me to lsh opote de trexei auti ti stigmi.

class Bounding_box():
    def __init__(self,point1:list, point2:list):
        if (len(point1) == len(point2)):
            self.corner_one = point1
            self.corner_two = point2
            self.dims = len(point1)
        else:
            raise ValueError("Points must have the same num of dimensions")
    def contains(self, bb:'Bounding_box'):
        values = []
        for i in range(self.dims):
            minA = min(self.corner_one[i], self.corner_two[i])
            maxA = max(self.corner_one[i], self.corner_two[i])
            minB = min(bb.corner_one[i], bb.corner_two[i])
            maxB = max(bb.corner_one[i], bb.corner_two[i])
            values.append(
                maxA >= maxB and
                minA <= minB
                )
        if sum(values) == self.dims:
            return True
        else:
            return False
    def find_area_needed(self, bb:'Bounding_box')->int:
        area = 1
        for i in range(self.dims):
            A = max(self.corner_one[i], self.corner_two[i])
            B = max(bb.corner_one[i], bb.corner_two[i])
            if (B < A and (A is not 0) and (B is not 0)):
                A = min(self.corner_one[i], self.corner_two[i])
                B = min(bb.corner_one[i], bb.corner_two[i])
            if (A == 0):
                A = 1
            if B == 0:
                B = 1
            area *= abs(B-A)
        return area
    def intersects(self, bb: 'Bounding_box'):
        #an itan ylopoihmenh tha koitaze an yparxei tomi se opoiadhpote diastasi.
        #logw elleipsis xronou den einai ylopoihmeni.
        
        #return true simainei oti epistrefei olo to dentro.
        return True

class R_tree():
    def __init__(self, corpus = None, bounding_box=Bounding_box([0,0],[0,0]), max_capacity:int = 3,keywords:list = None):
        self.corpus = corpus
        self.keywords = keywords
        self.dims = len(keywords)
        self.bounding_box = bounding_box
        self.max_capacity = max_capacity
        self.docs = []

    def insert(self, val:CorpusDocument)->bool:
        if sum(val.tf_idf_vector) == 0:
            return True
        if self.bounding_box.contains(Bounding_box(val.tf_idf_vector, val.tf_idf_vector)): 
            for index, item in enumerate(self.docs):
                if (isinstance(item, R_tree)):
                    if(item.insert(val)):
                        return True
                if isinstance(item, CorpusDocument):
                    self.docs[index] = self.split_leaf(item, val)
                    self.docs[index].docs.append(item)
                    self.docs[index].docs.append(val)
            if len(self.docs) < self.max_capacity:
                self.docs.append(val)
                return True
        area_needed = []
        for index, doc in enumerate(self.docs):
            if isinstance(doc, CorpusDocument):
                self.docs[index] = self.split_leaf(doc, val)
                self.docs[index].docs.append(doc)
                self.docs[index].docs.append(val)
                return True
            val_bounding_box = Bounding_box(val.tf_idf_vector, val.tf_idf_vector)
            area_needed.append(doc.bounding_box.find_area_needed(val_bounding_box))
        min_value = min(area_needed)
        min_index = area_needed.index(min_value)
        new_dims_1 = []
        new_dims_2 = []
        for i in range(self.dims):
            new_dims_1.append(min(self.docs[index].bounding_box.corner_one[i], val.tf_idf_vector[i]))
            new_dims_2.append(max(self.docs[index].bounding_box.corner_two[i],val.tf_idf_vector[i]))
        self.docs[min_index].bounding_box = Bounding_box(new_dims_1, new_dims_2)
        return self.docs[min_index].insert(val)

    def split_leaf(self, doc:CorpusDocument, value:CorpusDocument)->'R_tree':
        min_arr = []
        max_arr = []
        for i in range(self.dims):
            max_of_two = max(doc.tf_idf_vector[i], value.tf_idf_vector[i])
            min_of_two = min(doc.tf_idf_vector[i], value.tf_idf_vector[i])
            max_arr.append(max_of_two)
            min_arr.append(min_of_two)
        return R_tree(bounding_box=Bounding_box(min_arr, max_arr), keywords=self.keywords)

    def mass_insert(self)->bool:
        self.corpus.set_tf_idf_vector(self.keywords,len(self.keywords))
        min_value = 100000
        max_value = -10
        for i in range(len(self.corpus.documents)):
            for item in self.corpus[i].tf_idf_vector:
                if item > max_value:
                    max_value = item
                if item < min_value:
                    min_value = item
            min_value_box = [min_value]*len(self.keywords)
            max_value_box = [max_value]*len(self.keywords)
        self.bounding_box= Bounding_box(min_value_box,max_value_box )
        for i in range(len(self.corpus.documents)):
            self.insert(self.corpus[i])

    def query(self, querybb:Bounding_box, arr = []):
        test = self.bounding_box.intersects(querybb)
        test2 = querybb.intersects(self.bounding_box)
        if not (self.bounding_box.intersects(querybb)):
            return arr
        for item in self.docs:
            if (isinstance(item, CorpusDocument)):
                arr.append(item)
            else:
                item.query(querybb, arr)
        return arr