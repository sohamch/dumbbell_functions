import numpy as np
import onsager.crystal as crystal
from states import *
from representations import *
from test_structs import *
# from gensets import *
import unittest

class test_statemaking(unittest.TestCase):
    def setUp(self):
        famp0 = [np.array([1.,1.,0.]),np.array([1.,0.,0.])]
        famp12 = [np.array([1.,1.,1.]),np.array([1.,1.,0.])]
        self.family = [famp0,famp12]
        self.crys = tet2
        # self.pairs_pure = genpuresets(tet2,0,family)
        # self.pairs_mixed = genmixedsets(tet2,0,family)
        #generating pairs from families is now taken care of within states

    def test_dbStates(self):
        #check that symmetry analysis is correct
        dbstates=dbStates(self.crys,0,self.family)
        self.assertEqual(len(dbstates.symorlist),4)
        #check that every (i,or) set is accounted for
        sm=0
        for i in dbstates.symorlist:
            sm += len(i)
        self.assertEqual(sm,len(dbstates.iorlist))

        #test group operations
        db=dumbbell(1, np.array([1.,1.,0.]), np.array([1,1,0]))
        Glist = list(dbstates.crys.G)
        x = np.random.randint(0,len(Glist))
        g = Glist[x] #select random groupop
        newdb_test = db.gop(self.crys,0,g)
        newdb, p = dbstates.gdumb(g,db)
        count=0
        if(newdb_test==newdb):
            self.assertEqual(p,1)
            count=1
        elif(newdb_test==-newdb):
            self.assertEqual(p,-1)
            count=1
        self.assertEqual(count,1)

        #test indexmapping
        for stateind,tup in enumerate(dbstates.iorlist):
            i,o = tup[0],tup[1]
            R, (ch,inew) = dbstates.crys.g_pos(g,np.array([0,0,0]),(dbstates.chem,i))
            onew  = np.dot(g.cartrot,o)
            if any(np.allclose(onew+t[1],0,atol=1.e-8) for t in dbstates.iorlist):
                onew = -onew
            count=0
            for j,t in enumerate(dbstates.iorlist):
                if(t[0]==inew and np.allclose(t[1],onew)):
                    foundindex=j
                    count+=1
            self.assertEqual(count,1)
            self.assertEqual(foundindex,dbstates.indexmap[x][stateind])
    #Test jumpnetwork
    def test_purejumps(self):
        famp0 = [np.array([1.,0.,0.])/np.linalg.norm(np.array([1.,0.,0.]))*0.126]
        family = [famp0]
        pdbcontainer = dbStates(cube,0,family)
        jset,jind = pdbcontainer.jumpnetwork(0.3,0.01,0.01)
        test_dbi = dumbbell(0, np.array([0.126,0.,0.]),np.array([0,0,0]))
        test_dbf = dumbbell(0, np.array([0.126,0.,0.]),np.array([0,1,0]))
        count=0
        for i,jlist in enumerate(jset):
            for q,j in enumerate(jlist):
                if j.state1 == test_dbi or j.state1 == -test_dbi:
                    if j.state2 == test_dbf or j.state2 == -test_dbf:
                        if j.c1 == j.c2 == -1:
                           count += 1
                           jtest = jlist
        self.assertEqual(count,1) #see that this jump has been taken only once into account
        self.assertEqual(len(jtest),24)

        #test_indices
        #First check if they have the same number of lists and elements
        self.assertEqual(len(jind),len(jset))
        #now check if all the elements are correctly correspondent
        for lindex in range(len(jind)):
            self.assertEqual(len(jind[lindex]),len(jset[lindex]))
            for jindex in range(len(jind[lindex])):
                (i1,o1) = pdbcontainer.iorlist[jind[lindex][jindex][0]]
                (i2,o2) = pdbcontainer.iorlist[jind[lindex][jindex][1]]
                self.assertEqual(jset[lindex][jindex].state1.i,i1)
                self.assertEqual(jset[lindex][jindex].state2.i,i2)
                self.assertTrue(np.allclose(jset[lindex][jindex].state1.o,o1))
                self.assertTrue(np.allclose(jset[lindex][jindex].state2.o,o2))

    def test_mStates(self):
        dbstates=dbStates(self.crys,0,self.family)
        mstates1 = mStates(self.crys,0,self.family)

        #check that symmetry analysis is correct
        self.assertEqual(len(mstates1.symorlist),4)

        #check that negative orientations are accounted for
        for i in range(4):
            self.assertEqual(len(mstates1.symorlist[i])/len(dbstates.symorlist[i]),2)

        #check that every (i,or) set is accounted for
        sm=0
        for i in mstates1.symorlist:
            sm += len(i)
        self.assertEqual(sm,len(mstates1.iorlist))

        #check indexmapping
        Glist = list(mstates1.crys.G)
        x = np.random.randint(0,len(Glist))
        g = Glist[x] #select random groupop
        i,o = mstates1.iorlist[0]
        for stateind,tup in enumerate(mstates1.iorlist):
            i,o = tup[0],tup[1]
            R, (ch,inew) = mstates1.crys.g_pos(g,np.array([0,0,0]),(mstates1.chem,i))
            onew  = np.dot(g.cartrot,o)
            count=0
            for j,t in enumerate(mstates1.iorlist):
                if(t[0]==inew and np.allclose(t[1],onew)):
                    foundindex=j
                    count+=1
            self.assertEqual(count,1)
            self.assertEqual(foundindex,mstates1.indexmap[x][stateind])

    def test_mixedjumps(self):
        famp0 = [np.array([1.,0.,0.])/np.linalg.norm(np.array([1.,0.,0.]))*0.126]
        family = [famp0]
        mdbcontainer = mStates(cube,0,family)
        #check for the correct number of states
        jset,jind = mdbcontainer.jumpnetwork(0.3,0.01,0.01)
        test_dbi = dumbbell(0, np.array([0.126,0.,0.]),np.array([0,0,0]))
        test_dbf = dumbbell(0, np.array([0.126,0.,0.]),np.array([0,1,0]))
        count=0
        for i,jlist in enumerate(jset):
            for q,j in enumerate(jlist):
                if j.state1.db == test_dbi:
                    if j.state2.db == test_dbf:
                        if j.c1 == j.c2 == 1:
                           count += 1
                           jtest = jlist
        self.assertEqual(count,1) #see that this jump has been taken only once into account
        self.assertEqual(len(jtest),24)

        #check if conditions for mixed dumbbell transitions are satisfied
        count=0
        for jl in jset:
            for j in jl:
                if j.c1==-1 or j.c2==-1:
                    count+=1
                    break
                if not (j.state1.i_s==j.state1.db.i and j.state2.i_s==j.state2.db.i and np.allclose(j.state1.R_s,j.state1.db.R) and np.allclose(j.state2.R_s,j.state2.db.R)):
                    count+=1
                    break
            if count==1:
                break
        self.assertEqual(count,0)

        #test_indices
        #First check if they have the same number of lists and elements
        self.assertEqual(len(jind),len(jset))
        #now check if all the elements are correctly correspondent
        for lindex in range(len(jind)):
            self.assertEqual(len(jind[lindex]),len(jset[lindex]))
            for jindex in range(len(jind[lindex])):
                (i1,o1) = mdbcontainer.iorlist[jind[lindex][jindex][0]]
                (i2,o2) = mdbcontainer.iorlist[jind[lindex][jindex][1]]
                self.assertEqual(jset[lindex][jindex].state1.db.i,i1)
                self.assertEqual(jset[lindex][jindex].state2.db.i,i2)
                self.assertTrue(np.allclose(jset[lindex][jindex].state1.db.o,o1))
                self.assertTrue(np.allclose(jset[lindex][jindex].state2.db.o,o2))