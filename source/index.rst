.. abm_liv documentation master file, created by
   sphinx-quickstart on Thu Nov 21 15:18:44 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
.. _abm_liv: https://github.com/cjber/abm_liv
.. role:: bash(code)
   :language: bash

abm_liv Documentation
=====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Developer Guide
===============

This guide provides information for both contributing to the abm_liv project, and for adjusting the existing program to suit your own needs.

Contributing on GitHub
----------------------

Here are the basic steps required to contribute to existing code.

1. Install :bash:`git` on your system.
2. Fork the abm_liv_ repository to your GitHub account and get the source code using::

    git clone https://github.com/<your_username>/abm_liv
    cd abm_liv

3. Run tests?


Customising the Code
--------------------

The program has been written to provide several simplistic methods for customisation as the user requires. Some basic customisation has been self contained within the :bash:`main.py` script.

* Customising the geographic area of interest.

   - The :bash:`bounds` variable reads a shapefile called :bash:`bounds.gpkg` contained within the :bash:`data` directory. This file may be changed by placing a different Geopackage polygon in this location with a matching name. Note that for the model to run, the :bash:`data_clean.py` script must be ran first.

   - Additionally, a :bash:`*.shp` polygon may be used, but the name and location must be edited when the :bash:`bounds` variable is assigned in both the :bash:`main.py`, :bash:`data_clean.py` and :bash:`api.py` scripts.

* Adding Class level functions.
   - Additional functions may be added to either the :bash:`crime.py` or :bash:`police.py` scripts. These should be contained within the respective class and appended below existing functions.

An example function added to the :bash:`crime.py` crime Class could take the form::

     def shift(self):
        if random.random < 0.5:
            self.x + 1
            self.y + 1

This would cause a crime to randomly move a small distance every so often. This function should then be added to the :bash:`update` function in the :bash:`main.py` script. In the section::

    for c in self.crime_list:
        c.solve(self.police_list)


