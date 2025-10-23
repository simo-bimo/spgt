import argparse
import os

from typing import List

from spgt.translator import Translator
from spgt.solver import solve
from spgt.base.logic import Formula

from spgt import names


def get_args():
	parser: argparse.ArgumentParser = argparse.ArgumentParser(
		"spgt",
		"Small Plans for Good Times (SPGT): A compact planner for temporal FOND plans in ASP."
	)
	
	parser.add_argument("domain")
	parser.add_argument("problem")
	
	parser.add_argument('--subprocess',
					action='store_true',
					help="Whether to run clingo as a CLI subprocess or through the Python API.")
	
	parser.add_argument('--clingo_path',
					 type=str,
					 default='clingo',
					 help="The location of the clingo executable.")
	
	parser.add_argument('--clingo_args',
					 type=str,
					 help="Extra arguments to give to clingo when run through the CLI.")
	
	parser.add_argument("-g", "--goal", 
					type=str, 
					help="""Used to overwrite the goal of a domain.
					Use -g ? or --goal=? to print out the available variables and symbols.
					""")
	
	parser.add_argument('-td', '--temp_dir',
					 type=str,
					 default='./output')
	
	parser.add_argument('-gr', '--graph',
					 action='store_true')
	
	parser.add_argument('--start_size',
					 type=int,
					 default=1)
	
	parser.add_argument('--ppltl', action='store_true')
	parser.add_argument('--strong', action='store_true')
	
	parser.set_defaults(
		graph=False,
		ppltl=False,
		strong=False,
		clingo_args=""
	)
	
	args = parser.parse_args()
	
	args.domain = os.path.abspath(args.domain)
	args.problem = os.path.abspath(args.problem)
	args.temp_dir = os.path.abspath(args.temp_dir)
	
	if not os.path.isdir(args.temp_dir):
		os.mkdir(args.temp_dir)
	
	return args

def set_goal(arg_goal: str, t: Translator) -> Formula:
	'''
	Overwrites the goal of t based on arg_goal.
	If arg_goal is the empty string, prints variables and symbols,
	then asks for command line input of new goal.
	'''
	if arg_goal != "?":
		t.overwrite_goal(Formula.parse(arg_goal))
		return
	
	# Explain the options and ask them for the goal.
	print("The available variables are:")
	for v in sorted(t.variables, key=lambda v: v.symbol):
		print(f"\t{v.symbol}:")
		print("\t\t" + ", ".join(sorted(v.domain)))
		
	print("The available binary logic symbols are:")
	for bop, symb in Formula.binary_mappings.items():
		print(f"\t{symb}: {bop}")
		
	print("The available unary logic symbols are:")
	for uop, symb in Formula.unary_mappings.items():
		print(f"\t{symb}: {uop}")
	
	form_str = input("Please provide the desired goal formula: ")
	t.overwrite_goal(Formula.parse(form_str))
	pass
	
def parse_clingo_args(args: str) -> List[str]:
	if len(args) == 0:
		return []
	
	return args.split(' ')

def main():
	args = get_args()
	args.clingo_args = parse_clingo_args(args.clingo_args)
	
	translator: Translator = Translator(args.domain, args.problem)
	if not args.goal is None:
		set_goal(args.goal, translator)
	
	# The translator may already contain, or have been updated
	# to contain ppltl formulae, in which case we need to use the
	# correct regressor and planner.
	# if translator.is_ppltl():
		# args.ppltl = True
	
	instance_loc = os.path.abspath(os.path.join(args.temp_dir, "instance.lp"))
	output_loc = os.path.abspath(os.path.join(args.temp_dir, "output.lp"))
	
	translator.save_ASP(instance_loc)
	
	output = solve(args, instance_loc)
	with open(output_loc, "w+") as f:
		f.writelines(s+'\n' for s in output)
	
if __name__ == '__main__':
	main()