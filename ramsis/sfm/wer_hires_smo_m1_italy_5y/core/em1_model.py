"""
WerHiResSmoM1Italy5y model code that uses hydraulic borehole data and a seismicity catalog
to forecast the number of events above a certain magnitude based on a
hydraulics plan.
"""

# Note: Please change all references to WerHiResSmoM1Italy5y, wer_hires_smo_m1_italy_5y to what your model name
# abbreviation should be.

# This model has been implemented in python, however it is not required
# to be in python. If it is in another language, a system call will probably
# be made from the ../server/model_adaptor.py to your model. Your model
# may require alterations to what data is available from RAMSIS, so the
# example model adaptor may provide a guide to you on what default
# functions are availble.
import os.path as path
import xml.etree.ElementTree as ET
import argparse
import logging
from datetime import datetime

from ramsis.sfm.wer_hires_smo_m1_italy_5y.core.error import (SeismicEventThresholdError,
                                       NegativeVolumeError)

LOGGER = 'ramsis.sfm.wer_hires_smo_m1_italy_5y_model'
NAME = 'WerHiResSmoM1Italy5yMODEL'
logger = logging.getLogger(LOGGER)
ABS_PATH = path.dirname(path.realpath(__file__))
PARENT_ABS_PATH = path.dirname(ABS_PATH)

class ResultLocator:
    def __init__(self, tag_url="{http://www.scec.org/xml-ns/csep/forecast/0.1}", xml_filename="werner.HiResSmoSeis-m1.italy.5yr.xml"):
        tree = ET.parse(path.join(PARENT_ABS_PATH, xml_filename))
        root = tree.getroot()
        cell_dimension_element = root.find(f"./{tag_url}forecastData/{tag_url}defaultCellDimension")
        self.lon_increment = float(cell_dimension_element.get('lonRange'))
        self.lat_increment = float(cell_dimension_element.get('latRange'))
        print("increment", self.lon_increment, self.lat_increment)
        cells = root.findall(f"./{tag_url}forecastData/{tag_url}depthLayer/{tag_url}cell")
        #print("cells", len(cells))
        self.mag_list = [element.get('m') for element in list(cells[0])]
        #print(self.mag_list)
        df_columns = ["lon", "lat"].extend(self.mag_list)
        dict_list = []
        for cell in cells:
            row_dict = {element.get('m'): float(element.text) for element in cell.iter() if element.get('m')}
            row_dict["lon"] = float(cell.get('lon'))
            row_dict["lat"] = float(cell.get('lat'))
            dict_list.append(row_dict)
        self.results_df = pd.DataFrame.from_dict(dict_list)
        #print(len(self.results_df), self.results_df.iloc[0])
        self.cell_area = self.lon_increment * self.lat_increment
    def cell_search(self, min_lon, max_lon,
                    min_lat, max_lat, grid_match=True):
        if grid_match:
            # Cater for original csep case in a more time efficient way.
            lon = (min_lon + max_lon) / 2
            lat = (min_lat + max_lat) / 2
            mask_lon = self.results_df['lon'].values == lon
            mask_lat = self.results_df['lat'].values == lat
            row = self.results_df[mask_lon & mask_lat]
            assert len(row) in [0, 1], (f"One or zeros rows expected: "
                                        "{len(row)} rows returned")
            return [1.0, row]
        else:
            # return all cells that have overlapping area

            mask_grid = (self.results_df['lon'].values >= min_lon &
                         self.results_df['lon'].values < max_lon &
                         self.results_df['lat'].values >= min_lat &
                         self.results_df['lat'].values < max_lat)
            rows = self.results_df[mask_grid]
            return rows


#### Implement model
# Read xml file into structure searchable by lat, lon.
# for bin in reservoir, check minlat, minlon, maxlat, maxlon
# against data by returning datapoints that overlap with region
# and the fraction of overlap.
#
# Write data to various arrays.





# Please see ../server/model_adaptor.py for where this is called
# What inputs are requires are entirely dependant on model.
def exec_model(mag_bin_list,
               epoch_duration,
               reservoir_geom,
               datetime_start,
               datetime_end):
    """
    Run the model training and forecast stages.

    :param datetime_start: Start of period to forecast.
    :param datetime_end: End of period to forecast.
    :param epoch_duration: Number of seconds between returned forecast
        rate values.
    # TODO

    :rtypes: (a) float, (b) float, (mc) float, (forecast_values) pd.DataFrame
    """
    forecast_values = forecast_seismicity(
        a, b, mc, hydraulics_plan, datetime_start,
        datetime_end, epoch_duration,
        last_hydraulic_row=last_hydraulic_row)
    logger.info("Completed forecast")
    return a, b, mc, forecast_values

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%s")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('datetime_start', type=valid_date,
                        help='Start date for forecast, YYYYmmDDTHHMMss')
    parser.add_argument('datetime_end', type=valid_date,
                        help='End date for forecast, YYYYmmDDTHHMMss')
    parser.add_argument('epoch_duration', type=float,
                        help='Time between forecasts in seconds')
    args = parser.parse_args()
    return args


# It is not required to make the file executable, however nice to have for running
# independently.
if __name__ == "__main__":
    args = parseargs()
    results = exec_model(args.datetime_start,
                         args.datetime_end,
                         args.epoch_duration)
