import config as cfg
import utils
import MPB1
import MPB2
import model_utils

MPB1_experiments = [
    {'set_file': '../sets/NFL_set.txt', 'set_seeds': [["titans", "seahawks", "saints"],
                                                      ["vikings", "colts", "dolphins"],
                                                      ["titans", "giants", "cardinals"]]},
    {'set_file': '../sets/MLB_set_berts_vocab.txt', 'set_seeds': [["mets", "astros", "brewers"],
                                                                  ["mariners", "royals", "brewers"],
                                                                  ["cubs", "mets", "phillies"]]},
    {'set_file': '../sets/Presidents_set_berts_vocab.txt', 'set_seeds': [["bush", "adams", "obama"],
                                                                         ["lincoln", "nixon", "trump"],
                                                                         ["clinton", "kennedy", "reagan"]]}
]

MPB2_experiments = [
    {'set_file': '../sets/NFL_set.txt', 'set_seeds': [["titans", "seahawks", "saints"],
                                                      ["vikings", "colts", "dolphins"],
                                                      ["titans", "giants", "cardinals"]]},
    {'set_file': '../sets/MLB_set.txt', 'set_seeds': [["mets", "astros", "brewers"],
                                                      ["mariners", "royals", "brewers"],
                                                      ["cubs", "mets", "phillies"]]},
{'set_file': '../sets/Presidents_set.txt', 'set_seeds': [["bush", "adams", "obama"],
                                                         ["lincoln", "nixon", "trump"],
                                                         ["clinton", "kennedy", "reagan"]]},
    {'set_file': '../sets/US_states_set.txt', 'set_seeds': [["hawaii", "iowa", "delaware"],
                                                            ["montana", "maryland", "washington"],
                                                            ["oregon", "alaska", "alabama"]]},
    {'set_file': '../sets/Countries_set.txt', 'set_seeds': [["cambodia", "bulgaria", "canada"],
                                                            ["japan", "jordan", "kenya"],
                                                            ["uzbekistan", "finland", "oman"]]},
    # for set & subset results run the EURO seeds with countries set as well:
    {'set_file': '../sets/Euro_set.txt', 'set_seeds': [['croatia', 'macedonia', 'liechtenstein'],
                                                       ['poland', 'slovenia', 'france'],
                                                       ["moldova", "romania", "spain"]]},
    {'set_file': '../sets/Capitals_set.txt', 'set_seeds': [["baghdad", "tbilisi", "berlin"],
                                                           ["tbilisi", "jerusalem", "hanoi"],
                                                           ["tbilisi", "tehran", "dublin"]]},
    {'set_file': '../sets/Music_genres_set.txt', 'set_seeds': [["rap", "pop", "techno"],
                                                               ["rock", "gospel", "techno"],
                                                               ["rock", "blues", "punk"]]}
]


def run_expander_experiment(exp_name, bert, bert_tokenizer):
    seed = cfg.general_config['seed']
    output_file = utils.get_output_file(seed, exp_name)
    if exp_name == "MPB1" or exp_name.startswith("sent_num") or exp_name == "BB":
        expanded = MPB1.expand_with_mpb1(set(seed), output_file, bert, bert_tokenizer)
    elif exp_name == "MPB2" or exp_name.startswith("sim_param"):
        expanded = MPB2.expand_with_mpb2(set(seed), output_file, bert, bert_tokenizer)
    else:
        print("wrong exp name.")
        return -1
    map_score = utils.evaluate(expanded, output_file, cfg.general_config['set_file'])
    return map_score


def run_expander_experiments(expander_experiments, expander_name, bert, bert_tokenizer):
    for exp in expander_experiments:
        cfg.general_config['set_file'] = exp['set_file']
        if "Music_genres" in exp['set_file']:
            cfg.MPB2_config['assume_oracle_candidates'] = False
        else:
            cfg.MPB2_config['assume_oracle_candidates'] = True
        if "Countries_set" in exp['set_file'] or "Capitals_set" in exp['set_file']:     # bigger sets then the others
            cfg.general_config['size_of_expanded'] = 350
        set_total_map = 0
        for seed in exp['set_seeds']:
            cfg.general_config['seed'] = seed
            map_score = run_expander_experiment(expander_name, bert, bert_tokenizer)
            if map_score == -1:
                break
            set_total_map += map_score
        print("for set: " + exp['set_file'] + " average map score is: " + str(set_total_map / len(exp['set_seeds'])))


def run_similarity_param_exp(bert, bert_tokenizer):
    cfg.expander_params_to_mpb2_default()
    cfg.MPB2_config['percentage_of_corpus_to_use'] = 25         # for result reproduction reasons
    cfg.general_config['set_file'] = '../sets/US_states_set.txt'    # '../sets/NFL_set.txt'
    cfg.general_config['seed'] = ["nebraska", "wisconsin", "arizona"]   # ["jets", "bills", "cowboys"]
    for sim_param in [1, 5, 50, 300, 700, 3000]:
        cfg.MPB2_config['similarity_param'] = sim_param
        map_score = run_expander_experiment("sim_param" + str(sim_param), bert, bert_tokenizer)
        print("for sim_param: " + str(sim_param) + " map score is: " + str(map_score))


def run_num_of_sent_and_indicative_exp(bert, bert_tokenizer):
    cfg.expander_params_to_mpb1_default()
    cfg.general_config['set_file'] = '../sets/NFL_set.txt'
    for num_of_sent in [20, 100, 300, 1000, 2000, 4000]:
        cfg.general_config['num_of_sentences'] = num_of_sent
        for num_of_ind in [1, 5, 10, 20, 40, 80, 160, 600]:
            cfg.general_config['num_of_indicative_patterns'] = num_of_ind
            if num_of_ind > num_of_sent:
                continue
            set_total_map = 0
            for seed in [['chiefs', 'broncos', 'texans'], ['cowboys', 'bengals', 'ravens'],
                         ['titans', 'chiefs', 'raiders'], ['jets', '49ers', 'giants'],
                         ['seahawks', 'patriots', 'bills']]:
                cfg.general_config['seed'] = seed
                map_score = run_expander_experiment("sent_num" + str(num_of_sent) + "_indicative_num" + str(num_of_ind), bert, bert_tokenizer)
                if map_score == -1:
                    break
                set_total_map += map_score
            print("for num_of_sent: " + str(num_of_sent) + "num of ind: " + str(num_of_ind) + " average map score is: " + str(set_total_map / 5))


if __name__ == "__main__":
    model, tokenizer = model_utils.get_model_and_tokenizer_bert("bert-large-uncased")
    # run_num_of_sent_and_indicative_exp(model, tokenizer)
    # run_similarity_param_exp(model, tokenizer)
    cfg.expander_params_to_mpb1_default()
    run_expander_experiments(MPB1_experiments, "MPB1", model, tokenizer)
    # cfg.expander_params_to_mpb2_default()
    # run_expander_experiments(MPB2_experiments, "MPB2", model, tokenizer)


