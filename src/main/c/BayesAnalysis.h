#ifndef BAYES_ANNALYSIS
#define BAYES_ANNALYSIS

#include "bayes/bayes_Interface.h"

#ifdef __cplusplus
extern "C"
{
#endif

	/*=================================================================================*/
	/*                                                                                 */
	/*                 MAIN FITTING FUNCTIONS                                          */
	/*                                                                                 */
	/*=================================================================================*/

	/**
* The main/convinient entry point for Bayesian parameter estimation. Wraps bayes_DoBayesFitting().
* This is designed to look similar to the entry point to other alogorithms (RLD, LMA), using similar var names and types.
* The Bayes algorithm does not accept the IRF (instr) here as othe alogorithms do, it must be loaded seperately.
*
* \param[in] xincr The time increment inbetween the values in the trans array.
* \param[in] laser_period Laser repetition or modualtion period.
* \param[in] trans The transient (time resolved) signal to be analysed, the 'data'.
* \param[in] ndata The number of data points.
* \param[in] fit_start The index into the trans array marking the start to the data to be used in the fit.
* \param[in] fit_end The index into the trans array marking the end of the data to be used in the fit.
* \param[in,out] param An array of parameters, the order of which must match fitfunc. Provide parameter estimates, these are overridden with the fitted values.
* \param[in] paramfree An array indicating which parameters are free (1), fixed (0)
* \param[in] nparam The number of parameters.
* \param[in] modeltype The fit model type, e.g. FIT_MONOEXP.
* \param[out] fitted An array containing values fitted to the data, the 'fit'. Fit points are coincident in time with the data points.
* \param[out] residuals An array containing the difference between the data and the fit. Can be NULL if not required.
* \param[out] error The estimated error in the parameters
* \param[out] minuslogprob The resulting negated log probability (-log(P)) of the estimate.
* \param[out] nphotons The total number of photons included in the fit.
* \param[out] chisq The resulting raw chi squared value of the fit. To get the reduced chisq, divide by the degrees of freedom (fit_end - fit_start - nparam). Requires residuals array. Can be NULL if not required.
* \return An error code, 0 = success.
*/
	int Bayes_fitting_engine(/* Data in... */
							 float xincr,
							 float *trans,
							 int ndata,
							 int fit_start,
							 int fit_end,
							 float laser_period,
							 float instr[],
							 int ninstr,
							 /* Model... */
							 float param[],
							 int paramfree[],
							 int nparam,
							 /* Data out... */
							 float *fitted,
							 float *residuals,
							 float *error,
							 /* Metadata output */
							 float *minuslogprob,
							 int *nphotons,
							 float *chisq);

#ifdef __cplusplus
}
#endif

#endif /* BAYES_ANNALYSIS */