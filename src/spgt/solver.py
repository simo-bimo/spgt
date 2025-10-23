import subprocess

from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingo import Control
from clingo import Model

from typing import List, AnyStr

from time import time

from spgt.names import ASP_PPLTL_PLANNER_PATH, \
		ASP_PLANNER_PATH, ASP_REGRESSOR_PATH, \
		ASP_PPLTL_REGRESSOR_PATH, ASP_CLINGRAPH_PATH, \
		ASP_STRONG_PATH

def filter_atoms(atoms: List[AnyStr], filter: List[AnyStr] = [], as_facts: bool = False) -> List[AnyStr]:
	'''
	Takes a list of atoms and returns any whose name matches one of those in filter.
	
	`as_facts` means the returned listed contains facts, ending with a full stop, instead of just atoms.
	'''
	output_atoms = []
	for a in atoms:
		if sum([a.startswith(r) for r in filter]):
			local_a = a
			if as_facts:
				local_a += "."
			output_atoms.append(local_a)
	return output_atoms

def _run_clingo_as_subprocess(clingo_path: AnyStr,
							  files: List[AnyStr],
							  k: int = 1, 
							  extra_args: List[AnyStr] = []) -> List[AnyStr] | bool | None:
	'''
	Runs clingo as a subprocess on the input files with the `numNodes` parameter set to k.
	returns a list of strings representing a stable model, or False if no such model is found.
	
	Any error from clingo returns None.
	'''
	args = [clingo_path]
	args += files
	args += ['-c', f'numNodes={k-1}']
	args += extra_args
	
	proc = subprocess.run(
		args,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True
	)
	
	if "UNSATISFIABLE" in proc.stdout:
		return False
		
	if "SATISFIABLE" in proc.stdout:
		return proc.stdout.split('\n')
	
	# There must've been some kind of error.
	print(proc.stdout)
	return None

def solve_iteratively_subprocess(args, files, start_time):
	clingo_path = args.clingo_path
	
	output = False
	num_nodes = args.start_size-1
	while output == False:
		num_nodes += 1
		print(f"Attempting to solve with {num_nodes} nodes.")
		remaining_time = args.time_limit - time() + start_time
		extra_args = ['--out-ifs=\\n']
		extra_args += args.clingo_args
		
		if args.time_limit >= 0:
			extra_args += [f'--time-limit={int(remaining_time)}']
		
		output = _run_clingo_as_subprocess(clingo_path, files, num_nodes, extra_args=extra_args)
	
	if output is None:
		print('Failed to solve.')
		return []
	
	print(f"Solved with {num_nodes} nodes.")
	return output


def generate_graph(model: List[AnyStr], temp_dir: AnyStr):
	facts = filter_atoms(model, ['node', 'edge', 'attr', 'graph'], as_facts=True)
	
	fb = Factbase()
	for f in facts:
		fb.add_fact_string(f)
	fb.add_fact_string("attr(node, 0, penwidth, 3).")
	graphs = compute_graphs(fb)
	render(graphs, temp_dir, format='png', name_format="graph_{graph_name}")
	pass

def atoms_from_model(model: Model):
	'''
	Takes as input a clingo model and returns a list of each atom as a string.
	'''
	return [str(a) for a in model.symbols(atoms=True)]
	
def _create_and_solve(files: List[AnyStr], k: int = 1, extra_args: List[AnyStr] = []) -> List[AnyStr] | bool:
	'''
	Uses the clingo python API to run clingo on the input files with the `numNodes` parameter set to k.
	returns a list of strings representing a stable model, or False if no such model is found.
	'''
	
	# mute terminal output and set controller size.
	ctl = Control(['-c', f'numNodes={k-1}'] + extra_args)
	for f in files:
		ctl.load(f)
	ctl.ground()
		
	with ctl.solve(yield_=True) as hdlr:
		if hdlr.get().unsatisfiable:
			return False
		model = hdlr.model()
	return atoms_from_model(model)

def solve_iteratively(args, files):
	output = False
	clingo_args = args.clingo_args
	num_nodes = args.start_size-1
	while output == False:
		num_nodes += 1
		print(f"Attempting to solve with {num_nodes} nodes.")
		
		output = _create_and_solve(files, num_nodes, extra_args=clingo_args)
	
	print(f"Solved with {num_nodes} nodes.")
	return output

def select_files(args) -> List[str]:
	files = [ASP_PLANNER_PATH, ASP_REGRESSOR_PATH]
	if args.ppltl:
		files = [ASP_PPLTL_PLANNER_PATH, ASP_PPLTL_REGRESSOR_PATH]
	
	if args.graph:
		files += [ASP_CLINGRAPH_PATH]
		
	if args.strong:
		files += [ASP_STRONG_PATH]
	return files
	
def solve(args, instance_file: AnyStr, start_time: float):
	
	files = select_files(args)
	files += [instance_file]
	
	if args.time_limit >= 0:
		args.subprocess = True
	
	if args.subprocess:
		output = solve_iteratively_subprocess(args, files, start_time)
	else:
		output = solve_iteratively(args, files)
	
	if args.graph and len(output):
		generate_graph(output, args.temp_dir)
	
	return output