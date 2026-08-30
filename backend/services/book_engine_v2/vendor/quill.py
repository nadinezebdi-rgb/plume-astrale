# -*- coding: utf-8 -*-
import math, os
GOLD="#A8823F"; PAPER="#FBF7F0"

def shaft(t, curve, sway):
    """t=0 pointe (haut) -> t=1 base. Rachis legerement en S."""
    x = curve*math.sin(math.pi*t)*(1-0.25*t) + sway*t*t
    return x, 100.0*t

def tangent(t, curve, sway, d=1e-4):
    x1,y1=shaft(max(0.0,t-d),curve,sway); x2,y2=shaft(min(1.0,t+d),curve,sway)
    dx,dy=x2-x1,y2-y1; n=math.hypot(dx,dy) or 1.0
    return dx/n, dy/n

def env(t, peak, wmax, head, tailend):
    """largeur de la palme"""
    if t<=0.0 or t>=tailend: return 0.0
    if t<peak: return wmax*math.sin(math.pi/2*(t/peak))**head
    u=(t-peak)/(tailend-peak)
    return wmax*(math.cos(math.pi/2*u)**1.15)

def notch_factor(t, notches):
    f=1.0
    for tc,drop,rise,nd in notches:
        if tc <= t <= tc+drop:                 # chute franche apres la pointe de barbe
            u=(t-tc)/drop
            f=min(f, 1.0-(1.0-nd)*(u**0.72))
        elif tc+drop < t <= tc+drop+rise:      # remontee convexe vers la barbe suivante
            u=(t-tc-drop)/rise
            f=min(f, nd+(1.0-nd)*(u**0.95))
    return f

def side(sgn, curve, sway, peak, wmax, head, tailend, notches, steps=560):
    pts=[]
    for i in range(steps+1):
        t=tailend*i/steps
        w=env(t,peak,wmax,head,tailend)*notch_factor(t,notches)
        bx,by=shaft(t,curve,sway); tx,ty=tangent(t,curve,sway)
        nx,ny=-ty*sgn, tx*sgn
        pts.append((bx+nx*w, by+ny*w))
    return pts

def dpath(pts, close=True):
    return "M %.2f %.2f "%pts[0] + " ".join("L %.2f %.2f"%p for p in pts[1:]) + (" Z" if close else "")

def rachis(curve, sway, t0, t1, w0, w1):
    a=[];b=[]
    for i in range(161):
        t=t0+(t1-t0)*i/160
        u=(t-t0)/(t1-t0)
        k=(w0+(w1-w0)*u)*math.sin(math.pi*u)**0.45
        bx,by=shaft(t,curve,sway); tx,ty=tangent(t,curve,sway)
        a.append((bx+ty*k, by-tx*k)); b.append((bx-ty*k, by+tx*k))
    return dpath(a+b[::-1])

def calamus(curve, sway, t0, t1, w0, w1):
    a=[];b=[]
    for i in range(41):
        t=t0+(t1-t0)*i/40
        u=i/40
        k=w0+(w1-w0)*u
        bx,by=shaft(t,curve,sway); tx,ty=tangent(t,curve,sway)
        a.append((bx+ty*k, by-tx*k)); b.append((bx-ty*k, by+tx*k))
    return dpath(a+b[::-1])

def nibshape(curve, sway, tbase, h, wcol):
    xe,ye = shaft(tbase,curve,sway)
    W=wcol
    bag=(f"M {xe-W:.2f} {ye-3.5:.2f} L {xe+W:.2f} {ye-3.5:.2f} "
         f"L {xe+W*0.88:.2f} {ye+5.5:.2f} L {xe-W*0.88:.2f} {ye+5.5:.2f} Z")
    y0=ye+7.0; y1=y0+h
    bec=(f"M {xe-W*0.86:.2f} {y0:.2f} L {xe+W*0.86:.2f} {y0:.2f} "
         f"C {xe+W*0.83:.2f} {y0+0.30*h:.2f} {xe+W*0.34:.2f} {y0+0.80*h:.2f} {xe+0.7:.2f} {y1:.2f} "
         f"L {xe-0.7:.2f} {y1:.2f} "
         f"C {xe-W*0.34:.2f} {y0+0.80*h:.2f} {xe-W*0.83:.2f} {y0+0.30*h:.2f} {xe-W*0.86:.2f} {y0:.2f} Z")
    sw=0.85
    fente=(f"M {xe-sw:.2f} {y0+0.26*h:.2f} L {xe+sw:.2f} {y0+0.26*h:.2f} "
           f"L {xe+0.35:.2f} {y1-1.5:.2f} L {xe-0.35:.2f} {y1-1.5:.2f} Z")
    r=2.5; cy=y0+0.19*h
    ev=(f"M {xe-r:.2f} {cy:.2f} A {r} {r} 0 1 0 {xe+r:.2f} {cy:.2f} "
        f"A {r} {r} 0 1 0 {xe-r:.2f} {cy:.2f} Z")
    return bag,bec,fente,ev

def build(fill=GOLD, grad=False, nib=False, swoosh=False, lean=0.0,
          curve=6.5, sway=2.0, peak=0.56, wmax=25.0, head=0.62, tailend=0.90,
          notches_l=((0.31,0.075,0.125,0.52),(0.51,0.075,0.125,0.52),(0.71,0.070,0.115,0.56)),
          notches_r=((0.41,0.075,0.125,0.54),(0.61,0.075,0.125,0.54),(0.79,0.065,0.095,0.60)),
          rach=(0.015,0.885,0.55,1.5), cal=(0.885,1.062,1.6,1.6), nibh=46.0, wcol=8.0):
    L=side(-1,curve,sway,peak,wmax,head,tailend,notches_l)
    R=side(+1,curve,sway,peak,wmax,head,tailend,notches_r)
    gid="g%d"%(abs(hash((fill,grad,nib,swoosh,lean)))%99999)
    paint=fill; defs=""
    if grad:
        defs=(f'<defs><linearGradient id="{gid}" x1="0.1" y1="0" x2="0.9" y2="1">'
              f'<stop offset="0" stop-color="#E9BE45"/><stop offset=".5" stop-color="#C6942A"/>'
              f'<stop offset="1" stop-color="#96691A"/></linearGradient></defs>')
        paint=f"url(#{gid})"
    subs=[dpath(L+R[::-1]), calamus(curve,sway,*cal), rachis(curve,sway,*rach)]
    if nib:
        bag,bec,fente,ev = nibshape(curve,sway,1.10,nibh,wcol)
        subs += [bec, bag, fente, ev]
    body=[f'<path fill-rule="evenodd" d="{" ".join(subs)}" fill="{paint}"/>']
    if swoosh:
        body.append(f'<path d="M -30 170 C 8 188 74 184 102 161 C 76 176 16 175 -16 166 Z" fill="{paint}"/>')
    inner="".join(body)
    # --- boite englobante reelle (pour un viewBox serre et une mise a l'echelle previsible)
    import math as _m
    pts = list(L)+list(R)
    for i in range(41):
        t=cal[0]+(cal[1]-cal[0])*i/40
        bx,by=shaft(t,curve,sway); tx,ty=tangent(t,curve,sway)
        k=cal[2]+(cal[3]-cal[2])*i/40
        pts += [(bx+ty*k,by-tx*k),(bx-ty*k,by+tx*k)]
    if nib:
        xe,ye=shaft(1.10,curve,sway)
        pts += [(xe-wcol,ye-3.5),(xe+wcol,ye-3.5),(xe,ye+7.0+nibh)]
    if swoosh:
        pts += [(-30,170),(102,161),(102,186)]
    if lean:
        a=_m.radians(lean); ca,sa=_m.cos(a),_m.sin(a); ox,oy=0.0,60.0
        pts=[(ox+(x-ox)*ca-(y-oy)*sa, oy+(x-ox)*sa+(y-oy)*ca) for x,y in pts]
    pad=4.0
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    x0,y0=min(xs)-pad,min(ys)-pad
    w,h=max(xs)-x0+pad, max(ys)-y0+pad
    g=f'<g transform="rotate({lean} 0 60)">{inner}</g>' if lean else inner
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}" '
            f'width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="xMidYMid meet">{defs}{g}</svg>')

V={
 "R1_reference":  dict(),
 "R2_lean":       dict(lean=-10, curve=8.0, sway=3.0),
 "R3_fine":       dict(wmax=21.5, peak=0.58, head=0.70,
      notches_l=((0.33,0.07,0.12,0.56),(0.53,0.07,0.12,0.56),(0.73,0.065,0.11,0.60)),
      notches_r=((0.43,0.07,0.12,0.58),(0.63,0.07,0.12,0.58),(0.80,0.06,0.09,0.63))),
 "R4_4barbes":    dict(wmax=26.0,
      notches_l=((0.27,0.065,0.105,0.50),(0.43,0.065,0.105,0.50),(0.59,0.065,0.105,0.52),(0.75,0.06,0.10,0.56)),
      notches_r=((0.35,0.065,0.105,0.52),(0.51,0.065,0.105,0.52),(0.67,0.065,0.105,0.54),(0.81,0.055,0.085,0.60))),
 "R5_nib":        dict(nib=True),
 "R6_logo":       dict(nib=True, swoosh=True, grad=True, lean=-8, curve=8.0, sway=3.0),
 "R7_logo_plat":  dict(nib=True, swoosh=True, lean=-8, curve=8.0, sway=3.0),
}
os.makedirs("/home/claude/plume/q",exist_ok=True)
for k,v in V.items(): open(f"/home/claude/plume/q/{k}.svg","w").write(build(**v))
print(" ".join(V))
