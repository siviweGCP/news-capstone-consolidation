"""Sphinx configuration for the News Application documentation."""

import os
import sys

import django

sys.path.insert(0, os.path.abspath("../.."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_project.settings")
django.setup()

project = "News Application Consolidation"
author = "Siviwe Ngwilingwili"
copyright = "2026, Siviwe Ngwilingwili"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = []
exclude_patterns = []
html_theme = "alabaster"
html_static_path = []
autodoc_member_order = "bysource"
