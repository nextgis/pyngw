# pyngw

Python client library wraper for NextGIS Web REST API operations.


python wrapper for NextGIS Web REST API.
See comments in code


### Usage ###

```
pip install --upgrade --force-reinstall git+https://github.com/nextgis/pyngw.git
```
```
import pyngw

ngwapi = pyngw.Pyngw(ngw_url = 'https://sandbox.nextgis.com', login = 'administrator', password = 'demodemo')
print(ngwapi.get_childs_resources(0))
```


# Function list

## Connect to NextGIS Web

### Connect with password
* ngwapi = pyngw.Pyngw(ngw_url = 'https://sandbox.nextgis.com', login = 'administrator', password = 'demodemo')
### Connect as guest
* ngwapi = pyngw.Pyngw(ngw_url = 'https://sandbox.nextgis.com') 

## Check URL

* check_resource_id(resource_id) -> bool
  	return True if id exist in ngw
* check_ngw_url() -> bool
  	return True if ngw answer on URL provided in pyngw constructor
 	
## Get 

* get_resource(resource_id) -> dict 
	wraper for query GET
* get_childs_resources(resource_group_id) 
	Get child resources of parent resource: resource group, or layer with styles. wraper for query GET ?parent= 
* get_childs_ids_recursive(resource_id) -> list 
    return list of ids of resources element tree. Usedul for batch change resources
* get_feature_count(layer_id) -> int
  	Obtain count of features in vector layer
* get_features(self,resource_id:int,params:str='')->list:
* get_TMS_url(resource_id) -> str
  	Get URL of Tile Map Service protocol for map style
* get_styles_from_webmap_top
* download_ngw4qgis(group_id,target_path, overwrite=False,use_latest_qml=True, intersects=wkt_string)

## Search

* get_resource_id_by_name(name,group_id=0) -> int
	read resource names in group_id, returns id of frist found resource with this name.
* search_resource_by_name(name,group_id=0,cls='') -> list	
	   Search by name with wildcards, not using api method /search. Returns list of dicts.
* search_by_cls(group_id=0,cls='webmap') -> list
* get_layers4webmap(group_id,namesource='',layer_adapter='tile') -> dict  # Return list with layers for create_webmap
* download_vector_layer(path,layer_id,format='geojson',srs=4326,zipped=False)
	Download NextGIS Web vector layer as GeoJSON or GeoPackage file
* download_qgis_style(path,style_id)
    download vector layers from resource group as gpkg files and one qml style. qml style will saved as filename same as layer, so you can open all gpkg in qgis


## Edit

* replace_qgis_style(filepath,style_id) -> dict
* webmap_reorder_layers_by_list(webmap_id, orderlist) -> bool
* update_resource_payload(resource_id,payload,skip_errors=True)
* webmap_set_extent_by_layer(webmap_id,layer_id) -> bool
* replace_vector_layer(old_display_name,group_id,filepath) -> int

## Create

* create_vector_feature(layer_id,geom,fields)->int
* create_vector_features_ogr(layer_id, filepath, page_size=100)->bool # Copy features from vector file to ngw. Require GDAL Python bingings. 
* create_resource_group(parent_id=0, display_name='') #can generate random group name, useful for developing)
* create_vector_layer(group_id,display_name,geometry_type,fields)
* upload_vector_layer_tus(parent_id=0, display_name='') #Using tus.io protocol
* upload_vector_layer_ogr2ogr(filepath,group_id,display_name='',layer=None, geometry_type = None)
* upload_vector_layer(filepath,group_id, display_name='',
            cast_is_multi=True,
            cast_has_z=False,
            skip_other_geometry_types=True,
            fix_errors='LOSSY',
            skip_errors=True,
            fid_source='AUTO',
            fid_field=None) #same arguments as on https://docs.nextgis.com/docs_ngweb_dev/doc/developer/create.html#create-vector-layer
* create_postgis_connection
* create_postgis_layer
* create_wms_connection
* create_wms_layer
* create_wms
* create_wfs
* create_raster_style
* create_webmap(group_id,childrens,display_name='') #create webmap from list of children, as return from ngw REST API
* create_webmap_from_group(group_id,display_name='')
* upload_raster_layer(filepath, group_id, display_name = '') -> int
    Note: this library not implemented create raster layer with nextgisweb lunkwill, see https://github.com/nextgis/ngw_external_api_python
* upload_qgis_style(filepath,layer_id,display_name='')
* upload_qmls_byname(resource_group_id,qml_path) #for each layer in group, upload qml file with exact name +.qml

# Delete

* delete_resource_by_id(resource_id)
* truncate_group(group_id)
* truncate_layer(layer_id)
* delete_features(resource_id:int,ids:list)



# Examples

## Get python dict description of resource

```
ngwapi.get_resource(resource_id)
```
```
ngwapi.get_childs_resources(resource_id)
```


## Upload QML styles by names
В NGW загружены векторные слои. Добавить к ним стили, которые лежат на диске с совпадающими названиями

```
 ngwapi.upload_qmls_byname(group_id,'qml')
```

## GET TMS url

```
ngwapi.get_TMS_url(style_id)

http://trolleway.nextgis.com/api/component/render/tile?z={z}&x={x}&y={y}&resource=72
```


## Create webmap for group

```
        ngwapi.create_webmap_from_group(group_id=group_id)
 ```

## Get list of layer id for webmap

```
        style_ids = ngwapi.get_styles_from_webmap_top(webmap_id) #only top-level of webmap now processed
```
## Set some parameters for all resources in group with some cls

```
group_id = 936
svg_marker_library = 853
layers = ngwapi.get_childs_resources(group_id)

change_payload = {'qgis_vector_style':{'svg_marker_library':{'id':svg_marker_library}}}

for layer in layers:   
    subs = ngwapi.get_childs_resources(layer['resource']['id'])
    for sub in subs:
        if sub['resource']['cls'] == 'qgis_vector_style':
            print(sub['resource']['display_name'])
            ngwapi.update_resource_payload(sub['resource']['id'],change_payload)

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
ngwapi.upload_vector_layer(filepath='data.geojson',group_id=0, display_name='')

```

## Upload layer using ogr2ogr

Upload vector layer in any ogr compatible format using ogr2ogr. Wrap for long ogr2ogr call string
```

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

## Create empty vector layers

```
fields=[{"datatype":"STRING","display_name":"fld1","keyname":"fieldname1"}]
new_id = ngwapi.create_vector_layer(group_id=0,display_name = 'layer ' + ngwapi.generate_name(),geometry_type='LINESTRING',fields=fields)

print(new_id)

```


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

## Search resources

Two functions for search:

- get_resource_id_by_name(name,group_id): return id of frist found resource
- search_resource_by_name(name,group_id=0,cls=''): returns list of dicts, or empty list. Accepted wildcards: `*` `?`, see https://docs.python.org/3/library/fnmatch.html for refrence

```
import pyngw
ngwapi = pyngw.Pyngw(ngw_url = 'https://sandbox.nextgis.com', login = 'administrator', password = 'demodemo')


ngwapi.get_resource_id_by_name('parks',group_id=3)
9
ngwapi.search_resource_by_name('parks',group_id=3)[0]['resource']['id']
9

# search vector layer in group by name
len(ngwapi.search_resource_by_name('places to eat',group_id=3,cls='vector_layer'))
1
# search resource by name with wildcards
 len(ngwapi.search_resource_by_name('places to *',group_id=3,cls='vector_layer'))
1
ngwapi.search_resource_by_name('places to ???',group_id=3,cls='vector_layer')[0]['resource']['id']
7
```
