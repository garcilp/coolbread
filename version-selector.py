import imageio
import requests
import time
import numpy as np
import os
import urllib.request
import unicodedata
import re
from glob import glob
from shutil import copy

folder = "%IMAGES%"                # root folder for card images
destination = "%OUTPUT%"           # output folder
backs_folder = "%BACKS_OUTPUT%"    # output folder for the back side of DFCs
copy_array = []
backs_array = []

def process_line(input_str: str):
    # Extract the quantity and card name from a given line of the text input
    input_str = str(" ".join([x for x in input_str.split(" ") if x]))
    if input_str.isspace() or len(input_str) == 0:
        return None, None
    num_idx = 0
    input_str = input_str.replace("//", "&").replace("/", "&")
    while True:
        if num_idx >= len(input_str):
            return None, None
        try:
            int(input_str[num_idx])
            num_idx += 1
        except ValueError:
            if num_idx == 0:
                # no number at the start of the line - assume qty 1
                qty = 1
                name = " ".join(input_str.split(" "))
            else:
                # located the break between qty and name
                try:
                    qty = int(input_str[0 : num_idx + 1].lower().replace("x", ""))
                except ValueError:
                    return None, None
                name = " ".join(x for x in input_str[num_idx + 1 :].split(" ") if x)
            return name, qty

def find_card(cardname):
	os_tree = os.walk(folder, topdown = True);
	options = []
	for root, dirs, files in os_tree:
		for name in files:
			if name.endswith(".png") & (str(cardname) in name):
				options.append(root + "\\" + name)
	return(options)
	
def find_set(cardname):
	os_tree = os.walk(folder, topdown = True);
	options = []
	for root, dirs, files in os_tree:
		for name in files:
			if name.endswith(".png") & (cardname in name):
				options.append(root[12:])
	return(options)

def is_double_faced(cardname):
	r = requests.get('https://api.scryfall.com/cards/search?q=' + cardname).json()
	if "image_uris" not in r["data"][0]:
		return r["data"][0]["card_faces"][1]["name"]
	else:
		return False

with open('decklist.txt', 'r') as cards:
	for card in cards:
		faces = []
		# Turn line into parseable quantity and cardname
		card = card.replace("\n", "")
		(query, qty) = process_line(card)	
		
		if is_double_faced(str(query)) != False:
			faces = query.split(' & ')
			query = faces[0]
			if len(faces) == 1:
				faces.append(is_double_faced(query));
					
		# check to see if card exists
		if len(find_card(query)) == 0:
			print("No versions of " + str(query) + " present in the chosen folder.")
		else:
			# look for the card as many times as needed
			idx = 1
			while idx <= qty:			
				if len(find_card(query)) == 1:
					# if there is only one version, store it into an array
					if is_double_faced(query) != False:
						try:
							copy_array.append(find_card(faces[0])[0])
							backs_array.append(find_card(faces[1])[0])
						except:
							print(query + " not found!")
					else:
						copy_array.append(find_card(query)[0])
					print(query, "successfully added to array.")
				else:
					index = 0
					variants = len(find_card(query))
					print("Please choose a version for " + query)
					while index < variants:
						print(str(index+1) + ": " + (find_set(query)[index]))
						index += 1
					
					while True:
						try:
							choice=int(input())
						except ValueError:
							print("Please enter a valid option as displayed above.")
							continue
						if choice > variants:
							print("Please enter a valid option as displayed above.")
							continue
						else:
							break
					copy_array.append(find_card(query)[choice - 1])
					print()
				idx += 1
			
	for file in copy_array:
		version = 1
		origin, cardname = os.path.split(file)
		base, ext = os.path.splitext(file)
		set = file.split("\\")[2]
		copy(file,destination + '\\' + os.path.splitext(cardname)[0] + ' (' + set + ')' + ext)
			
	if backs_array != []:
		try:
			# Create target Directory
			os.mkdir(backs_folder)
			print("Directory " , backs_folder ,  " Created ") 
		except FileExistsError:
			print('')
			
		for file in backs_array:
			version = 1
			origin, cardname = os.path.split(file)
			base, ext = os.path.splitext(file)
			set = file.split("\\")[2]
			copy(file,backs_folder + '\\' + os.path.splitext(cardname)[0] + ' (' + set + ')' + ext)