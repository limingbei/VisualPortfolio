# -*- coding: utf-8 -*-
u"""
Created on 2015-11-9

@author: cheng.li
"""

from functools import wraps
import seaborn as sns
import matplotlib
from matplotlib.ticker import FuncFormatter
import pandas as pd
from VisualPortfolio.Timeseries import aggregateReturns


def plotting_context(func):
    @wraps(func)
    def call_w_context(*args, **kwargs):
        set_context = kwargs.pop('set_context', True)
        if set_context:
            with context():
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return call_w_context


def context(context='notebook', font_scale=1.5, rc=None):
    if rc is None:
        rc = {}

    rc_default = {'lines.linewidth': 1.5,
                  'axes.facecolor': '0.995',
                  'figure.facecolor': '0.97'}

    # Add defaults if they do not exist
    for name, val in rc_default.items():
        rc.setdefault(name, val)

    return sns.plotting_context(context=context, font_scale=font_scale,
                                rc=rc)


def two_dec_places(x, pos):
    return '%.2f' % x


def percentage(x, pos):
    return '%.0f%%' % (x * 100)


def plottingRollingReturn(cumReturns, benchmarkReturns, ax, title='Strategy Cumulative Returns'):

    y_axis_formatter = FuncFormatter(two_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    cumReturns.plot(lw=3,
                    color='forestgreen',
                    alpha=0.6,
                    label='Strategy',
                    ax=ax)

    if benchmarkReturns is not None:
        benchmarkReturns.plot(lw=2,
                              color='gray',
                              alpha=0.6,
                              label=benchmarkReturns.name,
                              ax=ax)

    ax.axhline(0.0, linestyle='--', color='black', lw=2)
    ax.set_ylabel('Cumulative returns')
    ax.set_title(title)
    ax.legend(loc='best')
    return ax


def plottingDrawdownPeriods(cumReturns, drawDownTable, top, ax, title='Top 5 Drawdown Periods'):
    y_axis_formatter = FuncFormatter(two_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    cumReturns.plot(ax=ax)
    lim = ax.get_ylim()

    tmp = drawDownTable.sort_values(by='draw_down')
    topDrawdown = tmp.groupby('recovery').first()
    topDrawdown = topDrawdown.sort_values(by='draw_down')[:top]
    colors = sns.cubehelix_palette(len(topDrawdown))[::-1]
    for i in range(len(colors)):
        recovery = topDrawdown.index[i]
        ax.fill_between((topDrawdown['peak'][i], recovery),
                        lim[0],
                        lim[1],
                        alpha=.4,
                        color=colors[i])

    ax.set_title(title)
    ax.set_ylabel('Cumulative returns')
    ax.legend(['Cumulative returns'], loc='best')
    ax.set_xlabel('')
    return ax


def plottingUnderwater(drawDownSeries, ax, title='Underwater Plot'):
    y_axis_formatter = FuncFormatter(percentage)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    drawDownSeries.plot(ax=ax, kind='area', color='coral', alpha=0.7)
    ax.set_ylabel('Drawdown')
    ax.set_title(title)
    ax.legend(loc='best')
    ax.set_xlabel('')
    return ax


def plottingMonthlyReturnsHeapmap(returns, ax, title='Monthly Returns (%)'):
    monthlyRetTable = aggregateReturns(returns, 'monthly')
    monthlyRetTable = monthlyRetTable.unstack()
    sns.heatmap(monthlyRetTable.fillna(0) * 100.0,
                annot=True,
                fmt=".1f",
                annot_kws={"size": 9},
                alpha=1.0,
                center=0.0,
                cbar=False,
                cmap=matplotlib.cm.RdYlGn_r,
                ax=ax)
    ax.set_ylabel('Year')
    ax.set_xlabel('Month')
    ax.set_title(title)
    return ax


def plottingAnnualReturns(returns, ax, title='Annual Returns'):
    x_axis_formatter = FuncFormatter(percentage)
    ax.xaxis.set_major_formatter(FuncFormatter(x_axis_formatter))
    ax.tick_params(axis='x', which='major', labelsize=10)

    annulaReturns = pd.DataFrame(aggregateReturns(returns, 'yearly'))

    ax.axvline(annulaReturns.values.mean(),
               color='steelblue',
               linestyle='--',
               lw=4,
               alpha=0.7)

    annulaReturns.sort_index(ascending=False).plot(
        ax=ax,
        kind='barh',
        alpha=0.7
    )

    ax.axvline(0.0, color='black', linestyle='-', lw=3)

    ax.set_ylabel('Year')
    ax.set_xlabel('Returns')
    ax.set_title(title)
    ax.legend(['mean'], loc='best')
    return ax


def plottingMonthlyRetDist(returns, ax, title="Distribution of Monthly Returns"):
    x_axis_formatter = FuncFormatter(percentage)
    ax.xaxis.set_major_formatter(FuncFormatter(x_axis_formatter))
    ax.tick_params(axis='x', which='major', labelsize=10)

    monthlyRetTable = aggregateReturns(returns, 'monthly')

    ax.hist(
        monthlyRetTable,
        color='orange',
        alpha=0.8,
        bins=20
    )

    ax.axvline(
        monthlyRetTable.mean(),
        color='steelblue',
        linestyle='--',
        lw=4,
        alpha=1.0
    )

    ax.axvline(0.0, color='black', linestyle='-', lw=3, alpha=0.75)
    ax.legend(['mean'], loc='best')
    ax.set_ylabel('Number of months')
    ax.set_xlabel('Returns')
    ax.set_title(title)
    return ax


def plottingExposure(positions, ax, title="Total non cash exposure (%)"):
    y_axis_formatter = FuncFormatter(two_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    positions_without_cash = positions.drop('cash', axis='columns')
    total_security_position = positions_without_cash.sum(axis=1) * 100.
    total_security_position.plot(kind='area', color='lightblue', alpha=1.0, ax=ax)
    ax.set_title(title)


def plottingTop5Exposure(positions, ax, top=10, title="Top 10 securities exposure (%)"):
    y_axis_formatter = FuncFormatter(two_dec_places)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    positions_without_cash = positions.drop('cash', axis='columns')
    df_max = positions_without_cash.mean()
    df_top = df_max.nlargest(top)
    (positions[df_top.index] * 100.).plot(ax=ax)
    ax.legend(loc='upper center', frameon=True, bbox_to_anchor=(0.5, -0.14), ncol=5)
    ax.set_title(title)
    return ax
