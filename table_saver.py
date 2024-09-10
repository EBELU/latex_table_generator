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
        'titles' must given as a keyword argument.
        
        2. latex_table(arr_titles, arr_0, arr_1,..., **kwargs)
        Given an arbitrary number of 1D-arrays representing the columns of the table. 
        If the 'titles'-argument is empty the first array given is implicitly set as the titels.
        The arrays are not required to be of the same length.
        
        3. latex_table(dict, **kwargs)
        Given a dictionary containing 1D-arrays representing the columns of the table.
        The indices are interpreted as the column titles.
        The arrays are not required to be of the same length.
    
    titles: array-like
        Array like object containing strings och tuples/lists of strings representing the column titles of the tables.
        The array must have the same length as the number of column in the table.
        A tuple/list given as a single title will be expanded into a titles consiting of several rows.
        
    label: str
        The label placed into \label{...} of the table.
        'tab:' is added by default.
        
    caption: str
        The text placed into \caption{...} of the table.
        
    **kwargs:
        Key word arguments passed to the set_options method.
        
        
    -> Returns:
        Class instance of latex_table
        
    Class Methods
    -------------------------------------------------
    
    
    Special Member Variables
    -------------------------------------------------
    
    latex_table.table_path:
        Lists the path to the directory where the saved tables will be placed.
        It is static and typically only needs to be set one at the start of the script.
    
    Examples
    -------------------------------------------------

    Ex 1.
        numpy_array_with_data = (np.array([[1332, 1173, 662, 356], [1.00, 1.00, 0.85, 0.62], 
        [5.2711, 5.2711, 30.018, 10.539], [392, 392, 346, 368]]))
        
        isotopes = [r'\atom{Co}{60}', r'\atom{Co}{60}', r'\atom{I}{137}', r'\atom{Ba}{133}']
        
        A_error = [5,7,8,5]
        
        lt = latex_table(['Isotope','Energy', 'I', r'T', 'A'], 
        isotopes, *numpy_array_with_data, caption='A nice table', label='a_nice_label')
        
        lt.set_units(['', r'\kilo\electronvolt', '',  'y','\kilo Bq']) # Add units to the column
        
        lt.set_options(precision = [0,0,2,4,0], alignment = "lcccc") # Set the number of decimals on each column
        
        lt.set_uncertanty(A_error, -1) # Set error for the last column
    
    """
   
    import numpy as np
    table_path = "" # Static path to the directory where tables are saved
    
    def __init__(self, *data, titles: list = [], label: str = "", caption: str = "", **kwargs) -> "latex_table":  
        import numpy as np
        if len(data) > 1:
            if len(titles):
                data_lists = data
                self.titles = [titles]
            else:
                data_lists = list(data[1:])
                self.titles = [data[0]]
            self.rows = len(max(data_lists, key = len))
            self.cols = len(data_lists)
            temp_data = np.full((self.cols, self.rows), r"\,", dtype=object)
            for i,L in enumerate(data_lists):
                temp_data[i][:len(L)] = L
            self.data = temp_data.T
        elif isinstance(data[0], dict):
            self.titles = [list(data[0].keys())]
            data_lists = list(data[0].values())
            self.rows = len(max(data_lists, key = len))
            self.cols = len(data_lists)
            temp_data = np.full((self.cols, self.rows), r"\,", dtype=object)
            for i,L in enumerate(data_lists):
                temp_data[i][:len(L)] = L
            self.data = temp_data.T
            
        else:
            if not titles:
                raise ValueError("column_titles must be specified as a keyword")
            self.data = data[0]
            self.titles = [list(titles)]
            self.rows, self.cols  = self.data.shape
        
        if len(self.titles[0]) != self.cols:
            raise AssertionError(f"The length of title array, {len(self.titles) }, "
                                 f"does not match the number of columns, {self.cols}"
                                 f"\nAttempted title array: {self.titles}")
        # self.data = pd.DataFrame(data)
        # self.titles = list(column_titles)
        # self.format_options["precision"] = [6] * self.cols       
        # self.titles *= 2
        
        
        # self.titles[1] = ["", "", r"\multicolumn{2}{c}{Multi}"]
        self.uncertanty = np.zeros_like(self.data)
        self.formaters = np.full_like(self.data, "{}", dtype=object)
        self.format_options = {"style" : "booktabs",
                               "nan_char" : r"\,",
                               "linebreak" : r"\\",
                               "precision" : [6] * self.cols}
        self.table_options = {"caption" : caption,
                        "label" : f"tab:{label}",
                        "position" : "H",
                        "alignment" : "c" * self.cols,
                        "position_float": r"\centering"}
        self.set_options(**kwargs)
        

        
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
        
    
    def set_uncertanty(self, array, idx = None):
        if isinstance(idx, type(None)) and array.shape != (self.cols, self.rows):
            raise ValueError("")
        elif isinstance(idx, type(None)):
            self.uncertanty = array
        elif isinstance(idx, slice) or isinstance(idx, int):
            self.uncertanty.T[idx] = array
            
            
        
        
        
    """=== WIP ==="""
    # make_multirow
    """=== WIP ==="""
    # make_multicol
    """=== WIP ==="""
    # def inset(self, idx, title, data):
        
        
    def set_formater(self, format_string, col = "single", row = "single"):
        """Sets format options for the tabular. A latex command like \macro{} will be interpreted as \macro{tabular_cell}. 
        A command can be applied to entire row or column by only indexing one or the other. 
        Slices are also accepted.
        
        If given a string without {} it will replace the content of the cell with the string.

        Args:
            format_string (str): Latex command to apply.
            col (int/slice, optional): Column index. Defaults to "full".
            row (int/slice, optional): Row index. Defaults to "full".
        """        
        common_latex_formats = {"bf" : r"\textbf¤[{}¤]",
                                "it" : r"\textit¤[{}¤]",
                                "ul" : r"¤[\ul{}¤]",
                                "$$" : "${}$"}
        if format_string.lower() in common_latex_formats:
            format_string = common_latex_formats[format_string]
        else:
            format_string = format_string.replace("{}", "¤[¤]").replace(
            "{", "¤[").replace("}", "¤]").replace("¤[¤]", "¤[{}¤]")
        if isinstance(col, str) and isinstance(row, str):
            self.formaters[:,:] = format_string
        elif isinstance(col, str) and not isinstance(row, str):

            self.formaters[row,:] = format_string
        elif not isinstance(col, str) and isinstance(row, str):
            print("hej")
            self.formaters[:,col] = format_string
        else:
            self.formaters[col,row] = format_string
            
   

    
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
             'alignment': 'c...c', 
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
    
    def set_units(self, unit_array, encapsulation = "$[]$"):
        r"""
        Takes a list of strings compatible with the siunitx function \unit{}.
        The length of the list must match the number of columns, a column without a unit is left as an empty string.
        The units are placed under the column title for each column.
        
        Ex:
            latex_table.set_units([r"\kilo\electronvolt"]) -> [keV]
        """
        
        if len(unit_array) != self.cols:
            raise ValueError(f"The length of the unit array, {len(unit_array)}, "
                             f"must match the number of columns in the table, {self.cols}."
                             "\n\tIf no unit is desired for a column title leave en empty string '' ")
        half_enc_len = len(encapsulation) // 2
        for i, unit in enumerate(unit_array):
            if unit:
                if not isinstance(self.titles[0][i], str):
                    # If the title element is already a tuple it is extended. * breaks the old tuple
                    self.titles[0][i] = (*self.titles[0][i], encapsulation[:half_enc_len] + 
                                  self._format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                else:
                    self.titles[0][i] = (self.titles[0][i], encapsulation[:half_enc_len] + 
                                  self._format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                    
    def set_alignment(self, string):
        if len(string.replace("|", "")) < self.cols:
            raise ValueError("The number of alignment is less than"
                             f"the number of columns. Current number of columns: {self.cols}")
        self.table_options["alignment"] = string
        
    def set_precision(self, new_precision):
        if isinstance(new_precision, int):
            self.format_options["precision"] = [new_precision] * self.cols
        else:
            if len(new_precision) != self.cols:
                raise ValueError("A precision must be specified for each column or universally with and int."
                                 f" Current columns: {self.cols}, given array was {len(new_precision)}")
            self.format_options["precision"] = list(new_precision)
    def set_style(self, string):
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
        title_str = ""
        def sub_tubular(L):
            """Breaks up a multi-row title into a tabular"""
            tabular = r"\begin{tabular}{c} "
            for string in L:
                tabular += (string + r" \\ ")
            return tabular + r"\end{tabular}"
        for title_row in reversed(self.titles):
            title = []
            for column_title in title_row:
                if not isinstance(column_title, str):
                    # If the title element is not a sting its sent to be broken up
                    title.append(sub_tubular(column_title))
                else:
                    title.append(str(column_title))
            title_str += (self._make_table_row(title, r"\\") + "\n\t\t")
            
        # Make final touches depending on design of the table
        if self.format_options["style"] == "booktabs":
            return (r"\toprule" + "\n\t\t") + title_str + "\n\t\t" + r"\midrule"
        elif self.format_options["style"] == "grid":
            return (r"\hline" + "\n\t\t") + title_str + "\n\t\t" + r"\hline"
    
        
    def _make_table_body(self) -> str:
        """
        The function that makes the tabular of the table
        """
        str_data = [] # Data array with all values as strings
        def format_column_element(i, p, error, formater):            
            if isinstance(i, str): # Dont format strings as floats, its bad
                formater_string = "{}"
            elif not np.isclose(error, 0):
                formater_string = r"\num¤[{0:.{1}f} \pm {2:.{1}f}¤]"
            else:
                formater_string = "{0:.{1}f}"
                
            return self._format_brackets(formater.format(formater_string.format(i, p , error)))
            
        for i, column in enumerate(self.data.T):
            str_data.append(np.vectorize(format_column_element)(
                column, self.format_options["precision"][i], (self.uncertanty.T)[i], (self.formaters.T)[i]))
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

if __name__ == "__main__":
    latex_table.table_path = "/home/eewa/Documents/Kurser/MSFN02/Bildbehandling/Datorövningar/övn_rapport/"
    # lt = latex_table(["Apa", ("AB", "AA"), "C", "D"], np.full((4,), "A"), *np.linspace(1, 2, 12).reshape((3,4)),
    #                  label="tabel", caption="This is nice table")
    # lt.add_units([r"", r"\g", r"\g", r"\g"])
    # lt.set_lines("grid")
    # latex_table.__doc__
    # lt.set_options(alignment = "cc|c|cc")
    # lt.set_options(precision = [1,1,4,5])
    
    # lt.set_uncertanty(np.linspace(1,2, 4).reshape((1,4)), slice(3,4))
    
    # lt.save("test")
    
    # print(lt.format_options.values())
    
    numpy_array_with_data = (np.array([[1332, 1173, 662, 356],
                                      [1.00, 1.00, 0.85, 0.62],
                                      [5.2711, 5.2711, 30.018, 10.539],
                                      [392, 392, 346, 368]])) # Transpose to get correct col-row
    

    numpy_array_with_data = (np.array([[1332, 1173, 662, 356], [1.00, 1.00, 0.85, 0.62], 
    [5.2711, 5.2711, 30.018, 10.539], [392, 392, 346, 368]]))
    
    isotopes = [r'\atom{Co}{60}', r'\atom{Co}{60}', r'\atom{I}{137}', r'\atom{Ba}{133}']
    
    A_error = [5,7,8,5]
    
    lt = latex_table(['Isotope','Energy', 'I', r'T', 'A'], 
    isotopes, *numpy_array_with_data, caption='A nice table', label='a_nice_label')
    
    lt.set_units(['', r'\kilo\electronvolt', '',  'y','\kilo Bq']) # Add units to the column
    
    lt.set_options(precision = [0,0,2,4,0], alignment = "lcccc") # Set the number of decimals on each column
    
    lt.set_uncertanty(A_error, -1) # Set error for the last column
    
    lt.save("test_table")
    print(lt)



