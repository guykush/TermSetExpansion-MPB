# import os
# from whoosh import index
# from whoosh.fields import Schema, TEXT, ID
#
#
# if not os.path.exists("indexdir"):
#     os.mkdir("indexdir")
#
# '''
# Schema definition: title(name of file), path(as ID), content(indexed
# but not stored),textdata (stored text content)
# '''
# schema = Schema(title=TEXT(stored=True), content=TEXT)
# # Creating a index writer to add document as per schema
# ix = index.create_in("indexdir", schema)
# writer = ix.writer()
# root = "textFiles/"
# file_paths = [os.path.join(root, i) for i in os.listdir(root)]
# print("there are ", len(file_paths), " articles")
# i = 0
# for path in file_paths:
#     # if i == 500000:           #uncomment to make a smaller corpus and indexer (500000 can be changed of course)
#     #     break
#     fp = open(path, 'r')
#     text = fp.read()
#     fp.close()
#     writer.add_document(title=path.split("/")[-1], content=text)
#     i += 1
#     if i % 5 == 0:
#         print("indexed " + str(i) + " articles")
#         print("committing " + str(i) + " articles")
#         writer.commit()
#         print("finished committing " + str(i) + " articles")
#         writer = ix.writer()
# print("finished indexing " + str(i) + " articles out of ", len(file_paths))

