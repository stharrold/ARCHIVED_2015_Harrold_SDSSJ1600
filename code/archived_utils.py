r"""Archived utilities for reproducing Harrold et al 2015 on
SDSS J160036.83+272117.8. Code here is no longer used.

"""


# ARCHIVED
# print("`dataframes.balanced.all_data`: In order to refine the period, weight each\n" +
#       "dataset by phase coverage by drawing random samples without replacement.")
# # NOTE: This is done after estimating the period from the CRTS-only data.
# # Necessary for finding the period since the McDonald data only samples
# # the primary eclipse.
# dataframes.balanced = code.utils.Container()
# dataframes.balanced.all_data = dataframes.all_data.copy()
# collections_phasecovers = dict(crts=1.0, mcd=0.1)
# collection_min_phasecover = min(
#     collections_phasecovers,
#     key=lambda coll: collections_phasecovers[coll])
# min_phasecover = collections_phasecovers[collection_min_phasecover]
# collections_tfmasks = dict()
# for collection in dataframes.all_data['collection'].unique():
#     collections_tfmasks[collection] = \
#         (dataframes.all_data['collection'] == collection)
# collection_min_phasecover_num = np.count_nonzero(
#     collections_tfmasks[collection_min_phasecover])
# for (collection, phasecover) in sorted(collections_phasecovers.items()):
#     balanced_collection_num = int(
#         (phasecover / min_phasecover) * collection_min_phasecover_num)
#     tfmask_collection = collections_tfmasks[collection]
#     num_appends = int(
#         balanced_collection_num / np.count_nonzero(tfmask_collection)) - 1
#     for _ in range(num_appends):
#         df_to_append = dataframes.all_data.loc[tfmask_collection].copy()
#         dataframes.balanced.all_data = dataframes.balanced.all_data.append(
#             df_to_append, ignore_index=True)
# print()
# print(("`dataframes.balanced.all_data`: Number of observations.\n" +
#        "Total: {num}").format(num=len(dataframes.balanced.all_data)))
# for collection in sorted(dataframes.balanced.all_data['collection'].unique()):
#     print(("{col}: {num}").format(
#         col=collection,
#         num=np.count_nonzero(
#                 dataframes.balanced.all_data['collection'] == collection)))


# ARCHIVED
# print("`dataframes.subsample.all_data`: For computational limits, reduce the number\n" +
#       "of datapoints by drawing random samples without replacement from"
#       "the balanced dataset.")
# rand_idxs = np.random.choice(len(dataframes.balanced.all_data), size=int(1e4), replace=False)
# dataframes.subsample = code.utils.Container()
# dataframes.subsample.all_data = dataframes.balanced.all_data.iloc[rand_idxs].copy()
# print()
# print(("`dataframes.subsample.all_data`: Number of observations.\n" +
#        "Total: {num}").format(num=len(dataframes.subsample.all_data)))
# for collection in sorted(dataframes.subsample.all_data['collection'].unique()):
#     print(("{col}: {num}").format(
#         col=collection,
#         num=np.count_nonzero(
#                 dataframes.subsample.all_data['collection'] == collection)))


# ARCHIVED
# print("`dataframes.subsample`: In order to refine the period, weight each\n" +
#       "dataset by phase coverage by drawing random samples without replacement.")
# # NOTE: Necessary for finding the period since the McDonald data only samples
# # the primary eclipse.
# dataframes.subsample = pd.DataFrame(columns=dataframes.crts.all_data.columns)
# collections_tfmasks = dict()
# min_obs = len(dataframes.crts.all_data)
# for collection in dataframes.crts.all_data['collection'].unique():
#     tfmask_collection = (dataframes.crts.all_data['collection'] == collection)
#     collections_tfmasks[collection] = tfmask_collection
#     min_obs = min(
#         min_obs, np.count_nonzero(tfmask_collection))
# for (collection, tfmask) in collections_tfmasks.items():
#     num_obs = np.count_nonzero(tfmask)
#     rand_idxs = np.random.choice(num_obs, size=min_obs, replace=False)
#     df_to_append = dataframes.crts.all_data.loc[tfmask].iloc[rand_idxs].copy()
#     dataframes.subsample = dataframes.subsample.append(
#         df_to_append, ignore_index=True)
# print()
# print(("`dataframes.subsample`: Number of observations.\n" +
#        "Total: {num}").format(num=len(dataframes.subsample)))
# for collection in sorted(dataframes.subsample['collection'].unique()):
#     print(("{col}: {num}").format(
#         col=collection,
#         num=np.count_nonzero(dataframes.subsample['collection'] == collection)))


def calc_periodogram(
    times, fluxes, fluxes_err, filts, min_period=None, max_period=None,
    num_periods=None, sigs=(95.0, 99.0), num_shuffles=100,
    show_plot=True, period_unit='seconds', flux_unit='relative'):
    r"""Calculate periods, powers, best period, and significance levels
    using multiband generalized Lomb-Scargle periodogram. Convenience function
    for methods from [1]_, [2]_.
       
    Parameters
    ----------
    times : numpy.ndarray
        1D array of time coordinates for data. Unit is time,
        e.g. seconds or days.
    fluxes : numpy.ndarray
        1D array of fluxes. Unit is integrated flux,
        e.g. relative flux or magnitudes.
    fluxes_err : numpy.ndarray
        1D array of errors for fluxes. Unit is same as `fluxes`.
    filts : list
        1D array of string values for filters.
        Example: filts=['u', 'g', 'r', u', 'g', 'r', ...]
    min_period : {None}, float, optional
        Minimum period to sample. Unit is same as `times`.
        If `None` (default), `min_period` defined by `calc_period_limits`.
    max_period : {None}, float, optional
        Maximum period to sample. Unit is same as `times`.
        If `None` (default), `max_period` defined by `calc_period_limits`.
    num_periods : {None}, int, optional
        Number of periods to sample, including `min_period` and `max_period`.
        If `None` (default), `num_periods` defined by `calc_period_limits`,
        or 1e3, whichever is fewer  to limit computation time.
    sigs : {(95.0, 99.0)}, tuple of floats, optional
        Levels of statistical significance for which to compute corresponding
        Lomb-Scargle relative percentile powers via shuffling `times`.
    num_shuffles : {100}, int, optional
        Number of shuffles to compute significance levels.
    show_periodogram : {True, False}, bool, optional
        If `True` (default), display periodogram plot of Lomb-Scargle
        power spectral density vs period with significance levels.
    period_unit : {'seconds'}, string, optional
    flux_unit : {'relative'}, string, optional
        Strings describing period and flux units for labeling the plot
        with `plot_periodogram`.
    
    Returns
    -------
    periods : numpy.ndarray
        1D array of periods. Unit is same as `times`.
    powers  : numpy.ndarray
        1D array of powers. Unit is relative Lomb-Scargle power spectral density
        from flux and angular frequency, e.g. from relative flux,
        angular frequency 2*pi/seconds.
    sigs_powers : list
        Relative powers corresponding to levels of statistical significance.
        Example: 
            [(95.0, [0.051, 0.052, 0.049, ...]),
             (99.0, [0.059, 0.062, 0.061, ...])]
            np.shape(relative_powers) == np.shape(times)

    See Also
    --------
    calc_period_limits, plot_periodogram
    
    Notes
    -----
    - Computing periodogram of 1e3 periods with 100 shuffles
        takes ~85 seconds for a single 2.7 GHz core.
        Computation time is approximately linear with number
        of periods and number of shuffles.

    References
    ----------
    .. [1] Ivezic et al, 2014,
           "Statistics, Data Mining, and Machine Learning in Astronomy'
    .. [2] VanderPlas and Ivezic, 2015
           http://adsabs.harvard.edu/abs/2015arXiv150201344V
    
    """
    # Check input.
    (min_period_limit, max_period_limit, num_periods_limit) = \
        calc_period_limits(times=times)
    if min_period is None:
        min_period = min_period_limit
    if max_period is None:
        max_period = max_period_limit
    if num_periods_limit is None:
        num_periods = num_periods_limit
    # Model time series and find best period.
    model = gatspy_per.LombScargleMultiband(Nterms_base=6, Nterms_band=1)
    model.optimizer.period_range = (min_period, max_period)
    model.fit(t=times, y=fluxes, dy=fluxes_err, filts=filts)
    model.best_period
    # Calculate powers for plot.
    min_omega = 2.0*np.pi / max_period
    max_omega = 2.0*np.pi / min_period
    num_omegas = num_periods
    omegas = \
        np.linspace(
            start=min_omega, stop=max_omega, num=num_omegas, endpoint=True)
    periods = 2.0*np.pi / omegas
    powers = model.periodogram(periods=periods)
    # Model noise in time series and find significance levels.
    np.random.seed(seed=0) # for reproducibility
    noise_model = copy.copy(model)
    shuffled_times = copy.copy(times)
    noise_powers_arr = []
    for _ in xrange(num_shuffles):
        np.random.shuffle(shuffled_times)
        noise_model.fit(t=shuffled_times, y=fluxes, dy=fluxes_err, filts=filts)
        noise_powers_arr.append(noise_model.periodogram(periods=periods))
    # TODO: redo below here
    dists = \
        astroML_ts.lomb_scargle_bootstrap(
            t=times, y=fluxes, dy=fluxes_err, omega=omegas, generalized=True,
            N_bootstraps=num_bootstraps, random_state=0)
    sigs_powers = zip(sigs, np.percentile(dists, sigs))
    if show_periodogram:
        # Plot custom periodogram with delta BIC.
        ax0 = \
            plot_periodogram(
                periods=periods, powers=powers, xscale='log', n_terms=1,
                period_unit=period_unit, flux_unit=flux_unit, return_ax=True)
        xlim = (min(periods), max(periods))
        ax0.set_xlim(xlim)
        for (sig, power) in sigs_powers:
            ax0.plot(xlim, [power, power], color='black', linestyle=':')
        ax0.set_title("Generalized Lomb-Scargle periodogram with\n" +
                      "relative Bayesian Information Criterion")
        ax1 = ax0.twinx()
        ax1.set_ylim(
            tuple(
                astroML_ts.lomb_scargle_BIC(
                    P=ax0.get_ylim(), y=fluxes, dy=fluxes_err, n_harmonics=1)))
        ax1.set_ylabel("delta BIC")
        plt.show()
        for (sig, power) in sigs_powers:
            print(
                ("INFO: At significance = {sig}%, " +
                 "power spectral density = {pwr}").format(
                    sig=sig, pwr=power))
    return (periods, powers, sigs_powers)


def select_sig_periods_powers(
    peak_periods, peak_powers, cutoff_power):
    r"""Select the periods with peak powers above the cutoff power.
           
    Parameters
    ----------
    peak_periods : numpy.ndarray
        1D array of periods. Unit is time, e.g. seconds or days.
    peak_powers  : numpy.ndarray
        1D array of powers. Unit is Lomb-Scargle power spectral density
        from flux and angular frequency, e.g. from relative flux,
        angular frequency 2*pi/seconds.
    cutoff_power : float
        Power corresponding to a level of statistical significance.
        Only periods above this cutoff power level are returned.
    
    Returns
    -------
    sig_periods : numpy.ndarray
        1D array of significant periods. Unit is same as `peak_periods`.
    sig_powers : numpy.ndarray
        1D array of significant powers. Unit is same as `peak_powers`.

    See Also
    --------
    calc_periodogram, astroML.time_series.search_frequencies

    Notes
    -----
    - Call after `astroML.time_series.search_frequencies`.
    - Call before `calc_best_period`.
   
    """
    # Check input.
    peak_periods = np.asarray(peak_periods)
    peak_powers = np.asarray(peak_powers)
    # Select significant periods and powers.
    sig_idxs = np.where(peak_powers > cutoff_power)
    sig_periods = peak_periods[sig_idxs]
    sig_powers = peak_powers[sig_idxs]
    return (sig_periods, sig_powers)


def calc_best_period(
    times, fluxes, fluxes_err, candidate_periods, n_terms=6,
    show_periodograms=False, show_summary_plots=True,
    period_unit='seconds', flux_unit='relative'):
    r"""Calculate the period that best represents the data from a multi-term
    generalized Lomb-Scargle periodogram. Convenience function for methods
    from [1]_.
       
    Parameters
    ----------
    times : numpy.ndarray
        1D array of time coordinates for data. Unit is time,
        e.g. seconds or days.
    fluxes : numpy.ndarray
        1D array of fluxes. Unit is integrated flux,
        e.g. relative flux or magnitudes.
    fluxes_err : numpy.ndarray
        1D array of errors for fluxes. Unit is same as `fluxes`.
    candidate_periods : numpy.ndarray
        1D array of candidate periods. Unit is same as `times`.
    n_terms : {6}, int, optional
        Number of Fourier terms to fit the light curve. To fit eclipses well
        often requires ~6 terms, from section 10.3.3 of [1]_.
    show_periodograms : {False, True}, bool, optional
        If `False` (default), do not display periodograms (power vs period)
        for each candidate period.
    show_summary_plots : {True, False}, bool, optional
        If `True` (default), display summary plots of delta BIC vs period and
        periodogram for best fit period.
    period_unit : {'seconds'}, string, optional
    flux_unit : {'relative'}, string, optional
        Strings describing period and flux units for labeling the plot.
        Example: period_unit='seconds', flux_unit='relative' will label the
        x-axis with "Period (seconds)" and label the y-axis with
        "Lomb-Scargle Power Spectral Density\n" +
        "(from flux in relative, ang. freq. in 2*pi/seconds)".
    
    Returns
    -------
    best_period : float
        Period with the highest relative Bayesian Information Criterion.
        Unit is same as `times`.

    See Also
    --------
    astroML.time_series.search_frequencies, calc_num_terms

    Notes
    -----
    - Ranges around each candidate period are based on the angular frequency
      resolution of the original data. Adopted from [2]_.
        acquisition_time = max(times) - min(times)
        omega_resolution = 2.0 * np.pi / acquisition_time
        num_omegas = 1000 # balance fast computation with medium range
        anti_aliasing = 1.0 / 2.56 # remove digital aliasing
        # ensure sampling precision is higher than data precision
        sampling_precision = 0.1 
        range_omega_halfwidth = \
            ((num_omegas/2.0) * omega_resolution * anti_aliasing *
             sampling_precision)
    - Calculating best period from 100 candidate periods takes ~61 seconds for a single 2.7 GHz core.
      Computation time is approx linear with number of candidate periods.
    - Call after `astroML.time_series.search_frequencies`.
    - Call before `calc_num_terms`.

    References
    ----------
    .. [1] Ivezic et al, 2014,
           "Statistics, Data Mining, and Machine Learning in Astronomy"
    .. [2] http://zone.ni.com/reference/en-XX/help/372416A-01/svtconcepts/
           fft_funda/
    
    """
    # Check input
    # TODO: separate as a function
    # sort to allow combining identical periods
    candidate_periods = sorted(candidate_periods) 
    comp_time = 61 * len(candidate_periods)/100 
    if comp_time > 10.0:
        print("INFO: Estimated computation time: {time:.0f} sec".format(
            time=comp_time))
    # Calculate the multiterm periodograms using a range around each
    # candidate angular frequency based on the angular frequency resolution
    # of the original data.
    acquisition_time = max(times) - min(times)
    omega_resolution = 2.0 * np.pi / acquisition_time
    num_omegas = 1000 # chosen to balance fast computation with medium range
    anti_aliasing = 1.0 / 2.56 # remove digital aliasing
    # ensure sampling precision is higher than data precision
    sampling_precision = 0.1 
    range_omega_halfwidth = \
        ((num_omegas/2.0) * omega_resolution * anti_aliasing *
         sampling_precision)
    max_period = 0.5 * acquisition_time
    min_omega = 2.0 * np.pi / max_period
    median_sampling_period = np.median(np.diff(times))
    min_period = 2.0 * median_sampling_period
    max_omega = 2.0 * np.pi / (min_period)
    periods_bics = []
    for candidate_period in candidate_periods:
        candidate_omega = 2.0 * np.pi / candidate_period
        range_omegas = \
            np.clip(
                np.linspace(
                    start=candidate_omega - range_omega_halfwidth,
                    stop=candidate_omega + range_omega_halfwidth,
                    num=num_omegas, endpoint=True),
                min_omega, max_omega)
        range_periods = 2.0 * np.pi / range_omegas
        range_powers = \
            astroML_ts.multiterm_periodogram(
                t=times, y=fluxes, dy=fluxes_err, omega=range_omegas,
                n_terms=n_terms)
        range_bic_max = \
            max(astroML_ts.lomb_scargle_BIC(
                P=range_powers, y=fluxes, dy=fluxes_err, n_harmonics=n_terms))
        range_omega_best = range_omegas[np.argmax(range_powers)]
        range_period_best = 2.0 * np.pi / range_omega_best
        # Combine identical periods, but only keep the larger delta BIC.
        if len(periods_bics) > 0:
            if np.isclose(last_range_omega_best, range_omega_best,
                          atol=omega_resolution):
                if last_range_bic_max < range_bic_max:
                    periods_bics[-1] = (range_period_best, range_bic_max)
            else:
                periods_bics.append((range_period_best, range_bic_max))
        else:
            periods_bics.append((range_period_best, range_bic_max))
        (last_range_period_best, last_range_bic_max) = periods_bics[-1]
        last_range_omega_best = 2.0 * np.pi / last_range_period_best
        if show_periodograms:
            print(80*'-')
            plot_periodogram(
                periods=range_periods, powers=range_powers, xscale='linear',
                n_terms=n_terms, period_unit=period_unit, flux_unit=flux_unit,
                return_ax=False)
            print("Candidate period: {per} seconds".format(
                per=candidate_period))
            print("Best period within window: {per} seconds".format(
                per=range_period_best))
            print("Relative Bayesian Information Criterion: {bic}".format(
                bic=range_bic_max))
    # Choose the best period from the maximum delta BIC.
    best_idx = np.argmax(zip(*periods_bics)[1])
    (best_period, best_bic) = periods_bics[best_idx]
    if show_summary_plots:
        # Plot delta BICs after all periods have been fit.
        print(80*'-')
        periods_bics_t = zip(*periods_bics)
        fig = plt.figure()
        ax = fig.add_subplot(111, xscale='log')
        ax.plot(
            periods_bics_t[0], periods_bics_t[1], color='black', marker='o')
        ax.set_title("Relative Bayesian Information Criterion vs period")
        ax.set_xlabel("Period (seconds)")
        ax.set_ylabel("delta BIC")
        plt.show()
        best_omega = 2.0 * np.pi / best_period
        range_omegas = \
            np.clip(
                np.linspace(
                    start=best_omega - range_omega_halfwidth,
                    stop=best_omega + range_omega_halfwidth,
                    num=num_omegas, endpoint=True),
                min_omega, max_omega)
        range_periods = 2.0 * np.pi / range_omegas
        range_powers = \
            astroML_ts.multiterm_periodogram(
                t=times, y=fluxes, dy=fluxes_err, omega=range_omegas,
                n_terms=n_terms)
        plot_periodogram(
            periods=range_periods, powers=range_powers, xscale='linear',
            n_terms=n_terms, period_unit=period_unit, flux_unit=flux_unit,
            return_ax=False)
        print("Best period: {per} seconds".format(per=best_period))
        print("Relative Bayesian Information Criterion: {bic}".format(
            bic=best_bic))
    return best_period


def refine_best_period(
    times, fluxes, fluxes_err, best_period, n_terms=6, show_plots=True,
    period_unit='seconds', flux_unit='relative'):
    r"""Refine the best period to a higher precision from a multi-term
    generalized Lomb-Scargle periodogram. Convenience function for methods
    from [1]_.
       
    Parameters
    ----------
    times : numpy.ndarray
        1D array of time coordinates for data. Unit is time,
        e.g. seconds or days.
    fluxes : numpy.ndarray
        1D array of fluxes. Unit is integrated flux,
        e.g. relative flux or magnitudes.
    fluxes_err : numpy.ndarray
        1D array of errors for fluxes. Unit is same as `fluxes`.
    best_period : float
        Period that best represents the data. Unit is same as `times`.
    n_terms : {6}, int, optional
        Number of Fourier terms to fit the light curve. To fit eclipses well
        often requires ~6 terms, from section 10.3.3 of [1]_.
    show_plots : {True, False}, bool, optional
        If `True`, display plots of periodograms and phased light curves.
    period_unit : {'seconds'}, string, optional
    flux_unit : {'relative'}, string, optional
        Strings describing period and flux units for labeling the plot.
        Example: period_unit='seconds', flux_unit='relative' will label a
        periodogram x-axis with "Period (seconds)" and label a periodogram
        y-axis with
        "Lomb-Scargle Power Spectral Density\n
        (from flux in relative, ang. freq. in 2*pi/seconds)".

    Returns
    -------
    refined_period : float
        Refined period. Unit is same as `times`.
    phases : ndarray
        The phase coordinates of the best-fit light curve.
        Unit is decimal orbital phase.
    fits_phased : ndarray
        The relative fluxes for the `phases` of the best-fit light curve.
        Unit is same as `fluxes`.
    times_phased : ndarray
        The phases of the corresponding input `times`.
        Unit is decimal orbital phase.
    mtf : astroML.time_series.MultiTermFit
        Instance of the `astroML.time_series.MultiTermFit` class
        for the best fit model.

    See Also
    --------
    calc_best_period, calc_num_terms

    Notes
    -----
    -  Range around the best period is based on the angular frequency
        resolution of the original data. Adopted from [2]_.
        acquisition_time = max(times) - min(times)
        omega_resolution = 2.0 * np.pi / acquisition_time
        num_omegas = 2000 # chosen to balance fast computation with small range
        anti_aliasing = 1.0 / 2.56 # remove digital aliasing
        # ensure sampling precision very high relative to data precision
        sampling_precision = 0.01 
        range_omega_halfwidth = \
            ((num_omegas/2.0) * omega_resolution * anti_aliasing *
             sampling_precision)
    - Call after `calc_num_terms`.

    References
    ----------
    .. [1] Ivezic et al, 2014,
           "Statistics, Data Mining, and Machine Learning in Astronomy"
    .. [2] http://zone.ni.com/reference/en-XX/help/372416A-01/svtconcepts/
           fft_funda/
    
    """
    # Calculate the multiterm periodogram and choose the best period
    # from the maximal power.
    acquisition_time = max(times) - min(times)
    omega_resolution = 2.0 * np.pi / acquisition_time
    num_omegas = 2000 # chosen to balance fast computation with medium range
    anti_aliasing = 1.0 / 2.56 # remove digital aliasing
    # ensure sampling precision very high relative to data precision
    sampling_precision = 0.01 
    range_omega_halfwidth = \
      ((num_omegas/2.0) * omega_resolution * anti_aliasing *
       sampling_precision)
    max_period = 0.5 * acquisition_time
    min_omega = 2.0 * np.pi / max_period
    median_sampling_period = np.median(np.diff(times))
    min_period = 2.0 * median_sampling_period
    max_omega = 2.0 * np.pi / (min_period)
    best_omega = 2.0 * np.pi / best_period
    range_omegas = \
        np.clip(
            np.linspace(
                start=best_omega - range_omega_halfwidth,
                stop=best_omega + range_omega_halfwidth,
                num=num_omegas, endpoint=True),
            min_omega, max_omega)
    range_periods = 2.0 * np.pi / range_omegas
    range_powers = \
        astroML_ts.multiterm_periodogram(
            t=times, y=fluxes, dy=fluxes_err, omega=range_omegas,
            n_terms=n_terms)
    refined_omega = range_omegas[np.argmax(range_powers)]
    refined_period = 2.0 * np.pi / refined_omega
    mtf = astroML_ts.MultiTermFit(omega=refined_omega, n_terms=n_terms)
    mtf.fit(t=times, y=fluxes, dy=fluxes_err)
    (phases, fits_phased, times_phased) = \
        mtf.predict(Nphase=1000, return_phased_times=True, adjust_offset=True)
    if show_plots:
        plot_periodogram(
            periods=range_periods, powers=range_powers, xscale='linear',
            n_terms=n_terms, period_unit=period_unit, flux_unit=flux_unit,
            return_ax=False)
        plot_phased_light_curve(
            phases=phases, fits_phased=fits_phased, times_phased=times_phased,
            fluxes=fluxes, fluxes_err=fluxes_err, n_terms=n_terms,
            flux_unit=flux_unit, return_ax=False)
        print("Refined period: {per} seconds".format(per=refined_period))
    return (refined_period, phases, fits_phased, times_phased, mtf)


def plot_phased_histogram(
	hist_phases, hist_fluxes, hist_fluxes_err, times_phased, fluxes,
    fluxes_err, flux_unit='relative', return_ax=False):
    r"""Plot a Bayesian blocks histogram for a phased light curve.
    Convenience function for methods from [1]_.

    Parameters
    ----------
    hist_phases : numpy.ndarray
        1D array of the phased times of the right edge of each histogram bin.
        Unit is decimal orbital phase.
    hist_fluxes : numpy.ndarray
        1D array of the median fluxes corresponding to the histogram bins
        with right edges of `hist_phases`. Unit is integrated flux,
        e.g. relative flux or magnitudes.
    hist_fluxes_err : np.ndarray
        1D array of the rank-based standard deviation of the binned fluxes
        (sigmaG from section 4.7.4 of [1]_). Unit is same as `hist_fluxes`.
    times_phased : ndarray
        The phases of the time coordinates for the observed data.
        Unit is same as `hist_phases`.
    fluxes : numpy.ndarray
        1D array of fluxes corresponding to `times_phased`.
        Unit is same as `hist_fluxes`.
    fluxes_err : numpy.ndarray
        1D array of errors for fluxes. Unit is same as `hist_fluxes_err`.
    flux_unit : {'relative'}, string, optional
        String describing flux units for labeling the plot.
        Example: flux_unit='relative' will label the y-axis
        with "Flux (relative)".
    return_ax : {False, True}, bool
        If `False` (default), show the periodogram plot. Return `None`.
        If `True`, return a `matplotlib.axes` instance for
        additional modification.

    Returns
    -------
    ax : matplotlib.axes
        Returned only if `return_ax` is `True`. Otherwise returns `None`.
    
    See Also
    --------
    plot_phased_light_curve, calc_phased_histogram
    
    Notes
    -----
    - The phased light curve is plotted through two complete cycles to
      illustrate the deepest minimum.

    References
    ----------
    .. [1] Ivezic et al, 2014, "Statistics, Data Mining, and Machine Learning in Astronomy"
    
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.errorbar(
        x=np.append(times_phased, np.add(times_phased, 1.0)),
        y=np.append(fluxes, fluxes),
        yerr=np.append(fluxes_err, fluxes_err),
        fmt='.k', ecolor='gray')
    plt_hist_phases = np.append(hist_phases, np.add(hist_phases, 1.0))
    plt_hist_fluxes = np.append(hist_fluxes, hist_fluxes)
    plt_hist_fluxes_upr = \
      np.add(plt_hist_fluxes, np.append(hist_fluxes_err, hist_fluxes_err))
    plt_hist_fluxes_lwr = \
        np.subtract(
            plt_hist_fluxes, np.append(hist_fluxes_err, hist_fluxes_err))
    ax.step(x=plt_hist_phases, y=plt_hist_fluxes, color='blue', linewidth=2)
    ax.step(x=plt_hist_phases, y=plt_hist_fluxes_upr,
            color='blue', linewidth=3, linestyle=':')
    ax.step(x=plt_hist_phases, y=plt_hist_fluxes_lwr,
            color='blue', linewidth=3, linestyle=':')
    ax.set_title("Phased light curve\n" +
                 "with Bayesian block histogram")
    ax.set_xlabel("Orbital phase (decimal)")
    ax.set_ylabel("Flux ({unit})".format(unit=flux_unit))
    if return_ax:
        return_obj = ax
    else:
        plt.show()
        return_obj = None
    return return_obj


def calc_phased_histogram(
    times_phased, fluxes, fluxes_err, flux_unit='relative', show_plot=True):
    r"""Calcluate a Bayesian blocks histogram for a phased light curve.
    Assumes that phased lightcurve is symmetrical about phase=0.5.
    Convenience function for methods from [1]_.

    Parameters
    ----------
    times_phased : numpy.ndarray
        1D array of the phases of the time coordinates for the observed data.
        Unit is decimal orbital phase.
    fluxes : numpy.ndarray
        1D array of fluxes corresponding to `times_phased`.
        Unit is integrated flux, e.g. relative flux or magnitudes.
    fluxes_err : numpy.ndarray
        1D array of errors for fluxes. Unit is same as `fluxes`.
        Errors are used only for determining bin widths,
        not for determining flux
    flux_unit : {'relative'}, string, optional
        String describing flux units for labeling the plot.
        Example: flux_unit='relative' will label the y-axis
        with "Flux (relative)".
    show_plot : {True, False}, bool, optional
        If `True`, display plot of phased light curve with histogram.

    Returns
    -------
    hist_phases : numpy.ndarray
        1D array of the phased times of the right edge of each
        Bayesian block bin. Unit is same as `times_phased`.
    hist_fluxes : numpy.ndarray
        1D array of the median fluxes corresponding to the Bayesian block bins
        with right edges of `hist_phases`. Unit is same as `fluxes`.
    hist_fluxes_err : np.ndarray
        1D array of the rank-based standard deviation of the binned fluxes
        (sigmaG from section 4.7.4 of [1]_). Unit is same as `fluxes`.
    
    See Also
    --------
    plot_phased_histogram
    
    Notes
    -----
    - The phased light curve is assumed to be symmetrical about phase=0.5
      since the phased lightcurve is folded at phase=0.5. This allows fitting
      unevenly sampled data.
    - Phased times for each bin are defined by the right edge since
      `matplotlib.pyplot.step` constructs plots expecting coordinates for the
      right edges of bins.
    - Because Bayesian blocks have variable bin width, the histogram is
      computed from three complete cycles to prevent the edges of the
      data domain from affecting the computed bin widths.
    - Binned fluxes are combined using the median rather than a weighted
      average. Errors in binned flux are the rank-based standard deviation
      of the binned fluxes (sigmaG from section 4.7.4 of [1]_).

    References
    ----------
    .. [1] Ivezic et al, 2014,
           "Statistics, Data Mining, and Machine Learning in Astronomy"
    
    """
    # Check input.
    times_phased = np.asarray(times_phased)
    fluxes = np.asarray(fluxes)
    fluxes_err = np.asarray(fluxes_err)
    # Fold the phased light curve at phase=0.5 to enforce symmetry to
    # accommodate irregular data sampling.
    tfmask_lt05 = times_phased < 0.5
    tfmask_gt05 = np.logical_not(tfmask_lt05)
    phases_folded = np.append(
        times_phased[tfmask_lt05], np.subtract(1.0, times_phased[tfmask_gt05]))
    phases_mirrored = np.append(phases_folded, np.subtract(1.0, phases_folded))
    fluxes_folded = np.append(fluxes[tfmask_lt05], fluxes[tfmask_gt05])
    fluxes_mirrored = np.append(fluxes_folded, fluxes_folded)
    fluxes_err_folded = np.append(
        fluxes_err[tfmask_lt05], fluxes_err[tfmask_gt05])
    fluxes_err_mirrored = np.append(fluxes_err_folded, fluxes_err_folded)
    # Append the data to itself (tesselate) 2 times for total of 3 cycles
    # to compute histogram without edge effects.
    # Note: astroML.density_estimation.bayesian_blocks requires input times
    # (phases) be unique.
    tess_phases = phases_mirrored
    tess_fluxes = fluxes_mirrored
    tess_fluxes_err = fluxes_err_mirrored
    for begin_phase in xrange(0, 2):
        tess_phases = np.append(
            tess_phases, np.add(phases_mirrored, begin_phase + 1.0))
        tess_fluxes = np.append(tess_fluxes, fluxes_mirrored)
        tess_fluxes_err = np.append(tess_fluxes_err, fluxes_err_mirrored)
    (tess_phases, uniq_idxs) = np.unique(ar=tess_phases, return_index=True)
    tess_fluxes = tess_fluxes[uniq_idxs]
    tess_fluxes_err = tess_fluxes_err[uniq_idxs]
    # Compute edges of Bayesian blocks histogram.
    # Note: number of edges = number of bins + 1
    tess_bin_edges = astroML_dens.bayesian_blocks(
        t=tess_phases, x=tess_fluxes, sigma=tess_fluxes_err,
        fitness='measures')
    # Determine the median flux and sigmaG within each Bayesian block bin.
    tess_bin_fluxes = []
    tess_bin_fluxes_err = []
    for idx_start in xrange(len(tess_bin_edges) - 1):
        bin_phase_start = tess_bin_edges[idx_start]
        bin_phase_end = tess_bin_edges[idx_start + 1]
        tfmask_bin = np.logical_and(
            bin_phase_start <= tess_phases,
            tess_phases <= bin_phase_end)
        if tfmask_bin.any():
            (bin_flux, bin_flux_err) = \
                astroML_stats.median_sigmaG(tess_fluxes[tfmask_bin])
        else:
            (bin_flux, bin_flux_err) = (np.nan, np.nan)
        tess_bin_fluxes.append(bin_flux)
        tess_bin_fluxes_err.append(bin_flux_err)
    tess_bin_fluxes = np.asarray(tess_bin_fluxes)
    tess_bin_fluxes_err = np.asarray(tess_bin_fluxes_err)
    # Fix number of edges = number of bins. Values are for are right edge
    # of each bin.
    tess_bin_edges = tess_bin_edges[1:]
    # Crop 1 complete cycle out of center of of 3-cycle histogram.
    # Plot and return histogram.
    tfmask_hist = np.logical_and(1.0 <= tess_bin_edges, tess_bin_edges <= 2.0)
    hist_phases = np.subtract(tess_bin_edges[tfmask_hist], 1.0)
    hist_fluxes = tess_bin_fluxes[tfmask_hist]
    hist_fluxes_err = tess_bin_fluxes_err[tfmask_hist]
    if show_plot:
        plot_phased_histogram(
            hist_phases=hist_phases, hist_fluxes=hist_fluxes,
            hist_fluxes_err=hist_fluxes_err, times_phased=phases_mirrored,
            fluxes=fluxes_mirrored, fluxes_err=fluxes_err_mirrored,
            flux_unit=flux_unit, return_ax=False)
    return (hist_phases, hist_fluxes, hist_fluxes_err)


@numba.jit(nopython=True)
def calc_ymeans(hash_filts, hash_unique_filts, ymean_by_filt):
    r"""For speeding up 
    gatspy.periodic.lomb_scargle_multiband.LombScargleMultiband

    call with hash_filts = numpy.asarray(map(hash, filts))

    """
    idx_filt = 0
    num_filts = len(hash_filts)
    num_uniqs = len(hash_unique_filts)
    ymeans = np.empty(num_filts)
    while idx_filt < num_filts:
        filt = hash_filts[idx_filt]
        idx_uniq = 0
        while idx_uniq < num_uniqs:
            uniq_filt = hash_unique_filts[idx_uniq]
            if uniq_filt == filt:
                ymean = ymean_by_filt[idx_uniq]
                ymeans[idx_filt] = ymean
                break
            idx_uniq += 1
        idx_filt += 1
    return ymeans



def model_quantities_from_lc_velr_stellar(
    period, phase0, lc_params, velr_b, stellar_b):
    """Calculate physical quantities of a spherical binary system model
    from its light curve parameters, radial velocity of the brighter star,
    and a stellar model of the brighter star modeled from a spectrum.
    The system is assumed to be an eclipsing single-line spectroscopic binary.
    
    Parameters
    ----------
    phase0 : float
    period : float
        TODO: define `period`, `phase0` from `lc_params`
    lc_params : tuple
        Tuple of floats representing the model light curve parameters.
        `lc_params = \
            (phase_orb_int, phase_orb_ext,
             light_oc, light_ref, light_tr)`.
        Units are:
        {phase_orb_int/ext} = phase of external/internal
            events (tangencies) in radians
            int: internal tangencies, end/begin ingress/egress
            ext: external tangencies, begin/end ingress/egress
        {light_oc/ref/tr} = relative flux
            oc:  occulatation event
            ref: between-eclipse reference light level
            tr:  transit event
    velr_b : float
        Semi-amplitude (half peak-to-peak) of radial velocity
        of the brighter star (greater integrated flux).
        Unit is meters/second.
    stellar_b : tuple
        Tuple of floats representing the parameters of a stellar model
        that was fit to the brighter star (greater integrated flux) from
        single-line spectroscopy of the system.
        `stellar_b = (mass_b, radius_b, teff_b)`
        Units are MKS:
        {mass} = stellar mass in kg
        {radius} = stellar radius in meters
        {teff} = stellar effective temperature in Kelvin
    
    Returns
    -------
    quants : tuple
        Tuple of floats representing the physical quantities
        of a spherical binary model from geometric parameters.
        `quants = \
            (# Quantities for the entire binary system
             phase0, period, incl_rad, sep, massfunc,
             # Quantities for the smaller-radius star ('_s')
             velr_s, axis_s, mass_s, radius_s, teff_s,
             # Quantities for the greater-radius star ('_g')
             velr_g, axis_g, mass_g, radius_g, teff_g)`
        Units are MKS:
        {phase0} = time at which phase of orbit is 0 in
            Unixtime Barycentric Coordinate Time
        {period} = period of orbit in seconds
        {incl_rad} = orbital inclination in radians
        {sep} = star-star separation distance in meters
        {massfunc} = mass function of system in kg
            massfunc = (m2 * sin(i))**3 / (m1 + m2)**2
            where star 1 is the brighter star
        {velr} = radial velocity amplitude (half peak-to-peak) in m/s
        {axis} = semimajor axis of star's orbit in meters
        {radius} = stellar radius in meters
        {mass} = stellar mass in kg
        {teff} = stellar effective temperature in Kelvin

    See Also
    --------
    model_geometry_from_light_curve, seg_model_fluxes_rel

    Notes
    -----
    * Eclipse light levels are referred to by transit or occultaton events
      of the smaller-radius star, not by "primary" or "secondary", which can
      depend on context. For an example, see [1]_.
    * Quantities are calculated as follows:
      * The system geometry is modeled from `lc_params`. The relative
        integrated fluxes of the stars determine whether brighter/dimmer
        star ('_b'/'_d') has the smaller/greater radius ('_s'/'_g').
      * `phase0, period, incl_rad`: Defined from `lc_params`.
      * `massfunc`: Calculated from `lc_params`, `velr_b`.
      * `mass_b`, `radius_b`, `teff_b`: Defined from `stellar_b`.
      * `axis_b`: Calculated from `lc_params`, `velr_b`.
      * `mass_d`, `velr_d`, `axis_d`: Calculated from
        `lc_params`, `velr_b`, `stellar_b`
      * `sep`: Calculated from `lc_params`, `velr_b`, `stellar_b`.
      * `radius_d`, `teff_d`: Calculated from
        `lc_params`, `velr_b`, `stellar_b`
      * From `lc_params`, the ratio of radii as determined by light levels may
        be different from that determined by timings if there was no
        self-consistent solution for inclination.

    References
    ----------
    .. [1] https://github.com/ccd-utexas/binstarsolver/wiki/Supported_examples
    .. [2] Budding, 2007, "Introduction to Astronomical Photometry"

    """
    ########################################
    # Check input and define and compute physical quantities.
    # Quantities for:
    #     brighter star: '_b'
    #     dimmer star: '_d'
    #     smaller-radius star: '_s'
    #     greater-radius star: '_g'
    # Brightness is total integrated flux (total luminosity).
    # TODO: Insert check input here.
    # For system:
    #     From light curve:
    #         Define the phase, period, inclination.
    #     From light curve and radial velocity:
    #         Calculate the mass function.
    # TODO: get phase0 and period from lc_params.
    (phase_orb_int, phase_orb_ext,
     light_oc, light_ref, light_tr) = lc_params
    time_begin_ingress = -phase_orb_ext*period / (2.0*np.pi)
    time_end_ingress   = -phase_orb_int*period / (2.0*np.pi)
    time_begin_egress  = -time_end_ingress
    (flux_intg_rel_s, flux_intg_rel_g, radii_ratio_lt,
     incl_rad, radius_sep_s, radius_sep_g) = \
        model_geometry_from_light_curve(params=lc_params, show_plots=False)
    massfunc = \
        bss.utils.calc_mass_function_from_period_velr(
            period=period, velr1=velr_b)
    # For brighter star:
    #     From stellar model:
    #         Define the mass, radius, temperature.
    #     From light curve, radial velocity:
    #         Calculate the semi-major axis.
    (mass_b, radius_b, teff_b) = stellar_b
    axis_b = \
        bss.utils.calc_semimaj_axis_from_period_velr_incl(
            period=period, velr=velr_b, incl=incl_rad)
    # For dimmer star:
    #     From light curve, radial velocity, stellar model:
    #         Calculate the mass.
    #         Calculate the radial velocity.
    #         Calculate the semi-major axis.
    mass_d = \
        bss.utils.calc_mass2_from_period_velr1_incl_mass1(
            period=period, velr1=velr_b, incl=incl_rad, mass1=mass_b)
    velr_d = \
        bss.utils.calc_velr2_from_masses_period_incl_velr1(
            mass1=mass_b, mass2=mass_d, velr1=velr_b,
            period=period, incl=incl_rad)
    axis_d = \
        bss.utils.calc_semimaj_axis_from_period_velr_incl(
            period=period, velr=velr_d, incl=incl_rad)
    # For system:
    #     From light curve, radial velocity, stellar model:
    #         Calculate the star-star separation distance.
    sep = \
        bss.utils.calc_sep_from_semimaj_axes(
            axis_1=axis_b, axis_2=axis_d)
    # Use relative integrated fluxes to determine whether brighter/dimmer star
    # has smaller/greater radius.
    # If smaller-radius star is brighter than the greater-radius star, then the
    # parameters from the radial velocities and the stellar model refer to the
    # smaller-radius star. Otherwise, the parameters refer to the
    # greater-radius star. 
    if flux_intg_rel_s >= flux_intg_rel_g:
        smaller_is_brighter = True
    else:
        smaller_is_brighter = False
    # Assign quantities to respective stars.
    if smaller_is_brighter:
        velr_s = velr_b
        (mass_s, radius_s, teff_s) = (mass_b, radius_b, teff_b)
        axis_s = axis_b
        (mass_g, velr_g, axis_g) = (mass_d, velr_d, axis_d)
    else:
        velr_g = velr_b
        (mass_g, radius_g, teff_g) = (mass_b, radius_b, teff_b)
        axis_g = axis_b
        (mass_s, velr_s, axis_s) = (mass_d, velr_d, axis_d)
    # For dimmer star:
    #     From light curve, radial velocity, stellar model:
    #         Calculate the radius, effective temperature.
    # NOTE: Ratios below are quantities of
    # smaller-radius star / greater-radius star
    radii_ratio_sep = radius_sep_s / radius_sep_g
    flux_rad_ratio = \
        bss.utils.calc_flux_rad_ratio_from_light(
            light_oc=light_oc, light_tr=light_tr, light_ref=light_ref)
    teff_ratio = \
        bss.utils.calc_teff_ratio_from_flux_rad_ratio(
            flux_rad_ratio=flux_rad_ratio)
    if smaller_is_brighter:
        radius_g = radius_s / radii_ratio_sep
        teff_g = teff_s / teff_ratio
    else:
        radius_s = radius_g * radii_ratio_sep
        teff_s = teff_g * teff_ratio
    ########################################
    # Check calculations and return.
    # Check that the masses are calculated consistently.
    assert (mass_d >= massfunc)
    assert np.isclose(
        mass_s / mass_g,
        bss.utils.calc_mass_ratio_from_velrs(
            velr_1=velr_s, velr_2=velr_g))
    assert np.isclose(
        mass_s + mass_g,
        bss.utils.calc_mass_sum_from_period_velrs_incl(
            period=period, velr_1=velr_s, velr_2=velr_g, incl=incl_rad))
    # Check that the semi-major axes are calculated consistently.
    assert np.isclose(sep, axis_s + axis_g)
    # Check that the radii are calculated consistently.
    # There may be a difference if there was no self-consistent solution
    # for inclination.
    assert radius_s <= radius_g
    rtol = 1e-1
    try:
        assert np.isclose(radii_ratio_lt, radii_ratio_sep, rtol=rtol)
    except AssertionError:
        warnings.warn(
            ("\n" +
             "Radii ratios do not agree to within rtol={rtol}.\n" +
             "The solution for inclination from the light curve\n" +
             "may not be self-consistent:\n" +
             "    radii_ratio_lt              = {rrl}\n" +
             "    radius_sep_s / radius_sep_g = {rrs}").format(
                 rtol=rtol,
                 rrl=radii_ratio_lt,
                 rrs=radii_ratio_sep))
    try:
        radius_s_from_velrs_times = \
            bss.utils.calc_radius_from_velrs_times(
                velr_1=velr_s, velr_2=velr_g,
                time_1=time_begin_ingress, time_2=time_end_ingress)
        radius_s_from_radius_sep = \
            bss.utils.calc_radius_from_radius_sep(
                radius_sep=radius_sep_s, sep=sep)
        radius_g_from_velrs_times = \
            bss.utils.calc_radius_from_velrs_times(
                velr_1=velr_s, velr_2=velr_g,
                time_1=time_begin_ingress, time_2=time_begin_egress)
        radius_g_from_radius_sep = \
            bss.utils.calc_radius_from_radius_sep(
                radius_sep=radius_sep_g, sep=sep)
        assert np.isclose(
            radius_s, radius_s_from_velrs_times, rtol=rtol)
        assert np.isclose(
            radius_s, radius_s_from_radius_sep, rtol=rtol)
        assert np.isclose(
            radius_s_from_velrs_times, radius_s_from_radius_sep, rtol=rtol)
        assert np.isclose(
            radius_g, radius_g_from_velrs_times, rtol=rtol)
        assert np.isclose(
            radius_g, radius_g_from_radius_sep, rtol=rtol)
        assert np.isclose(
            radius_g_from_velrs_times, radius_g_from_radius_sep, rtol=rtol)
    except AssertionError:
        warnings.warn(
            ("\n" +
             "Radii computed from the following methods do not agree\n" +
             "to within rtol={rtol}. Units are meters:\n" +
             "    radius_s                  = {rs:.2e}\n" +
             "    radius_s_from_velrs_times = {rs_vt:.2e}\n" +
             "    radius_s_from_radius_sep  = {rs_rs:.2e}\n" +
             "    radius_g                  = {rg:.2e}\n" +
             "    radius_g_from_velrg_times = {rg_vt:.2e}\n" +
             "    radius_g_from_radius_sep  = {rg_rs:.2e}").format(
                 rtol=rtol,
                 rs=radius_s,
                 rs_vt=radius_s_from_velrs_times,
                 rs_rs=radius_s_from_radius_sep,
                 rg=radius_g,
                 rg_vt=radius_g_from_velrs_times,
                 rg_rs=radius_g_from_radius_sep))
    quants = \
        (phase0, period, incl_rad, sep, massfunc,
         velr_s, axis_s, mass_s, radius_s, teff_s,
         velr_g, axis_g, mass_g, radius_g, teff_g)
    return quants
