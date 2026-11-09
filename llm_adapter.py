"""Optional OpenAI-compatible LLM adapter. Does not generate legal citations or opinions.
Use only for summarizing the user's story into a structured draft; confirmation is required.
No API key = free, deterministic operation. Sending text to remote APIs is opt-in.
"""
import json, os
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from engine import FIELDS, safe_text

SYSTEM = '''You are a cautious information extractor for an Indian consumer refund assistant.
Extract ONLY facts explicitly stated in the user's story. Do not guess or interpret statutory law.
Return exactly one JSON object, keys: merchant, product, amount, date, issue, contact, evidence, remedy.
Every value must be a string; if absent leave empty. Do not invent details or law. No markdown.'''

def extract_with_llm(text, api_key, base_url, model):
    endpoint=base_url.rstrip('/') + '/chat/completions'
    parsed=urlparse(endpoint)
    if parsed.scheme!='https' or not parsed.netloc:raise ValueError('HTTPS API endpoint required')
    if not api_key:raise ValueError('API key required')
    data=json.dumps({'model':model,'temperature':0,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':safe_text(text)}]}).encode()
    request=Request(endpoint,data=data,headers={'Authorization':f'Bearer {api_key}','Content-Type':'application/json'})
    with urlopen(request,timeout=18) as response:obj=json.load(response)
    content=obj['choices'][0]['message']['content'].strip()
    if content.startswith('```'):content=content.split('\n',1)[-1].rsplit('```',1)[0]
    result=json.loads(content)
    if not isinstance(result,dict):raise ValueError('Invalid model response')
    return {f:str(result.get(f,'') or '')[:500] for f in FIELDS}
