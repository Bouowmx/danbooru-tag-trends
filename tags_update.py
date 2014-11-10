import datetime, json, multiprocessing, pymongo, urllib2
from time import time

def tags_update(num_processes):
	t1 = time()
	processes = []
	i = 1
	while (i <= num_processes): #Each process requires maximum 9.5 MB of RAM.
		processes.append(multiprocessing.Process(target = tags_update_child, args = (i, num_processes)))
		processes[i - 1].start()
		i += 1
	t2 = time()
	print "Time elapsed: " + str(t2 - t1) + " s"

def tags_update_child(page, increment):
	connection = pymongo.MongoClient("mongodb://Bouowmx:ReimuHakurei@ds051110.mongolab.com:51110/danbooru_tags")
	collection = connection["danbooru_tags"]["tags"]
	while (True):
		tags = json.load(urllib2.urlopen("http://danbooru.donmai.us/tags.json?login=Bouowmx&api_key=BFVfdHX247_49YwdJznRRvo6dusI6fiEaZIMtW9AO-4&search[order]=count&limit=1000&page=" + str(page)))
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
	tags_update(100)