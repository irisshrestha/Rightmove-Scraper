from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
import csv
def find_property(complex):
    #Load website
    #Set up header and cookies to try to emulate browser before sending request
    session = HTMLSession()
    user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    url = "https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E1460&insId=1&radius=0.0&minPrice=150000&maxPrice=325000&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false"
    cookies = session.head(url)

    #Rightmove is a dynamic website, so the website seen on browser is not the same as seem through requests
    original_site = session.get(url, headers=user_agent, allow_redirects=False, cookies = cookies)
    #Use requests_html to dynamically render the website as if it was run through a browser
    original_site.html.render()
    #Extract html text to feed into beautiful soup
    original_html_text = original_site.html.html

    ##################################################################
    #Start of scraping
    #################################################################
    #Use beautiful soup to read the code and find the property cards on Rightmove
    soup = BeautifulSoup(original_html_text, "lxml")
    properties = soup.find_all("div", class_="propertyCard-wrapper")

    #Create list to store information in
    property_info = []

    #Go through each property card and extract information
    for property in properties:
        #Extract basic information
        price = property.find("div", class_="propertyCard-priceValue").text.replace(" ", "")
        address = property.find("div", class_="propertyCard-details").a.address.text
        property_type_info = property.find("div", class_="property-information").find_all("span",class_="text")
        property_type = property_type_info[0].text
        no_bedrooms = property_type_info[1].text
        #Find if shared ownership
        property_description = property.find("div", class_="propertyCard-description").text
        if "shared" in property_description.lower():
            shared_owner = "Yes"
        else:
            shared_owner = "No"
        # find main link of property to extract further information from it
        link = f"https://www.rightmove.co.uk{property.find("a", class_="propertyCard-link")["href"]}"

        #For complex information
        if complex == 1:
            #Go into the link
            cookies2 = session.head(link)
            individual_site = session.get(link,headers=user_agent, allow_redirects=False, cookies = cookies2)
            individual_site.html.render()
            individual_html_text = individual_site.html.html

            soup2 = BeautifulSoup(individual_html_text, "lxml")

            #Extract tenure information
            tenure_info_all = soup2.find_all("div", class_ = "_3ZGPwl2N1mHAJH3cbltyWn")
            for info in tenure_info_all:
                if "freehold" in info.text.lower():
                    tenure = "Freehold"
                    break
                if  "leasehold" in info.text.lower():
                    tenure = "Leasehold"
                    break
                else:
                    tenure = "Not provided"

            #Can use full description to get further information in future
            full_description = soup2.find("div", class_="STw8udCxUaBUMfOOZu0iL _3nPVwR0HZYQah5tkVJHFh5")


        #Set complex variables to be blank
        else:
            tenure =""

        ##################################################################
        # Prepare function output
        #################################################################

        # Put information into a list
        individual_property_info = [price, property_type, shared_owner, no_bedrooms, link, tenure]
        # Add info back into main list
        property_info.append(individual_property_info)

    return property_info


#########################################################################
#Start of inputs
#########################################################################
while True:
    question = input("Would you like a basic or comprehensive information of the properties?: ")
    if question.lower()=="basic":
        complexity = 0
        field = ["Price", "Type", "Shared ownership", "Bedrooms", "Link"]
        break
    elif question.lower()=="complex" or question.lower()=="comprehensive":
        complexity = 1
        field = ["Price", "Type", "Shared ownership", "Bedrooms", "Link", "Tenure"]
        break
    else:
        print("Invalid choice")

while True:
    question = input("Would you like a csv output or just text: ")
    if question.lower()=="text":
        output_type = 0
        break
    elif question.lower()=="csv":
        output_type = 1
        break
    else:
        print("Invalid choice")


#########################################################################
#Run function
#########################################################################
property_info = find_property(complexity)



#########################################################################
#Outputs
#########################################################################
#Produce desired output
if output_type == 0:
    for i in range(0,len(property_info)):
        for j in range(0, len(field)):
            print(f"{field[j]}:{property_info[i][j]} ")

        print("\n")

elif output_type == 1:
    #Write all the info into a csv
    with open("properties.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(field)
        for i in range(0,len(property_info)):
            writer.writerow(property_info[i])
    print("Properties.csv created.")


#Print a summary
print("\n")
print(f"Output provided for {len(property_info)} properties")


