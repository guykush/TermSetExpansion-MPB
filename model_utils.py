import operator
import torch
from pytorch_pretrained_bert import tokenization, BertForMaskedLM, BertModel
import math
import numpy


def get_model_and_tokenizer_bert(model_name):
    bert = BertForMaskedLM.from_pretrained(model_name)
    tokenizer = tokenization.BertTokenizer.from_pretrained(model_name)
    bert.eval()
    if torch.cuda.is_available():
        device = 'cuda'
        print("Using GPU!")
    else:
        device = "cpu"
        print("GPU not available.")
    bert.to(device)
    return bert, tokenizer


def prepare_sentence_for_bert(sent, tokenizer):
    pre, target, post = sent.split('***')
    if 'mask' in target.lower():
        target = ['[MASK]']
    tokens = ['[CLS]'] + tokenizer.tokenize(pre)
    target_idx = len(tokens)
    tokens += target + tokenizer.tokenize(post) + ['[SEP]']
    return tokens, target_idx


def get_attention(sequence):
    attention = [1 for i in sequence if i != 0]
    attention.extend([0 for i in sequence if i ==0])
    return attention


def get_batch_results_from_bert(tokens_list, tokenizer, bert):
    max_seq_size = max([len(tokens) for tokens in tokens_list])
    input_id_list = []
    attention_list = []
    for sequence_tokens in tokens_list:
        sequence_ids = tokenizer.convert_tokens_to_ids(sequence_tokens)
        sequence_ids.extend([0] * (max_seq_size - len(sequence_ids)))
        input_id_list.append(sequence_ids)
        attention_list.append(get_attention(sequence_ids))
    input_tensor = torch.LongTensor(input_id_list)
    attention_tensor = torch.LongTensor(attention_list)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    input_tensor = input_tensor.to(device)
    attention_tensor = attention_tensor.to(device)
    with torch.no_grad():
        bert_output = bert(input_ids=input_tensor, attention_mask=attention_tensor)
    return bert_output


def get_models_suggestions_for_batch(model, tokenizer, patterns):
    tokens_list = []
    target_idx_list = []
    for pattern in patterns:
        tokens, target_idx = prepare_sentence_for_bert(pattern, tokenizer)
        tokens_list.append(tokens)
        target_idx_list.append(target_idx)
    batch_model_results = get_batch_results_from_bert(tokens_list, tokenizer, model)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    batch_target_results = []
    for i, target_idx in enumerate(target_idx_list):
        batch_target_results.append(batch_model_results[i, target_idx])
    batch_target_results_tensor = torch.stack(batch_target_results)
    batch_target_results_tensor = batch_target_results_tensor.to(device)
    res = torch.nn.functional.softmax(batch_target_results_tensor, -1)
    _, best = torch.topk(res, len(res[0]))
    return best


def get_models_top_k_suggestions_for_group_of_patterns(model, tokenizer, patterns_and_max_positions, k, batch_size):
    res_tensor = None
    first_results = True
    sum_of_all_max_position_inverses = sum((1/j[1]) for j in patterns_and_max_positions)
    for batch_num in range(math.ceil((len(patterns_and_max_positions) / batch_size))):
        batch_start_index = batch_size * batch_num
        batch_end_index = min(batch_size * (1 + batch_num), len(patterns_and_max_positions))
        if batch_start_index >= batch_end_index or batch_end_index > len(patterns_and_max_positions):
            continue
        batch_masked_sentences = patterns_and_max_positions[batch_start_index:batch_end_index]
        tokens_list = []
        target_idx_list = []
        for pattern, _ in batch_masked_sentences:
            tokens, target_idx = prepare_sentence_for_bert(pattern, tokenizer)
            tokens_list.append(tokens)
            target_idx_list.append(target_idx)
        batch_results = get_batch_results_from_bert(tokens_list, tokenizer, model)
        for batch_index, (masked_pattern, max_position) in enumerate(batch_masked_sentences):
            weight_of_current_pattern = (1 / max_position) / sum_of_all_max_position_inverses  # give more weight in the score to better contexts
            sequence_results = batch_results[batch_index, target_idx_list[batch_index]]
            sequence_results = torch.nn.functional.softmax(sequence_results, -1)
            if first_results:
                res_tensor = sequence_results.log() * weight_of_current_pattern
                first_results = False
            else:
                res_tensor = res_tensor.add(sequence_results.log() * weight_of_current_pattern)
    _, best_k = torch.topk(res_tensor, k)
    best_k_ints = [int(x) for x in best_k]
    return tokenizer.convert_ids_to_tokens(best_k_ints)


def get_patterns_top_k_model_suggestions_for_each_pattern(model, tokenizer, patterns, k, batch_size):
    patterns_and_top_suggestions = []
    for batch_num in range(math.ceil((len(patterns) / batch_size))):
        batch_start_index = batch_size * batch_num
        batch_end_index = min(batch_size * (1 + batch_num), len(patterns))
        if batch_start_index >= batch_end_index or batch_end_index > len(patterns):
            continue
        batch_patterns = patterns[batch_start_index:batch_end_index]
        batch_results = get_models_suggestions_for_batch(model, tokenizer, batch_patterns)
        batch_results = batch_results.tolist()
        for batch_index, pattern in enumerate(batch_patterns):
            patterns_and_top_suggestions.append((pattern, set(batch_results[batch_index][:k])))
    return patterns_and_top_suggestions


def get_indicative_patterns(bert, tokenizer, masked_sentences, terms, number_of_indicative_patterns, log_output_file, batch_size):
    best_sentences_and_max_positions = []  # a list of tuples (masked sentence, maxPosition)
    for batch_num in range(math.ceil((len(masked_sentences) / batch_size))):
        batch_start_index = batch_size * batch_num
        batch_end_index = min(batch_size * (1 + batch_num), len(masked_sentences))
        if batch_start_index >= batch_end_index or batch_end_index > len(masked_sentences):
            continue
        batch_masked_sentences = masked_sentences[batch_start_index:batch_end_index]
        batch_results = get_models_suggestions_for_batch(bert, tokenizer, batch_masked_sentences)
        for batch_index, masked_sentence_to_check in enumerate(batch_masked_sentences):
            max_position_current_sent = -1
            np_array_suggestions = batch_results[batch_index].cpu().numpy()
            for t in terms:             # find positions of term seed in bert predictions
                term_position = numpy.nonzero(np_array_suggestions == tokenizer.convert_tokens_to_ids(tokenizer.tokenize(t))[-1])[0][0]
                if term_position > max_position_current_sent:
                    max_position_current_sent = term_position
            if len(best_sentences_and_max_positions) > number_of_indicative_patterns and \
                    max_position_current_sent > max([i[1] for i in best_sentences_and_max_positions]):
                continue                # current is worse then the worst indicative pattern
            add_current = True
            to_remove = []
            for masked_sentence_in_top, max_position_in_top in best_sentences_and_max_positions:
                # check similarity:
                if len(set(masked_sentence_to_check.split()).intersection(set(masked_sentence_in_top.split()))) >\
                        0.5 * min(len(masked_sentence_to_check.split()), len(masked_sentence_in_top.split())):
                    if max_position_in_top <= max_position_current_sent:
                        add_current = False  # similar to a sentence with better position, don't add
                        break
                    else:   # similar to a sentence with worse position, remove the old one when adding
                        to_remove.append((masked_sentence_in_top, max_position_in_top))
            if add_current:
                if len(to_remove) > 0:
                    for r in to_remove:
                        best_sentences_and_max_positions.remove(r)
                best_sentences_and_max_positions.append((masked_sentence_to_check, max_position_current_sent))
                best_sentences_and_max_positions.sort(key=operator.itemgetter(1))       # sort by max positions
                best_sentences_and_max_positions = best_sentences_and_max_positions[:number_of_indicative_patterns]
    print_chosen_patterns_to_output_file(best_sentences_and_max_positions, log_output_file)
    return best_sentences_and_max_positions[:number_of_indicative_patterns]


def print_chosen_patterns_to_output_file(best_sentences_and_max_positions, log_output_file):
    for sent, position in best_sentences_and_max_positions:
        log_output_file.write("chose the indicative pattern:" + "\n")
        log_output_file.write(sent + "\n")
        log_output_file.write("max position of it was: " + str(position) + "\n")









