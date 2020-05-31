from collections import defaultdict
import corpus_utils
import os
import config as cfg


def clean_string(inp):
    return inp.lower().replace('_', ' ')


def get_masked_sentences_for_seed(terms, log_output_file, num_of_sentences, use_indexer, corpus_dir, tokenizer):
    sentences = corpus_utils.find_sentences_with_seed_terms(terms, use_indexer, corpus_dir, num_of_sentences)
    masked_sentences = mask_sentences_and_filter(sentences, terms, tokenizer, num_of_sentences)
    log_output_file.write("Using " + str(len(masked_sentences)) + " sentences to search for indicative patterns.\n")
    return masked_sentences


def mask_sentences_and_filter(sentences, term_set, tokenizer, num_of_sentences):
    masked_sentences = []
    for sent in sentences:
        for term in term_set:
            if term in sent:
                replaced = sent.replace(term, "***mask***")
                if replaced[-1] != ".":
                    replaced += "."
                if replaced.count("***mask***") != 1 or len(tokenizer.tokenize(replaced)) > 400:
                    continue
                masked_sentences.append(replaced)
    return masked_sentences[:num_of_sentences]


# for set_file: assuming each row in the file contains comma separated synonyms that represent the same term
def get_set_from_file(set_file):
    item_to_index = defaultdict(int)
    next_index = 1
    with open(set_file) as f2:
        for line in f2:
            parts = [x.strip() for x in line.split(',')]
            parts = [x for x in parts if x]
            if parts:
                for p in parts:
                    item_to_index[clean_string(p)] = next_index
                next_index = next_index + 1
    return item_to_index, next_index - 1


# for set_file: assuming each row in the file contains comma separated synonyms that represent the same term
def get_first_syn_of_terms_from_file(set_file):
    terms = set()
    with open(set_file) as f2:
        for line in f2:
            parts = [x.strip() for x in line.split(',')]
            parts = [x for x in parts if x]
            if parts:
                terms.add(clean_string(parts[0]))
    return terms


def get_output_file(seed, exp="not_from_experiments"):
    log_dir = "../logDir/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not exp == "not_from_experiments":
        exp_log_dir = "../logDir/" + exp + "/"
        if not os.path.exists(exp_log_dir):
            os.makedirs(exp_log_dir)
        log_dir = exp_log_dir
    set_name = cfg.general_config['set_file'].split("/")[-1].split(".")[0]
    set_log_dir = log_dir + set_name + "/"
    if not os.path.exists(set_log_dir):
        os.makedirs(set_log_dir)
    seed_string = "".join(seed)
    output_file_name = "./" + set_log_dir + "/" + seed_string + "_log_output"  # make seed output file
    return open(output_file_name, 'w')


def get_map(item_to_index, expansion, synsets_to_seek):
    seen_indices = set()
    bad_entries_count = 0
    good_entries_count = 0
    score_sum = 0.0
    intrusions = []
    for idx, item in enumerate(expansion):
        if clean_string(item) not in item_to_index:
            bad_entries_count = bad_entries_count + 1
            intrusions.append((item, '#%d' % (idx + 1)))
        else:
            good_entries_count = good_entries_count + 1
            this_index = item_to_index[clean_string(item)]
            if this_index not in seen_indices:
                seen_indices.add(this_index)
                percentage_here = 1.0 * good_entries_count / (good_entries_count + bad_entries_count)
                score_sum = score_sum + percentage_here
        if len(seen_indices) == synsets_to_seek:
            break
    return score_sum / synsets_to_seek, intrusions  # Returns MAP precision, weights of offending intrusions.


def print_expansion_to_output_file(results, output_file):
    i = 1
    for term in results:
        output_file.write(str(i) + ". " + term + "\n")
        i += 1


def print_expansion_with_scores_to_output_file(results, output_file):
    i = 1
    for term, term_score in results:
        output_file.write(str(i) + ". " + term + " score is: " + str(term_score) + "\n")
        i += 1


def print_candidate_stats_to_output_file(log_output_file, candidates, expected_set, size_of_set):
    log_output_file.write(str(len(set(candidates).intersection(expected_set))) + " desired terms out of "
                          + str(size_of_set) + " are in candidates.")
    s = list(set(expected_set) - set(candidates))
    set_string = ', '.join(str(e) for e in s)
    log_output_file.write(" did not find: " + set_string + "\n")


def evaluate(expanded_set, log_output_file, set_file):
    full_set, size = get_set_from_file(set_file)
    if "Music_genres" in cfg.general_config['set_file']:       # this is an open set, calc map 70.
        map_score, intruders = get_map(full_set, expanded_set, 70)
    else:
        map_score, intruders = get_map(full_set, expanded_set, size)
    print("map is: ", map_score)
    log_output_file.write("map is: " + str(map_score))
    log_output_file.write(", intruders are: " + str(intruders) + "\n")
    return map_score
