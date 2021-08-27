from datetime import datetime
import time
from outstream import OutStream
import os
import fileutil

class Recorder:
    """
    Recorder provides utility methods to log key-value pairs and then flush so
    that it writes to file in an auditd compatible format.
    The incrementEventid should be called before attempting to write or flush
    so that the eventid and event time are properly set.
    """

    def __init__(self, file ):
        self._outstream = OutStream(file)
        self._file      = file
        self._eventid   = 0
        self._eventtime = None
        self._keys      = list()
        self._vals      = list()


    def getFile(self):
        """
        Returns the file associated with this recorder.
        """
        return self._file


    def getFileSize(self):
        """
        Gets the file size in bytes.
        """
        stats = os.stat(self._file)
        return stats.st_size

    def append(self, key, val):
        """
        Appends the key and value to the buffer to be written out in flush.
        The key should be of type str, the val will be coverted to str.
        The flush should be called after desired appends have been made.
        """
        if( not isinstance(key, str) ):
            raise TypeError('The key must be of type str, was ' + str(type(key)) )
        #if( not isinstance(val, str) ):
        #    raise TypeError('The val must be of type str, was ' + str(type(val)) )
        self._keys.append(key)
        self._vals.append(val) # may be a dictionary or str


    def flush(self):
        """
        Creates str from key value buffers and writes to file.
        The buffers are cleared.  This method should be used after calling append.
        """
        if( len(self._keys) > 0 ):
            kvpList = []
            for i in range(len(self._keys)):
                key = self._keys[i]
                val = self._vals[i]
                kvp = None
                kvp = '"%s":["%s"]' % (key, str(val))
                kvpList.append( kvp )
            kvpStr = ", ".join(kvpList)
            # Clear the lists
            self._keys = list() # clear the list, clear() did not work?
            self._vals = list() # clear the list, clear() did not work?


            # Convert timestamp into human readable date
            humantime = fileutil.formatTime( self._eventtime )

            self._outstream.writef('{"serial":%d, "timestamp":%.3f, "time":"%s", "data":{%s}},\n',
                                 self._eventid, self._eventtime, humantime, kvpStr )
            #self.writeLine( kvpStr )


    def incrementEventid(self):
        """
        Increments to create a new event with a new timestamp.  Users should promptly call
        the writeKeyValue method and finish with flush.
        """
        self._eventtime = time.time() # 1624868759.1945467, seconds since the epoch
        self._eventid = self._eventid + 1

    def writeln(self, key, val):
        """
        Immediately writes to file with the key and value.
        The key should be of type str, the val will be coverted to str.
        """
        #self.writeLine( key + "=" + str(val) ) # auditd deprecated format
        kvp = '"%s":["%s"]' % (key, str(val))
        self.writeLine( key, kvp )

    def writeLine(self, type, kvpStr):
        """
        Immediately writes kvpStr to file with header prefix.
        """
        # auditd deprecated format
        #self._outstream.writef('type=PSUTIL_CPU msg=audit(%.3f:%d): %s\n', self._eventtime, self._eventid, kvpStr )

        # Convert timestamp into human readable date
        humantime = fileutil.formatTime( self._eventtime )

        # The eventid and type should make record unique
        uniqueKey = type + str(self._eventid)

        self._outstream.writef('"%s" : {"type":"%s", "serial":%d, "timestamp":%.3f, "time":"%s", "data":{%s} },\n',
                             uniqueKey, type, self._eventid, self._eventtime, humantime, kvpStr )

    def __del__(self):
        """
        Close the stream.
        """
        del( self._outstream )
