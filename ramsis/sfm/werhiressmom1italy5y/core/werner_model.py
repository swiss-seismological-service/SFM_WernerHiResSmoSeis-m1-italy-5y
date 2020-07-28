"""
WerHiResSmoM1Italy5y model code that maps results from an XML file
to a spatial grid.
"""
import os.path as path
import pandas as pd
import xml.etree.ElementTree as ET
import logging
from numpy import round as nround
from numpy import arange

LOGGER = 'ramsis.sfm.wer_hires_smo_m1_italy_5y_model'
NAME = 'WerHiResSmoM1Italy5yMODEL'
logger = logging.getLogger(LOGGER)
ABS_PATH = path.dirname(path.realpath(__file__))
PARENT_ABS_PATH = path.dirname(ABS_PATH)
MAGNITUDE_COMPLETENESS = 1.0 ### dummy value, find what this should be # noqa

class ResultLocator:
    """ Class to translate model results from an xml file
    to a data format that is searchable by result location.
    """

    def __init__(
            self, tag_url="{http://www.scec.org/xml-ns/csep/forecast/0.1}",
            xml_filename="werner.HiResSmoSeis-m1.italy.5yr.xml"):
        logger.info(f"Loading xml file: {xml_filename}")
        tree = ET.parse(path.join(ABS_PATH, xml_filename))
        root = tree.getroot()

        # Depth element of model.
        cell_depth_element = root.find(
            f"./{tag_url}forecastData/{tag_url}depthLayer")

        # Reverse the direction of depth to altitude
        self.max_depth_km = -float(cell_depth_element.get('min'))
        self.min_depth_km = -float(cell_depth_element.get('max'))

        cell_dimension_element = root.find(
            f"./{tag_url}forecastData/{tag_url}defaultCellDimension")
        self.lon_increment = float(cell_dimension_element.get('lonRange'))
        self.lat_increment = float(cell_dimension_element.get('latRange'))

        self.lon_add = float(cell_dimension_element.get('lonRange')) / 2.0
        self.lat_add = float(cell_dimension_element.get('latRange')) / 2.0

        # List of available magnitudes in model.
        cells = root.findall(
            f"./{tag_url}forecastData/{tag_url}depthLayer/{tag_url}cell")
        self.mag_list = [element.get('m') for element in list(cells[0])]

        # Create dataframe containing all information
        dict_list = []
        for cell in cells:
            row_dict = {element.get('m'): float(element.text)
                        for element in cell.iter() if element.get('m')}
            row_dict["lon"] = float(cell.get('lon'))
            row_dict["lat"] = float(cell.get('lat'))
            dict_list.append(row_dict)
        self.results_df = pd.DataFrame.from_dict(dict_list)
        logger.info("Successfully loaded xml file")

        self.cell_area = self.lon_increment * self.lat_increment
        self.lon_min = self.results_df['lon'].min()
        self.lon_max = self.results_df['lon'].max()
        self.lat_min = self.results_df['lat'].min()
        self.lat_max = self.results_df['lat'].max()

    def cell_search(self, min_lon, max_lon,
                    min_lat, max_lat, grid_match=True):
        """ Search through dataframe for result cells that overlap
        with the submitted area. If grid_match then assume that there
        is only one result cell that matches, and reduce the search time.


        Creates a new dataframe containing single row. This row contains
        the expectation value information that has been averaged from
        overlapping cells. The contribution from each overlapping cell
        is weighted by the overlapping fractional area.

        :param min_lon: minimum longitude of search area, inclusive, degrees.
        :param max_lon: max longitude of search area, not-inclusive of
            value, degrees.
        :param min_lon: minimum latitude of search area, inclusive, degrees.
        :param min_lon: maximum latitude of search area, non-inclusive of
            value, degrees.
        """
        result_row_df = pd.DataFrame(
            {"min_lon": min_lon, "max_lon": max_lon,
             "min_lat": min_lat, "max_lat": max_lat, "overlap": 1.0},
            index=[0])
        if grid_match:
            # Cater for original csep case in a more time efficient way.
            lon = round(min_lon + self.lon_add, 2)
            lat = round(min_lat + self.lat_add, 2)
            mask_lon = self.results_df['lon'].values == lon
            mask_lat = self.results_df['lat'].values == lat
            result = self.results_df[mask_lon & mask_lat]
            assert len(result) in [0, 1], ("One or zeros rows expected: "
                                           f"{len(result)} rows returned")
            if result.empty:
                return None
            else:
                result.drop(columns=['lat', 'lon'], axis=1)
                result.reset_index(drop=True, inplace=True)
                retval = pd.concat([result_row_df, result], axis=1)
                return retval

        else:
            result_area = (max_lon - min_lon) * (max_lat - min_lat)
            # return all cells that have overlapping area
            mask_grid = (
                ((self.results_df['lon'].values + self.lon_add) >= min_lon) & # noqa
                ((self.results_df['lon'].values - self.lon_add) < max_lon) & # noqa
                ((self.results_df['lat'].values + self.lat_add) >= min_lat) & # noqa
                ((self.results_df['lat'].values - self.lat_add) < max_lat)) # noqa
            result = self.results_df[mask_grid].copy()
            if result.empty:
                return None

            result['overlap'] = 0.0
            # Calculate fractional overlap of each grid cell with
            # result area
            for ind, row in result.iterrows():
                row_min_lon = row['lon'] - self.lon_add
                row_max_lon = row['lon'] + self.lon_add
                row_min_lat = row['lat'] - self.lat_add
                row_max_lat = row['lat'] + self.lat_add
                dx = min(max_lon, row_max_lon) - max(min_lon, row_min_lon)
                dy = min(max_lat, row_max_lat) - max(min_lat, row_min_lat)
                area = dx * dy
                if area > 0.0:
                    row['overlap'] = area / result_area
                else:
                    result.drop(index=ind, inplace=True)
            # find weighted average of all expectation values that
            # overlap area
            result[self.mag_list] = result[self.mag_list].multiply(
                result['overlap'], axis="index")
            result = result.sum()

            # Around edges, have assumed nearest expectation is valid
            # Confirm if correct, or if interpolating with zero expectation
            # value is more correct? In this case, remove next line.
            result = result / result['overlap']
            result.drop(columns=['lat', 'lon'], axis=1)
            assert len(result) in [0, 1], (
                f"One or zeros rows expected: {len(row)} rows returned")
            return pd.concat([result_row_df, result], axis=1)

    def validate_reservoir(self, reservoir):
        """ Validate the input reservoir information
        against the information from the xml file.

        Asserts that the depth interval that is searched for
        is fully within the results area.
        :param reservoir: dict keys [x, y, z] describe edges
            of searched for result areas.
        """
        depth_list = reservoir['z']
        assert min(depth_list) <= self.min_depth_km * 1000.
        assert max(depth_list) >= self.max_depth_km * 1000.


def check_grid_match(reservoir_geom, lon_min, lon_max, lon_inc,
                     lat_min, lat_max, lat_inc):
    """ Check whether queried results grid matches the results
    grid available from the xml file.
    Right now, this only checks if the two grids are identical,
    and does not check whether one grid has same resolution
    but is of a different total dimension.

    :param reservoir_geom: dict keys: [x, y, z] each element contains
        a list of values describing the edges of the forecast areas.
    :param lon_min: minimum longitude of xml result.
    :param lon_max: maximum longitude of xml result.
    :param lat_min: minimum longitude of xml result.
    :param lat_max: maximum longitude of xml result.

    :rtype: Bool describing whether thegrid matches.
    """
    model_lon_list = nround(arange(lon_min, lon_max, lon_inc), 2).\
        tolist()
    model_lat_list = nround(arange(lat_min, lat_max, lat_inc), 2).\
        tolist()

    # compare with reservoir geom
    compare_lon = reservoir_geom['x'] == model_lon_list
    compare_lat = reservoir_geom['y'] == model_lat_list
    # Figure out what to do for non-matching depths
    # where depth within range, allow and scale expected
    # values accordingly
    # where depth values are out of range, return full
    # expected value?
    grid_match = True
    if not compare_lon:
        logger.warn("input longitudes do not match model longitudes"
                    "new_grid will be generated")
        grid_match = False
    if not compare_lat:
        logger.warn("input latitudes do not match model latitudes"
                    "new_grid will be generated")
        grid_match = False
    return grid_match

def forecast_scaling(returned_df, mag_column_names):
    # The database stores values in a values per year format,
    # so simply divide by 5. Openquake will do the scaling over time.
    returned_df[mag_column_names] = returned_df[mag_column_names] * 0.2 # noqa
    return returned_df


def exec_model(reservoir_geom):
    """
    Access model results
    """
    # Initialize class from xml data for easy data access
    result_locator = ResultLocator()
    result_locator.validate_reservoir(reservoir_geom)

    returned_df = pd.DataFrame(
        columns=["min_lon", "max_lon", "min_lat", "max_lat", "overlap"].extend(
            result_locator.mag_list))
    grid_match = check_grid_match(reservoir_geom,
                                  result_locator.lon_min,
                                  result_locator.lon_max,
                                  result_locator.lon_increment,
                                  result_locator.lat_min,
                                  result_locator.lat_max,
                                  result_locator.lat_increment)
    logger.info("Check if the grid matches the original model grid: "
                f"{grid_match}")

    logger.info("Starting results collection for input spatial grid")
    min_lon = round(reservoir_geom['x'][0] - result_locator.lon_add, 2)
    min_lat = round(reservoir_geom['y'][0] - result_locator.lat_add, 2)

    for lon in reservoir_geom['x'][:-1]:
        max_lon = round(lon + result_locator.lon_add, 2)
        for lat in reservoir_geom['y'][:-1]:
            max_lat = round(lat + result_locator.lat_add, 2)
            cell_results = result_locator.cell_search(
                min_lon, max_lon, min_lat, max_lat, grid_match=grid_match)
            if cell_results is None:
                pass
            else:
                returned_df = pd.concat([returned_df, cell_results],
                                        ignore_index=True)
            min_lat = max_lat
        min_lon = max_lon

    # Scale by forecast time from 5 year value to one year value
    returned_df = forecast_scaling(returned_df,
                                   result_locator.mag_list)
    mc = MAGNITUDE_COMPLETENESS
    logger.info(f"Successfully returning {len(returned_df)} subgeometries "
                "from model.")
    depth_km = abs(result_locator.max_depth_km - result_locator.min_depth_km)
    return returned_df, result_locator.mag_list, mc, depth_km
