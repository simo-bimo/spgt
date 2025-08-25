import argparse
import os

from typing import List

from spgt.translator import Translator

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_args():
	parser: argparse.ArgumentParser = argparse.ArgumentParser(
		"spgt",
		"Small Plans for Good Times (SPGT): A compact planner for temporal FOND plans in ASP."
	)
	
	parser.add_argument("domain")
	parser.add_argument("problem")
	
	parser.add_argument("-g", "--goal", type=str)
	
	parser.add_argument('-td', '--temp_dir',
					 type=str,
					 default='./output')
	
	args = parser.parse_args()
	
	args.domain = os.path.abspath(args.domain)
	args.problem = os.path.abspath(args.problem)
	args.temp_dir = os.path.abspath(args.temp_dir)
	
	if not os.path.isdir(args.temp_dir):
		os.mkdir(args.temp_dir)
	
	return args

def ask_for_goal(args, problem_encoding):
	print("You need to specify a goal formula.")
	print_vars = input("See available variables? (y/N)")
	if print_vars.lower() in ["y", "yes"]:
		variable_vars = [x for x in problem_encoding if x.startswith("variableValue")]
		print("\n".join(variable_vars))
	
	goal = input("Goal Formula: ")
	args.goal = goal

def main():
	args = get_args()
	
	# translate
	translator: Translator = Translator(args.domain, args.problem)
	
	# if args.goal is None:
		# ask_for_goal(args)
		
	# solve
	translator.save_ASP(os.path.join(args.temp_dir, "instance.lp"))
	
	# output
	
if __name__ == '__main__':
	main()