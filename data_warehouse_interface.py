import constants
import psycopg2
import os


class DataWarehouseInterface:
    def __init__(self):
        self.connection = None
        self.cursor = None

    @staticmethod
    def _get_connection_parameters(include_database):
        connection_parameters = constants.DATABASE_SERVER_CONNECTION_PARAMETERS.copy()
        if include_database:
            connection_parameters['database'] = constants.DATABASE
        return connection_parameters

    def connect_to_database(self):
        try:
            self.connection = psycopg2.connect(**self._get_connection_parameters(include_database=True))
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
        except psycopg2.OperationalError:
            try:
                connection = psycopg2.connect(**self._get_connection_parameters(include_database=False))
                connection.autocommit = True
                cursor = connection.cursor()
                cursor.execute(query=f'CREATE DATABASE {constants.DATABASE};')
                self.connection = psycopg2.connect(**self._get_connection_parameters(include_database=True))
                self.connection.autocommit = True
                self.cursor = self.connection.cursor()
                self.cursor.execute(query='CREATE TABLE users\n'
                                          '(\n'
                                          '    user_id INT PRIMARY KEY,\n'
                                          '    step    SMALLINT NOT NULL\n'
                                          ');')
                self.cursor.execute(query=f'CREATE TABLE places\n'
                                          f'(\n'
                                          f'    place_id   SERIAL PRIMARY KEY,\n'
                                          f'    user_id    INT NOT NULL REFERENCES users(user_id),\n'
                                          f'    name       VARCHAR({constants.MAXIMUM_NAME_LENGTH}) NULL,\n'
                                          f'    latitude   FLOAT8 NULL,\n'
                                          f'    longitude  FLOAT8 NULL,\n'
                                          f'    photo_path VARCHAR({constants.MAXIMUM_PHOTO_PATH_LENGTH}) NULL\n'
                                          f');')
            except psycopg2.OperationalError:
                raise ConnectionError('Connection to the database server could not be established')

    def does_user_exist(self, user_id):
        self.cursor.execute(query=f'SELECT\n'
                                  f'    user_id\n'
                                  f'FROM users\n'
                                  f'WHERE user_id = {user_id};')
        return bool(self.cursor.fetchall())

    def add_user(self, user_id):
        if self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id already exists')
        self.cursor.execute(query=f'INSERT INTO users\n'
                                  f'(\n'
                                  f'    user_id,\n'
                                  f'    step\n'
                                  f')\n'
                                  f'VALUES\n'
                                  f'(\n'
                                  f'    {user_id},\n'
                                  f'    {constants.NEUTRAL}\n'
                                  f');')

    def update_step(self, user_id, step):
        if not self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id does not exist')
        self.cursor.execute(query=f'UPDATE users\n'
                                  f'SET\n'
                                  f'    step = {step}\n'
                                  f'WHERE user_id = {user_id};')

    def get_step(self, user_id):
        if not self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id does not exist')
        self.cursor.execute(query=f'SELECT\n'
                                  f'    step\n'
                                  f'FROM users\n'
                                  f'WHERE user_id = {user_id};')
        return self.cursor.fetchall().pop()[0]

    def add_place(self, user_id):
        if not self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id does not exist')
        self.cursor.execute(query=f'INSERT INTO places\n'
                                  f'(\n'
                                  f'    user_id\n'
                                  f')\n'
                                  f'VALUES\n'
                                  f'(\n'
                                  f'    {user_id}\n'
                                  f');')

    def _get_maximum_place_id(self, user_id):
        if not self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id does not exist')
        self.cursor.execute(query=f'SELECT\n'
                                  f'    MAX(place_id)\n'
                                  f'FROM places\n'
                                  f'WHERE user_id = {user_id};')
        maximum_place_id = self.cursor.fetchall().pop()[0]
        if maximum_place_id is None:
            raise ValueError('The user has not added any places yet')
        return maximum_place_id

    def update_name(self, user_id, name):
        self.cursor.execute(query=f'UPDATE places\n'
                                  f'SET\n'
                                  f'    name = \'{name}\'\n'
                                  f'WHERE place_id = {self._get_maximum_place_id(user_id=user_id)};')

    def update_location(self, user_id, latitude, longitude):
        self.cursor.execute(query=f'UPDATE places\n'
                                  f'SET\n'
                                  f'    latitude = {latitude},\n'
                                  f'    longitude = {longitude}\n'
                                  f'WHERE place_id = {self._get_maximum_place_id(user_id=user_id)};')

    def update_photo(self, user_id, photo_content):
        place_id = self._get_maximum_place_id(user_id=user_id)
        photo_path = os.path.join(constants.PHOTOS, f'{place_id}.jpg')
        with open(file=photo_path, mode='wb') as photo_file:
            photo_file.write(photo_content)
        self.cursor.execute(query=f'UPDATE places\n'
                                  f'SET\n'
                                  f'    photo_path = \'{photo_path}\'\n'
                                  f'WHERE place_id = {place_id};')

    def get_all_places(self, user_id):
        if not self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id does not exist')
        self.cursor.execute(query=f'SELECT\n'
                                  f'    place_id,\n'
                                  f'    user_id,\n'
                                  f'    name,\n'
                                  f'    latitude,\n'
                                  f'    longitude,\n'
                                  f'    photo_path\n'
                                  f'FROM places\n'
                                  f'WHERE user_id = {user_id};')
        return self.cursor.fetchall()

    def get_place(self, place_id):
        self.cursor.execute(query=f'SELECT\n'
                                  f'    place_id,\n'
                                  f'    user_id,\n'
                                  f'    name,\n'
                                  f'    latitude,\n'
                                  f'    longitude,\n'
                                  f'    photo_path\n'
                                  f'FROM places\n'
                                  f'WHERE place_id = {place_id};')
        try:
            return self.cursor.fetchall().pop()
        except IndexError:
            raise ValueError('A place with this place_id does not exist')

    def delete_all_places(self, user_id):  # Implement photo deletion
        if not self.does_user_exist(user_id=user_id):
            raise ValueError('A user with this user_id does not exist')
        self.cursor.execute(query=f'DELETE\n'
                                  f'FROM places\n'
                                  f'WHERE user_id = {user_id};')

    def disconnect_from_database(self):
        self.cursor.close()
        self.connection.close()
