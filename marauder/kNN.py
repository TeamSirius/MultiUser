# Brett (Berty) Fischler and Hunter (Kenneth) Wapman
# October 2014
# kNN Implementation for Senior Design Project

from collections import Counter
import sets
import math
import sys
import os
from math import isinf
from datetime import datetime


#-------------
# CONSTANTS
#-------------

COEFF_JACCARD = 1.6
COEFF_EUCLIDEAN = 2.6
COEFF_DENSITY = .08
PENALTY = 0.16
MODE = "COMBINED"


MAXINT = sys.maxsize
MININT = (MAXINT * -1) - 1

# Minimum normalized RSSI value detected; used as "not detected" value
MIN_DETECTED = MAXINT

# TODO: Either incorporate this or get rid of it
MAC_COUNTS = {}

#---------------------
# CLASS DEFINITIONS
#---------------------


class AccessPoint(object):

    """ AccessPoint Object """

    def __init__(self, ap, from_django=False):
        """Takes in tuple( MAC,strength,standard_deviation,datetime) """
        if not from_django:
            self.mac = ap[0]
            self.strength_dbm = float(ap[1])
            #self.strength = 10 ** (float(ap[1]) / 10)
            self.strength = self.strength_dbm
            self.std = 10 ** (float(ap[2]) / 10)
            self.datetime = ap[3]

        else:
            self.mac = ap['mac_address']
            self.strength_dbm = ap['signal_strength']
            self.strength = 10 ** (self.strength_dbm / 10)
            self.std = 10 ** (ap['standard_deviation'] / 10)
            self.datetime = ap['recorded']


class Location(object):

    """ Location Object """

    def __init__(self, loc):
        self.x = loc[0]
        self.y = loc[1]
        self.direction = loc[2]
        self.floor_id = loc[3]
        self.init_aps(loc[4])

    # Stores Access Points in a {mac_id : AccessPoint} dictionary
    def init_aps(self, aps):
        """ Stores the AccessPoint list in a {mac_id : AccessPoint } dict """
        self.aps = {}
        for ap in aps:
            self.aps[ap[0]] = AccessPoint(ap)


#----------------------
# DISTANCE FUNCTIONS
#----------------------

def getKeySet(aps1, aps2):
    """ Returns a set of shared keys between the two given AP dictionaries """
    keys = sets.Set()
    for mac_id in aps1.keys():
        keys.add(mac_id)
    for mac_id in aps2.keys():
        keys.add(mac_id)
    return keys


def kNNDistance(aps1, aps2, density=0):
    """ Returns distance between the given AccessPoint dicts.
    Takes Jaccard coefficient, Euclidean distance, and density into account.
    """
    distances = []
    euc_dist = euclidean(aps1, aps2)
    jaccard_dist = jaccard(aps1, aps2)
    if jaccard_dist == 0:
        return float("INF")

    rVal = (COEFF_JACCARD / jaccard_dist) + (COEFF_EUCLIDEAN * euc_dist)
    if MODE == "COMBINED":
        rVal += (COEFF_DENSITY * density)
    return rVal


def euclideanOld(aps1, aps2):
    """ Returns the Euclidean distance between the given AccessPoint dicts """
    global MIN_DETECTED
    keys = getKeySet(aps1, aps2)
    rVal = 0
    for key in keys:
        strength1 = MIN_DETECTED
        if key in aps1:
            strength1 = aps1[key].strength
        strength2 = MIN_DETECTED
        if key in aps2:
            strength2 = aps2[key].strength
        rVal = rVal + ((strength1 - strength2) ** 2)
    return math.sqrt(rVal)


def euclidean(aps1, aps2):
    """ Returns the Euclidean distance between the given AccessPoint dicts """
    global MIN_DETECTED
    global PENALTY
    keys = getKeySet(aps1, aps2)
    both = []
    aps1_only = []
    aps2_only = []
    for key in keys:
        if key in aps1 and key in aps2:
            both.append(key)
        elif key in aps1:
            aps1_only.append(key)
        else:
            aps2_only.append(key)
    rVal = 0
    for key in both:
        rVal += (aps1[key].strength - aps2[key].strength) ** 2
    for key in aps1_only:
        rVal += ((aps1[key].strength - MIN_DETECTED) ** 2) * PENALTY
    for key in aps2_only:
        rVal += ((MIN_DETECTED - aps2[key].strength) ** 2) * PENALTY
    return math.sqrt(rVal)


def jaccard(aps1, aps2):
    """ Returns the Jaccard coeff between the given AccessPoint dicts """
    count = 0
    for ap in aps2.values():
        if ap.mac in aps1.keys():
            count += 1
    intersection = count
    union = len(aps1.keys()) + len(aps2.keys()) - count
    return float(intersection) / union


def realDistance(d1, d2):
    """ Returns the real distance between the two given Location objects """
    if d1 is None or d2 is None:
        return 0
    return math.sqrt(pow(d1.x - d2.x, 2) + pow(d1.y - d2.y, 2))


#-----------------
# kNN FUNCTIONS
#-----------------

def weighted_avg(tuples, inverse):
    """ Given a list of tuples (t[0] is the value and t[1] is the distance),
    returns a weighted average of the values. If inverse == True, we use the
    inverse of the given weights.
    """
    s = 0
    for t in tuples:
        if t[1] == 0:
            return t[0]
    if inverse:
        weight_sum = sum([1 / t[1] for t in tuples])
    else:
        weight_sum = sum([t[1] for t in tuples])
    for t in tuples:
        if isinf(t[1]) or weight_sum == 0:
            return t[0]
        if inverse:
            s += t[0] * (1 / t[1]) / weight_sum
        else:
            s += t[0] * t[1] / weight_sum
    return s


def applykNN(data, aps, k, element=None):
    """ Uses kNN technique to locate the given AccessPoint dict """
    k = min(k, len(data))
    floor = getFloor(data, aps)
    for d in data:
        if d.floor_id == floor:
            if MODE == "JACCARD":
                d.distance = 1 / (jaccard(d.aps, aps) + .01)
            elif MODE == "EUCLIDEAN":
                d.distance = euclidean(d.aps, aps)
            else:
                d.distance = kNNDistance(d.aps, aps, density=d.density)
        else:
            d.distance = float("INF")
    data = sorted(data, key=lambda x: x.distance)
    x = weighted_avg([(loc.x, loc.distance) for loc in data[:k]], True)
    y = weighted_avg([(loc.y, loc.distance) for loc in data[:k]], True)
    return (x, y, floor, data[:k])


def getFloor(data, aps, k=5):
    """ Uses kNN technique to find the floor of the given AccessPoint dict """
    k = min(k, len(data))
    data = sorted(data, key=lambda d: jaccard(d.aps, aps), reverse=True)
    d = Counter([loc.floor_id for loc in data[:k]])
    floor = d.most_common(1)[0][0]
    return floor


#----------------------
# GET DATA FUNCTIONS
#----------------------

def getData(excluded=[]):
    sql_data = getSqlData()
    all_data = getLocations(sql_data)
    data = []
    testdata = []
    for d in all_data:
        if d.floor_id == 4 or d.floor_id == 5:
            data.append(d)
        elif d.floor_id == 6:
            testdata.append(d)
    addDensities(data)
    (mean, st_dev) = normalize(data)
    testdata = [e for (i, e) in enumerate(testdata) if i not in excluded]
    return (data, testdata, mean, st_dev)


def getLocations(data):
    """ Returns an array of Location objects corresponding to the given data"""
    locations = []
    for d in data:
        cur_macs = d["macs"]
        cur_rss = d["rss"]
        cur_aps = []
        for i in range(len(cur_macs)):
            cur_aps.append((cur_macs[i], cur_rss[i], 0, 0))
        locations.append(
            (d["x"],
             d["y"],
                d["direction"],
                d["floor_id"],
                cur_aps))
    return [Location(i) for i in locations]


def getSQLLocations(db_cursor):
    locations = []
    db_cursor.execute(
        """SELECT floor_id,marauder_accesspoint.location_id, x_coordinate, y_coordinate, direction,
         array_to_string(array_agg(mac_address),',') as MAC_list,
         array_to_string(array_agg(signal_strength),',') as strength_list
         from marauder_accesspoint
         join marauder_location
            on marauder_location.id=marauder_accesspoint.location_id
        where floor_id = 4 or floor_id =5
         group by floor_id,marauder_accesspoint.location_id,x_coordinate,y_coordinate,direction""")
    access_points = cur.fetchall()
    for ap in access_points:
        cur_aps = []
        temp_macs = ap[5].split(",")
        temp_rss = ap[6].split(",")
        num_macs = len(temp_macs)
        for i in range(num_macs):
            cur_aps.append((temp_macs[i], temp_rss[i], 0, 0))
        locations.append(Location((ap[2], ap[3], ap[4], ap[0], cur_aps)))

    addDensities(locations)
    return locations


def getTestPoints(db_cursor):
    pts = {}
    db_cursor.execute(
        """SELECT floor_id,marauder_accesspoint.location_id, x_coordinate, y_coordinate, direction,
         array_to_string(array_agg(mac_address),',') as MAC_list,
         array_to_string(array_agg(signal_strength),',') as strength_list
         from marauder_accesspoint
         join marauder_location
            on marauder_location.id=marauder_accesspoint.location_id
        where floor_id = 9
         group by floor_id,marauder_accesspoint.location_id,x_coordinate,y_coordinate,direction
         limit 1""")
    access_points = cur.fetchall()
    for ap in access_points:
        temp_macs = ap[5].split(",")
        temp_rss = ap[6].split(",")
        num_macs = len(temp_macs)
        for i in range(num_macs):
            pts[temp_macs[i]] = temp_rss[i]
    return pts


def getSqlData(db_cursor=None):
    if db_cursor is None:
        from scripts.db.db import Database
        password = os.environ.get('SIRIUS_PASSWORD')
        if password is None:
            raise Exception('No database password available')

        db = Database(password)

        cur = db.get_cur()
    else:
        cur = db_cursor
    cur.execute(
        """SELECT floor_id,marauder_accesspoint.location_id, x_coordinate, y_coordinate, direction,
         array_to_string(array_agg(mac_address),',') as MAC_list,
         array_to_string(array_agg(signal_strength),',') as strength_list
         from marauder_accesspoint
         join marauder_location
            on marauder_location.id=marauder_accesspoint.location_id
         group by floor_id,marauder_accesspoint.location_id,x_coordinate,y_coordinate,direction""")
    access_points = cur.fetchall()
    res = []
    for f in access_points:
        msg = {
            'floor_id': f[0],
            'location_id': f[1],
            'x': f[2],
            'y': f[3],
            'direction': f[4],
            'macs': f[5].split(','),
            'rss': map(float, f[6].split(','))
        }
        res.append(msg)
    return res


#---------------------------
# COMBINEDIZATION FUNCTIONS
#---------------------------

def get_sd(l):
    """ Returns the standard deviation of the given list """
    mean = get_mean(l)
    rVal = 0
    for elem in l:
        rVal += (elem - mean) ** 2
    return (rVal / (len(l) - 1)) ** .5


def get_mean(l):
    """ Returns the mean of the given list """
    return sum(l) / len(l)


def normalize(data):
    """ Normalizes the given data and returns the mean and standard dev """
    global MIN_DETECTED
    global MAC_COUNTS  # TODO: Get rid of this if we don't incorporate it
    strengths = []
    for loc in data:
        for ap in loc.aps.values():
            strengths.append(ap.strength)
            # JUST ADDED
            if ap.mac not in MAC_COUNTS.keys():
                MAC_COUNTS[ap.mac] = 0
            MAC_COUNTS[ap.mac] += 1
    mean = get_mean(strengths)
    st_dev = get_sd(strengths)
    for loc in data:
        for ap in loc.aps.values():
            ap.strength = (ap.strength - mean) / st_dev
            if ap.strength < MIN_DETECTED:
                MIN_DETECTED = ap.strength
    return (mean, st_dev)


def normalizeAPs(aps, mean, st_dev):
    """ Normalizes the given AccessPoint dict """
    for ap in aps.values():
        ap.strength = (ap.strength - mean) / st_dev


#----------------------
# ANALYSIS FUNCTIONS
#----------------------

def error(element, x, y, floor):
    """ Returns the error between the given element and our x and y vals """
    if element.floor_id == 6 and floor != 5:
        return -1
    elif element.floor_id < 6 and element.floor_id != floor:
        return -1
    else:
        dist = math.sqrt(pow(element.x - x, 2) + pow(element.y - y, 2))
    return dist


def addDensities(data):
    """ Adds the density of points around each Location as a Location member """
    for i in range(len(data)):
        count = 1
        loc1 = data[i]
        for j in range(len(data)):
            loc2 = data[j]
            if i == j or loc1.floor_id != loc2.floor_id:
                continue
            if loc1.floor_id == 1:
                den_threshold = 9.555 * 20
            else:
                den_threshold = 14.764 * 20
            if realDistance(loc1, loc2) < den_threshold:
                count += 1
        loc1.density = count


def testAccuracy(error_output, guess_output, neighbor_output, k=4):
    """ Pulls data from the database, runs kNN on each test point, and prints
    results to various files
    """
    (data, testdata, mean, st_dev) = getData()
    wrong_floor_count = 0
    errors = []
    distances = [0 for i in range(10)]
    for i in range(len(testdata)):
        element = testdata[i]
        dataelem = data[i]
        data.remove(dataelem)
        aps = element.aps
        normalizeAPs(aps, mean, st_dev)
        (x, y, floor, neighbors) = applykNN(data, aps, k, element=element)
        data.insert(i, dataelem)
        cur_error = error(element, x, y, floor)
        if cur_error == -1:
            wrong_floor_count += 1
        else:
            if MODE == "COMBINED":
                guess_output.write(str(element.x) + " " + str(element.y) + " " +
                                   str(x) + " " + str(y) + "\n")
                neighbor_output.write(
                    str(element.x) + " " + str(element.y) + " " + str(x) + " " +
                    str(y) + "\n")
                for n in neighbors:
                    neighbor_output.write(str(n.x) + " " + str(n.y) + "\n")
            # For Halligan_2.png, 14.764px ~= 1 meter
            # For Halligan_1.png 9.555px ~= 1 meter
            if floor == 1:
                cur_error /= 14.764
                error_output.write(str(cur_error) + "\n")
                if MODE != "COMBINED" and i == len(testdata) - 1:
                    error_output.write("\n")
                errors.append(cur_error)
                distances[min(int(cur_error), 9)] += 1
            else:
                cur_error /= 9.555
                error_output.write(str(cur_error) + "\n")
                if MODE != "COMBINED" and i == len(testdata) - 1:
                    error_output.write("\n")
                errors.append(cur_error)
                distances[min(int(cur_error), 9)] += 1
    print "MODE:", MODE
    print "FOR " + str(len(testdata)) + " POINTS:"
    print "Incorrect Floor Count:", wrong_floor_count
    print "Min error:", min(errors)
    print "Max error:", max(errors)
    print "Avg error: " + str(float(sum(errors)) / (len(testdata) - wrong_floor_count)) + "m"
    print "Distances:", distances
    print ""
    return float(sum(errors)) / len(testdata)

    '''This code is used for LOOCV. Remember to comment out the call to normalizeAPs()
    ### BEST VALUE: 3.95m ###
    import copy
    testdata = copy.deepcopy(data)'''

    ''' This code is used for the wrapper method.
    best_density = 0
    best_error = 100
    for MODE in ["COMBINED"]:
        for COEFF_DENSITY in [float(i) / 350 for i in range(15, 30)]:
            print "DENSITY:", COEFF_DENSITY
            cur_error = testAccuracy(error_output, guess_output, neighbor_output, k)
            if cur_error < best_error:
                best_error = cur_error
                best_density = COEFF_DENSITY
        print best_error, best_density
        '''


#----------------------
# django code
#----------------------

def stringList(L):
    return "(" + ",".join(L) + ")"

    build_list = "("
    length = len(L)
    last = length - 1
    for i in range(length):
        build_list += "\'"
        build_list += L[i]
        build_list += "\'"
        if i != last:
            build_list += ","
    build_list += ")"
    return build_list


def kNN(db_cursor, aps_dic):
    """Takes in a database cursor and a dictionary with MAC address keys and RSS values.
        Will return a tuple of length four indicating (SUCCESS,X,Y,FLOOR_ID). In the case
        of no mac addresses being present in the database the return will be (False,None,None,None)"""
    ERROR_RETURN = (False, None, None, None)  # Return in case of error
    kVal = 3  # K parameter for kNN
    # Returns a non-zero number if accesspoints are present in the database
    # -- Returns 0 when there is no overlap
    db_cursor.execute(
        """select count(*) from marauder_accesspoint where mac_address = ANY(%s)""",
        [aps_dic.keys()])
    num = db_cursor.fetchone()
    if not num or int(num[0]) == 0:
        return ERROR_RETURN
    # Gets all known FP locations as Location Objects form the database
    #   the returned Locations already have the desity calculated
    data = getSQLLocations(db_cursor)
    # Normalizes the known data and returns the mean and std such as to normalize
    #   the input data
    mean, std = normalize(data)
    # Builds Access point list from dictionary
    aps = {}
    for mac_address, rss in aps_dic.iteritems():
        # Takes in tuple( MAC,strength,standard_deviation,datetime).
        # NOTE: standard_deviation and datetime are not used"""
        aps[mac_address] = AccessPoint((mac_address, rss, 0, 0))

    # Normalizes the input data
    normalizeAPs(aps, mean, std)
    # Applies the kNN algorithm and returns x,y,floor
    (x, y, floor_id, _) = applykNN(data, aps, kVal)
    return (True, x, y, floor_id)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.stderr.write("Usage: python kNN.py -k K error_output " +
                         "guess_output neighbor_output\n")
        sys.exit(1)
    args = sys.argv[1:]
    k = 4
    if args[0] == "-k":
        k = int(args[1])
        args = args[2:]
    error_output = open(args[0], "w+")
    guess_output = open(args[1], "w+")
    neighbor_output = open(args[2], "w+")
    for MODE in ["EUCLIDEAN", "JACCARD", "COMBINED"]:
        testAccuracy(error_output, guess_output, neighbor_output, k)
