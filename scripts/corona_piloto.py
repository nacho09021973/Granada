"""Dos filas locales de transición. Corta las superficies de las hiladas en el
prisma convexo exterior y toma su relieve en el perímetro para el encuentro."""
import numpy as np
from mathutils.bvhtree import BVHTree

def dos_filas(V,F,p):
    base, techo = p[:192:2],p[1:192:2]
    eje=techo[0]-base[0]
    eje/=np.linalg.norm(eje)
    centro=(base[0]+base[48])/2
    interior=p[-191::2]
    radial=interior-centro
    h=radial@eje
    radial-=np.outer(h,eje)
    # Octógono exterior alrededor del marco, anchura elegida para dos filas.
    esquinas=radial[::12]*1.46
    normales=np.cross(np.roll(esquinas,-1,axis=0)-esquinas,eje)
    normales/=np.linalg.norm(normales,axis=1)[:,None]
    for i in range(8):
        if normales[i]@esquinas[i]<0:
            normales[i]*=-1
    lim=(esquinas*normales).sum(axis=1)
    radio=np.linalg.norm(radial,axis=1)
    dirs=radial/radio[:,None]
    ext=np.min(lim/np.maximum(dirs@normales.T,1e-10),axis=1)
    arbre=BVHTree.FromPolygons(V,F,all_triangles=True)
    heights=[]
    for i in range(96):
        punto=centro+dirs[i]*(ext[i]+0.005)
        hit=arbre.ray_cast(punto-10*eje,eje)[0]
        heights.append(h[i] if hit is None else (np.asarray(hit)-punto)@eje)
    rings=[interior]
    for fila in (0,1):
        ang=((np.arange(96)+6*fila)%12)/12
        perfil=1-np.abs(2*ang-1)
        for t in (0.20,0.55,0.82,1.):
            s=(fila+t)/2
            r=radio+(ext-radio)*s
            z=h*(1-s)+np.array(heights)*s+0.28*np.sin(np.pi*t)*perfil
            rings.append(centro+dirs*r[:,None]+np.outer(z,eje))
    caras=[]
    for k in range(len(rings)-1):
        for i in range(96):
            a=k*96+i
            b=k*96+(i+1)%96
            caras.extend([(a,b,b+96),(a,b+96,a+96)])
    # Solo examinar triángulos que puedan intersectar el prisma local.
    cerca=np.linalg.norm(V-centro,axis=1)<6
    sel=cerca[F].any(axis=1)
    trozos=[]
    for tri in V[F[sel]]:
        resto=list(tri)
        for normal,d in zip(normales,lim):
            if not resto: break
            dentro,fuera=[],[]
            for a,b in zip(resto,resto[1:]+resto[:1]):
                da,db=(a-centro)@normal-d,(b-centro)@normal-d
                (fuera if da>0 else dentro).append(a)
                if (da>0)!=(db>0):
                    x=a+(b-a)*da/(da-db)
                    dentro.append(x); fuera.append(x)
            for i in range(1,len(fuera)-1):
                trozos.extend([fuera[0],fuera[i],fuera[i+1]])
            resto=dentro
    return (np.vstack(rings),np.array(caras)),(np.array(trozos),np.arange(len(trozos)).reshape(-1,3)),sel
