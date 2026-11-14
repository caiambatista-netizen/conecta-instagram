import numpy as np, wave
SR=48000; BPM=84; beat=60/BPM; DUR=30.5
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N)
def note(f): return 440*2**((f-69)/12)
def add(sig, start, ch=(1,1)):
    i=int(start*SR); n=min(len(sig), N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*ch[0]; R[i:i+n]+=sig[:n]*ch[1]
def env(n, a, d, s, r_len):
    e=np.ones(n); A=int(a*SR); D=int(d*SR); Rl=int(r_len*SR)
    e[:A]=np.linspace(0,1,A); e[A:A+D]=np.linspace(1,s,D); e[A+D:]=s
    e[-Rl:]*=np.linspace(1,0,Rl); return e
def piano(m, dur, vel=0.25):
    n=int(dur*SR); t=np.arange(n)/SR; f=note(m)
    sig=sum(np.sin(2*np.pi*f*k*t)*(0.6**(k-1))*np.exp(-t*(1.6+0.9*k)) for k in range(1,6))
    sig*=np.minimum(1,t/0.004)
    return sig*vel
def pad(ms, dur, vel=0.06):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        for det in (-0.08,0,0.08):
            f=note(m)*2**(det/12)
            s+=np.sin(2*np.pi*f*t+np.sin(2*np.pi*0.2*t)*0.6)
    return s*env(n,1.2,0.5,0.85,1.2)*vel/len(ms)
# Progressão: Cmaj7 - Am7 - Fmaj7 - G(sus) (2 compassos cada? 1 compasso = 4 tempos)
prog=[([48,55,64,67,71],[60,64,67,71]),([45,52,60,64,67],[57,60,64,67]),([41,48,57,60,64],[53,57,60,64]),([43,50,59,62,67],[55,59,62,67])]
bar=4*beat; t=0; i=0
rng=np.random.default_rng(7)
while t<DUR:
    bass,ch=prog[i%4]
    add(pad(ch, bar+1.2), t)
    add(piano(bass[0]-12+12, bar*0.95, 0.18), t)
    arp=[ch[0]+12,ch[1]+12,ch[2]+12,ch[3]+12,ch[2]+12,ch[1]+12,ch[2]+12,ch[3]+12]
    for k,m in enumerate(arp):
        pan=0.5+0.35*np.sin(k)
        add(piano(m, beat*1.6, 0.10+0.03*rng.random()), t+k*beat/2, (1-pan+0.5,pan+0.5))
    # batida leve: kick no 1 e 3, shaker
    for b in (0,2):
        n=int(0.25*SR); tt=np.arange(n)/SR
        kick=np.sin(2*np.pi*(55+70*np.exp(-tt*30))*tt)*np.exp(-tt*14)*0.22
        if t>=bar*2: add(kick, t+b*beat)
    for k in range(8):
        n=int(0.06*SR); nz=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*60)
        nz=np.diff(np.concatenate([[0],nz]))*0.035*(0.6 if k%2==0 else 1)
        if t>=bar*2: add(nz, t+k*beat/2+0.01)
    t+=bar; i+=1
# reverb simples (eco difuso)
def verb(x):
    y=x.copy()
    for d,g in ((0.031,0.35),(0.047,0.3),(0.071,0.25),(0.113,0.2),(0.173,0.15)):
        k=int(d*SR); y[k:]+=x[:-k]*g
    return y
L=verb(L); R=verb(R)
fade=int(2.5*SR); L[-fade:]*=np.linspace(1,0,fade); R[-fade:]*=np.linspace(1,0,fade)
fi=int(0.8*SR); L[:fi]*=np.linspace(0,1,fi); R[:fi]*=np.linspace(0,1,fi)
m=max(abs(L).max(),abs(R).max()); L/=m*1.12; R/=m*1.12
st=np.stack([L,R],1); data=(st*32767).astype(np.int16)
w=wave.open("trilha.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes()); w.close()
print("ok")
