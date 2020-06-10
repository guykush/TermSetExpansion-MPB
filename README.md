# MPB
This project was developed by Guy Kushilevitz (guykushilevitz@gmail.com), 2020.

It implements two set expanders as described in our [paper](https://www.arxiv.org/abs/2005.01063).

We provide a [link](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v) to the corpus, indexer, s2v files and sets we used.

To run the code, you will need to install the following python packages: pytorch_pretrained_bert, sense2vec, whoosh (only if you want to use an indexer).
## Entering points
There are 4 main entering points to this code (in order to expand sets):
1. run_expiriments.py- running this file will run the experiments described in our paper and reproduce the reported results. Notice the exact results will be reproduced only if using the exact corpus (see "corpus" section) and configs (the ones suplied) we used. Also, the seeds where randomly chosen, but for reproducing reasons they are now hard coded in the code.
2. MPB1.py: will run a single expansion (for a seed declared in the config file) using the MPB1 expander.
3. MPB2.py: will run a single expansion (for a seed declared in the config file) using the MPB2 expander.
4. From python code: run MPB1.expand_with_mpb1(seed) or MPB2.expand_with_mpb2(seed) where seed is a list of terms. Returns the expanded set with MPB1 or MPB2 (see [paper](https://www.arxiv.org/abs/2005.01063)).

## Configs
Configurations can be changed in the file config.py which also contains information about each configuration.
When running MPB1.py or MPB2.py the seed is also be determined in this file.

## Corpus
#### Generating the Corpus
We use a wikipedia dump to make a corpus. A wikipedia dump can be found [here](https://dumps.wikimedia.org/enwiki/latest/).
After downloading the dump file (we use the file "enwiki-latest-pages-articles.xml.bz2.") The python file "makeTextFiles" should be given the address of the xml file.
running it (for around 12 hours) will generate a directory called textFiles. This is our corpus.
It should be noted that in order to recreate our reported experiment results, the exact corpus we used needs to be used.
We use a Wikipedia dump from 03-Mar-2020 01:55. It might not be available so we provide a [link](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v) to download our produced text files.
#### Using the Corpus
A directory that contains the "textFiles" directory with all the text files should be made.
We use a [Whoosh](https://whoosh.readthedocs.io/en/latest/intro.html) indexer to index and access these files quickly.
We also allow not using a indexer (can be decided in config.py), which will of course cause a longer runtime.
In order for the experiments to be easilly reproducible, we ran them without an indexer which takes alot of space (and in our implementation, will also fause non determinisem). If you do want to use one, you need to state so in the the config file.
Also, a directory named "indexdir" produced by the whoosh indexer needs to be in the same directory as "textFiles".
You can use the script "index_text_files", also included, to generate this directory from the text files or [download](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v) the indexer files we used (only if you are using our provided text files).
#### sense2vec
for MPB2 candidates we use [sense2vec](https://www.github.com/explosion/sense2vec/blob/master/README.md). A couple of files need to be downloaded and merged and put in the data folder, We also supply a [link](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v) to these files (after merging) in case they are no longer available. This directory needs to be in the same data directory.
#### data directory structure
A data directory should be made and address of it should be given in the config.py file.
This directory should contain a "textFiles" directory, a sence2vec directory and can optionally have an "indexer" directory, all of which can be [dowanloaded](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v) if using our corpus or made using provided python files as described above.


## Sets
We provide the term sets we used for our evaluation in this project and [here](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v). Path to it should be given in the config file.
If you want to use your own set the file containing it should be a text file where each row contains comma separated synonyms that represent the same term and multi words terms are separated by *_*, for instance a row can be: *"NY, New_York"*. For more examples, see set files [suplied](https://www.drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v). It is possible to run an expansion without a set file, in this case no evaluation will be done.

