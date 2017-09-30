import ee
import json
import logging

from utilities import geom_utils


def _ee_biomass(geom, thresh, asset_id1, asset_id2):

    image1 = geom_utils.get_thresh_image(thresh, asset_id1)
    image2 = ee.Image(asset_id2)
    region = geom_utils.get_region(geom)

    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.sum(),
        'geometry': region,
        'bestEffort': True,
        'scale': 27
    }

    # Calculate stats 10000 ha, 10^6 to transform from Mg (10^6g) to Tg(10^12g) and 255 as is the pixel value when true.
    area_stats = image2.multiply(image1) \
        .divide(10000 * 255.0) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)

    carbon_stats = image2.multiply(ee.Image.pixelArea().divide(10000)).reduceRegion(**reduce_args)
    area_results = area_stats.combine(carbon_stats).getInfo()

    return area_results


def _execute_geojson(thresh, geojson, begin, end):
    """Query GEE using supplied args with threshold and geojson."""

    # Authenticate to GEE and maximize the deadline
    ee.Initialize()
    ee.data.setDeadline(60000)
    geojson = json.loads(geojson)
    
    # Biomass loss by year
    loss_by_year = _ee_biomass(geojson, thresh, r'HANSEN/gfw_loss_by_year_threshold_2015', r"users/davethau/whrc_carbon_test/carbon")
    logging.info('BIOMASS_LOSS_RESULTS: %s' % loss_by_year)

    # Prepare result object
    biomass_loss =  _order_loss_hist(loss_by_year, begin, end)

    return {'result': biomass_loss}


def _order_loss_hist(data, begin, end):
    return [data[str(y)] for y in range(int(begin), int(end) + 1)]


def calc_biomass_and_loss(thresh, geojson, begin, end):
    return json.dumps(_execute_geojson(thresh, geojson, begin, end))
