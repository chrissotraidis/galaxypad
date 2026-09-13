import argparse,pathlib,re,json,statistics
parser=argparse.ArgumentParser();parser.add_argument('--experiment',type=pathlib.Path,required=True);p=parser.parse_args().experiment.resolve()
all={}
for name in ['A1','B','A2']:
 path=p/name/'window.log'
 if not path.exists():continue
 groups={}
 for line in path.read_text().splitlines():
  m=re.search(r'\[GalaxyPad (frame window|performance|runtime counters|audio counters)\] (.*)',line)
  if not m:continue
  vals={k:float(v) for k,v in re.findall(r'(\w+)=(-?\d+(?:\.\d+)?)',m[2])};groups.setdefault(m[1],[]).append(vals)
 f=groups.get('frame window',[]);cpu=groups.get('performance',[])
 if not f:continue
 secs=sum(x['seconds'] for x in f);frames=sum(x['presented'] for x in f)
 a={'windows':len(f),'seconds':secs,'frames':frames,'weighted_fps':frames/secs,'fps_min':min(x['fps'] for x in f),'fps_max':max(x['fps'] for x in f),'cpu_percent_mean':statistics.mean(x['process_cpu_percent'] for x in cpu),'thermal_states':sorted(set(x['thermal_state'] for x in cpu))}
 for group in ['runtime counters','audio counters']:
  vs=groups.get(group,[])
  if len(vs)>1:a[group+'_delta']={k:vs[-1][k]-vs[0][k] for k in vs[0] if k in vs[-1] and not any(z in k for z in ['max','min','peak','available','first','last','mono'])}
 all[name]=a
print(json.dumps(all,indent=2));(p/'measurement.json').write_text(json.dumps(all,indent=2))
