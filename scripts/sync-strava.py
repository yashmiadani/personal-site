import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

def post(url, data):
    req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as r:return json.load(r)
def get(url, token):
    req=urllib.request.Request(url,headers={'Authorization':f'Bearer {token}'})
    with urllib.request.urlopen(req) as r:return json.load(r)
client_id=os.environ['STRAVA_CLIENT_ID']; secret=os.environ['STRAVA_CLIENT_SECRET']; refresh=os.environ['STRAVA_REFRESH_TOKEN']
tok=post('https://www.strava.com/oauth/token',{'client_id':client_id,'client_secret':secret,'grant_type':'refresh_token','refresh_token':refresh})
if tok.get('refresh_token') and tok['refresh_token']!=refresh:
    path=os.environ.get('STRAVA_REFRESH_TOKEN_FILE','/tmp/strava-refresh-token')
    with open(path,'w') as f:f.write(tok['refresh_token'])
    os.chmod(path,0o600)
year=datetime.now(timezone.utc).year; after=int(datetime(year,1,1,tzinfo=timezone.utc).timestamp()); page=1; runs=[]
while True:
    batch=get(f'https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=200&page={page}',tok['access_token'])
    runs.extend(a for a in batch if a.get('sport_type') in ('Run','TrailRun','VirtualRun') or a.get('type')=='Run')
    if len(batch)<200:break
    page+=1
out={'year':year,'km':round(sum(float(a.get('distance',0)) for a in runs)/1000,1),'runs':len(runs),'updatedAt':datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}
open('running-data.js','w').write('window.YASHMI_RUNNING = '+json.dumps(out,separators=(',',':'))+';\n')
print(f"Synced {out['runs']} runs / {out['km']} km for {year}")
