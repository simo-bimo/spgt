from spgt.base.logic import Formula, Falsum, Verum, Atom, Assign, Neg, Disj, Conj
import unittest

class TestFormulaBasic(unittest.TestCase):
	"""
	Tests formulas that do not include assignments.
	"""
	def test_a_str(self):
		'''
		Tests that the string representation of a formula is generated correctly.
		'''
		a = Atom('a')
		b = Atom('b')
		c = Atom('c')
		d = Atom('d')
		e = Atom('e')
		f = Atom('f')
		h = Atom('h')
		
		subtests = [
			(Conj(a, b), "(a∧b)"),
			(Conj(a, Conj(b, c)), "(a∧(b∧c))"),
			(Conj(Conj(c, Disj(e, d)), b), "((c∧(e∨d))∧b)"),
			(Disj(Conj(h, f), Conj(d, c)), "((h∧f)∨(d∧c))"),
			(Neg(Disj(Conj(h, f), Conj(d, c))), "¬((h∧f)∨(d∧c))"),
			(Conj(Conj(c, Disj(e, d)), Neg(b)), "((c∧(e∨d))∧¬b)"),
		]
		
		for formula, exp_output in subtests:
			with self.subTest(formula=formula, exp_output=exp_output):
				self.assertEqual(str(formula), exp_output)
			
		pass
	
	def test_b_parse(self):
		'''
		Tests that strings are parsed correctly.
		'''
		subtests = [
			("a&b", "(a∧b)"),
			("a&(b&c)", "(a∧(b∧c))"),
			("(c&(e|d))&b", "((c∧(e∨d))∧b)"),
			("(h&f)|(d&c)", "((h∧f)∨(d∧c))"),
			("!((h&f)|(d&c))", "¬((h∧f)∨(d∧c))"),
			("(c&(e|d))&!b", "((c∧(e∨d))∧¬b)"),
		]
		
		for original, exp_output in subtests:
			with self.subTest(original=original, exp_output=exp_output):
				form = Formula.parse(original)
				self.assertEqual(str(form), exp_output)
			
		pass
	
	def test_c_nnf(self):
		'''
		Tests the Negation Normal Form is generated correctly.
		'''
		subtests = [
			("a&b", "(a∧b)"),
			("!(a&b)", "(¬a∨¬b)"),
			("!(a&(b&c))", "(¬a∨(¬b∨¬c))"),
			("(c&(e|d))&b", "((c∧(e∨d))∧b)"),
			("(h&f)|(d&c)", "((h∧f)∨(d∧c))"),
			("!((h&f)|(d&c))", "((¬h∨¬f)∧(¬d∨¬c))"),
			("(c&(e|d))&(!b)", "((c∧(e∨d))∧¬b)"),
		]
		
		for original, exp_output in subtests:
			with self.subTest(original=original, exp_output=exp_output):
				form = Formula.parse(original)
				nnf = Formula.NNF(form)
				self.assertEqual(str(nnf), exp_output)
			
		pass
	
	def test_d_asp(self):
		"""
		Tests that the ASP rules of the formulae are generated correctly.
		(After having been put into NNF form.)
		"""
		subtests = [
			("a&b", "conj(a, b)"),
			("!(a&b)", "neg(conj(a, b))"),
			("(c&(e|d))&b", "conj(conj(c, disj(e, d)), b)"),
			("!((h&f)|(d&c))", "neg(disj(conj(h, f), conj(d, c)))"),
			("(c&(e|d))&(!b)", "conj(conj(c, disj(e, d)), neg(b))"),
		]
		
		for original, exp_output in subtests:
			with self.subTest(original=original, exp_output=exp_output):
				form = Formula.parse(original)
				asp = form.as_ASP()
				self.assertEqual(asp, exp_output.replace(' ', ''))
		pass
	
	def test_e_simplify_constants(self):
		"""
		Tests constants falsum and verum are simplified correctly.
		"""
		a = Formula.parse("a")
		b = Formula.parse("b")
		c = Formula.parse("c")
		d = Formula.parse("d")
		e = Formula.parse("e")
		
		subtests = [
			(Conj(Falsum(), a), str(Falsum())),
			(Conj(Verum(), b), str(b)),
			(Conj(Verum(), Falsum()), str(Falsum())),
			(Disj(Falsum(), a), str(a)),
			(Disj(b, Verum()), str(Verum())),
			(Conj(Disj(Verum(), a), b), str(b))
		]
		for psi, exp_simp in subtests:
			with self.subTest(psi_str = str(psi), exp_simp=exp_simp, psi=psi):
				simplified = str(Formula.simplify_constants(psi))
				self.assertEqual(simplified, exp_simp)
		pass
	
	@unittest.skip("Deprecated")
	def test_f_regression(self):
		"""
		Tests that the regression works well on single atom Adding effects.
		"""
		subtests = [
			("a&b", "b"),
			("a&(b&c)", "(b∧c)"),
			("a&(b|c)", "(b∨c)"),
			("a|(b&a)", str(Verum()))
		]
		# for psi_str, exp_reg in subtests:
		# 	with self.subTest(psi_str=psi_str, exp_reg=exp_reg):
		# 		psi = Formula.parse(psi_str)
		# 		eff = Effect([psi.subformulae[0]])
		# 		regression = Formula.regress(psi, eff)
		# 		self.assertEqual(str(regression), exp_reg)
		pass
	
	@unittest.skip("Deprecated")
	def test_g_organise(self):
		"""
		Tests that the organise function operates correctly.
		"""
		subtests = [
			("a&b", "(a∧b)"),
			("b&a", "(a∧b)"),
			("a&(b&c)", "(a∧(b∧c))"),
			("b&(c&a)", "(a∧(b∧c))"),
			("(c&a)&b", "(a∧(b∧c))"),
			("(c&(e|d))&b", "(b∧(c∧(d∨e)))"),
			("(h&f)|(d&c)", "((c∧d)∨(f∧h))"),
		]
		
		# for og, exp_org in subtests:
		# 	with self.subTest(original=og, exp_org=exp_org):
		# 		form = Formula.parse(og)
		# 		organised = Formula.organise(form)
		# 		self.assertEqual(str(organised), exp_org)
			
		pass

class TestFormulaVariables(unittest.TestCase):
	def test_a_str(self):
		"""
		Tests that the Assignments are renderered correctly as strings.
		"""
		subtests = [
			(Assign("baguette", "dry"), "(baguette=dry)"),
			(Disj(Assign("baguette", "moist"), Assign("customer", "hungry")), "((baguette=moist)∨(customer=hungry))"),
		]
		
		for og, exp_str in subtests:
			with self.subTest(og=og, exp_str=exp_str):
				self.assertEqual(str(og), exp_str)
			
		pass
	
	def test_b_parse(self):
		"""
		Tests that the VariableAssignment type is parsed
		correctly
		"""
		subtests = [
			("(baguette=dry)", "(baguette=dry)"),
			("(baguette=moist)|(customer=hungry)", "((baguette=moist)∨(customer=hungry))"),
		]
		
		for og, exp_form in subtests:
			with self.subTest(original=og, exp_form=exp_form):
				form = Formula.parse(og)
				self.assertEqual(str(form), exp_form)
			
		pass
	
	@unittest.skip("Unimplemented")
	def test_c_asp(self):
		"""
		Tests assigned variables generate the correct ASP.
		"""
		pass

if __name__ == "__main__":
	unittest.main()