"""
### KDDs_Project module

Automated Docs I created for my KDDs project.
This includes 3 python files, each one of them for a different purpose explained inside each file \n
Contribute your own Trees by adding files here and importing them as you see fit

### So, what is this project all about?
Let's say you got a bunch of documents and you want to find how many of them have 'keyword1'  and 'keyword2' in common, and how similar are those documents.
This project is all about creating a k-dimensional tree with all the documents (one dimension per keyword), then extracting the documents that have common keywords out of the tree, then comparing them via LSH algorithm.

### IMPORTANT FOR LSH ALGORITHM
For my LSH implemenation to work you need to feed the constructor a Tree of your choice, but LSH.run() needs an array with CorpusDocuments that you found when searching inside the tree, but not the tree itself

### Code is still in Beta. Expect bugs
"""