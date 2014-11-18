import datetime, flask, json, multiprocessing, pymongo, urllib2

app = flask.Flask(__name__)
danbooru_login = "Bouowmx"
danbooru_api_key = "BFVfdHX247_49YwdJznRRvo6dusI6fiEaZIMtW9AO-4"
database_username = "Bouowmx"
database_password = "MarisaKirisame"
database = pymongo.MongoClient("mongodb://" + database_username + ":" + database_password + "@ds051110.mongolab.com:51110/danbooru_tags")["danbooru_tags"]

@app.route("/")
def home():
	return flask.render_template("home.html")

@app.route("/search")
def search():
	if (flask.request.args.get("name") == None):
		return flask.render_template("search.html")
	else:
		# results = json.load(urllib2.urlopen("http://danbooru.donmai.us/login=" + danbooru_login + "&api_key=" + danbooru_api_key + "&search[name_matches]=" + flask.request.args.get("name") + ("&search[category]=" + flask.request.args.get("category")) if (flask.request.args.get("category") != "all") else "" + "&search[hide_empty]=yes&search[order]=" + flask.request.args.get("order") + "&search[has_wiki]=" + flask.request.args.get("has_wiki"))
		#if (flask.request.args.get("exact") == None):
			#database["tags"].find({"name": {"$regex": flask.request.args.get("name")}}, limit = 1000, sort = [("post_count", pymongo.DESCENDING) if flask.request.args.get("
		pass

@app.route("/top")
def top_100(safe = False):
	tags = database["tags"].find(limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_general = database["tags"].find({"category": 0}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_artist = database["tags"].find({"category": 1}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_copyright = database["tags"].find({"category": 3}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	tags_character = database["tags"].find({"category": 4}, limit = 100, sort = [("post_count", pymongo.DESCENDING)])
	return flask.render_template("top.html", safe = safe, tags = tags, tags_general = tags_general, tags_artist = tags_artist, tags_copyright = tags_copyright, tags_character = tags_character, total_posts = database["post_count"].find_one()["post_count"][0])

@app.route("/top/safe")
def top_100_safe():
	return top_100(safe = True)

if (__name__ == "__main__"):
	app.run(debug = True, port = 9001)

