import redis
import random
import csv

# Setup our redis connection. It's on the VM, so local is fine.
pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
r = redis.Redis(connection_pool=pool)

# Define variables
# R = 16384 // switch at 2'5 * m = 40960
PointOfTest = [5, 10, 15, 20, 25]
a = [] #Attack Vector
PointOfSwitch = 40960 # R = 16384 // switch at 2'5 * m = 40960
cCard = 40960 # Construction cardinality
nF = 5 # Number of filtering passes
sizeA = 40000 # Desired size of initial (unfiltered) attack vector

#Create the csv
with open('HighResults.csv', 'w', newline='') as csvfile:
    fieldnames = ['index', 'Target Cardinality', 'Length of A', 'Percent Cardinality', 'Number Evasion Rate', 'Evasion Rate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

# For every high card we want to test
for index in PointOfTest:
    print("Multiplier: ", index)

    a.clear()
    sizeA = int((40960 * index) / 2) # Formula to find a nice size for the initial unfiltered vector
    # Find elements for attack vector A
    while len(a) < sizeA:
        r.delete('test')
        x = 0
        # Fill the HLL
        while (r.pfcount('test') < cCard):
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

    print("Size Original A: ", len(a))
    print("-------------------")

    for filter in range(nF):
        r.delete('test')
        random.shuffle(a)
        y = random.randint(0, 10000000)
        while (r.pfcount('test') < cCard):
            r.pfadd('test', str(y))
            y = y + 1
        for x in a:
            c_ant = r.pfcount('test');
            r.pfadd('test', str(x))
            # Remove elements that increase the HLL estimate
            c_new = r.pfcount('test');
            if c_new != c_ant:
                a.remove(x);

    # Test the filtered set
    r.delete('test1')

    y = random.randint(0, 10000000)
    s = 40960 * index
    while (r.pfcount('test1') < s):
        r.pfadd('test1', str(y))
        y = y + 1

    # Insert elements in a
    for x in a:
        r.pfadd('test1', str(x))

    res = (s + len(a)) - r.pfcount('test1')
    finalLen = len(a)

    # Add the new row for the csv
    with open('HighResults.csv', 'a', newline='') as csvfile:
        fieldnames = ['index', 'Target Cardinality', 'Length of A', 'Percent Cardinality', 'Number Evasion Rate', 'Evasion Rate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'index': str(index), 'Target Cardinality': str(s), 'Length of A': str(finalLen),
                         'Percent Cardinality': str(finalLen/s),'Number Evasion Rate': str(res),
                         'Evasion Rate': str(res/len(a))})
