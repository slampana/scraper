from datetime import datetime

import urllib3
from bs4 import BeautifulSoup

from globals import *


def db_select_imdb_show_list():
    # fetch the list of all shows to get details for
    print("Fetching all shows...")
    id_list = collection_show.find({"order": {"$gt": 0}}, {'id': 1, 'order': 1, '_id': 0}).sort([("order", 1)])

    return id_list


def db_select_imdb_season_list(show_id):
    # fetch the list of all shows to get details for
    print("Fetching all seasons...")
    id_list = collection_show.find({"id": show_id}, {'season.id': 1, '_id': 0}).sort([("season.id", 1)])
    print("Done fetching seasons...")

    return id_list


def imdb_fetch_episode_details():
    # declare variables
    start_time = datetime.now()
    count = 1

    # get show list
    ids = db_select_imdb_show_list()

    # process each show returned from the show list
    for id in ids:
        # declare variables
        show_id = id['id']
        order = id['order']
        timestamp = datetime.now()
        seasons = db_select_imdb_season_list(show_id)

        for season_list in seasons:
            if len(season_list) != 0:
                for season in season_list.get("season"):
                    season_id = season['id']
                    valid_url = True
                    url = "http://www.imdb.com/title/" + show_id + "/episodes?season=" + season_id
                    http = urllib3.PoolManager()

                    # make sure http request is valid
                    try:
                        r = http.request('GET', url)
                    except:
                        valid_url = False
                        print("Problem with URL data returned.")
                        pass

                    # print details for console tracking
                    print(order, url)

                    # proceed with the process is there's a valid http response
                    if valid_url:
                        # soup the data returned from the http request
                        soup = BeautifulSoup(r.data, 'html.parser')

                        # setup soups
                        try:
                            soup_episode = soup.find_all("div", {"class": lambda l: l and l.startswith('list_item')})
                        except IndexError:
                            soup_episode = None
                            pass

                        # parse soups and input data into show dict
                        if soup_episode is not None:
                            episode_list = []
                            for episode in soup_episode:
                                id = episode.find_all('meta')[0]['content'].strip()
                                name = episode.find_all("div", {"itemprop": "episodes"})[0].find_all('a')[0].get_text().strip()
                                try:
                                    description = episode.find_all("div", {"itemprop": "description"})[0].get_text().strip()
                                    if "Add a Plot" in description:
                                        description = "Not yet available."
                                except IndexError:
                                    print("No description found.")
                                    description = "Not yet available."
                                    pass
                                try:
                                    air_date = episode.find_all("div", {"class": "airdate"})[0].get_text().strip()
                                except IndexError:
                                    print("No air date found.")
                                    air_date = "Not yet available."
                                    pass
                                try:
                                    image = episode.find_all('img')[0]['src'].strip()
                                except KeyError:
                                    image = "http://ia.media-imdb.com/images/G/01/imdb/images/nopicture/200x112/tv-3053553855._CB332471307_.png"
                                episode_dict = ({"id": id, "name": name, "description": description, "air_date": air_date, "image": image})
                                episode_list.append(episode_dict)
                            collection_show.update({"id": show_id, "season.id": season_id}, {"$unset": {"season.$.episode": 1}}, False, False)
                            collection_show.update({"id": show_id, "season.id": season_id}, {"$set": {"season.$.episode": episode_list, "season.$.timestamp": timestamp}})
                        else:
                            print("No episode found")

                        count += 1
                        collection_show.update_one({"id": show_id}, {"$set": {"episode_fetched": True}})

                    else:
                        count += 1
            else:
                count += 1
                collection_show.update_one({"id": show_id}, {"$set": {"episode_fetched": True}})
                print("No seasons found for", show_id)

    # print process results
    print("Process complete. ", count-1, "shows processed.")
    end_time = datetime.now()
    duration = end_time - start_time
    print("Start time: ", str(start_time))
    print("End time: ", str(end_time))
    print("Total duration (minutes): ", str(duration.seconds / 60))


imdb_fetch_episode_details()


