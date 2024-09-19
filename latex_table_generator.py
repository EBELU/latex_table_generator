# -*- coding: utf-8 -*-
r"""
    =================
    -----------------
    LaTeX Table Generator
    -----------------
    =================
    
    Provides the *latex_table* class to turn sets of data into latex table.
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
    
"Created on Mon Sep  9 10:43:17 2024"
import numpy as np
import pandas as pd

if __name__ == "__main__":
    array = np.array
# import matplotlib.pyplot as plt
# import os, sys
# dir_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/"
# os.chdir(dir_path)

"""
-------------------------------------------------------------------------------
===============================================================================

                                 Helper Classes
                    
===============================================================================
-------------------------------------------------------------------------------
"""


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
    
    
    
    
    
    
    
    
    
    
    
    
    

"""
-------------------------------------------------------------------------------
===============================================================================

                                Formatter functions
                    
===============================================================================
-------------------------------------------------------------------------------
"""

def remove_spacer(L) -> list:
    """
    Removes multicolumn_spacer and multirow_spacer during formatting.
    """
    return list(L[L != multicolumn_spacer()])
    
def make_table_row(L: list, linebreak: str) -> str:
    "Writes a table row from a list/array"
    return ("{} " + r"& {} " * (len(L) - 1) +  linebreak).format(*L)

def format_brackets(string):
    """As {} is used by the python string formatter '¤[' and '¤]' are used insted. 
    This function replaces '¤[' and '¤]' with {} for use in Latex"""
    return string.replace("¤]", "}").replace("¤[", "{")










"""
-------------------------------------------------------------------------------
===============================================================================

                                   Main class
                    
===============================================================================
-------------------------------------------------------------------------------
"""

class latex_table:
    
    r"""
            
    Constructor 
    -------------------------------------------------
    Arguments
    =========
    *data:
        The constructor provides 3 ways of creating a latex-table.
        
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
        Key word arguments passed to the set_options method. See set_options for valid kwargs.
        
        
    -> Returns:
        Class instance of latex_table
        
"""


    """
    =======
    Static Path
    =======
    """
    table_path = "" # Static path to the directory where tables are saved
    
    
    """
    =======
    Constructor
    =======
    """
            
    def __init__(self, *data, titles: list = [], label: str = "", caption: str = "", **kwargs) -> "latex_table":  
        
        # Check if nan_character is given to be used in the default arrays
        # Can probablly be done better
        try:
            nan_char = kwargs["nan_char"]
        except KeyError:
            nan_char = r"\,"
            
        if len(data) == 0:
            raise ValueError("No data given")
            
        if len(data) > 1:
            # Take the abitrary number of columns
            if titles:
                # If titles are specific the first array is no longer the title array
                data_lists = data
                titles = [pd.Series(titles)]
                self.titles = pd.DataFrame(titles, dtype=object)
            else:
                data_lists = list(data[1:])
                titles = [pd.Series(data[0])]
                self.titles = pd.DataFrame(titles, dtype=object)
                
            # Figure out the shape of the tabular
            self.rows = len(max(data_lists, key = len)) # Finds the logest sub-list
            self.cols = len(data_lists)
            
            # Initiates an array of the correct shape
            # This is to allow for subarrays of different length
            # The empty elements are filled with nan_char
            temp_data = np.full((self.cols, self.rows), nan_char, dtype=object)
            # Fill default list
            for i,L in enumerate(data_lists):
                temp_data[i][:len(L)] = L
            self.data = pd.DataFrame(temp_data.T) # Transpose so the data looks correct
            
        elif isinstance(data[0], dict):
            # Extract keys as the title-array
            self.titles = pd.DataFrame(list(data[0].keys()), dtype = object)
            # Values set as the data array
            data_lists = list(data[0].values())
            
            # Figure out the shape of the tabular
            self.rows = len(max(data_lists, key = len)) # Finds the logest sub-list
            self.cols = len(data_lists)
            
            # Initiates an array of the correct shape
            # This is to allow for subarrays of different length
            # The empty elements are filled with nan_char
            temp_data = np.full((self.cols, self.rows), nan_char, dtype=object)
            # Fill default list
            for i,L in enumerate(data_lists):
                temp_data[i][:len(L)] = L
            self.data = pd.DataFrame(temp_data.T) # Transpose so the data looks correct
            
        else:
            if not titles: # Title must be specified when giving one array as blob
                raise ValueError("titles= must be specified as a"+
                                 " keyword when giving a single data array")
            self.data = pd.DataFrame(data[0])
            self.titles = pd.DataFrame([pd.Series(list(titles))], dtype = object)
            # print(self.titles)
            self.rows, self.cols  = self.data.shape
        
        if len(self.titles[0]) != self.cols and False:
            raise AssertionError(f"The length of title array, {len(self.titles) }, "
                                 f"does not match the number of columns, {self.cols}"
                                 f"\nAttempted title array: {self.titles}")
        
        # Set defaults
        self.uncertanty = np.zeros_like(self.data)
        self.formatters = np.full_like(self.data, "{}", dtype=object)
        self.format_options = {"style" : "booktabs",
                               "nan_char" : nan_char,
                               "precision" : [6] * self.cols,
                               "multicol_alignment": "c"}
        
        self.table_options = {"caption" : caption,
                        "label" : f"tab:{label}",
                        "position" : "H",
                        "alignment" : "c" * self.cols,
                        "position_float": r"\centering"}
        
        self.linebreaks = {"title" : [[r"\\"] for i in range(len(self.titles))],
                           "tabular": [[r"\\"] for i in range(self.rows)]}
        
                
        for i, column in enumerate(self.data.to_numpy().T):
            most_decialms = min(np.array(column, dtype = str)) # Convert to strings and find smallest value
            # Handle floats that are ints and ints, must use the any-loop to handle int and str the same list
            if most_decialms.endswith(".0") or any(isinstance(element, int) for element in column):
                self.format_options["precision"][i] = 0
            else:
                # If something throws, ignore and dont change
                try:
                    decimal_points = len(most_decialms.split(".")[1]) # Insolate decimals
                    if not isinstance(decimal_points, int):
                        # If something borks in the prevoius ex. return None, throw something
                        raise ValueError
                    self.format_options["precision"][i] = decimal_points
                except:
                    pass
            

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
        return format_brackets(
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
    
    """
    =======
    Multicolumn and multirow
    =======
    """
    def make_multicolumn(self, target: str, row_idx: int, start_idx: int, span: int, content: str,
                         insert:bool = False, cline = False, alignment:str = "default"):
        """Insert a multicolumn into the table. It is recommended to do this after any multirows has been inserted to avoid yankyness.

        Args:
            target (str): Choose where to insert the multicolumn, options are 'title'/'tabular' 
            row_idx (int): Desired index of the row containing the multicolumn
            start_idx (int): Index of the column where the multicolumn starts.
            span (int): How many columns the multicolumn should cover.
            content (str): Text to be displayed in the multicolumn.
            insert (bool, optional): If the new multicolumn is to be inserted into an existing row.
            cline (bool, optional): Set clines to the row containing the multicolumn. Options are:
            - True: The cline follows the multicolumn
            - 'hline': Removes all other cline options for the row and inserts \hline under the row.
            - str: An arbitrary that is placed inside \clines{}
            Defaults to False.
            alignment (str, optional): Sets the alignment of the multicolumn. Defaults to "default".
        """        
        if target == "title":
            target_array = self.titles
        elif target == "tabular":
            target_array = self.data
        else:
            raise KeyError("Invalid target. Valid targets are 'title'/'tabular'.")
        
        if alignment == "default":
            alignment = self.format_options["multicol_alignment"]
            
        new_multicol = multicolumn(start_idx, span, content, clines=cline, alignment=alignment)
        multi_col = [new_multicol] + [multicolumn_spacer()] * (span - 1)
            
        if insert:
            old_elements = target_array.iloc[row_idx][start_idx: start_idx + span]
            for i, e in enumerate(old_elements):
                if isinstance(e, multicolumn) or isinstance(e, multicolumn_spacer):
                    raise AssertionError(f"Multicolumns collide at row {row_idx}, column {i + start_idx}"
                                         f"{self.info(target, (i + start_idx, row_idx))}")
            
            new_row = pd.concat([target_array.iloc[row_idx][:start_idx], pd.Series(multi_col), 
                                target_array.iloc[row_idx][start_idx + span:]], ignore_index=True)
            
            if target == "title":
                self.titles.iloc[row_idx] = new_row
            else:
                self.data.iloc[row_idx] = new_row

            if cline:
                self.linebreaks[target][row_idx].append(new_multicol.cline)

        
        else:
            front_pad = start_idx - 1 if start_idx > 1 else 0
            back_pad = self.cols - start_idx - span 
            if back_pad < 0: back_pad = 0
            
            new_row = [""] * front_pad + multi_col + [""] * back_pad

            self._insert(new_row, row_idx, "row", target)

            if cline:
                self.linebreaks[target][row_idx]= [r"\\", new_multicol.cline]
            
    def make_multirow(self, target:str, column_idx:int, start_idx:int, span:int, content:str,
                      insert:bool = False):
        """Creates a multirow in the table. Either by inserting into an existing column or making a new.

        Args:
            target (str): Choose where to insert the multirow, options are 'title'/'tabular' 
            column_idx (int): The desired index of the new column or index of column of column to be modified.
            start_idx (int): Index of the column where the multirow starts.
            span (int): How many rows the multirow should cover
            content (str): Text to be displayed in the multirow
            insert (bool, optional): If False a new column is inserted with the multirow. If True existing element are erased to fit the multicolumn . Defaults to False.
        """      
        if insert:
            if target == "title":
                target_array = self.titles
            elif target == "tabular":
                target_array = self.data
            else:
                raise KeyError("Invalid target. Valid targets are 'title'/'tabular'.")
            old_elements = target_array[column_idx][start_idx: start_idx + span]
            # print(old_elements)
            for i, e in enumerate(old_elements):
                if isinstance(e, multirow) or isinstance(e, multirow_spacer):
                    raise AssertionError(f"Multirows collide at row {i + start_idx}, column {column_idx}"
                                         f"{self.info({target}, ({i + start_idx}, {column_idx}))}")
                    
            new_multirow = [multirow(start_idx, span, content)] + [multirow_spacer()] * (span - 1)
            new_column = pd.concat([target_array[column_idx][:start_idx], pd.Series(new_multirow), 
                                    target_array[column_idx][start_idx + span:]], ignore_index=True)
            
            if target == "title":
                self.titles[column_idx] = new_column
            elif target == "tabular":
                self.data[column_idx] = new_column
            
                
        else:
            empty_title_col = ["" for i in range(len(self.titles))]
            empty_tab_col = ["" for i in range(self.rows)]            
            new_multirow = [multirow(start_idx, span, content)] + [multirow_spacer()] * (span - 1)
            if target == "title":
                top_pad = start_idx - 1 if start_idx > 1 else 0
                bottom_pad = len(self.titles) - start_idx - span 
                if bottom_pad < 0: bottom_pad = 0
                new_column = [""] * top_pad + new_multirow + [""] * bottom_pad
                
                self._insert(empty_tab_col, column_idx, "col", title_array=new_column)
            elif target == "tabular":
                top_pad = start_idx - 1 if start_idx > 1 else 0
                bottom_pad = self.rows - start_idx - span 
                if bottom_pad < 0: bottom_pad = 0
                new_column = [""] * top_pad + new_multirow + [""] * bottom_pad
                self._insert(new_column, column_idx, "col", title_array=empty_title_col)
            else:
                raise KeyError("Invalid target. Valid targets are 'title'/'tabular'.")
                
            if column_idx != self.cols:
                idx_set = set()
                for linebreak_L in self.linebreaks["title"] + self.linebreaks["tabular"]:
                    idx_set = idx_set | set([c.start - 1 for c in linebreak_L if isinstance(c, cline_obj)])
                if bool(idx_set) and column_idx <= max(idx_set):
                    for linebreak_L in self.linebreaks["title"] + self.linebreaks["tabular"]:
                        for cl in linebreak_L:
                            if isinstance(cl, cline_obj) and cl.start >= start_idx:
                                cl.shift(1)
    
    
    
    def set_uncertanty(self, array, idx = None):
        if isinstance(idx, type(None)) and array.shape != (self.cols, self.rows):
            raise ValueError("")
        elif isinstance(idx, type(None)):
            self.uncertanty = array
        elif isinstance(idx, slice) or isinstance(idx, int):
            self.uncertanty.T[idx] = array
            

        
            
    """=== WIP ==="""
    # def inset_column(self, idx, title, data):
        
    # def insert_row(self, idx, data, target = "tabular"):
        


        
        
    def set_formatters(self, format_string, col = "single", row = "single"):
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
            self.formatters[:,:] = format_string
        elif isinstance(col, str) and not isinstance(row, str):
            self.formatters[row,:] = format_string
        elif not isinstance(col, str) and isinstance(row, str):
            self.formatters[:,col] = format_string
        else:
            self.formatters[col,row] = format_string
            
   

    
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
            'precision': [6, 6,..., 6, 6]
            'multicol_alignment': 'c'
        """
        
        for key,item in kwargs.items():
            if key in self.table_options:
                match key:
                    case "alignment":
                        self.set_alignment(item)
                    case _:
                        self.table_options[key] = item
            elif key in self.format_options:
                match key:
                    case "style":
                        self.set_style(item)
                    case "precision":
                        self.set_precision(item)
                    case _:
                        self.format_options[key] = item
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
                if not isinstance(self.titles.values[-1][i], str):
                    # If the title element is already a tuple it is extended. * breaks the old tuple
                    self.titles[self.titles.columns[i]] = (*self.titles.values[-1][i], encapsulation[:half_enc_len] + 
                                  format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                else:
                    self.titles[self.titles.columns[i]] = [(self.titles.values[-1][i], encapsulation[:half_enc_len] + 
                                  format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])]
                    
                    
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
            case "grid":
                self.format_options["style"] = "grid"
                self.format_options["multicol_alignment"] = f"|{self.format_options['multicol_alignment']}|"
                # self.table_options["alignment"] = ("|{}" * len(self.table_options["alignment"]) + "|").format(*self.table_options["alignment"])
                self.table_options["alignment"] = "".join(f"|{c}|" for c in self.table_options["alignment"] if c != "|")
                self._check_lines()
                self.linebreaks["tabular"][-1].append(" \hline")
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
        for i, title_row in enumerate(self.titles.values):
            title = []
            for column_title in remove_spacer(title_row):
                if (isinstance(column_title, multicolumn) or 
                    isinstance(column_title, multirow) or 
                    isinstance(column_title, multirow_spacer)):
                    column_title = str(column_title)
                if not isinstance(column_title, str):
                    # If the title element is not a sting its sent to be broken up
                    title.append(sub_tubular(column_title))
                else:
                    title.append(str(column_title))
            linebreak = "".join([str(e) for e in self.linebreaks["title"][i]])
            title_str = (make_table_row(title, linebreak) + "\n\t\t") + title_str

            
        # Make final touches depending on design of the table
        if self.format_options["style"] == "booktabs":
            return (r"\toprule" + "\n\t\t") + title_str + r"\midrule"
        elif self.format_options["style"] == "grid":
            return (r"\hline" + "\n\t\t") + title_str  + r"\hline"
    
        
    def _make_table_body(self) -> str:
        """
        The function that makes the tabular of the table
        """
        str_data = [] # Data array with all values as strings
        def format_column_element(i, p, error, formatter):         
            if isinstance(i, multicolumn) or isinstance(i, multirow) or isinstance(i, multirow_spacer):
                i = str(i)
            if isinstance(i, str): # Dont format strings as floats, its bad
                formatter_string = "{}"
            elif not np.isclose(error, 0):
                formatter_string = r"\num¤[{0:.{1}f} \pm {2:.{1}f}¤]"
            else:
                formatter_string = "{0:.{1}f}"
                
            return format_brackets(formatter.format(formatter_string.format(i, p , error)))
            
        for i, column in enumerate(self.data.values):
            L = [format_column_element(value, 
                                       self.format_options["precision"][j], 
                                       (self.uncertanty)[i][j], 
                                       (self.formatters)[i][j])
                 for j, value in enumerate(remove_spacer(column))]
            str_data.append(L)

        body = "" # String containing the tabluar
        for i in range(self.rows):
            linebreak = "".join([str(e) for e in self.linebreaks["tabular"][i]])
            body += (make_table_row(str_data[i], linebreak) + "\n\t\t") # New row is added 
        if self.format_options["style"] == "booktabs":
            body += r"\bottomrule" # Finishing touches
        return body
    
    
    
    
    def _insert(self, array, index, axis, target = None, title_array = []):
        """
        Universal insert function. Should only be used internally.
        """
        if axis == "col": # Change columns
            new_tabular = self.data.copy()
            new_title = self.titles.copy()    
            new_title.insert(index, -1, title_array)
            new_tabular.insert(index, -1, array) 
            
            # Change backend data
            self.formatters = np.insert(self.formatters, index, "{}", axis=1)
            self.uncertanty = np.insert(self.uncertanty, index, 0, axis=1)
            self.format_options["precision"].insert(index, 0)
            self.cols += 1
            self.table_options["alignment"] += self.table_options["alignment"][0]
            
            
            # Reset index
            new_tabular.columns = np.arange(len(new_tabular.columns))
            new_title.columns = np.arange(len(new_title.columns))
            # Apply new columns
            self.data = new_tabular
            self.titles = new_title
            
        elif axis == "row": # Change row
            new_tabular = self.data.T.copy()
            new_title = self.titles.T.copy()  
            if target == "title":
                new_title.insert(index, -1, array)
                
                # Change backend data
                self.linebreaks["title"].insert(index, [r"\\"])
            elif target == "tabular":
                new_tabular.insert(index, -1, array)    
                
                # Change backend data
                self.formatters = np.insert(self.formatters, index, "{}", axis=0)
                self.uncertanty = np.insert(self.uncertanty, index, 0, axis=0)
                self.linebreaks["tabular"].insert(index, [r"\\"])

                self.rows += 1
            
            # Reset index
            new_tabular.columns = np.arange(len(new_tabular.columns))
            new_title.columns = np.arange(len(new_title.columns))
            # Apply new rows
            self.data = new_tabular.T
            self.titles = new_title.T
            
    def info(self, exception = False, index = None):
    
        line = "-----------------------------------"
        def info_format(i):
            if isinstance(i, multirow):
                return f"|{i.content}|"
            elif isinstance(i, multirow_spacer):
                return "|multirow_spacer|"
            elif isinstance(i, multicolumn):
                return f"--{i.content}--"
            elif isinstance(i, multicolumn_spacer):
                return "-multicol_spacer-"
            else:
                return i

        show_cpy_tab = self.data.copy()
        show_cpy_title = self.titles.copy()
        for col in show_cpy_tab:
            show_cpy_tab[col] = show_cpy_tab[col].apply(info_format)
            show_cpy_title[col] = show_cpy_title[col].apply(info_format)
            
        if exception == "title":
            show_cpy_title[index[0]][index[1]] = '\033[41m' + str(show_cpy_title[index[0]][index[1]])  + '\033[0m'
            return("\n" + line + "\nTable Titles:\n" + str(show_cpy_title))
        if exception == "tabublar":
            show_cpy_title[index[0]][index[1]] = '\033[41m' + str(show_cpy_title[index[0]][index[1]]) + + '\033[0m'
            return("\n" + line + "\nTable Tabular:\n" + str(show_cpy_tab))
        
        print("Table Options:")
        for key, v in self.table_options.items():
            print("\t", key, "=",  v)
        print()    
        print("Format Options:")
        for key, v in self.format_options.items():
            print("\t", key, "=",  v)
 

        print("\n", line)
        print("Table Titles (Transposed!):")
        print(show_cpy_title.T)
        print("\n", line)
        print("Table Tabular:")
        print(show_cpy_tab)

 
        print("\n", line)
        print("Table Formatters:")
        print(pd.DataFrame(self.formatters).apply(lambda x: x.apply(lambda y: format_brackets(y))))

        print("\n", line)
        print("Table Uncertanty:")
        print(pd.DataFrame(self.uncertanty))
        
        print("\n", line)
        print("Title Linebreaks:")
        for i, l in enumerate(self.linebreaks["title"]):
            print(i,": ", *l)
            
        print("\nTabular Linebreaks:")
        for i, l in enumerate(self.linebreaks["tabular"]):
            print(i, ": ", *l)

    def _check_lines(self):
        def check_column(column):
            idx_column = np.zeros(len(column)-1)
            for i in range(len(column) - 1):
                if isinstance(column[i], multirow) or isinstance(column[i], multirow_spacer):
                    if isinstance(column[i+1], multirow_spacer):
                        idx_column[i] = 1
            return idx_column
        
        idx_array = np.array([np.array(check_column(col), dtype=bool) 
                              for col in self.data.copy().to_numpy().T]).T
        for i, bool_row in enumerate(idx_array):
            idx_array = np.where(bool_row, None, (np.arange(len(bool_row))))
            idx_array = np.array(idx_array, dtype=str)
            idx_str_L = "".join(idx_array).split("None")
            new_breakline = [r"\\"]
            for j, line_string in enumerate(idx_str_L):
                if len(line_string) == self.cols:
                    new_breakline.append(cline_obj(string_val="hline"))
                elif line_string:
                    new_breakline.append(cline_obj(int(line_string[0]), len(line_string)))
            self.linebreaks["tabular"][i] = new_breakline
        