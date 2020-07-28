# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
Miscellaneous WerHiResSmoM1Italy5y model core facilities.
"""
import pandas as pd
from obspy import read_events

from ramsis.sfm.wer_hires_smo_m1_italy_5y.core.error import (WerHiResSmoM1Italy5yObspyCatalogError,
                                       WerHiResSmoM1Italy5yWellInputError)

# This file should contain utility functions that convert data from
# original format given by marshmallow parser to something the model
# can consume. These are some ideas suitable for a model implemented
# in python. in other languages, you may consider writing to a file with
# a format that may be read my your model. To maintain seperation between
# different model runs, any created files should be created in a model
# run specific folder.

def obspy_catalog_parser(xml_string):
    if isinstance(xml_string, str):
        xml_string = xml_string.encode('utf-8')
    try:
        obspy_catalog = read_events(xml_string)
    except AttributeError:
        raise WerHiResSmoM1Italy5yObspyCatalogError()
    # TODO (sarsonl) Should there be further checks on the information,
    # such as lat and lon?
    if len(obspy_catalog.events) == 0:
        raise WerHiResSmoM1Italy5yObspyCatalogError("Number of events is zero.")
    (dttime_column,
     mag_column,
     latitude_column,
     longitude_column,
     depth_column) = zip(*[(e.preferred_origin().time.datetime,
                            e.preferred_magnitude().mag,
                            e.preferred_origin().latitude,
                            e.preferred_origin().longitude,
                            e.preferred_origin().depth)
                           for e in obspy_catalog.events])
    # sort_index() is required for the model. If the index is not
    # in order, it cannot be searched and sliced.
    catalog = pd.DataFrame({'mag': mag_column,
                            'lat': latitude_column,
                            'lon': longitude_column,
                            'depth': depth_column},
                           index=dttime_column).sort_index()
    return catalog

def hydraulics_parser(well_data):
    try:
        sections_data = well_data['sections']
        # TODO (sarsonl) further checks on how many sections there are
        # and whether hydraulics exist.
        hydraulics_data = sections_data[0]['hydraulics']
    except AttributeError:
        raise WerHiResSmoM1Italy5yWellInputError()
    # Not sure at this point if topflow is the field that will be used,
    # or whether bottom flow is more correct,
    # or whether this information wil be available in the first place.
    # perhaps a calculation would have to be done in order to get flow rate.
    dttime_column, flow_column = zip(*[(h['datetime_value'],
                                        h['topflow_value'])
                                     for h in hydraulics_data])
    hydraulics = pd.DataFrame({'flow': flow_column},
                              index=dttime_column).sort_index()
    return hydraulics
