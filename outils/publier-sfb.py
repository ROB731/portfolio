#!/usr/bin/env python3
"""Publie ce dossier dans le projet SFB portfolio-herman-robe (table project_files de Supabase).

Lit la clé dans /opt/sfb/api/.env sans jamais l'afficher. N'écrit que les lignes de ce projet.
Sauvegarder avant : copier project_files (GET) dans un fichier JSON. Relancer : python3 outils/publier-sfb.py
"""
import json,base64,os,re,urllib.request,urllib.error,datetime,mimetypes
env=dict(l.strip().split('=',1) for l in open('/opt/sfb/api/.env') if re.match(r'^(SUPABASE_URL|SUPABASE_SERVICE_ROLE_KEY)=',l))
U=env['SUPABASE_URL'].strip('"'); K=env['SUPABASE_SERVICE_ROLE_KEY'].strip('"')
PID='b6b5aa2a-0ba9-4687-9ccb-52ebb0952225'
H={'apikey':K,'Authorization':'Bearer '+K,'Content-Type':'application/json','Prefer':'return=minimal'}
def call(method,path,body=None):
    r=urllib.request.Request(U+'/rest/v1/'+path,data=json.dumps(body).encode() if body is not None else None,headers=H,method=method)
    try:
        with urllib.request.urlopen(r,timeout=60) as x: return x.status,x.read()
    except urllib.error.HTTPError as e: return e.code,e.read()[:200]
R='/opt/portfolio/'
chemins=['index.html','css/style.css','js/main.js','js/lib/reveal.js','js/lib/carousel.js','assets/icons.svg','assets/photo-profil.jpg','assets/Logo_IRN.png']+sorted('assets/projets/'+f for f in os.listdir(R+'assets/projets'))
mimes={'.html':'text/html','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml','.jpg':'image/jpeg','.png':'image/png'}
st,b=call('GET','project_files?project_id=eq.%s&select=id,path'%PID); existants={x['path']:x['id'] for x in json.loads(b)}
now=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()+'+00:00'; total=0
for c in chemins:
    raw=open(R+c,'rb').read(); ext=os.path.splitext(c)[1]
    binaire = ext in ('.jpg','.png')
    ligne={'content':base64.b64encode(raw).decode() if binaire else raw.decode('utf-8'),'is_binary':binaire,'mime_type':mimes[ext],'size_bytes':len(raw),'updated_at':now}
    if c in existants: st,b=call('PATCH','project_files?id=eq.%s&project_id=eq.%s'%(existants[c],PID),ligne); act='mis à jour'
    else: ligne.update(project_id=PID,path=c); st,b=call('POST','project_files',ligne); act='créé'
    print(st,act,c,len(raw)); total+=len(raw)
    assert st in (200,201,204),b
st,b=call('PATCH','projects?id=eq.%s'%PID,{'updated_at':now}); print(st,'projet : date de mise à jour')
