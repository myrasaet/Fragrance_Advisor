# import csv
import requests
import string
import time
import pygsheets
import pandas as pd
import sys
from bs4 import BeautifulSoup

alphabet = [sys.argv[1]]

url = 'https://www.parfumo.com/Brands/'

cookies = {
    # Insert your cookies here
}

headers = {
    # Insert your headers here
}

def get_brand_sites(base_url,url_iter):
    all_brand_sites = []

    for i in url_iter:
        full_url = "{}{}".format(base_url,i)
        print("Fetching brand URLs for",i,"...")
        response = requests.get(full_url, cookies = cookies, headers = headers)

        if response.status_code == 200:
            html_code = response.text
        else:
            print(f"Failed. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(html_code, 'html.parser')
        elements = soup.find_all('a', class_='p-box mb-1 pl-1 pr-1')
        brand_sites = [element.get('href') for element in elements]
        all_brand_sites += brand_sites
    
    time.sleep(0.1)

    return all_brand_sites

def get_perfume_sites(brands):
    all_perfume_sites = []

    for i in brands:
        print("Fetching perfume URLs for",i.split('/')[-1],"...")
        response = requests.get(i, cookies = cookies, headers = headers)

        if response.status_code == 200:
            html_code = response.content
        else:
            print(f"Failed. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(html_code, 'html.parser')

        #Check if multipage
        pages = soup.find_all('a', href=lambda href: href.startswith(i+'?current_page=') if href else False)
        pages_list = [page['href'] for page in pages]
        page_numbers = []

        for page in pages_list:
            page_number = int(page.split('current_page=')[-1].split('&')[0])
            page_numbers.append(page_number)
        
        if page_numbers:
            max_page_number = max(page_numbers)
        else:
            max_page_number = 0
        
        final_pages = range(1,max_page_number+1)

        if max_page_number > 1:
            perfume_sites = []

            for j in final_pages:
                print("Fetching perfume URLs for",i.split('/')[-1],"Page",j,"...")
                page_response = requests.get(i+'?current_page='+str(j)+'&', cookies = cookies, headers = headers)

                if page_response.status_code == 200:
                    page_html_code = page_response.text
                else:
                    print(f"Failed. Status code: {page_response.status_code}")

                page_soup = BeautifulSoup(page_html_code, 'html.parser')
                page_spans = page_soup.find_all('span',  class_=lambda classes: classes and 'ml-0-5' in classes)

                for span in page_spans:
                    parent_a = span.find_parent('a')
                    perfume_site = parent_a.get('href')
                    perfume_sites.append(perfume_site)
        else:
            response = requests.get(i, cookies = cookies, headers = headers)

            if response.status_code == 200:
                html_code = response.text
            else:
                print(f"Failed. Status code: {response.status_code}")

            soup = BeautifulSoup(html_code, 'html.parser')
            spans = soup.find_all('span',  class_=lambda classes: classes and 'ml-0-5' in classes)

            perfume_sites = []

            for span in spans:
                parent_a = span.find_parent('a')
                perfume_site = parent_a.get('href')
                perfume_sites.append(perfume_site)
        
        # perfume_sites_df = pd.DataFrame(perfume_sites)
        # perfume_sites_df.to_csv(i.split('/')[-1]+'.csv',index=False,header=False)

        all_perfume_sites.extend(perfume_sites)
    
    time.sleep(0.1)

    return all_perfume_sites

def open_gsheets(file_name):
    gdrive = pygsheets.authorize(service_file='credentials.json')
    sheet = gdrive.open(file_name)
    return sheet[0]

def get_perfume_info(perfumes,gsheets):
    for i in perfumes:
        print("Fetching data for",i.split('/')[-1],"...")
        response = requests.get(i, cookies = cookies, headers = headers)

        if response.status_code == 200:
            html_code = response.text
        else:
            print(f"Failed. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(html_code, 'html.parser')

        #fragrance
        try:
            fragrance_h1 = soup.find('h1',class_="p_name_h1",itemprop="name")
            fragrance = fragrance_h1.contents[0].strip()
        except Exception as e:
            fragrance = ""

        #brand
        try:
            url_parts = i.split('/')
            brand_url = '/'.join(url_parts[:-1])
            brand_a = soup.find('a',href=brand_url)
            brand = brand_a.text
        except Exception as e:
            brand = ""

        #perfumer
        try:
            perfumer_div = soup.find('div', class_='p_details_holder_second')
            perfumer_div_c = perfumer_div.find('a', href=lambda x: x and x.startswith('https://www.parfumo.com/Perfumers/'))
            perfumer = perfumer_div_c.text
        except Exception as e:
            perfumer = ""

        #sex
        try:
            sex_div = soup.find('div', class_='p_details_holder')
            sex_div_c = sex_div.find('div', class_=lambda x: x and x.startswith('p_gender_big'))
            sex_div_list = sex_div_c.get('class')
            if 'lightblue' in sex_div_list:
                sex = 'Male'
            elif 'lightpink' in sex_div_list:
                sex = 'Female'
            elif 'lightgreen' in sex_div_list:
                sex = 'Unisex'
            else:
                sex = 'Unknown'
        except Exception as e:
            sex = ""

        #rating
        try:
            rating_span = soup.find('span',itemprop="ratingValue",class_="ratingvalue")
            rating = rating_span.text
        except Exception as e:
            rating = ""

        #scent
        try:
            scent_div = soup.find_all('div',class_="w-100 nowrap")
            for div in scent_div:
                scent_span = div.find('span',class_='blue')
                if scent_span:
                    scent = scent_span.get_text()
                    break
                else:
                    scent = ""
        except Exception as e:
            scent = ""

        #longevity
        try:
            longevity_div = soup.find_all('div',class_="w-100 nowrap")
            for div in longevity_div:
                longevity_span = div.find('span',class_='pink')
                if longevity_span:
                    longevity = longevity_span.get_text()
                    break
                else:
                    longevity = ""
        except Exception as e:
            longevity = ""
            
        #sillage
        try:
            sillage_div = soup.find_all('div',class_="w-100 nowrap")
            for div in sillage_div:
                sillage_span = div.find('span',class_='purple')
                if sillage_span:
                    sillage = sillage_span.get_text()
                    break
                else:
                    sillage = ""
        except Exception as e:
            sillage = ""

        #bottle
        try:
            bottle_div = soup.find_all('div',class_="w-100 nowrap")
            for div in bottle_div:
                bottle_span = div.find('span',class_='green')
                if bottle_span:
                    bottle = bottle_span.get_text()
                    break
                else:
                    bottle = ""
        except Exception as e:
            bottle = ""

        #value_for_money
        try:
            value_for_money_div = soup.find_all('div',class_="w-100 nowrap")
            for div in value_for_money_div:
                value_for_money_span = div.find('span',class_='grey')
                if value_for_money_span:
                    value_for_money = value_for_money_span.text
                    break
                else:
                    value_for_money = ""
        except Exception as e:
            value_for_money = ""

        #main_accords
        try:
            main_accords_div = soup.find_all('div',class_="s-circle-container mb-0-5")
            main_accords = [accord.get_text() for accord in main_accords_div]
            if not main_accords:
                main_accords = ""
        except Exception as e:
            main_accords = ""

        #notes
        try:
            notes_span = soup.find_all('span',attrs={"data-nt":"n"})
            notes = [note.get_text() for note in notes_span]
            if not notes:
                notes = ""
        except Exception as e:
            notes = ""

        #top_notes
        try:
            top_notes_span = soup.find_all('span',attrs={"data-nt":"t"})
            top_notes = [note.get_text() for note in top_notes_span]
            if not top_notes:
                top_notes = ""
        except Exception as e:
            top_notes = ""

        #heart_notes
        try:
            heart_notes_span = soup.find_all('span',attrs={"data-nt":"m"})
            heart_notes = [note.get_text() for note in heart_notes_span]
            if not heart_notes:
                heart_notes = ""
        except Exception as e:
            heart_notes = ""

        #base_notes
        try:
            base_notes_span = soup.find_all('span',attrs={"data-nt":"b"})
            base_notes = [note.get_text() for note in base_notes_span]
            if not base_notes:
                base_notes = ""
        except Exception as e:
            base_notes = ""

        #reviews
        all_reviews = []
        reviews_article = soup.find_all('article',class_=lambda x: x and x.startswith('review_article_'))
        for article in reviews_article:
            
            #username
            article_a = article.find('a',class_='review_user_photo')
            username = article_a.get('href').split('/')[-1]

            #scent
            try:
                scent_span = article.find('span',class_='nr blue')
                scent = scent_span.get_text()
            except Exception as e:
                scent = ""

            #longevity
            try:
                longevity_span = article.find('span',class_='nr red')
                longevity = longevity_span.get_text()
            except Exception as e:
                longevity = ""

            #sillage
            try:
                sillage_span = article.find('span',class_='nr purple')
                sillage = sillage_span.get_text()
            except Exception as e:
                sillage = ""

            #bottle
            try:
                bottle_span = article.find('span',class_='nr green')
                bottle = bottle_span.get_text()
            except Exception as e:
                bottle = ""

            #value_for_money
            try:
                value_for_money_span = article.find('span',class_='nr grey')
                value_for_money = value_for_money_span.get_text()
            except Exception as e:
                value_for_money = ""

            reviews = [username,scent,longevity,sillage,bottle,value_for_money]
            all_reviews.append(reviews)
        
        if not all_reviews:
            all_reviews = ""

        new_perfume = [i,fragrance,brand,perfumer,sex,rating,scent,longevity,sillage,bottle,value_for_money,str(main_accords),str(notes),str(top_notes),str(heart_notes),str(base_notes),str(all_reviews)]
        gsheets.append_table(values=new_perfume, dimension='ROWS', overwrite=False)
        
        scent = ""
        longevity = ""
        sillage = ""
        bottle = ""
        value_for_money = ""

    time.sleep(0.1)

    return

def main():
    all_brands = get_brand_sites(url,alphabet)
    all_perfumes = get_perfume_sites(all_brands)
    gsheets = open_gsheets() # Insert your GSheets file name
    get_perfume_info(all_perfumes,gsheets)

if __name__ == "__main__":
  main()