import subprocess
import os

from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render

from typing import List, AnyStr

from spgt.names import ASP_PLANNER_PATH, ASP_REGRESSOR_PATH, ASP_CLINGRAPH_PATH

clingo_executable = "clingo"

def _run_clingo_as_subprocess(files: List[AnyStr], i: int = 1, extra_args: List[AnyStr] = []):
	args = [clingo_executable]
	args += files
	args += ['-c', f'numNodes={i}']
	args += extra_args
	
	proc = subprocess.run(
		args,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True
	)
	if "ERROR" in proc.stdout:
		return proc.stdout
	if "SATISFIABLE" in proc.stdout and\
		"UNSATISFIABLE" not in proc.stdout:
		return proc.stdout
	return None

def generate_graph(solution_file: AnyStr, temp_dir: AnyStr, graph_name: AnyStr):
	output_file = os.path.abspath(os.path.join(temp_dir, graph_name))
	
	fb = Factbase()
	fb.add_fact_file(solution_file)
	fb.add_fact_string("attr(node, 0, penwidth, 3).")
	graphs = compute_graphs(fb)
	render(graphs, temp_dir, format='png', name_format=graph_name+"_{graph_name}")
	pass

def solve_iteratively(instance_file, generate_graph: bool=False):
	files = [instance_file, ASP_REGRESSOR_PATH, ASP_PLANNER_PATH]
	if generate_graph:
		files.append(ASP_CLINGRAPH_PATH)
		
	output = None
	num_nodes = 0
	while output is None:
		num_nodes += 1
		print(f"Attempting to solve with {num_nodes} nodes.")
		args = ['--out-ifs=\\n']
		# if generate_graph:
			# args = ['--outf=2']
		output = _run_clingo_as_subprocess(files, num_nodes, extra_args=args)
	
	print(f"Solved with {num_nodes+1} nodes.")
	return output