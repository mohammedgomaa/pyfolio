from __future__ import division

import timeseries
import utils
import positions
import plotting
import internals

import numpy as np
import pandas as pd


def create_returns_tear_sheet(df_rets, algo_create_date=None, backtest_days_pct=0.5, cone_std=1.0):
    
    benchmark_rets = utils.get_symbol_rets('SPY')
    benchmark2_rets = utils.get_symbol_rets('IEF')  # 7-10yr Bond ETF.

    # if your directory structure isn't exactly the same as the research server you can manually specify the location
    # of the directory holding the risk factor data
    # risk_factors = load_portfolio_risk_factors(local_risk_factor_path)
    risk_factors = internals.load_portfolio_risk_factors().dropna(axis=0)

    plotting.set_plot_defaults()

    df_cum_rets = timeseries.cum_returns(df_rets, starting_value=1)

    print "Entire data start date: " + str(df_cum_rets.index[0])
    print "Entire data end date: " + str(df_cum_rets.index[-1])

    if algo_create_date is None:
            algo_create_date = df_rets.index[ int(len(df_rets)*backtest_days_pct) ] 

    print '\n'

    plotting.show_perf_stats(df_rets, algo_create_date, benchmark_rets)

    plotting.plot_rolling_returns(
        df_cum_rets, df_rets, benchmark_rets, benchmark2_rets, algo_create_date, cone_std=cone_std)

    plotting.plot_rolling_beta(df_cum_rets, df_rets, benchmark_rets)

    plotting.plot_rolling_sharp(df_cum_rets, df_rets)

    plotting.plot_rolling_risk_factors(
        df_cum_rets, df_rets, risk_factors, legend_loc='best')

    plotting.plot_calendar_returns_info_graphic(df_rets)

    df_weekly = timeseries.aggregate_returns(df_rets, 'weekly')
    df_monthly = timeseries.aggregate_returns(df_rets, 'monthly')

    plotting.plot_return_quantiles(df_rets, df_weekly, df_monthly)

    plotting.show_return_range(df_rets, df_weekly)

    # Get interesting time periods

    plotting.plot_interesting_times(df_rets, benchmark_rets)

    #########################
    # Drawdowns

    plotting.plot_drawdowns(df_rets, top=5)
    print '\nWorst Drawdown Periods'
    drawdown_df = timeseries.gen_drawdown_table(df_rets, top=5)
    drawdown_df['peak date'] = pd.to_datetime(drawdown_df['peak date'],unit='D')
    drawdown_df['valley date'] = pd.to_datetime(drawdown_df['valley date'],unit='D')
    drawdown_df['recovery date'] = pd.to_datetime(drawdown_df['recovery date'],unit='D')
    drawdown_df['net drawdown in %'] = map( utils.round_two_dec_places, drawdown_df['net drawdown in %'] ) 
    print drawdown_df.sort('net drawdown in %', ascending=False)


def create_position_tear_sheet(df_rets, df_pos_val, gross_lev=None):
    df_cum_rets = timeseries.cum_returns(df_rets, starting_value=1)

    plotting.plot_gross_leverage(df_cum_rets, gross_lev)

    df_pos_alloc = positions.get_portfolio_alloc(df_pos_val)

    plotting.plot_exposures(df_cum_rets, df_pos_alloc)

    plotting.show_and_plot_top_positions(df_cum_rets, df_pos_alloc)

    plotting.plot_holdings(df_pos_alloc)


def create_txn_tear_sheet(df_rets, df_pos_val, df_txn):
    df_cum_rets = timeseries.cum_returns(df_rets, starting_value=1)

    plotting.plot_turnover(df_cum_rets, df_txn, df_pos_val)

    plotting.plot_daily_volume(df_cum_rets, df_txn)

    plotting.plot_volume_per_day_hist(df_txn)


def create_full_tear_sheet(df_rets, df_pos=None, df_txn=None,
                           gross_lev=None, fetcher_urls='',
                           algo_create_date=None,
                           backtest_days_pct=0.5, cone_std=1.0):

    create_returns_tear_sheet(df_rets, algo_create_date=algo_create_date, backtest_days_pct=backtest_days_pct, cone_std=cone_std)

    if df_pos is not None:
        create_position_tear_sheet(df_rets, df_pos, gross_lev=gross_lev)

        if df_txn is not None:
            create_txn_tear_sheet(df_rets, df_pos, df_txn)
