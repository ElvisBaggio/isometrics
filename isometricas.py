import os
import pandas as pd
import geopandas as gpd
import requests
import json
import fiona
import earthpy as et
import warnings; warnings.filterwarnings('ignore', 'GeoSeries.notna', UserWarning)

from shapely.geometry import Point, Polygon
from geopandas import GeoSeries, GeoDataFrame
from earthpy import clip as cl

fiona.supported_drivers
fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default


def inputNumber(message):
  while True:
    try:
       userInput = int(input(message))
    except ValueError:
       print("Não é um inteiro! Tente novamente")
       continue
    else:
       return userInput

def inputText(message):
    while True:
        try:
            userInput = input(message)
            if not userInput:
                raise ValueError('Digite um nome válido')
        except ValueError as e:
            print(e)
            continue
        else:
            return userInput


if __name__ == '__main__':
    #Get csv name and info
    csv = inputText("Nome do arquivo (se estiver sem extensão, vai considerar .csv): ")
    #csv = 'ids_teste'
    if csv.find('.') == -1:
        csv = csv.replace(".csv","")
        openCSV = 'csv/'+ csv + '.csv'
    else:
        openCSV = 'csv/'+ csv
        csv = csv.split('.')[0]

    #abertura do csv
    try:
        ids_merchant = pd.read_csv(openCSV)
    except:
        print('Erro ao abrir o arquivo')
        exit()         

    #Get area name and info
    areafile = inputText("Nome do arquivo de limites ou recorte (Digite 'N' para não utilizar): ")    
    if areafile != 'N':
        if areafile.find('.') == -1:
            areafile = areafile.replace(".geojson","")
            openArea = 'data/'+ areafile + '.geojson'
        else:
            openArea = 'data/'+ areafile
            areafile = areafile.split('.')[0]

        try:
            area = gpd.read_file(openArea)
        except:
            print('Erro ao abrir o arquivo de área')
            exit()           
    else:
        areafile = 'F'

    size_input = inputNumber("Digite a distância em metros (de '1000' a '15000'). Digite '0' para ler do arquivo:")
    
    

#Para cada linha do CSV, repete a ação de criação de isométricas
for index, row in ids_merchant.iterrows():

    #parametros de abertura de arquivo e definição de ranges
    frn_id = row['frn_id']
    trading_name = row['trading_name']
    latitude = row['origin_latitude']
    longitude = row['origin_longitude']
    region = row['logistic_region'].upper()
    status = row['processed']
    size_isos = row['distance']

    #define ranges

    if size_input == 0:
        ranges = list(range(500, size_isos+500, 500))
        ranges = [list(ranges[:10]),list(ranges[10:20]),list(ranges[20:30])]
        minValue = 0
        maxValue = int((size_isos/500)-1)
    else:
        ranges = list(range(500, size_input+500, 500))
        ranges = [list(ranges[:10]),list(ranges[10:20]),list(ranges[20:30])]
        minValue = 0
        maxValue = int((size_input/500)-1)

    if status == 'F':
        iso_array = []
        print (frn_id,latitude,longitude,region,size_isos)
        for x in ranges:
            if x!=[]:
                body = {"locations":[[longitude,latitude]],"range":x,"id":frn_id,"location_type":"start","range_type":"distance"}
                headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': '5b3ce3597851110001cf6248f9413c6dbd1b4184aca6b57c3ad8bc72',
                'Content-Type': 'application/json; charset=utf-8'
                }
                try:
                    print(str(frn_id) +': Gerando isométricas:' + str(x))
                    call = requests.post('https://api.openrouteservice.org/v2/isochrones/driving-car', json=body, headers=headers)
                except:
                    print('ERRO: Erro na chamada do serviço.\n')
                    print(call.status_code, call.reason)
                    continue

                try:
                    iso_array.append(gpd.GeoDataFrame.from_features(call.json()))
                except ValueError:
                    print('Erro ao combinar isométricas. Verifique os dados')
        concat_area = pd.concat(iso_array, ignore_index=True)
        concat_area.insert(0, "frn_id", frn_id)
        concat_area.insert(0, "trading_name", trading_name)
        concat_area.insert(0,"name",concat_area['value'])
        concat_area = concat_area.drop(['center'],axis=1)

        #corta a isométrica combinada com o limite do praça
        if areafile != 'F':
            try:
                print(str(frn_id) +': Recortando as isométricas com a area')
                concat_area = cl.clip_shp(concat_area,area[area['area_name']==region])
            except ValueError:
                print(str(frn_id) +': ERRO: Não foi possivel recortar com a area. Verifique o nome da área ou se a coordenada está dentro do hub logístico.\n')
                continue
        else:
            continue

        #Recorta as áreas maiores com as áreas menores
        try:
            print(str(frn_id) +': Recortando das isométricas.\n')
            for i in reversed(range(minValue+1,maxValue+1)):
                concat_area[concat_area['value']==(i+1)*500.] = gpd.overlay(concat_area[concat_area['value']==(i+1)*500.],concat_area[concat_area['value']==(i)*500.], how='difference')
        except ValueError:
            print(str(frn_id) +': ERRO: Falha no recorte das isométricas.\n')
            print('')
            continue

        concat_area.to_file('results/geojson/'+str(frn_id)+'.geojson',driver='GeoJSON')
        concat_area.to_file('results/kml/'+str(frn_id)+'.kml',driver='kml')
        ids_merchant.at[index,'processed']= 'T'
        ids_merchant.to_csv(openCSV, mode='w', index=False)
    else:
        print(str(frn_id) +' já processado')
