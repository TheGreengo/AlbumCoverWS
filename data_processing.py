import re 
import pandas as pd
'''
This file takes the `info.csv` file written by the web scraping script and 
creates a new column in the .csv file with the image name, now reflecting
the image extension (.png, .gif, .jpg, or .jpeg mostly)
'''

#ID,year,album_name_1,album_name_2,genres,label,artist_1,artist_2,length,img_url
def parse_line(line):
    res = []

    pos = 0
    for i in range(9):
        done = False
        open = False
        temp = ""
        while not done:
            if line[pos] == "," and not open:
                done = True
            if line[pos] == '"':
                open = not open
            # append
            if not done:
                temp += line[pos]
            # incrememnt
            pos += 1
        res.append(temp)

    res.append(line[pos:-1])

    return res

# read in the original csv
with open("info.csv", "r") as file:
    lines = file.readlines()

# get all IDs for which a valid image exists
with open("valid.txt", "r") as file:
    valid = [i.split(".")[0] for i in file.readlines()]

# initialize all of the colum names
names = lines[0].split(",")
names[-1] = names[-1][:-1]

# make a dictionary for all of the things
data = {}
for i in names:
    data[i] = []
data["path"] = []
print(data)

for i in lines:
    # skip the first line
    if i == names:
        continue

    if i[:6] not in valid:
        continue

    stuff = parse_line(i)

    # test if correct
    if len(stuff) != 10:
        print(i[:6])

    # add the the "path"
    pathy = "\"" + str(stuff[0]) + "." + stuff[-1].split(".")[-1][:-1] + "\""
    stuff.append(pathy)

    for i in stuff:
        i = i.replace(",", ";")

    # correct the ,s 
    thing = 0
    for j in data:
        data[j].append(stuff[thing])
        thing += 1

# create a pandas dataframe
df = pd.DataFrame(data)
print(df)

# write it out to a new_info.csv
df.to_csv("new_info.csv", index=False)
