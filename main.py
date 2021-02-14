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
    print('Hmmm, what about your entering a year and your coordinates',
          '\nSounds freaky? Don\'t worry, I won\'t kidnap you, I will just build a map with',
          'places around you, where tourning of films took place in specified year, I swear')
    time.sleep(0.5)

def request_data():
    '''
    This function asks user to enter year for films and coordinates (latitude and longitude)
    and returns them in format (year, (lat, lon))
    '''

    print(f'So which {term.bold("year")} you chose?')
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
    '''
    #print_main_screen()
    #year, coordinates = request_data()
    #print(year, coordinates)
    coordinates = [46.314755, 25.082925]
    mappy = folium.Map(tiles='OpenStreetMap', location=coordinates, zoom_start=6)
    user_location = folium.FeatureGroup(name='User location')
    user_location.add_child(folium.Marker(location=coordinates,
                                          popup='You are here',
                                          icon=folium.Icon()))
    mappy.add_child(user_location)

    year = 2007

    yearfilt_films = filter_by_year(year, read_data('locations.list.min'))
    yearfilt_loc_films = locate_films(yearfilt_films)
    yearfilt_loc_dist_films_complete = find_distance_asc(yearfilt_loc_films, coordinates)

    film_locs = folium.FeatureGroup(name='Film Locations')

    for film in yearfilt_loc_dist_films_complete[:5]:
        film_locs.add_child(folium.Marker(location=film[3],
                                         popup=film[0],
                                         icon=folium.Icon(color='pink')))

    mappy.add_child(film_locs)


    mappy.save('tourning_places.html')


def find_distance_asc(films_data, coordinates):
    for film in films_data:
        dist = distance.distance(film[-1], coordinates).km
        film.append(dist)
    films_data.sort(key = lambda x: x[-1])
    return films_data




def minimize_data(datafile):
    with open(datafile+'.min', 'w') as min_f:
        min_f.write('==============\n')

    begin = False
    with open(datafile, 'r', errors='ignore') as rfile:
        counter = 0
        for line in rfile:
            counter+=1
            if counter%1000 == 0:
                with open(datafile+'.min', 'a') as min_f:
                    min_f.write(line)
            line = line.strip()
            if line == '==============':
                begin = True
                continue
            if begin:
                film_loc = line.split('\t')
                while '' in film_loc:
                    film_loc.remove('')



def read_data(filepath: str) -> list:
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
                print('Error line:', line)
                continue

    return films_data


def filter_by_year(year: int, films_data) -> list:
    filtered_films_data = []
    for film_data in films_data:
        if int(film_data[1]) == year:
            filtered_films_data.append(film_data)

    return filtered_films_data


def locate_films(films):
    start = time.time()
    geolocator = Nominatim(user_agent='xcitin')
    films_loc = []
    for film in films[:8]:
        try:
            location = geolocator.geocode(film[2])
            film_loc = film + [tuple([location.latitude, location.longitude])]
            films_loc.append(film_loc)

        except GeocoderUnavailable as err:
            continue
        except AttributeError as err:
            continue

    print(time.time()-start)
    return films_loc



if __name__ == '__main__':
    main()
    #minimize_data('locations.list')
    #films_data = read_data('locations.list.min')
    #print(filter_by_year(2003, films_data))
    #minimize_data('~/covid.csv')
