#unit tests
import unittest
import flimlib
import numpy as np
import math

samples = 256
a_in = 10.0
tau_in = 2.0
period = 0.04
time = np.linspace(0,(samples-1)*period,samples,dtype=np.float32)
photon_count32 = a_in * np.exp(-time/tau_in)
photon_count64 = np.asarray(photon_count32,dtype=np.float64)
photon_count2d = np.zeros([256,256])

linear_const = 1
photon_count_linear = linear_const * time

class Test3Integral(unittest.TestCase):
    def test_output_margin(self):
        result = flimlib.GCI_triple_integral_fitting_engine(
            period, photon_count32)
        
        # test to an integer precision since the triple integral fit isn't as rigorous
        self.assertAlmostEqual(result.A, a_in, 0)
        self.assertAlmostEqual(result.tau, tau_in, 0)
        self.assertAlmostEqual(result.Z, 0.0, 0)
        self.assertTrue(result.tries>0)
        self.assertAlmostEqual(result.fitted[0], a_in, 0)
        self.assertAlmostEqual(result.residuals[0], 0.0, 0)
        self.assertAlmostEqual(result.residuals[-1], 0.0, 0)


    def test_photon_count(self):
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count64) #passing float 64 should be fine
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count2d) #passing 2d array will fail
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, 5.7) #must be 1d array
        flimlib.GCI_triple_integral_fitting_engine(period, [1,2])

    def test_instr(self):
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, instr=[1,2,3,4,5])
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, instr=["42"])
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, instr=list(range(300))) # no errors??? ask mark/jenu. ok we should actually just check that it's the right length
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, instr=5)
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, instr="foo")
        with self.assertRaises(TypeError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, instr={"foo": "bar"})

    def test_noise_type_input(self):
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='foo')
        with self.assertRaises(TypeError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type={"foo": "bar"})

    def test_unused_noise_types(self):
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GAUSSIAN_FIT')
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_MLE')

    def test_noise_const(self):
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_CONST',sig=2)
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_CONST',sig=[5])
        with self.assertRaises(TypeError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_CONST',sig=[1,2,3,4,5])
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_CONST',sig='foo')
    
    def test_noise_given(self):
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GIVEN',sig=list(range(samples)))
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GIVEN',sig=2)
        with self.assertRaises(TypeError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GIVEN',sig={"foo": "bar"})
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GIVEN',sig='foo')
        with self.assertRaises(ValueError):
            flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GIVEN',sig=[1,2,3,4,5])
        
    def test_noise_const_and_given(self):
        #the result should be the same if noise given is constant
        result_const = flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_CONST',sig=1.0)
        result_noise_given = flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_GIVEN',sig=np.ones(samples))
        self.assertAlmostEqual(result_const.chisq,result_noise_given.chisq)
        self.assertAlmostEqual(result_const.A,result_noise_given.A)
        self.assertAlmostEqual(result_const.Z,result_noise_given.Z)
        self.assertAlmostEqual(result_const.tau,result_noise_given.tau)

    def test_noise_poisson_data(self):
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_POISSON_DATA')
        # this should print a warning
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_POISSON_DATA',sig=2)

    def test_noise_poisson_fit(self):
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_POISSON_FIT')
        # this should print a warning
        flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, noise_type='NOISE_POISSON_FIT',sig=2)
    
    def test_chisq_target(self):
        result = flimlib.GCI_triple_integral_fitting_engine(period, photon_count32, chisq_target=0.0) #impossible target causes it to run more than once and give up
        self.assertTrue(result.tries>1)

class TestGCIPhasor(unittest.TestCase):
    def test_output_margin(self):
        result = flimlib.GCI_Phasor(period, photon_count32)
        self.assertEqual(result.error_code, 0)
        self.assertAlmostEqual(result.fitted[0], a_in, 1)
        self.assertAlmostEqual(result.residuals[0], 0.0, 1)


def dummy_exp_tau(x, param):
    y = param[1]*np.exp(-x / param[2])
    #y = param[0] + param[1]*np.exp(-x / param[2])
    dy_dparam = [1,0,0]
    dy_dparam[1] = np.exp(-x/param[2])
    dy_dparam[2] = param[1]*x*np.exp(-x/param[2])/(param[2]**2)
    return y, dy_dparam

def dummy_exp_tau_predicate(n_param):
    return n_param == 3

# linear fit!
def dummy_linear(x, param):
    y = param[1]*x
    #y = param[0] + param[1]*x
    dy_dparam = [1,0]
    dy_dparam[1] = x
    return y, dy_dparam

def dummy_linear_predicate(n_param):
    return n_param == 2

class TestGCIMarquardt(unittest.TestCase):
    def test_output_margin(self):
        param_in = [0,a_in+1,tau_in+1] # slight offset to detect if the fitting works!
        result = flimlib.GCI_marquardt_fitting_engine(period, photon_count32, param_in)
        self.assertAlmostEqual(0.0,result.param[0],1)
        self.assertAlmostEqual(a_in,result.param[1],1)
        self.assertAlmostEqual(tau_in,result.param[2],1)

    def test_paramfree(self):
        param_in = [0,a_in+1,tau_in+1] # slight offset to detect if the fitting works!
        result = flimlib.GCI_marquardt_fitting_engine(period, photon_count32, 
            param_in, paramfree=[1,0,1])
        # second parameter should have been held fixed!
        self.assertAlmostEqual(a_in+1, result.param[1],1)

    def test_restraintype(self):
        with self.assertRaises(ValueError):
            flimlib.GCI_set_restrain_limits([0,0],[0],[0])
        with self.assertRaises(ValueError):
            flimlib.GCI_set_restrain_limits([[0,0],[0,0]],[0,0],[0,0])
        param_in = [0,a_in+1,tau_in+1]
        flimlib.GCI_set_restrain_limits([0,1,0],[0,0,0],[0,a_in-1,0])
        result = flimlib.GCI_marquardt_fitting_engine(period, photon_count32, param_in, restrain_type='ECF_RESTRAIN_USER')
        self.assertTrue(result.param[1] <= a_in-1)
    
    def test_multiexp_lambda(self):
        lambda_in = 1/tau_in # lambda is the decay rate!
        param_in = [0,a_in+1,lambda_in+1] # slight offset to detect if the fitting works!
        result = flimlib.GCI_marquardt_fitting_engine(period, photon_count32, param_in, fitfunc=flimlib.GCI_multiexp_lambda)

        self.assertAlmostEqual(a_in, result.param[1], 1)
        self.assertAlmostEqual(lambda_in, result.param[2],1)
    
    def test_user_defined_fitfunc(self):
        param_in = [0.0,a_in+1,tau_in+1] # slight offset to detect if the fitting works!
        fitfunc_in = flimlib.FitFunc(dummy_exp_tau, nparam_predicate=dummy_exp_tau_predicate)
        result = flimlib.GCI_marquardt_fitting_engine(period, photon_count32, param_in, fitfunc=fitfunc_in)
        self.assertAlmostEqual(0.0,result.param[0],1)
        self.assertAlmostEqual(a_in,result.param[1],1)
        self.assertAlmostEqual(tau_in,result.param[2],1)

        # linear fit! (did not work with the first param being nonzero)
        param_in = [0, linear_const+1]
        fitfunc_in = flimlib.FitFunc(dummy_linear, nparam_predicate=dummy_linear_predicate)
        result = flimlib.GCI_marquardt_fitting_engine(period, photon_count_linear, param_in, fitfunc=fitfunc_in, noise_type='NOISE_CONST',sig=1.0)
        self.assertAlmostEqual(0.0,result.param[0],1)
        self.assertAlmostEqual(linear_const,result.param[1],1)

    def test_nparam(self):
        with self.assertRaises(TypeError):
            param_in = [a_in+1,tau_in+1] # forgot the first parameter!
            flimlib.GCI_marquardt_fitting_engine(period, photon_count_linear, param_in)

        # any odd number of parameters greater or equal to 3 should work!
        param_in = [0, a_in+1,tau_in+1, 1, 1] # pass 5 parameters
        flimlib.GCI_marquardt_fitting_engine(period, photon_count_linear, param_in)
        

if __name__ == '__main__':
    unittest.main()