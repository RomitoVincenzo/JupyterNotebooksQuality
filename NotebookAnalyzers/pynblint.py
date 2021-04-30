import json
import ast
from notebooktoall.transform import transform_notebook


def notebook_to_dict(filename):
    """
       Turns a notebook into a dictionary object

       Args:
           filename(str): name of the notebook file in the TargetNotebooks folder
       Returns:
           data: dictionary object representing the notebook

       A way you might use me is

       nb_dict = notebook_to_dict("file.ipynb")
    """
    f = open("../TargetNotebooks/" + filename, )
    data = json.load(f)
    f.close()
    return data


def notebook_to_script(filename):
    """
       Extracts the code from a jupyter notebook in the TargetNotebooks folder

       Args:
           filename(str): name of the notebook file in the TargetNotebook folder
       Returns:
           script: string containing the python code from the jupyter notebook

       A way you might use me is

       script = notebook_to_script("file.ipynb")
    """
    transform_notebook(ipynb_file="../TargetNotebooks/" + filename, export_list=["py"])
    f = open(filename.replace(".ipynb", ".py"), 'r')
    script = f.read()
    f.close()
    return script


def count_func_defs(code):
    """
       Extracts the number of function definitions from a string of code

       Args:
           code(str): string of python code
       Returns:
           f_num: integer representing the number of function definitions in the code

       A way you might use me is

       function_defs_count = count_func_defs(code)
    """
    tree = ast.parse(code)
    f_num = sum(isinstance(exp, ast.FunctionDef) for exp in tree.body)
    return f_num


def count_non_executed_cells(notebook):
    """
        Number of non-executed cells from a dictionary representing the notebook

        Args:
            notebook(dic): python dictionary object representing the jupyter notebook
        Returns:
            not_exec_cells: integer representing the number of non-executed cells in the notebook

        A way you might use me is

        non-exec_cells_count = count_non_executed_cells(nb_dict)
    """
    not_exec_cells = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'code':
            if cell['execution_count'] is None and cell['source'] != []:
                not_exec_cells = not_exec_cells + 1  # This is a not executed Python Cell containing actual code
    return not_exec_cells


def count_empty_cells(notebook):
    """
        Number of empty cells from a dictionary representing the notebook

        Args:
            notebook(dic): python dictionary object representing the jupyter notebook
        Returns:
            empty_cells_count: integer representing the number of empty cells in the notebook

        A way you might use me is

        empty_cells_count = count_empty_cells(nb_dict)
    """
    empty_cell = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'code':
            if cell['execution_count'] is None and cell['source'] == []:
                empty_cell = empty_cell + 1  # This is an empty Python Cell
    return empty_cell


def count_md_lines(notebook):
    """
        Number of markdown rows from a dictionary representing the notebook

        Args:
            notebook(dic): python dictionary object representing the jupyter notebook
        Returns:
            markdowns: integer representing the number of markdown rows in the notebook

        A way you might use me is

        md_lines_count = count_md_lines(nb_dict)
    """
    markdowns = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'markdown':
            rows = len(cell['source'])
            markdowns = markdowns + rows
    return markdowns


def count_md_titles(notebook):
    """
        Number of markdown title rows from a dictionary representing the notebook

        Args:
            notebook(dic): python dictionary object representing the jupyter notebook
        Returns:
            titles: integer representing the number of markdown title rows in the notebook

        A way you might use me is

        titles_count = count_md_titles(nb_dict)
    """
    titles = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'markdown':
            for row in cell['source']:
                if row.lstrip().startswith('#'):
                    titles = titles + 1
    return titles


def are_imports_in_first_cell(code):
    """
        Verifies if there are no import statements in cells that are not the first one

        Args: code(str): string of python code Returns: correct_position: boolean value that is True if there are no
        imports other than those in the first cell of code and False otherwise

        A way you might use me is

        all_imports_in_first_cell = are_imports_in_first_cell(code)
    """
    found_first_cell = False  # when True it means we found the first cell of code that has to be ignored
    second_cell_not_reached = True
    # when set to False we are actually reading instructions from the second cell of
    # code, from now on we need to analyze all the cells looking for import statements
    correct_position = True
    cell = ''
    program = code.split('\n')
    for line in program:
        if not found_first_cell:
            # it ignores all the lines before the first cell generated by nbconvert(python# version ecc.)
            if line[0:5] == '# In[':
                found_first_cell = True
        elif not second_cell_not_reached:
            # starting from the second cell it saves all the instructions until it find a new cell
            if line[0:5] != '# In[':
                cell = cell + '\n' + line
            else:
                tree = ast.parse(cell)
                # once it finds a new cell it verifies if there are any imports statement in the previous cell
                if sum(isinstance(exp, ast.Import) for exp in tree.body) > 0:
                    correct_position = False
                    break
        else:
            if line[0:5] == '# In[':
                # following instructions are from the second cell of code, the first one we have to analyze
                second_cell_not_reached = False
    return correct_position


def has_linear_execution_order(notebook):
    """The function takes a dict representing notebook dictionary, it returns True if the cells are executed in
    sequential order,starting from 1, and False otherwise """
    """
        Verifies if the notebook has been run in sequential order, starting from 1

        Args:
            notebook(dic): python dictionary object representing the jupyter notebook
        Returns:
            correct_exec: boolean value that is True if notebook cells have been sequentially run top to bottom

        A way you might use me is

        linear_exec_order = has_linear_execution_order(nb_dict)
    """
    correct_exec = True
    counter = 1
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'code':
            if counter == cell['execution_count']:
                counter = counter + 1
            else:
                if cell['source']:
                    correct_exec = False
    return correct_exec


def count_class_defs(code):
    """The function takes a python code string and returns the number of class definitions"""
    """
        Extract the number of class definitions from a python code

        Args:
            code(str): string of python code
        Returns:
            class_def_num: interger value representing the number of class definitions in the python code

        A way you might use me is

        class_def_count = count_class_defs(code)
    """
    tree = ast.parse(code)
    class_def_num = sum(isinstance(exp, ast.ClassDef) for exp in tree.body)
    return class_def_num


def count_cells(nb_dict):
    """
    The function takes a dictionary representing the notebook and returns the number of cells

        Args:
            nb_dict(dict): dictionary representing the notebook
        Returns:
            len(nb_dict["cells"]): integer value representing the number of cells into the notebook

        A way you might use me is

        cells_count = count_cells(nb_dict)
    """
    return len(nb_dict["cells"])


def count_md_cells(nb_dict):
    """
    The function takes a dictionary representing the notebook and returns the number of markdown cells

        Args:
            nb_dict(dict): dictionary representing the notebook
        Returns:
            counter: integer value representing the number of markdown cells into the notebook

        A way you might use me is

        md_cells_count = count_md_cells(nb_dict)
    """
    counter = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == 'markdown':
            counter = counter + 1
    return counter


def count_code_cells(nb_dict):
    """
    The function takes a dictionary representing the notebook and returns the number of code cells

        Args:
            nb_dict(dict): dictionary representing the notebook
        Returns:
            counter: integer value representing the number of code cells into the notebook

        A way you might use me is

        code_cell_count = count_code_cells(nb_dict)
    """
    counter = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == 'code':
            counter = counter + 1
    return counter


def count_raw_cells(nb_dict):
    """
    The function takes a dictionary representing the notebook and returns the number of raw cells
    
        Args:
            nb_dict(dict): dictionary representing the notebook
        Returns:
            counter: integer value representing the number of raw cells into the notebook

        A way you might use me is

        raw_cells_count = count_raw_cells(nb_dict)
    """
    counter = 0
    for cell in nb_dict["cells"]:
        if cell["cell_type"] == 'raw':
            counter = counter + 1
    return counter


def get_bottom_md_lines_ratio(nb_dict, bottom_size=4):
    """
        Percentage of markdown rows in the last cells of the notebook out of the total of md rows

        Args: nb_dict(dict): python dictionary object representing the jupyter notebook.

        Returns: md_bottom_cells/md_first_cells: Percentage of markdown rows in the last cells of the notebook

        A way you might use me is

        last_ten_cells_md_ratio = get_bottom_md_lines_ratio(nb_dict, 10)
    """
    total_cells = count_cells(nb_dict)
    if bottom_size < total_cells / 3:
        md_first_cells = 0
        md_bottom_cells = 0
        cell_counter = 1
        for cell in nb_dict["cells"]:
            if cell_counter <= total_cells - bottom_size and cell["cell_type"] == "markdown":
                md_first_cells = md_first_cells + len(cell["source"])
            elif cell_counter > total_cells - bottom_size and cell["cell_type"] == "markdown":
                md_bottom_cells = md_bottom_cells + len(cell["source"])
            cell_counter = cell_counter + 1
    else:
        return None
    return md_bottom_cells/md_first_cells
