# -*- coding: utf-8 -*-

"""
-------------------------------------------------------------------------------
===============================================================================

                                Formatter functions
                    
===============================================================================
-------------------------------------------------------------------------------
"""
import numpy as np
import pandas as pd

def make_table_row(L: list, linebreak: str) -> str:
    "Writes a table row from a list/array"
    return ("{} " + r"& {} " * (len(L) - 1) +  linebreak).format(*L)

def format_brackets(string):
    """As {} is used by the python string formatter '¤[' and '¤]' are used insted. 
    This function replaces '¤[' and '¤]' with {} for use in Latex"""
    return string.replace("¤]", "}").replace("¤[", "{")

def latex_formatter(macros:list, targets:list) -> list:  
    """Apply a list of string representing latex macros to a list of text strings.

    Args:
        macros (list/str): A string or list of strings representing latex macros without closed '{}'. Backslash '\' is optional.
        targets (list): A list of text strings.

    Returns:
        list: List of text strings now given to the macros as arguments.
    """    
    @np.vectorize
    def apply_formatter(obj, formatter):
        if obj:
            return fr"{formatter}¤[{obj}¤]"
        else:
            return ""
    # Vectorize function to avoid loops
    vec_format_brackets = np.vectorize(format_brackets)
    apply_formatter
    backslash = "\string"[0] # Define a single backslash cos strings are dumb
    
    # Case if only one string is given
    if isinstance(macros, str):
        macros = [macros]
        
    for form in macros:
        # Check if a backslash is already there
        if not form.startswith(backslash):
            form = backslash + form
        targets = apply_formatter(targets, form)
    return vec_format_brackets(targets)