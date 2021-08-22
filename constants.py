import os


TELEGRAM_BOT_API_TOKEN = ''


DATABASE_SERVER_CONNECTION_PARAMETERS = {
  'host': '127.0.0.1',
  'port': '5432',
  'user': 'postgres',
  'password': '299792458'
}
DATABASE = 'remember_places_bot'
MAXIMUM_NAME_LENGTH = 100
MAXIMUM_PHOTO_PATH_LENGTH = 1000


NEUTRAL = 0
NAME = 1
LOCATION = 2
PHOTO = 3
DEPARTURE = 4


ROOT = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(ROOT, 'photos')


DGIS_MAPS_API_KEY = ''
MAXIMUM_DISTANCE = 5000
MAXIMUM_PLACES_ON_MAP_NUMBER = 99
MAP_WIDTH = 1280
MAP_HEIGHT = 1280
