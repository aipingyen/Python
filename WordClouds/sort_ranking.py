from operator import itemgetter
from pymongo import MongoClient

def insert(year_feature, year, text):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01_featureRank
    # print(year_feature)
    featureRank = {'Brand': year_feature[0], 'year': year, 'feature':year_feature[1], 'level': year_feature[5]}
    collection.insert_one(featureRank)               #共計400個JsonObj to record ranking of feature

    # print(year_feature)
    # print(year)
    # print(text)

def sort_feature(feature_list, year, text):
    year_feature = sorted(feature_list, key=itemgetter(3))
    # print(year_feature)
    maxFea = float(year_feature[9][3])
    minFea = float(year_feature[0][3])
    ranges = maxFea - minFea
    rank = round((ranges/4),2)
    # print(len(year_feature))
    for i in range(10):
        value = float(year_feature[i][3])
        if (value > (maxFea - rank * 1)):
            year_feature[i] += tuple([int(5)])
        elif ((maxFea - rank * 1) >= value > ( maxFea - rank * 2)):
            year_feature[i] += tuple([int(4)])
        elif ((maxFea - rank * 2) >= value > ( maxFea - rank * 3)):
            year_feature[i] += tuple([int(3)])
        elif ((maxFea - rank * 3) >= value > ( maxFea - rank * 4)):
            year_feature[i] += tuple([int(2)])
        elif ((maxFea - rank * 4) >= value):
            year_feature[i] += tuple([int(1)])
        else:
            print("loss")
        insert(year_feature[i], year, text)

def partition(year_data, year):
    comfortables = []
    fuelEcos = []
    safes = []
    spaces = []
    for idx in year_data:
        if 'comfortable' in idx:
            comfortable = []
            comfortable.append(tuple(idx.split(',')))
            for idx in comfortable:
                idx += tuple([float(idx[3])])
                comfortables.append(idx)
            if len(comfortables) == 10:
                sort_feature(comfortables, year, 'comfortable')
        else:
            None
        if 'fuelEco' in idx:
            fuelEco = []
            fuelEco.append(tuple(idx.split(',')))
            for idx in fuelEco:
                idx += tuple([float(idx[3])])
                fuelEcos.append(idx)
            if len(fuelEcos) == 10:
                sort_feature(fuelEcos, year, 'fuelEco')
        else:
            None
        if 'safe' in idx:
            safe = []
            safe.append(tuple(idx.split(',')))
            for idx in safe:
                idx += tuple([float(idx[3])])
                safes.append(idx)
            if len(safes) == 10:
                sort_feature(safes, year, 'safe')
        else:
            None
        if 'space' in idx:
            space = []
            space.append(tuple(idx.split(',')))
            for idx in space:
                idx += tuple([float(idx[3])])
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
        print(year)
        print(len(year_data))
        print(year_data)
        partition(year_data, year)

