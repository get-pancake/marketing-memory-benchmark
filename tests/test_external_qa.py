import unittest
from benchmarks.integrated.external_evaluate import matches

class ExternalScorerTests(unittest.TestCase):
    def test_numeric_answer_cannot_hide_conflicting_candidates(self):
        label={'answer_type':'number','answer':42}
        self.assertTrue(matches('42%',label))
        self.assertFalse(matches('42 or 43',label))
        self.assertFalse(matches('142',label))
    def test_boolean_and_unknown_are_whole_answers(self):
        self.assertTrue(matches('no',{'answer_type':'boolean','answer':False}))
        self.assertFalse(matches('no, but possibly yes',{'answer_type':'boolean','answer':False}))
        self.assertFalse(matches('unknown until Alice responds',{'answer_type':'unknown','answer':'unknown'}))
    def test_set_requires_exact_dates_without_explanatory_distractors(self):
        label={'answer_type':'set','answer':['2026-01-01','2026-02-01']}
        self.assertTrue(matches('2026-02-01; 2026-01-01',label))
        self.assertFalse(matches('2026-02-01',label))
        self.assertFalse(matches('2026-02-01; 2026-01-01; 2026-03-01',label))
    def test_entity_aliases_are_explicit(self):
        self.assertTrue(matches('Quarrendon Freight Lines',{'answer_type':'account','answer':'quarrendon'}))
        self.assertFalse(matches('Quarrendon or Elmridge',{'answer_type':'account','answer':'quarrendon'}))

if __name__=='__main__':unittest.main()
