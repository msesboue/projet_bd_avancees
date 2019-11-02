from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
from os import listdir
from os.path import isfile, join
from tqdm import tqdm
from geojson import Point, Feature, FeatureCollection, dump
import numpy as np

class Restaurant:
    def __init__(self, title, address, pricing, labels, coordonnees):
        self.title = title
        self.address = address
        self.pricing = pricing
        self.labels = labels 
        self.coordonnees = coordonnees

def ws_resto(restaurants):
    repository = "./Data/web_html"
    files = [f for f in listdir(repository) if isfile(join(repository, f))]

    for f in tqdm(files):
        absfile = os.path.abspath(f)
        html = open(repository + '/' + f, encoding='utf-8').read()
        page_content = BeautifulSoup(html, "lxml")
        blocks = page_content.find_all("div", class_="row search-result")
        #lats = page_content.find_all("div", class_="row search-result")['data-lat']

        for it, block in enumerate(blocks):
            tmp = block.find("div", class_="col-md-8 col-lg-9 p15")
            title = tmp.find("p", class_="search-title").text
            address = tmp.find("a", class_="search-address-label").text
            pricing = tmp.find("span", class_="search-price").text
            coordonnees = [block['data-lon'], block['data-lat']]
            labels = []
            for label in tmp.find_all("a", class_="search-cuisine-label"):
                labels.append(label.text)
            if len(address) !=0:
                restaurants.append(Restaurant(title, address, pricing, labels, coordonnees))
    print("Nombre de restaurant : "+str (len(restaurants)))
    return restaurants
def struct2geojson(restaurants):
    features = []
    for r in restaurants:
        #point = Point((r.coordonnees[0],r.coordonnees[1]))
        features.append(Feature(properties={"nom" : r.title, "adresse" : r.address, "prix" : r.pricing, "labels": r.labels}, geometry=Point((float(r.coordonnees[0]), float(r.coordonnees[1])))))
    features_collection = FeatureCollection(features)
        
    with open('restaurants.geojson', 'w', encoding="utf-8-sig") as f:
        dump(features_collection, f, ensure_ascii=False)

def main():
    restaurants = []
    ws_resto(restaurants)
    struct2geojson(restaurants)

if __name__ == '__main__':
    main()
    

