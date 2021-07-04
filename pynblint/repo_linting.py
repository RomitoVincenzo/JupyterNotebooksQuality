import os
from pynblint import nb_linting


def get_duplicate_notebooks(repo):
    """
        The function takes a repository and checks whether two or more notebooks with the same filename are present.

        Args:
            repo(Repository): python object representing the repository
        Returns:
            paths: list containing paths to notebooks with duplicate filenames

        A way you might use me is

        duplicate_nb_in_repo = get_duplicate_notebooks(repo)
    """
    nb_filenames = []
    duplicate_filanames = []
    paths = []
    for notebook in repo.notebooks:
        filename = os.path.basename(notebook.path)
        if filename in nb_filenames:
            duplicate_filanames.append(filename)
        else:
            nb_filenames.append(filename)
    for filename in duplicate_filanames:
        for notebook in repo.notebooks:
            if os.path.basename(notebook.path) == filename:
                paths.append(notebook.path)
    return paths


def get_untitled_notebooks(repo):
    """
        The function takes a repository and checks whether there is any untitled notebook

        Args:
            repo(Repository): python object representing the repository
        Returns:
            untitled_notebooks: list containing paths to untitled notebooks

        A way you might use me is

        untitled_nb_in_repo = get_untitled_notebooks(repo)
    """
    untitled_notebooks = []
    for notebook in repo.notebooks:
        if not nb_linting.is_titled(notebook):
            untitled_notebooks.append(notebook.path)
    return untitled_notebooks


def get_copied_notebooks(repo):
    """
    The function takes a repository and checks whether there is any copied notebook
    Args:
        repo(Repository): python object representing the repository

    Returns:
        List: paths to copied notebooks

     A way you might use me is

        copied_nb_in_repo = get_copied_notebooks(repo)

    """
    copied_notebooks = []
    for notebook in repo.notebooks:
        if not nb_linting.is_not_copy(notebook):
            copied_notebooks.append(notebook.path)
    return copied_notebooks
