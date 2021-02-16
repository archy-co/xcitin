'''
Main module
'''
import time
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy import distance
import folium
import blessed

term = blessed.Terminal()
geolocator = Nominatim(user_agent='xcitin')


# Constants
FILMS_LIST_CHECKSIZE = 450


def print_main_screen():
    '''
    This function prints main screen entry information like greeting, brief explanation
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
    #print_main_screen()
    #year, user_coordinates = request_data()
    #print(year, user_coordinates)
    user_coordinates = [7.09024, -105.712891]
    user_coordinates = [-26.85338750,133.27515449] # Aursralia
    user_coordinates = [53.41291, -8.24389] # Ireland
    user_coordinates = [50.5010789, 4.4764595] # Belgie
    user_coordinates = [40.463667, -3.74922] # Spain
    user_coordinates = [52.132633, 5.291266] # Netherlands
    user_coordinates = [49.8037633, 15.4749126] # Czeck republic
    user_coordinates = [88.505859, 30.656816] # Asia
    user_coordinates = [20.593684, 78.96288] # India
    user_coordinates = [7.873054, 80.771797] # Sri Lanka
    user_coordinates = [35.10964, 73.00781] # Pakistan
    user_coordinates = [28.394857, 84.124008] # Nepal
    user_coordinates = [46.818188, 8.227512] # Switzerland
    user_coordinates = [43.93667, 12.44639] # San Marino
    user_coordinates = [45.32829, 11.6415] # Italy
    user_coordinates = [47.7, 13.06667] # Austria
    user_coordinates = [41.14961, -8.61099] # Portugal
    user_coordinates = [32.62781, -115.45446] # Mexico
    user_coordinates = [49.55404, 25.59067] # Ternopil
    user_coordinates = [37.09024, -95.712891] # USA


    
    user_location = geolocator.geocode(user_coordinates)
    user_country = unify_country(str(user_location).split(',')[-1].strip())

    print('Country:', user_country)

    year= 2004
    mappy = folium.Map(tiles='OpenStreetMap', location=user_coordinates, zoom_start=6)
    user_location = folium.FeatureGroup(name='User location')
    user_location.add_child(folium.Marker(location=user_coordinates,
                                          popup='You are here',
                                          icon=folium.Icon(icon='home')))
    mappy.add_child(user_location)


    filtered_films = filter_by_year(year, read_data('locations.list'))
    print(f'For {year}: {term.bold(len(filtered_films))} films\' locations found')

    filtered_films = filter_federal(filtered_films)
    filtered_films = filter_pure_countries(filtered_films, user_country)

    print(f'Total location after filtering: {term.bold(len(filtered_films))}')

    if len(filtered_films) > 900:
        filtered_films = random_pick(filtered_films, FILMS_LIST_CHECKSIZE)
        print(f'Picked {term.bold(len(filtered_films))} random of them')
        

    print(f'\n\n Now I\'ll be finding location\'s coordinates for {len(filtered_films)} locations.\n',
          f'It may take some time - estimated time: {round(len(filtered_films)/3, 2)} sec\n',
          'I\'ll log you what I found right away so that you didn\'t get bored :)')

    located_films = locate_films(filtered_films)
    yearfilt_loc_dist_films_complete = find_distance_asc(located_films, user_coordinates)

    film_locs = folium.FeatureGroup(name='Film Locations')

    for film in yearfilt_loc_dist_films_complete[:7]:
        film_locs.add_child(folium.Marker(location=film[3],
                                         popup=film[0],
                                         icon=folium.Icon(icon='fas', color='pink')))

    mappy.add_child(film_locs)


    famous_film_places_gr = folium.FeatureGroup(name='Famous Film Places')

    famous_film_places = [[[34.0928092, -118.3286614], 'Hollywood'],
                     [[40.703830518, -74.005666644], 'Wall Street']]

    for coord, loc in famous_film_places:
        famous_film_places_gr.add_child(folium.Marker(location=coord,
                                         popup=loc,
                                         icon=folium.Icon(icon='star', color='lightgreen')))

    mappy.add_child(famous_film_places_gr)



    mapname = 'tourning_places.html'
    print(f'Everything is ready, take a look to {term.bold(mapname)}')
    mappy.save(mapname)


def random_pick(films, anchor_size):
    '''
    Picks random list of films and returns about anchor_size films picked randomly.
    This function may not be called if films are filtered well and anchor_size is not
    reached

    >>> random_pick(['F1', 'F2', 'F3'], 3)
    ['F1', 'F2', 'F3']
    >>> random_pick(['F1', 'F2', 'F3', 'F4', 'F5'], 2)
    ['F2', 'F5']
    '''

    divider, picked_films = len(films)//anchor_size, []
    for film in films:
        if random.randint(divider+1, 3*divider)%divider==0:
            picked_films.append(film)

    return picked_films


def unify_country(country: str) -> str:
    '''
    Unifies and unites some countries. Takes a country as input and returns it's group 
    or unified name

    >>> unify_country('United States')
    'USA'
    >>> unify_country('Monaco')
    'France'
    '''
    if country in ['United States', 'United States of America']:
        return 'USA'
    elif country in ['United Kingdom', 'Éire / Ireland']:
        return 'UK'
    elif country in ['France', 'Monaco', 'België / Belgique / Belgien']:
        return 'France'
    elif country in ['Portugal', 'España', 'Andorra', 'Spain']:
        return 'Spain'
    elif country in ['Nederland', 'Netherlands', 'Deutschland', 'Česko', 'Polska', 'Poland']:
        return 'Germany'
    elif country in ['India', 'ලංකාව இலங்', 'آزاد کشمیر', 'नेपाल']:
        return 'India'
    elif country in ['Ukraine', 'Україна', 'Moldova', 'Polska', 'Беларусь', 'Poland']:
        return 'Ukraine'
    elif country in ['Italia', 'Italy', 'Schweiz/Suisse/Svizzera/Svizra', 'Civitas Vaticana', 'San Marino']:
        return 'Italy'
    elif country in ['México', 'Mexico']:
        return 'Mexico'
    elif country in ['Türkiye', 'Turkey']:
        return 'Turkey'
    else:
        return country


def filter_federal(films):
    '''
    Filters films which contains word federal in location, because they raises geopy exception
    for handling which extra 4 secs are required for each film. Therefore, for some years it could
    optimize time twice
    >>> filter_federal([['F1', 2003, 'Federal District'], ['F2', 2001, 'Simple District']])
    [['F2', 2001, 'Simple District']]
    '''

    filt_films = []
    for film in films:
        if 'Federal' not in film[2]:
            filt_films.append(film)

    return filt_films


def filter_pure_countries(filtered_films, user_country):
    '''
    Some countries are quite isolated or could be grouped with neighboring countries to create
    a group which could be considered as a whole: in this group are enough locations, and
    filtering it from overall results will optimize time dramatically

    This function creates such groups and filters for each group depending whethe user country
    belongs to group of not: if user country belongs to group, only films' locations form such
    group will be located. Otherwise, such countries will be filtered from and their locations
    won't be calculated

    Generally speaking this function calls function filter_pure_country for all pure countries
    '''

    pure_countries = ['USA', 'Canada', 'UK', 'France', 'Spain', 'Germany', 'India', 'Ukraine', 'Italy',
                      'China', 'Russia', 'Australia', 'Mexico', 'Turkey']

    for p_country in pure_countries:
        filtered_films_interim = filter_pure_country(p_country, filtered_films, user_country)
        if len(filtered_films_interim) < 1 or\
          (len(filtered_films_interim) < 6 and len(filtered_films) < 120):
            break
        else:
            filtered_films = filtered_films_interim

    return filtered_films


def filter_pure_country(pure_country, films, user_country):
    '''
    Filters one pure country: if user_country belongs to pure_country group, only films from
    this group will be returned. Otherwise, pure_country group will be filtered and removed
    from list
    >>> filter_pure_country('USA', [['F1', 2011, 'NY, USA'], ['F2', 2011, 'Toronto, Canada']], 'USA')
    [['F1', 2011, 'NY, USA']]
    '''
    filt_films = []
    for film in films:
        film_country = film[2].split(',')[-1].strip()
        if user_country in pure_country and unify_country(film_country) in pure_country:
            filt_films.append(film)
        elif user_country not in pure_country and unify_country(film_country) not in pure_country:
            filt_films.append(film)


    return filt_films
    


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
    with open(filepath, 'r', errors='ignore') as datafile:
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
            except IndexError:
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


def locate_films(films, verbose=True):
    '''
    This function determines coordinates of place using geopy geolocator.
    It takes films list of lists as argument, where in each child sublist is supposed to be
    3 elements - filmname, year, location - and returns the same list of lists but each child
    sublist is extended with tuple of coordinatas (latitude, longitude)

    >>> locate_films([['Backstroke', 2007, 'Salt Lake City, Utah, USA']], False)
    [['Backstroke', 2007, 'Salt Lake City, Utah, USA', (40.7596198, -111.8867975)]]
    '''
    start = time.time()
    films_loc = []
    for film in films:
        try:
            location = already_located(film[2], films_loc)
            film_loc = film + [location]
            if location == None:
                loc_gcode = geolocator.geocode(film[2])
                location = tuple([loc_gcode.latitude, loc_gcode.longitude])

            film_loc = film + [location]
            films_loc.append(film_loc)
            if verbose:
                print(f'{term.bold(film[0])}:\t{location} - {film[2].split(",")[-1].strip()} ')
        except GeocoderUnavailable:
            #print('geoerror:', film)   # specific geopy exception
            continue
        except AttributeError as err:
            #print('attrerror', film)   # location not found
            continue

    return films_loc


def already_located(film_loc, films_loc):
    for film in films_loc:
        if film[2] == film_loc:
            return film[-1]

    return None



if __name__ == '__main__':
    main()
