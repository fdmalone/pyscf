#!/usr/bin/env python
# Copyright 2014-2018 The PySCF Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

import unittest
import numpy
import scipy.linalg
import tempfile
from pyscf import gto
from pyscf import scf
from pyscf import dft

h2o_z0 = gto.M(
    verbose = 5,
    output = '/dev/null',
    atom = [
    ["O" , (0. , 0.     , 0.)],
    [1   , (0. , -0.757 , 0.587)],
    [1   , (0. , 0.757  , 0.587)] ],
    basis = '6-31g')

h2o_z1 = gto.M(
    verbose = 5,
    output = '/dev/null',
    atom = [
    ["O" , (0. , 0.     , 0.)],
    [1   , (0. , -0.757 , 0.587)],
    [1   , (0. , 0.757  , 0.587)] ],
    basis = '6-31g',
    charge = 1,
    spin = 1,)

h2o_z0_s = gto.M(
    verbose = 5,
    output = '/dev/null',
    atom = [
    ["O" , (0. , 0.     , 0.)],
    [1   , (0. , -0.757 , 0.587)],
    [1   , (0. , 0.757  , 0.587)] ],
    symmetry = 1,
    basis = '6-31g')

h2o_z1_s = gto.M(
    verbose = 5,
    output = '/dev/null',
    atom = [
    ["O" , (0. , 0.     , 0.)],
    [1   , (0. , -0.757 , 0.587)],
    [1   , (0. , 0.757  , 0.587)] ],
    basis = '6-31g',
    charge = 1,
    spin = 1,
    symmetry = 1,)

h4_z0_s = gto.M(
    verbose = 5,
    output = '/dev/null',
    atom = '''C 0 0 0
    H  1  1  1
    H -1 -1  1
    H -1  1 -1
    H  1 -1 -1''',
    basis = '6-31g',
    symmetry = 1,)

h4_z1_s = gto.M(
    verbose = 5,
    output = '/dev/null',
    atom = '''C 0 0 0
    H  1  1  1
    H -1 -1  1
    H -1  1 -1
    H  1 -1 -1''',
    basis = '6-31g',
    charge = 1,
    spin = 1,
    symmetry = 1,)

def tearDownModule():
    global h2o_z0, h2o_z1, h2o_z0_s, h2o_z1_s, h4_z0_s, h4_z1_s
    h2o_z0.stdout.close()
    h2o_z1.stdout.close()
    h2o_z0_s.stdout.close()
    h2o_z1_s.stdout.close()
    h4_z0_s.stdout.close()
    h4_z1_s.stdout.close()
    del h2o_z0, h2o_z1, h2o_z0_s, h2o_z1_s, h4_z0_s, h4_z1_s

class KnowValues(unittest.TestCase):
    def test_nr_rhf(self):
        mf = scf.RHF(h2o_z0)
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), -75.98394849812, 9)

    def test_nr_rohf(self):
        mf = scf.RHF(h2o_z1)
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), -75.5783963795897, 9)


    def test_nr_uhf(self):
        mf = scf.UHF(h2o_z1)
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), -75.58051984397145, 9)

    def test_nr_uhf_cart(self):
        mol = h2o_z1.copy()
        mol.cart = True
        mf = scf.newton(scf.UHF(mol))
        mf.kernel()
        self.assertAlmostEqual(mf.e_tot, -75.58051984397145, 9)


    def test_nr_rhf_symm(self):
        mf = scf.RHF(h2o_z0_s)
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), -75.98394849812, 9)

    def test_nr_rohf_symm(self):
        mf = scf.RHF(h2o_z1_s)
        mf.irrep_nelec['B2'] = (1,0)
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), -75.578396379589819, 9)


    def test_nr_uhf_symm(self):
        mf = scf.UHF(h2o_z1_s)
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), -75.58051984397145, 9)


    def test_nr_rks_lda(self):
        mf = dft.RKS(h2o_z0)
        eref = mf.kernel()
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 3
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)

    def test_nr_rks_rsh(self):
        '''test range-separated Coulomb'''
        mf = dft.RKS(h2o_z0)
        mf.xc = 'wb97x'
        eref = mf.kernel()
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 3
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)

    def test_nr_rks(self):
        mf = dft.RKS(h2o_z0)
        mf.xc = 'b3lyp'
        eref = mf.kernel()
        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 3
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)

    def test_rks_gen_g_hop(self):
        mf = dft.RKS(h2o_z0)
        mf.grids.build()
        mf.xc = 'b3lyp'
        nao = h2o_z0.nao_nr()
        numpy.random.seed(1)
        mo = numpy.random.random((nao,nao))
        mo_occ = numpy.zeros(nao)
        mo_occ[:5] = 2
        nocc, nvir = 5, nao-5
        dm1 = numpy.random.random(nvir*nocc)
        nr = scf.newton(mf)
        g, hop, hdiag = nr.gen_g_hop(mo, mo_occ, mf.get_hcore())
        self.assertAlmostEqual(numpy.linalg.norm(hop(dm1)), 40669.392804071264, 7)

    def test_nr_roks(self):
        mf = dft.RKS(h2o_z1)
        mf.xc = 'b3lyp'
        eref = mf.kernel()

        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 3
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)


    def test_nr_uks_lda(self):
        mf = dft.UKS(h2o_z1)
        eref = mf.kernel()

        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 2
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)

    def test_nr_uks_rsh(self):
        '''test range-separated Coulomb'''
        mf = dft.UKS(h2o_z1)
        mf.xc = 'wb97x'
        eref = mf.kernel()

        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 3
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)

    def test_nr_uks(self):
        mf = dft.UKS(h2o_z1)
        mf.xc = 'b3lyp'
        eref = mf.kernel()

        mf.max_cycle = 1
        mf.conv_check = False
        mf.kernel()
        nr = scf.newton(mf)
        nr.max_cycle = 3
        nr.conv_tol_grad = 1e-5
        self.assertAlmostEqual(nr.kernel(), eref, 9)

    def test_nr_uks_fast_newton(self):
        mf = dft.UKS(h4_z1_s)
        mf.xc = 'b3lyp'
        mf1 = scf.fast_newton(mf)
        self.assertAlmostEqual(mf1.e_tot, -39.696083841107587, 9)

        mf1 = scf.fast_newton(dft.UKS(h4_z1_s))
        self.assertAlmostEqual(mf1.e_tot, -39.330377813428001, 9)

    def test_nr_rks_fast_newton(self):
        mf = dft.RKS(h4_z0_s)
        mf.xc = 'b3lyp'
        mf1 = scf.fast_newton(mf)
        self.assertAlmostEqual(mf1.e_tot, -40.10277421254213, 9)

    def test_nr_rohf_fast_newton(self):
        mf = scf.ROHF(h4_z1_s)
        mf1 = scf.fast_newton(mf)
        self.assertAlmostEqual(mf1.e_tot, -39.365972147397649, 9)

    def test_uks_gen_g_hop(self):
        mf = dft.UKS(h2o_z0)
        mf.grids.build()
        mf.xc = 'b3p86'
        nao = h2o_z0.nao_nr()
        numpy.random.seed(1)
        mo =(numpy.random.random((nao,nao)),
             numpy.random.random((nao,nao)))
        mo_occ = numpy.zeros((2,nao))
        mo_occ[:,:5] = 1
        nocc, nvir = 5, nao-5
        dm1 = numpy.random.random(nvir*nocc*2)
        nr = scf.newton(mf)
        g, hop, hdiag = nr.gen_g_hop(mo, mo_occ, (mf.get_hcore(),)*2)
        self.assertAlmostEqual(numpy.linalg.norm(hop(dm1)), 33565.97987644776, 7)


if __name__ == "__main__":
    print("Full Tests for Newton solver")
    unittest.main()

