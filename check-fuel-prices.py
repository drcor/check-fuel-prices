#!/usr/bin/env python3
# author: drcor

import requests
import json
import os
import simplekml
from datetime import datetime
import math
import argparse
import yaml

URL = "https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/PesquisarPostos?idsTiposComb={}&idMarca=&idTipoPosto=&idDistrito=&idsMunicipios=&qtdPorPagina=5000&pagina=1"
TYPES_OF_FUEL = {
    "95": 3201,
    "98": 3405,
    "diesel": 2101
}

class FuelStation(object):
	# Fuel station constructor
	def __init__(self, name, district, municipality, town, address, latitude, longitude, price, brand):
		self.name = name
		self.district = district
		self.municipality = municipality
		self.town = town
		self.address = address
		self.latitude = latitude
		self.longitude = longitude
		self.price = price
		self.brand = brand

class CheckFuelPrices:
    def __init__(self, configPath:str, urlFormat:str, databasePath:str):
        # parse default configurations from the config file
        with open(configPath, 'r') as configfile:
            configOptions = yaml.safe_load(configfile)
        # import default configurations
        self.latitude = configOptions['latitude']
        self.longitude = configOptions['longitude']
        self.fuelType = self.convertFuelNameToRef(configOptions['fuel'])
        self.createKml = configOptions['create_kml']
        self.searchRadiusInKm = configOptions['search_radius']

        self.url = urlFormat.format(self.fuelType)
        self.databaseFile = os.path.join(databasePath, "fuel_prices_{}.json".format(self.fuelType))
        
        if self.isTimeToUpdateDatabase():
            self.updateDatabase()
            self.lastDatabaseUpdate = datetime.now()
        else:
            self.lastDatabaseUpdate = datetime.fromtimestamp(os.path.getmtime(self.databaseFile))


    def setFuelType(self, fuelName:str):
        self.fuelType = self.convertFuelNameToRef(fuelName)

    def setLatitude(self, latitude:float):
        if latitude and -90.0 <= latitude <= 90.0:
            self.latitude = latitude
    
    def setLongitude(self, longitude:float):
        if longitude and -180.0 <= longitude <= 180.0:
            self.longitude = longitude

    def isDatabaseAvailable(self) -> bool:
        return os.path.isfile(self.databaseFile)
    
    def isTimeToUpdateDatabase(self) -> bool:
        if self.isDatabaseAvailable():
            last_update = datetime.fromtimestamp(os.path.getmtime(self.databaseFile)) # Get time of last update
            # return True if database was not updated this week or if database is empty
            return last_update.isocalendar()[1] is not datetime.now().isocalendar()[1] or os.stat(self.databaseFile).st_size == 0
        else:
            return True
    
    def updateDatabase(self):
        # create database file if not exists
        if not self.isDatabaseAvailable():
            open(self.databaseFile, 'a').close()

        # Get database from API
        response = requests.get(self.url)

        if response.status_code == 200:
            try:
                json_response = json.loads(response.content)["resultado"]
                # Save in a file
                with open(self.databaseFile, "w") as file:
                    file.writelines(json.dumps(json_response))
            except Exception as e:
                print(e)
                exit(1)
        else:
            print("⚠️ failed to retrieve online data!")
            exit(1)

    def isStationNear(self, latitude:float, longitude:float) -> bool:
        arcLength = self.calculateEarthArcFromRadius(self.searchRadiusInKm)
        latitudeDistance = abs(latitude - self.latitude)
        longitudeDistance = abs(longitude - self.longitude)
        # return True if the distance between the two locations is smaller or equal to the radius
        return math.sqrt(latitudeDistance**2 + longitudeDistance**2) <= arcLength

    # converts the name of the fuel to it's reference in database
    def convertFuelNameToRef(self, fuelName:str) -> int:
        if fuelName in TYPES_OF_FUEL.keys():
            return TYPES_OF_FUEL[fuelName]
        else:
            return self.fuelType
    
    # Calculate the arc of earth equivalent to the radius of search
    def calculateEarthArcFromRadius(self, radius:float) -> float:
        earthRadius = 6371 # km
        return (radius * 180) / (math.pi * earthRadius)
    
    def searchDatabase(self):
        self.nearFuelStations = []
        stationsDatabase = None
        # read database
        with open(self.databaseFile, "r") as file:
            stationsDatabase = json.load(file)
        # create list of objects
        for station in stationsDatabase:
            if self.isStationNear(station['Latitude'], station['Longitude']):
                priceInFloat = float(station['Preco'].split()[0].replace(',', '.'))
                self.nearFuelStations.append(FuelStation(station['Nome'],
                                                    station['Distrito'],
                                                    station['Municipio'],
                                                    station['Localidade'],
                                                    station['Morada'],
                                                    station['Latitude'],
                                                    station['Longitude'],
                                                    priceInFloat,
                                                    station['Marca']))
        if len(self.nearFuelStations) > 1:
            # sort by price
            self.nearFuelStations = sorted(self.nearFuelStations, key=lambda fuelStation: fuelStation.price)

    def showResults(self):
        print(f"Data from: {self.lastDatabaseUpdate.strftime('%d/%m/%Y')}")
        
        if self.nearFuelStations == []:
            print("\n!Não existem bombas de combustível nesse raio!")
            exit()

        # Show the fuel stations list on monitor
        row_format ="{:>2} | {:<16} {:<40} {:<9} {:<15} {:<25}"
        print(row_format.format("Nº", "Marca", "Nome", "Preco", "Municipio", "Localizacao"))
        print("-" * len(row_format.format("", "", "", "", "", "")))
        for i, station in enumerate(self.nearFuelStations, start=1):
            print(row_format.format(
                i, 
                station.brand, 
                station.name, 
                str(station.price) + " €", 
                station.municipality, 
                "{}, {}".format(station.latitude, station.longitude)
            ))

        if self.createKml:
            self.saveKMLFile()

    # TODO: save kml file
    def saveKMLFile(self):
        kml = simplekml.Kml()
        for i, station in enumerate(self.nearFuelStations):
            kml.newpoint(name=f'{i} - {station.price}', description=f"{station.brand} - {station.name}", coords=[(station.longitude, station.latitude)])
        
        kml.save("fuelstations{}_[{}_{}]x{}_{}.kml".format(datetime.now().strftime("%Y%m%d"), self.latitude, self.longitude, self.searchRadiusInKm, self.fuelType))

# execute the Main class code
if __name__ == "__main__":
    CONFIG_PATH = os.path.expanduser('~')+"/.config/check-fuel-prices.yaml"
    DATA_PATH = os.path.expanduser('~')

    # create cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--radius", type=float, help="Radius of search in kilometers")
    parser.add_argument("-f", "--fuel", choices=TYPES_OF_FUEL.keys(), help="Type of fuel, default is 95")
    parser.add_argument("-k", "--kml", action="store_true", help="Save fuel stations in a KML file")
    parser.add_argument("latitude", type=float, help="Latitude location to search", nargs="?")
    parser.add_argument("longitude", type=float, help="Longitude location to search", nargs="?")
    
    # parse the arguments
    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        print("Error: Failed to parse the arguments")
        exit(1)

    # create class
    checkFuelPrices = CheckFuelPrices(CONFIG_PATH, URL, DATA_PATH)

    # update kml configuration
    checkFuelPrices.createKml = args.kml
    
    # update radius
    if args.radius and args.radius > 0:
        checkFuelPrices.searchRadiusInKm = args.radius

    # update fuel
    checkFuelPrices.setFuelType(args.fuel)
    
    # update latitude and longitude
    checkFuelPrices.setLatitude(args.latitude)
    checkFuelPrices.setLongitude(args.longitude)

    checkFuelPrices.searchDatabase()
    checkFuelPrices.showResults()
    
