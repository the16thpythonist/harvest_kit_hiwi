|made-with-python| |python-version| |version|

.. |made-with-python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
   :target: https://www.python.org/

.. |python-version| image:: https://img.shields.io/badge/Python-3.8.0-green.svg
   :target: https://www.python.org/

.. |version| image:: https://img.shields.io/badge/version-0.1.0-orange.svg
   :target: https://www.python.org/

=========================================================
Harvest Time Tracking + KIT HiWi Arbeitszeitdokumentation
=========================================================

Automatically export the time you tracked with Harvest_ online time tracking tool as a KIT HiWi
Arbeitszeit Dokumentation (AZD)!

Doing the AZD can be tedious, especially if you're really bad at manual time tracking :smile: . So why
spend half an hour *every month* if I have just spent 10 hours automating the whole process for you!

Harvest_ is a free online tool to keep track of your time. Without spending any money you get 2 free
projects, access on multiple devices and full REST API functionality. This package uses the Harvest REST API
to automatically query all the tracked working hours, inserts them into the template and outputs the
final PDF completely automatically.

.. _Harvest: https://www.getharvest.com/harvest-time-tracking

* Free software: MIT license
* Documentation: https://harvest-kit-hiwi.readthedocs.io.

Features
--------

* Automatically keep track of monthly "carry over" time by creating JSON archives of past AZD's
* Optionally \*cough\* *fix* \*cough\* any working time spent on holidays or sundays
* Automatically manage the leave / vacation time each month to fit perfectly

Usage
-----

(1) Clone this repo

.. code-block:: shell

    git clone https://github.com/the16thpythonist/harvest_kit_hiwi.git

(2) Install via ``pip``:

.. code-block:: shell

    cd harvest_kit_hiwi
    pip3 install -e .

(3) Insert your Harvest account details and your personal information into the config file at
``harvest_kit_hiwi/harvest_kit_hiwi/config.yml``

(4) Use the command line interface to generate your document

.. code-block:: shell

    python3 -m harvest_kit_hiwi.cli azd [month number]

**DONE:** This will generate a PDF file with all the content from harvest! It will also create a SVG file
with the same content, which can be manually adjusted and then potentially be exported as a PDF manually.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
