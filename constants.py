import os


TOKEN = '1941449780:AAEw43miqSB_YEfOI_yRZi1aye8Lcz69KgY'


CONNECTION_PARAMETERS = {
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


ROOT = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(ROOT, 'photos')
