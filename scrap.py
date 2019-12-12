# import json
import random

# with open("captions.json") as fp:
#     data = json.load(fp)
# for item in data:
#     # print(item)
#     # print(item["filename"])
#     ls = item["caption"]
#     print(item["filename"] + "#0" + "   " + ls[0])
#     print(item["filename"] + "#1" + "   " + ls[1])
#
#     with open("Flickr_8k.devImages.txt", "a") as text_file:
#         # text_file.write(item["filename"] + "#0" + "   " + ls[0] + "\n")
#         # text_file.write(item["filename"] + "#1" + "   " + ls[1] + "\n")
#
#         text_file.write(item["filename"] + "\n")
#
#     # for s in item:
#     #     print(s)
#     # for key, value in item:
#     # print(key)
# with open("Flickr_8k.devImages.txt", "a") as text_file:
#     for count in range(800):
#         # Get a random number.
#         num = random.randint(1, 7500)
#
#         # Write 12 random intergers in the range of 1-100 on one line
#         # to the file.
#         text_file.write(str(num) + ".png" + "\n")

# fin = open("./Flickr8k_text/Flickr8k.token.txt", "rt")
# fout = open("./Flickr8k_text/out.txt", "a")
#
# for desc in fin:
#     for x in desc:
#         fout.write(x.replace('দুই', 'দুই'))
#         fout.write(x.replace('৩', 'তিন'))
#
# fin.close()
# fout.close()

filename = '../Flickr8k_text/Flickr_8k.token.txt'
# load descriptions
file = open(filename, 'r')
# read all text
text = file.read()
# close the file
file.close()

# define punctuation
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

my_str = "Hello!!!, he said ---and went."

# To take input from the user
# my_str = input("Enter a string: ")

# remove punctuation from the string
no_punct = ""
for char in my_str:
    if char not in punctuations:
        no_punct = no_punct + char

# display the unpunctuated string
print(no_punct)
