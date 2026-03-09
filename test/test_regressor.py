import unittest

from spgt.asp.symbols import *
from spgt.base.logic import SASVariable, SASValue, Assign, Conj, Disj, Formula
from spgt.base.domain import GroundedAction, GroundedEffect
from spgt.regressor import Regressor

import clingo

class TestRegressor(unittest.TestCase):
	def test_basic_formulae(self):
		'''
		Tests that the python regressor returns the correct ASP output.
		'''
		
		zero = SASVariable(0, 2)
		one = SASVariable(1, 2)
		two = SASVariable(2, 2)
		
		var_mapping = {0: zero, 1: one, 2: two}
		
		add_one = GroundedEffect.from_formula('effect', Assign(one, SASValue(1)))
		
		program = '''
		answer(@reg(F, effect)) :- F=conj(has_value(2,0), has_value(1, 1)).
		'''
		
		regressor = Regressor(var_mapping, [], {add_one.name: add_one})
		
		ctl = clingo.Control()
		ctl.add('base', [], program)
		
		ctl.ground(context=regressor)
		
		def verify_model(m: clingo.Model):
			atoms = [str(s) for s in m.symbols(atoms=True, terms=True)]
			self.assertIn('answer(conj(has_value(2,0),verum))', atoms)
		
		ctl.solve(on_model=verify_model)
		
		
		
		pass