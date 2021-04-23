import json
import ast
from notebooktoall.transform import transform_notebook

def notebookToJson(filename):
    """The function takes the .ipynb file and returns it as a dictionary python object"""
    f=open("../TargetNotebooks/"+(filename),)
    data = json.load(f)
    f.close()
    return data

#def notebookToCode(data):
#    """The function takes the JSON of the target notebook and returns a python code string"""
#    code=[]
#    for cell in data["cells"]:
#        if cell["cell_type"] == 'code':
#            code.append(''.join(cell["source"]))
#    code = '\n'.join(code)
#    return code

def notebookToCode(filename):
    """The function takes the name of the desired .ipynb file in the target notebooks folder, and returns the python code sintax tree"""
    transform_notebook(ipynb_file="../TargetNotebooks/"+(filename), export_list=["py"])
    f = open(filename.replace(".ipynb",".py"),'r')
    py_code = f.read()
    f.close() 
    return py_code

def functionsNumber(code):
    """The function takes a python code string and returns the number of function definitions"""
    tree = ast.parse(code)
    f_num=sum(isinstance(exp, ast.FunctionDef) for exp in tree.body)
    return f_num

def notExecutedCells(notebook):
    """The function takes a dict representing a notebook and returns the number of non-executed cells"""
    not_exec_cells=0
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'code':
            if cell['execution_count']==None and cell['source']!=[]:
                not_exec_cells=not_exec_cells+1 #This is a not executed Python Cell containing actual code
    return not_exec_cells

def emptyCells(notebook):
    """The function takes a dict representing a notebook and returns the number of empty cells"""
    empty_cells=0
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'code':
            if cell['execution_count']==None and cell['source']==[]:
                empty_cells=empty_cells+1 #This is an empty Python Cell
    return empty_cells

def importsCorrectPosition(code):
    """The function takes a python code string and returns True if there are no imports other than those in the first cell of code and False otherwise"""
    found_first_cell=False #when True it means we found the first cell of code that has to be ignored
    second_cell_not_reached = True #when set to False we are actually reading instructions from the second cell of code, from now on we need to analyze all the cells looking for import statements
    imports_correct_position= True
    cell=''
    program = code.split('\n')
    for line in program:
        if found_first_cell==False: #it ignores all the lines before the first cell generated by nbconvert(python version ecc.)
            if line[0:5] == '# In[':
                found_first_cell=True
        elif second_cell_not_reached==False: #starting from the second cell it saves all the instructions until it find a new cell
            if line[0:5] != '# In[':
                cell=cell+'\n'+line
            else:
                tree = ast.parse(cell) #once it finds a new cell it verifies if there are any imports statement in the previous cell
                if sum(isinstance(exp, ast.Import) for exp in tree.body)>0:
                    imports_correct_position=False
                    break
        else:
            if line[0:5] == '# In[':
            #following instructions are from the second cell of code, the first one we have to analyze
                second_cell_not_reached=False
    return imports_correct_position

def cellsCorrectOrder(notebook):
    """The function takes a dict representing notebook dictionary, it returns True if the cells are executed in sequential order, starting from 1, and False otherwise"""
    correct_exec=True
    counter=1
    for cell in notebook["cells"]:
        if cell["cell_type"] == 'code':
            if counter==cell['execution_count']:
                counter=counter+1
            else:
                if cell['source']!=[]:
                    correct_exec=False
    return correct_exec

def classesNumber(code):
    """The function takes a python code string and returns the number of class definitions"""
    tree = ast.parse(code)
    class_def_num=sum(isinstance(exp, ast.ClassDef) for exp in tree.body)
    return class_def_num
