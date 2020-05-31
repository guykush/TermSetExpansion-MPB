from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh import index
import os


def find_sentences_with_seed_terms(terms, use_indexer, corpus_dir, number_of_sentences):
    if use_indexer:
        print("using indexer.")
        return find_sentences_with_terms_indexer(terms, corpus_dir, number_of_sentences)
    else:
        return find_sentences_with_terms_search_text_files(terms, corpus_dir, number_of_sentences)


# returns a dictionary. candidate is the key and candidate_sentences the value.
# size of each candidate_sentences list is number_of_sentences.
def find_sentences_for_all_candidates(candidates, use_indexer, corpus_dir, number_of_sentences, part_of_corpus):
    candidate_sentences = {}
    for candidate in candidates:
        candidate_sentences[candidate] = []
    if use_indexer:
        for candidate in candidates:
            candidate_sentences[candidate].\
                extend(find_sentences_with_terms_indexer([candidate], corpus_dir, number_of_sentences))
    else:
        candidates_to_find = candidates
        candidates_found = set()
        text_file_dir = corpus_dir + "textFiles/"
        text_files = os.listdir(text_file_dir)
        text_files.sort()   # to maintain compatibility in different run environments
        stop_after = len(text_files) * part_of_corpus
        for i, fileName in enumerate(text_files):
            if i > stop_after:
                break
            if i % 100000 == 0:
                print("finished " + str(i) + " files.")
            file_full_name = corpus_dir + "textFiles/" + fileName
            f = open(file_full_name, 'r')
            text = f.read()
            f.close()
            for candidate in candidates_to_find:
                candidate_sentences[candidate].extend(get_sentences_with_terms_from_file(text, [candidate]))
                if len(candidate_sentences[candidate]) > 1.2 * number_of_sentences:  # have some extra for the filtering later
                    candidates_found.add(candidate)
                if len(candidates_to_find) == 0:
                    return candidate_sentences
            candidates_to_find = candidates_to_find - candidates_found
            candidates_found.clear()
    return candidate_sentences


def find_sentences_with_terms_search_text_files(terms, corpus_dir, number_of_sentences):
    text_file_dir = corpus_dir + "textFiles/"
    sentences_with_terms = []
    text_files = os.listdir(text_file_dir)
    text_files.sort()  # to maintain compatibility in different run environments
    for fileName in text_files:
        file_full_name = corpus_dir + "textFiles/" + fileName
        f = open(file_full_name, 'r')
        text = f.read()
        sentences_with_terms.extend(get_sentences_with_terms_from_file(text, terms))
        f.close()
        if len(sentences_with_terms) > 1.2 * number_of_sentences:  # have some extra for the filtering later
            return sentences_with_terms
    return sentences_with_terms


def find_sentences_with_terms_indexer(terms, corpus_dir, number_of_sentences):
    ix = index.open_dir(corpus_dir + "indexdir")
    query_str = get_indexer_query(terms)
    containing_files = []
    with ix.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query, limit=None)
        for result in results:
            containing_files.append(result['title'])
    sentences_with_terms = []
    for fileName in containing_files:
        file_full_name = corpus_dir + "textFiles/" + fileName
        f = open(file_full_name, 'r')
        text = f.read()
        sentences_with_terms.extend(get_sentences_with_terms_from_file(text, terms))
        f.close()
        if len(sentences_with_terms) > 1.2 * number_of_sentences:   # have some extra for the filtering later
            return sentences_with_terms
    return sentences_with_terms


def get_sentences_with_terms_from_file(text, terms):
    sentences_with_terms = []
    for term in terms:
        if term in text.lower():
            replaced_string = text.replace(",", ".").replace("\n", ".").replace("*", ".")
            for sentence in replaced_string.split("."):
                if term.lower() in sentence.lower() and len(sentence.split()) > 5:
                    if len(term.split()) == 1:    # in this case we want to make sure its not part of a longer word
                        if term.lower() in sentence.lower().split() or non_alpha_before_and_after(term, sentence.lower()):
                            sentences_with_terms.append(sentence.lower())
                    else:
                        sentences_with_terms.append(sentence.lower())
    return sentences_with_terms


def non_alpha_before_and_after(term, sentence):
    term_index = sentence.lower().index(term.lower())
    if term_index + len(term) < len(sentence):
        if sentence.lower()[term_index + len(term)].isalpha():
            return False
    if term_index != 0:
        if sentence.lower()[term_index - 1].isalpha():
            return False
    return True


def get_indexer_query(terms):
    if len(terms) == 1:
        return terms[0]
    else:
        term_list = []
        for t in terms:
            term_list.append("'" + t + "'")
        return " OR ".join(term_list)
