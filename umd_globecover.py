import ee
import os
import json
import logging
import sys

# source: https://code.earthengine.google.com/75f17d0ce29c96d62ff533963eec1fc5                                  

def _get_thresh_image(thresh, asset_id):
    """Renames image bands using supplied threshold and returns image."""
    image = ee.Image(asset_id)
    
    band_name = 'loss_{}'.format(thresh)
   
    return image.select(band_name)

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


def _ee_globcover(geom, thresh, asset_id1, asset_id2):

    image1 = _get_thresh_image(thresh, asset_id1)
    image2 = ee.Image(asset_id2).select('landcover')
    region = _get_region(geom)

    group_args = {"groupField": 1, "groupName": 'globe_cover_val'}
    
    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.histogram().unweighted().group(**group_args),
        'geometry': region,
        'bestEffort': True,
        'scale': 27.829872698318393
    }
    
    area_stats = image1.addBands(image2).reduceRegion(**reduce_args).getInfo()

    return area_stats


def _get_coords(geojson):
    if geojson.get('features') is not None:
        return geojson.get('features')[0].get('geometry').get('coordinates')
    elif geojson.get('geometry') is not None:
        return geojson.get('geometry').get('coordinates')
    else:
        return geojson.get('coordinates')


def _execute_geojson(thresh, geojson, begin, end):
    """Query GEE using supplied args with threshold and geojson."""

    # Authenticate to GEE and maximize the deadline
    ee.Initialize()
    ee.data.setDeadline(60000)
    #geojson = json.loads(geojson)
    
    # Loss and globcover histogram
    loss_and_lulc = _ee_globcover(geojson, thresh, r'projects/wri-datalab/HansenComposite_14-15', r"ESA/GLOBCOVER_L4_200901_200912_V2_3")
    
    logging.info('Loss_and_LULC histograms: %s' % loss_and_lulc)

    # Prepare result object
    result_dict = _format_response(loss_and_lulc, begin, end)

    return {'result': result_dict}

def _format_response(data, begin, end):

    requested_years = range(int(begin), int(end) + 1)

    final_dict = {}

    for row in data['groups']:
        
        globe_cover_val = row['globe_cover_val']
        
        bucket_list = row['histogram']['bucketMeans']
        count_list = row['histogram']['histogram']
        data_pairs = zip(bucket_list, count_list)
        
        # remove zeros
        data_pairs = [(2000 + int(bucket), int(count)) for bucket, count in data_pairs if (int(bucket) != 0 and int(count) != 0)]
        
        final_dict[globe_cover_val] = {year: count for year, count in data_pairs if year in requested_years}

    return final_dict

def calc_globecover(thresh, geojson, begin, end):
    return json.dumps(_execute_geojson(thresh, geojson, begin, end))
    
if __name__ == '__main__':

    geojson = json.dumps({"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-56.832275390625,-21.637005211106306],[-57.3651123046875,-22.715390019335942],[-56.4,-23.49347666096087],[-55.2504545454,-22.649502094242195],[-55.8599853515625,-21.058870866501525],[-56.832275390625,-21.637005211106306]]]}}]})

    thresh = '30'
    start = '2001'
    end = '2005'
    
    print json.dumps(_execute_geojson(thresh, geojson, start, end))