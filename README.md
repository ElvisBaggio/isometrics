# isometrics

Cria isométricas a partir de um csv utilizando o serviço ORS.

```
$ python3 isometricas.py
```

Insira o nome do arquivo presente na pasta csv
```
Nome do arquivo (se estiver sem extensão, vai considerar .csv):
```

Defina a distância ou digite '0' para ler do csv
```
Digite a distância em metros (de '1000' a '15000'). Digite '0' para ler do arquivo:
```

### Diretórios necessários
- /csv/
- /results/
- /results/kml/
- /results/geojson/
- /data/

Na pasta data o arquivo areas.geojson é obrigatório.

### Estrutura do CSV:

Todos os campos são obrigatórios.

- *frn_id:* Identificador único para geração das isométricas

- *trading_name:* Nome do Local

- *origin_latitude:* Latitude da origem

- *origin_longitude:* Latitude da origem

- *logistic_region:* Nome da área

- *distance:* Distância para criação das isométricas.

- *processed:* Grava o status do processamento no csv

### exemplo csv

| frn_id,trading_name,origin_latitude,origin_longitude,logistic_region,distance,processed|
| ------ |
| 12345,Local 1,-23.597875,-46.667232,SAO PAULO,7000,F |
| 34567,Local 2,-23.621545,-46.699664,SAO PAULO,10000,F |
| 891011,Local 3,-23.621656,-46.699464,Sao Paulo,10000,F |

