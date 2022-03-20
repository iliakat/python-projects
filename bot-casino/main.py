from threading import *
from bot import *
from promo import *

t1 = Thread(target = main)
t2 = Thread(target = promo)

t1.start()
t2.start()