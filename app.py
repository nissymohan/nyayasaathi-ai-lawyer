"""NyayaSaathi Streamlit chat UI. Works without paid APIs. Run: python -m streamlit run app.py"""
import json
import streamlit as st
from engine import (Case, FIELDS, QUESTIONS, SOURCES, classify, extract_facts, guidance,
                    legal_answer, missing, public_summary, render_notice, triage)
from llm_adapter import extract_with_llm

st.set_page_config(page_title='NyayaSaathi | Consumer Legal Help',page_icon='⚖️',layout='wide')
st.markdown('''<style>.block-container{max-width:1120px;padding-top:1.5rem}.stChatMessage{border-radius:16px}h1,h2,h3{letter-spacing:-.02em}.subtitle{color:#527089}</style>''',unsafe_allow_html=True)
st.title('⚖️ NyayaSaathi')
st.markdown('<div class="subtitle">Consumer dispute companion · भारत के लिए उपभोक्ता शिकायत सहायक</div>',unsafe_allow_html=True)
if 'case' not in st.session_state:st.session_state.case=Case()
if 'chat' not in st.session_state:st.session_state.chat=[]
if 'started' not in st.session_state:st.session_state.started=False
if 'draft' not in st.session_state:st.session_state.draft=''
if 'pending' not in st.session_state:st.session_state.pending=None
with st.sidebar:
    st.header('Preferences / विकल्प')
    language=st.radio('Language / भाषा',['English','हिन्दी'],horizontal=True)
    L='hi' if language=='हिन्दी' else 'en'
    st.session_state.case.language=L
    st.divider()
    st.subheader('AI mode (optional)')
    model_mode=st.toggle('Enable optional LLM fact extraction',value=False,help='Only if you provide a trusted HTTPS OpenAI-compatible endpoint. No key needed in default free mode.')
    api_key=base_url=model=''
    if model_mode:
        st.warning('The entered narrative is sent to your chosen external AI provider. Avoid personally identifying details and review their data policies.')
        api_key=st.text_input('API key',type='password')
        base_url=st.text_input('API base URL (HTTPS)',value='https://api.openai.com/v1')
        model=st.text_input('Model',value='gpt-4o-mini')
    st.caption('Default mode is offline, free and deterministic. The optional model only extracts facts; legal claims come from a fixed verified source catalog.')
    if st.button('Start a new case / नया मामला',use_container_width=True):
        st.session_state.case=Case(language=L);st.session_state.chat=[];st.session_state.started=False;st.session_state.pending=None;st.session_state.draft='';st.rerun()
    st.divider()
    st.markdown('**Official information**')
    for source in SOURCES.values():st.markdown(f"- [{source['title']}]({source['url']})")

st.warning('Information and drafting aid only, not an advocate or legal representation. Do not enter Aadhaar, card numbers, passwords, home addresses or case numbers. Consult a qualified lawyer for deadlines, court matters and urgent issues.' if L=='en' else 'यह केवल जानकारी और मसौदा सहायता है, वकील का विकल्प नहीं। आधार, कार्ड, पासवर्ड, घर का पता या केस नंबर न लिखें। समयसीमा, अदालत और गंभीर मामलों के लिए वकील से सलाह लें।')
left,right=st.columns([1.55,1],gap='large')
with left:
    st.subheader('Conversation / बातचीत')
    if not st.session_state.chat:
        st.info('Describe your consumer purchase/refund issue in ordinary language. You can ask follow-up questions any time.' if L=='en' else 'अपनी खरीद/रिफंड समस्या सरल भाषा में बताएं। आप कभी भी सवाल पूछ सकते हैं।')
    for item in st.session_state.chat:
        with st.chat_message(item['role']):st.markdown(item['text'])
    prompt=st.chat_input('E.g. I paid ₹2999 but my online order never arrived...' if L=='en' else 'उदा. मैंने ₹2999 दिए, लेकिन ऑनलाइन ऑर्डर नहीं आया...')
    if prompt:
        st.session_state.chat.append({'role':'user','text':prompt})
        c=st.session_state.case
        if not st.session_state.started:
            c=extract_facts(prompt,L)
            st.session_state.case=c;st.session_state.started=True
            decision=triage(c)
            if decision['status']=='consumer':
                if model_mode and api_key and model and base_url:
                    try:
                        proposed=extract_with_llm(prompt,api_key,base_url,model)
                        st.session_state.pending={k:v for k,v in proposed.items() if v and not getattr(c,k)}
                        if st.session_state.pending:st.toast('AI suggestions available for your review, not yet accepted.')
                    except Exception as e:st.toast('AI unavailable; safe local mode continues. '+type(e).__name__)
                response=('I can help you prepare a factual complaint. I never guarantee outcomes. '+(QUESTIONS[L][missing(c)[0]] if missing(c) else 'Your details look complete; review them on the right.')) if L=='en' else ('मैं शिकायत का तथ्यात्मक मसौदा तैयार करने में मदद करूँगा। परिणाम की गारंटी नहीं है। '+(QUESTIONS[L][missing(c)[0]] if missing(c) else 'जानकारी पूरी है; दाईं ओर जाँचें।'))
            else:response=decision['message']
        else:
            decision=triage(c)
            # Every new message is checked independently; triage never ignores unsafe topics.
            current=classify(prompt)
            question=legal_answer(prompt,L)
            if current=='urgent_review':response=legal_answer(prompt,L)['answer'];st.session_state.pending=None
            elif current=='out_of_scope':response=triage(Case(narrative=prompt,language=L))['message']
            elif decision['status']!='consumer':
                # A new well-defined consumer story can replace an ambiguous/out-of-scope opening.
                if current=='consumer':
                    c=extract_facts(prompt,L);st.session_state.case=c;response=QUESTIONS[L][missing(c)[0]] if missing(c) else ('Review the case summary.' if L=='en' else 'केस की जाँच करें।')
                else:response=decision['message']
            elif question['topic'] not in ('clarify',) and ('?' in prompt or current=='uncertain' or question['topic'] in ('limitation','cost','rights','proof','outcome')):
                response=question['answer']+'\n\n'+('Sources: ' if L=='en' else 'स्रोत: ')+', '.join(f"[{SOURCES[x]['title']}]({SOURCES[x]['url']})" for x in question['sources'])
            else:
                # Conversational fact collection: each reply fills the next unconfirmed field.
                todo=missing(c)
                if todo:
                    field=todo[0]
                    setattr(c,field,prompt.strip()[:500]);todo=missing(c)
                    response=(f'Captured {field}. ' if L=='en' else f'{field} दर्ज किया। ')+(QUESTIONS[L][todo[0]] if todo else ('Details collected. Please review and confirm the draft in the Case panel.' if L=='en' else 'जानकारी मिली। कृपया केस पैनल में जाँचकर मसौदा बनाएं।'))
                else:response=question['answer']
        st.session_state.chat.append({'role':'assistant','text':response})
        st.rerun()
    st.divider()
    with st.expander('Voice input (optional) / आवाज़ से बोलें'):
        st.caption('Works locally if faster-whisper is installed; first use may download a speech model. Copy the editable transcript into chat. No audio upload is sent to an external speech API.')
        audio=st.audio_input('Record story')
        if audio and st.button('Transcribe locally'):
            try:
                from faster_whisper import WhisperModel
                import tempfile,os
                with tempfile.NamedTemporaryFile(delete=False,suffix='.wav') as f:f.write(audio.getvalue());path=f.name
                try:
                    model_asr=WhisperModel('tiny',device='cpu',compute_type='int8')
                    segments,_=model_asr.transcribe(path,language=L)
                    transcript=' '.join(seg.text.strip() for seg in segments)
                finally:os.unlink(path)
                st.text_area('Editable transcript: copy into chat',transcript,height=90)
            except ImportError:st.error('Voice needs: pip install -r requirements-voice-optional.txt')
            except Exception as e:st.error('Transcription unavailable ('+type(e).__name__+'). Please type your story.')
with right:
    st.subheader('Case workspace / केस विवरण')
    c=st.session_state.case
    decision=triage(c) if st.session_state.started else {'status':'not_started','message':'Describe an issue to begin.'}
    if decision['status']=='consumer':st.success('Consumer-purchase scope · proceed cautiously')
    elif decision['status'] in ('urgent_review','out_of_scope','uncertain'):st.error(decision['message'])
    else:st.info('No case yet')
    if st.session_state.pending:
        st.markdown('**Optional AI suggestions — review before accepting**')
        st.json(st.session_state.pending)
        if st.button('Accept AI suggestions'):
            for key,value in st.session_state.pending.items():setattr(c,key,value)
            st.session_state.pending=None;st.rerun()
        if st.button('Reject AI suggestions'):
            st.session_state.pending=None;st.rerun()
    if decision['status']=='consumer':
        st.caption(f"{len(FIELDS)-len(missing(c))}/{len(FIELDS)} facts collected. Everything is editable; AI never silently changes accepted facts.")
        with st.form('case_form'):
            edits={f:st.text_input(QUESTIONS[L][f],value=getattr(c,f),key='field_'+f) for f in FIELDS}
            saved=st.form_submit_button('Save confirmed facts / जानकारी सहेजें',use_container_width=True)
            if saved:
                for key,value in edits.items():setattr(c,key,value.strip()[:500])
                st.session_state.draft='';st.success('Facts confirmed.');st.rerun()
        st.markdown('**Evidence checklist (not uploaded or stored)**')
        for item in ['Invoice/order confirmation','Payment receipt','Seller chat/email','Photos, tracking or return records']:
            st.checkbox(item,key='ev_'+item)
        st.markdown('**Suggested actions**')
        for step in guidance(c)['steps']:st.write('• '+step)
        if missing(c):st.caption('To draft a letter, confirm: '+', '.join(missing(c)))
        else:
            if st.button('Generate draft grievance',type='primary',use_container_width=True):st.session_state.draft=render_notice(c)
            if st.session_state.draft:
                revised=st.text_area('Review and edit before downloading',st.session_state.draft,height=280)
                st.download_button('Download complaint (.txt)',revised.encode('utf-8'),file_name='seller_grievance.txt',mime='text/plain',use_container_width=True)
                st.download_button('Export case (.json)',json.dumps(public_summary(c),ensure_ascii=False,indent=2),file_name='case_summary.json',mime='application/json',use_container_width=True)
                st.caption('No email is sent and no legal filing is made automatically.')
    st.divider()
    st.markdown('**Escalation** · [National Consumer Helpline (1915)](https://consumeraffairs.gov.in/pages/nch) · [e-Jagriti](https://e-jagriti.gov.in/) · [Legal aid](https://nalsa.gov.in/)')
st.caption('Demo privacy: no database. Streamlit session data remains in memory until session ends. Optional LLM sends redacted story to user-configured provider. Never submit sensitive personal information.')
