# KI-generiert (Claude, Anthropic). Aufruf: python3 werkzeuge/stilcheck.py prozesse/team2  (benötigt: pip install lxml)
# Prüft Label-Matching (Stiehl Regeln 10-12, 14, 16, 17) und Camunda-7-Pflichtattribute.
import glob, sys
from lxml import etree
NS={'b':'http://www.omg.org/spec/BPMN/20100524/MODEL','c':'http://camunda.org/schema/1.0/bpmn'}
C='{http://camunda.org/schema/1.0/bpmn}'
D=sys.argv[1]; files={}; fehler=[]
for f in glob.glob(D+'/*.bpmn'):
    t=etree.parse(f); p=t.find('.//b:process[@isExecutable="true"]',NS); files[p.get('id')]=(f.split('/')[-1],t,p)
def ends(p): return sorted(e.get('name') for e in p.findall('b:endEvent',NS))
def msgs(t): return sorted(m.get('name') for m in t.findall('.//b:messageFlow',NS))
for pid,(fn,t,p) in files.items():
    ids={}
    # Regel 16/17: eindeutige Namen
    for tag in ('endEvent',):
        ns=[e.get('name') for e in p.findall('b:'+tag,NS)]
        if len(ns)!=len(set(ns)): fehler.append(f'{fn}: doppelte Endereignis-Namen {ns}')
    acts=[e.get('name') for e in p if etree.QName(e).localname.endswith('Task') or etree.QName(e).localname=='callActivity']
    if len(acts)!=len(set(acts)): fehler.append(f'{fn}: doppelte Aktivitätsnamen')
    if len(acts)>10: fehler.append(f'{fn}: mehr als 10 Aktivitäten ({len(acts)})')
    if not p.get(C+'historyTimeToLive'): fehler.append(f'{fn}: historyTimeToLive fehlt')
    for e in p:
        ln=etree.QName(e).localname
        if ln in ('serviceTask','sendTask','businessRuleTask') and not (e.get(C+'topic') and e.get(C+'type')=='external'):
            fehler.append(f'{fn}: {e.get("id")} ohne external topic')
        if ln=='userTask' and not e.get(C+'candidateGroups'): fehler.append(f'{fn}: {e.get("id")} ohne candidateGroups')
        if ln=='userTask' and e.find('.//c:formData',NS) is None: fehler.append(f'{fn}: {e.get("id")} ohne Formular')
        if ln=='exclusiveGateway':
            outs=[s for s in p.findall('b:sequenceFlow',NS) if s.get('sourceRef')==e.get('id')]
            if len(outs)>1:
                if not e.get('name'): fehler.append(f'{fn}: verzweigendes Gateway {e.get("id")} ohne Frage')
                for s in outs:
                    if s.find('b:conditionExpression',NS) is None and e.get('default')!=s.get('id'): fehler.append(f'{fn}: {s.get("id")} ohne Bedingung')
                    if not s.get('name'): fehler.append(f'{fn}: Ausgang {s.get("id")} unbeschriftet')
            ins=[s for s in p.findall('b:sequenceFlow',NS) if s.get('targetRef')==e.get('id')]
            if len(ins)>1 and len(outs)>1: fehler.append(f'{fn}: Gateway {e.get("id")} verzweigt und führt zusammen (Regel 22)')
        if ln in ('task','serviceTask','sendTask','receiveTask','userTask','businessRuleTask','callActivity'):
            ins=[s for s in p.findall('b:sequenceFlow',NS) if s.get('targetRef')==e.get('id')]
            if len(ins)>2: fehler.append(f'{fn}: {e.get("name")} hat {len(ins)} eingehende Linien (max. 2)')
    for ca in p.findall('b:callActivity',NS):
        ce=ca.get('calledElement')
        if ce not in files: fehler.append(f'{fn}: calledElement {ce} fehlt'); continue
        cfn,ct,cp=files[ce]
        # Label-Matching: Gateway direkt nach Call Activity
        nxt=[s.get('targetRef') for s in p.findall('b:sequenceFlow',NS) if s.get('sourceRef')==ca.get('id')]
        gws=[p.find(f'b:exclusiveGateway[@id="{n}"]',NS) for n in nxt]; gws=[g for g in gws if g is not None and len([x for x in p.findall('b:sequenceFlow',NS) if x.get('sourceRef')==g.get('id')])>1]
        kind_ends=[e.get('name') for e in cp.findall('b:endEvent',NS) if not any(s.get('targetRef')==e.get('id') and cp.find(f'.//*[@id="{s.get("sourceRef")}"]',NS).tag.endswith('Task') and 'erinner' in (cp.find(f'.//*[@id="{s.get("sourceRef")}"]',NS).get('name') or '').lower() for s in cp.findall('b:sequenceFlow',NS))]
        if gws:
            gates=sorted(s.get('name') for s in p.findall('b:sequenceFlow',NS) if s.get('sourceRef')==gws[0].get('id'))
            if gates!=sorted(kind_ends): fehler.append(f'{fn}: Label-Matching {ca.get("name")}: Gates {gates} != Endereignisse {sorted(kind_ends)}')
            else: print(f'Label-Matching ok: {fn} {ca.get("name")} -> {gates}')
        # Regel 14: Nachrichtenflüsse Eltern/Kind gleich benannt
        pm=sorted(m.get('name') for m in t.findall('.//b:messageFlow',NS) if ca.get('id') in (m.get('sourceRef'),m.get('targetRef')))
        if pm!=msgs(ct): fehler.append(f'{fn}: Nachrichtenflüsse {ca.get("name")} {pm} != Kind {msgs(ct)}')
        elif pm: print(f'Nachrichtenflüsse ok: {ca.get("name")} {pm}')
    # Regel 13: jede Send-/Receive-/Nachrichtenereignis hat Nachrichtenfluss
    mf=set(); [mf.update([m.get('sourceRef'),m.get('targetRef')]) for m in t.findall('.//b:messageFlow',NS)]
    for e in p:
        ln=etree.QName(e).localname
        if ln in ('sendTask','receiveTask') or (ln in ('intermediateCatchEvent','startEvent') and e.find('b:messageEventDefinition',NS) is not None):
            if e.get('id') not in mf: fehler.append(f'{fn}: {e.get("name")} ohne Nachrichtenfluss (Regel 13)')
print('\nFEHLER:' if fehler else '\nKeine Fehler.'); [print(' -',x) for x in fehler]
