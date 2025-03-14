import requests
import pandas as pd

base_url = "https://goadmin.ifrc.org"

def collect_all(endpoint, content):
    api_endpoint = f"/api/v2/{endpoint}/"
    link = base_url + api_endpoint
    bucket = {
        "id" : [],
        "content" : []
    }
    try:
        while link != None:
            print(f"Calling {link}...")
            res = requests.get(link)
            if res.status_code == 200:
                res_val = res.json()
                temp = res_val["results"]
                for item in temp:
                    bucket["id"].append(item["id"])
                    bucket["content"].append(item[content])
                link = res_val["next"]
            else:
                print("Invalid response statuse code received: ", res.status_code)
                return
    
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)
    
    df = pd.DataFrame(bucket)
    df.set_index("id", inplace=True)
    df.to_csv(f"../aux_data/{endpoint}.csv")

collect_all("disaster_type", "name")
collect_all("country", "iso3")
collect_all("per-formcomponent", "title")
