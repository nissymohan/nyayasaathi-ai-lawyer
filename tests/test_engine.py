import unittest
from engine import Case,extract_facts,missing,render_notice,classify,legal_answer,triage,safe_text,public_summary

class EngineTests(unittest.TestCase):
 def setUp(self):
  self.good=Case(merchant='ExampleMart',product='shoes',amount='1000',date='10-10-2026',issue='Refund not received',contact='sent emails',evidence='receipt',remedy='refund',narrative='My refund was not received',language='en')
 def test_extraction_exact(self):
  c=extract_facts('Refund Rs 2,499 on 12-10-2026 not received')
  self.assertEqual((c.amount,c.date),('2499','12-10-2026'))
 def test_missing_not_invented(self):
  c=extract_facts('My parcel never arrived')
  self.assertEqual(c.amount,'');self.assertIn('merchant',missing(c))
 def test_incomplete_rejected(self):
  with self.assertRaises(ValueError):render_notice(Case(merchant='Shop',narrative='refund'))
 def test_out_of_scope(self):self.assertEqual(classify('landlord deposit not returned'),'out_of_scope')
 def test_urgent(self):self.assertEqual(classify('I got a court summons for a return'),'urgent_review')
 def test_unknown(self):self.assertEqual(classify('hello I need help'),'uncertain')
 def test_no_invented_law(self):
  d=render_notice(self.good);self.assertIn('1000',d);self.assertNotIn('Supreme Court',d);self.assertNotIn('Section',d)
 def test_hindi(self):
  c=Case(merchant='दुकान',product='जूते',amount='1000',date='10-10-2026',issue='रिफंड नहीं मिला',contact='ईमेल भेजा',evidence='रसीद',remedy='रिफंड',narrative='रिफंड नहीं मिला',language='hi')
  self.assertIn('शिकायत',render_notice(c))
 def test_block_urgent_draft(self):
  self.good.narrative='I received court summons for my refund'
  with self.assertRaises(ValueError):render_notice(self.good)
 def test_block_out_of_scope_draft(self):
  self.good.narrative='My landlord refused a refund of rent deposit'
  with self.assertRaises(ValueError):render_notice(self.good)
 def test_faq_sources(self):
  response=legal_answer('What is the deadline?')
  self.assertIn('consumer_act',response['sources'])
 def test_unknown_faq_no_false_sources(self):
  self.assertEqual(legal_answer('abcxyz')['sources'],[])
 def test_redaction(self):
  self.assertNotIn('1234 5678 9012',safe_text('Aadhaar 1234 5678 9012'))
 def test_summary(self):
  self.assertTrue(public_summary(self.good)['draft'])
 def test_hindi_triage(self):
  self.assertEqual(classify('दुकानदार ने रिफंड नहीं दिया'),'consumer')
if __name__=='__main__':unittest.main()
