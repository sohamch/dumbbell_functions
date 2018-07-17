import numpy as np
import onsager.crystal as crystal
from representations import *
from states import *
from collision import *
import time
def purejumps(crys,chem,iorset,cutoff,solv_solv_cut,closestdistance):
    """
    Makes a jumpnetwork of pure dumbbells within a given distance to be used for omega_0
    and to create the solute-dumbbell stars.
    Parameters:
        crys,chem - working crystal object and sublattice respectively.
        iorset - allowed orientations in the given sublattice (negatives excluded)
        cutoff - maximum jump distance
        solv_solv_cut - minimum allowable distance between two solvent atoms - to check for collisions
        closestdistance - minimum allowable distance to check for collisions with other atoms. Can be a single
        number or a list (corresponding to each sublattice)
    """
    def inset(j,s):
        return hash(j) in s

    def inlist(j,l):
        return any(hash(j)==hash(j1) for j1 in l)

    def dx_excess(db1,db2):
        (i1,i2) = (db1.i,db2.i)
        (R1,R2) = (db1.R,db2.R)
        dR = crys.unit2cart(R2,crys.basis[chem][i2]) - crys.unit2cart(R1,crys.basis[chem][i1])
        if np.dot(dR,dR) > cutoff**2:
            return True

    nmax = [int(np.round(np.sqrt(cutoff**2/crys.metric[i,i]))) + 1 for i in range(3)]
    Rvects = [np.array([n0,n1,n2]) for n0 in range(-nmax[0],nmax[0]+1)
                                 for n1 in range(-nmax[1],nmax[1]+1)
                                 for n2 in range(-nmax[2],nmax[2]+1)]
    jumplist=[]
    hashset=set([])
    tcheck=[]
    tlen = []
    dbstates = dbStates(crys,chem,iorset)
    print("Entering main loop")
    count=0
    for R in Rvects:
        for i in iorset:
            for f in iorset:
                db1 = dumbbell(i[0],i[1],np.array([0,0,0]))
                db2 = dumbbell(f[0],f[1],R)
                if db1==db2:#catch the diagonal case
                    continue
                if dx_excess(db1,db2):
                    continue
                for c1 in[-1,1]:
                    rotcheck = i[0]==f[0] and np.allclose(R,0,atol=crys.threshold)
                    if rotcheck:
                        j = jump(db1,db2,c1,1)
                        start = time.time()
                        cond=inset(j,hashset)
                        tcheck.append(time.time()-start)
                        tlen.append(len(hashset))
                        if cond: #no point doing anything else if the jump has already been considered
                            continue
                        if not (collision_self(crys,chem,j,solv_solv_cut,solv_solv_cut) or collision_others(crys,chem,j,closestdistance)):
                            #If the jump has not already been considered, check if it leads to collisions.
                            jlist=[]
                            for g in crys.G:
                                # jnew = j.gop(crys,chem,g)
                                db1new = dbstates.gdumb(g,db1)
                                db2new = dbstates.gdumb(g,db2)
                                jnew = jump(db1new[0],db2new[0],c1*db1new[1],1*db2new[1])
                                if not inset(jnew,hashset):
                                    jlist.append(jnew)
                                    # jlist.append(-jnew)
                                    hashset.add(hash(jnew))
                                    # hashset.add(hash(-jnew))
                            jumplist.append(jlist)
                            continue
                    for c2 in [-1,1]:
                        j = jump(db1,db2,c1,c2)
                        start = time.time()
                        cond=inset(j,hashset)
                        tcheck.append(time.time()-start)
                        tlen.append(len(hashset))
                        if cond: #no point doing anything else if the jump has already been considered
                            continue
                        if not (collision_self(crys,chem,j,solv_solv_cut,solv_solv_cut) or collision_others(crys,chem,j,closestdistance)):
                            #If the jump has not already been considered, check if it leads to collisions.
                            jlist=[]
                            for g in crys.G:
                                # jnew = j.gop(crys,chem,g)
                                db1new = dbstates.gdumb(g,db1)
                                db2new = dbstates.gdumb(g,db2)
                                jnew = jump(db1new[0],db2new[0],c1*db1new[1],c2*db2new[1])
                                if not inset(jnew,hashset):
                                    jlist.append(jnew)
                                    # jlist.append(-jnew)
                                    hashset.add(hash(jnew))
                                    # hashset.add(hash(-jnew))
                            jumplist.append(jlist)
    return jumplist,tcheck,tlen

def mixedjumps(crys,chem,iorset,cutoff,solt_solv_cut,closestdistance):
    """
    Makes a jumpnetwork of pure dumbbells within a given distance to be used for omega_0
    and to create the solute-dumbbell stars.
    Parameters:
        crys,chem - working crystal object and sublattice respectively.
        iorset - allowed orientations in the given sublattice for mixed dumbbells
        cutoff - maximum jump distance
        solt_solv_cut - minimum allowable distance between solute and solvent atoms - to check for collisions
        closestdistance - minimum allowable distance to check for collisions with other atoms. Can be a single
        number or a list (corresponding to each sublattice)
    """
    nmax = [int(np.round(np.sqrt(cutoff**2/crys.metric[i,i]))) + 1 for i in range(3)]
    Rvects = [np.array([n0,n1,n2]) for n0 in range(-nmax[0],nmax[0]+1)
                                 for n1 in range(-nmax[1],nmax[1]+1)
                                 for n2 in range(-nmax[2],nmax[2]+1)]
    jumplist=[]
    mstates = mStates(crys,chem,iorset)
    for i in iorset:
        for f in iorset:
            for R in Rvects:
                db1 = dumbbell(i[0],i[1],np.array([0,0,0]))
                p1 = Sdpair(i[0],np.array([0,0,0]),db1)
                db2=dumbbell(f[0],f[1],R)
                p2 = Sdpair(f[0],R,db2)
                j = jump(p1,p2,1,1)#since only solute moves, both indicators are +1
                if not inset(jump,jumplist):
                    newlist=[]
                    for g in crys.G:
                        jnew=j.gop(crys,chem,g)
                        if not inlist(jnew,newlist):
                            newlist.append(jnew)
                            newlist.append(-jnew)
                    jumplist.append(newlist)
