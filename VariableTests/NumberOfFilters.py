import redis
import random
import csv
from datetime import datetime

# Setup our redis connection. It's on the VM, so local is fine.
pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
r = redis.Redis(connection_pool=pool)

# Define variables
a = [] #Attack Vector
PointOfSwitch = 40960 # R = 16384 // switch at 2'5 * m = 40960
cCard = 40960 # Construction cardinality
iters = 9 # Number of filtering passes
sizeA = 30000 # Desired size of initial (unfiltered) attack vector

# Auxiliary variables
a_aux = []
results = []

# Create the csv
with open('NoFSuccess.csv', 'w', newline='') as csvfile:
    fieldnames = ['nFilter', 'success1', 'success2', 'success3', 'success4', 'success5', 'average', 'percent average']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

with open('NoFReduction.csv', 'w', newline='') as csvfile:
    fieldnames = ['nFilter', 'reduction', 'time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

a.clear()
# Find elements for attack vector A
while len(a) < sizeA:
    r.delete('test')
    x = 0
    # Fill the HLL to cCard point
    while (r.pfcount('test') < cCard):
        r.pfadd('test', str(x))
        x = x + 1
    # Insert 20k elements to find non-incrementals before reseting to cCard or ending if len(a) is enough
    aux = x + random.randint(0, 10000000) # x + random in order to assure no duplicate values
    for i in range(1, 20000):
        c_ant = r.pfcount('test')
        r.pfadd('test', str(aux))
        c_new = r.pfcount('test');
        if c_new == c_ant:
            a.append(aux)
        aux = aux + 1

a_aux = a

# Test depending on the number of filter passes
# Start with only one filter pass, test, then repeat adding one more filter pass.
for iterator in range(1, iters):
    a_aux = a
    results.clear()
    startTime = datetime.now().replace(microsecond=0)
    for z in range(0, iterator):
        r.delete('test')
        random.shuffle(a_aux)
        y = random.randint(0, 10000000)
        while (r.pfcount('test') < 40960):
            r.pfadd('test', str(y))
            y = y + 1
        for x in a_aux:
            c_ant = r.pfcount('test');
            r.pfadd('test', str(x))
            # Remove elements that increase the HLL estimate
            c_new = r.pfcount('test');
            if c_new != c_ant:
                a_aux.remove(x);

    endTime = datetime.now().replace(microsecond=0)
    exTime = (endTime - startTime).total_seconds()
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
        for x in a_aux:
            r.pfadd('test1', str(x))

        res = (s + len(a_aux)) - r.pfcount('test1')
        results.append(res)
        finalLen = len(a_aux)

        print("Tests made")
        print("-----------------------------------------------------")

    # Add the new row for the csv
    average = sum(results) / len(results)
    with open('NoFSuccess.csv', 'a', newline='') as csvfile:
        fieldnames = ['nFilter', 'success1', 'success2', 'success3', 'success4', 'success5', 'average',
                      'percent average']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'nFilter': str(iterator), 'success1': str(results[0]), 'success2': str(results[1]),
                         'success3': str(results[2]),
                         'success4': str(results[3]), 'success5': str(results[4]), 'average': str(average),
                         'percent average': str((average / len(a_aux)) * 100)})

    print("Reduced: " + str(len(a_aux)) + "/// Not Reduced: " + str(sizeA))
    with open('NoFReduction.csv', 'a', newline='') as csvfile:
        fieldnames = ['nFilter', 'reduction', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'nFilter': str(iterator), 'reduction': str((len(a_aux) / sizeA) * 100), 'time': exTime})
    print("CSV")
    print("-----------------------------------------------------")
