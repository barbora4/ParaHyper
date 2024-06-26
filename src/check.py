#!/usr/bin/python3

import parse
from formula import Formula
import automata
import invariant_conditions
import sat_solver
import libmata.nfa.nfa as mata_nfa
from libmata import parser, alphabets, plotting
import time 
import sys 
import itertools

if __name__ == "__main__":
    start = time.time()
    
    grammar_parser = parse.create_parser("grammar.txt")
    args = parse.parse_command_line_arguments()

    # get symbol mapping
    with open(args["symbol_mapping"]) as f:
        symbol_map = f.read().splitlines()

    # load initial configuration of a system (.mata)
    initial_configurations = automata.get_initial_configurations(
        args["initial_config"],
        symbol_map
    )
    atomic_propositions = initial_configurations.atomic_propositions

    # parse formula into tree
    with open(args["formula"]) as f:
        input_formula = f.read()
    tree = grammar_parser.parse(input_formula)
    formula = Formula(tree, atomic_propositions)
    # print formula parsed into Buchi Normal Form
    formula.print_formula()

    # create automaton for initial mso formula
    formula.make_initial_automaton()

    # parse system transducer from file
    system_transducer = automata.parse_transducer_from_file(
        args["system_transducer"],
        symbol_map 
    )

    # create transducer for local constraints of mso formula
    formula.make_local_constraints_transducer()

    # extended transducer for the system
    restricted_transducer = automata.restrict_transducer_with_formula(
       system_transducer,
       formula.mso_local_constraints_transducer,
       formula.trace_quantifiers_list
    )

    # extended initial configurations with MSO formula
    restricted_initial_conf = automata.restrict_automaton_with_formula(
        initial_configurations, 
        formula.mso_initial_automaton,
        formula.trace_quantifiers_list,
        restricted_transducer.symbol_map.copy()[-1]
    )

    # transducer for eventuality constraints
    formula.make_eventuality_constraints_transducer()
    # optional transducer for the relation
    relation = None 
    if args["relation"] != None:
        tmp_map = formula.mso_eventuality_constraints_transducer.symbol_map.copy()
        tmp_map = tmp_map[:int(len(tmp_map)/2)]
        tmp_map[-1] = sorted(tmp_map[-1])
        relation = automata.parse_transducer_from_file(
            args["relation"],
            tmp_map,
            with_configuration=True
        )
        relation.symbol_map = tmp_map.copy() + tmp_map.copy()
    # optional invariant
    invariant = None
    if args["invariant"] != None:
        invariant_symbol_map = restricted_initial_conf.symbol_map.copy()
        invariant_symbol_map[-1] = sorted(invariant_symbol_map[-1])
        invariant = automata.get_automaton_with_configuration_tape(
            args["invariant"],
            invariant_symbol_map
        )
        invariant.symbol_map = invariant_symbol_map.copy()

    # conditions for SAT solver
    # get only used symbols (not the whole alphabet)
    used_alphabet = restricted_transducer.get_used_symbols()
    A, T = sat_solver.find_solution(
        k_aut = int(args["max_states"]), 
        restricted_initial_conf = restricted_initial_conf,
        restricted_transducer = restricted_transducer,
        original_transducer = system_transducer,
        accepting_transitions = formula.mso_eventuality_constraints_transducer,
        trace_quantifiers = formula.trace_quantifiers_list,
        T_aut = relation,
        A_aut = invariant,
        relation_bound = args["relation_bound"] 
    ) 

    if (A,T) == (None, None):
        print("Solution was not found for", args["max_states"], "states")
    else:
        end = time.time()
        print("Solution was found in", end-start, "seconds")
        # save the advice bits
        A.save_automaton(name="A")
        T.save_automaton(name="T")