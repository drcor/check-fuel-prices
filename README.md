# Check fuel prices

## Introduction

Check fuel prices is a script that shows the nearest fuel stations in Portugal near to you in a certain radius.

## Usage
Install dependencies
```sh
pip install -r requirements.txt
```

Then configure your default options in the configuration file
Create a file in your `.config` folder and insert the following options
```yaml
# Configuration file for check-fuel-prices.py
# With the default options
location: [0.0000, 0.0000] # [latitude, longitude]
fuel: "95" # 95, 98, diesel
create_kml: false
search_radius: 8 # kilometers

```
Where is `<latitude>` and `<longitude>` you should replace with the coordinates of the place you want

**!!Atention!!:** All the above options have to be defined in the configuration file in order to the script work

Then run:
```sh
python3 check-fuel-prices.py
```

## Options
- `-f` - Select the type of fuel 95, 98 or diesel. The default is 95
- `-r` - Radius of search in kilometers. The default is 8 km
- `-k` - Save the fuel stations locations in a KML file
- `-h` - Show help menu

