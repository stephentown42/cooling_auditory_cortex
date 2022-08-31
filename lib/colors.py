"""
Code to manage colors (mostly these functions are obsolete, but kept for the moment while we check)

"""

######################################
# Color Dictionaries - need to find a way to bring these together and remove redundancy

f_colors = {'F1311':'#c297d3', 'F1509':'#7671b6', 'F1706':'#0e6b96'}
f_markers = {'F1311':'s', 'F1509':'d', 'F1706':'o'}


VOWELS_IN_NOISE = dict(
    Restricted = dict(
        Control = '#920108',
        Bilateral = '#fe969b'
    ),
    Clean = dict(
        Control = '#484848', 
        Bilateral = '#928cc5'
    )
)

VOWELS_SPATIAL = dict(
    separated = dict(
        Control = '#ff8b28',
        Bilateral = '#ffc37a'
    ),
    colocated = dict(
        Control = '#9e0067',
        Bilateral = '#ef8ae2'
    ),
    single_speaker = dict(          # clean
        Control = '#42426e',
        Bilateral = '#928cc5'
    )
)


LOCALIZATION = dict(
    Bilateral='#7e2e8d',
    Control='#808080',
    Left='#4169E1',
    Right='#E0B941'
)


project_colors = dict(
        VOWELS_IN_NOISE = VOWELS_IN_NOISE,
        VOWELS_SPATIAL = VOWELS_SPATIAL,        
        LOCALIZATION = LOCALIZATION       
    )

unmasking_colors = dict(colocated = '#9e0067', separated = '#ff8b28', single_speaker = '#42426e')



init_colors = dict(                             # Old colors taken from the init file, written at an earlier stage - can probably be deleted if not called
    Clean='#484848', 
    Restricted='#920108',
    Noise='#920108',
    Continuous='b',
    colocalized = dict(
        control = 'r',
        cooled = '#ff6666'
        ),
    separated = dict(
        control = 'g',
        cooled = '#1ae61a'
        ),
    single_speaker = dict(
        control = 'k',
        cooled = '.5'
    )
    )



################################################################################
# Functions - I'm pretty sure these are redundant as they're not called by anything else
def change_color_lightness(h, increment):

    rgb = html2rgb(h) 
    
    hls = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)

    new_lightness = hls[1] + increment    

    return colorsys.hls_to_rgb(hls[0], new_lightness, hls[2])
  
  
def change_color_saturation(rgb, delta):
        
    hls = colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])

    new_saturation = hls[2] + delta    

    return colorsys.hls_to_rgb(hls[0], hls[1], new_saturation)
  

def html2rgb(h):
    """
    Converts html color into rgb scale (0-255)
    
    Parameters:
    ----------
    h : str
        html string 
    
    >>> html2rgb('#B4FBB8')
    (180, 251, 184)

    Returns:
    --------
    rgb : tuple
        RBG values for tuple
    """

    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
