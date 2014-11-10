import json, pymongo, urllib2

login = "Bouowmx"
api_key = "<key>"

def tags_aliases_update():
    connection = pymongo.MongoClient("")
    collection = connection["danbooru_tags"]["tags"]
    collection_aliases = connection["danbooru_tags"]["tags_aliases_pending"]
    #Check if currently pending aliases in database have become active
    aliases = collection_aliases.find()
    i = 0
    while (i < aliases.count()):
        alias = json.load(urllib2.urlopen("http://danbooru.donmai.us/tag_aliases.json?login=Bouowmx&api_key=<key>&search[antecedent_name]=" + aliases[i]["antecedent_name"]))
        if (alias["status"] = "active"):
            #ADD THIS LINE!!!!! ADD THIS LINE!!! -> delete alias from database
            tag = collection.find_one({"name": aliases[i]["antecedent_name"]})
            collection.update({"name": aliases[i]["antecedent_name"]}, {"name": alias["consequent_name"], "post_count": tag["post_count"], "category": tag["category"]})
    #Add pending aliases
    i = 0
    while (True):
        aliases = json.load(urllib2.urlopen("http://danbooru.donmai.us/tag_aliases.json?login=Bouowmx&api_key=<key>&limit=1000&page=" + str(i)))
        if (aliases == []):
            break
        active_reached = False
        for alias in aliases:
            if (alias["status"] == "active"):
                active_reached = True
                break
            collection_aliases.update({"antecedent_name": alias["antecedent_name"]}, {"antecedent_name": alias["antecedent_name"], "consequent_name": alias["consequent_name"]}, upsert = True)
        if (active_reached):
            break
    pass

def top_100():
    #Connect to database
    tags = collection.find(limit = 100) #Check this line
    #Somehow get the total number of posts
    return render_template("home.html", tags = tags)
