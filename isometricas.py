import os
import pandas as pd
import geopandas as gpd
import requests
import json
import fiona

from shapely.geometry import Point, Polygon
from geopandas import GeoSeries, GeoDataFrame
import earthpy as et
from earthpy import clip as cl

import warnings; warnings.filterwarnings('ignore', 'GeoSeries.notna', UserWarning)
  
fiona.supported_drivers
fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default

# Print area file
def printArea(df,filename):
    try:
        os.remove(filename)
    except OSError:
        pass
    df.to_file(driver="GeoJSON",filename=filename)

if __name__ == '__main__':
    #Get csv name and info
    csv = input("Nome do arquivo (se estiver sem extensão, vai considerar .csv): ")
    #csv = 'teste1'
    if csv.find('.') == -1:
        csv = csv.replace(".csv","")
        openFile = 'csv/'+ csv + '.csv'
    else:
        openFile = 'csv/'+ csv
        csv = csv.split('.')[0]    

    brasil_iFood = input("Incluir camada complementar da área da praça para recortar (s para 'sim', qualquer tecla para continuar):" )
    brasil_iFood = True if brasil_iFood.lower()=='s' else False    

#parametros de abertura de arquivo e definição de ranges
ids_merchant = pd.read_csv(openFile)
area_ifood = gpd.read_file("data/areas_ifood.geojson")
ranges = [[500,1000,1500,2000,2500,3000,3500,4000,4500,5000],[5500,6000,6500,7000,7500,8000,8500,9000,9500,10000]]#,[10500,11000]]
minValue = 0
maxValue = 19

#Para cada linha do CSV, repete a ação de criação de isométricas

for index, row in ids_merchant.iterrows():
    frn_id = row['frn_id']
    latitude = row['origin_latitude']
    longitude = row['origin_longitude']
    region = row['logistic_region'].upper()
    status = row['status']
    if status == '':
        iso_array = []
        print (frn_id,latitude,longitude,region)
        for x in ranges:
            body = {"locations":[[longitude,latitude]],"range":x,"id":frn_id,"location_type":"start","range_type":"distance"}
            headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': '5b3ce3597851110001cf62480bc2f932fdaf4f92a024171caeeb95c8',
            'Content-Type': 'application/json; charset=utf-8'
            }
            try:
                print('Gerando isométricas:' + str(x))
                call = requests.post('https://api.openrouteservice.org/v2/isochrones/driving-car', json=body, headers=headers)
            except:
                print('Erro na chamada do serviço')
                print(call.status_code, call.reason)
            
            iso_array.append(gpd.GeoDataFrame.from_features(call.json()))
        concat_area = pd.concat(iso_array, ignore_index=True)   
        concat_area.insert(0, "frn_id", frn_id)
        concat_area.insert(0,"name",concat_area['value'])   
        concat_area = concat_area.drop(['center'],axis=1)

        #corta a isométrica combinada com o limite do praça
        print('Recortando as isométricas com a praça')
        concat_area = cl.clip_shp(concat_area,area_ifood[area_ifood['area_name']==region])
        
        # Recorta as áreas maiores com as áreas menores    
        for i in reversed(range(minValue+1,maxValue+1)):
            concat_area[concat_area['value']==(i+1)*500.] = gpd.overlay(concat_area[concat_area['value']==(i+1)*500.],concat_area[concat_area['value']==(i)*500.], how='difference')
            
        print(concat_area)
        concat_area.to_file('results/geojson/'+str(frn_id)+'.geojson',driver='GeoJSON')
        concat_area.to_file('results/kml/'+str(frn_id)+'.kml',driver='kml')
        ids_merchant.to_csv(openFile, mode='a', header=False)
    else:
        print(frn_id+' já processado')