from flask import Flask
from flask import request
import pymongo
import pprint
import json
import math
import bson
import bson.json_util
import os
from datetime import datetime
import re
import helper

user_home = os.path.expanduser("~")
config_path = user_home + "/.config/chiania-www/config.json"

config={
    "spacescan":{
        "api_url":"spacescanApiUrl",
        "api_key":"spacescanApiKey"
    },
    "mintgarden":{
        "api_url":"mintgardenaApiUrl"
    },
    "mongodb":{
        "server":"localhost",
        "database":"mongo_database",
        "user":"dbuser",
        "password":"dbpassword"
    }
}


if(os.path.exists(config_path)):
    with open(config_path,"r") as file:
        config=json.load(file)
else:
    with open(config_path,"w") as file:
        file.write(json.dumps(config,indent=2))

mongo = pymongo.MongoClient("mongodb+srv://" + config['mongodb']['user'] + 
        ":" + config['mongodb']['password'] +"@" + config['mongodb']['server'] +
        "/?retryWrites=true&w=majority")

#db is "chiania"
db = mongo.chiania

result_size=5

app = Flask(__name__)

@app.route("/")
def home():
    return "Chiania Api"

@app.route("/nfts", methods=["GET"])
def nfts():
    error=None
    qargs={}
    out=''

    if request.method == "GET":
        page=0
        if helper.is_integer(request.args.get("page")):
            page=int(request.args.get("page"))
        start=page*result_size
        end=start+result_size
        
        for arg in ["nft_id","collection_id","owner_encoded_id","owner_address_encoded_id",
                    "creator_encoded_id","creator_address_encoded_id","creator_name",
                    "ItemStatus","Name","ItemCategory","ItemType","Prefix","Collection"]:
            if request.args.get(arg) is not None:
                #out+=request.args.get(arg)
                qargs[arg]=request.args.get(arg)
        count_cursor=db.items.aggregate([
                { "$match": qargs},
                { "$count": "count" }
            ])
        count_list=list(count_cursor)
        count=count_list[0]['count']
        data_cursor=db.items.find(qargs).sort(
            [("Nr",pymongo.ASCENDING),("Name",pymongo.ASCENDING)]
            ).skip(start).limit(result_size)
        data_list=list(data_cursor)
        out_dict={
            "status":"success",
            "paging":{
                "page": page,
                "last_page": math.floor(count/result_size),
                "start": start,
                "end": end,
                "count":count
            },
            "data": data_list,
        }
        out=bson.json_util.dumps(out_dict,indent=2)
    return out
@app.route("/item_categories", methods=["GET"])
def item_categories():
    error=None
    out=''
    
    data_cursor=db.items.aggregate(
        [{"$group":{
                    "_id":"$ItemCategory",
                    "count":{"$sum":1}
                   }}])
    data_list=list(data_cursor)
    out_dict={
        "status":"success",
        "paging":{
            "page": 0,
            "last_page": 0
        },
        "data": data_list,
    }
    out=bson.json_util.dumps(out_dict,indent=2)
    return out
