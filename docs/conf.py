"""Sphinx configuration."""
from datetime import datetime

project = "aga"
author = "Riley Shahar"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinx_click",
]

default_role = "code"

html_theme = "sphinx_rtd_theme"
