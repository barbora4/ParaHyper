from lark import Lark, Transformer
import argparse

class TreeToJson(Transformer):
    # remove trace_quantifiers from tree
    def trace_quantifiers(self, s):
        if type(s) == list and len(s) == 1:
            return s[0]
        else:
            return s

    # remove ltl_formula from tree
    def ltl_formula(self, s):
        if type(s) == list and len(s) == 1:
            return s[0]
        else:
            return s
    
    # remove atom from tree
    def atom(self, s):
        if type(s) == list and len(s) == 1:
            return s[0]
        else: 
            return s
    
    # remove parameterized_atomic_proposition from tree
    def parameterized_atomic_proposition(self, s):
        if type(s) == list and len(s) == 1:
            return s[0]
        else:
            return s

def create_parser(grammar_file_path):
    # HyperLTL(MSO) grammar
    with open(grammar_file_path) as f:
        grammar = f.read()
    return Lark(grammar, start="trace_quantifiers")

def parse_command_line_arguments():
    # parse command line arguments
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument(
        "--formula", 
        help="path to the file with formula",
        required = True
    )
    input_parser.add_argument(
        "--initial_config", 
        help="path to the .mata file with FA representing initial configurations of the system",
        required = True
    )
    input_parser.add_argument(
        "--system_transducer",
        help="path to the file with transducer representing transitition between system configurations",
        required = True 
    )
    input_parser.add_argument(
        "--symbol_mapping",
        help="path to the file with list of symbols",
        required=True
    )
    input_parser.add_argument(
        "--max_states",
        help="maximum number of states of the generated advice bits",
        required=True
    )
    # optional argument for the transducer
    input_parser.add_argument(
        "--relation",
        help="optional file with transducer for the relation",
        required = False 
    )
    # optional argument for the invariant
    input_parser.add_argument(
        "--invariant",
        help="optional file with invariant",
        required=False 
    )
    # optional argument for the transducer bound
    input_parser.add_argument(
        "--relation_bound",
        help="optional bound for the transducer",
        required=False
    )
    
    args = vars(input_parser.parse_args())
    return args