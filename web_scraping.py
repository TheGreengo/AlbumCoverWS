import os
import sys
import time
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from requests_html import HTMLSession

PREF = "https://en.wikipedia.org"

def full_loop(COUNT):
    with open("urls.csv", "w") as file:
        file.write("ID,url,year,\n")
        for i in range(74):
            earl = f"https://en.wikipedia.org/wiki/Category:{1950 + i}_albums"
            req = requests.get(earl)
            soup = BeautifulSoup(req.content, 'html.parser')
            time.sleep(0.15)

            COUNT = get_albums(soup, file, COUNT, 1950 + i)
            next = soup.find("a", string="next page")

            while (next != None):
                req = requests.get(PREF + next.get("href"))
                soup = BeautifulSoup(req.content, 'html.parser')
                time.sleep(0.15)
                COUNT = get_albums(soup, file, COUNT, 1950 + i)
                next = soup.find("a", string="next page")
        print(f"I think it's done. Final count: {COUNT}")

def get_albums(soup, file, COUNT, year):
    sou = soup.find(id='mw-pages')
    s = sou.findAll('div', class_='mw-category-group')
    for i in s:
        things = i.findAll("a")
        for j in things:
            title = j.text.strip()
            url = PREF + j.get("href")
            file.write(f"{COUNT:0>6},{year},{url},\n")
            COUNT += 1
    return COUNT

def save_static(temp_cont):
    with open("temp_file", "w") as file:
        file.write(temp_cont)

def read_static():
    with open("temp_file", "r") as file:
        cont = file.read()
    return cont

def get_soup(earl):
    req = requests.get(earl)
    soup = BeautifulSoup(req.content, 'html.parser')
    return soup

def get_album_info(soup):
    table = soup.find("table")

    info = [
        # from body: album_name_1 
        get_album_name_1(soup),
        # from table: album_name_2 
        get_album_name_2(table),
        # genres       
        get_genres(table),
        # label        
        get_label(table),
        # from by in table: artist_1     
        get_artist_1(soup),
        # from chronology: artist_2     
        get_artist_2(table),
        # length       
        get_length(table),
        # img_url      
        get_img_url(table),
    ]

    return info

def get_album_name_1(soup):
    name = soup.find("b")
    if name != None:
        return name.text
    return ""

def get_album_name_2(table):
    poss = table.find("th",class_=["album","summary","infobox-above"])
    if poss != None:
        return poss.text.strip()
    return ""

def get_img_url(table):
    poss = table.find("td",class_=["infobox-image"])
    if poss != None:
        earl = poss.find("img")
        if earl != None:
            return "" if earl.get("src") == None else earl.get("src")
    return ""

def get_genres(table):
    genres = []
    start = table.find('a', {'title' : 'Music genre'})
    if start != None:
        cont = start.parent.parent
        lis = cont.findAll("li")
        if lis != None:
            for i in lis:
                genre = i.find("a")
                if genre != None:
                    genres.append(genre.text.strip())
        td = cont.find("td")
        if td != None:
            genre =  td.find("a")
            if genre != None:
                genres.append(genre.text.strip())
    return list(set(genres))

def get_label(table):
    start = table.find('a', {'title' : 'Record label'})
    if start != None:
        cont = start.parent.parent
        if cont != None:
            td = cont.find("td")
            if td != None:
                link = td.find("a")
                if link != None:
                    return link.text
    return ""

def get_artist_1(table):
    poss = table.find("th",class_=["description","infobox-header"])
    if poss != None:
        poss = table.find("div",class_="contributor")
        if poss != None:
            inner = poss.find("a")
            if inner != None:
                return inner.text.strip()
            return poss.text.strip()
    return ""

def get_artist_2(table):
    poss = table.findAll("th",class_=["description","infobox-header"])
    if poss != None:
        for i in poss:
            for j in i.findAll("a"):
                if "chronology" in i.text:
                    return j.text.strip()
    return ""

def get_length(table):
    poss = table.find("span",class_="duration")
    if poss != None:
        min = poss.find("span", class_="min")
        sec = poss.find("span", class_="s")
        if (min != None) and (sec != None):
            return (int(min.text) * 60) + int(sec.text)
    return -999

def time_out_visit(earl, year):
    print(earl)
    print(year)

def info_scrape(num):
    lines = []
    errors = 0
    with open("urls.csv","r") as file:
        lines = file.readlines()
    lines.pop(0)
    with open("info.csv","a") as file:
        file.write("ID,year,album_name_1,album_name_2,genres,label,artist_1,artist_2,length,img_url")
        for i in lines:
            ID = i[:6]
            if int(ID) <= num:
                continue
            year = i[7:11]
            earl = i[12:-2]
            req = requests.get(earl)
            soup = BeautifulSoup(req.content, "html.parser")
            time.sleep(0.105)
            try:
                cont = get_album_info(soup)
                file.write(f"{ID},{year},\"{cont[0]}\",\"{cont[1]}\",\"{cont[2]}\",")
                file.write(f"\"{cont[3]}\",\"{cont[4]}\",\"{cont[5]}\",{cont[6]},\"{cont[7]}\"\n")
            except:
                errors += 1
                file.write(f"{ID},{year}, , , , , , , , \n")

def save_image(earl, name):
    image_url = "https:" + earl 
    headers = {'User-Agent': 'GreengoBot/0.0 (https://github.com/TheGreengo/)'}
    img_data = requests.get(image_url, headers=headers).content
    with open(name, 'wb') as handler:
        handler.write(img_data)

# 199747
def pic_scrape(num):
    with open("info.csv","r") as file:
        lines = file.readlines()
    lines.pop(0)
    count = 0
    for i in lines:
        if not((", , , , , , " in i) or (i.split("\"")[-2] == "")):
            Id = i.split(",")[0]
            if int(Id) <= num:
                continue 
            toop = i.split(".")[-1][:-2]
            save_image(i.split("\"")[-2], f"./pics/{Id}.{toop}")
            time.sleep(0.11)

if __name__ == "__main__":
    # This function gets all of the urls for pages with album listings and uses
    # them to make a .csv file with all of the addresses needed for scraping 
    # the actual album info
    full_loop(0)

    # This function goes through the urls listed in the urls.csv file and 
    # performs the web scraping of the image urls and album info, writing those
    # to a .csv file
    info_scrape(0)

    # This function goes through the the .csv file generated by the `info_scrape`
    # function, and retrieves each of the images, writing it to a local `pics` 
    # directory
    pic_scrape(0)
