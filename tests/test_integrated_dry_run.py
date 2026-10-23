import copy
import unittest
from study.fixtures import build
from study.contract import visible,applicable
from benchmarks.integrated.dry_run import execute

class MockExecutionTests(unittest.TestCase):
    def setUp(self):
        data,_=build('pilot',1,2026102307);self.world=data['worlds'][0]
        self.q=data['queries'][0]['query'];self.evidence=visible(self.world['events'],self.q)
        eligible=applicable(self.evidence,self.q,self.world['catalog']);tid=sorted(eligible)[0]
        ids=sorted(set().union(*eligible[tid]))
        self.proposal={'status':'recommend','plays':[{'template':tid,'evidence':ids}],'missing':[]}
    def test_mock_executes_capabilities_and_returns_provenance(self):
        r=execute(self.proposal,self.evidence,self.q,self.world['catalog'])
        self.assertEqual(r['status'],'completed')
        self.assertEqual(r['report']['source_ids'],self.proposal['plays'][0]['evidence'])
        self.assertEqual(r['calls'][-1]['capability'],'prepare_evidence_report')
    def test_missing_evidence_is_not_repaired_from_world(self):
        r=execute(self.proposal,[],self.q,self.world['catalog'])
        self.assertEqual(r['status'],'rejected');self.assertEqual(r['calls'],[])
    def test_budget_is_enforced_before_each_capability(self):
        r=execute(self.proposal,self.evidence,dict(self.q,max_units=0),self.world['catalog'])
        self.assertEqual(r['status'],'rejected');self.assertEqual(r['units'],0)
    def test_unknown_capability_cannot_run(self):
        catalog=copy.deepcopy(self.world['catalog'])
        t=next(t for t in catalog if t['id']==self.proposal['plays'][0]['template'])
        t['workflow']=['send_outreach'];t['units']=1
        r=execute(self.proposal,self.evidence,self.q,catalog)
        self.assertEqual(r['status'],'rejected');self.assertEqual(r['reason'],'unavailable_capability')

if __name__=='__main__':unittest.main()
