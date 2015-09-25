import sys
import urllib3
import mysql.connector as sql
from xml.dom import minidom
from xml.parsers.expat import ExpatError

api_key = "58AE0E6345017543"
db_config = {
  'user': 'slampana',
  'password': 'Campana1',
  'host': '212.47.227.68',
  'database': 'tvdb',
  'raise_on_warnings': True,
}


def db_select(connection, series_id):
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM series WHERE id = %s""", (series_id,))

    row = cursor.fetchone()

    while row is not None:
            print(row[1], "-", row[5], "-", row[9])
            row = cursor.fetchone()

    cursor.close()


def search_series(search_text):
    formatted_search_text = str.replace(search_text, " ", "%20")
    url = "http://thetvdb.com/api/GetSeries.php?seriesname=" + formatted_search_text

    http = urllib3.PoolManager()
    r = http.request('GET', url)
    xml = minidom.parseString(r.data)

    for node in xml.getElementsByTagName('Series'):
        print(node.getElementsByTagName('seriesid')[0].firstChild.data, "-", sep='', end='')
        print(node.getElementsByTagName('SeriesName')[0].firstChild.data, "-", sep='', end='')
        print(node.getElementsByTagName('FirstAired')[0].firstChild.data, sep='')


def get_series_details(series_id):
    url = "http://thetvdb.com/api/" + api_key + "/series/" + str(series_id) + "/all"

    http = urllib3.PoolManager()
    r = http.request('GET', url)
    xml = minidom.parseString(r.data)

    for node in xml.getElementsByTagName('Series'):
        print(node.getElementsByTagName('id')[0].firstChild.data, "-", sep='', end='')
        print(node.getElementsByTagName('SeriesName')[0].firstChild.data, "-", sep='', end='')
        print(node.getElementsByTagName('FirstAired')[0].firstChild.data, sep='')
        print(node.getElementsByTagName('Genre')[0].firstChild.data.split("|")[1:-1])
        print(node.getElementsByTagName('Status')[0].firstChild.data, sep='')


def get_episode_details(series_id):
    url = "http://thetvdb.com/api/" + api_key + "/series/" + str(series_id) + "/all"

    http = urllib3.PoolManager()
    r = http.request('GET', url)
    xml = minidom.parseString(r.data)

    for node in xml.getElementsByTagName('Episode'):
        season = int(node.getElementsByTagName('SeasonNumber')[0].firstChild.data)
        episode = int(node.getElementsByTagName('EpisodeNumber')[0].firstChild.data)
        if season > 0:
            print(node.getElementsByTagName('id')[0].firstChild.data, "-", sep='', end='')
            print("S", "{:0>2d}".format(season), "E", "{:0>2d}".format(episode), "-", sep='', end='')
            print(node.getElementsByTagName('EpisodeName')[0].firstChild.data, sep='')


def main_get_series_details():
    try:
        search_text = input("Series Name: ")
        search_series(search_text)

        series_id = input("Series ID: ")
        get_series_details(series_id)
        get_episode_details(series_id)
    except IOError as e:
        print("I/O ERROR: ", e)
    except ExpatError as e:
            print("ERROR WITH API PAGE: ", e)
    except:
        print("UNEXPECTED ERROR:", sys.exc_info()[0])
        raise

    try:
        connection = sql.connect(**db_config)

        db_select(connection, str(series_id))
    except sql.Error as e:
        print("ERROR WITH SQL CONNECTION: ", e)
    except ExpatError as e:
            print("ERROR WITH API PAGE: ", e)
    except:
        print("UNEXPECTED ERROR:", sys.exc_info()[0])
        raise
    finally:
        if connection:
            connection.close()


main_get_series_details()