#
# This is a helper script that splits zip file into mulitple smaller files
# with the sizes smaller than 100mb so that Github won't complain anything
# about their file size.
#
# To use this script
#  - py split.py [filename]
#

import sys

# the maximum size of 'non-big' file on Github is 100MB
# I have to manually split all zip files before checking them in.
# 95mb is used instead of 100mb this is because Github has slightly
# more strict rule somehow the real size limitation is smaller than
# 100mb
ZIP_FILE_SIZE_CAP = 1024 * 1024 * 95

# make sure we have one valid argument
if len(sys.argv) > 1:
    # try reading the file
    file_name = sys.argv[1]

    f = None
    try:
        # open the file
        f = open(file_name, 'rb')

        # if the file doesn't exist, just emit a warning and bail
        if f.closed:
            print('Can\'t open the file!')
        else:
            # indicate a message that we are splitting a file
            print( 'Splitting file ' + file_name )

        # read the first trunk
        chunk = f.read(ZIP_FILE_SIZE_CAP)

        # new file index
        index = 0

        # loop until the chunk is empty (the file is exhausted)
        while chunk:
            # save the chunk data into a separate file
            new_file_name = file_name + str(index)
            new_file = open(new_file_name, 'wb+')
            new_file.write(chunk)
            new_file.close()

            print('Writing file ' + new_file_name )

            # update the index
            index = index + 1

            # read the next chunk
            chunk = f.read(ZIP_FILE_SIZE_CAP)

        # we are done here, close the file
        f.close()
    except:
        print('Failed to read file, maybe there is a typo in the file name?')
else:
    print("Missing file argument.")