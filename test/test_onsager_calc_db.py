import onsager.crystal as crystal
from Onsager_calc_db import *
from test_structs import *
import states
from representations import *
import unittest
from stars import *
from vector_stars import *

class test_dumbbell_mediated(unittest.TestCase):
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

        # self.jset0,self.jset2 = self.pdbcontainer_si.jumpnetwork(0.4,0.01,0.01), self.mdbcontainer_si.jumpnetwork(0.4,0.01,0.01)
        #
        # self.crys_stars = StarSet(self.pdbcontainer_si,self.mdbcontainer_si,self.jset0,self.jset2, Nshells=1)
        # self.vec_stars = vectorStars(self.crys_stars)
        #
        # #generate 1, 3 and 4 jumpnetworks
        # (self.jnet_1,self.jnet_1_indexed), self.jtype = self.crys_stars.jumpnetwork_omega1()
        # (self.symjumplist_omega43_all,self.symjumplist_omega43_all_indexed),(self.symjumplist_omega4,self.symjumplist_omega4_indexed),(self.symjumplist_omega3,self.symjumplist_omega3_indexed)=self.crys_stars.jumpnetwork_omega34(0.4,0.01,0.01,0.01)

        # self.W1list = np.ones(len(self.jnet_1))
        # self.W2list = np.ones(len(self.jset2[0]))
        # self.W3list = np.ones(len(self.symjumplist_omega3))
        # self.W4list = np.ones(len(self.symjumplist_omega4))

        #generate all the bias expansions - will separate out later
        #Previously, all the jumplists were created as arrays of ones.
        #To make things more concrete, we initialize them with random numbers
        self.onsagercalculator=dumbbellMediated(self.pdbcontainer_si,self.mdbcontainer_si,0.3,0.01,0.01,0.01,NGFmax=4,Nthermo=1)
        self.W1list = np.random.rand(len(self.onsagercalculator.jnet_1))
        self.W2list = np.random.rand(len(self.onsagercalculator.jnet0))
        self.W3list = np.random.rand(len(self.onsagercalculator.symjumplist_omega3))
        self.W4list = np.random.rand(len(self.onsagercalculator.symjumplist_omega4))
        self.biases =\
        self.onsagercalculator.vkinetic.biasexpansion(self.onsagercalculator.jnet_1,self.onsagercalculator.jnet2,self.onsagercalculator.om1types,self.onsagercalculator.symjumplist_omega43_all)

#     def test_displacements(self):
#
#         #Set up a simple jumpnetwork of three states in a cubic lattice
#         famp0 = [np.array([0.126,0.,0.])]
#         family = [famp0]
#         pdbcontainer = states.dbStates(cube,0,family)
#         mdbcontainer = states.mStates(cube,0,family)
#         jnet0_states,jnet_0_ind = pdbcontainer.jumpnetwork(0.3,0.01,0.01)
#         jnet2_states,jnet_2_ind = mdbcontainer.jumpnetwork(0.3,0.01,0.01)
#
#         jnet0_solute, jnet0_solvent = calc_dx_species(cube,jnet0_states,jnet_0_ind,type="bare")
#         jnet2_solute, jnet2_solvent = calc_dx_species(cube,jnet2_states,jnet_2_ind,type="mixed")
#
#         #We'll test if we have the correct displacement for the following jump, which should be there
# #         Jump object:
# #           Initial state:
# # 	             dumbbell :basis index = 0, lattice vector = [0 0 0], orientation = [0. 1. 0.]
# #           Final state:
# # 	             dumbbell :basis index = 0, lattice vector = [0 0 1], orientation = [0. 1. 0.]
# #                Jumping from c = -1 to c= -1
#         db1 = dumbbell(0,np.array([0.,.126,0.]),np.array([0,0,0],dtype=int))
#         db2 = dumbbell(0,np.array([.126,0.,0.]),np.array([0,0,1],dtype=int))
#         jmp_test = jump(db1,db2,-1,-1)
#         dx_test = np.array([0.0,0.0,0.28])
#         # dx_solvent = None
#         for i,jlist in enumerate(jnet0_states):
#             for j,jmp in enumerate(jlist):
#                 if  np.allclose(jmp_test.state1.o*jmp_test.c1,jmp.state1.o*jmp.c1):
#                     if  np.allclose(jmp_test.state2.o*jmp_test.c2,jmp.state2.o*jmp.c2):
#                         if np.allclose(jmp.state1.R,jmp_test.state1.R):
#                             if np.allclose(jmp.state2.R,jmp_test.state2.R):
#                                 dx_solvent = jnet0_solvent[i][j][1]                                #
#         # self.assertFalse(dx_solvent==None)
#         self.assertTrue(np.allclose(dx_solvent,dx_test),msg="dx_solvent,dx_test = {}, {}".format(dx_solvent,dx_test))
#         # self.assertTrue(jnet0_solute==None)

    def test_calc_eta(self):
        #set up the pre-factors and energies for rate calculations
        pre0 = np.random.rand(len(self.onsagercalculator.pdbcontainer.symorlist))
        betaene0 = np.random.rand(len(self.onsagercalculator.pdbcontainer.symorlist))
        pre0T = np.random.rand(len(self.onsagercalculator.jnet0))
        betaene0T = np.random.rand(len(self.onsagercalculator.jnet0))
        pre2 = np.random.rand(len(self.onsagercalculator.mdbcontainer.symorlist))
        betaene2 = np.random.rand(len(self.onsagercalculator.mdbcontainer.symorlist))
        pre2T = np.random.rand(len(self.onsagercalculator.jnet2))
        betaene2T = np.random.rand(len(self.onsagercalculator.jnet2))

        # (eta00_solvent,eta00_solute), (eta02_solvent,eta02_solute) = \
        self.onsagercalculator.calc_eta(pre0, betaene0, pre0T, betaene0T, pre2, betaene2, pre2T, betaene2T)

        self.assertEqual(len(self.onsagercalculator.eta00_solvent),len(self.onsagercalculator.vkinetic.starset.purestates))
        self.assertEqual(len(self.onsagercalculator.eta00_solute),len(self.onsagercalculator.vkinetic.starset.purestates))

        self.assertEqual(len(self.onsagercalculator.eta02_solvent),len(self.onsagercalculator.vkinetic.starset.mixedstates))
        self.assertEqual(len(self.onsagercalculator.eta02_solute),len(self.onsagercalculator.vkinetic.starset.mixedstates))

        if len(self.onsagercalculator.vkinetic.vecpos_bare)==0:
            self.assertTrue(np.allclose(self.onsagercalculator.eta00_solvent,np.zeros((len(self.onsagercalculator.vkinetic.starset.purestates),3))))
            self.assertTrue(np.allclose(self.onsagercalculator.eta00_solute,np.zeros((len(self.onsagercalculator.vkinetic.starset.purestates),3))))

        else:
            #The non-local pure dumbbell biases have been tested in test_vecstars.
            #Here, we check if for periodic dumbbells, we have the same solvent bias.
            for i in range(len(self.onsagercalculator.vkinetic.starset.purestates)):
                for j in range(len(self.onsagercalculator.vkinetic.starset.purestates)):
                    if self.onsagercalculator.vkinetic.starset.purestates[i].db.i == self.onsagercalculator.vkinetic.starset.purestates[j].db.i:
                        if np.allclose(self.onsagercalculator.vkinetic.starset.purestates[i].o,self.onsagercalculator.vkinetic.starset.purestates[j].o):
                            self.assertTrue(np.allclose(self.onsagercalculator.eta00_solvent[i,:]),np.allclose(self.onsagercalculator.eta00_solvent[j,:]))

        Nvstars_pure = self.onsagercalculator.vkinetic.Nvstars_pure
        for i in range(len(self.onsagercalculator.eta02_solvent)):
            #get the indices of the state
            st = self.onsagercalculator.vkinetic.starset.mixedstates[i]
            #next get the vectorstar,state indices
            indlist = self.onsagercalculator.vkinetic.stateToVecStar_mixed[st]
            #The IndOfStar in indlist for the mixed case is already shifted by the number of pure vector stars.
            if len(indlist)!=0:
                vlist=[]
                for tup in indlist:
                    vlist.append(self.onsagercalculator.vkinetic.vecvec[tup[0]][tup[1]])
                eta_test_solvent = sum([np.dot(self.onsagercalculator.eta02_solvent[i,:],v)*v for v in vlist])
                eta_test_solute = sum([np.dot(self.onsagercalculator.eta02_solute[i,:],v)*v for v in vlist])
                # print(vlist)
                self.assertTrue(np.allclose(eta_test_solvent*len(self.onsagercalculator.vkinetic.vecvec[indlist[0][0]]),self.onsagercalculator.eta02_solvent[i]),msg="{} {}".format(eta_test_solvent,self.onsagercalculator.eta02_solvent[i]))
                self.assertTrue(np.allclose(eta_test_solute*len(self.onsagercalculator.vkinetic.vecvec[indlist[0][0]]),self.onsagercalculator.eta02_solute[i]),msg="{} {}".format(eta_test_solute,self.onsagercalculator.eta02_solute[i]))

        # #test that the periodic eta vectors are same for dumbbells having the same orientation and lattice sites.
        # #For the pure states only - for the mixed states, the states are origin states anyway, so a dumbbell can't be repeated
        # for i,st1 in enumerate(self.onsagercalculator.vkinetic.starset.purestates):
        #     for j,st2 in enumerate(self.onsagercalculator.vkinetic.starset.purestates):
        #         #check if the dumbbells have the same orientation site vectors
        #         if st1.db.i==st2.db.i and np.allclose(st1.db.o,st2.db.o):
        #             self.assertTrue(np.allclose(self.onsagercalculator.eta00_solvent[i,:],self.onsagercalculator.eta00_solvent[j,:]),msg="{}\n{}".format(st1,st2))
        #             #eta00 for solute is suppose to be zero anyway, but still check if something funny is not going on.
        #             self.assertTrue(np.allclose(self.onsagercalculator.eta00_solute[i],self.onsagercalculator.eta00_solute[j]))
        #             self.assertTrue(np.allclose(self.onsagercalculator.eta00_solute[i],np.zeros(3)))

    def test_bias_updates(self):
        """
        This is to check if the del_bias expansions are working fine.
        """
        pass
        # pre0 = np.ones(len(self.onsagercalculator.pdbcontainer.symorlist))
        # betaene0 = np.ones(len(self.onsagercalculator.pdbcontainer.symorlist))
        # pre0T = np.ones(len(self.onsagercalculator.jnet0))
        # betaene0T = np.ones(len(self.onsagercalculator.jnet0))
        # pre2 = np.ones(len(self.onsagercalculator.mdbcontainer.symorlist))
        # betaene2 = np.ones(len(self.onsagercalculator.mdbcontainer.symorlist))
        # pre2T = np.ones(len(self.onsagercalculator.jnet2))
        # betaene2T = np.ones(len(self.onsagercalculator.jnet2))
        #
        # self.onsagercalculator.calc_eta(pre0, betaene0, pre0T, betaene0T, pre2, betaene2, pre2T, betaene2T)
