import numpy as np
import onsager.crystal as crystal
from stars import *
from test_structs import *
from states import *
from representations import *
from functools import reduce
from vector_stars import *
from test_structs import *
import unittest

class test_vecstars(unittest.TestCase):
    def setUp(self):
        latt = np.array([[0.,0.5,0.5],[0.5,0.,0.5],[0.5,0.5,0.]])*0.55
        self.DC_Si = crystal.Crystal(latt,[[np.array([0.,0.,0.]),np.array([0.25,0.25,0.25])]],["Si"])
        self.cube = cube
        #keep it simple with [1.,0.,0.] type orientations for now
        o = np.array([1.,0.,0.])/np.linalg.norm(np.array([1.,0.,0.]))*0.126
        famp0 = [o.copy()]
        family = [famp0]

        self.pdbcontainer_si = dbStates(self.DC_Si,0,family)
        self.mdbcontainer_si = mStates(self.DC_Si,0,family)

        self.jset0,self.jset2 = self.pdbcontainer_si.jumpnetwork(0.4,0.01,0.01), self.mdbcontainer_si.jumpnetwork(0.4,0.01,0.01)

        self.crys_stars = StarSet(self.pdbcontainer_si,self.mdbcontainer_si,self.jset0,self.jset2, Nshells=2)
        self.vec_stars = vectorStars(self.crys_stars)

        #generate 1, 3 and 4 jumpnetworks
        (self.jnet_1,self.jnet_1_indexed), self.jtype = self.crys_stars.jumpnetwork_omega1()
        (self.symjumplist_omega43_all,self.symjumplist_omega43_all_indexed),(self.symjumplist_omega4,self.symjumplist_omega4_indexed),(self.symjumplist_omega3,self.symjumplist_omega3_indexed)=self.crys_stars.jumpnetwork_omega34(0.4,0.01,0.01,0.01)

        self.W1list = np.ones(len(self.jnet_1))
        self.W2list = np.ones(len(self.jset2[0]))
        self.W3list = np.ones(len(self.symjumplist_omega3))
        self.W4list = np.ones(len(self.symjumplist_omega4))

        #generate all the bias expansions - will separate out later
        self.biases = self.vec_stars.biasexpansion(self.jnet_1,self.jset2[0],self.jtype,self.symjumplist_omega43_all)

    def test_basis(self):
        self.assertEqual(len(self.vec_stars.vecpos),len(self.vec_stars.vecvec))
        #choose a random vector star
        vecstarind = np.random.randint(0,len(self.vec_stars.vecpos))
        #get the representative state of the star
        testvecstate = self.vec_stars.vecpos[vecstarind][0]
        count=0
        for i in range(len(self.vec_stars.vecpos)):
            if self.vec_stars.vecpos[vecstarind][0] == self.vec_stars.vecpos[i][0]:
                count += 1
                #The number of times the position list is repeated is also the dimensionality of the basis.

        #Next see what is the algaebric multiplicity of the eigenvalue 1.
        glist=[]
        for g in self.crys_stars.crys.G:
            pairnew = testvecstate.gop(self.crys_stars.crys, self.crys_stars.chem, g)
            pairnew = pairnew - pairnew.R_s
            if vecstarind < self.vec_stars.Nvstars_pure:
                if pairnew == testvecstate or pairnew==-testvecstate:
                    glist.append(g)
            else:
                if pairnew == testvecstate:
                    glist.append(g)
        sumg = sum([g.cartrot for g in glist])/len(glist)
        vals,vecs = np.linalg.eig(sumg)
        count_eigs=0
        for val in vals:
            if np.allclose(val,1.0,atol=1e-8):
                count_eigs+=1
        self.assertEqual(count,count_eigs,msg="{}".format(testvecstate))

    def test_state_indexing(self):
        for st in self.vec_stars.starset.purestates:
            indToVecStars = self.vec_stars.stateToVecStar_pure[st]
            for tup in indToVecStars:
                self.assertEqual(st,self.vec_stars.vecpos[tup[0]][tup[1]])

        for st in self.vec_stars.starset.mixedstates:
            indToVecStars = self.vec_stars.stateToVecStar_mixed[st]
            for tup in indToVecStars:
                self.assertEqual(st,self.vec_stars.vecpos[tup[0]][tup[1]])

    def test_bias1expansions(self):
        for i in range(10):
            #test bias_1
            #select a representative state and another state in the same star at random
            #from complex state space
            starind = np.random.randint(0,self.vec_stars.Nvstars_pure)
            st = self.vec_stars.vecpos[starind][0] #get the representative state.
            n = np.random.randint(0,len(self.vec_stars.vecpos[starind]))
            st2 = self.vec_stars.vecpos[starind][n]
            #Now, we calculate the total bias vector - zero for solute in complex space
            bias_st_solvent=np.zeros(3)
            bias_st_solvent2=np.zeros(3)
            count=0
            for jt,jlist in enumerate(self.jnet_1):
                for j in jlist:
                    if st==j.state1:
                        count+=1
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        bias_st_solvent += self.W1list[jt]*dx
                    if st2==j.state1:
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        bias_st_solvent2 += self.W1list[jt]*dx

            bias1expansion_solute,bias1expansion_solvent = self.biases[1]
            self.assertTrue(count>=1)
            self.assertTrue(np.allclose(bias1expansion_solute,np.zeros_like(bias1expansion_solute)),msg="{}\n{}".format(bias1expansion_solute,bias1expansion_solute))
            self.assertEqual(bias1expansion_solvent.shape[1],len(self.W1list))

            #get the total bias vector
            bias1expansion_solute,bias1expansion_solvent = self.biases[1]
            tot_bias_solvent = np.dot(bias1expansion_solvent,self.W1list)
            #now get the components of the given states
            indlist=[]
            # bias_cartesian = np.zeros(3)
            for ind,starlist in enumerate(self.vec_stars.vecpos):
                if starlist[0]==st:
                    indlist.append(ind)

            bias_cartesian = sum([tot_bias_solvent[i]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian2 = sum([tot_bias_solvent[i]*self.vec_stars.vecvec[i][n] for i in indlist])

            self.assertTrue(np.allclose(bias_cartesian,bias_st_solvent))
            self.assertTrue(np.allclose(bias_cartesian2,bias_st_solvent2)

    def test_bias2expansions(self):
        for i in range(10):
            #test omega2 expansion
            starind = np.random.randint(self.vec_stars.Nvstars_pure,self.vec_stars.Nvstars)
            st = self.vec_stars.vecpos[starind][0] #get the representative state.
            n = np.random.randint(0,len(self.vec_stars.vecpos[starind]))
            st2 = self.vec_stars.vecpos[starind][n]
            #Now, we calculate the total bias vector
            bias_st_solute=np.zeros(3)
            bias_st_solute2=np.zeros(3)
            bias_st_solvent=np.zeros(3)
            bias_st_solvent2=np.zeros(3)
            count=0
            for jlist in self.jset2[0]:
                for j in jlist:
                    if st==j.state1:
                        count+=1
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        dx_solute = dx + j.state2.db.o/2. - j.state1.db.o/2.
                        dx_solvent = dx - j.state2.db.o/2. + j.state1.db.o/2.
                        bias_st_solute += dx_solute
                        bias_st_solvent += dx_solvent
                    if st2==j.state1:
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        dx_solute = dx + j.state2.db.o/2. - j.state1.db.o/2.
                        dx_solvent = dx - j.state2.db.o/2. + j.state1.db.o/2.
                        bias_st_solute2 += dx_solute
                        bias_st_solvent2 += dx_solvent

            bias2expansion_solute,bias2expansion_solvent = self.biases[2]
            self.assertTrue(count>=1)
            self.assertEqual(bias2expansion_solvent.shape[1],len(self.W2list))
            # vectors
            tot_bias_solvent = np.dot(bias2expansion_solvent,self.W2list)
            tot_bias_solute = np.dot(bias2expansion_solute,self.W2list)

            #now get the components
            indlist=[]
            # bias_cartesian = np.zeros(3)
            for ind,starlist in enumerate(self.vec_stars.vecpos):
                if starlist[0]==st:
                    indlist.append(ind)

            bias_cartesian_solvent = sum([tot_bias_solvent[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian_solvent2 = sum([tot_bias_solvent[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][n] for i in indlist])

            bias_cartesian_solute = sum([tot_bias_solute[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian_solute2 = sum([tot_bias_solute[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][n] for i in indlist])

            self.assertTrue(np.allclose(bias_cartesian_solvent,bias_st_solvent),msg="{}\n{}".format(bias_cartesian_solvent,bias_st_solvent)) #should get the same bias vector anyway
            self.assertTrue(np.allclose(bias_cartesian_solvent2,bias_st_solvent2),msg="{}\n{}".format(bias_cartesian_solvent2,bias_st_solvent2))

            self.assertTrue(np.allclose(bias_cartesian_solute,bias_st_solute),msg="{}\n{}".format(bias_cartesian_solute,bias_st_solute)) #should get the same bias vector anyway
            self.assertTrue(np.allclose(bias_cartesian_solute2,bias_st_solute2),msg="{}\n{}".format(bias_cartesian_solute2,bias_st_solute2))

    def test_bias43expansions(self):
        for i in range(10):
            #test omega2 expansion
            starindpure = np.random.randint(0,self.vec_stars.Nvstars_pure)
            starindmixed = np.random.randint(self.vec_stars.Nvstars_pure,self.vec_stars.Nvstars)

            st_pure = self.vec_stars.vecpos[starindpure][0] #get the representative state.
            n_pure = np.random.randint(0,len(self.vec_stars.vecpos[starindpure]))
            st2_pure = self.vec_stars.vecpos[starindpure][n_pure]

            st_mixed = self.vec_stars.vecpos[starindmixed][0] #get the representative state.
            n_mixed = np.random.randint(0,len(self.vec_stars.vecpos[starindmixed]))
            st2_mixed = self.vec_stars.vecpos[starindmixed][n_mixed]

            #Now, we calculate the total bias vector
            bias4_st_solute=np.zeros(3)
            bias4_st_solute2=np.zeros(3)
            bias4_st_solvent=np.zeros(3)
            bias4_st_solvent2=np.zeros(3)

            bias3_st_solute=np.zeros(3)
            bias3_st_solute2=np.zeros(3)
            bias3_st_solvent=np.zeros(3)
            bias3_st_solvent2=np.zeros(3)

            count=0
            for jlist in self.symjumplist_omega4:
                #In omega_4, the intial state should be a complex
                for j in jlist:
                    if st_pure==j.state1:
                        count+=1
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        dx_solute = j.state2.db.o/2. #state2 is the mixed dumbbell.
                        dx_solvent = dx - j.state2.db.o/2.
                        bias4_st_solute += dx_solute
                        bias4_st_solvent += dx_solvent
                    if st2_pure==j.state1:
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        dx_solute = j.state2.db.o/2. #state2 is the mixed dumbbell.
                        dx_solvent = dx - j.state2.db.o/2.
                        bias4_st_solute2 += dx_solute
                        bias4_st_solvent2 += dx_solvent

            bias4expansion_solute,bias4expansion_solvent = self.biases[4]
            self.assertTrue(count>=1)
            self.assertEqual(bias4expansion_solvent.shape[1],len(self.W4list))
            self.assertEqual(bias4expansion_solute.shape[1],len(self.W4list))
            # vectors
            tot_bias_solvent = np.dot(bias4expansion_solvent,self.W4list)
            tot_bias_solute = np.dot(bias4expansion_solute,self.W4list)

            #now get the components
            indlist=[]
            # bias_cartesian = np.zeros(3)
            for ind,starlist in enumerate(self.vec_stars.vecpos):
                if starlist[0]==st_pure:
                    indlist.append(ind)

            bias_cartesian_solvent = sum([tot_bias_solvent[i]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian_solvent2 = sum([tot_bias_solvent[i]*self.vec_stars.vecvec[i][n_pure] for i in indlist])

            bias_cartesian_solute = sum([tot_bias_solute[i]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian_solute2 = sum([tot_bias_solute[i]*self.vec_stars.vecvec[i][n_pure] for i in indlist])

            self.assertTrue(np.allclose(bias_cartesian_solvent,bias4_st_solvent),msg="{}\n{}".format(bias_cartesian_solvent,bias4_st_solvent)) #should get the same bias vector anyway
            self.assertTrue(np.allclose(bias_cartesian_solvent2,bias4_st_solvent2),msg="{}\n{}".format(bias_cartesian_solvent2,bias4_st_solvent2))

            self.assertTrue(np.allclose(bias_cartesian_solute,bias4_st_solute),msg="{}\n{}".format(bias_cartesian_solute,bias4_st_solute)) #should get the same bias vector anyway
            self.assertTrue(np.allclose(bias_cartesian_solute2,bias4_st_solute2),msg="{}\n{}".format(bias_cartesian_solute2,bias4_st_solute2))

            count=0
            for jlist in self.symjumplist_omega3:
                #In omega_3, the intial state should be a mixed dumbbell
                for j in jlist:
                    if st_mixed==j.state1:
                        count+=1
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        dx_solute = -j.state1.db.o/2.
                        dx_solvent = dx + j.state1.db.o/2.
                        bias3_st_solute += dx_solute
                        bias3_st_solvent += dx_solvent
                    if st2_mixed==j.state1:
                        dx = disp(self.crys_stars.crys,self.crys_stars.chem,j.state1,j.state2)
                        dx_solute = -j.state1.db.o/2.
                        dx_solvent = dx + j.state1.db.o/2.
                        bias3_st_solute2 += dx_solute
                        bias3_st_solvent2 += dx_solvent

            bias3expansion_solute,bias3expansion_solvent = self.biases[3]
            self.assertTrue(count>=1)
            self.assertEqual(bias3expansion_solvent.shape[1],len(self.W3list))
            self.assertEqual(bias3expansion_solute.shape[1],len(self.W3list))
            # vectors
            tot_bias_solvent = np.dot(bias3expansion_solvent,self.W3list)
            tot_bias_solute = np.dot(bias3expansion_solute,self.W3list)

            #now get the components
            indlist=[]
            # bias_cartesian = np.zeros(3)
            for ind,starlist in enumerate(self.vec_stars.vecpos):
                if starlist[0]==st_mixed:
                    indlist.append(ind)
            # print(indlist)
            bias_cartesian_solvent = sum([tot_bias_solvent[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian_solvent2 = sum([tot_bias_solvent[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][n_mixed] for i in indlist])

            bias_cartesian_solute = sum([tot_bias_solute[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][0] for i in indlist])
            bias_cartesian_solute2 = sum([tot_bias_solute[i-self.vec_stars.Nvstars_pure]*self.vec_stars.vecvec[i][n_mixed] for i in indlist])

            self.assertTrue(np.allclose(bias_cartesian_solvent,bias3_st_solvent),msg="{}\n{}".format(bias_cartesian_solvent,bias3_st_solvent)) #should get the same bias vector anyway
            self.assertTrue(np.allclose(bias_cartesian_solvent2,bias3_st_solvent2),msg="{}\n{}".format(bias_cartesian_solvent2,bias3_st_solvent2))

            self.assertTrue(np.allclose(bias_cartesian_solute,bias3_st_solute),msg="{}\n{}".format(bias_cartesian_solute,bias3_st_solute)) #should get the same bias vector anyway
            self.assertTrue(np.allclose(bias_cartesian_solute2,bias3_st_solute2),msg="{}\n{}".format(bias_cartesian_solute2,bias3_st_solute2))
