'''
Main module
'''
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy import distance
import folium
import blessed

term = blessed.Terminal()

def print_main_screen():
    '''
    This function prints main screen entry information
    '''

    print(term.center(term.bold('XCITIN')))
    time.sleep(0.5)
    print('Hello, I\'m xcitin! Let\'s do something exciting!')
    time.sleep(0.8)
    print('Hmmm, what about your entering a year and your coordinates. \nSounds freaky?',
          'Don\'t worry, I won\'t kidnap you, I will just build a map with up to 7 closest',
          'places around you, where tourning of films took place in specified year, I swear.')
    time.sleep(0.5)


def request_data():
    '''
    This function asks user to enter year for films and coordinates (latitude and longitude)
    and returns them in format (year, (lat, lon))
    '''

    print(f'So which {term.bold("year")} you choose?')
    while True:
        try:
            year = int(input('> '))
            if 1800 < year <= 2021:
                break
            print('Just a year in range films existed')
        except ValueError:
            print('Format for year: 4-digit decimal number, e.g. 2003')

    print('Great, now let\'s choose a place. Enter coordinates in format: lat, lon')

    while True:
        try:
            lat, lon = [round(float(coord), 6) for coord in input('> ').split(',')]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                break
            print('Range for latitide: from -90 to 90; range for lon: from -180 to 180')
        except ValueError:
            print('Format for coordinates: 2 float comma separated values, e.g. 45.84712, 81.47264')

    print('Perfect!')

    return (year, (lat, lon))


def main():
    '''
    Main function. Organazis the flow of the program by calling the other functions
    General flow:
        print main screen
        ask user to enter data
        create map with user location
        read data file, filter it and find closest locations
        mark this location on map on seperate lawyer
    '''
    print_main_screen()
    year, coordinates = request_data()
    #print(year, coordinates)
    #coordinates = [46.314755, 25.082925]
    mappy = folium.Map(tiles='OpenStreetMap', location=coordinates, zoom_start=6)
    user_location = folium.FeatureGroup(name='User location')
    user_location.add_child(folium.Marker(location=coordinates,
                                          popup='You are here',
                                          icon=folium.Icon()))
    mappy.add_child(user_location)

    #year = 2007

    yearfilt_films = filter_by_year(year, read_data('locations.list.min'))
    print('Now I\'ll be finding location\'s coordinates. It may take some time. I\'ll log you',
          'what I found right away so that you didn\'t get bored :)')
    yearfilt_loc_films = locate_films(yearfilt_films)
    yearfilt_loc_dist_films_complete = find_distance_asc(yearfilt_loc_films, coordinates)

    film_locs = folium.FeatureGroup(name='Film Locations')

    for film in yearfilt_loc_dist_films_complete[:7]:
        film_locs.add_child(folium.Marker(location=film[3],
                                         popup=film[0],
                                         icon=folium.Icon(color='pink')))

    mappy.add_child(film_locs)

    mapname = 'tourning_places.html'

    print(f'Everything is ready, take a look to {term.bold(mapname)}')

    mappy.save(mapname)


def find_distance_asc(films_data, coordinates):
    '''
    This function finds distance between each of films_data film and coordinates, appends this
    distance to the each film of films_data, sorts them in ascending order and returns list of lists

    films_data is list of lists that contains coordinates in format (lat, lon) as last element
    of each sublist

    coordinates is tuple of list in format (lat, lon)
    >>> find_distance_asc([['Awesome', 2007, 'USA', (31.53131, 34.86676)]], [46.31475, 25.08292])
    [['Awesome', 2007, 'USA', (31.53131, 34.86676), 1844.1301598361874]]
    '''
    for film in films_data:
        dist = distance.distance(film[-1], coordinates).km
        film.append(dist)
    films_data.sort(key = lambda x: x[-1])
    return films_data


def read_data(filepath: str) -> list:
    '''
    This function read data from filepath. This file supposed to have starting line '=============='
    after with list of films begins. Any lines before this start point marker will be ignored.
    Generally, the format for lines is: name_of_film (year) {serie} \t Location \t (optional)

    Sometimes instead of \t could be multiple \t. This function works fine with that.
    Any exceptional formats are ignored as well as films with non-int year (e.g. unknown year ????)


    Function returns list of lists where each child sublist contain 3 elements:
    filmname, year, location
    '''
    begin, films_data = False, []
    with open(filepath, 'r') as datafile:
        for line in datafile:
            try:
                line = line.strip()
                if line == '==============':
                    begin = True
                    continue
                if begin:
                    film_loc = line.split('\t')
                    while '' in film_loc:
                        film_loc.remove('')

                    part_1 = '%s' % film_loc[0]
                    part1_split = part_1.split('(')
                    name = part1_split[0].strip().strip('"')
                    year = int(part1_split[1][:4])
                    films_data.append([name, year, film_loc[1]])
            except ValueError:
                continue

    return films_data


def filter_by_year(year: int, films_data) -> list:
    '''
    This functions filters films for specified year from list of lists films_data.
    Returns the same list of lists but only with films matching specified year

    >>> filter_by_year(2007, [['Vsenpumpen', 2007, 'Jravallen, Skne ln, Sweden'],\
                       ['Wait Up Harriet', 2006, 'New Zealand']])
    [['Vsenpumpen', 2007, 'Jravallen, Skne ln, Sweden']]
    '''
    filtered_films_data = []
    for film_data in films_data:
        if int(film_data[1]) == year:
            filtered_films_data.append(film_data)

    return filtered_films_data


def locate_films(films):
    '''
    This function determines coordinates of place using geopy geolocator.
    It takes films list of lists as argument, where in each child sublist is supposed to be
    3 elements - filmname, year, location - and returns the same list of lists but each child
    sublist is extended with tuple of coordinatas (latitude, longitude)

    >>> locate_films([['Backstroke', 2007, 'Salt Lake City, Utah, USA']])
    [['Backstroke', 2007, 'Salt Lake City, Utah, USA', (40.7596198, -111.8867975)]]
    '''
    start = time.time()
    geolocator = Nominatim(user_agent='xcitin')
    films_loc = []
    for film in films:
        try:
            location = geolocator.geocode(film[2])
            film_loc = film + [tuple([location.latitude, location.longitude])]
            films_loc.append(film_loc)
            print(f'{term.bold(film[0])}:\t({round(location.latitude, 4)}, {round(location.longitude, 4)})')
        except GeocoderUnavailable:
            continue
        except AttributeError as err:
            continue

    print(f'Well, it took {round(time.time()-start, 2)} sec')
    return films_loc



if __name__ == '__main__':
    main()
