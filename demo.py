# -*- coding: utf-8 -*-
"""
Latex Table Generator Demo

@author: Erik Ewald
"""

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import numpy as np
from src.latex_table import latex_table
from src.helper_functions import latex_formatter

def demo1():
    "Minimum working example"
    samples = ['A', 'B']
    data = [1, 2]
    column_names = ['Samples', 'Data']
    
    # These are all equiavalent
    lt = latex_table(column_names, samples, data)    
    lt = latex_table([samples, data], titles=column_names)
    lt = latex_table({'Sample' : ['A', 'B'], 'Data' : [1, 2]})
    
    print(lt)
    
def demo2():
    numpy_array_with_data = (np.array([[1332, 1173, 662, 356], 
                                       [1.00, 1.00, 0.85, 0.62], 
                                       [5.2711, 5.2711, 30.018, 10.539], 
                                       [392, 392, 346, 368]]))
    
    isotopes = [r'\atom{Co}{60}', r'\atom{Co}{60}', r'\atom{I}{137}', r'\atom{Ba}{133}']
    A_error = [5,7,8,5]
    
    lt = latex_table(['Isotope','Energy', 'I', r'T', 'A'], # Titles
    isotopes, *numpy_array_with_data, caption='A nice table', label='a_nice_label')
    
    lt.set_units(['', r'\kilo\electronvolt', '',  'y','\kilo Bq']) # Add units to the column
    
    lt.set_options(alignment = "lcccc") # Set column alignment
    
    lt.set_uncertanty(A_error, -1) # Set error for the last column
    # lt.save("nice_table") # -> nice_table.tex
    print(lt)
    
def demo3():
    # Make some data
    angles = [30, 45, 60, 75]
    compton_E_exp = [561, 464, 400, 335]
    compton_E_theory = np.array([563, 482, 404, 341]).round(-1)
    cross_section_exp = [1, 0.7, 0.6, 0.4]
    cross_section_theory = [1, 0.63, 0.40, 0.28]
    
    # Create table
    lt = latex_table([r"$\theta$", "Experiment", "Theory", "Experiment", "Theory"],
                     angles, compton_E_exp, compton_E_theory,
                     cross_section_exp, cross_section_theory,
                     # Make caption
                     caption = r"The energy of scttered photons at angle $\theta$...",
                     # Make label
                     label = "table_label", 
                     # Change style to grid and spcecify precision
                     style = "grid", precision=[0,0,0,1,2])
    
    # Set units for two columns
    lt.set_units(["", "\kilo\electronvolt", "\kilo\electronvolt", "", ""])
    # Make multicolumns for columns 1-2 and 3-4
    lt.make_multicolumn("title", 1, 1, 2, r"$h\nu ' \pm \sigma$", cline=True)
    lt.make_multicolumn("title", 1, 3, 2, r"$\kn{rel}$", insert=True, cline=True)
    # Put the theta in a multirow for centering
    lt.make_multirow("title", 0, 1, 2, r"$\theta$", insert=True)
    # Specify the first column as angles with siunitx \ang{}
    lt.set_formatters(r"\ang{}", col=0)
    # Uncertanty for the 2nd row is constant at 5
    lt.set_uncertanty(5, 1)
    # Uncertanty for the second row is not constant and is set with an array
    lt.set_uncertanty([40,40,40,30], 2)
    print(lt)

def demo_latex_formatter():
    L = latex_formatter(r"textbf", [1,2,3])
    print(L)


