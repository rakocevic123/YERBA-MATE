"""Analysis code for Rakocevic & Alomenu (2026), Frontiers in Photobiology.

*Light, photoperiod and temperature drive growth, functional, and secondary
sexual dimorphism modulations in yerba mate -- New insights provided by machine
learning.*

The subpackages:

``config``      paths, experimental design constants, variable names, palettes
``io_light``    reshape the raw light campaign matrices to long format
``io_growth``   build the 90-axis x 25-month unified growth dataset
``io_physio``   load leaf gas exchange and derive the efficiency traits
``stats``       Scheirer-Ray-Hare, two-way ANOVA effect sizes, Tukey letters
``models``      gradient boosting machine fitting and permutation importance
``plotting``    shared styling and palettes used for the manuscript figures
"""
__version__ = "1.0.0"

from . import config, io_growth, io_light, io_physio, models, plotting, stats  # noqa: F401
