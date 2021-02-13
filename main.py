'''
Main module
'''
import time
import geopy
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
          '\nSounds freaky? Don\'t worry, I won\'t kidnap you, I will just build',
          'a map with places around you, where tourning of films took place in specified year, I swear')
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
    print_main_screen()
    year, coordinates = request_data()
    print(year, coordinates)
    mappy = folium.Map(tiles='OpenStreetMap', location=coordinates, zoom_start=6)
    mappy.save('tourning_places.html')




if __name__ == '__main__':
    main()
