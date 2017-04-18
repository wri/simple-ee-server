import ee
import os
import json
import logging
import sys


def _get_thresh_image(thresh, asset_id):
    """Renames image bands using supplied threshold and returns image."""
    image = ee.Image(asset_id)

    # Select out the gain band if it exists
    if 'gain' in asset_id:
        before = image.select('.*_' + thresh, 'gain').bandNames()
    else:
        before = image.select('.*_' + thresh).bandNames()

    after = before.map(
        lambda x: ee.String(x).replace('_.*', ''))

    image = image.select(before, after)
    return image

def _get_type(geojson):
    if geojson.get('features') is not None:
        return geojson.get('features')[0].get('geometry').get('type')
    elif geojson.get('geometry') is not None:
        return geojson.get('geometry').get('type')
    else:
        return geojson.get('type')

def _get_region(geom):
    """Return ee.Geometry from supplied GeoJSON object."""
    poly = _get_coords(geom)
    ptype = _get_type(geom)
    if ptype.lower() == 'multipolygon':
        region = ee.Geometry.MultiPolygon(poly)
    else:
        region = ee.Geometry.Polygon(poly)
    return region


def _ee(geom, thresh, asset_id):
    image = _get_thresh_image(thresh, asset_id)
    region = _get_region(geom)

    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.sum(),
        'geometry': region,
        'bestEffort': False,
        'scale': 27.829872698318393,
        'maxPixels': 1e9
    }

    # Calculate stats
    area_stats = image.divide(10000 * 255.0) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)
    area_results = area_stats.getInfo()

    return area_results


def _get_coords(geojson):
    if geojson.get('features') is not None:
        return geojson.get('features')[0].get('geometry').get('coordinates')
    elif geojson.get('geometry') is not None:
        return geojson.get('geometry').get('coordinates')
    else:
        return geojson.get('coordinates')
            
            
def _order_loss_hist(data, begin, end):
    return [data[str(y)] for y in range(int(begin), int(end) + 1)]


def _execute_geojson(thresh, geojson, begin, end):
    """Query GEE using supplied args with threshold and geojson."""

    # Authenticate to GEE and maximize the deadline
    ee.Initialize()
    ee.data.setDeadline(60000)

    # Loss by year
    loss_by_year = _ee(geojson, thresh, 'HANSEN/gfw_loss_by_year_threshold_2015')
    logging.info('LOSS_RESULTS: %s' % loss_by_year)

    loss = _order_loss_hist(loss_by_year, begin, end)

    return {'result': loss}

    
def calc_loss(thresh, geojson, begin, end):
    return json.dumps(_execute_geojson(thresh, geojson, begin, end))
    
    
if __name__ == '__main__':
    geojson = {"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-56.832275390625,-21.637005211106306],[-57.3651123046875,-22.715390019335942],[-56.4,-23.49347666096087],[-55.2504545454,-22.649502094242195],[-55.8599853515625,-21.058870866501525],[-56.832275390625,-21.637005211106306]]]}}]}

    thresh = '30'
    start = '2001'
    end = '2010'
    
    print json.dumps(_execute_geojson(thresh, geojson, start, end))
