#-----------------------------------------------------------------------
# stopwatch.py
#-----------------------------------------------------------------------

import sys
import time
import stdio

#-----------------------------------------------------------------------

class Stopwatch:

    # Construct self and start it running.
    def __init__(self):
        self._creationTime = time.time()  # Creation time

    # Return the elapsed time since creation of self, in seconds.
    def elapsedTime(self):
        return time.time() - self._creationTime

#-----------------------------------------------------------------------

# For testing.
# Accept integer n as a command-line argument. Compare the performance
# of squaring integers using i**2 vs. i*i for the task of computing the
# sum of the squares of the integers from 1 to n.

def main():
    n = int(sys.argv[1])
    
    total1 = 0.0
    watch1 = Stopwatch()
    for i in range(1, n+1):
        total1 += i**2
    time1 = watch1.elapsedTime()
    
    total2 = 0.0
    watch2 = Stopwatch()
    for i in range(1, n+1):
        total2 += i*i
    time2 = watch2.elapsedTime()
    
    stdio.writeln(total1/total2)
    stdio.writeln(time1/time2)

if __name__ == '__main__':
    main()
    
#-----------------------------------------------------------------------

# python stopwatch.py 1000000
# 1.0
# 3.6211243214440323

# python stopwatch.py 1000000
# 1.0
# 3.1306418500739683

