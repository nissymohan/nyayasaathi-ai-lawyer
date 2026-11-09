from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
import os
root=os.path.dirname(__file__);dest=os.path.join(root,'solution_doc.pdf')
navy=colors.HexColor('#173958');teal=colors.HexColor('#127b83');gray=colors.HexColor('#374b5d')
s=getSampleStyleSheet();s.add(ParagraphStyle(name='Title2',fontName='Helvetica-Bold',fontSize=19,leading=23,textColor=navy,spaceAfter=8));s.add(ParagraphStyle(name='H2b',fontName='Helvetica-Bold',fontSize=10.4,leading=13,textColor=teal,spaceBefore=9,spaceAfter=3));s.add(ParagraphStyle(name='Body2',fontName='Helvetica',fontSize=8.25,leading=11.7,textColor=gray,spaceAfter=5));s.add(ParagraphStyle(name='Tiny2',fontName='Helvetica',fontSize=7.4,leading=10.2,textColor=gray,spaceAfter=4))
p=lambda x,style='Body2':Paragraph(x,s[style]);bullet=lambda x:p('&#8226;  '+x)
def footer(c,d):
 c.saveState();w,h=A4;c.setStrokeColor(colors.HexColor('#d6e5e9'));c.line(16*mm,15*mm,w-16*mm,15*mm);c.setFont('Helvetica',7);c.setFillColor(gray);c.drawString(16*mm,11*mm,'Kuku AI Generalist  |  Problem 2  |  NyayaSaathi');c.drawRightString(w-16*mm,11*mm,f'{d.page} / 2');c.restoreState()
doc=SimpleDocTemplate(dest,pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=15*mm,bottomMargin=20*mm)
story=[p('NYAYA SAATHI','Title2'),p('<b>Problem 2: AI Lawyer for India | Consumer grievance companion</b><br/>Scoped, auditable and demonstrable. This is an information and drafting tool, not legal representation.')]
story.extend([p('01   Problem and why this scope','H2b'),p('For a small online-purchase dispute, a buyer often struggles to organise dates, proof and a written grievance. I deliberately focus on <b>refunds, defective purchases and failed deliveries</b> rather than pretending to know all Indian law. The user leaves with a reviewed case summary, a seller complaint draft and official escalation links.')])
story.append(p('02   What actually works','H2b'))
for x in [
 '<b>Chat-first intake:</b> English/Hindi text conversation with sequential follow-up questions; extracts only clearly stated amounts, dates and issue cues.',
 '<b>Case workspace:</b> eight editable fields (seller, item, amount, date, issue, prior contact, evidence, requested remedy); users confirm before drafting.',
 '<b>Useful output:</b> downloadable grievance letter and JSON case record; evidence checklist, verified links to the National Consumer Helpline and e-Jagriti.',
 '<b>Safety:</b> unfamiliar problems are not silently classified as consumer cases; urgent court/criminal/safety terms and known non-consumer disputes trigger refusal/escalation.',
 '<b>Optional AI and voice:</b> a swappable OpenAI-compatible adapter suggests JSON facts only (explicit user acceptance needed). Voice can be locally transcribed with faster-whisper. Neither feature is required to run the free default app.'
]:story.append(bullet(x))
story.append(p('03   Architecture and model boundaries','H2b'))
rows=[['INPUT','INTAKE + TRIAGE','CONFIRM','ACTION'],['Chat / optional local voice','Rule-based extraction; optional LLM suggests facts','User edits eight fields','Grievance TXT, case JSON, NCH / e-Jagriti']]
t=Table([[p(v,'Tiny2') for v in r] for r in rows],colWidths=[39*mm,48*mm,38*mm,47*mm]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6f2f4')),('INNERGRID',(0,0),(-1,-1),.3,colors.HexColor('#d0dde3')),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#d0dde3')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t)
story.append(p('04   Source grounding and assumptions','H2b'));story.append(p('No LLM generates legal cases or references. FAQ answers are fixed and attached to official sources: India Code (Consumer Protection Act, 2019), Department of Consumer Affairs (NCH, 1915), and e-Jagriti. The default app requires no API or account. A model can only suggest factual fields; all factual claims need user confirmation. No compensation, legal outcome, forum, filing fee or case-specific deadline is promised. No real complaint is automatically submitted.'))
story.append(p('05   How to run and reproduce','H2b'));story.append(p('<b>Windows:</b> <font face="Courier">python -m pip install -r requirements.txt</font>; then <font face="Courier">python -m streamlit run app.py</font>. <b>Tests:</b> <font face="Courier">python -m unittest discover -s tests -v</font>. Synthetic evidence: <font face="Courier">test_cases.json</font> and <font face="Courier">raw_outputs/T01-T12.json</font>. Deployment steps in <font face="Courier">DEPLOYMENT.md</font>.'))
story.append(PageBreak())
story.append(p('VALIDATION, SAFETY & SCALE','Title2'));story.append(p('06   Quality checks and raw runs','H2b'))
story.append(p('<b>15 deterministic engine checks pass</b> (scope, Hindi, missing fields, guarded drafts, source mapping and redaction). <b>12 synthetic raw outputs</b> were generated without hand-editing JSON. This proves code-path behaviour, not real legal correctness or a live browser test.'))
for x in [
 '<b>T01 standard refund:</b> completed fields yield grievance; <b>T03 Hindi:</b> Hindi factual complaint.',
 '<b>T04 missing proof/amount:</b> no invented fields or draft; <b>T05 tenancy:</b> referral outside scope.',
 '<b>T06 court summons:</b> blocks automated drafting; <b>T07 fabricated precedent request:</b> does not invent authority or guarantee a remedy.',
 '<b>T09 ambiguous issue:</b> remains uncertain; <b>T10 Hindi court matter:</b> escalates; <b>T12 defective jacket:</b> replacement request is rendered.'
]:story.append(bullet(x))
story.append(p('07   Honest limitations and failures','H2b'))
story.append(p('Rules are language-limited and can miss slang or veiled urgency; conversational replies can be misclassified as fields, dates and sellers are not verified, and user-entered false facts can appear in a draft. Hindi free-text comprehension remains partial. Voice requires a local download and may mis-transcribe. The optional external LLM can still hallucinate extracted facts, so suggestions require acceptance and cannot author legal positions. <b>Known design failure:</b> a broad “AI lawyer” concept would overpromise law coverage; I narrowed scope and locked legal assertions to checked sources.'))
story.append(p('08   AI use, safety and human-in-the-loop','H2b'))
story.append(p('ChatGPT was used to help implement the code, test plan, interface and documentation. The primary free workflow is deterministic rather than pretending to be a general legal LLM. An optional external model is plug-and-play, but not required to reproduce the results. A user checks the facts and draft before using it; an actual lawyer must advise on court matters, criminal allegations, filing deadlines, jurisdiction, contested entitlement or urgent issues. Sensitive identifiers should not be entered; any external model receives partially redacted text only when the user opts in.'))
story.append(p('09   Scale and success metrics','H2b'))
story.append(p('The input and output contract is a stable Python <font face="Courier">Case</font> record. For scale: stateless hosting, source-update review, regression tests across languages, versioned prompts, optional API-routing and lawyer escalation. Evaluate on real consenting users: completion rate, corrections per case, time to usable draft, safe-refusal recall, unsupported legal claim rate (target zero), and successful navigation to the official grievance channel. These product outcomes are <b>proposed metrics, not measured results</b>.'))
story.append(p('10   Sources & submission','H2b'))
story.append(p('Official sources checked 08 Nov 2026: <font color="#127b83">indiacode.nic.in</font> (Consumer Protection Act 2019); <font color="#127b83">consumeraffairs.gov.in/pages/nch</font> (1915); <font color="#127b83">consumerhelpline.gov.in</font>; <font color="#127b83">e-jagriti.gov.in</font>; <font color="#127b83">nalsa.gov.in</font>. Submit this <b>two-page PDF</b>, a working app or GitHub link, and the raw-outputs folder. Optional walkthrough is up to three minutes. A hosted URL must be created using the owner’s hosting account.'))
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(dest)
