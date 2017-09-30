import ee
import json
import logging

from utilities import geom_utils


def _ee_globcover(geom, thresh, asset_id1, asset_id2):

    image1 = geom_utils.get_thresh_image(thresh, asset_id1)
    mask_image1 = image1.mask()
    
    image2 = ee.Image(asset_id2).select('landcover')
    combine_image = image1.multiply(500).add(image2.updateMask(mask_image1))

    # combine_image = ee.Image(asset_id2).select('landcover')
    combine_image = combine_image.addBands([ee.Image.pixelArea()])
    
    region = geom_utils.get_region(geom)
    
    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.frequencyHistogram().unweighted().group(),
        'geometry': region,
        'bestEffort': False,
        'scale': 27.829872698318393,
        'maxPixels': 1e13
    }
    
    area_stats = combine_image.reduceRegion(**reduce_args).getInfo()
    # print area_stats

    return area_stats


def _execute_geojson(thresh, geojson, begin, end):
    """Query GEE using supplied args with threshold and geojson."""

    # Authenticate to GEE and maximize the deadline
    ee.Initialize()
    ee.data.setDeadline(60000)
    
    # Loss and globcover histogram
    loss_and_lulc = _ee_globcover(geojson, thresh, r'projects/wri-datalab/HansenComposite_16', r"ESA/GLOBCOVER_L4_200901_200912_V2_3")
    
    logging.info('Loss_and_LULC histograms: %s' % loss_and_lulc)
    
    area_stats = flatten_area_hist(loss_and_lulc)
    print area_stats

    # Prepare result object
    result_dict = _format_response(area_stats, begin, end)

    return {'result': result_dict}


def _format_response(data, begin, end):

    requested_years = range(int(begin), int(end) + 1)
    
    globcover_vals = [11, 14, 20, 30, 40, 50, 60, 70, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230]

    empty_year_dict = {year: 0 for year in requested_years}
    final_dict = {val: empty_year_dict.copy() for val in globcover_vals}

    for combine_value, count in data.iteritems():

        if combine_value != 'null':
        
            year = 2000 + int(combine_value) / 500
            globcover = int(combine_value) % 500
            
            if year in requested_years:
                final_dict[globcover][year] = count

    return final_dict


def calc_globecover(thresh, geojson, begin, end):
    return json.dumps(_execute_geojson(thresh, geojson, begin, end))
    

def flatten_area_hist(area_hist):
    out_dict = {}

    for output_group in area_hist['groups']:
        lulc_val = output_group['group']
        m2_val = 0
        
        for pixel_size, pixel_count in output_group['histogram'].iteritems():
            m2_val += float(pixel_size) * pixel_count

        # convert m2 to ha
        out_dict[lulc_val] = m2_val / 10000

    print out_dict
        
    return out_dict
