import pandas as pd
import re
from googleplaces import GooglePlaces, types, lang
import numpy as np
ready=['groceries']#put in category names you want to search,need to prepare the namelist for stores
type_codes=[40]#put in corresponding type_code you want to search for each category, remember only one for each category
GOOGLE_MAPS_KEY = ""#please enter your own google maps key here
google_places = GooglePlaces(GOOGLE_MAPS_KEY)
keyworddic={'bars':'bar','cafe':'cafe','brewery':'liquor','groceries':None}
with open('D:\\fieldlist.txt') as f:
    lines = f.readlines()
lines_c=[]
typesdic={}
for i in range(len(lines)):
    typesdic[i+1]=re.sub('\n','',lines[i])#type_code reference
print(typesdic)
def check(kind,keyword,type_code):#goal of this function is to find nearby stores around ones we scraped
    #keywords are other details you want to add for search, put them into keyworddic,please check https://developers.google.com/maps/documentation/places/web-service/search-nearby for format of keywords
    #type_code refers to the kind of stores you want to search for,see fieldlist.txt/typesdic to check the name the code referring to
    final={'Name':[],'Address':[],'location':[],'Price_level':[],'rating':[],'user_ratings_total':[],'phone_number':[],
           'international':[],'reviews':[],'photo':[],'website':[],'Type':[],'Opening_Hour':[],'Pairing':[]}#dict for constructing dataframe
    waiting_str='D://'+kind
    waiting_str+='.csv'
    waiting=pd.read_csv(waiting_str,encoding = "ISO-8859-1")
    waiting.drop_duplicates(subset=['Name'])
    check=0#set only for groceries due to the fact that most of the groceries don't have real address, which means most of them will turn out duplicate results
    for i in range(len(waiting)):
        name=waiting.loc[i]['Name']# name of stores you scraped
        address=waiting.loc[i]['Address']# address of stores you scraped
        query_result=None
        if address is np.nan:#in case the store doesn't have real address
            location='Boston,United States'#put in the address of the whole district you want to check
            if check<1:
                query_result = google_places.text_search(
                    location=location,radius=2000, types=[typesdic[type_code]])# please check https://developers.google.com/maps/documentation/places/web-service/search-text for more instructions of this function
                if kind=='groceries':
                    check+=1
            name=None#in this case the search results don't have specific pairing(cause we are using address of the whole district)
        else:
            address=re.sub('\(.*\)','',address)
            if address!='Boston':#the store has real, specific address
                address+=',Boston'#some stores are chained, make sure we only get the stores in desired district
                query_result = google_places.nearby_search(
                location=address, keyword=keyword,
                radius=2000, types=[typesdic[type_code]])# please check https://developers.google.com/maps/documentation/places/web-service/search-nearby for more instructions of this function
            else:#the store has real address but we only know the district
                location='Boston,United States'
                if check<1:
                    query_result = google_places.text_search(
                        query=location,radius=2000, types=[typesdic[type_code]])
                    if kind=='groceries':
                        check+=1
                name=None
        if query_result:
            for place in query_result.places:
                place.get_details()
                details=place.details#please check https://developers.google.com/maps/documentation/places/web-service/details for contents inside this attribute
                print(details)
                final['Name'].append(details['name'])
                final['Address'].append(details['vicinity'])
                if 'geometry' in details:#in case if this item was not included in final results
                    final['location'].append(details['geometry']['location'])
                else:
                    final['location'].append('Not Found')
                if 'price_level' in details:
                    final['Price_level'].append(details['price_level'])
                else:
                    final['Price_level'].append('Not Found')
                if 'rating' in details:
                    final['rating'].append(details['rating'])
                else:
                    final['rating'].append('Not Found')
                if 'user_ratings_total' in details:
                    final['user_ratings_total'].append(details['user_ratings_total'])
                else:
                    final['user_ratings_total'].append('Not Found')
                if 'opening_hours' in details:
                    final['Opening_Hour'].append(details['opening_hours'])
                else:
                    final['Opening_Hour'].append('Not Found')
                if 'formatted_phone_number' in details:
                    final['phone_number'].append(details['formatted_phone_number'])
                else:
                    final['phone_number'].append('Not Found')
                if 'international_phone_number' in details:
                    final['international'].append(details['international_phone_number'])
                else:
                    final['international'].append('Not Found')
                if 'reviews' in details:
                    final['reviews'].append(details['reviews'])
                else:
                    final['reviews'].append('Not Found')
                if 'photos' in details:
                    final['photo'].append(details['photos'])
                else:
                    final['photo'].append('Not Found')
                if 'website' in details:
                    final['website'].append(details['website'])
                else:
                    final['website'].append('Not Found')
                final['Type'].append(details['types'])
                final['Pairing'].append(name)#pair the results and stores we scraped
        res=pd.DataFrame.from_dict(final)
        res_str='D:\\google_'+kind+'.csv'
        res.to_csv(res_str)#save the final results as csv file
ind=0
for i in ready:
    check(i,keyworddic[i],type_codes[ind])
    ind+=1


