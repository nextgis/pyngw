import pyngw

ngwapi = pyngw.Pyngw(ngw_url = 'https://sandbox.nextgis.com', login = 'administrator', password = 'demodemo')


ngwapi.replace_vector_layer(group_id=3279,old_display_name='photos',filepath='temp_photos.gpkg')

'''


docker run --rm -it -v ${PWD}:/opt/website   trolleway_website:dev  /bin/bash

'''