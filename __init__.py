"""

Put documentation here

"""

__version__ = '0.1.0'

# -----------------------------------------------------------------------------------------------------------
# Analysis configuration - most of this below can be deleted

ferrets = [
    dict(
        fNum=1311,
        rxnTime=True,
        method='cool',              # Cooling below 20°C
        name='Magnum',
        plotrow=1,
        timestep = None,
        attn_round = 3,
        attn_matching = dict(
            time = 'all',
            condition = 'isCooled'
            )
        ),
    dict(
        fNum=1509, 
        rxnTime=True,
        method='cool',
        name='Robin',
        plotrow=2,
        timestep = 'day',
        attn_round = None,
        attn_matching = dict(
            time = 'day',
            condition = 'originalFile'
            )      
        ),
    dict(
        fNum=1706,
        rxnTime=False,
        method='opto',                # mDlx-ChR2 (driving GABAergic inhibitory interneurons via 463 nm light) 
        name='Mimi',
        plotrow=0,
        timestep = 'sessionDate',
        attn_round = None,
        attn_matching = dict(
            time = 'sessionDate',
            condition = 'opto'
            )        
        )
    ]


settings = dict(
    cooled_threshold = 20,           # Temperature below which cortex is considered to be 'cooled'
    warm_threshold = 35,             # Temperature above which cortex is considered to be 'warm'
    control_limit = 0.6,
    noise_level = 70,                # Sound level of noise in dB SPL (two speakers)
    default_level = 60,              # Default sound level of vowels in dB SPL when 0 dB attenuation (two speakers)
    min_trials = 10                  # Min number of trials for each attenuation (across masks)
)
