import datetime, flask, json, multiprocessing, pymongo, urllib2

app = flask.Flask(__name__)
danbooru_login = "Bouowmx"
danbooru_api_key = "BFVfdHX247_49YwdJznRRvo6dusI6fiEaZIMtW9AO-4"
database_username = "Bouowmx"
database_password = "MarisaKirisame"

@app.route("/")
def top_100():
	tags = database_connection()["danbooru_tags"]["tags"].find(limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_general = database_connection()["danbooru_tags"]["tags"].find({"category": 0}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_artist = database_connection()["danbooru_tags"]["tags"].find({"category": 1}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_copyright = database_connection()["danbooru_tags"]["tags"].find({"category": 3}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_character = database_connection()["danbooru_tags"]["tags"].find({"category": 4}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	total_posts = json.load(urllib2.urlopen("http://danbooru.donmai.us/posts.json?login=" + danbooru_login + "&api_key=" + danbooru_api_key))[0]["id"]
	return flask.render_template("home.html", tags = tags, tags_general = tags_general, tags_artist = tags_artist, tags_copyright = tags_copyright, tags_character = tags_character, total_posts = total_posts)

def database_connection():
	return pymongo.MongoClient("mongodb://" + database_username + ":" + database_password + "@ds051110.mongolab.com:51110/danbooru_tags")

def tags_aliases_update():
	connection = pymongo.MongoClient("")
	collection = connection["danbooru_tags"]["tags"]
	collection_aliases = connection["danbooru_tags"]["tags_aliases_pending"]
	#Check if currently pending aliases in database have become active
	aliases = collection_aliases.find()
	i = 0
	while (i < aliases.count()):
		alias = json.load(urllib2.urlopen("http://danbooru.donmai.us/tag_aliases.json?login=" + danbooru_login + "&api_key=" + danbooru_api_key + "&search[antecedent_name]=" + aliases[i]["antecedent_name"]))
		if (alias["status"] == "active"):
			#ADD THIS LINE!!!!! ADD THIS LINE!!! -> delete alias from database
			tag = collection.find_one({"name": aliases[i]["antecedent_name"]})
			collection.update({"name": aliases[i]["antecedent_name"]}, {"name": alias["consequent_name"], "post_count": tag["post_count"], "category": tag["category"]})
	#Add pending aliases
	i = 0
	while (True):
		aliases = json.load(urllib2.urlopen("http://danbooru.donmai.us/tag_aliases.json?login=" + danbooru_login + "&api_key=" + danbooru_api_key + "&limit=1000&page=" + str(i)))
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

def tags_update(num_processes):
	processes = []
	i = 1
	while (i <= num_processes): #Each process requires maximum 9.5 MB of RAM.
		processes.append(multiprocessing.Process(target = tags_update_child, args = (i, num_processes)))
		processes[i - 1].start()
		i += 1
	print "Time elapsed: " + str(t2 - t1) + " s"

def tags_update_child(page, increment):
	collection = database_connection()["danbooru_tags"]["tags"]
	while (True):
		tags = json.load(urllib2.urlopen("http://danbooru.donmai.us/tags.json?login=" + danbooru_login + "&api_key=" + danbooru_api_key + "&search[order]=count&limit=1000&page=" + str(page)))
		if (page == []):
			return
		for tag in tags:
			cursor = collection.find({"name": tag["name"]})
			post_count = []
			if (cursor.count() > 0):
				post_count = cursor[0]["post_count"]
			#post_count.append(tag["post_count"])
			post_count = [tag["post_count"]] + post_count
			collection.update({"name": tag["name"]}, {"name": tag["name"], "post_count": post_count, "created_at": tag["created_at"][:tag["created_at"].index("T")] if tag["created_at"] is not None else None, "category": tag["category"]}, upsert = True)
		page += increment

if (__name__ == "__main__"):
	app.run(debug = True, port = 9001)

