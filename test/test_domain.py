import unittest

from spgt.asp.symbols import *
from spgt.base.domain import GroundedAction, GroundedEffect
from spgt.base.logic import Formula, Verum, Falsum, Atom, Neg, Conj, Disj, Assign

class TestEffectBasic(unittest.TestCase):
	def test_a_effect_repr(self):
		subtests = [
			(
				("x", [('a', 'b'), ('c', 'd')], [('e', 'f')]),
				"Effect(x, adds(a=b,c=d), deletes(e=f))"
			),
		]
		for inpt,expected in subtests:
			with self.subTest(input=int, expected=expected):
				e = GroundedEffect(*inpt)
				self.assertEqual(str(e), expected)
		pass
	
	def test_b_effect_from_formula(self):
		a = Atom('a')
		b = Atom('b')
		c = Atom('c')
		d = Atom('d')
		e = Atom('e')
		f = Atom('f')
		
		subtests = [
			(
				"x",
				Conj(Assign(a, b), Conj(Assign(c, d), Neg(Assign(e, f)))),
				"Effect(x, adds(a=b,c=d), deletes(e=f))"
			),
			(
				"baguette",
				Conj(Neg(Assign(e, f)), Conj(Assign(c, d), Assign(a, b))),
				"Effect(baguette, adds(a=b,c=d), deletes(e=f))"
			),
		]
		for name,form,expected in subtests:
			with self.subTest(input=int, expected=expected):
				e = GroundedEffect.from_formula(name, form)
				self.assertEqual(str(e), expected)
		pass
	
	def test_c_effect_as_ASP(self):
		a = Atom('a')
		b = Atom('b')
		c = Atom('c')
		d = Atom('d')
		e = Atom('e')
		f = Atom('f')
		
		subtests = [
			(
				"x",
				Conj(Assign(a, b), Conj(Assign(c, d), Neg(Assign(e, f)))),
				[
					'add(x, a, b).',
					'add(x, c, d).',
					'del(x, e, f).'
				]
			),
			(
				"baguette",
				Conj(Neg(Assign(e, f)), Conj(Assign(c, d), Assign(a, b))),
				[
					'add(baguette, a, b).',
					'add(baguette, c, d).',
					'del(baguette, e, f).'
				]
			),
		]
		for name,form,expected in subtests:
			with self.subTest(input=int, expected=expected):
				e = GroundedEffect.from_formula(name, form)
				rules_set = set(e.as_ASP())
				self.assertSetEqual(rules_set, set(expected))	
		pass