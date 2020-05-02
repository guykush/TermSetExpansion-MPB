from sense2vec import Sense2Vec


def get_query_from_terms(terms, s2v):
    query = []
    for term in terms:
        query.append(s2v.get_best_sense(term))
    return query


def get_candidates_closest_to_seed_terms(terms, num_of_candidates, num_of_top_frequency_terms_to_consider):
    s2v = Sense2Vec().from_disk("../data/s2v_reddit_2019_lg")
    query = get_query_from_terms(terms, s2v)
    most_similar = s2v.most_similar(query, n=num_of_candidates * 50)  # have some extra because of non top frequency cands
    candidates = [i[0] for i in most_similar]
    clean_candidates = [t for t in terms]
    most_frequent = s2v.frequencies[:num_of_top_frequency_terms_to_consider]
    most_frequent = [i[0] for i in most_frequent]
    for cand in candidates:
        if cand in most_frequent:
            without_pos = cand.split("|")[0]
            clean = without_pos.replace("_", " ").lower()
            to_add = clean.replace(".", "")
            if to_add not in clean_candidates:
                clean_candidates.append(to_add)
        if len(clean_candidates) == num_of_candidates:
            break
    return set(clean_candidates)



