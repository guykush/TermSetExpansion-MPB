# MPB
This project was developed by Guy Kushilevitz (guykushilevitz@gmail.com), 2020.

It implements two set expanders as described in our paper.

We provide a [link](/data) to the corpus, s2v files and sets we used.

To run the code, you will need to install the following python packages: pytorch_pretrained_bert, sense2vec, whoosh (only if you want to use an indexer).
## Entering points
There are 3 main entering points to this code (in order to expand sets):
1. run_expiriments.py- running this file will run the experiments described in our paper and reproduce the reported results. Notice the exact results will be reproduced only if using the exact corpus (see "corpus" section) and configs (the ones suplied) we used. Also, the seeds where randomly chosen, but for reproducing reasons they are now hard coded in the code.
2. MPB1.py: will run a single expansion using the MPB1 expander.
3. MPB2.py: will run a single expansion using the MPB2 expander.

## Configs
Configurations can be changed in the file config.py which also contains information about each configuration.
When running MPB1.py or MPB2.py the seed is also be determined in this file.

## Corpus
#### Generating the Corpus
We use a wikipedia dump to make a corpus. A wikipedia dump can be found [here](/wiki).
After downloading the dump file (we use the file "enwiki-latest-pages-articles.xml.bz2.") The python file "makeTextFiles" should be given the address of the xml file.
running it (for around 12 hours) will generate a directory called textFiles. This is our corpus.
It should be noted that in order to recreate our reported experiment results, the exact corpus we used needs to be used.
We use a Wikipedia dump from 03-Mar-2020 01:55. It might not be available so we provide a [link](/data) to download our produced text files.
#### Using the Corpus
A directory that contains the "textFiles" directory with all the text files should be made and address of it should be given in the config file.
We use a [Whoosh](/whoosh) indexer to index and access these files quickly.
We also allow not using a indexer (can be decided in config.py), which will of course cause a longer runtime.
In order for the experiments to be reproducible, we ran them without an indexer. If you do want to use one, you need to state so in the the config file, and uncomment parts of the corpus_util file.
Also, a directory called "indexdir" produced by the whoosh indexer, needs to be in the same directory as "textFiles".
You can use the script "index_text_files", also included, to generate this directory from the text files.
#### sense2vec
for MPB2 candidates we use [sense2vec](/s2v). A couple of files need to be downloaded and merged and put in the data folder, We also supply a [link](/data) to these files (after merging) in case they are no longer available.

## Sets
We provide the term sets we used for our evaluation. To run experiments a directory named "sets" needs to be created (or [downloaded](/data).) and the path to it needs to be given in the config file.
If you want to use your own set the file containing it should be a text file where each row contains comma separated synonyms that represent the same term and multi words terms are separated by *_*, for instance a row can be: *"NY, New_York"*. For more expamples, see set files [suplied](/data). It is possible to run an expansion without a set file, in this case no evaluation will be done.
  
[data]: https://drive.google.com/open?id=1J-UFRWe36uwrEBglHNgO95dx_TKJEt3v
[s2v]: https://github.com/explosion/sense2vec/blob/master/README.md
[wiki]:  https://dumps.wikimedia.org/enwiki/latest/
[whoosh]: https://whoosh.readthedocs.io/en/latest/intro.html

