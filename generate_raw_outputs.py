import json,os
from engine import infer_case,public_summary
root=os.path.dirname(__file__)
with open(os.path.join(root,'test_cases.json'),encoding='utf-8') as f: cases=json.load(f)
for test in cases:
 c=infer_case(test['narrative'],test['language'])
 for key,val in test['fields'].items():setattr(c,key,val)
 output=public_summary(c)
 output['test_id']=test['id']
 with open(os.path.join(root,'raw_outputs',test['id']+'.json'),'w',encoding='utf-8') as f: json.dump(output,f,ensure_ascii=False,indent=2)
print('Generated',len(cases),'raw outputs')
