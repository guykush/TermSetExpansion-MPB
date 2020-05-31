import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID


index_dir_path = "../data/indexdir"
if not os.path.exists(index_dir_path):
    os.mkdir(index_dir_path)

'''
Schema definition: title(name of file), path(as ID), content(indexed
but not stored),textdata (stored text content)
'''
schema = Schema(title=TEXT(stored=True), content=TEXT)
# Creating an index writer to add document as per schema
ix = index.create_in(index_dir_path, schema)
writer = ix.writer()
text_files = "../data/textFiles/"
file_paths = [os.path.join(text_files, i) for i in os.listdir(text_files)]
print("there are ", len(file_paths), " articles")
for i, path in enumerate(file_paths):
    fp = open(path, 'r')
    text = fp.read()
    fp.close()
    writer.add_document(title=path.split("/")[-1], content=text)
    i += 1
    if i % 5 == 0:
        writer.commit()
        writer = ix.writer()
    if i % 1000 == 0:
        print("indexed " + str(i) + " articles")
print("finished indexing " + str(i) + " articles out of ", len(file_paths))

