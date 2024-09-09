#!/home/eewa/anaconda3/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 10:43:17 2024

@author: Erik Ewald
"""

import numpy as np
import matplotlib.pyplot as plt

import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/"
os.chdir(dir_path)


class latex_table:
    r"""
    =================
    -----------------
    LaTeX Table Saver
    -----------------
    =================
    
    
    Turn python datasets into a latex table.
            
    Constructor 
    -------------------------------------------------
    Arguments
    =========
    *data:
        The constructor provides 3 was of creating a latex-table.
        
        1. latex_table(ndarray, column_titles = list, **kwargs)
        Given a single 2D-numpy array, the columns of the array representing the columns in the table.
        column_titles must given as a keyword argument.
        
        2. latex_table(arr_titles, arr_0, arr_1,..., **kwargs)
        Given an arbitrary number of 1D-arrays representing the columns of the table. 
        If column_titles is empty the first array given is implicitly set as the titels.
        The arrays are not required to be of the same length.
        
        3. latex_table(dict, **kwargs)
        Given a dictionary containing 1D-arrays representing the columns of the table.
        The indices are interpreted as the column titles.
        The arrays are not required to be of the same length.
    
    titles:
        Array like object containing strings och tuples/lists of strings representing the column titles of the tables.
        The array must have the same length as the number of column in the table.
        A tuple/list given as a single title will be expanded into a titles consiting of several rows.
        
    label:
        The label placed into \label{...} of the table.
        'tab:' is added by default.
        
    caption:
        The text placed into \caption{...} of the table
        
        
    -> Returns:
        Class instance of latex_table
        
    Class Methods
    -------------------------------------------------
    
    
    Special Member Variables
    -------------------------------------------------
    latex_table.
    
    """
   
    import numpy as np
    table_path = "" # Static path to the directory where tables are saved
    
    def __init__(self, *data, titles: list = [], label: str = "", caption: str = "", **kwargs) -> "latex_table":  
        import numpy as np
        if len(data) > 1:
            data_lists = list(data[1:])
            self.rows = len(max(data_lists, key = len))
            self.cols = len(data_lists)
            temp_data = np.full((self.cols, self.rows), r"\,", dtype=object)
            for i,L in enumerate(data_lists):
                temp_data[i][:len(L)] = L
            self.data = temp_data.T
            self.titles = data[0]
        elif isinstance(data[0], dict):
            """=== WIP ==="""
            pass
        else:
            if not titles:
                raise ValueError("column_titles must be specified as a keyword")
            self.data = data[0]
            self.titles = list(titles)
            self.rows, self.cols  = self.data.shape
            
        # self.data = pd.DataFrame(data)
        # self.titles = list(column_titles)
        # self.format_options["precision"] = [6] * self.cols
        self.format_options = {"style" : "booktabs",
                               "nan_char" : r"\,",
                               "linebreak" : r"\\",
                               "precision" : [6] * self.cols}
        self.table_options = {"caption" : caption,
                        "label" : f"tab:{label}",
                        "position" : "H",
                        "alignment" : "S" * self.cols,
                        "position_float": r"\centering"}
        self.set_options(**kwargs)
        
    # def inset(self, idx, title, data):
        
    def save(self, buf, abspath = False):
        """
        Saves the table to a file
        
        Use the static class variable *latex_table.table_path* at the beginning of the script 
        to select a common destination that is not the working directory for all tables.
        
        If abspath = False .tex is added automatically
        
        """
        if not abspath:
            buf += ".tex"
        if latex_table.table_path and not abspath:
            buf = latex_table.table_path + buf
        with open(buf, "w") as file:
            file.write(self.__str__())
        file.close()
    
    def __str__(self):
        return self._format_brackets(
r"""\begin¤[table¤][{position}]
    {position_float}
    \caption¤[{caption}¤]
    \label¤[{label}¤]
    \begin¤[tabular¤]¤[{alignment}¤]
        {titles}
        {body}
    \end¤[tabular¤]
\end¤[table¤]""".format(titles = self._make_titles(), 
    body = self._make_table_body(), **self.table_options))
        
    
    # add_uncertanty
    """=== WIP ==="""
    # make_multirow
    """=== WIP ==="""
    # make_multicol
    """=== WIP ==="""
    # formater 
    
    """
    =======
    Setters
    =======
    """
    def set_options(self, **kwargs):
        #"""=== WIP ==="""
        
        """Main setter for all formating and table options
        
        Default table_options:
             'caption': '', 
             'label': 'tab:', 
             'position': 'H', 
             'alignment': 'S...S', 
             'position_float': '\\centering'
             
        Default format_options:
            'style': 'booktabs',
            'nan_char': r'\,', 
            'linebreak': r'\\', 
            'precision': [6, 6,..., 6, 6]
        """
        
        for key in kwargs:
            if key in self.table_options:
                match key:
                    case "alignment":
                        self.set_alignment(kwargs[key])
                    case _:
                        self.table_options[key] = kwargs[key]
            elif key in self.format_options:
                match key:
                    case "style":
                        self.set_lines(kwargs[key])
                    case "precision":
                        self.set_precision(kwargs[key])
                    case _:
                        self.format_options[key] = kwargs[key]
            else:
                raise KeyError(f"Key '{key}' is not viable option")
    
    def add_units(self, unit_array, encapsulation = "$[]$"):
        r"""
        Takes a list of strings compatible with the siunitx function \unit{}.
        The length of the list must match the number of columns, a column without a unit is left as an empty string.
        The units are placed under the column title for each column.
        
        Ex:
            latex_table.set_units([r"\kilo\electronvolt"]) -> [keV]
        """
        half_enc_len = len(encapsulation) // 2
        for i, unit in enumerate(unit_array):
            if unit:
                if not isinstance(self.titles[i], str):
                    # If the title element is already a tuple it is extended. * breaks the old tuple
                    self.titles[i] = (*self.titles[i], encapsulation[:half_enc_len] + 
                                  self._format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                else:
                    self.titles[i] = (self.titles[i], encapsulation[:half_enc_len] + 
                                  self._format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                    
    def set_alignment(self, string):
        if len(string.replace("|", "")) < self.cols:
            raise ValueError("The number of alignment charaters must equal "
                             f"the number of columns. Current number of columns: {self.cols}")
        self.table_options["alignment"] = string
        
    def set_precision(self, new_precision):
        if isinstance(new_precision, int):
            self.format_options["precision"] = [new_precision] * self.cols
        else:
            if len(new_precision) != self.cols:
                raise ValueError("A precision must be specified for each column or universally with and int."
                                 f"Current columns: {self.cols}")
            self.format_options["precision"] = list(new_precision)
    def set_lines(self, string):
        """
        Change the design of the table to use 'booktabs' or 'grid'
        """
        match string:
            case "booktabs":
                self.format_options["style"] = "booktabs"
                self.format_options["linebreak"] = r"\\"
            case "grid":
                self.format_options["style"] = "grid"
                self.format_options["linebreak"] = r"\\ \hline"
                self.table_options["alignment"] = ("|{}" * len(self.table_options["alignment"]) + "|").format(*self.table_options["alignment"])
            case _:
                raise IndexError("Allowed options are 'booktabs' and 'grid'")
                
                
    """
    ==============
    Make functions
    ==============
    """
    def _make_titles(self) -> str:
        """
        The function that makes the title row for the table
        """
        title = [] 
        def sub_tubular(L):
            """Breaks up a multi-row title into a tabular"""
            tabular = r"\begin{tabular}{c} "
            for string in L:
                tabular += (string + r" \\ ")
            return tabular + r"\end{tabular}"
    
        for column_title in self.titles:
            if not isinstance(column_title, str):
                # If the title element is not a sting its sent to be broken up
                title.append(sub_tubular(column_title))
            else:
                title.append(str(column_title))
                
        # Make final touches depending on design of the table
        if self.format_options["style"] == "booktabs":
            return (r"\toprule" + "\n\t\t") + self._make_table_row(title, "") + (r"\\" + "\n\t\t" + r"\midrule")
        elif self.format_options["style"] == "grid":
            return (r"\hline" + "\n\t\t") + self._make_table_row(title, "") + (r"\\" + "\n\t\t" + r"\hline")
        
        return self._make_table_row(title, "") # Not needed?
        
    def _make_table_body(self) -> str:
        """
        The function that makes the tabular of the table
        """
        str_data = [] # Data array with all values as strings
        def format_column_element(i, p):
            if isinstance(i, str): # Dont format strings as floats, its bad
                return i
            else:
                return "{0:.{1}f}".format(i, p)
        for i, column in enumerate(self.data.T):
            str_data.append(np.vectorize(format_column_element)(column, self.format_options["precision"][i]))
        str_data = np.array(str_data).T

        body = "" # String containing the tabluar
        for i in range(self.rows):
            body += (self._make_table_row(str_data[i], self.format_options["linebreak"]) + "\n\t\t") # New row is added 
        if self.format_options["style"] == "booktabs":
            body += r"\bottomrule" # Finishing touches
        return body
    
    """
    ================
    Internal helpers
    ================
    """
    def _make_table_row(self, L: list, linebreak: str) -> str:
        "Writes a table row from a list/array"
        return ("{} " + r"& {} " * (len(L) - 1) +  linebreak).format(*L)
    
    def _format_brackets(self, string):
        """As {} is used by the python string formatter '¤[' and '¤]' are used insted. 
        This function replaces '¤[' and '¤]' with {} for use in Latex"""
        return string.replace("¤]", "}").replace("¤[", "{")
    
    def _is_iter(self, obj):
        try:
            iter(obj)
            return True
        except TypeError:
            return False

latex_table.table_path = "/home/eewa/Desktop/"
lt = latex_table(["Apa", ("AB", "AA"), "C", "D"], np.full((4,), "A"), *np.linspace(1, 2, 12).reshape((3,4)),
                 label="tabel", caption="This is nice table")
lt.add_units([r"", r"\g", r"\g", r"\g"])
lt.set_lines("grid")
latex_table.__doc__
lt.set_options(alignment = "cc|c|cc")
lt.set_options(precision = [1,1,4,5])
lt.save("test")
print(lt)



