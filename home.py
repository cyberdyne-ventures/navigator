import os
import ast
import sys
import streamlit as st

directory = os.getcwd()  # Current working directory

def get_imported_modules(file_path):
    """
    Parse a Python file and extract all imported modules.
    """
    imported_modules = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:  # Specify utf-8 encoding
            tree = ast.parse(file.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imported_modules.append(node.module)
    except UnicodeDecodeError:
        # Handle files with unexpected encoding gracefully
        imported_modules.append(f"Error reading {file_path}: encoding issue.")
    return imported_modules

def list_imports_in_all_files(directory):
    """
    List imported modules from all Python files in the given directory.
    """
    all_imports = {}
    filenames = [f for f in os.listdir(directory) if f.endswith(".py")]
    for filename in filenames:
        file_path = os.path.join(directory, filename)
        all_imports[filename] = get_imported_modules(file_path)
    return all_imports

def run():
    st.title("Friday: A FOSS Project for AI-Assisted Threat Hunting ")
    st.markdown(
        """
        ### Sections:
        - AI Interface: Load a dataframe and ask questions about your machine learning detections or conventional detection artifacts.
        - Anomaly Detection: A simple interface for hunting outlier events in a dataframe.
        - Data Compression: A point and click interface for deduplicating rows in a dataframe.
        """
    )
    st.write("Version: 6 1212")
    st.write("System Information:")
    st.write("Python version:", sys.version)
    #st.write("Python executable:", sys.executable)
    # List imported modules
    st.markdown("Imported Modules:")
    # Get the current working directory
    directory = os.getcwd()  # Current working directory
    # List imports from all Python files in the current directory
    all_imports = list_imports_in_all_files(directory)
    for file, imports in all_imports.items():
        st.write(f"**{file}**:")
        for module in imports:
            st.write(f"- {module}")
    
