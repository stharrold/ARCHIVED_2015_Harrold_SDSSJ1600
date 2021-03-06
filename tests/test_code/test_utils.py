#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Pytests for code/utils.py.

Notes
-----
Tests are executed using pytest.

"""


# Import standard packages.
from __future__ import absolute_import, division, print_function
import collections
import copy
import StringIO
import sys
sys.path.insert(0, '.') # Test the code in this repository.
# Import installed packages.
import astroML.time_series as astroML_ts
import binstarsolver as bss
import gatspy.datasets as gatspy_data
import gatspy.periodic as gatspy_per
import matplotlib.pyplot as plt
import numpy as np
# Import local packages.
import code


# TODO: test_Container
# TODO: test_flux_ADU_to_electrons
# TODO: test_flux_intg_to_rate
# TODO: test_flux_rate_to_magC
# TODO: test_extinct_airmass
# TODO: test_composite_flux
# TODO: test_try_color_to_Teff
# TODO: test_rolling_window


def test_calc_period_limits(
    times=xrange(10), ref_min_period=2.0, ref_max_period=4.5,
    ref_num_periods=23):
    r"""Pytest for code/utils.py:
    calc_period_limits
    
    """
    (test_min_period, test_max_period, test_num_periods) = \
        code.utils.calc_period_limits(times=times)
    assert np.isclose(ref_min_period, test_min_period)
    assert np.isclose(ref_max_period, test_max_period)
    assert np.isclose(ref_num_periods, test_num_periods)
    return None


def test_calc_sig_levels_cases():
    r"""Pytest cases for code/utils.py:
    calc_sig_levels

    """
    # Define function for testing cases.
    def test_calc_sig_levels(
        model, sig_periods, ref_sig_powers, sigs=(95.0, 99.0),
        num_shuffles=100):
        r"""Pytest for code/utils.py:
        calc_sig_levels

        """
        test_sig_powers = code.utils.calc_sig_levels(
            model=model, sig_periods=sig_periods, sigs=sigs,
            num_shuffles=num_shuffles)
        for key in ref_sig_powers:
            assert np.all(np.isclose(ref_sig_powers[key], test_sig_powers[key]))
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    model.fit(t=times, y=mags, dy=mags_err, filts=filts)
    (min_period, max_period, _) = code.utils.calc_period_limits(times=times)
    model.optimizer.period_range = (min_period, max_period)
    sigs = (95.0, 99.0)
    num_shuffles = 100
    sig_periods = \
        [1.66051856e+03, 2.99875187e-02, 1.49938947e-02, 9.99595991e-03,
         7.49698121e-03, 5.99759039e-03, 4.99799500e-03, 4.28399755e-03,
         3.74849907e-03, 3.33200001e-03]
    ref_sig_powers = \
        {95.0: \
            [0.25057282, 0.26775067, 0.25570964, 0.27631931, 0.26301363,
             0.26418357, 0.2457524 , 0.24058861, 0.24839262, 0.24550175],
         99.0: \
            [0.32243259, 0.31730944, 0.29074282, 0.33228392, 0.29340864,
             0.29399481, 0.26595011, 0.26355087, 0.29701109, 0.2730018]}
    test_calc_sig_levels(
        model=model, sig_periods=sig_periods, ref_sig_powers=ref_sig_powers,
        sigs=sigs, num_shuffles=num_shuffles)
    # TODO: insert additional test cases here.
    return None


def test_plot_periodogram(
    periods=[1,2,4,8,16], powers=[1,2,4,2,1], xscale='log',
    period_unit='seconds', flux_unit='relative', return_ax=True):
    r"""Pytest for code/utils.py:
    plot_periodogram
    
    """
    ax = \
      code.utils.plot_periodogram(
          periods=periods, powers=powers, xscale=xscale,
          period_unit=period_unit, flux_unit=flux_unit,
          return_ax=return_ax)
    assert isinstance(ax, plt.Axes)
    return None


def test_calc_min_flux_time_cases():
    r"""pytest cases for code/utils.py:
    calc_min_flux_time

    """
    # Define function for testing cases.
    def test_calc_min_flux_time(
        model, filt, ref_min_flux_time, best_period=None,
        lwr_time_bound=None, upr_time_bound=None, tol=0.1, maxiter=10):
        r"""Pytest for code/utils.py:
        calc_min_flux_time

        """
        test_min_flux_time = \
            code.utils.calc_min_flux_time(
                model=model, filt=filt, best_period=best_period,
                lwr_time_bound=lwr_time_bound, upr_time_bound=upr_time_bound,
                tol=tol, maxiter=maxiter)
        assert np.isclose(ref_min_flux_time, test_min_flux_time)
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    fluxes_rel = np.empty_like(mags)
    fluxes_rel_err = np.empty_like(mags_err)
    for filt in np.unique(filts):
        tfmask = (filt == filts)
        fluxes_rel[tfmask] = \
            map(lambda mag_1: \
                    bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=np.median(mags[tfmask])),
                mags[tfmask])
        fluxes_rel_err[tfmask] = \
            map(lambda mag_1, mag_2: \
                    abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=mag_2)),
                np.add(mags[tfmask], mags_err[tfmask]),
                mags[tfmask])
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    best_period = rrlyrae.get_metadata(lcid)['P']
    model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
    min_flux_time_init = \
        code.utils.calc_min_flux_time(
            model=model, filt='z', best_period=best_period, tol=0.1, maxiter=10)
    for (filt, ref_min_flux_time) in \
        zip(['u', 'g', 'r', 'i', 'z'],
            [0.370657590606, 0.366563989108, 0.375194445097, 0.377970590837,
             0.378704402065]):
        time_window_halfwidth = 0.1 * best_period
        test_calc_min_flux_time(
            model=model, filt=filt, ref_min_flux_time=ref_min_flux_time,
            best_period=best_period,
            lwr_time_bound=min_flux_time_init - time_window_halfwidth,
            upr_time_bound=min_flux_time_init + time_window_halfwidth,
            tol=1e-5, maxiter=10)
    # TODO: insert additional test cases here.
    return None


# TODO: test_calc_min_flux_time_opt_cases


def test_calc_phases(
    times=xrange(12), best_period=4, min_flux_time=1,
    ref_phases=[0.75, 0.0, 0.25, 0.5]*3):
    r"""Pytest for code/utils.py:
    calc_phases

    """
    test_phases = \
        code.utils.calc_phases(
            times=times, best_period=best_period, min_flux_time=min_flux_time)
    assert np.all(np.isclose(ref_phases, test_phases))
    return None


def test_calc_next_phase0_time(
    time=5.0, phase=0.5, best_period=10,
    ref_next_phase0_time=10.0):
    r"""Pytest for code/utils.py:
    calc_next_phase0_time

    """
    test_next_phase_time = \
        code.utils.calc_next_phase0_time(
            time=time, phase=phase, best_period=best_period)
    assert np.isclose(ref_next_phase0_time, test_next_phase_time)
    return None


def test_plot_phased_light_curve(
    phases=np.linspace(start=0, stop=1, num=100, endpoint=False),
    fluxes=[1]*100, fluxes_err=[1]*100,
    fit_phases=[1]*100, fit_fluxes=[1]*100,
    flux_unit='relative', return_ax=True):
    r"""pytest for code/utils.py:
    plot_phased_light_curve

    """
    ax = \
        code.utils.plot_phased_light_curve(
            phases=phases, fluxes=fluxes, fluxes_err=fluxes_err,
            fit_phases=fit_phases, fit_fluxes=fit_fluxes,
            flux_unit=flux_unit, return_ax=return_ax)
    assert isinstance(ax, plt.Axes)
    return None


def test_calc_residual_fluxes_cases():
    r"""pytest cases for code/utils.py:
    calc_residual_fluxes

    """
    # Define function for testing cases.
    def test_calc_residual_fluxes(
        phases, fluxes, fit_phases, fit_fluxes,
        ref_residual_fluxes, ref_resampled_fit_fluxes):
        r"""Pytest for code/utils.py:
        calc_flux_residual_fluxes

        """
        (test_residual_fluxes, test_resampled_fit_fluxes) = \
            code.utils.calc_residual_fluxes(
                phases=phases, fluxes=fluxes,
                fit_phases=fit_phases, fit_fluxes=fit_fluxes)
        assert \
            np.all(
                np.isclose(
                    ref_residual_fluxes,
                    test_residual_fluxes))
        assert \
            np.all(
                np.isclose(
                    ref_resampled_fit_fluxes,
                    test_resampled_fit_fluxes))
        return None
    # Test fit to linear function: flux = 1*phase
    # Order of `phases` and `fit_phases` should not matter.
    # `fluxes` and `fit_fluxes` are sampled at different coordinates.
    (start, stop) = (0, 1)
    phases = np.linspace(start=start, stop=stop, num=100, endpoint=False)
    np.random.shuffle(phases)
    fluxes = copy.deepcopy(phases)
    fit_phases = np.linspace(start=start, stop=stop, num=101, endpoint=False)
    np.random.shuffle(fit_phases)
    fit_fluxes = copy.deepcopy(fit_phases)
    ref_residual_fluxes = [0.0]*len(phases)
    ref_resampled_fit_fluxes = fluxes
    test_calc_residual_fluxes(
        phases=phases, fluxes=fluxes,
        fit_phases=fit_phases, fit_fluxes=fit_fluxes,
        ref_residual_fluxes=ref_residual_fluxes,
        ref_resampled_fit_fluxes=ref_resampled_fit_fluxes)
    # TODO: Insert additional test cases here.
    return None


# Seed random number generator for reproducibility.
np.random.seed(0)
def test_calc_z1_z2(
    dist=np.random.normal(loc=0, scale=1, size=1000),
    ref_z1=0.53192162282074262, ref_z2=0.6959521800983498):
    r"""pytest for code/utils.py:
    calc_z1_z2

    """
    (test_z1, test_z2) = code.utils.calc_z1_z2(dist=dist)
    assert np.isclose(ref_z1, test_z1)
    assert np.isclose(ref_z2, test_z2)
    return None


# # TODO: fix test and speedup
# def test_calc_nterms_base_cases():
#     r"""Pytest cases for code/utils.py:
#     calc_nterms_base

#     """
#     # Define function for testing cases.
#     def test_calc_nterms_base(
#         model, ref_model_best, max_nterms_base=20, show_summary_plots=False,
#         show_periodograms=False, period_unit='seconds', flux_unit='relative'):
#         r"""Pytest for code/utils.py:
#         test_calc_nterms_base

#         """
#         test_model_best = code.utils.calc_nterms_base(
#             model=model, max_nterms_base=max_nterms_base,
#             show_summary_plots=show_summary_plots,
#             show_periodograms=show_periodograms,
#             period_unit=period_unit, flux_unit=flux_unit)
#         assert ref_model_best.Nterms_base == test_model_best.Nterms_base
#         return None
#     # Test adapted from
#     # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
#     rrlyrae = gatspy_data.fetch_rrlyrae()
#     lcid = rrlyrae.ids[0]
#     (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
#     fluxes_rel = np.empty_like(mags)
#     fluxes_rel_err = np.empty_like(mags_err)
#     for filt in np.unique(filts):
#         tfmask = (filt == filts)
#         fluxes_rel[tfmask] = \
#             map(lambda mag_1: \
#                     bss.utils.calc_flux_intg_ratio_from_mags(
#                         mag_1=mag_1,
#                         mag_2=np.median(mags[tfmask])),
#                 mags[tfmask])
#         fluxes_rel_err[tfmask] = \
#             map(lambda mag_1, mag_2: \
#                     abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
#                         mag_1=mag_1,
#                         mag_2=mag_2)),
#                 np.add(mags[tfmask], mags_err[tfmask]),
#                 mags[tfmask])
#     model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
#     model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
#     test_calc_nterms_base(
#         model=model, ref_model_best=model, max_nterms_base=20,
#         show_summary_plots=True, show_periodograms=False,
#         period_unit='seconds', flux_unit='relative')
#     # TODO: insert additional test cases here.
#     return None


# TODO: combine test_ls_*_cases below.
def test_ls_are_valid_params_cases():
    r"""Pytest cases for code/utils.py:
    ls_are_valid_params

    """
    # Define function for testing cases.
    def test_ls_are_valid_params(params, model, ref_are_valid):
        r"""Pytest for code/utils.py:
        ls_are_valid_params

        """
        test_are_valid = code.utils.ls_are_valid_params(
            params=params, model=model)
        assert ref_are_valid == test_are_valid
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    fluxes_rel = np.empty_like(mags)
    fluxes_rel_err = np.empty_like(mags_err)
    for filt in np.unique(filts):
        tfmask = (filt == filts)
        fluxes_rel[tfmask] = \
            map(lambda mag_1: \
                    bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=np.median(mags[tfmask])),
                mags[tfmask])
        fluxes_rel_err[tfmask] = \
            map(lambda mag_1, mag_2: \
                    abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=mag_2)),
                np.add(mags[tfmask], mags_err[tfmask]),
                mags[tfmask])
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    best_period = rrlyrae.get_metadata(lcid)['P']
    params = (best_period)
    model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
    test_ls_are_valid_params(params=params, model=model, ref_are_valid=True)
    # TODO: insert additional test cases here.
    return None


def test_ls_model_fluxes_rel_cases():
    r"""Pytest cases for code/utils.py:
    ls_model_fluxes_rel

    """
    # Define function for testing cases.
    def test_ls_model_fluxes_rel(params, model, ref_modeled_fluxes_rel):
        r"""Pytest for code/utils.py:
        ls_model_fluxes_rel

        """
        test_modeled_fluxes_rel = code.utils.ls_model_fluxes_rel(
            params=params, model=model)
        assert np.all(np.isclose(
            ref_modeled_fluxes_rel, test_modeled_fluxes_rel))
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    fluxes_rel = np.empty_like(mags)
    fluxes_rel_err = np.empty_like(mags_err)
    for filt in np.unique(filts):
        tfmask = (filt == filts)
        fluxes_rel[tfmask] = \
            map(lambda mag_1: \
                    bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=np.median(mags[tfmask])),
                mags[tfmask])
        fluxes_rel_err[tfmask] = \
            map(lambda mag_1, mag_2: \
                    abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=mag_2)),
                np.add(mags[tfmask], mags_err[tfmask]),
                mags[tfmask])
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    best_period = rrlyrae.get_metadata(lcid)['P']
    params = (best_period)
    model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
    test_ls_model_fluxes_rel(
        params=params, model=model,
        ref_modeled_fluxes_rel=model.predict(
            t=model.t, filts=model.filts, period=best_period))
    # TODO: insert additional test cases here.
    return None


def test_ls_log_prior_cases():
    r"""Pytest cases for code/utils.py:
    ls_log_prior

    """
    # Define function for testing cases.
    def test_ls_log_prior(params, model, ref_lnp):
        r"""Pytest for code/utils.py:
        ls_log_prior

        """
        test_lnp = code.utils.ls_log_prior(params=params, model=model)
        assert np.isclose(ref_lnp, test_lnp)
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    fluxes_rel = np.empty_like(mags)
    fluxes_rel_err = np.empty_like(mags_err)
    for filt in np.unique(filts):
        tfmask = (filt == filts)
        fluxes_rel[tfmask] = \
            map(lambda mag_1: \
                    bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=np.median(mags[tfmask])),
                mags[tfmask])
        fluxes_rel_err[tfmask] = \
            map(lambda mag_1, mag_2: \
                    abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=mag_2)),
                np.add(mags[tfmask], mags_err[tfmask]),
                mags[tfmask])
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    best_period = rrlyrae.get_metadata(lcid)['P']
    params = (best_period)
    model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
    test_ls_log_prior(params=params, model=model, ref_lnp=0.0)
    # TODO: insert additional test cases here.
    return None


def test_ls_log_likelihood_cases():
    r"""Pytest cases for code/utils.py:
    ls_log_likelihood

    """
    # Define function for testing cases.
    def test_ls_log_likelihood(params, model, ref_lnp):
        r"""Pytest for code/utils.py:
        ls_log_likelihood

        """
        test_lnp = code.utils.ls_log_likelihood(
            params=params, model=model)
        assert np.isclose(ref_lnp, test_lnp)
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    fluxes_rel = np.empty_like(mags)
    fluxes_rel_err = np.empty_like(mags_err)
    for filt in np.unique(filts):
        tfmask = (filt == filts)
        fluxes_rel[tfmask] = \
            map(lambda mag_1: \
                    bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=np.median(mags[tfmask])),
                mags[tfmask])
        fluxes_rel_err[tfmask] = \
            map(lambda mag_1, mag_2: \
                    abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=mag_2)),
                np.add(mags[tfmask], mags_err[tfmask]),
                mags[tfmask])
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    best_period = rrlyrae.get_metadata(lcid)['P']
    params = (best_period)
    model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
    test_ls_log_likelihood(
        params=params, model=model, ref_lnp=-4200.6511888667446)
    # TODO: insert additional test cases here.
    return None


def test_ls_log_posterior_cases():
    r"""Pytest cases for code/utils.py:
    ls_log_posterior

    """
    # Define function for testing cases.
    def test_ls_log_posterior(params, model, ref_lnp):
        r"""Pytest for code/utils.py:
        ls_log_posterior

        """
        test_lnp = code.utils.ls_log_posterior(
            params=params, model=model)
        assert np.isclose(ref_lnp, test_lnp)
        return None
    # Test adapted from
    # https://github.com/astroML/gatspy/blob/master/examples/MultiBand.ipynb
    rrlyrae = gatspy_data.fetch_rrlyrae()
    lcid = rrlyrae.ids[0]
    (times, mags, mags_err, filts) = rrlyrae.get_lightcurve(lcid)
    fluxes_rel = np.empty_like(mags)
    fluxes_rel_err = np.empty_like(mags_err)
    for filt in np.unique(filts):
        tfmask = (filt == filts)
        fluxes_rel[tfmask] = \
            map(lambda mag_1: \
                    bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=np.median(mags[tfmask])),
                mags[tfmask])
        fluxes_rel_err[tfmask] = \
            map(lambda mag_1, mag_2: \
                    abs(1.0 - bss.utils.calc_flux_intg_ratio_from_mags(
                        mag_1=mag_1,
                        mag_2=mag_2)),
                np.add(mags[tfmask], mags_err[tfmask]),
                mags[tfmask])
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    best_period = rrlyrae.get_metadata(lcid)['P']
    params = (best_period)
    model.fit(t=times, y=fluxes_rel, dy=fluxes_rel_err, filts=filts)
    test_ls_log_posterior(
        params=params, model=model, ref_lnp=-4200.6511888667446)
    # TODO: insert additional test cases here.
    return None


def test_seg_are_valid_params(
    params=(0.018, 0.045, 0.535, 1.016, 0.874, 0.061),
    ref_are_valid=True):
    """Pytest for code/utils.py:
    seg_are_valid_params

    """
    test_are_valid = code.utils.seg_are_valid_params(params=params)
    assert ref_are_valid == test_are_valid
    return None


# Cases for test_seg_are_valid_params
test_seg_are_valid_params(
    params=(-0.018, 0.045, 0.535, 1.016, 0.874, 0.061),
    ref_are_valid=False)


def test_seg_model_fluxes_rel(
    params=(0.018, 0.045, 0.535, 1.016, 0.874, 0.061),
    phases=np.asarray([0.0, 0.25, 0.5, 1.0]),
    ref_modeled_fluxes_rel=np.asarray([0.535, 1.016, 0.874, 0.874])):
    """pytest for code/utils.py:
    seg_model_fluxes_rel

    """
    test_modeled_fluxes_rel = \
        code.utils.seg_model_fluxes_rel(params=params, phases=phases)
    assert np.all(np.isclose(ref_modeled_fluxes_rel, test_modeled_fluxes_rel))
    return None


def test_seg_log_prior(
    params=(0.018, 0.045, 0.535, 1.016, 0.874, 0.061), ref_lnp=0.0):
    """Pytest for code/utils.py:
    seg_log_prior

    """
    test_lnp = code.utils.seg_log_prior(params=params)
    assert np.isclose(ref_lnp, test_lnp)
    return None


# Cases for test_seg_log_prior
test_seg_log_prior(
    params=(-0.018, 0.045, 0.535, 1.016, 0.874, 0.061), ref_lnp=-np.inf)


def test_seg_log_likelihood(
    params=(0.018, 0.045, 0.535, 1.016, 0.874, 0.061),
    phases=np.asarray([0.0, 0.25, 0.5, 1.0]),
    fluxes_rel=np.asarray([0.535, 1.016, 0.874, 0.874]),
    ref_lnp=7.511771526416612):
    """pytest for code/utils.py:
    seg_log_likelihood

    """
    test_lnp = code.utils.seg_log_likelihood(
        params=params, phases=phases, fluxes_rel=fluxes_rel)
    assert np.isclose(ref_lnp, test_lnp)
    return None


# Cases for test_seg_log_likelihood
test_seg_log_likelihood(
    params=(-0.018, 0.045, 0.535, 1.016, 0.874, 0.061), ref_lnp=-np.inf)


def test_seg_log_posterior(
    params=(0.018, 0.045, 0.535, 1.016, 0.874, 0.061),
    phases=np.asarray([0.0, 0.25, 0.5, 1.0]),
    fluxes_rel=np.asarray([0.535, 1.016, 0.874, 0.874]),
    ref_lnp=7.511771526416612):
    """Pytest for code/utils.py:
    seg_log_posterior

    """
    test_lnp = code.utils.seg_log_posterior(
        params=params, phases=phases, fluxes_rel=fluxes_rel)
    assert np.isclose(ref_lnp, test_lnp)
    return None


# Cases for test_seg_log_likelihood
test_seg_log_likelihood(
    params=(-0.018, 0.045, 0.535, 1.016, 0.874, 0.061),
    phases=np.asarray([0.0, 0.25, 0.5, 1.0]),
    fluxes_rel=np.asarray([0.535, 1.016, 0.874, 0.874]),
    ref_lnp=-np.inf)


def test_read_quants_gianninas(
    fobj=StringIO.StringIO("Name         SpT    Teff log L/Lo  t_cool \n" +
                           "==========  ===== ======= ====== =========\n" +
                           "J1600+2721  DA6.0   8353. -1.002 1.107 Gyr"),
    dobj=collections.OrderedDict(
        [('Name', 'J1600+2721'), ('SpT', 'DA6.0'), ('Teff', 8353.0),
         ('log L/Lo', -1.002), ('t_cool', 1.107)])):
    r"""Test that parameters from Gianninas are read correctly.
    
    """
    assert dobj == code.utils.read_quants_gianninas(fobj=fobj)
    return None


def test_has_nans(
    obj={'a': None, 'b': {'b1': True, 'b2': [False, 1, np.nan, 'asdf']}},
    found_nan=True):
    r"""Test that nans are found correctly.
    
    """
    assert code.utils.has_nans(obj) == found_nan
    return None


# Cases for test_has_nans
test_has_nans(
    obj={'a': None, 'b': {'b1': True, 'b2': [False, 1, 'nan', ('asdf', 2.0)]}},
    found_nan=False)


def test_model_geometry_from_light_curve(
    params=(3.5/360.0, 12.3/360.0, 0.898, 1.0, 0.739),
    show_plots=False,
    ref_geoms=(0.102, 0.898, 0.539115831462, 88.8888888889,
               0.0749139580237, 0.138957275514)):
    r"""Pytest style test for code/utils.py:
    model_geometry_from_light_curve
    Default test from Budding 2007 in 
    http://nbviewer.ipython.org/github/ccd-utexas/binstarsolver/blob/
    master/examples/20150419T163000_binstarsolver_book_examples.ipynb

    """
    test_geoms = code.utils.model_geometry_from_light_curve(
        params=params, show_plots=show_plots)
    assert np.all(np.isclose(ref_geoms, test_geoms))
    return None


# Cases for test_model_geometry_from_light_curve
# Test from Carroll and Ostlie 2007 in 
# http://nbviewer.ipython.org/github/ccd-utexas/binstarsolver/blob/
# master/examples/20150419T163000_binstarsolver_book_examples.ipynb
test_model_geometry_from_light_curve(
    params=(0.164135455619/(2.0*np.pi), 0.165111260919/(2.0*np.pi),
            0.0478630092323, 1.0, 0.758577575029),
    show_plots=False,
    ref_geoms=(0.952136990768, 0.0478630092323, 2.2458916679, 90.0,
               0.000481306260183, 0.163880773527))


def test_model_quants_from_velrs_lc_geoms(
    velr_s=33.0, velr_g=3.1, period=271209600.0,
    light_oc=0.0478630092323, light_ref=1.0, light_tr=0.758577575029,
    radius_sep_s=0.000481306260183, radius_sep_g=0.163880773527, incl_deg=90.0,
    ref_quants=(
        9.52168297795, 0.894461128231, 1.07833021001, 367.162456742,
        1.31361736091, 13.9836686806, 3.94386308928)):
    r"""Pytest for code/utils.py:
    model_quants_from_velrs_lc_geoms
    Default test is from Carroll and Ostlie 2007 with Budding 2007 from
    http://nbviewer.ipython.org/github/ccd-utexas/binstarsolver/blob/
    master/examples/20150419T163000_binstarsolver_book_examples.ipynb

    """
    test_quants = code.utils.model_quants_from_velrs_lc_geoms(
        velr_s=velr_s, velr_g=velr_g, period=period,
        light_oc=light_oc, light_ref=light_ref, light_tr=light_tr,
        radius_sep_s=radius_sep_s, radius_sep_g=radius_sep_g,
        incl_deg=incl_deg)
    assert np.all(np.isclose(ref_quants, test_quants))
    return None



def test_rv_are_valid_params(
    params=(-100.0, 0.1, 300.0, 20.0), ref_are_valid=True):
    r"""Pytest for code/utils.py:
    rv_are_valid_params

    """
    test_are_valid = code.utils.rv_are_valid_params(params=params)
    assert ref_are_valid == test_are_valid
    return None


# Cases for test_rv_are_valid_params
test_rv_are_valid_params(
    params=(-100.0, -0.1, 300.0, 20.0), ref_are_valid=True)
test_rv_are_valid_params(
    params=(-100.0, -1.1, 300.0, 20.0), ref_are_valid=False)
test_rv_are_valid_params(
    params=(-100.0, 1.1, 300.0, 20.0), ref_are_valid=False)
test_rv_are_valid_params(
    params=(-100.0, 0.1, 300.0, -20.0), ref_are_valid=False)


def test_rv_model_radial_velocities(
    params=(1.0, 0.25, 1.0, 1.0),
    phases=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
    ref_rvels=np.asarray([2.0, 1.0, 0.0, 1.0, 2.0])):
    r"""Pytest for code/utils.py:
    rv_model_radial_velocities

    """
    test_rvels = code.utils.rv_model_radial_velocities(
        params=params, phases=phases)
    assert np.all(np.isclose(ref_rvels, test_rvels))
    return None


def test_rv_log_prior(
    params=(-100.0, 0.1, 300.0, 20.0), ref_lnp=0.0):
    r"""Pytest for code/utils.py:
    rv_log_prior

    """
    test_lnp = code.utils.rv_log_prior(params=params)
    assert np.isclose(ref_lnp, test_lnp)
    return None


# Cases for test_rv_log_prior
test_rv_log_prior(
    params=(-100.0, 1.1, 300.0, 20.0), ref_lnp=-np.inf)


def test_rv_log_likelihood(
    params=(1.0, 0.25, 1.0, 1.0),
    phases=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
    rvels=np.asarray([2.0, 1.0, 0.0, 1.0, 2.0]),
    ref_lnp=-4.594692666023363):
    r"""Pytest for code/utils.py:
    test_rv_log_likelihood

    """
    test_lnp = code.utils.rv_log_likelihood(
        params=params, phases=phases, rvels=rvels)
    assert np.isclose(ref_lnp, test_lnp)
    return None


# Cases for test_rv_log_likelihood
test_rv_log_likelihood(
    params=(1.0, 1.25, 1.0, 1.0),
    phases=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
    rvels=np.asarray([2.0, 1.0, 0.0, 1.0, 2.0]),
    ref_lnp=-np.inf)


def test_rv_log_posterior(
    params=(1.0, 0.25, 1.0, 1.0),
    phases=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
    rvels=np.asarray([2.0, 1.0, 0.0, 1.0, 2.0]),
    ref_lnp=-4.594692666023363):
    r"""Pytest for code/utils.py:
    test_rv_log_posterior

    """
    test_lnp = code.utils.rv_log_posterior(
        params=params, phases=phases, rvels=rvels)
    assert np.isclose(ref_lnp, test_lnp)
    return None


# Cases for test_rv_log_posterior
test_rv_log_posterior(
    params=(1.0, 1.25, 1.0, 1.0),
    phases=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
    rvels=np.asarray([2.0, 1.0, 0.0, 1.0, 2.0]),
    ref_lnp=-np.inf)


def test_calc_corr_sig_level(
    y1=np.repeat([0., 1., 1., 0., 1., 0., 0., 1.], 128),
    y2=np.ones(128), sig=0.99, min_ncorrs=0.99,
    ref_sig_level=0.578125):
    """Pytest for code/utils.py:
    calc_corr_sig_level
    
    """
    np.random.seed(0) # for reproducibility
    test_sig_level = code.utils.calc_corr_sig_level(y1=y1, y2=y2, sig=0.99)
    assert np.isclose(ref_sig_level, test_sig_level)
    return None


def test_align_data_sets(
    x1=[-3,-2,-1,0,1,2,3], y1=[0,0,0,0,0,1,0], x2=[-1,0,1], y2=[0,1,0],
    resample_factor=2, show_plots=False, sig=0.99, min_ncorrs=1e3,
    ref_x1_aligned=[-1,-0.5,0,0.5,1], ref_y1_aligned=[0,0.5,1,0.5,0],
    ref_x1_offset=-2,
    ref_x2_aligned=[-1,-0.5,0,0.5,1], ref_y2_aligned=[0,0.5,1,0.5,0],
    ref_x2_offset=0):
    """Pytest for code/utils.py:
    align_data_sets.
    
    """
    (test_x1_aligned, test_y1_aligned, test_x1_offset,
     test_x2_aligned, test_y2_aligned, test_x2_offset) = \
        code.utils.align_data_sets(
            x1=x1, y1=y1, x2=x2, y2=y2, resample_factor=resample_factor,
            show_plots=show_plots, sig=sig, min_ncorrs=min_ncorrs)
    assert np.all(np.isclose(ref_x1_aligned, test_x1_aligned))
    assert np.all(np.isclose(ref_y1_aligned, test_y1_aligned))
    assert np.isclose(ref_x1_offset, test_x1_offset)
    assert np.all(np.isclose(ref_x2_aligned, test_x2_aligned))
    assert np.all(np.isclose(ref_y2_aligned, test_y2_aligned))
    assert np.isclose(ref_x2_offset, test_x2_offset)
    return None
