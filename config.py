# general configs are used when directly running MPB1 or MPB2 and when running run_experiments.

# - corpus_dir is the path to the directory that contains a directory named "textFiles" with all text files and an "indexer" directory if using an indexer.
# - num_of_sentences: number of corpus sentences to search for indicative patterns in
# - num_of_indicative_patterns: number of indicative patterns the algorithm uses
# - size_of_expanded: size_of_expanded set the algorithm returns.
# - use_indexer: True if an indexer for corpus searching is available.
# - batch_size: size of batch for BERT
# -set_file: path to text file containing the set. assuming each row in the file contains comma separated synonyms
# that represent the same term and multi words terms are separated by "_", for instance a row can be: "NY, New_York"
# - seed: seed terms to expand

general_config = {'corpus_dir': "../data/",
                  'num_of_sentences': 2000,             # if available in corpus
                  'num_of_indicative_patterns': 160,
                  'size_of_expanded': 200,
                  'use_indexer': False,
                  'batch_size': 50,
                  'set_file': "../sets/NFL_set.txt",  # if available, for evaluation.
                  'seed': ["jets", "ravens", "giants"]}


# MPB2 configs are used when running MPB2 directly or when running MPB2 from run_experiments.

# - assume_oracle_candidates: can be True only if set is available.
# This will add to candidates all "correct" terms for the algorithm to score.
# - max_sentences_for_each_cand: number of sentences retrieved from corpus for each candidate for the scoring process.
# - similarity_param: size of top of the list the algorithm will use for similarity measure between patterns.
# - total_terms_to_consider: X top frequency terms will be used for the expansion.
# - percentage_of_corpus_to_use: the corpus we use contains ~5000000 articles.
# Searching for candidate sentences in all of these without an indexer takes very long.
# with this field you can control which part of the corpus tou want to use.
MPB2_config = {'assume_oracle_candidates': True,    # only possible if full set is available
               'max_sentences_for_each_cand': 100,   # if available in corpus. Should be larger than num_of_indicative_patterns
               'similarity_param': 50,
               'total_terms_to_consider': 200000,  # If you want all available terms to be used use 4000000
               'percentage_of_corpus_to_use': 50}  # relevant only when "use_indexer" is false


def expander_params_to_mpb1_default():      # used for running experiments with our config
    general_config['num_of_sentences'] = 2000
    general_config['num_of_indicative_patterns'] = 160
    general_config['size_of_expanded'] = 200
    general_config['use_indexer'] = False


def expander_params_to_mpb2_default():  # used for running experiments with our config
    general_config['num_of_sentences'] = 2000
    general_config['num_of_indicative_patterns'] = 20
    general_config['size_of_expanded'] = 200
    general_config['use_indexer'] = False
    MPB2_config['assume_oracle_candidates'] = True
    MPB2_config['max_sentences_for_each_cand'] = 100
    MPB2_config['similarity_param'] = 50
    MPB2_config['percentage_of_corpus_to_use'] = 50
    MPB2_config['total_terms_to_consider'] = 200000



