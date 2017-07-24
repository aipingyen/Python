from operator import itemgetter

def write(year_feature, year, text):
    with open('C:\\Users\\BIG DATA\\Desktop\\Project\\radar\\{}{}.csv'.format(text,year), 'a', encoding='utf8') as fw:
        for i in range(len(year_feature)):
            fw.write('{}\n'.format(year_feature[i]))

def sort_feature(feature_list, year, text):
    year_feature = sorted(feature_list, key=itemgetter(3))   #sorted(list[tuple] , key)
    write(year_feature, year, text)                          #以特徵值為單位,計算該年度此品牌的排名

def partition(year_data, year):     #***if unenough 10***
    comfortables = []
    fuelEcos = []
    safes = []
    spaces = []
    for idx in year_data:
        if 'comfortable' in idx:
            comfortable = []
            comfortable.append(tuple(idx.split(',')))
            for idx in comfortable:
                idx += tuple([float(idx[2])])
                comfortables.append(idx)
            if len(comfortables) == 10:
                sort_feature(comfortables, year, 'comfortable')
        else:
            None
        if 'fuelEco' in idx:
            fuelEco = []
            fuelEco.append(tuple(idx.split(',')))
            for idx in fuelEco:
                idx += tuple([float(idx[2])])
                fuelEcos.append(idx)
            if len(fuelEcos) == 10:
                sort_feature(fuelEcos, year, 'fuelEco')
        else:
            None
        if 'safe' in idx:
            safe = []
            safe.append(tuple(idx.split(',')))
            for idx in safe:
                idx += tuple([float(idx[2])])
                safes.append(idx)
            if len(safes) == 10:
                sort_feature(safes, year, 'safe')
        else:
            None
        if 'space' in idx:
            space = []
            space.append(tuple(idx.split(',')))
            for idx in space:
                idx += tuple([float(idx[2])])
                spaces.append(idx)
            if len(spaces) == 10:
                sort_feature(spaces, year, 'space')
        else:
            None

    # print("\ncomfortable : ", comfortable)
    # print("\nfuelEco : ", fuelEco)
    # print("\nsafe : ", safe)
    # print("\nspace : ", space)

if __name__ == '__main__':
    carName_list = ['Volkswagen', 'Toyota', 'LEXUS', 'Mazda', 'Mitsubishi', 'Nissan', 'BMW', 'Mercedes Benz', 'Honda', 'Ford']
    adj_Dicts = ['comfortable', 'fuelEco', 'safe', 'space']

    for year in range(2008, (2017) + 1, 1):
    # year = 2008
        year_data = []
        for carName in carName_list:
            with open('C:\\Users\\BIG DATA\\Desktop\\Project\\radar\\{}\\{}.csv'.format(carName, year), 'r', encoding='utf8') as fr:
                year_data += fr.read().split()
        print(year_data)
        partition(year_data, year)