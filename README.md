# pyngw

Python client library wraper for NextGIS Web REST API operations.


python wrapper for NextGIS Web REST API. 
See comments in code


### Usage ###

```
pip install git+https://github.com/nextgis/pyngw.git

import pyngw

ngwapi = pyngw.Pyngw(ngw_url='https://sandbox.nextgis.com',login='administrator',password='demodemo')
print(ngwapi.get_childs_resources(0))

```

# Examples

## Upload QML styles by names
В NGW загружены векторные слои. Добавить к ним стили, которые лежат на диске с совпадающими названиями

```
        ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])
        ngwapi.upload_qmls_byname(group_id,'qml')

```

## Create webmap for group

```
    def create_webmap(self,group_id):
        ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])
        ngwapi.create_webmap_from_group(group_id=group_id)

 ```

## Get list of layer id for webmap

```
        ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])
         
        style_ids = ngwapi.get_styles_from_webmap_top(webmap_id) #only top-level of webmap now processed
```

## Update vector layer parameters for all layers in webmap

```
    def set_cache_4_webmap(self,webmap_id):
        payload = {"tile_cache": {
            "enabled": True,
            "image_compose": True,
            "max_z": None,
            "ttl": 60*60*24*30,
            "track_changes": False,
            "seed_z": None
          }}
 
        ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])
         
        style_ids = ngwapi.get_styles_from_webmap_top(webmap_id)
        for style_id in style_ids:
            print('update '+str(style_id)) 
            ngwapi.update_resource_payload(style_id,payload)

```

## Sort layers in webmap using text strings

```

layersorder = '''
podp_ln.qml
relef_ln.qml
dorogi_ln.qml
dorogi_pln.qml
dorsoor_ln.qml
'''


ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])

#Search for frist webmap in resource group
webmaps = ngwapi.search_by_cls(GROUP_ID,'webmap')
assert webmaps is not None
webmap = webmaps[0]

# some python text operations with list
orderlist = layersorder.replace('.qml','').splitlines()

# reorder layers in webmap
ngwapi.webmap_reorder_layers_by_list(webmap,orderlist)


```

## Upload layer using REST API

Upload geojson or shapefile zip to group 0, name will auto-generated
```
ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])

ngwapi.upload_vector_layer(filepath='data.geojson',group_id=0, display_name='')

```

## Upload layer using ogr2ogr

Upload vector layer in any ogr compatible format using ogr2ogr. Wrap for long ogr2ogr call string
```
ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])

ngwapi.upload_vector_layer_ogr2ogr(filepath = 'data.gpkg',
                                   group_id=0, 
                                   display_name = '',
                                   layer = 'boundary',
                                   geometry_type = 'MULTIPOLYGON')

```

## Upload all layers from gpkg to NextGIS WEB

```
    def upload(self,group_id,filename):
        """
        Upload all layers from GPKG to NGW using ogr2ogr
        """
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("GPKG")
        file = driver.Open(filename, 0)

        # get list of layer names + geometry type
        layers = list()
        for layer_index in range(file.GetLayerCount()):
            layer_obj = file.GetLayerByIndex(layer_index)
            layer_name = layer_obj.GetName()
            
            #get geometry_type for frist feature
            for feature in layer_obj: 
                geometry_type = feature.GetGeometryRef().GetGeometryName()
                break

            layerinfo = (layer_name, geometry_type)
            layers.append(layerinfo)
            
        del file
        del driver

        ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url=config.ngw_url,login=config.ngw_creds[0],password=config.ngw_creds[1])

        layerindex = 0
        for layerdata in layers:
            layername, geometry_type = layerdata
            print()
            print()
            print(layername,geometry_type)
            
            if geometry_type not in ('MULTIPOINT','MULTIPOLYGON'):
                 ngwapi.upload_vector_layer_ogr2ogr(filename,group_id,display_name=layername, layer = layername, geometry_type = geometry_type)
```


# Function list

## Search and helpers

* get_resource
* get_childs_resources
* search_group_by_name
* search_by_cls
* get_layers4webmap
* download_vector_layer
* get_TMS_url
* get_childs_resources
* get_styles_from_webmap_top

## Edit

* replace_qgis_style
* webmap_reorder_layers_by_list
* update_resource_payload

## Create

* create_vector_feature
* create_resource_group
* upload_vector_layer_ogr2ogr
* upload_vector_layer
* create_postgis_connection
* create_postgis_layer
* create_wms_connection
* create_wms_layer
* create_wms
* create_wfs
* upload_raster_layer
* upload_geojson
* create_raster_style
* upload_qgis_style
* create_webmap
* create_webmap_from_group
* upload_qmls_byname

# Delete

* delete_resource_by_id
* truncate_group


```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import os
from ngw_simple_api import ngw_simple_api

import pprint
pp = pprint.PrettyPrinter(indent=4)


ngwapi = ngw_simple_api.Ngw_simple_api(ngw_url='https://sandbox.nextgis.com',login='administrator',password='demodemo')

def test_ngw_webmaps():
    GROUPNAME='ngw_simple_api demo'

    # Check if NGW group exist by name, and delete it
    old_group_id = ngwapi.search_group_by_name(GROUPNAME,0)
    if old_group_id is not None:
        ngwapi.delete_resource_by_id(old_group_id)

    group_id = ngwapi.create_resource_group(parent_id=0, display_name=GROUPNAME)

    #create vector layer by upload geojson file
    layer_id = ngwapi.upload_geojson('../sampledata/sample_lines.geojson',group_id)

    #create qgis vector style by upload qml file
    style_id = ngwapi.upload_qgis_style('../sampledata/sample_lines.qml',layer_id)


    #create webmap
    webmap_children_lines=dict(layer_enabled=True,
            layer_adapter="tile",
            display_name="some_layer",
            layer_style_id=style_id,
            item_type="layer"
    )

    webmap_layers=(webmap_children_lines,webmap_children_lines)
    webmap_id = ngwapi.create_webmap(group_id=group_id,childrens=webmap_layers,display_name='webmap1')

    url = 'https://sandbox.nextgis.com/resource/{id}/update'.format(id=webmap_id)
    print('')
    print('Webmap created')
    print(url)

if __name__ == "__main__":
    test_ngw_webmaps()


```
