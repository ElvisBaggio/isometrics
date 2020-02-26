# import os
# import pandas as pd
# import geopandas as gpd
# import requests
# import json
# import fiona

# from shapely.geometry import Point, Polygon
# from geopandas import GeoSeries, GeoDataFrame

# fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
# fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default

# # Print area file
# def printArea(df,filename):
#     try:
#         os.remove(filename)
#     except OSError:
#         pass
#     df.to_file(driver="GeoJSON",filename=filename)

# if __name__ == '__main__':
#     #Get filename and info
#     #filename = input("Nome do arquivo (se estiver sem extensão, vai considerar .csv): ")
#     filename = 'teste1'
#     if filename.find('.') == -1:
#         filename = filename.replace(".csv","")
#         openFile = filename + '.csv'
#     else:
#         openFile = filename
#         filename = filename.split('.')[0]    

#     add_recorte = input("Incluir camada complementar da área da praça para recortar (s para 'sim', qualquer tecla para continuar):" )
#     add_recorte = True if add_recorte.lower()=='s' else False   
# geo = 'villalobos.geojson'
# iso = gpd.read_file(geo)  
# df = pd.read_csv(openFile)

# for index, row in df.iterrows():
#     print (row['frn_id'], row['longitude'], row['latitude'], row['region'])
 
#     region = row['region']
#     if add_recorte:
#         areas_ifood = gpd.read_file("areas_ifood.geojson")
#         a = gpd.overlay(iso,areas_ifood[areas_ifood['area_name']=='SAO PAULO'], how='difference')
#         print(a)

start = 500
stop = 5000
step = 500

print(list(range(start, stop, step)))