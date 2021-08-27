#------------------------------------------------------------------------------#
# Utility functions for compressing/decompressing files.
#------------------------------------------------------------------------------#
import zipfile # note, only formatting, does not compress/decompress
from zipfile import ZipFile
from stopwatch import Stopwatch
import stdio
import zlib
import datetime

import os

#-----------------------------------------------------------------------------//
# Compresses the given file.  Writes out new filename+'.zip'
# Returns the zipfilename
#-----------------------------------------------------------------------------//
def compress( filename ):
    zipfilename = filename + '.zip'
    #stdio.writeln('Creating zip file ' + zipfilename )
    zf = zipfile.ZipFile( zipfilename, mode='w' )
    
    # The name of the file in the archive, avoids directory structure being zipped
    arcname = os.path.basename(filename)
    #stdio.writeln('  compressing...' )
    zf.write( filename, arcname, compress_type=zipfile.ZIP_DEFLATED )
    zf.close()
    #stdio.writeln('Done.' )
    
    #info(zipfilename)
    
    return zipfilename



#-----------------------------------------------------------------------------//
# Decompresses the given file.  Writes out new filename without .zip extension.
# Returns the last unzipped filename (typically only one)
#-----------------------------------------------------------------------------//
def decompress( zipfilename, outputDir='.' ):
    #stdio.writeln('Creating unzipping file ' + zipfilename )
    zf = zipfile.ZipFile( zipfilename )
    lastfilename = None
    for filename in zf.namelist():
        #stdio.writeln('  decompressing '+ filename +'...' )
        zf.extract(filename, outputDir)
        lastfilename = filename
    zf.close()
    #stdio.writeln('Done.' )
    return filename


#-----------------------------------------------------------------------------//
# Prints to standard output information about the contents of the specified zip file
#-----------------------------------------------------------------------------//
def info( zipfilename ):
    #for name in zf.namelist():
    #    print( 'ZIPUTIL name: ' + name + ' = ' + str( zf.getinfo(name) ) )
    #for zipinfo in zf.infolist():
    #    print( 'ZIPUTIL info: ' + str( zipinfo ) )
    with ZipFile(zipfilename, 'r') as zip:
        for info in zip.infolist():
            print(info.filename)
            print('\tModified:\t' + str(datetime.datetime(*info.date_time)))
            print('\tSystem:\t\t' + str(info.create_system) + '(0 = Windows, 3 = Unix)')
            print('\tZIP version:\t' + str(info.create_version))
            print('\tCompressed:\t' + str(info.compress_size) + ' bytes')
            print('\tUncompressed:\t' + str(info.file_size) + ' bytes')


#------------------------------------------------------------------------------#
# Main function (avoid scipts, better to put in this function)
#------------------------------------------------------------------------------#
def main():
    # Perform encryption of hybrid scheme
    import sys
    #import os

    filename = sys.argv[1]
    #pathname, fileext  = os.path.splitext(filename)
    fileext = filename[len(filename)-4:]
    #stdio.writeln('File name = ' + filename)
    #stdio.writeln('File  ext = ' + fileext)
    #stdio.writeln('File sans ext = ' + filename[:-4] )

    if( fileext == '.zip' ):
        watch = Stopwatch()
        decompress( filename )
        decompress_time = watch.elapsedTime()
        stdio.writeln('Decompression took: ' + str(decompress_time) )
    else:
        watch = Stopwatch()
        compress( filename )
        compress_time = watch.elapsedTime()
        stdio.writeln('Compression took: ' + str(compress_time) )

#------------------------------------------------------------------------------#
# Call main if passed to python interpreter
#------------------------------------------------------------------------------#
if __name__ == '__main__':
    main()
