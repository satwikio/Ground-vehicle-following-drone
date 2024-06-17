import numpy as np
a=-8
for i in range (500):
    a+=0.5
    angle = np.arctan(a)
    print(a,angle)