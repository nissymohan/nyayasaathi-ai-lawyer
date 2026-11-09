"""NyayaSaathi: auditable, privacy-conscious consumer-help decision engine.
No generative model is allowed to invent legal sources or send complaints.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
import re
import json
from datetime import date, datetime

SOURCES = {
    'consumer_act': {'title':'Consumer Protection Act, 2019 (India Code)', 'url':'https://www.indiacode.nic.in/indiacode/handle/123456789/15256?sam_handle=123456789%2F1362&view_type=browse'},
    'nch': {'title':'National Consumer Helpline (Government of India)', 'url':'https://consumeraffairs.gov.in/pages/nch'},
    'nch_portal': {'title':'National Consumer Helpline grievance portal', 'url':'https://consumerhelpline.gov.in/'},
    'ejagriti': {'title':'e-Jagriti consumer commission filing portal', 'url':'https://e-jagriti.gov.in/'},
    'legal_aid': {'title':'National Legal Services Authority', 'url':'https://nalsa.gov.in/'},
}
FIELDS = ['merchant', 'product', 'amount', 'date', 'issue', 'contact', 'evidence', 'remedy']
QUESTIONS = {
 'en': {'merchant':'Who is the seller or online platform?', 'product':'What did you purchase or order?', 'amount':'How much did you pay? (₹)', 'date':'When did you pay or place the order?', 'issue':'What exactly went wrong?', 'contact':'What happened when you contacted the seller? (Say “not yet” if you have not.)', 'evidence':'What proof do you have (invoice, payment proof, screenshots, messages)?', 'remedy':'What would you like: refund, replacement or another resolution?'},
 'hi': {'merchant':'विक्रेता या ऑनलाइन प्लेटफ़ॉर्म का नाम क्या है?', 'product':'आपने क्या खरीदा या ऑर्डर किया?', 'amount':'आपने कितने रुपये भुगतान किए?', 'date':'ऑर्डर या भुगतान कब किया?', 'issue':'ठीक-ठीक क्या समस्या हुई?', 'contact':'विक्रेता से बात करने पर क्या जवाब मिला? (यदि नहीं किया, “अभी नहीं” लिखें)', 'evidence':'आपके पास क्या प्रमाण हैं (बिल, पेमेंट, स्क्रीनशॉट, संदेश)?', 'remedy':'आप क्या चाहते हैं: रिफंड, नया सामान या अन्य समाधान?'}
}
LEGAL_FAQ = {
 'process': {'en':'You can first contact the seller in writing with order details and proof. For a pre-litigation grievance, use the National Consumer Helpline (1915). If needed, review consumer commission filing through e-Jagriti. The right forum, timing, and remedies depend on your facts.', 'hi':'पहले विक्रेता को ऑर्डर और प्रमाण सहित लिखित शिकायत भेजें। मुकदमे से पहले की शिकायत के लिए राष्ट्रीय उपभोक्ता हेल्पलाइन (1915) का उपयोग करें। ज़रूरत हो तो e-Jagriti पर उपभोक्ता आयोग में शिकायत की प्रक्रिया देखें। सही मंच, समयसीमा और समाधान तथ्य पर निर्भर करते हैं।', 'sources':['nch','ejagriti']},
 'rights': {'en':'Consumer protection law provides avenues to challenge defective goods, deficiencies in services, and certain unfair practices. Whether a particular claim succeeds cannot be decided from a short chat. See the official Consumer Protection Act, 2019.', 'hi':'उपभोक्ता कानून खराब सामान, सेवाओं में कमी और कुछ अनुचित व्यापार व्यवहार की शिकायत के रास्ते देता है। केवल छोटी बातचीत से किसी दावे की सफलता तय नहीं हो सकती। आधिकारिक उपभोक्ता संरक्षण अधिनियम, 2019 देखें।', 'sources':['consumer_act']},
 'limitation': {'en':'Consumer commission complaints ordinarily have a two-year limitation period from the cause of action under Section 69 of the Consumer Protection Act, 2019, subject to legal exceptions and case-specific interpretation. If a deadline might be close, consult a qualified lawyer immediately.', 'hi':'उपभोक्ता संरक्षण अधिनियम, 2019 की धारा 69 के तहत सामान्यतः कारण उत्पन्न होने से दो वर्ष की समयसीमा है; अपवाद और तथ्य-विशेष व्याख्या लागू हो सकती है। समयसीमा निकट हो तो तुरंत योग्य वकील से बात करें।', 'sources':['consumer_act']},
 'cost': {'en':'Available complaint routes and applicable fees depend on the type of filing and current rules. Check the live official e-Jagriti instructions before filing; this tool does not calculate fees.', 'hi':'शिकायत के प्रकार और मौजूदा नियमों के अनुसार शुल्क अलग हो सकता है। दाखिल करने से पहले e-Jagriti के वर्तमान निर्देश देखें; यह टूल शुल्क की गणना नहीं करता।', 'sources':['ejagriti']},
 'proof': {'en':'Keep the invoice/order number, payment proof, delivery or return records, product photos, and emails or chats with the seller. Only include documents you actually possess and redact sensitive identifiers.', 'hi':'बिल/ऑर्डर नंबर, भुगतान का प्रमाण, डिलीवरी/रिटर्न रिकॉर्ड, सामान की फोटो और विक्रेता से हुई बातचीत रखें। केवल उपलब्ध प्रमाण बताएं और संवेदनशील जानकारी छिपाएं।', 'sources':['nch']},
 'outcome': {'en':'A refund, replacement or compensation may be requested depending on the problem, but no remedy or outcome is guaranteed. Preserve evidence and seek professional guidance when contested.', 'hi':'समस्या के अनुसार रिफंड, बदलकर सामान या मुआवज़े की मांग की जा सकती है, लेकिन कोई नतीजा निश्चित नहीं है। प्रमाण सुरक्षित रखें और विवाद गंभीर हो तो पेशेवर सलाह लें।', 'sources':['consumer_act']}
}
URGENT = [r'\barrest\b',r'\bfir\b',r'\bpolice\b',r'\bcriminal\b',r'\bsummons\b',r'\bcourt notice\b',r'\bcourt order\b',r'\blegal notice received\b',r'\bhearing tomorrow\b',r'\bthreaten(?:ed|ing)?\b',r'\bblackmail\b',r'\bviolence\b',r'\bsuicid',r'\bself.harm\b',r'गिरफ्तार',r'पुलिस',r'एफआईआर',r'कोर्ट.*नोटिस',r'अदालत.*समन',r'धमकी',r'आत्महत्या']
OUTSIDE = [r'\blandlord\b',r'\btenant\b',r'\brent deposit\b',r'\bsalary\b',r'\bemployer\b',r'\bdivorce\b',r'\bcustody\b',r'\binheritance\b',r'\bvisa\b',r'मकान मालिक',r'किराया',r'वेतन',r'तलाक',r'विरासत']
CONSUMER = [r'\brefund\b',r'\breturn\b',r'\bdelive(?:ry|red)\b',r'\bproduct\b',r'\bitem\b',r'\border\b',r'\bbought\b',r'\bpurchased\b',r'\bshop\b',r'\bseller\b',r'\bmerchant\b',r'\bdefective\b',r'\bdamaged\b',r'\bwarranty\b',r'रिफंड',r'ऑर्डर',r'सामान',r'खरीद',r'डिलीवरी',r'खराब',r'दुकानदार',r'विक्रेता',r'वापसी',r'पैसे वापस']

@dataclass
class Case:
    merchant:str=''; product:str=''; amount:str=''; date:str=''; issue:str=''; contact:str=''; evidence:str=''; remedy:str=''; narrative:str=''; language:str='en'
    def to_dict(self):return asdict(self)


def has_any(text, patterns):
    return any(re.search(p,text,flags=re.I) for p in patterns)

def classify(text):
    """Unknown never silently becomes a consumer case."""
    if has_any(text,URGENT): return 'urgent_review'
    if has_any(text,OUTSIDE): return 'out_of_scope'
    if has_any(text,CONSUMER): return 'consumer'
    return 'uncertain'

def extract_facts(text, language='en'):
    c=Case(narrative=text.strip(),language=language)
    m=re.search(r'(?:₹|(?:rs\.?|inr)\s*)([\d,]+(?:\.\d{1,2})?)',text,re.I)
    if m:c.amount=m.group(1).replace(',','')
    d=re.search(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',text)
    if d:c.date=d.group(1)
    if re.search(r'\brefund\b|रिफंड|पैसे वापस',text,re.I):c.issue='Refund not received' if language=='en' else 'रिफंड नहीं मिला'
    elif re.search(r'\bdamaged\b|\bdefective\b|\bbroken\b|खराब',text,re.I):c.issue='Damaged or defective product' if language=='en' else 'खराब सामान'
    elif re.search(r'not delivered|never arrived|undelivered|डिलीवरी नहीं',text,re.I):c.issue='Order not delivered' if language=='en' else 'ऑर्डर नहीं मिला'
    return c

# Compatibility with prior prototype
infer_case=extract_facts

def missing(c):return [f for f in FIELDS if not str(getattr(c,f)).strip()]
def next_question(c):
    todo=missing(c)
    return QUESTIONS[c.language][todo[0]] if todo else None

def clean(s):return re.sub(r'[\r\n\t]+',' ',str(s)).strip()[:1000]

def safe_text(s):
    # Redact common high-risk Indian identifiers before text is passed to optional LLM.
    s=re.sub(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b','[REDACTED_ID]',s)
    s=re.sub(r'\b(?:\d[ -]*?){13,19}\b','[REDACTED_CARD]',s)
    return s[:2500]

def legal_answer(text, language='en'):
    t=text.lower()
    if has_any(t,URGENT):
        return {'topic':'urgent','answer':('This could involve a deadline, court process, safety or criminal allegations. Please consult a qualified lawyer promptly. If anyone is in immediate danger, contact local emergency services.' if language=='en' else 'इस मामले में समयसीमा, अदालत, सुरक्षा या आपराधिक आरोप हो सकते हैं। जल्द योग्य वकील से सलाह लें। तत्काल खतरा हो तो स्थानीय आपात सेवा को संपर्क करें।'),'sources':['legal_aid']}
    topics=[('limitation',[r'\bdeadline\b',r'\btime limit\b',r'\btoo late\b',r'\bhow long\b',r'\byears?\b',r'समयसीमा',r'कितने दिन']),('cost',[r'\bfee\b',r'\bcost\b',r'\bcharge\b',r'खर्च',r'शुल्क']),('proof',[r'\bevidence\b',r'\bproof\b',r'\bdocuments?\b',r'प्रमाण',r'सबूत']),('rights',[r'\bright\b',r'\blaw\b',r'\blegal\b',r'अधिकार',r'कानून']),('outcome',[r'\bcompensation\b',r'\bwin\b',r'\breplacement\b',r'\bguarantee\b',r'मुआवजा',r'जीत',r'बदलकर']),('process',[r'\bhow\b',r'\bwhere\b',r'\bcomplain\b',r'\bnext\b',r'\brefus',r'\bescalat',r'कैसे',r'कहाँ',r'शिकायत'])]
    for topic,patterns in topics:
        if has_any(t,patterns):return {'topic':topic,'answer':LEGAL_FAQ[topic][language],'sources':LEGAL_FAQ[topic]['sources']}
    return {'topic':'clarify','answer':('I can help with consumer purchase/refund disputes. Tell me what happened, or ask about next steps, evidence, refunds, deadlines or official filing.' if language=='en' else 'मैं खरीद और रिफंड संबंधी उपभोक्ता विवाद में मदद कर सकता हूँ। समस्या बताएं या अगले कदम, प्रमाण, रिफंड, समयसीमा या शिकायत दाखिल करने के बारे में पूछें।'),'sources':[]}

def triage(case):
    status=classify(case.narrative+' '+case.issue)
    if status=='urgent_review':
        message='Potentially urgent or high-stakes legal matter. Seek a qualified lawyer promptly; do not rely on this assistant for court deadlines or criminal/safety issues.' if case.language=='en' else 'यह गंभीर या तात्कालिक कानूनी मामला हो सकता है। जल्द योग्य वकील से सलाह लें; अदालत की समयसीमा या सुरक्षा/आपराधिक मामले के लिए इस टूल पर निर्भर न रहें।'
    elif status=='out_of_scope':
        message='This service focuses on consumer purchases, defective goods and refunds; it does not advise on employment, tenancy or family disputes.' if case.language=='en' else 'यह सेवा खरीद, खराब सामान और रिफंड की शिकायतों तक सीमित है; रोजगार, किराया या पारिवारिक विवाद इसमें शामिल नहीं हैं।'
    elif status=='uncertain':
        message='I cannot confidently identify this as a consumer purchase dispute. Please describe the purchase, seller and problem, or consult a qualified adviser.' if case.language=='en' else 'यह स्पष्ट नहीं कि यह उपभोक्ता खरीद विवाद है। कृपया खरीद, विक्रेता और समस्या बताएं, या योग्य सलाहकार से बात करें।'
    else:message='Within this prototype’s consumer-purchase scope; no legal result is guaranteed.' if case.language=='en' else 'यह मामला इस प्रोटोटाइप के उपभोक्ता-खरीद दायरे में है; कानूनी परिणाम निश्चित नहीं है।'
    return {'status':status,'message':message}

def guidance(case):
    decision=triage(case)
    if decision['status']!='consumer':return {**decision,'steps':[],'sources':SOURCES}
    steps=(['Send a factual written grievance to the seller and preserve a copy.','If unresolved, contact the National Consumer Helpline at 1915 or its official portal.','For formal consumer commission filing, consult the current e-Jagriti guidance and assess deadlines/jurisdiction with a qualified professional.'] if case.language=='en' else ['विक्रेता को तथ्यात्मक लिखित शिकायत भेजें और उसकी कॉपी रखें।','समाधान न मिले तो राष्ट्रीय उपभोक्ता हेल्पलाइन 1915 या आधिकारिक पोर्टल पर जाएं।','उपभोक्ता आयोग में औपचारिक शिकायत के लिए e-Jagriti के मौजूदा निर्देश देखें और समयसीमा/क्षेत्राधिकार वकील से जाँचें।'])
    return {**decision,'steps':steps,'sources':SOURCES}

def render_notice(case):
    if triage(case)['status']!='consumer':raise ValueError('Unsupported or high-risk case; no automatic draft.')
    if missing(case):raise ValueError('Confirm all eight fields before drafting.')
    v={f:clean(getattr(case,f)) for f in FIELDS}
    if case.language=='hi':
        return f'''विषय: {v['merchant']} को उपभोक्ता शिकायत – समाधान का अनुरोध

महोदय/महोदया,

मैंने {v['date']} को {v['product']} के लिए ₹{v['amount']} का भुगतान किया था। मुझे निम्न समस्या हुई: {v['issue']}।

पहले किया गया संपर्क: {v['contact']}।
मेरे पास उपलब्ध साक्ष्य: {v['evidence']}।
मेरा अनुरोधित समाधान: {v['remedy']}।

कृपया मेरी शिकायत की जांच कर लिखित रूप से उत्तर दें और उपयुक्त समाधान बताएं। कृपया शिकायत प्राप्त होने की पुष्टि भी करें।

सादर,
[आपका नाम]
[संपर्क विवरण]
[तारीख]

नोट: यह उपयोगकर्ता-समीक्षा के लिए शिकायत का मसौदा है; किसी वकील द्वारा सत्यापित कानूनी नोटिस नहीं।'''
    return f'''Subject: Consumer grievance – request for resolution ({v['merchant']})

Dear Customer Support,

I paid INR {v['amount']} on {v['date']} for {v['product']}. The issue is: {v['issue']}.

Earlier contact with the seller: {v['contact']}.
Evidence I currently have: {v['evidence']}.
Resolution I request: {v['remedy']}.

Please review this grievance, confirm receipt, and respond in writing with an appropriate resolution.

Sincerely,
[Your name]
[Contact details]
[Date]

Note: User-review draft of a seller grievance, not a lawyer-vetted legal notice.'''

def public_summary(case):
    g=guidance(case)
    return {'case':case.to_dict(),'missing':missing(case),'triage':triage(case),'guidance':g,'draft':render_notice(case) if not missing(case) and g['status']=='consumer' else None}
