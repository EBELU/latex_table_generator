#!/home/eewa/anaconda3/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 10:43:17 2024

@author: Erik Ewald
"""

import numpy as np
import matplotlib.pyplot as plt
array = np.array
import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/"
os.chdir(dir_path)
import pandas


class multicolumn:
    def __init__(self, columns, placement):
        self.columns = columns
        self.placement = placement
        self.row_list = [""] * columns
        self.clines = []
        self.occpied_indices = np.array([], dtype = int)
    def add_multicol(self, starting_idx, span, content, clines = False, alignment = "c"):
        self.sanity_check(starting_idx, span)     
        L = self.row_list[:starting_idx + 1] + self.row_list[starting_idx + span:]
        L[starting_idx] = rf"\multicolumn¤[{span}¤]¤[{alignment}¤]¤[{content}¤]"
        self.row_list = L
        
        self.occpied_indices = np.append(self.occpied_indices, 
                                         np.arange(starting_idx, starting_idx + span))
        
        if clines and not r"\hline" in self.clines:
            if clines == r"hline":
                self.clines.clear()
                self.clines.append(r"\hline")
            elif isinstance(clines, str):
                self.clines.append(fr"\clines¤[{clines}¤]")
            else:
                self.clines.append(
                    fr"\cline¤[{starting_idx + 1}-{starting_idx + span}¤] ")
                
    def sanity_check(self, starting_idx, span):
        if starting_idx>= self.columns:
            raise IndexError("Starting index is out of bounds")
        if starting_idx + span > self.columns:
            raise IndexError("Span is out of bounds")
        span_idx = np.arange(starting_idx, starting_idx + span)
        if any(np.isin(span_idx, self.occpied_indices)):
            raise IndexError(r"Multicolumns collide at index"
                             f" {span_idx[np.isin(span_idx, self.occpied_indices)]}")
            
    def shift(self, index):
        self.row_list.insert(0, "")
        self.occpied_indices += 1
        self.columns += 1
        
    def __str__(self):
        return format_brackets(make_table_row(
            self.row_list, r"\\") + "\t" + "".join(self.clines) + "\n\t\t")
    
    def __eq__(self, multicol):
        return self.placement == multicol.placement
    def __lt__(self, multicol):
        return self.placement < multicol.placement
# mc = multicolumn(4, 0)
# mc.add_multicol(1, 3, "Hej", clines = True)
# mc.add_multicol(0, 1, "Hej", clines =  False)
# print(mc)
    
def make_table_row(L: list, linebreak: str) -> str:
    "Writes a table row from a list/array"
    return ("{} " + r"& {} " * (len(L) - 1) +  linebreak).format(*L)

def format_brackets(string):
    """As {} is used by the python string formatter '¤[' and '¤]' are used insted. 
    This function replaces '¤[' and '¤]' with {} for use in Latex"""
    return string.replace("¤]", "}").replace("¤[", "{")

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
        
    Class Methods
    -------------------------------------------------
    
    
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
   
    import numpy as np
            
    table_path = "" # Static path to the directory where tables are saved
            
    def __init__(self, *data: "list/array" , titles: list = [], label: str = "", caption: str = "", **kwargs) -> "latex_table":  
        import numpy as np     
        
        # Check if nan_character is given to be used in the default arrays
        # Can probablly be done better
        try:
            nan_char = kwargs["nan_char"]
        except KeyError:
            nan_char = r"\,"
        
        if len(data) > 1:
            # Take the abitrary number of columns
            if titles:
                # If titles are specific the first array is no longer the title array
                data_lists = data
                self.titles = np.array([titles], dtype=object)
            else:
                data_lists = list(data[1:])
                self.titles = np.array([data[0]], dtype=object)
                
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
            self.data = temp_data.T # Transpose so the data looks correct
        elif isinstance(data[0], dict):
            # Extract keys as the title-array
            self.titles = np.array([list(data[0].keys())], dtype = object)
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
            self.data = temp_data.T # Transpose so the data looks correct
            
        else:
            if not titles: # Title must be specified when giving one array as blob
                raise ValueError("column_titles must be specified as a keyword")
            self.data = np.array(data[0])
            self.titles = np.array([list(titles)], dtype = object)
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
        
        # Set defaults
        self.uncertanty = np.zeros_like(self.data)
        self.formaters = np.full_like(self.data, "{}", dtype=object)
        self.format_options = {"style" : "booktabs",
                               "nan_char" : nan_char,
                               "linebreak" : r"\\",
                               "precision" : [6] * self.cols}
        
        self.table_options = {"caption" : caption,
                        "label" : f"tab:{label}",
                        "position" : "H",
                        "alignment" : "c" * self.cols,
                        "position_float": r"\centering"}
        
        mcl = multicolumn(2, 0)
        mcl.add_multicol(0, 2, "content")
        
        self.multicolumns = {"title" : [], "tabular": []}
                
        for i, column in enumerate(self.data.T):
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
    def make_multicolumn(self, target: str, row_idx: int, start_idx: int, span: int, content: str, cline = False, alignment:str = "c"):
        """Insert a multicolumn into the table. It is recommended to do this after any multirows has been inserted to avoid yankyness.

        Args:
            target (str): Choose where to insert the multicolumn, options are 'title'/'tabular' 
            row_idx (int): Desired index of the row containing the multicolumn
            start_idx (int): Index of the column where the multicolumn starts.
            span (int): How many columns the multicolumn should cover.
            content (str): Text to be displayed in the multicolumn
            cline (bool, optional): Set clines to the row containing the multicolumn. Options are:
            - True: The cline follows the multicolumn
            - 'hline': Removes all other cline options for the row and inserts \hline under the row.
            - str: An arbitrary that is placed inside \clines{}
            Defaults to False.
            alignment (str, optional): Sets the alignment of the multicolumn. Defaults to "c".
        """        
        placement_L = [mc.placement for mc in self.multicolumns[target]]
        if row_idx in placement_L:
            idx = placement_L.index(row_idx)
            row = self.multicolumns[target][idx]
            row.add_multicol(start_idx, span, content, cline, alignment)
            self.multicolumns[target][idx] = row
        else:
            row = multicolumn(self.cols, row_idx)
            row.add_multicol(start_idx, span, content, cline, alignment)
            self.multicolumns[target].append(row)
            
    def make_multirow(self, column_idx:int, start_idx:int, span:int, content:str, replace:bool = False):
        """Creates a multirow in the table. Either by inserting a new column or replacing elements.

        Args:
            column_idx (int): The desired index of the new column or index of column of column to be modified.
            start_idx (int): Index of the column where the multirow starts.
            span (int): How many rows the multirow should cover
            content (str): Text to be displayed in the multirow
            replace (bool, optional): If False a new column is inserted with the multirow. If True existing element are erased to fit the multicolumn . Defaults to False.
        """        
        new_title_col = np.array([""] * len(self.titles), dtype=object)
        new_tab_col = np.array([""] * self.rows, dtype=object)
        multirow = format_brackets(fr"\multirow¤[{start_idx + 1}¤]¤[*¤]¤[{content}¤]")
        new_tab_col[start_idx] = multirow
        if replace:
            for i in range(span):
                self.data.T[column_idx][start_idx + i] = ""
            self.data.T[column_idx][start_idx] = multirow
        else:
            self._insert(new_tab_col, column_idx, "col", title_array=new_title_col)
        
            
    """=== WIP ==="""
    # def inset_column(self, idx, title, data):
        
    # def insert_row(self, idx, data, target = "tabular"):
        

        
        
        
        
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
                        self.set_lines(item)
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
                if not isinstance(self.titles[0][i], str):
                    # If the title element is already a tuple it is extended. * breaks the old tuple
                    self.titles[0][i] = (*self.titles[0][i], encapsulation[:half_enc_len] + 
                                  format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                else:
                    self.titles[0][i] = (self.titles[0][i], encapsulation[:half_enc_len] + 
                                  format_brackets(fr"\unit¤[{unit}¤]") + encapsulation[half_enc_len:])
                    
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
        picked_multicolumns = 0
        def sub_tubular(L):
            """Breaks up a multi-row title into a tabular"""
            tabular = r"\begin{tabular}{c} "
            for string in L:
                tabular += (string + r" \\ ")
            return tabular + r"\end{tabular}"
        for i in range(len(self.titles) + len(self.multicolumns["title"])):
            if i in [mc.placement for mc in self.multicolumns["title"]]:
                title_str = str(self.multicolumns["title"][picked_multicolumns]) + title_str
                picked_multicolumns += 1
                continue
            else:
                title_row = self.titles[i - picked_multicolumns]
            title = []
            for column_title in title_row:
                if not isinstance(column_title, str):
                    # If the title element is not a sting its sent to be broken up
                    title.append(sub_tubular(column_title))
                else:
                    title.append(str(column_title))
            title_str = (make_table_row(title, r"\\") + "\n\t\t") + title_str

            
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
        def format_column_element(i, p, error, formater):            
            if isinstance(i, str): # Dont format strings as floats, its bad
                formater_string = "{}"
            elif not np.isclose(error, 0):
                formater_string = r"\num¤[{0:.{1}f} \pm {2:.{1}f}¤]"
            else:
                formater_string = "{0:.{1}f}"
                
            return format_brackets(formater.format(formater_string.format(i, p , error)))
            
        for i, column in enumerate(self.data.T):
            str_data.append(np.vectorize(format_column_element)(
                column, self.format_options["precision"][i], (self.uncertanty.T)[i], (self.formaters.T)[i]))
        str_data = np.array(str_data).T

        body = "" # String containing the tabluar
        picked_multicolumns = 0
        for i in range(self.rows + len(self.multicolumns["tabular"])):
            if i in [mc.placement for mc in self.multicolumns["tabular"]]:
                body += str(self.multicolumns["tabular"][picked_multicolumns])
                picked_multicolumns += 1
            else:
                body += (make_table_row(str_data[i - picked_multicolumns], self.format_options["linebreak"]) + "\n\t\t") # New row is added 
        if self.format_options["style"] == "booktabs":
            body += r"\bottomrule" # Finishing touches
        return body
    
    def _insert(self, array, index, axis, target = None, title_array = []):

        print(axis)
        if axis == "col": # Change columns
            new_titles = np.insert(self.titles.copy(), index, title_array, axis = 1)
            new_tabular = np.insert(self.data.copy(), index, array, axis = 1)
            
            print(new_titles, "\n\n", new_tabular)
            self.formaters = np.insert(self.formaters, index, "{}", axis=1)
            self.uncertanty = np.insert(self.uncertanty, index, 0, axis=1)
            self.format_options["precision"].insert(index, 0)
            self.cols += 1
        elif axis == "row": # Change row
            new_titles = list(self.titles.copy())
            new_tabular = list(self.data.copy())
            if target == "title":
                new_titles.insert(index, array)
            elif target == "tabular":
                new_tabular.insert(index, array)
                
                self.formaters = np.insert(self.formaters, index, "{}", axis=0)
                self.uncertanty = np.insert(self.uncertanty, index, 0, axis=0)
                
            self.rows += 1
            
        self.data = np.array(new_tabular, dtype=object)
        self.titles = np.array(new_titles, dtype=object)
        # print(np.array(new_titles, dtype = object), "\n\n", np.array(new_tabular, dtype = object), "\n\n" )

if __name__ == "__main__":
    samples = ['A', 'B']
    data = [1, 2]
    column_names = ['Samples', 'Data']
    # These are all equiavalent
    lt = latex_table(column_names, samples, data)
    # lt = latex_table([samples, data], titles=column_names)
    # lt = latex_table({'Sample' : ['A', 'B'], 'Data' : [1, 2]})
    
    # print(lt)
    
    lt.make_multicolumn("title", 1, 0, 1, "content")
    lt.make_multicolumn("title", 1, 1, 1, "content")
    lt.make_multicolumn("title", 2, 0, 2, "content", cline = True)
    
    # lt._insert(np.array(["H", "G"]), index = 2, axis = "col",  title_array=["Hello"])
    
    lt.make_multirow(0, 0, 2, "content")
    lt.make_multirow(0, 1, 1, "contentdwaiuhi", True)
    print(lt)
    # lt._insert(np.array(["h", 2]), 0, 1, target = "tabular")

    lt.set_style("grid")
    latex_table.table_path = "/home/eewa/Documents/Kurser/MSFN02/Bildbehandling/Datorövningar/övn_rapport/"
    # lt = latex_table(["Apa", ("AB", "AA"), "C", "D"], np.full((4,), "A"), *np.linspace(1, 2, 12).reshape((3,4)),
    #                   label="tabel", caption="This is nice table")
    # lt.set_units([r"", r"\g", r"\g", r"\g"])
    # lt.set_style("grid")
    # latex_table.__doc__
    # lt.set_options(alignment = "cc|c|cc")
    # lt.set_options(precision = [1,1,4,5])
    
    # lt.set_uncertanty(np.linspace(1,2, 4).reshape((1,4)), slice(3,4))
    
    # lt.save("test")
    
    # lt.save("test_table")
    
    # numpy_array_with_data = (np.array([[1332, 1173, 662, 356],
    #                                   [1.00, 1.00, 0.85, 0.62],
    #                                   [5.2711, 5.2711, 30.018, 10.539],
    #                                   [392, 392, 346, 368]])) # Transpose to get correct col-row
    

    # numpy_array_with_data = (np.array([[1332, 1173, 662, 356], [1.00, 1.00, 0.85, 0.62], 
    # [5.2711, 5.2711, 30.018, 10.539], [392, 392, 346, 368]]))
    
    # isotopes = [r'\atom{Co}{60}', r'\atom{Co}{60}', r'\atom{I}{137}', r'\atom{Ba}{133}']
    
    # A_error = [5,7,8,5]
    
    # lt = latex_table(['Isotope','Energy', 'I', r'T', 'A'], 
    # isotopes, *numpy_array_with_data, caption='A nice table', label='a_nice_label')
    
    # lt.set_units(['', r'\kilo\electronvolt', '',  'y','\kilo Bq']) # Add units to the column
    
    # lt.set_options(precision = [0,0,2,4,0], alignment = "lcccc") # Set the number of decimals on each column
    
    # lt.set_uncertanty(A_error, -1) # Set error for the last column
    
    # lt.save("test_table")

    
    



