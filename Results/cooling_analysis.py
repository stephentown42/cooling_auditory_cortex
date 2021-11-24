"""
Analysis tools used in multiple parts of the project



TO DO:
    - Add binomial test


Created:
    2021-07-20: Stephen Town

"""
from datetime import datetime

import pandas as pd
import numpy as np


# PREPROCESSING:
def filename_to_sessiondate(s):
    """
    Strip datetime from behavioral results file name
    
    Parameters:
    ----------
    s : str
        File name using GoFerret output file name formatting (e.g. )
    
    >>> filename_to_sessiondate('10_3_2021 level9_opto 12_17 BlockWE-127.txt')
    datetime.datetime(2021, 3, 10, 12, 17)

    >>> filename_to_sessiondate('08_07_2014 level23_spatial_Magnum 17_56 log')
    datetime.datetime(2014, 7, 8, 17, 56)

    Returns:
    --------
    session_dt : datetime
        Datetime corresponding to start of session
    """

    [f_date, _, f_time, _] = s.split()
    date_string = f_date + ' ' + f_time[0:5]
    session_dt = datetime.strptime(date_string, '%d_%m_%Y %H_%M')

    return session_dt


def constrain_attenutations_by_control_performance(df, control_limit, min_trials=5):
    """
    For some sessions, performance on control sessions (when cooling wasn't
    performed) was very poor. This creates floor effects in which it becomes
    impossible to observe any potential effects of cooling. 
    
    To raise baseline performance in control data, we identify attenuations 
    in specific paired sessions that the subject discriminated poorly without cooling,
    and then remove data for both cooled and control trials at that specific 
    attenutation.
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe with cooling status ['isCooled'] and 
        listener performance ['Correct']
    control_limit : float
        Minimum performance required at each control attenutation
        
    Notes:
    ------
    Here, paired sessions refers to two test sessions (one with and one without
    cooling) performed on the same day.

    This function has no threshold for the number of trials - it assumes that
    insight from behavior gained by looking at 3 trials is as useful as looking
    at 100 trials. (I.e. it's a dumb way to do this process)

    The process also acts by combination of day and mask, which means that data
    from particular conditions is being removed from particular days; whereas
    it really should be that flagged attenuations on a given day are removed from
    all maks

    
    Returns:
    --------
    df : pandas dataframe
        Subset of input data with potentially fewer rows
    """

    updated_df = []
    control_limit = control_limit * 100
                 
    for (day, mask), mask_data in df.groupby(by=['day', 'Mask']):

        control_df = mask_data[mask_data['isCooled']== False]

        # byAtten = control_df.groupby(by='Atten')                            # Method 3: Take only sound levels at which critical value was exceeded
        
        # nCorrect = byAtten['Correct'].sum().cumsum()
        # nTrials = byAtten['Correct'].count().cumsum()
        
        # pCorrect = nCorrect / nTrials
        # good_attns = pCorrect[pCorrect > control_limit].index.to_list()     

        byAtten = count_correct_trials(control_df, 'Atten')                 # Method 4: Avoid Cumulative sums (what was I thinking?!) and have min requirement for estimating performance

        low_samples = byAtten[byAtten['nTrials'] < min_trials]['Atten'].to_list()
        ok_perform = byAtten[byAtten['pCorrect'] > control_limit]['Atten'].to_list()

        good_attns = list(set(low_samples) | set(ok_perform))

        mask_data = mask_data[mask_data['Atten'].isin(good_attns)]

        if mask_data is not None:
            updated_df.append(mask_data)                
                                
    return pd.concat(updated_df)


def drop_rare_attenuations(df, min_trials):
    """
    Some vowel attenuations were only presented on a very small number
    of trials (e.g. 5 vs. 50 for a reasonable sample size). Drop these
    attenuations with small trial numbers
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing attenuations and some other columns
    min_trials : int
        Minimum number of trials required to be included in analysis
    
    Returns:
    --------
    df : pandas dataframe
        Subset of input dataframe
    """

    grouped_data = df.groupby(by='Atten')
    enough_trials = grouped_data['Atten'].count() > min_trials

    attns_to_keep = enough_trials.index[ enough_trials.values]
    df = df[ df['Atten'].isin( attns_to_keep.to_list())]

    return df


def match_for_atten(df, time_interval='day', condition_interval='originalFile'):
    """
    Drops attenuations that weren't tested in two
    sessions (cooling) or within the same block (opto) on the same day
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing sound levels (column name: Atten) and
        test sessions (column name: originalFile)
    time_interval : str
        Column name denoting window over which samples are considered
        as a pair ('day' or 'block')
    
    Returns:
    --------
    df : pandas dataframe
        Dataframe covering matched attenuations
    """

    if time_interval == 'all':  # Magnum, unpaired

        good_attns = df[df[condition_interval]]['Atten'].unique()           # isCooled is logical (true for cooled)
        df = df[df['Atten'].isin(good_attns)]
    
        return df

    else:                       # Mimi, Robin - paired
        updated_df = []

        for sample, data in df.groupby(time_interval):
                
            byAtten = data.groupby(by='Atten')             # Get attenuations that are tested in both sessions
            sessions = byAtten[condition_interval].unique()

            nSessions = sessions.apply(len)
            Attns = nSessions[nSessions.values == 2]

            data = data[data['Atten'].isin(Attns.index.to_list())]
            updated_df.append(data)

        return pd.concat(updated_df)


def match_sample_sizes(df, levels):
    """
    The results of this matching seem highly dependent on the random state
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe with unequal numbers of trails for several conditions (e.g. 
        mask and SNR)
    levels : str, or list of strings
    
    Returns:
    --------
    ~ : pandas dataframe
        Dataframe containing equal number of trials for each unique combination 
        of values in the columns defined by levels
    """

    g = df.groupby(by=levels)
    n = g['Trial'].count().min()

    matched_df = []

    for ginfo, gdata in g:
        matched_df.append( gdata.sample(n, replace=False, random_state=24, axis=0))

    return pd.concat(matched_df)
    

def temperature_preprocessing(df, warm_threshold, cooled_threshold):
    """
    Drop intermediate temperatures between warm and cooled thresholds 
    Drop trials performed in control (warm) conditions from cooled sessions
    (either before cooling was achieved or after a problem with the loop arose)
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing temperatures from left and right cooling loops
    warm_threshold : float
        Value above which cortical temperatures are considered to be normal
    cooled_threshold : float
        Value below which cortical temperatures are considered to be cooled
    
    Returns:
    --------
    df : pandas dataframe
        Subset of input dataframe 
    """

    df['meanTemp'] = (df['LeftTemperature'] + df['RightTemperature']) / 2       # Get mean temperature between left and right loops
    
    idx = df[(df['meanTemp'] > cooled_threshold) & (df['meanTemp'] < warm_threshold)].index     # Remove intermediate temperatures
    df.drop(idx, inplace=True)

    for session, sData in df.groupby('originalFile'):                           # Remove warm trials from sessions with cooling 
        if any(sData['meanTemp'] < warm_threshold):         
            df.drop(sData[sData['meanTemp'] > cooled_threshold].index, inplace=True)
            
    df['isCooled'] = df['meanTemp'] <= cooled_threshold

    return df


# ANALYSIS:
def count_correct_trials(df, groupvars):
    """
    Gets the number of trials correct and in total for each combination of variables
    to preserve
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing columns for trials and whether the animal was correct
        on those trials, as well as some other columns that may be used for grouping
    groupvars : list of str
        Column names to obtain separate trial counts 

    >>> count_correct_trials( pd.DataFrame(np.array([[1, 6, 0], [2, 5, 1], [3, 6, 1]]), columns=['Trial', 'Condition', 'Correct']), ['Condition'])        
        Condition  nTrials  nCorrect    pCorrect
    0          5        1         1        100.0
    1          6        2         1         50.0

    Returns:
    --------
    results : pandas dataframe
        Dataframe containing number of trials and number of trials correct for each 
        combination of groupvars
    """

    grouped_data = df.groupby(groupvars)
    nTrials  = grouped_data['Trial'].count()
    nCorrect = grouped_data['Correct'].sum()

    results = pd.concat([nTrials, nCorrect], axis=1)    
    results.reset_index(level=groupvars, inplace=True)
    results.rename({'Trial':'nTrials', 'Correct':'nCorrect'}, axis=1, inplace=True)

    results['pCorrect'] = results['nCorrect'] / results['nTrials'] * 100

    return results


def permutation_test(nX, nY, cX, cY, nIterations=10000):
    """
    Runs a permutation test to answer the question, what is the probability 
    of a difference in accuracy (measured as proportion correct) observed
    between two conditions (e.g. cooled and not cooled) occuring randomly.

    Calculation is computed as y-x
    
    Parameters:
    ----------
    nX : int
        Total number of trials in control condition    
    nY : int
        Total number of trials in cooled condition
    pX : int
        Number of correct trials observed in control testing
    pY : int
        Number of correct trials observed in cooled testing
    nIterations : int, optional
        Number of iterations to permute


    >>> result = permutation_test(100, 200, 80, 20)
    >>> result['p_below']
    0.0

    >>> result = permutation_test(100, 200, 20, 160)
    >>> result['p_below']
    1.0
        
    Returns:
    --------
    p_below : float
        Probability of randomly observing a more negative effect 
        of cooling than was found experimentally
    """

    # Ensure inputs are integers
    nIterations = int(nIterations)

    # Create vectors     
    isCooled = np.concatenate((np.zeros(nX), np.ones(nY)))
    isCorrect = np.concatenate((np.ones(cX), np.zeros(nX-cX), np.ones(cY), np.zeros(nY-cY)))

    # Randomly shuffle
    rng = np.random.default_rng(seed=13)
    outcomes = np.zeros((nIterations, 2))

    for i in range(0, nIterations):

        rng.shuffle(isCooled)          # Note that this affects the initial variable

        outcomes[i,0] = isCorrect[isCooled==0].mean()
        outcomes[i,1] = isCorrect[isCooled==1].mean()

    # Get differences between conditions (cooled - control)
    shuffled_difference = np.diff(outcomes, axis=1)     
    observed_diff = (cY / nY) - (cX / nX)

    p_below = np.sum(shuffled_difference < observed_diff) / nIterations         # Tail 1: Cooling impairs performance
    p_above = np.sum(shuffled_difference > observed_diff) / nIterations         # Tail 2: Cooling improves performance  
    
    return dict(
        p_below = p_below, 
        p_above = p_above, 
        observed_delta = observed_diff * 100,                   # proportion to percentage
        perm_values = shuffled_difference * 100                 # proportion to percentage
    )


def round_to_nearest(ser, round_to):
    """
    Round to nearest multiple 

    TO DO: Switch from taking an entire dataframe and using the attenuation value, 
    to loading the attenuation column in the function all. (I.e. be more explicit)
    
    Parameters:
    ----------
    ser : pandas series
        Dataframe containing column to be rounded (Atten)
    round_to: int or float
        Value to round to nearest multiple 

    >>> round_to_nearest(pd.Series([1.2, 6.1, -0.5, 4.5]), 3)        
    0    0.0
    1    6.0
    2   -0.0
    3    6.0
    dtype: float64
    
    Returns:
    --------
    df : pandas dataframe
        Dataframe with attenuation value rounded
    """

    if round_to is not None:            
        ser = np.round(ser / round_to) * round_to

    return ser
    

def main():
    permutation_test(100, 100, 80, 20, nIterations=10000)


if __name__ == '__main__':

    # main()
    import doctest
    doctest.testmod( optionflags= doctest.NORMALIZE_WHITESPACE)
