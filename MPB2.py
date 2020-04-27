import model_utils
import corpus_utils
import sence2vec_utils
import operator
import utils
import config as cfg

# Run configs can be changed in the config.py file.
# each experiment will create a log file named by the seed items.
# if you don't want to evaluate (or don't have the full set) simply comment out the utils.evaluate() call
# and disregard the set_file config (in the config file).


def score_candidates(model, tokenizer, candidates, indicative_patterns_and_max_positions, indicative_patterns_and_top_suggestions):
    candidate_score_list = []
    sum_of_all_max_position_inverses = sum((1 / j[1]) for j in indicative_patterns_and_max_positions)
    candidates_sentences = corpus_utils.find_sentences_for_all_candidates(candidates, cfg.general_config['use_indexer'],
                                                                          cfg.general_config['corpus_dir'],
                                                                          cfg.MPB2_config['max_sentences_for_each_cand'],
                                                                          cfg.MPB2_config['percentage_of_corpus_to_use'] / 100)
    for i, candidate in enumerate(candidates_sentences.keys()):
        if i % 20 == 0:
            print("finished  " + str(i) + " candidates out of " + str(len(candidates_sentences)))
        candidate_masked_sentences = utils.mask_sentences_and_filter(candidates_sentences[candidate], [candidate], tokenizer,
                                                                     cfg.MPB2_config['max_sentences_for_each_cand'])
        seed_and_candidate_contexts_similarity = []
        model_suggestions_for_candidate_patterns = model_utils.\
            get_patterns_top_k_model_suggestions_for_each_pattern(model, tokenizer, candidate_masked_sentences,
                                                                  cfg.MPB2_config['similarity_param'],
                                                                  cfg.general_config['batch_size'])
        for candidate_masked_sentence, model_suggestions_for_candidate in model_suggestions_for_candidate_patterns:
            for indicative_pattern, model_suggestions_for_indicative in indicative_patterns_and_top_suggestions:
                sim = len(model_suggestions_for_candidate.intersection(model_suggestions_for_indicative)) /\
                      cfg.MPB2_config['similarity_param']
                # 3-tuple (size of intersection, seed context, candidate context):
                seed_and_candidate_contexts_similarity.append((sim, indicative_pattern, candidate_masked_sentence))
        seed_and_candidate_contexts_similarity.sort(reverse=True, key=operator.itemgetter(1, 0))
        indicative_patterns_used = set()
        candidate_score = 0
        for similarity, indicative_pattern, candidate_patterns in seed_and_candidate_contexts_similarity:
            if len(indicative_patterns_used) == len(indicative_patterns_and_max_positions):  # we used all patterns
                break
            if indicative_pattern not in indicative_patterns_used:  # best sim for this indicative pattern
                max_position_current_pattern = indicative_patterns_and_max_positions[len(indicative_patterns_used)][1]
                weight_of_current_pattern = (1 / max_position_current_pattern) / sum_of_all_max_position_inverses  # give more weight in the score to better contexts
                candidate_score += similarity * weight_of_current_pattern
                indicative_patterns_used.add(indicative_pattern)
        #print((candidate, candidate_score))
        candidate_score_list.append((candidate, candidate_score))
    candidate_score_list.sort(reverse=True, key=operator.itemgetter(1))
    return candidate_score_list


def expand_with_mpb2(seed_terms, log_output_file, bert, bert_tokenizer):
    candidates = sence2vec_utils.get_candidates_closest_to_seed_terms(seed_terms,
                                                                      cfg.general_config['size_of_expanded'],
                                                                      cfg.MPB2_config['total_terms_to_consider'])
    log_output_file.write("Using " + str(len(candidates)) + " candidates\n")
    if cfg.MPB2_config['assume_oracle_candidates']:
        expected_terms = utils.get_first_syn_of_terms_from_file(cfg.general_config['set_file'])
        utils.print_candidate_stats_to_output_file(log_output_file, candidates, expected_terms, len(expected_terms))
        candidates = candidates.union(expected_terms)
    masked_sentences = utils.get_masked_sentences_for_seed(seed_terms, log_output_file,
                                                           cfg.general_config['num_of_sentences'],
                                                           cfg.general_config['use_indexer'],
                                                           cfg.general_config['corpus_dir'], bert_tokenizer)
    indicative_patterns_and_max_positions = model_utils.get_indicative_patterns(bert, bert_tokenizer, masked_sentences,
                                                                                seed_terms,
                                                                                cfg.general_config['num_of_indicative_patterns'],
                                                                                log_output_file,
                                                                                cfg.general_config['batch_size'])
    indicative_patterns = [i[0] for i in indicative_patterns_and_max_positions]
    indicative_patterns_and_top_suggestions = model_utils.get_patterns_top_k_model_suggestions_for_each_pattern\
        (bert, bert_tokenizer, indicative_patterns, cfg.MPB2_config['similarity_param'], cfg.general_config['batch_size'])
    candidate_score_list = score_candidates(bert, bert_tokenizer, candidates, indicative_patterns_and_max_positions,
                                            indicative_patterns_and_top_suggestions)
    utils.print_expansion_with_scores_to_output_file(candidate_score_list, log_output_file)
    return [i[0] for i in candidate_score_list]


if __name__ == "__main__":
    seed = cfg.general_config['seed']
    output_file = utils.get_output_file(seed)
    model, tokenizer = model_utils.get_model_and_tokenizer_bert("bert-large-uncased")
    expanded = expand_with_mpb2(set(seed), output_file, model, tokenizer)
    utils.evaluate(expanded, output_file, cfg.general_config['set_file'])
