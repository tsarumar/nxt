"""Omar Zid: reproducible desktop models for four LEGO NXT projects.

All values are simulated, not measured on physical hardware. SI-derived mm/s,
mm, radians, seconds are used internally. Run with Python + numpy + Pillow.
"""
from pathlib import Path
import math, json, csv, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'projects'
WORK = ROOT / 'data' / 'report_content'
D, B, BODY_R, SENSOR_FRONT = 56.0, 120.0, 75.0, 70.0

def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def clip(x,lo,hi): return min(hi,max(lo,x))

class Robot:
    """Exact constant-wheel-speed integration; independent encoder odometry."""
    def __init__(self, x=0., y=0., theta=0., dt=.02):
        self.x,self.y,self.th=x,y,theta
        self.ox,self.oy,self.ot=x,y,theta
        self.dt,self.t=dt,0.
        self.left,self.right,self.distance=0.,0.,0.
        self.trace=[]
    def step(self,v,omega,phase,dt=None,extra=None):
        dt=self.dt if dt is None else dt
        vl,vr=v-B*omega/2,v+B*omega/2
        dl,dr=vl*dt,vr*dt
        ds,dth=(dl+dr)/2,(dr-dl)/B
        if abs(dth)<1e-12:
            self.x+=ds*math.cos(self.th);self.y+=ds*math.sin(self.th)
            self.ox+=ds*math.cos(self.ot);self.oy+=ds*math.sin(self.ot)
        else:
            radius=ds/dth
            self.x+=radius*(math.sin(self.th+dth)-math.sin(self.th))
            self.y+=radius*(-math.cos(self.th+dth)+math.cos(self.th))
            self.ox+=radius*(math.sin(self.ot+dth)-math.sin(self.ot))
            self.oy+=radius*(-math.cos(self.ot+dth)+math.cos(self.ot))
        self.th+=dth;self.ot+=dth;self.t+=dt;self.distance+=abs(ds)
        self.left+=dl/(math.pi*D)*360;self.right+=dr/(math.pi*D)*360
        row=dict(t_s=self.t,x_mm=self.x,y_mm=self.y,heading_rad=self.th,
                 odo_x_mm=self.ox,odo_y_mm=self.oy,left_deg=self.left,right_deg=self.right,
                 v_mm_s=v,omega_rad_s=omega,phase=phase)
        if extra: row.update(extra)
        self.trace.append(row)
    def turn(self,target,phase='TURN'):
        while abs(wrap(target-self.ot))>1e-8:
            err=wrap(target-self.ot)
            self.step(0,math.copysign(.9,err),phase,min(self.dt,abs(err)/.9))
    def straight(self,length,heading,phase,speed=110.,callback=None):
        traveled=0.
        while traveled<length-1e-8:
            ds=min(speed*self.dt,length-traveled)
            self.step(math.copysign(speed,length),clip(4*wrap(heading-self.ot),-.7,.7),phase,ds/speed)
            traveled+=ds
            if callback: callback(self)
    def reverse(self,length,heading,phase='RETREAT',speed=110.):
        traveled=0.
        while traveled<length-1e-8:
            ds=min(speed*self.dt,length-traveled)
            self.step(-speed,clip(4*wrap(heading-self.ot),-.7,.7),phase,ds/speed);traveled+=ds

def save_csv(path,rows):
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def font(size=22):
    for p in ['C:/Windows/Fonts/segoeui.ttf','C:/Windows/Fonts/arial.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def plot(path,title,series,xlabel='x (mm)',ylabel='y (mm)',bounds=None,circles=None,rects=None):
    im=Image.new('RGB',(1200,800),'#f6f8fc');g=ImageDraw.Draw(im)
    g.text((65,24),title,fill='#12263a',font=font(28))
    allpts=[p for s in series for p in s[1]]
    if bounds: xmin,xmax,ymin,ymax=bounds
    else:
        xs=[p[0] for p in allpts];ys=[p[1] for p in allpts]
        xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
        dx=max(1,xmax-xmin);dy=max(1,ymax-ymin)
        xmin-=dx*.05;xmax+=dx*.05;ymin-=dy*.1;ymax+=dy*.1
    def tr(p):return (100+(p[0]-xmin)/(xmax-xmin)*1010,690-(p[1]-ymin)/(ymax-ymin)*585)
    for k in range(6):
        xx=xmin+(xmax-xmin)*k/5;yy=ymin+(ymax-ymin)*k/5
        px=tr((xx,ymin))[0];py=tr((xmin,yy))[1]
        g.line((px,105,px,690),fill='#dce3ec');g.line((100,py,1110,py),fill='#dce3ec')
        g.text((px-25,700),f'{xx:.0f}',fill='#425466',font=font(17))
        g.text((20,py-10),f'{yy:.0f}',fill='#425466',font=font(17))
    for c in circles or []:
        x,y,r,col=c;a=tr((x-r,y+r));b=tr((x+r,y-r));g.ellipse((*a,*b),outline=col,width=3)
    for r in rects or []:
        x1,y1,x2,y2=r; a=tr((x1,y2));b=tr((x2,y1));g.rectangle((*a,*b),fill='#ead5cf',outline='#ab4e38',width=2)
    for idx,(name,pts,col) in enumerate(series):
        mapped=[tr(p) for p in pts]
        if len(mapped)>1:g.line(mapped,fill=col,width=3)
        g.line((110+idx*320,65,142+idx*320,65),fill=col,width=4)
        g.text((151+idx*320,50),name,fill='#334155',font=font(18))
    g.text((510,751),xlabel,fill='#334155',font=font(20));g.text((12,70),ylabel,fill='#334155',font=font(18))
    im.save(path)

def ray_circle(sx,sy,angle,cx,cy,r):
    ux,uy=math.cos(angle),math.sin(angle);qx,qy=cx-sx,cy-sy
    proj=qx*ux+qy*uy;perp2=qx*qx+qy*qy-proj*proj
    if perp2>r*r:return math.inf
    root=math.sqrt(max(0,r*r-perp2));near=proj-root
    return near if near>=0 else math.inf

def ring_sim(layout,tag):
    ring_r,pusher,object_r,inner_band=600.,150.,20.,580.
    assert all(math.hypot(x,y)>=180 for x,y in layout), 'Objects overlap the initial swept pusher area'
    rb=Robot();items=[dict(x=float(x),y=float(y),ejected=False,id=i+1) for i,(x,y) in enumerate(layout)]
    ejects=[];scans=0;coverage=0;min_margin=math.inf
    while scans<32:
        scans+=1;hits=[]
        # One degree angular coverage, using physical in-place turning.
        for degree in range(360):
            rb.turn(math.radians(degree),'SCAN')
            sx,sy=rb.x+SENSOR_FRONT*math.cos(rb.th),rb.y+SENSOR_FRONT*math.sin(rb.th)
            candidates=[(ray_circle(sx,sy,rb.th,q['x'],q['y'],object_r),q['id']) for q in items if not q['ejected']]
            dist,idx=min(candidates,default=(math.inf,0))
            if dist<900:hits.append((dist+SENSOR_FRONT,rb.th,idx))
        coverage=360
        if not hits:break
        # Use minimum-range hit: closest approach makes bearing almost central.
        _,bearing,idx=min(hits,key=lambda z:z[0])
        rb.turn(bearing,'ALIGN');active=items[idx-1]
        def contact(r):
            nonlocal min_margin
            cx,cy=math.cos(r.th),math.sin(r.th)
            along=active['x']*cx+active['y']*cy
            across=-active['x']*cy+active['y']*cx
            if along<=math.hypot(r.x,r.y)+pusher+object_r and abs(across)<40:
                active['x']=(math.hypot(r.x,r.y)+pusher+object_r)*cx
                active['y']=(math.hypot(r.x,r.y)+pusher+object_r)*cy
            min_margin=min(min_margin,ring_r-max(math.hypot(r.x,r.y)+BODY_R,math.hypot(r.x,r.y)+pusher))
        rb.straight(inner_band-pusher,bearing,'PUSH',110,contact)
        # Black border is 20 mm wide. Calibrated low-speed completion travel.
        rb.straight(ring_r-inner_band,bearing,'BOUNDARY_FINISH',40,contact)
        active['ejected']=math.hypot(active['x'],active['y'])>=ring_r+object_r-1e-6
        if not active['ejected']:raise AssertionError('Pusher failed to expel object')
        ejects.append(dict(id=idx,x_mm=active['x'],y_mm=active['y'],time_s=rb.t))
        rb.reverse(ring_r-pusher,bearing)
    if any(not q['ejected'] for q in items):raise AssertionError('False clean stop')
    lcd=Image.new('RGB',(500,320),'#92a880');draw=ImageDraw.Draw(lcd)
    draw.ellipse((125,50,375,300),outline='#183323',width=3)
    for e in ejects:
        px=250+e['x_mm']/600*125;py=175-e['y_mm']/600*125
        draw.ellipse((px-4,py-4,px+4,py+4),fill='#183323')
        draw.text((px+5,py-10),str(e['id']),fill='#183323',font=font(14))
    draw.text((14,7),f'CLEAN  {len(ejects)} OUT',fill='#183323',font=font(23))
    lcd.save(OUT/f'p1_{tag}_lcd.png')
    save_csv(OUT/f'p1_{tag}_trace.csv',rb.trace);save_csv(OUT/f'p1_{tag}_ejections.csv',ejects or [dict(id='',x_mm='',y_mm='',time_s='')])
    return dict(tag=tag,object_count=len(items),expelled=len(ejects),clean_stop=True,
                time_s=rb.t,path_mm=rb.distance,verification_degrees=coverage,scans=scans,
                min_entire_robot_margin_mm=450 if not items else max(0.,min_margin),
                min_chassis_margin_mm=600-450-BODY_R if items else 600-BODY_R,
                trace=rb.trace,ejections=ejects,initial=layout)

def make_card():
    groups=[(4,8.,7.,35.),(7,5.,6.,55.),(3,12.,10.,25.)]
    bars=[];x=20.
    for group,(n,width,gap,height) in enumerate(groups,1):
        for k in range(n):bars.append(dict(x1=x,x2=x+width,height=height,group=group));x+=width+(gap if k<n-1 else 0)
        x+=35.
    return bars,300.

def scan_card(speed,seed=0,phase=0.,y=0.):
    bars,length=make_card();rng=np.random.default_rng(seed);dt=.01;spot=4.;debounce=3
    state='WHITE';pending=0;count=0;rows=[];groups=[];last_exit=None;groupcount=0
    t=phase
    while speed*t<=length:
        x=speed*t
        dark=sum(max(0,min(x+spot/2,b['x2'])-max(x-spot/2,b['x1'])) for b in bars if abs(y)<=b['height']/2)
        reflect=clip(80-60*min(1,dark/spot)+float(rng.normal(0,2)),0,100)
        if state=='WHITE':
            pending=pending+1 if reflect<35 else 0
            if pending>=debounce:
                if last_exit is not None and x-last_exit>=22 and groupcount:groups.append(groupcount);groupcount=0
                state='BLACK';count+=1;groupcount+=1;pending=0
        else:
            pending=pending+1 if reflect>65 else 0
            if pending>=debounce:state='WHITE';pending=0;last_exit=x
        rows.append(dict(t_s=t,x_mm=x,reflectance=reflect,count=count,state=state,group= len(groups)+1))
        t+=dt
    if groupcount:groups.append(groupcount)
    return dict(speed_mm_s=speed,seed=seed,phase_s=phase,total=count,expected=14,
                groups=groups,time_s=t-phase,trace=rows,y_mm=y)

def scanner_suite():
    runs=[]
    for speed in [40.,60.,90.,150.,300.]:
        for seed in range(30):runs.append(scan_card(speed,seed,seed*.01/30))
    summary=[]
    for speed in [40.,60.,90.,150.,300.]:
        s=[r for r in runs if r['speed_mm_s']==speed]
        summary.append(dict(speed_mm_s=speed,correct=sum(r['total']==14 for r in s),runs=len(s),
                            min_count=min(r['total'] for r in s),max_count=max(r['total'] for r in s),time_s=s[0]['time_s']))
    nominal=scan_card(60.,7,.003);offset=scan_card(60.,7,.003,y=18.)
    save_csv(OUT/'p2_nominal_trace.csv',nominal['trace'])
    save_csv(OUT/'p2_trials.csv',[{k:v for k,v in r.items() if k not in ['trace','groups']}|{'groups':','.join(map(str,r['groups']))} for r in runs])
    log=OUT/'Scanner.txt';log.write_text('Omar Zid | SIMULATED scanner results | count,time_s,speed_mm_s,seed\n',encoding='utf-8')
    mailbox=[];bt=[]
    for r in [nominal,scan_card(40.,8,.006)]:
        with open(log,'a',encoding='utf-8') as f:f.write(f"{r['total']},{r['time_s']:.3f},{r['speed_mm_s']:.1f},{r['seed']}\n")
        payload=f"COUNT={r['total']};TIME_MS={round(r['time_s']*1000)}";mailbox.append(payload)
        received=mailbox.pop(0);assert received==payload
        bt.append(dict(transport='EMULATED in-process mailbox; no radio hardware',sent=payload,received=received,matched=True))
    (OUT/'p2_emulated_bluetooth.json').write_text(json.dumps(bt,indent=2),encoding='utf-8')
    plot(OUT/'p2_reflectance.png','Scanner: sampled reflectance, speed 60 mm/s',
         [('Reflectance',[(r['x_mm'],r['reflectance']) for r in nominal['trace']],'#2864ab'),
          ('Count × 5',[(r['x_mm'],r['count']*5) for r in nominal['trace']],'#ba4b31')],ylabel='Reflectance / count × 5',bounds=(0,300,0,100))
    return dict(trials=summary,nominal=nominal,offset=offset,bluetooth=bt,bars=make_card()[0])

def ray_rect(x,y,a,r):
    dx,dy=math.cos(a),math.sin(a);lo,hi=0.,math.inf
    for o,d,mn,mx in [(x,dx,r[0],r[2]),(y,dy,r[1],r[3])]:
        if abs(d)<1e-12:
            if o<mn or o>mx:return math.inf
        else:
            t1,t2=(mn-o)/d,(mx-o)/d
            lo=max(lo,min(t1,t2));hi=min(hi,max(t1,t2))
    return lo if hi>=lo else math.inf

def rectangle_distance(x,y,r):
    return math.hypot(max(r[0]-x,0,x-r[2]),max(r[1]-y,0,y-r[3]))

def avoid_sim(N_cm,obstacles,tag,noise_mm=0.):
    rb=Robot();rng=np.random.default_rng(91);target=N_cm*10.;seen=0;checks=[]
    def sonar():
        sx,sy=rb.x+SENSOR_FRONT*math.cos(rb.th),rb.y+SENSOR_FRONT*math.sin(rb.th)
        d=min((ray_rect(sx,sy,rb.th,r) for r in obstacles),default=math.inf)
        measured=d+float(rng.uniform(-noise_mm,noise_mm)) if math.isfinite(d) else 2550.
        checks.append(dict(t_s=rb.t,x_mm=rb.x,y_mm=rb.y,heading_rad=rb.th,range_mm=measured,
                           phase=rb.trace[-1]['phase'] if rb.trace else 'START'))
        return measured
    def probe(angle):
        old=rb.ot;rb.turn(angle,'PROBE_TURN');d=sonar();rb.turn(old,'PROBE_RETURN');return d
    # Unknown obstacle dimensions: only ray measurements enter control decisions.
    while rb.ox<target-1e-7:
        d=sonar()
        if d>200:
            rb.straight(min(10.,target-rb.ox),0,'FORWARD',120);continue
        seen+=1;rb.turn(-math.pi/2,'TURN_RIGHT')
        budget=0
        while probe(0)<900:
            rb.straight(25.,-math.pi/2,'FIND_NEAR_CORNER',100);budget+=1
            if budget>80:raise AssertionError('Obstacle height exceeds search budget')
        rb.straight(BODY_R+35.,-math.pi/2,'CORNER_CLEARANCE',100)
        rb.turn(0,'TURN_ALONG_WALL');wall_seen=False;budget=0
        while True:
            side=probe(math.pi/2)
            if side<900:wall_seen=True
            if wall_seen and side>=900:break
            rb.straight(25.,0,'FOLLOW_SIDE',100);budget+=1
            if budget>100:raise AssertionError('No far corner or excessive width')
        rb.straight(BODY_R+35.,0,'FAR_CORNER_CLEARANCE',100)
        rb.turn(math.pi/2,'RETURN_TO_LINE');rb.straight(abs(rb.oy),math.pi/2,'RETURN_TO_LINE',100)
        rb.turn(0,'RESUME_LINE')
        if rb.ox>target+5:raise AssertionError('Obstacle detour overshoots configured endpoint')
    clearances=[min((rectangle_distance(row['x_mm'],row['y_mm'],r)-BODY_R for r in obstacles),default=math.inf) for row in rb.trace]
    minclear=min(clearances) if obstacles else None
    assert minclear is None or minclear>30
    assert abs(rb.x-target)<1e-5 and abs(rb.y)<1e-5
    for row,clear in zip(rb.trace,clearances):row['chassis_clearance_mm']=clear if math.isfinite(clear) else ''
    save_csv(OUT/f'p3_{tag}_trace.csv',rb.trace);save_csv(OUT/f'p3_{tag}_sonar.csv',checks)
    return dict(tag=tag,N_cm=N_cm,endpoint_x_mm=rb.x,endpoint_y_mm=rb.y,path_mm=rb.distance,
                time_s=rb.t,obstacles_avoided=seen,min_clearance_mm=minclear,
                max_line_deviation_mm=max(abs(r['y_mm']) for r in rb.trace),trace=rb.trace,obstacles=obstacles,noise_mm=noise_mm)

def line_sim(mode='PID',seed=13,tag=None):
    gains={'P':(.85,0.,0.),'PI':(.70,.28,0.),'PID':(.80,.25,.035)}
    kp,ki,kd=gains[mode];dt=.01;R=350.;edge=360.;ahead=35.;v0=110.;tau=.10
    start_r=math.sqrt(edge*edge-ahead*ahead)+3.
    start_a=-math.atan2(ahead,start_r)
    rb=Robot(start_r*math.cos(start_a),start_r*math.sin(start_a),start_a+math.pi/2,dt)
    rng=np.random.default_rng(seed);integ=0.;deriv=0.;last=0.;vl=vr=v0;rows=[]
    start_angle=math.atan2(rb.y,rb.x);unwrapped=0.;previous=start_angle;black_hold=0.;done=False
    for k in range(12000):
        sx,sy=rb.x+ahead*math.cos(rb.th),rb.y+ahead*math.sin(rb.th);sr=math.hypot(sx,sy)
        a=math.atan2(sy,sx)
        coverage=1/(1+math.exp(clip(-(sr-340)/2,-60,60)))-1/(1+math.exp(clip(-(sr-360)/2,-60,60)))
        reflect=80-60*coverage
        # Unique 18 mm broad transverse finish marker, same one color sensor.
        marker=abs(wrap(a))<.025 and 320<sr<395
        if marker:reflect=20.
        reflect=clip(reflect+float(rng.normal(0,1.2))+1.2*math.sin(rb.t*.25),0,100)
        e=(reflect-50)/30.;raw_der=(e-last)/dt
        deriv=.80*deriv+.20*raw_der;last=e
        proposed=clip(integ+e*dt,-2.,2.)
        u=kp*e+ki*proposed+kd*deriv;maxomega=(180-v0)/(B/2)
        saturated=abs(u)>maxomega
        # Conditional anti-windup: integrate only if saturation is not worsened.
        if not marker and (not saturated or e*u<0):integ=proposed
        u=clip(kp*e+ki*integ+kd*deriv,-maxomega,maxomega)
        # Suppress the marker's steering transient using the last valid command.
        if marker:u=rows[-1]['command_omega_rad_s'] if rows else .31
        cl,cr=clip(v0-B*u/2,-50,180),clip(v0+B*u/2,-50,180)
        vl+=(cl-vl)*dt/tau;vr+=(cr*.97-vr)*dt/tau
        # A repeatable external heading disturbance is injected at t = 8 s.
        if k==800:rb.th+=math.radians(8)
        rb.step((vl+vr)/2,(vr-vl)/B,'FOLLOW',extra=dict(reflectance=reflect,error=e,integral_s=integ,command_omega_rad_s=u,
                   sensor_edge_error_mm=sr-edge,saturated=int(saturated),marker=int(marker),left_speed_mm_s=vl,right_speed_mm_s=vr))
        ang=math.atan2(rb.y,rb.x);unwrapped+=wrap(ang-previous);previous=ang
        row=rb.trace[-1];row['lap_angle_rad']=unwrapped;rows.append(row)
        # Controller uses reflectance + odometry distance, not ground-truth angle.
        if rb.distance>1500 and reflect<25:black_hold+=dt
        else:black_hold=0.
        if black_hold>=.10:
            done=True;break
        if abs(sr-edge)>70 and rb.t>2:break
    normal=[r for r in rows if r['t_s']>1 and not r['marker']]
    errors=np.array([r['sensor_edge_error_mm'] for r in normal])
    result=dict(mode=mode,kp=kp,ki=ki,kd=kd,completed=done,time_s=rb.t,path_mm=rb.distance,
                rms_error_mm=float(np.sqrt(np.mean(errors**2))),max_error_mm=float(np.max(np.abs(errors))),
                mean_error_mm=float(np.mean(errors)),saturated_samples=sum(r['saturated'] for r in rows),
                lap_angle_rad=unwrapped,trace=rows,endpoint_x_mm=rb.x,endpoint_y_mm=rb.y)
    save_csv(OUT/f'p4_{tag or mode.lower()}_trace.csv',rows)
    return result

def section(heading,paragraphs,headers=None,rows=None,calculations=None,figure=None,caption=None):
    o=dict(heading=heading,paragraphs=paragraphs)
    if headers:o['table']=dict(headers=headers,rows=rows)
    if calculations:o['calculations']=calculations
    if figure:o['figure']=str(figure);o['caption']=caption
    return o

def compact_trace(rows,stride):
    selected=rows[::stride]
    if selected[-1] is not rows[-1]:selected.append(rows[-1])
    return selected

def main():
    OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    ring_layout=[(195,105),(-210,112),(260,-40),(-270,-160),(35,320),(350,190),(-340,240),(150,-330),(-70,-220)]
    ring=[ring_sim(ring_layout,'nominal'),ring_sim([(320*math.cos(k*.51),320*math.sin(k*.51)) for k in range(12)],'dense'),ring_sim([],'empty')]
    scanner=scanner_suite()
    avoids=[avoid_sim(160,[(420,-100,650,100),(1050,-180,1250,80)],'two_obstacles'),
            avoid_sim(120,[(400,-240,710,120)],'wide_tall',2),avoid_sim(80,[],'clear')]
    lines=[line_sim(m) for m in ['P','PI','PID']]
    print(json.dumps({'ring':[{k:v for k,v in r.items() if k not in ['trace','initial','ejections']} for r in ring],
                      'scanner':scanner['trials'],'avoid':[{k:v for k,v in r.items() if k not in ['trace','obstacles']} for r in avoids],
                      'line':[{k:v for k,v in r.items() if k!='trace'} for r in lines]},indent=2))
    assert all(r['completed'] and r['lap_angle_rad']>=2*math.pi for r in lines), 'Line lap failed'
    assert all(s['correct']==s['runs'] for s in scanner['trials'][:2]),'Scanner recommended speed failed'
    assert scanner['trials'][-1]['correct']<scanner['trials'][-1]['runs'],'Expected speed-limit failure absent'
    plot(OUT/'p1_ring.png','Clean the ring: center trace and ejection coordinates',
         [('Robot center',[(r['x_mm'],r['y_mm']) for r in ring[0]['trace']],'#2b67b1')],bounds=(-700,700,-700,700),
         circles=[(0,0,600,'#29313a')]+[(x,y,20,'#bd5a35') for x,y in ring_layout]+[(e['x_mm'],e['y_mm'],20,'#39825b') for e in ring[0]['ejections']])
    plot(OUT/'p3_route.png','Obstacle avoidance: actual trajectory around unknown rectangles',
         [('Robot center',[(r['x_mm'],r['y_mm']) for r in avoids[0]['trace']],'#2b67b1'),('Original line',[(0,0),(1600,0)],'#64748b')],
         bounds=(-100,1700,-400,250),rects=avoids[0]['obstacles'])
    plot(OUT/'p4_error.png','Single-sensor line following: P, PI and PID comparison',
         [(r['mode'],[(q['t_s'],q['sensor_edge_error_mm']) for q in r['trace'] if not q['marker']],c) for r,c in zip(lines,['#b56b35','#7963ba','#246cac'])],
         xlabel='time (s)',ylabel='Sensor edge error (mm)')
    plot(OUT/'p4_lap.png','PID one-lap trajectory: one sensed outer edge',
         [('PID robot center',[(r['x_mm'],r['y_mm']) for r in lines[2]['trace']],'#246cac')],bounds=(-420,420,-420,420),
         circles=[(0,0,340,'#8f959c'),(0,0,360,'#303a44')])
    reports=make_reports(ring,scanner,avoids,lines)
    results=dict(ring=[{k:v for k,v in r.items() if k not in ['trace']} for r in ring],
                 scanner={k:v for k,v in scanner.items() if k not in ['nominal','offset']}|{'nominal':{k:v for k,v in scanner['nominal'].items() if k!='trace'},'offset':{k:v for k,v in scanner['offset'].items() if k!='trace'}},
                 obstacle=[{k:v for k,v in r.items() if k!='trace'} for r in avoids],line=[{k:v for k,v in r.items() if k!='trace'} for r in lines])
    payload=dict(reports=reports,results=results)
    (WORK/'project_content.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    (OUT/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    # Compact real computed data for the offline browser replay.
    web=dict(ring=dict(radius=600,initial=ring_layout,ejections=ring[0]['ejections'],trace=compact_trace(ring[0]['trace'],25)),
             scanner=dict(bars=scanner['bars'],trace=compact_trace(scanner['nominal']['trace'],3)),
             obstacle=dict(obstacles=avoids[0]['obstacles'],trace=compact_trace(avoids[0]['trace'],25)),
             line=dict(radius=350,trace=compact_trace(lines[2]['trace'],5)),results=results)
    (OUT/'web-data.json').write_text(json.dumps(web,separators=(',',':')),encoding='utf-8')
    (OUT/'selftest.txt').write_text('PASS: wheel integration, ring empty verification, all objects expelled, complete robot contained, scanner 60 noisy runs at recommended speeds, expected high-speed failure, append log and emulated mailbox, rectangle chassis clearance >30 mm, configurable endpoint N, P/PI/PID one lap.\nAll evidence is simulated.\n',encoding='utf-8')

def make_reports(ring,scanner,avoids,lines):
    r=ring[0];a=avoids[0];p=lines[2];nom=scanner['nominal']
    common='All trials in this report are reproducible software simulations produced for Omar Zid. They are not physical measurements, proof of NXC compilation, or evidence of testing a LEGO robot. Motor B is the left wheel; motor C is the right wheel; the one color/light sensor is S1 and the fixed forward ultrasonic sensor is S4. Wheel diameter D = 56 mm and wheel-center track B = 120 mm are explicit assumed calibration values. Replace them with measured values before a physical demonstration.'
    references=['Assignment image: Screenshot_4.png — Project 1 Clean the Ring (4h).',
                'Assignment image: Screenshot_5.png — Project 2 SCANNER (4h).',
                'Assignment image: Screenshot_6.png — Project 3 Obstacle Avoidance (6h).',
                'Assignment image: Screenshot_7.png — Project 4 LineFollower (6h).',
                'Supplied NXC tutorial and NXC minimum reference, distributed with the source files.']
    report1=dict(id='project1',title='Project 1 — Clean the Ring',source='Screenshot_4.png',
      summary=f"Omar Zid | Simulated result: {r['expelled']}/{r['object_count']} objects expelled in {r['time_s']:.2f} s; robot stopped after a complete empty angular scan. The chassis stayed at least 75.00 mm inside the ring. The forward pusher reaches the boundary exactly, leaving zero extension tolerance in the ideal model.",sections=[
      section('Task, deliverables and declared model',[common,
       'The task is to push every object outside the ring quickly, keep the robot inside, stop when clean, and display a map of ejection locations on the robot screen. The model includes sensing, wheel movement, contact pushing, reverse movement, verification and a small LCD-style map. Objects have radius 20 mm. Ring outer radius is 600 mm, with a black boundary band from radius 580 to 600 mm. The robot is represented by a circular 75 mm chassis and a narrow 150 mm forward pusher. The color sensor is aligned with the pusher tip; S4 is 70 mm forward of the axle center. Initial object centers must be outside a 180 mm staging radius, leaving room for the 150 mm pusher, its 40 mm half-width, and the 20 mm object radius while turning.',
       'The start is the center with heading 0 rad. Nine separate rigid circular objects form the nominal scene. No object count or object positions are supplied to the controller: it receives ultrasonic distances while turning. Object IDs in the trace label the independent simulated scene for checking and plotting.'],
       ['Quantity','Value','Unit / meaning'],[['Outer ring radius',600,'mm'],['Black boundary width',20,'mm'],['Chassis radius',75,'mm'],['Pusher / color offset',150,'mm forward'],['Object radius',20,'mm'],['Ultrasonic offset',70,'mm forward']]),
      section('Search, push, boundary response and clean-stop logic',[
       'SEARCH turns the robot through headings 0°–359° in 1° increments and reads one forward range ray at each heading. SELECT chooses the smallest measured surface range, giving a bearing close to the center of the nearest visible object. ALIGN turns to that bearing. PUSH advances at 110 mm/s. A 40 mm half-width pusher captures the selected object when the front makes contact; the object then moves with the front face. The simulation integrates each wheel movement rather than jumping between waypoints.',
       'The color sensor reaches the inner black edge when the axle is 430 mm from the center. BOUNDARY_FINISH then travels the calibrated 20 mm band width at 40 mm/s, stopping at axle radius 450 mm. The pusher tip is at 600 mm and the object center at 620 mm, so the entire radius-20 mm object is outside or tangent to the ring. RETREAT reverses 450 mm on the same heading to the center. It then searches again. A successful clean stop requires a new complete scan with no object ranges inside the 900 mm search limit; absence of a detection while merely driving is insufficient.',
       'At the farthest ring radius, adjacent 1° rays are approximately 10.47 mm apart. This is narrower than the 40 mm object diameter. Under the ideal ray, clear staging and minimum object-size assumptions, an unoccluded object cannot hide between samples. Occlusion is handled by repeatedly clearing the nearest visible object and rescanning. An independent test checks the true remaining objects when the controller declares completion. The 32-scan safety cap is a failure budget; it does not use the true initial object count.']),
      section('Calculations with dimensions and units',[
       'The calculations distinguish chassis safety from the complete forward extension. A positive chassis margin does not imply a positive pusher margin. In this ideal model the pusher touches the outer border but does not cross it. Encoder distances are calculated from wheel circumference, not from motor percentages.'],calculations=[
       'Wheel circumference C = πD = π × 56 mm = 175.929 mm/revolution. Straight wheel travel s = C × encoder_degrees / 360°.',
       'Travel to first black reading = 580 mm − 150 mm = 430 mm. Finish travel = 600 − 580 = 20 mm. Maximum axle radius = 430 + 20 = 450 mm.',
       'Chassis margin = 600 − (450 + 75) = 75 mm. Complete forward-extension margin = 600 − (450 + 150) = 0 mm.',
       'Ejected object center radius = 450 + 150 + 20 = 620 mm; its nearest point is 620 − 20 = 600 mm.',
       f"A 450 mm forward run requires 450 / (π × 56) × 360 = {450/(math.pi*56)*360:.3f}° per wheel. Nine forward-and-reverse runs cover 9 × 2 × 450 = 8100 mm, matching the exported path {r['path_mm']:.3f} mm.",
       'An in-place 360° turn moves each wheel πB = π × 120 = 376.991 mm in opposite directions: 771.429° per wheel. Angular rate 0.9 rad/s corresponds to wheel speeds ±54 mm/s.',
       'Angular sampling chord = 2 × 600 mm × sin(0.5°) = 10.472 mm < 40 mm object diameter.']),
      section('Executed validation trials and exported map',[
       'The table contains executed trials; the alternate layout and initially empty ring exercise completion logic, not only the nominal arrangement. Time includes actual in-place scan/align rotations, push travel and reverse travel. The empty case stops only after taking all 360 range readings. An empty ring permits stopping even without pushing an object.',
       'The ejection CSV records object ID, coordinates in mm and simulated time in s. The LCD image represents a 100 × 64 pixel display enlarged five times. Coordinates use u = 50 + 25x/600 and v = 35 − 25y/600. Rounding produces pixel locations; the marker numbers are display labels. Ejection coordinates are derived from encoder pose and assumed contact geometry, so they are estimates of where the push finished rather than an external camera survey.'],
       ['Scene','Objects out','Search scans','Time (s)','Path (mm)','Chassis margin (mm)'],
       [[q['tag'],f"{q['expelled']}/{q['object_count']}",q['scans'],f"{q['time_s']:.3f}",f"{q['path_mm']:.1f}",f"{q['min_chassis_margin_mm']:.1f}"] for q in ring],
       figure=OUT/'p1_ring.png',caption='Computed robot-center trajectory. Brown circles show initial objects, green circles show the ejection coordinates, and the outer circle is the ring boundary.'),
      section('Ejection coordinate evidence',[
       'All nine nominal objects reached center radius 620 mm in this geometric contact model. The object is marked ejected only after that condition is met. The robot subsequently retreats and verifies the remaining ring; it does not stop immediately after the ninth recorded ejection.'],
       ['Object','x (mm)','y (mm)','Radius (mm)','Ejection time (s)'],
       [[q['id'],f"{q['x_mm']:.2f}",f"{q['y_mm']:.2f}",f"{math.hypot(q['x_mm'],q['y_mm']):.2f}",f"{q['time_s']:.2f}"] for q in r['ejections']],
       figure=OUT/'p1_nominal_lcd.png',caption='Enlarged LCD-style map generated from the ejection coordinates. Every plotted point lies outside the drawn ring.'),
      section('Limits and physical demonstration procedure',[
       'This is a planar kinematic/contact model. It omits motor acceleration, braking travel, pusher flex, object rolling resistance, wheel slip, object-to-object collisions and the real sonar cone. Full expulsion while every part of the robot remains inside is achieved with zero pusher margin. It therefore has no tolerance for a smaller ring, larger forward extension or excess stopping distance. The simulated result must not be presented as physical boundary certification.',
       'Before use, measure the ring radius, boundary-band width, chassis footprint, pusher offset, object dimensions and sensor position. Calibrate black/white readings at the actual floor height. Verify that the color sensor and pusher can reach the border together, and test braking at the 40 mm/s finish speed. If the teacher defines any contact with the border as leaving, this push geometry needs revision; the current model assumes touching the boundary is allowed. Add a guard timeout, clean-scan repetition and an obstacle-free center requirement for physical tests. Objects smaller than 40 mm, transparent or poorly reflecting objects, sonar blind zones and a center object violate the coverage assumptions.',
       'Acceptance evidence is p1_nominal_trace.csv, p1_nominal_ejections.csv, p1_dense_trace.csv and p1_empty_trace.csv. The source simulation can be rerun; the assertions detect falsely declaring the ring clean. NXC programs are provided separately and require hardware calibration and a real toolchain check.'])],references=[references[0],references[4]])

    report2=dict(id='project2',title='Project 2 — SCANNER',source='Screenshot_5.png',
      summary=f"Omar Zid | Simulated scanner counted {nom['total']} bars in groups {nom['groups']} over {nom['time_s']:.3f} s at 60 mm/s. All 30 noisy phase-varied runs at that speed were correct. Scanner.txt contains appended results; send and receive were verified through an explicitly emulated mailbox.",sections=[
      section('Task, card fixture and sensor model',[common,
       'The supplied task asks for the number of vertical bars with maximum accuracy and minimum working time, for the count/time to appear on screen and be appended to Scanner.txt, and for the sum to be sent to another robot. Each group contains bars with common width, spacing and height; dimensions differ between groups. The simulated card therefore uses three deliberately different groups, with a known 300 mm horizontal fixture travel. The sensor scans at y = 0 mm, through all bars. A single horizontal pass can only count bars intersecting that scan line; different heights do not reveal themselves as extra events.',
       'Black reflectance is 20 and white reflectance is 80 on a normalized 0–100 scale. A 4 mm rectangular sensing footprint averages covered black and white area along the travel direction. Gaussian sample noise has standard deviation 2 reflectance units. Different random seeds and initial sample phases test repeatability. No bar dimensions or group count enter the count state machine; the known 300 mm fixture length only defines where to stop.'],
       ['Group','Bars','Width (mm)','Gap (mm)','Height (mm)','x span (mm)'],
       [[1,4,8,7,35,'20–73'],[2,7,5,6,55,'108–179'],[3,3,12,10,25,'214–270']]),
      section('Time-sampled counting and grouping algorithm',[
       'The scanner samples every 0.010 s. WHITE transitions to BLACK only after three consecutive readings below 35. That stable transition increments the total exactly once. BLACK transitions back to WHITE after three consecutive readings above 65. Readings between 35 and 65 keep the current state and reset the pending confirmation. This hysteresis rejects small fluctuations, and three-sample confirmation rejects a single noisy sample. A wide black bar cannot be counted repeatedly while the sensor remains over it.',
       'The optional group display starts a new group when the white distance between confirmed transitions exceeds 22 mm. The card has 35 mm between groups and 6–10 mm within groups; hence the threshold separates these cases. Total bar counting does not rely on grouping. All 14 bars pass through the same scan line even though their heights differ. A separate y = 18 mm test intentionally misses the 35 mm-high and 25 mm-high groups because their half-heights are 17.5 and 12.5 mm; this is a geometric failure, not a counter defect.',
       'Elapsed time is sampled work time from the first acquisition to the stopping sample; it excludes setup and calibration. The nominal result is formatted as a screen/count-time record and appended using file append mode. A second run appends another record, preserving the first. The message COUNT=14;TIME_MS=... is placed in an in-process mailbox and read by a second receiver function. This demonstrates payload formatting and matching send/receive values. It does not demonstrate a Bluetooth radio, pairing, packet reliability or a second physical brick.']),
      section('Sampling calculations and speed selection',[
       'Counting accuracy depends on usable dark and white duration, not only on a threshold. A coarse speed can skip a narrow bar entirely or provide fewer than three confirmed samples. The 90 mm/s tests show that a theoretical no-noise bound does not guarantee a robust noisy run. The selected 60 mm/s speed retains additional sampling margin and takes less time than 40 mm/s.'],calculations=[
       'Sample displacement = v × Δt. At 60 mm/s × 0.010 s = 0.600 mm/sample. A 5 mm bar spans approximately 8.33 samples before footprint/threshold effects.',
       'With black = 20, white = 80 and entry threshold 35, the required black coverage fraction is (80 − 35)/(80 − 20) = 0.75. For a 4 mm footprint, 3 mm must be black.',
       'For the 5 mm narrowest bar, the ideal below-threshold x interval is 5 − 4/2 = 3 mm. Its duration at 60 mm/s is 3/60 = 0.050 s, giving about five samples for a three-sample debounce.',
       'A conservative noiseless phase-independent entry bound is v ≤ usable_width/(3Δt) = 3 mm/(3 × 0.010 s) = 100 mm/s. Noise and threshold uncertainty justify choosing 60 mm/s; the experiment independently tests that decision.',
       'At 300 mm/s, displacement is 3 mm/sample. A 3 mm usable dark interval yields about one sample, below the required three. Missed bars are therefore expected.',
       f"Nominal travel time = 300 mm / 60 mm/s = 5.000 s. The executed sampled acquisition is {nom['time_s']:.3f} s because it includes the final 10 ms stopping sample.",
       'At 60 mm/s, each wheel turns at 60/(π × 56) × 360 = 122.777°/s. The full 300 mm span requires 613.883° per wheel.']),
      section('Repeated noisy trials and deliberate failure test',[
       'Thirty runs at each speed use seeds 0–29 and phase offsets spanning one sample period. Every result below is generated from the state machine and noise model. Accuracy is the fraction of runs whose total equals 14, not an assertion that physical hardware has the same reliability. The high-speed trials are retained as failure evidence.'],
       ['Speed (mm/s)','Correct / runs','Min count','Max count','Work time (s)','Accuracy (%)'],
       [[q['speed_mm_s'],f"{q['correct']}/{q['runs']}",q['min_count'],q['max_count'],f"{q['time_s']:.3f}",f"{100*q['correct']/q['runs']:.1f}"] for q in scanner['trials']],
       figure=OUT/'p2_reflectance.png',caption='Actual nominal sampled reflectance and accumulated count. The count is multiplied by 5 only to make both traces visible on one scale.'),
      section('Files, receiver evidence and mounting sensitivity',[
       'Scanner.txt is regenerated as a deterministic demonstration file at the beginning of the simulation, then the two trial records are appended with append mode. Re-running the entire simulation rebuilds the demonstrator; this is separate from continuously preserving a physical brick file across power cycles. The full p2_trials.csv contains all 150 counts, speeds, sample phases and seeds, and p2_nominal_trace.csv contains every sensor reading and state transition.',
       f"At y = 18 mm, the executed mounting-offset test counted {scanner['offset']['total']} bars rather than 14. That value is expected because only the 55 mm-high middle group intersects the scan line. A teacher demonstration should first show the centered successful pass, then show the speed and mounting failures to explain the measurement limits."],
       ['Sender payload','Receiver payload','Match','Transport'],
       [[q['sent'],q['received'],'Yes' if q['matched'] else 'No','Emulated mailbox'] for q in scanner['bluetooth']]),
      section('Physical checks and conclusions',[
       'The recommended simulated configuration gives 14 bars in three groups, 4 + 7 + 3 = 14, while preserving count/time records and transmitting a matching payload in software. The elapsed work time does not include Bluetooth connection setup or receiver latency. No real radio latency or loss is claimed.',
       'For physical commissioning, measure the narrowest bar and gap with a ruler, check the sensor footprint at its mounting height, calibrate thresholds over actual black and white card, and ensure the scan line intersects the shortest bar. Check straightness with both wheel encoders and reduce speed until three stable samples are available under real noise. Confirm scanner file open/append/close behavior and a real receiver acknowledgment after pairing. The finite ray/footprint model omits uneven illumination, glossy print, motor drift, vibration, torn bars and communication failures. A white end region is not itself proof that every bar has been scanned; the known fixture travel provides that condition here.'])],references=[references[1],references[4]])

    report3=dict(id='project3',title='Project 3 — Obstacle Avoidance',source='Screenshot_6.png',
      summary=f"Omar Zid | Configurable N = 160 cm trial reached x = {a['endpoint_x_mm']:.2f} mm, y ≈ 0 mm after avoiding two unknown rectangles. Route length was {a['path_mm']:.2f} mm. Minimum clearance of the complete circular chassis was {a['min_clearance_mm']:.2f} mm, and simulated time including physical probing turns was {a['time_s']:.2f} s.",sections=[
      section('Task and endpoint definition',[common,
       'The assignment requests forward progress of configurable N cm while avoiding one or more parallelepiped obstacles of unknown size and keeping close to the original straight line. This report defines the requested endpoint as x = 10N mm on the original y = 0 mm line. The total curved/detour route is a separate measurement. Stopping after only N cm of wheel travel would end short of the requested forward endpoint when obstacles require detours.',
       'The environment is a planar top view of rigid rectangles. The controller is given N, its start pose and encoder calibration. Rectangle coordinates are known only to the simulated sensor and collision checker; the controller does not read their widths, heights, near edges or far edges. The robot has a circular collision footprint of radius 75 mm. The ultrasonic sensor lies 70 mm forward of the axle and is fixed to the chassis. To probe a side wall, the whole robot stops and rotates, takes a forward measurement, and rotates back. Those turns consume time and appear in the wheel trace.']),
      section('Measured-corner avoidance state machine',[
       'FORWARD advances in 10 mm steps with encoder heading feedback while the forward range exceeds 200 mm. If range is at most 200 mm, TURN_RIGHT rotates to −90°. FIND_NEAR_CORNER moves south in 25 mm increments. Between steps, a real simulated chassis rotation faces east and probes the obstacle; it then restores the south heading. Once the east ray becomes clear, the robot travels a further 110 mm south before turning east. This margin consists of the 75 mm chassis radius plus 35 mm clearance.',
       'FOLLOW_SIDE progresses east in 25 mm steps, with chassis rotations to probe north. It must first observe a wall and later observe that wall has ended; an initially clear north reading is insufficient to declare the far corner. After the far-corner observation, it travels another 110 mm east, turns north, and uses encoder y to return to y = 0. It turns east and resumes forward progress. Heading feedback applies ω = clamp[4(θtarget − θodo), −0.7, +0.7] rad/s; straight speed is 120 mm/s and detour speed is 100 mm/s.',
       'Search budgets prevent endless movement when the assumed geometry fails: at most 80 near-corner increments and 100 side increments. Such a timeout is reported as failure, not a successful avoidance. The modeled scenes have isolated convex rectangles and enough clear ground below them. Turning is safe here because the collision footprint is circular; a long real chassis needs a swept-footprint check.']),
      section('Odometry, unit conversions and safety calculations',[
       'Wheel increments produce both the true kinematic pose and independent encoder odometry. With no slip or encoder quantization in these baseline trials, they coincide. Each interval uses the exact constant-wheel-speed differential-drive arc; small-angle straight movement is handled separately. Heading is in radians internally and encoder rotation is in degrees.'],calculations=[
       'N_mm = 10 × N_cm. For N = 160 cm, endpoint x = 1600 mm. This does not constrain total route length to 1600 mm.',
       'ΔsL = πD × ΔencoderL/360; ΔsR = πD × ΔencoderR/360. Δs = (ΔsR + ΔsL)/2; Δθ = (ΔsR − ΔsL)/B.',
       'For Δθ ≠ 0: xnew = x + (Δs/Δθ)[sin(θ+Δθ) − sin θ]; ynew = y − (Δs/Δθ)[cos(θ+Δθ) − cos θ].',
       'The first nominal front face is x = 420 mm. A 200 mm range from a sensor 70 mm forward corresponds to center x ≈ 420 − 200 − 70 = 150 mm. Chassis-front clearance before turning is 420 − 150 − 75 = 195 mm.',
       'Required side center spacing is 75 + 35 = 110 mm. The chassis clearance is distance(center, rectangle) − 75 mm; center distance by itself would overstate safety by 75 mm.',
       f"Nominal path excess = {a['path_mm']:.0f} − 1600 = {a['path_mm']-1600:.0f} mm; route/forward-progress ratio = {a['path_mm']/1600:.3f}.",
       'One wheel encoder degree corresponds to π × 56/360 = 0.4887 mm. A 1° differential error between wheels changes estimated heading by 0.4887/120 = 0.004072 rad = 0.2333°. Over 1.6 m, an uncompensated constant 0.2333° heading error gives about 6.51 mm lateral drift.']),
      section('Executed scenarios and complete-chassis clearance',[
       'The nominal two-obstacle scene has rectangles x = 420–650 mm, y = −100–100 mm and x = 1050–1250 mm, y = −180–80 mm. The alternate wide/tall scene has x = 400–710 mm, y = −240–120 mm and adds uniform ultrasonic noise within ±2 mm. These dimensions are disclosed for validation and reproduction; the controller discovers the corners from range transitions. The clear-path case confirms N can change without changing the control algorithm.',
       'Clearance is evaluated over every simulated trace sample, including physical probing rotations. All recorded chassis clearances exceed 30 mm. The simulator uses exact local arcs with a maximum moving step of 2.4 mm. The nominal minimum 35 mm occurs in a straight segment parallel to the obstacle, so the reported minimum is not merely a distance from a few waypoint vertices. The circular body can rotate in place without increasing its footprint.'],
       ['Trial','N (cm)','Endpoint (mm)','Path (mm)','Min clearance (mm)','Time (s)'],
       [[q['tag'],q['N_cm'],f"({q['endpoint_x_mm']:.1f}, {q['endpoint_y_mm']:.1f})",f"{q['path_mm']:.1f}",f"{q['min_clearance_mm']:.1f}" if q['min_clearance_mm'] is not None else 'No obstacles',f"{q['time_s']:.2f}"] for q in avoids],
       figure=OUT/'p3_route.png',caption='Actual wheel-integrated trajectory. Shaded rectangles are the unknown-size objects in the sensor environment; the gray horizontal trace is the original y = 0 line.'),
      section('Performance tradeoffs and exported observations',[
       f"The nominal maximum lateral displacement was {a['max_line_deviation_mm']:.1f} mm. The robot returns to the original line after each obstacle rather than continuing a parallel offset to the end. This is a feasible conservative strategy; the report does not claim it is the global shortest route or the fastest possible avoidance. The {a['time_s']:.2f} s runtime is dominated by rotating a fixed sonar to take side measurements. A movable sensor or additional side sensor would reduce this overhead but would change the hardware assumption.",
       'The CSV trace includes time, true x/y, encoder x/y, heading, both wheel degrees, commanded speed/angular rate, state and chassis clearance. The separate sonar CSV contains every forward and side-probe reading with time and pose. The +∞ no-return condition is encoded as the modeled 2550 mm out-of-range reading. Because this is a ray sensor, a rectangle edge produces a sharp change from a finite range to no return; a real ultrasonic cone will produce a broader transition.',
       'The one-noisy-trial example is a deterministic sensitivity check, not a statistical physical reliability claim. Encoder calibration bias, wheel slip, an obstacle moving during a scan and nonrectangular or concave shapes require additional tests. An obstacle too near the final endpoint can force an overshooting detour; the simulation treats that as a failure of the configured route instead of claiming successful N progress.']),
      section('Physical readiness and acceptance criteria',[
       'Before a classroom hardware demonstration, measure the full footprint and sensor offset; calibrate encoder distance and turn direction; verify zero range versus out-of-range handling; and test braking before the 200 mm threshold. Use heading correction only after wheel directions are confirmed. Validate the detection threshold under the actual sonar beam cone and permit additional clearance for noise and braking.',
       'A physical run passes when the requested endpoint is reached near y = 0, no part of the chassis contacts any obstacle, the avoidance does not use manually entered obstacle dimensions, and a log shows both endpoint progress and total route length. The provided simulation passes those geometric checks under its stated assumptions. Its near-zero endpoint error is the expected consequence of ideal encoders and no slip, not an attainable measured accuracy claim for a real NXT. The separately provided NXC implementation follows the same sensing principle but has not been executed by this Python model.'])],references=[references[2],references[4]])

    report4=dict(id='project4',title='Project 4 — Single-Sensor PID Line Follower',source='Screenshot_7.png',
      summary=f"Omar Zid | Simulated PID completed one marker-to-marker lap in {p['time_s']:.3f} s. Sensor-edge RMS error was {p['rms_error_mm']:.3f} mm, compared with {lines[0]['rms_error_mm']:.3f} mm for P and {lines[1]['rms_error_mm']:.3f} mm for PI. Wheel dynamics, saturation, noise, bias and a repeatable heading disturbance are included.",sections=[
      section('Task, track geometry and one-sensor observation',[common,
       'The assignment requires a robot with only one color sensor to follow a line for one round using PID regulation. The software test uses a circular black line of centerline radius 350 mm and width 20 mm, so its inner and outer edges are radii 340 and 360 mm. The sensor is 35 mm ahead of the axle. The robot follows the outer edge at target reflectance 50, between calibrated black 20 and white 80. A smooth 2 mm edge transition models the sensor footprint. The reading has Gaussian noise σ = 1.2 reflectance units and a slow ±1.2-unit lighting drift.',
       'A broad 18 mm transverse black marker crosses the normal line once per circuit. The starting pose aligns the same forward sensor with this marker. Initial marker readings cannot end the run. Lap detection is armed only after encoder path exceeds 1500 mm; after arming, ten consecutive 10 ms readings below 25 trigger braking. The marker is wider than normal transient dark readings and its expected dwell is about 0.164 s at 110 mm/s. No second color sensor or hidden ground-truth track angle controls termination.',
       'The independent checker unwraps the true polar angle of the axle center and verifies that angular travel is at least 2π rad. That measurement validates the result after the controller stops; it is not supplied to PID or the stop condition. The start-marker alignment matters because a forward sensor crosses the finish before the axle center reaches the same position. Starting with the sensor on the marker makes the next encounter a full sensor-to-sensor circuit.']),
      section('Time-discrete PID, saturation and anti-windup',[
       'Error is e = (reading − 50)/30, a dimensionless normalized reflectance difference. Positive error means the outer-edge sensor is too far onto white; the command turns left to return toward black. Integral state I accumulates eΔt in seconds, and the derivative has units s⁻¹. A first-order filtered derivative is d[k] = 0.80d[k−1] + 0.20(e[k] − e[k−1])/Δt. This reduces differentiation of sample noise.',
       'The PID command is ω = Kp e + Ki I + Kd d, in rad/s. Integral state is clamped to ±2 s, and conditional integration rejects a proposed update if the command is saturated and the current error would drive it further into saturation. During the broad marker, the previous angular command is held and integration is frozen so the marker does not produce a steering kick. At startup the known entry command is 0.31 rad/s while the sensor leaves the marker.',
       'Base translational command is 110 mm/s. Wheel commands are vL = 110 − 60ω and vR = 110 + 60ω mm/s. Angular command is limited to ±1.1667 rad/s, and wheel commands to −50–180 mm/s. Each motor follows a first-order lag τ = 0.10 s. The right motor produces 97% of its command, introducing a repeatable speed bias. At t = 8.00 s an external 8° heading disturbance is injected into the true pose; encoder heading does not observe this bump. The color feedback must recover.'],
       ['Controller','Kp (s⁻¹)','Ki (s⁻²)','Kd','Sample period (s)','Filter'],
       [[q['mode'],q['kp'],q['ki'],q['kd'],.01,'0.80 / 0.20'] for q in lines]),
      section('Worked geometry and gain-unit calculations',[
       'Radians are treated as dimensionless in the unit table: Kp produces rad/s per normalized error, Ki rad/s² per normalized accumulated error, and Kd rad per normalized derivative. These numerical gains are valid for the defined normalization, 10 ms loop and wheel-speed mapping; copying them into a raw 0–100 reflectance or motor-percentage loop changes the controller.',
       'Tracking error is the actual sensor-point radius minus the outer edge radius, in mm. It is computed from the independent simulated pose for evaluation. PID itself receives only reflectance. Because the sensor lies ahead of the axle, axle radius 360 mm is not the zero sensor-error trajectory.'],calculations=[
       'Zero-error axle radius = √(360² − 35²) = 358.295 mm.',
       'Desired circular angular rate at nominal speed ≈ 110/358.295 = 0.3070 rad/s. Corresponding wheel speeds are 110 ± 60 × 0.3070 = 91.58 and 128.42 mm/s.',
       'For reading 56: e = (56 − 50)/30 = 0.20. If I = 0.40 s and filtered derivative d = 0.50 s⁻¹, PID command = 0.80 × 0.20 + 0.25 × 0.40 + 0.035 × 0.50 = 0.2775 rad/s.',
       'For that worked command, vL = 110 − 60 × 0.2775 = 93.35 mm/s and vR = 126.65 mm/s. Encoder speeds are 191.02 and 259.16 degrees/s respectively for 56 mm wheels.',
       'Angular saturation = (180 − 110)/(120/2) = 1.1667 rad/s. Integral clamp |I| ≤ 2 s prevents an integral term larger than 0.25 × 2 = 0.50 rad/s in PID.',
       'Expected marker dwell = 18 mm/110 mm/s ≈ 0.164 s. Required dark confirmation = 10 × 0.010 = 0.100 s, leaving about 64 ms nominal margin.',
       'Reference axle-circle circumference = 2π × 358.295 = 2251.23 mm; actual route is measured from wheel increments and varies with tracking error, startup and stop location.']),
      section('P, PI and PID executed comparison',[
       'Each comparison uses the same starting geometry, random seed, wheel lag, 3% right-motor command bias, lighting drift and 8° heading disturbance. Only controller gains change. Error statistics include samples after the first second and exclude the broad marker, where the sensor reading intentionally represents the finish stripe instead of the normal edge. Maximum error is the largest absolute sensor-edge error in that evaluation interval.',
       'P requires a steady reflectance error to create the sustained turn and counter the motor bias. PI reduces that steady error but its integral responds more slowly to a sudden heading disturbance. PID adds a filtered derivative and achieved the smallest RMS error in this selected scene. Its maximum transient error can still exceed P even when its overall RMS is lower; a low RMS is not a guarantee of minimum peak error. These gains are compared within one specified track, not claimed optimal for every path.'],
       ['Mode','Lap time (s)','RMS (mm)','Peak (mm)','Mean (mm)','Saturated samples'],
       [[q['mode'],f"{q['time_s']:.3f}",f"{q['rms_error_mm']:.3f}",f"{q['max_error_mm']:.3f}",f"{q['mean_error_mm']:.3f}",q['saturated_samples']] for q in lines],
       figure=OUT/'p4_error.png',caption='Computed sensor-edge error over time. The external heading disturbance occurs at 8.00 s. Marker samples are omitted from these error curves.'),
      section('One-lap evidence, trajectory and trace',[
       f"PID stopped after {p['time_s']:.3f} s and {p['path_mm']:.2f} mm of integrated wheel travel. Independent axle angular travel was {p['lap_angle_rad']:.5f} rad, at least 2π = 6.28319 rad. The controller used its armed single-sensor marker detector for this stop. It did not stop after a fixed guessed lap time or when a precomputed angle became 360°.",
       'The full p4_pid_trace.csv contains time, robot and encoder pose, wheel degrees, reflectance, normalized error, integral, angular command, both actual wheel speeds, saturation flags, marker flags, sensor-edge error and independent lap angle. The P and PI traces have the same schema for checking the comparison. Ground-truth error and lap angle are evaluation columns; they are not feedback inputs.',
       'A unique finish marker and a simple track without branches or shortcuts are assumptions of this one-sensor method. Encoder arming rejects the initial marker but cannot mathematically prove a full lap on any unknown track. For a course with repeated black patches, intersections or a shorter loop, the arming distance and marker design must be changed and independently checked.'],figure=OUT/'p4_lap.png',caption='Actual PID axle-center trajectory, with the inner and outer black-stripe edges drawn at 340 and 360 mm radius.'),
      section('Hardware tuning and model limits',[
       'For physical use, mount the one sensor 35 mm ahead at consistent height, measure black/white calibration, set the sensor on the intended edge, and confirm that positive correction turns toward black. Start with low forward power and Ki = Kd = 0; increase Kp until tracking is responsive, then add a small derivative to reduce overshoot and a small integral only if sustained bias remains. Keep the loop period fixed and include the real Δt in integral and derivative calculations. Motor percentages require measured speed conversion before these mm/s gains can be reused.',
       'The simulation includes realistic control complications but remains a planar model: it omits stiction, battery changes, cable drag, uneven floors, sensor spectral behavior, wheel slip and noncircular sharp track corners. Braking at the finish is idealized. The intentional heading bump demonstrates recovery in this model and is not a measured bump test on hardware. A real lap should be timed separately, its sensor log saved, and its completion observed by the teacher. The computed gains and traces supply a reproducible starting point rather than physical performance certification.'])],references=[references[3],references[4],'Assignment-supplied PID help link: http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html (reference link reproduced from the brief; not a measured hardware source).'])
    return [report1,report2,report3,report4]

if __name__=='__main__':main()
