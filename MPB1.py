import model_utils
import utils
import config as cfg


# Run configs can be changed in the config.py file.
# each experiment will create a log file named by the seed items.
# if you don't want to evaluate (or don't have the full set) simply comment out the utils.evaluate() call
# and disregard the set_file config (in the config file).


def expand_with_mpb1(seed_terms, log_output_file=None, bert=None, bert_tokenizer=None):
    if not bert or not bert_tokenizer:
        bert, bert_tokenizer = model_utils.get_model_and_tokenizer_bert("bert-large-uncased")
    if not log_output_file:
        log_output_file = utils.get_output_file(seed)
    masked_sentences = utils.get_masked_sentences_for_seed(seed_terms, log_output_file,
                                                           cfg.general_config['num_of_sentences'],
                                                           cfg.general_config['use_indexer'],
                                                           cfg.general_config['corpus_dir'], bert_tokenizer)
    indicative_patterns_and_max_positions = model_utils.get_indicative_patterns(bert, bert_tokenizer, masked_sentences,
                                                                                seed_terms,
                                                                                cfg.general_config['num_of_indicative_patterns'],
                                                                                log_output_file,
                                                                                cfg.general_config['batch_size'])
    results = model_utils.get_models_top_k_suggestions_for_group_of_patterns(bert, bert_tokenizer,
                                                                             indicative_patterns_and_max_positions,
                                                                             cfg.general_config['size_of_expanded'],
                                                                             cfg.general_config['batch_size'])
    utils.print_expansion_to_output_file(results, log_output_file)
    return results


if __name__ == "__main__":
    seed = cfg.general_config['seed']
    output_file = utils.get_output_file(seed)
    model, tokenizer = model_utils.get_model_and_tokenizer_bert("bert-large-uncased")
    expanded = expand_with_mpb1(seed, output_file, model, tokenizer)
    utils.evaluate(expanded, output_file, cfg.general_config['set_file'])
