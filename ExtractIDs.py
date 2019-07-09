import string
import requests
from bs4 import BeautifulSoup

def regxUrl(url_list, outputFile):
    IDlists = []
    for url in url_list:
        IDlists.append(url.split("/id", 1)[1])
    IDlists = list(dict.fromkeys(IDlists))

    file = open(outputFile, "w+")
    for id in IDlists:
        file.write(id + "\n")
    file.close()

def GetURLList(url):
    html = url.text
    soup = BeautifulSoup(html, 'html.parser')
    selectedContent = soup.find('div', {'id': 'selectedcontent'})
    li_list = selectedContent.find_all('li')
    urls = []
    for li in li_list:
        a_tag = li.find('a', href=True)
        urls.append(a_tag['href'])
    return urls

def GetIDs(category, outputFile):
    alphabets = list(string.ascii_uppercase)
    if category == "Health":
        category_base_url = "https://apps.apple.com/us/genre/ios-health-fitness/id6013"
    else:
        category_base_url = "https://apps.apple.com/us/genre/ios-education/id6017"
    urls = GetURLList(requests.get(category_base_url))
    for letter in alphabets:
        for pageNumber in range(130):
            print(letter, pageNumber)
            url = requests.get(category_base_url + "?letter="+letter+"&page="+str(pageNumber)+ "#page")
            urls.extend(GetURLList(url))
    regxUrl(urls, outputFile)

# regxUrl(GetURLList(requests.get("https://apps.apple.com/us/genre/ios-education/id6017")),'educationOut.txt')

# def removeDuplicates():
#     with open("merge.txt") as f:
#         IDlists = f.readlines()
#     print(len(IDlists))
#     IDlists = list(dict.fromkeys(IDlists))
#     file = open("EducationIds_Final.txt", "w+")
#     for id in IDlists:
#         file.write(id)
#     file.close()
#     print(len(IDlists))