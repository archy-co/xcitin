'''
This is supporting module which containg minimaze_data function to shrink larger files
'''

def minimize_data(datafile, nth=1000):
    '''
    This function is supporting function used for developpment purposes to shrink the file size
    by selecting one of nth element. By default nth is equal to 1000, so the shrinked file will be
    1000 times smaller

    datafile - name of file to read. New data will be saved in file with name datafile.min
    '''
    with open(datafile+'.min', 'w') as min_f:
        min_f.write('==============\n')

    begin = False
    with open(datafile, 'r', errors='ignore') as rfile:
        counter = 0
        for line in rfile:
            counter+=1
            if counter%nth == 0:
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

if __name__ == '__main__':
    minimize_data('locations.list', 100)
