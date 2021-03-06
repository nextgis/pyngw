#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
import os
import datetime
import shutil

import pprint
pp = pprint.PrettyPrinter(indent=4)


class Pyngw:

    '''
    Rule 1. 
    User of library should send data structures as described in docs.nextgis.com

    Rule 2.
    User of library can add own methods in main library file.

    '''

    def __init__(self,ngw_url='https://sandbox.nextgis.com',login='administrator',password='demodemo',log_level='ERROR'):
        """[create api instance with stored login and passwords]
        
        Keyword Arguments:
            ngw_url {str} -- [url of ngw instanse. Must not ended with slash symbol] (default: {'https://sandbox.nextgis.com'})
            login {str} -- [login] (default: {'administrator'})
            password {str} -- [password] (default: {'admin'})
        """
        self.ngw_url=ngw_url
        self.login=login
        self.password=password
        self.ngw_creds=(self.login,self.password)
        self.log_level = log_level
        
        if self.ngw_url.endswith('/'): raise ValueError('ngw_url should not ended with "/" ')

    def search_group_by_name(self,name,group_id=0):
        GROUPNAME = name

        url=self.ngw_url+'/api/resource/?parent='+str(group_id)
        request = requests.get(url, auth=self.ngw_creds)
        response = request.json()
        

        for element in response:
            if element['resource']['cls']=='resource_group' and element['resource']['display_name']==GROUPNAME:
                return element['resource']['id']
        return None
        
    def get_styles_from_webmap_top(self,resource_id):
        url=self.ngw_url+'/api/resource/'+str(resource_id)
        request = requests.get(url, auth=self.ngw_creds)
        response = request.json()
        
        found_ids = list()
        for element in response['webmap']['root_item']['children']:
            found_ids.append(element['layer_style_id'])
        return found_ids
    
    def search_by_cls(self,group_id=0,cls='webmap'):
 
        url=self.ngw_url+'/api/resource/?parent='+str(group_id)
        request = requests.get(url, auth=self.ngw_creds)
        response = request.json()
        
        found_ids = list()
        for element in response:
            if element['resource']['cls']==cls:
                found_ids.append(element['resource']['id'])
                
        if len(found_ids) == 0:
            return None
        else:
            return found_ids
    
    def pretty_print_query(self,req):
        print('\n{}\n{}\n{}\n\n{}'.format(
            '-----------REQUEST-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    def update_resource_payload(self,resource_id,payload,skip_errors=True):
        """ wrapper for PUT query, send payload"""
        assert payload is not None
        
        response = requests.put(self.ngw_url+'/api/resource/'+str(resource_id), json=payload, auth=self.ngw_creds )
        if skip_errors == False: assert response.ok
        
    def delete_resource_by_id(self,id):
        """delete ngw resource
        
        Arguments:
            id {[int, str]} -- [resource id]
        """
        url=self.ngw_url+'/api/resource/'+str(id)
        request = requests.delete(url, auth=self.ngw_creds)
        
    def truncate_group(self,group_id):
        resources = self.get_childs_resources(group_id)
        for resource in resources: self.delete_resource_by_id(resource['resource']['id'])

    def create_resource_group(self, parent_id=0, display_name=''):
        """[Create new resource group. Checks not performing]
        
        Keyword Arguments:
            parent_id {int} -- [id of resource group, where this resource will created] (default: {0})
            display_name {str} -- [display name of new resource] (default: {''})
        
        Returns:
            [int] -- [new resource group id]
        """
        
        if display_name == '': display_name = self.generate_name()
        payload = dict()

        payload['resource'] = {}
        payload['resource']['cls'] = 'resource_group'
        payload['resource']['parent']=dict(id=parent_id)
        payload['resource']['display_name'] = display_name

        
        url=self.ngw_url+'/api/resource/'
        request = requests.post(url, json = payload, auth=self.ngw_creds)

        assert request.status_code == 201

        response = request.json()
        group_id = response['id']
        return int(group_id)

    def upload_vector_layer_ogr2ogr(self,filepath,group_id,display_name='',layer=None, geometry_type = None, batch_size=200):
        import os
        
        if display_name == '': display_name = self.generate_name()
        new_group_name = self.generate_name()
        cmd = 'ogr2ogr -nlt POINT   -dsco "USERPWD=administrator:demodemo" -t_srs EPSG:4326 -f NGW "NGW:https://sandbox.nextgis.com/resource/0/Название на русском языке" post_office.geojson '
        cmd = ["ogr2ogr",
        '-skipfailures',
        '-dsco "USERPWD='+self.login+':'+self.password+'"',
        '-t_srs EPSG:4326', 
        '-f NGW',
        '"NGW:{url}/resource/0/{display_name}"'.format(url=self.ngw_url, display_name=display_name),
        filepath,
        ]
        if geometry_type is not None:
            nlt = '-nlt '+geometry_type
        else:
            nlt = ''
        
        cmd = 'ogr2ogr -f NGW -skipfailures -progress -update -dim XY -doo "BATCH_SIZE={BATCH_SIZE}" {nlt}  -nln {nln} -doo "USERPWD={login}:{password}" -t_srs EPSG:3857 "NGW:{url}/resource/{group_id}" "{filename}"'
        cmd = cmd.format(url=self.ngw_url, display_name=display_name,login=self.login,password=self.password, 
        group_id=group_id,
        new_group_name=new_group_name,
        filename=filepath,
        nlt = nlt,
        BATCH_SIZE = batch_size,
        nln = layer)
        #cmd = cmd + ' ' + '
        if layer is not None: cmd = cmd +' ' + layer
        print(cmd)
        
        os.system(cmd)    
    
    def upload_vector_layer(self,filepath,group_id, display_name=''):
        """[Create vector layer from file]
        
        Arguments:
            filepath {str} -- [path to file (geojson, zip with shp)]
            group_id {str} -- [id of resource group, where this resource will created]
        
        Keyword Arguments:
            display_name {str} -- [display name of new resource] (default: {''})
        
        Returns:
            [int] -- [id of new layer]
        """

        if display_name == '': display_name = self.generate_name()

        with open(filepath, 'rb') as fd:
            file_upload_result = requests.put(self.ngw_url + '/api/component/file_upload/upload', data=fd)

        payload=dict(
            resource=dict(cls='vector_layer', parent=dict(id=group_id), display_name=display_name),
        
        vector_layer=dict(  source=file_upload_result.json(),
                            srs=dict(id=3857))
        )

        vector_layer = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        return vector_layer.json()['id']


    
    def create_postgis_connection(self,group_id=0, display_name='',hostname='localhost',port=54321,database='gis',username='',password=''):
        """[Create PostGIS connection in ngw]
        
        Keyword Arguments:
            group_id {int} -- [description] (default: {0})
            display_name {str} -- [description] (default: {''})
            hostname {str} -- [description] (default: {'localhost'})
            port {int} -- [description] (default: {54321})
            database {str} -- [description] (default: {'gis'})
            username {str} -- [login for postgresql] (default: {''})
            password {str} -- [password for postgresql] (default: {''})
        
        Returns:
            [int] -- [id of new ngw resource]
        """
        if display_name == '': display_name = self.generate_name()
        
        payload =  {
        "postgis_connection": {
            "database": database,
            "hostname": hostname,
            "password": password,
            "port" : 54321,
            "username": username
        },
        "resource": {
            "cls": "postgis_connection",
            "description": "The localhost PostGIS Connection",
            "display_name": display_name,
            "parent": {
            "id": group_id
            }
        }
        }

        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds)
        assert response.status_code == 201
        postgis_connection_id = response.json()['id']
        return postgis_connection_id

    def create_postgis_layer(self,connection,table='',group_id=0, display_name=''):
        """[Create PostGIS layer in ngw]
        
        Arguments:
            connection {[int]} -- [id of PostGIS connection in ngw]
        
        Keyword Arguments:
            table {str} -- [description] (default: {''})
            group_id {int} -- [description] (default: {0})
            display_name {str} -- [description] (default: {''})
        
        Returns:
            [id] -- [id of new ngw resource]
        """
        if display_name == '': display_name = self.generate_name()
        payload =  {
        "postgis_layer": {
            "column_geom": "wkb_geometry",
            "column_id": "ogc_fid",
            "connection": {"id": connection},
            "fields": "update",
            "geometry_type": 'LINESTRING',
            "schema": "public",
            "srs": {"id": 3857},
            "table": table
        },
        "resource": {
            "cls": "postgis_layer",

            "display_name": display_name,

            "parent": {
            "id": group_id
            }
        }
        }


        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds)
        
        assert response.status_code == 201
        postgis_layer = response.json()['id']
        return postgis_layer


    def create_wms_connection(self,group_id=0, display_name='',url='',username=None,password=None):
        """[Create WMS connection in ngw]
        
        Keyword Arguments:
            group_id {int} -- [description] (default: {0})
            display_name {str} -- [description] (default: {''})
            url {str} -- [description] (default: {''})
            username {[type]} -- [username for WMS server] (default: {None})
            password {[type]} -- [password for WMS server] (default: {None})
        
        Returns:
            [int] -- [id of new WMS connection]
        """
        if display_name == '': display_name = self.generate_name()
        
        payload = {
        "resource": {
            "cls": "wmsclient_connection",
            "display_name": display_name,
            "parent": {
            "id": group_id
            }
        },
        "wmsclient_connection": {
            "url": url,
            "version": "1.1.1",
            "username": username,
            "password": password,

        }
        }
        #"https://mrdata.usgs.gov/services/kb"

        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds)
        assert response.status_code == 201
        wms_connection_id = response.json()['id']
        return wms_connection_id

    def create_wms_layer(self,connection,layer='',group_id=0, display_name=''):
        if display_name == '': display_name = self.generate_name()

        payload = {
            "resource": {
                "cls": "wmsclient_layer",
                "parent": {
                    "id": group_id
                },
                "display_name": display_name,
            },
            "wmsclient_layer": {
                "connection": {
                    "id": connection
                },
                "wmslayers": layer,
                "imgformat": "image/png",
                "srs": {
                    "id": 3857
                },
            }
        }


        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds)
        
        assert response.status_code == 201
        wms_layer = response.json()['id']
        return wms_layer

    def upload_raster_layer(self, filepath, group_id, display_name = ''):
        """[Create raster layer from file. Raster style is not created]
        
        Arguments:
            filepath {[type]} -- [path to file in local filesystem]
            group_id {[type]} -- [description]
        
        Keyword Arguments:
            display_name {str} -- [description] (default: {''})
        
        Returns:
            [id] -- [resource id of new layer]
        """
        if display_name == '': display_name = self.generate_name()
        with open(filepath, 'rb') as fd:
            file_upload_result = requests.put(self.ngw_url + '/api/component/file_upload/upload', data=fd)
        
        payload = {
        "resource": {
            "cls": "raster_layer",
            "display_name": display_name,
            "parent": {"id": group_id}
        },
        "raster_layer": {
            "source": file_upload_result.json(),
            "srs": {"id": 3857}
        }
        }
        
        raster_layer = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        if raster_layer.status_code != 201:
            print
            pp.pprint(file_upload_result.json())
            print
            pp.pprint(payload)
            pp.pprint(raster_layer.json())
        return raster_layer.json()['id']

    def upload_geojson(self,filepath,group_id):
        """[alias for backward compability, please use upload_vector_layer instead]
        
        Arguments:
            filepath {[type]} -- [description]
            group_id {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        return self.upload_vector_layer(filepath,group_id)

    def create_raster_style(self,layer_id,display_name = ''):
        if display_name == '': display_name = self.generate_name()

        payload=dict(
            resource=dict(cls='raster_style', parent=dict(id=layer_id), display_name=display_name),                       
        )
        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        return response.json()['id']  

    def upload_qgis_style(self,filepath,layer_id,display_name=''):
        if display_name == '':
            display_name=os.path.splitext(filepath)[0]

        print("upload style "+ filepath + ' to '+ self.ngw_url+'/api/resource/'+str(layer_id) + '    '+display_name)
            
        with open(filepath, 'rb') as fd:
            file_upload_result = requests.put(self.ngw_url + '/api/component/file_upload/upload', data=fd)
        payload=dict(
            resource=dict(cls='qgis_vector_style', parent=dict(id=layer_id), display_name=display_name),
        
        qgis_vector_style=dict(file_upload=file_upload_result.json())                        
        )
        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        return response.json()['id']

    def replace_qgis_style(self,filepath,style_id):

        print("replace style "+ filepath + ' to '+ self.ngw_url+'/api/resource/'+str(style_id) )

        with open(filepath, 'rb') as fd:
            file_upload_result = requests.put(self.ngw_url + '/api/component/file_upload/upload', data=fd)
        payload=dict(
                        qgis_vector_style=dict(id=style_id,file_upload=file_upload_result.json())                        
        )
        response = requests.put(self.ngw_url+'/api/resource/'+str(style_id), json=payload, auth=self.ngw_creds )
           
        return response.json()

    def create_wms(self,group_id,layers,display_name='autogenerated_wms_service'):
        """[summary]
        
        Arguments:
            group_id {[type]} -- [description]
            layers {[type]} -- [list of dicts, as decribed in ngw docs]
        
        Keyword Arguments:
            display_name {str} -- [description] (default: {'autogenerated_wms_service'})
        """
        
        payload = {
        "resource": {
            "cls": "wmsserver_service",
            "parent": {
                "id": group_id
            },
            "display_name": display_name,
 
        },
        "resmeta": {
            "items": {}
        },
        "wmsserver_service": {
            "layers": layers
        }
        }
        
        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        return response.json()['id'] 
    
    def create_wms_from_webmap(self,webmap_id, display_name='autogenerated_wfs_service'):
        wms_layers = list()
        webmap = self.get_resource(webmap_id)
        assert(webmap['resource']['cls']=='webmap')
        
        for element in webmap['webmap']['root_item']['children']:
            wms_layer = {
             "keyname": element["layer_style_id"],
             "display_name": element["display_name"],
             "resource_id": element["layer_style_id"],
             "min_scale_denom":None,"max_scale_denom":None
            }
            wms_layers.append(wms_layer)
        
        self.create_wms(group_id = webmap['resource']['parent']['id'],layers = wms_layers, display_name = display_name)
            
    def create_wfs(self,group_id,layers,display_name='autogenerated_wfs_service'):
        payload = {
        "resource": {
            "cls": "wfsserver_service", 
            "parent": { "id": group_id}, 
            "display_name": display_name, 
        }, 
        "wfsserver_service": {
            "layers": layers
        }
        }
        
        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        return response.json()['id'] 

    def create_vector_feature(self,layer_id,geom,fields):
        payload = {"geom": geom, "fields": fields}
        print
        pp.pprint(payload)
        print
        response = requests.post(self.ngw_url+'/api/resource/'+str(layer_id)+'/feature/', json=payload, auth=self.ngw_creds )
        pp.pprint(response.text)
        return response.json()['id']  
        '''
url='https://sandbox.nextgis.com'
login='administrator'
password='demodemo'
   
curl -d '{   "fields": {   "name": "object created in POST"},"geom": "LINESTRING (5028857 6471598, 5028969 6471598)"}' -u $login:$password -X POST $url/api/resource/417

curl -d '{   "fields": {   "name": "object created in POST"},"geom": "LINESTRING (5028857 6471598, 5028969 6471598)"}' -u administrator:demodemo -X POST https://sandbox.nextgis.com/api/resource/420/feature/

   '''   

    def get_layers4webmap(self, group_id,namesource='',layer_adapter='tile'):
        """
        Return list with layers for create_webmap 
        """
        response = self.get_childs_resources(group_id)
        webmap_children_lines = list()
        for layer in response:
            #call childrens second time for search vector_style
            if layer['resource']['cls'] != 'vector_layer': continue
            children_grand = self.get_childs_resources(layer['resource']['id'])
            layer_style_id = None
            children_name = None
            for subelement in children_grand:
                if subelement['resource']['cls'] != 'qgis_vector_style': continue
                layer_style_id = subelement['resource']['id']
                children_name = subelement['resource']['display_name']
            if layer_style_id is None: continue    
            element=dict()
            element['layer_adapter'] = layer_adapter
            element['display_name']=layer['resource']['display_name']
            if namesource == 'children': element['display_name'] = children_name
            element['layer_style_id']=layer_style_id
            element['layer_enabled']=True
            element['item_type']='layer'
            webmap_children_lines.append(element)
        return webmap_children_lines
        
    def create_webmap_from_group(self,group_id,display_name='', layer_adapter = 'tile'):
        childrens = self.get_layers4webmap(group_id, layer_adapter = layer_adapter)
        return self.create_webmap(group_id,childrens,display_name)
        
    def create_webmap(self,group_id,childrens,display_name=''):
        """[Create webmap]
        
        Arguments:
            group_id {[int]} -- [id of resource group in ngw, where map will be created]
            childrens {[type]} -- [list of children, as described in ngw REST API ]
        
        Keyword Arguments:
            display_name {str} -- [name of webmap] (default: ''})
        
        Returns:
            [int] -- [resource id of new webmap]
        """
        
        if display_name == '': display_name = 'map ' + self.generate_name()

        payload = {
            "resource":{
            "display_name":display_name,
            "parent":{
                "id":group_id
            },
            "cls":"webmap"
            },
            "webmap":{
            "root_item":{
                "item_type":"root",
                "children": childrens
            }
            }
            }


        response = requests.post(self.ngw_url+'/api/resource/', json=payload, auth=self.ngw_creds )
        assert response.ok
        return response.json()['id']   

    def download_vector_layer(self,path,layer_id,format='GeoJSON',srs=4326,zipped=False):
        """Download vector layer
        
        Arguments:
            path {[str]} -- [Path to save file]
            layer_id {[int]} -- [description]
        
        Keyword Arguments:
            format {str} -- [description] (default: {'geojson'})
            srs {int} -- [description] (default: {4326})
            zipped {bool} -- [description] (default: {False})
        """
        assert format in ('GeoJSON','GPKG','CSV')
        assert zipped in (False,True)
        if zipped == False:
            zipped_str = 'false'
        else:
            zipped_str = 'true'
        url = '{url}/api/resource/{layer_id}/export?format={format}&srs={srs}&zipped={zipped_str}&fid=ngw_id&encoding=UTF-8'
        url = url.format(url=self.ngw_url,
            layer_id = layer_id,
            format=format,
            srs=srs,
            zipped_str=zipped_str)
        #https://sandbox.nextgis.com/api/resource/56/export?format=csv&srs=4326&zipped=true&fid=ngw_id&encoding=UTF-8
    
        if self.log_level in ('DEBUG','INFO'): print('download vector layer '+url)
        response = requests.get(url, stream=True,auth=HTTPBasicAuth(self.login, self.password))
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        
    def download_qgis_style(self,path,resource_id):
        """Download qgis vector style
        
        Arguments:
            path {[str]} -- [Path to save file]
            resource_id {[int]} -- [resource id]
        
        Keyword Arguments:

        """

        url = '{url}/api/resource/{resource_id}/qml'
        url = url.format(url=self.ngw_url,
            resource_id = resource_id
            )

        response = requests.get(url, stream=True,auth=HTTPBasicAuth(self.login, self.password))
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    
    def get_TMS_url(self,style_id):
        url = '{url}/api/component/render/tile?resource={style_id}'
        url = url.format(url=self.ngw_url,style_id=style_id)
        url = url + '&x={x}&y={y}&z={z}'
        return url
        
    def generate_name(self):
        return str(datetime.datetime.now())

    def get_resource(self,resource_id):
        """  wraper for simple GET """
        url = '{url}/api/resource/{resource_id}'
        url = url.format(url=self.ngw_url,
            resource_id = resource_id)
        request = requests.get(url, auth=self.ngw_creds)
        response = request.json()
        return response
        
    def get_feature_count(self,resource_id):
        url = '{url}/api/resource/{resource_id}/feature_count'
        url = url.format(url=self.ngw_url,
            resource_id = resource_id)
        request = requests.get(url, auth=self.ngw_creds)
        response = request.json()
        return response['total_count']

    def get_childs_resources(self,resource_group_id):
        """[wraper for GET query ?parent= , with use login-password from class]
        
        Arguments:
            resource_group_id {int} -- [description]
        
        Returns:
            [str] -- [json with result]
        """
        #
        url = '{url}/api/resource/?parent={resource_group_id}'
        url = url.format(url=self.ngw_url,
            resource_group_id = resource_group_id)
        request = requests.get(url, auth=self.ngw_creds)
        response = request.json()
        return response
        
    def upload_qmls_byname(self,resource_group_id,qml_path):
        response = self.get_childs_resources(resource_group_id)
        print(response)
        for layer in response:
            print(layer['resource']['id'],layer['resource']['display_name'] )
            qml_filename = os.path.join(qml_path,layer['resource']['display_name']+'.qml')
            
            self.upload_qgis_style(filepath=qml_filename,layer_id=layer['resource']['id'],display_name='')
    
    
    def _sort_layers_by_list(self,layers,orderlist):
        """
        sort layers list by list of names.
        Not found elements keep at end of list (this behavior is differ from standart sort with lambda)
        """
        
        assert len(orderlist) > 0
        assert len(layers) > 0
        
        len_source_list = len(layers)
        

        res = [tuple for x in orderlist for tuple in layers if tuple['display_name'] == x] 
        res2 = [tuple for tuple in layers if tuple['display_name'] not in orderlist]  #not found
        res = res + res2
        
        assert len(res) == len_source_list
        return res
        
    def webmap_reorder_layers_by_list(self, webmap_id, orderlist):

        webmap_data = self.get_resource(webmap_id)
        #pp.pprint(payload_pre['webmap']['root_item']['children'])
        layers = webmap_data['webmap']['root_item']['children']

        layers_reordered = self._sort_layers_by_list(layers,orderlist) #reordering will be here

        payload = {'webmap':{'root_item':{'item_type':'root', 'children': layers_reordered  } }}

        url=self.ngw_url+'/api/resource/'+str(webmap_id)
        response = requests.put(url, json = payload, auth=self.ngw_creds) 

        assert response.ok        
        
        return 

