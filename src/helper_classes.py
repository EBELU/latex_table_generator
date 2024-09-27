# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
===============================================================================

                                 Helper Classes
                    
===============================================================================
-------------------------------------------------------------------------------
"""

import numpy as np
import pandas as pd
from .helper_functions import format_brackets


def remove_spacer(L) -> list:
    """
    Removes multicolumn_spacer and multirow_spacer during formatting.
    """
    return list(L[L != multicolumn_spacer()])

def is_multi(obj):
    return isinstance(obj, (multicolumn, multicolumn_spacer, multirow, multirow_spacer))

class multicolumn_spacer:
    """
    Class for filling space in the data arrays occupied by a multicolumn
    
    Does nothing except be there
    """
    def __init__(self):
        pass
    def __eq__(self, o):
        # Easy type check
        # As it contains nothing all instances are equal
        return isinstance(o, multicolumn_spacer)
    
    
    

class multirow_spacer:
    """
    Same as above
    
    Does nothing except be there but can be formatted into an empty string.
    This beacuse multirow requires the table to be symmetric while multicolumn is not
    """
    def __init__(self):
        pass
    def __str__(self):
        return ""
    def __eq__(self, o):
        return isinstance(o, multirow_spacer)
    
    
    

class cline_obj:
    """
    Keep clines dynamic to shift them when now columns are inserted
    """
    def __init__(self, start = 0, span = 0, string_val = ""):
        self.start = start + 1
        self.stop = start + span
        self.string_val = string_val
    def __str__(self):
        if self.string_val.endswith("hline"):
            return r" \hline"
        if self.string_val:
            return fr" \cline¤[{self.string_val}¤] "
        else:
            return fr" \cline¤[{self.start}-{self.stop}¤] "
    def shift(self, val):
        self.start += val
        self.stop += val
    def covered_indicies(self):
        return set(np.arange(self.start - 1, self.stop))
    
    
    
        
class multicolumn:
    def __init__(self, starting_idx, span, content, clines = False, alignment = "c"):
        self.start_idx = starting_idx
        self.span = span
        self.content = content
        self.alignment = alignment
        self.cline = ""
        if clines:
            if clines == r"hline":
                self.cline = cline_obj(string_val=r"\hline")
            elif isinstance(clines, str):
                self.cline = cline_obj(string_val=clines)
            else:
                self.cline = cline_obj(starting_idx, span)
 
    def shift(self, val):
        self.start_idx += val
        if isinstance(self.cline, cline_obj):
            self.cline.shift(val)
            
    def __str__(self):
        return format_brackets(rf"\multicolumn¤[{self.span}¤]¤[{self.alignment}¤]¤[{self.content}¤]")
    
    
    
    
    
class multirow:
    def __init__(self, starting_idx, span, content):
        self.span = span
        self.content = content
        self.start_idx = starting_idx
        
    def shift(self, val):
        self.start_idx += val
        
    def __str__(self):
        return format_brackets(rf"\multirow¤[{self.span}¤]¤[*¤]¤[{self.content}¤]")