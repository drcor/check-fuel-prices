# Check fuel prices

## Introduction
Check fuel prices is a script that shows the nearest fuel stations in Portugal near to you in a certain radius.
The fuel prices are obtained through the API of the website [Preço dos Combustiveis Online](https://precoscombustiveis.dgeg.gov.pt/)


## Usage
Install dependencies
```sh
pip install -r requirements.txt
```

Then create the file `~/.config/check-fuel-prices.yaml` and insert the following options, changing each value to your default choises:
```yaml
# Configuration file for check-fuel-prices.py
# With the default options
location: [0.0000, 0.0000] # [latitude, longitude]
fuel: "95" # 95, 98, diesel
create_kml: false
search_radius: 8 # kilometers

```
Where is `<latitude>` and `<longitude>` you should replace with the coordinates of the place you want to be your default.

> **Atention:** All the above options have to be set in the configuration file for the script to work

Then run in your terminal:
```sh
python3 check-fuel-prices.py [latitude] [longitude]
```
`latitude` and `longitude` are optional fields.

## Options
- `-f`,`--fuel` - Select the type of fuel 95, 98 or diesel. The default is 95
- `-r`, `--radius` - Radius of search in kilometers
- `-k`, `--kml` - Save the fuel stations locations in a KML file
- `-h`, `--help` - Show help menu

