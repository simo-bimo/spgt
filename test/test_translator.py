import unittest
import os
from spgt.translator import Translator
import pddl

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_DATA = os.path.join(THIS_DIR, os.pardir, "benchmarks", "domains")

def dict_to_set(d, key_lambda = lambda x: x, value_lambda = lambda x: x):
	return set((key_lambda(k),value_lambda(v)) for k,v in d.items())

class TestTranslatorComponenets(unittest.TestCase):
	def setUp(self):
		self.domain_directory = os.path.abspath(
			os.path.join(TEST_DATA, "acrobatics")
			)
		self.domain_path = os.path.abspath(
			os.path.join(self.domain_directory, "domain.pddl")
			)
		self.instance_paths = []
		for i in range(8):
			self.instance_paths.append(os.path.abspath(
				os.path.join(self.domain_directory, "p0" + str(i+1) + ".pddl")
				)
			)
	
	def test_a_unchanging_vars(self):
		t = Translator(self.domain_path, self.instance_paths[0], process_immediate=False)
		expected_unchanging = {"next-fwd", "next-bwd", "ladder-at"}
		found_unchanging = t.unchanging_predicates
		self.assertLessEqual(expected_unchanging, found_unchanging)
		self.assertLessEqual(found_unchanging, expected_unchanging)
		pass
		
	def test_b_action_parameter_possibilities(self):
		t = Translator(self.domain_path, self.instance_paths[0], process_immediate=False)
		walk_on_beam = [a for a in t.actions if a.name == 'walk-on-beam'].pop()
		
		expected_possibilities = [
			{('from','p0'), ('to', 'p1')}
		]
		
		actual_possibilities = [
			dict_to_set(poss, value_lambda=lambda x: x.name) for poss in t.__parameter_possibilities(walk_on_beam)
		]
		for e in expected_possibilities:
			self.assertIn(e, actual_possibilities)
		for a in actual_possibilities:
			self.assertIn(a, expected_possibilities)
		pass
	
	

if __name__ == "__main__":
	unittest.main()