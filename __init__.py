# -*- coding: utf-8 -*-
r"""
    =================
    -----------------
    LaTeX Table Generator
    -----------------
    =================
    
    Provides the *latex_table* class to turn sets of data into latex table. 
    The function *latex_formatter* can be used to apply macros to a list of strings.
    Printing the latex_table object prints the formatted table ready to be copy and pasted.
    
    This module also allows for some formating of the table, like precision in numbers, adding multicolumns
    or multirows and smoothly applies units to column titles (requiers siunitx).
    
    
    @author: Erik Ewald
    
    Class Methods
    -------------------------------------------------
    *latex_table*.info()
        Show info of current content and settings of the table.
    
    *latex_table*.make_multicolumn:
        Makes at multicolumn in the table
        
    *latex_table*.make_multirow:	
        Makes at multirow in the table
        
    *latex_table*.save:	
        Save the table to a file
        
    *latex_table*.set_formatters: 
        Set strings that will encapsulate the corresponding element. Ex \textbf{}.
        
    *latex_table*.set_options:	
        Change settings controlling the formatting and settings of the generated table.
        Ex alignment string, number of decimals
        
    *latex_table*.set_uncertantiy:
        Applies uncertainties to the existing data from a new vector or array by combining each element into \num{value \pm error}
        
    *latex_table*.set_units:
        Sets units at the bottom of each column title. Formatted into \unit{} from siunitx

    
    Special Member Variables
    -------------------------------------------------
    
    latex_table.table_path:
        Lists the path to the directory where the saved tables will be placed.
        It is static and typically only needs to be set one at the start of the script.
    
    Examples
    -------------------------------------------------

    Ex 1. Minimum working example
        samples = ['A', 'B']
        
        data = [1, 2]
        
        column_names = ['Samples', 'Data']
        
        # These are all equiavalent
        
        lt = latex_table(column_names, samples, data)
        
        
        lt = latex_table([samples, data], titles=column_names)
        
        lt = latex_table({'Sample' : ['A', 'B'], 'Data' : [1, 2]})
    
    Ex 2.
        numpy_array_with_data = (np.array([[1332, 1173, 662, 356], [1.00, 1.00, 0.85, 0.62], 
        [5.2711, 5.2711, 30.018, 10.539], [392, 392, 346, 368]]))
        
        isotopes = [r'\atom{Co}{60}', r'\atom{Co}{60}', r'\atom{I}{137}', r'\atom{Ba}{133}']
        
        A_error = [5,7,8,5]
        
        lt = latex_table(['Isotope','Energy', 'I', r'T', 'A'], 
        isotopes, *numpy_array_with_data, caption='A nice table', label='a_nice_label')
        
        lt.set_units(['', r'\kilo\electronvolt', '',  'y','\kilo Bq']) # Add units to the column
        
        lt.set_options(precision = [0,0,2,3,0], alignment = "lcccc") # Set the number of decimals on each column
        
        lt.set_uncertanty(A_error, -1) # Set error for the last column
    
    """

from .src.latex_table import latex_table
from .src.helper_functions import latex_formatter


