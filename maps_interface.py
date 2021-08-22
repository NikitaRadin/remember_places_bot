import requests
import constants


class MapsInterface:
    @staticmethod
    def get_distance(departure_longitude, departure_latitude, destination_longitude, destination_latitude):
        payload = {
            'points': [
                {
                    'x': departure_longitude,
                    'y': departure_latitude,
                    'type': 'pedo'
                },
                {
                    'x': destination_longitude,
                    'y': destination_latitude,
                    'type': 'pedo'
                }
            ],
            'locale': 'en',
            'type': 'pedestrian'
        }
        return requests.post(url=f'https://catalog.api.2gis.ru/carrouting/6.0.0/global?'
                                 f'key={constants.DGIS_MAPS_API_KEY}',
                             json=payload).json()['result'][0]['total_distance']

    @staticmethod
    def get_close_places_map(departure_coordinates, places_coordinates):
        places_coordinates_ = places_coordinates[:constants.MAXIMUM_PLACES_ON_MAP_NUMBER]
        places_coordinates_ = '&'.join(f'pt={places_coordinates_[index][0]},'
                                       f'{places_coordinates_[index][1]}~n:{index + 1}'
                                       for index in range(len(places_coordinates_)))
        return requests.get(url=f'https://static.maps.2gis.com/1.0?s={constants.MAP_WIDTH}x{constants.MAP_HEIGHT}&'
                                f'pt={departure_coordinates[0]},{departure_coordinates[1]}~c:rd&'
                                f'{places_coordinates_}').content
