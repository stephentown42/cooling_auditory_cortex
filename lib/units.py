"""
Code to deal with changes between metric, imperial and normalized units
"""


def inch2cm(inches):
    """
    Designed for use with matplotlib
    
    Parameters:
    ----------
    cm : int, float or list/tuple of ints/floats
        Values in cm that need converting
    
    Returns:
    --------
    y : float or list/tuple of floats
        Values in inches

    >>> cm2inch(2.54)
    1.0

    >>> cm2inch((25.4, 25.4))
    (10.0, 10.0)

    >>> cm2inch([254.0, 254.0])
    [100.0, 100.0]
    """

    if isinstance(inches, float) or isinstance(inches, int):
            return float(inches) * 2.54
    else:
        y = [float(x) * 2.54 for x in inches]

        if isinstance(inches, tuple):
            y = tuple(y)    
        
        return y


def cm2norm(x, fig_size):
    """
    Converts the desired size of an axis in centimeters into the required 
    normalized values, given a set figure size.

    The idea here is usually to generate a canvas big enough to show the axes, 
    and then cut the figure out in the figure design software (e.g. illustrator / gimp)
    
    
    Parameters:
    ----------
    x : list
        4-element vector containing the position of an object (usually axes) required in cm
    fig_size : tuple
        2-element tuple containing figure width and height in inches
    
    Returns:
    --------
    y : list
        4-element vector for position in units normalized for figure shape

    >>> cm2norm([0, 0, 5.08, 5.08], (2, 2))
    [0.0, 0.0, 1.0, 1.0]
    """

    assert len(x) == 4
    assert len(fig_size) == 2
    assert isinstance(fig_size, tuple)

    fig_size = inch2cm(fig_size)

    return [
        x[0] / fig_size[0],
        x[1] / fig_size[1],
        x[2] / fig_size[0], 
        x[3] / fig_size[1]
    ]


def cm2inch(cm):
    """
    Designed for use with matplotlib
    
    Parameters:
    ----------
    cm : int, float or list/tuple of ints/floats
        Values in cm that need converting
    
    Returns:
    --------
    y : float or list/tuple of floats
        Values in inches

    >>> cm2inch(2.54)
    1.0

    >>> cm2inch((25.4, 25.4))
    (10.0, 10.0)

    >>> cm2inch([254.0, 254.0])
    [100.0, 100.0]
    """

    if isinstance(cm, float) or isinstance(cm, int):
            return float(cm) / 2.54
    else:
        y = [float(x) / 2.54 for x in cm]

        if isinstance(cm, tuple):
            y = tuple(y)    
        
        return y


def inch2norm(fig_size, position):
    """ Converts a position in inches into normalized units for a given figure size """

    position[0] = position[0] / fig_size[0]
    position[1] = position[1] / fig_size[1]
    position[2] = position[2] / fig_size[0]
    position[3] = position[3] / fig_size[1]

    return position