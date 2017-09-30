import ee
import json

from utilities import geom_utils


def _ee(geom, thresh, asset_id, begin, end):
    image = geom_utils.get_thresh_image(thresh, asset_id)
    region = geom_utils.get_region(geom)

    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.sum().unweighted(),
        'geometry': region,
        'bestEffort': True,
        'scale': 27.829872698318393,
        'maxPixels': 1e13
    }

    # grab the last two chars and convert to int
    begin = int(begin[2:])
    end = int(end[2:])

    loss_area_img = image.gte(begin).And(image.lte(end)).multiply(ee.Image.pixelArea())

    # Calculate stats
    area_results = loss_area_img.reduceRegion(**reduce_args).getInfo()

    # grab results from the first (and only) band
    band_id = area_results.keys()[0]

    loss_ha = area_results[band_id] / 10000

    return loss_ha


def _execute_geojson(thresh, geojson, begin, end):
    """Query GEE using supplied args with threshold and geojson."""

    # Authenticate to GEE and maximize the deadline
    ee.Initialize()
    ee.data.setDeadline(60000)

    # Loss by year
    asset = 'projects/wri-datalab/HansenComposite_16'
    loss = _ee(geojson, thresh, asset, begin, end)
    print 'LOSS_RESULTS: %s' % loss

    return {'loss': loss}

    
def calc_loss(thresh, geojson, begin, end):
    return json.dumps(_execute_geojson(thresh, geojson, begin, end))

