# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 18:54:15 2021

@author: Colin
"""

# Import libraries
import pandas as pd
import matplotlib.pyplot as plt

# Read raw data
population = pd.read_csv('.\\static\\population.csv')
hosp = pd.read_csv('.\\epidemic\\hospital.csv')
icu = pd.read_csv('.\\epidemic\\icu.csv')
vax = pd.read_csv('..\\citf-public\\vaccination\\vax_state.csv')
cases = pd.read_csv('.\\epidemic\\cases_state.csv')

# Prep data
states = list(population['state'].values)
states = states[1:]
population.set_index('state', inplace=True)
hosp.set_index(pd.to_datetime(hosp['date']), inplace=True)
icu.set_index(pd.to_datetime(icu['date']), inplace=True)
vax.set_index(pd.to_datetime(vax['date']), inplace=True)
cases.set_index(pd.to_datetime(cases['date']), inplace=True)

# Filter for 2021
hosp = hosp.loc["2021"]
icu = icu.loc["2021"]
vax = vax.loc["2021"]
cases = cases.loc["2021"]

# Aggregate 
hosp_rates = {}
icu_rates = {}
vax_rates = {}
cases_state = {}
hosp_ratio = {}

for state in states:
    df_hosp = hosp[hosp['state']==state]
    df_hosp = df_hosp.join(cases[cases['state']==state]['cases_new'])
    hosp_rates[state] = df_hosp['admitted_total']/population.loc[state, 'pop'] * 100000
    hosp_ratio[state] = df_hosp['admitted_total']/df_hosp['cases_new'].shift(3)
    
    df_icu = icu[icu['state']==state]
    icu_rates[state] = (df_icu['icu_covid'] + df_icu['icu_pui'])/df_icu['bed_icu_covid']
    
    # slightly different treatment here as 80% of adults is the target rate
    df_vax = vax[vax['state']==state]
    vax_rates[state] = df_vax['dose2_cumul']/population.loc[state, 'pop_18']/0.8    
    
    cases_state[state] = cases[cases['state']==state]
    
    
df_hosp_rates = pd.DataFrame.from_dict(hosp_rates)
df_icu_rates = pd.DataFrame.from_dict(icu_rates)
df_vax_rates = pd.DataFrame.from_dict(vax_rates)
df_hosp_ratio = pd.DataFrame.from_dict(hosp_ratio)
df_hosp_ratio = df_hosp_ratio.replace([np.inf, -np.inf], np.nan).fillna(0)

# To avoid clutter, only KL + Selangor will be compared vs. the 3 Phase 3 states
# Hosp Rates
fig, ax = plt.subplots()
for state in ['W.P. Kuala Lumpur', 'Selangor', 'Perlis', 'Sarawak', 'W.P. Labuan']:
    ax.plot(df_hosp_rates.index, df_hosp_rates[state].rolling(7).mean(), label=state)
ax.plot(df_hosp_rates.index, [10]*len(df_hosp_rates.index), label="Phase 2 transition?")
ax.plot(df_hosp_rates.index, [3]*len(df_hosp_rates.index), label="Phase 3 transition")
ax.legend()
ax.set_xlabel('Date')
ax.set_ylabel('Daily Admissions per 100,000')
fig.suptitle("Daily Hospitalisation Rates By State - 7 Day MA")

# ICU rates    
fig, ax = plt.subplots()
for state in ['W.P. Kuala Lumpur', 'Selangor', 'Perlis', 'Sarawak', 'W.P. Labuan']:
    ax.plot(df_icu_rates.index, df_icu_rates[state].rolling(7).mean()*100, label=state)
ax.plot(df_icu_rates.index, [100]*len(df_icu_rates.index), label="Phase 2 Transition?")
ax.plot(df_icu_rates.index, [60]*len(df_icu_rates.index), label="Phase 3 Transition?")
ax.legend()
ax.set_xlabel('Date')
ax.set_ylabel('ICU Utilisation (%)')
fig.suptitle("ICU Utilisation Rate By State - 7 Day MA")

# Vax rates    
fig, ax = plt.subplots()
for state in ['W.P. Kuala Lumpur', 'Selangor', 'Perlis', 'Sarawak', 'W.P. Labuan']:
    ax.plot(df_vax_rates.index, df_vax_rates[state].rolling(7).mean()*100, label=state)
ax.plot(df_vax_rates.index, [40]*len(df_vax_rates.index), label="Phase 3 Transition")
ax.legend()
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Vaccination Rate (%)')
fig.suptitle("Cumulative Vaccination Rate By State - 7 Day MA")



fig, axes = plt.subplots(2,1)
for state in ['W.P. Kuala Lumpur', 'Selangor', 'Perlis', 'Sarawak', 'W.P. Labuan']:
    axes[0].plot(df_vax_rates.index, df_vax_rates[state].rolling(7).mean()*100, label=state)
    axes[1].plot(df_hosp_ratio.index, df_hosp_ratio[state].rolling(7).mean(), label=state)
axes[0].legend()
axes[1].legend()
axes[1].set_xlabel('Date')
axes[0].set_ylabel('Cumulative Vaccination Rate (%)')
axes[1].set_ylabel('Admissions/Cases Ratio (3 day lag)')
fig.suptitle("Cumulative Vaccination Rate By State - 7 Day MA")

test = hosp_ratio["Perlis"]
test = test.replace([np.inf, -np.inf], np.nan).fillna(0)

# clusters
clusters = pd.read_csv('.\\epidemic\\clusters.csv')
clusters['date_announced'] = pd.to_datetime(clusters['date_announced'])
test = clusters.groupby(['date_announced', 'state', 'category'])['cases_total'].sum()
test = test.reset_index().set_index('date_announced')
kl = test[test['state']=='WP Kuala Lumpur']
sel = test[test['state']=='Selangor']
