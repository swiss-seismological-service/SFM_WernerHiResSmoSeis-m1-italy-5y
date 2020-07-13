# ATLS RT-RAMSIS Model Implementation Template

This repository contains the template for implamenting a Seismicity Forecast Model
Worker (SFM-Worker). It is part of RT-RAMSIS which is an ATLS or adaptive traffic light system,
although it may be used as a stand-alone web service.

This package requires the use of the base worker package to be installed, which should be
available as a sister repository.

## Installation

Follow the installation instructions of the `ramsis.sfm.worker` (gitlab name) or
`ATLS_model_worker_base` (github name) namespace package.
You will want to rename the directory `'wer_hires_smo_m1_italy_5y'` and other instances where this tag appears
to what your chosen model name is (no spaces of course).

Each file that requires alteration should contain instructions on what to alter.
I would go through the following files in order, renaming the model as required:

* ramsis/sfm/wer_hires_smo_m1_italy_5y/schema.py (model specific inputs defined)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/settings.py (defaults defined)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/server/model_adaptor.py (data conversions, formatting and further validation)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/core/utils.py (utililty functions used by model_adaptor)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/core/wer_hires_smo_m1_italy_5y_model.py (actual model code should go here)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/core/error.py (error classes defined)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/tests/test_reimplementation.py (write tests)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/server/v1/routes.py (api configuration)
* ramsis/sfm/wer_hires_smo_m1_italy_5y/server/app.py (app is defined, renaming required)
* setup.py
* README.md
* Any __init__.py files that contain the model name
* sphinx documentation


Once you are happy to try out the package, invoke:

```
$ pip install -e .
```

Postman tests were setup for the WerHiResSmoM1Italy5y API, these can be imported from a json file under
/pm and modified. These API tests are quite useful for end-to-end testing of the API
as well as trying different input parameters in a user friendly way.

## User documentation
The user documentation can be found in the Sphinx documentation under docs/


###To be removed when docker container properly set up for this...

This worker requires a POSTGIS postgresql database to be setup on the system.
If postgresql is installed, create a database (have called db ramsis, username and password also the same, in example) enable the postgis extension.

$ ramsis-sfm-worker-db-init --logging-conf path/to/ramsis.sfm.`<insert_model_name>`/config/logging.conf  postgresql://ramsis:ramsis@localhost:5432/ramsis

Then to start model worker:
$ ramsis-sfm-worker-`<insert_model_name>` --logging-conf path/to/ramsis.sfm.`<insert_model_name>`/config/logging.conf postgresql://ramsis:ramsis@localhost:5432/ramsis
