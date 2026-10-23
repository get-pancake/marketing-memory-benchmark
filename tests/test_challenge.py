import copy,unittest
from benchmarks.challenge.generate import make_case
from benchmarks.challenge.core import *
from benchmarks.challenge.retrieve import select,closure
from benchmarks.challenge.check_oracle import sql_reference

class ChallengeTests(unittest.TestCase):
    def setUp(self):self.case=make_case(12345,1,1);self.ev=visible(self.case['events'],self.case['query'])
    def test_independent_sql_and_exhaustive(self):
        ids,items=sql_reference(self.case);self.assertEqual(ids,{e['id'] for e in self.ev})
        self.assertEqual(enumerate_optimum(items,7),optimize(candidates(self.ev,self.case['query']),7)['value'])
    def test_future_and_private_excluded(self):
        self.assertTrue(all(e['observed_day']<=30 and e['access']=='public' for e in self.ev))
        self.assertNotIn(1000,[e['value'] for e in self.ev])
    def test_gold_plan_requires_every_link(self):
        plan=optimize(candidates(self.ev,self.case['query']),7)['plan'];self.assertTrue(plan)
        output={'actions':[{'account':x['account'],'action':x['action'],'sources':[g[0] for g in x['support_groups']]} for x in plan]}
        self.assertTrue(score(output,self.case,self.ev)['exact_optimum'])
        output['actions'][0]['sources'].pop();self.assertTrue(score(output,self.case,self.ev)['unsafe'])
    def test_duplicate_account_and_budget(self):
        x=optimize(candidates(self.ev,self.case['query']),7)['plan'][0]
        one={'account':x['account'],'action':x['action'],'sources':[g[0] for g in x['support_groups']]}
        out=score({'actions':[one,one]},self.case,self.ev);self.assertIn('duplicate_account',out['errors'])
        q=copy.deepcopy(self.case);q['query']['budget']=0
        self.assertIn('over_budget',score({'actions':[one]},q,self.ev)['errors'])
    def test_conflict_cannot_be_dropped_by_packing(self):
        original=next(e for e in self.ev if e['relation']=='consent');other=dict(original,id='econflict',value=not original['value'])
        events=self.ev+[other];chosen=select(events,self.case['query'],[original['id']],'gbrain',100000)
        self.assertIn('econflict',[e['id'] for e in chosen])
    def test_retrieval_not_oracle_ranked(self):
        ranks=[e['id'] for e in self.ev]
        changed=copy.deepcopy(self.ev)
        # Boolean decision values and priorities affect the oracle but must not
        # alter catalog closure/order (use a huge cap to remove byte-length effects).
        for e in changed:
            if e['relation']=='priority' and e['authority']=='approved':e['value']=999
            if e['relation']=='consent':e['value']=not e['value']
        for arm in ['company','gtm','markdown']:
            self.assertEqual([x['id'] for x in select(self.ev,self.case['query'],ranks,arm,1000000)],
                             [x['id'] for x in select(changed,self.case['query'],ranks,arm,1000000)])
    def test_zero_context_does_not_earn_positive_value(self):
        result=score({'actions':[]},self.case,[])
        self.assertGreater(result['optimum'],0);self.assertEqual(result['normalized_value'],0);self.assertFalse(result['unsafe'])
    def test_same_corporate_sources_available_to_gtm(self):
        a=self.case['query']['accounts'][0];rows=closure(self.ev,a,True)
        self.assertTrue({'capacity','assurance','shareable'}<={e['relation'] for e in rows})

if __name__=='__main__':unittest.main()
