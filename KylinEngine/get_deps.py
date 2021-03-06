#
# This is a helper script that merges the split files by the script split.py
# If the directory only has one single file, it won't do anything about it.
# Otherwise, it will simply merge all files ended with zip* into a big file
# that ends with zip.
#
# Warning, the directory should have only one single set of split zip files.
# This is an assumption made by this script to simplify things.
#
# This file should be part of whichever project uses this repo as a
# dependency repo.
#
# To use this script
#  - py split.py [directory]
#

import os
import sys
import zipfile
import urllib.request

# the maximum size of 'non-big' file on Github is 100MB
# I have to manually split all zip files before checking them in.
ZIP_FILE_SIZE_CAP = 1024 * 1024 * 100

# dependecy directory
dependency_dir = '.'

# unzip what is in the directory
def unzip_dir(directory):
    # nothing
    zip_file_name = ''

    # at least check if this is a valid directory before moving on
    if not os.path.isdir(directory):
        print('Not a valid directory \"' + directory + '\"!')
    else:
        # index
        index = 0

        # whether there is more files to merge
        no_more_files = False

        # file to be written
        file = None

        # idealy, there could be more optimized version of doing this since this is 
        # essentially O(NxM) with M being the number of files in the directory and
        # N being the number of split zip files, which commonly equal to M.
        while not no_more_files:
            # whether we found a match
            found = False

            # loop through all files and merge those ends with 'zip*'
            for filename in os.listdir(directory):
                # search for the extension
                ext = 'zip' + str(index)

                # see if this file has that extention
                if filename.endswith(ext):
                    # we have a match
                    found = True
                    
                    # if this is the first time, create file
                    if file is None:
                        # use the same file name
                        zip_file_name = directory + '/' + os.path.splitext(filename)[0] + '.zip'
                        file = open(zip_file_name, 'wb+')

                    # indicate that we are merging this file
                    print('Merging file ' + filename)

                    # simply pack whatever is in that file to the bigger file
                    full_split_file_name = directory + '/' + filename
                    split_file = open(full_split_file_name, 'rb')

                    # read the first trunk
                    chunk = split_file.read(ZIP_FILE_SIZE_CAP)

                    # loop until the chunk is empty (the file is exhausted)
                    while chunk:
                        # just flush the content into the bigger file
                        file.write(chunk)

                        # read the next chunk again
                        # this shouldn't be neccessary if the split files are split
                        # by the script split.py
                        # however, this is still done this way to offer a bit of
                        # flexibility
                        chunk = split_file.read(ZIP_FILE_SIZE_CAP)

                    # close the file
                    split_file.close()

                    # delete the file since we don't need it anymore
                    os.remove(full_split_file_name)

                    # update the index
                    index = index + 1

                    # no need to keep searching anymore, we are done here
                    break
                else:
                    # not this one, keep going
                    continue

            # we are done here
            if not found:
                no_more_files = True
        
        # if we do have a file written, close it since we are done here
        if file is not None:
            # indicate the output file
            print( 'Merged file ' + zip_file_name )

            # we are done
            file.close()

        # if we don't have a valid 'zip_file_name', it means we have one single
        # zip file in this folder, find it
        for filename in os.listdir(directory):
            # we should have only one single zip file in this folder
            # we don't care about the second one
            if filename.endswith('zip'):
                zip_file_name = directory + '/' + filename

        if zip_file_name != "":
            # indicate that we are unzipping the file
            print('Decompress file ' + zip_file_name)
            
            # now that we know we have a zip file for sure, unzip it
            with zipfile.ZipFile(zip_file_name,"r") as zip_ref:
                zip_ref.extractall(directory)

            # we don't need the zip file anymore, delete it
            os.remove(zip_file_name)
        else:
            # no valid zip file, something is wrong
            print('No valid zip file in directory ' + directory)

# helper function to download all zip files and decompress them
def sync_files(dep_file_urls, folder_name):
    # dependency file list
    dep_files = []

    # check if the dependency is ready
    dep_folder = dependency_dir + '/' + folder_name
    if os.path.isdir(dep_folder):
        print('Skipping dependency ' + folder_name + ' as it is existed.')
        dep_file_urls.clear()
        return

    # create the new dir
    os.mkdir(dep_folder)

    # retrieve all the files first
    for file_url in dep_file_urls:
        # extract a the file name from url
        last_slash = file_url.rfind('/')
        file_name = file_url[last_slash:]

        # get rid of the new line signal
        if file_url[-1] == '\n':
            file_name = file_url[last_slash:-1]

        # get a temporary name for it first
        temp_file = dep_folder + '/' + file_name

        # retrieve the file
        urllib.request.urlretrieve(file_url, temp_file)

        # mark the file so that it will be deleted later
        dep_files.append(temp_file)

    # clear this list
    dep_file_urls.clear()

    # decompress the files
    unzip_dir(dep_folder)

# main function
def main():
    # make sure we have one valid argument
    if len(sys.argv) <= 1:
        print("Missing directory argument.")
        return

    # setup dependecy directory if needed
    if len(sys.argv) >= 3:
        global dependency_dir
        dependency_dir = './' + sys.argv[2]

        # create the directory if needed
        if not os.path.isdir(dependency_dir):
            os.makedirs(dependency_dir)

        print('Dependency directory is \'' + dependency_dir + '\'')

    # argument one has to be the url leads to the dependency list
    url = sys.argv[1]

    # get content from the url
    file = urllib.request.urlopen(url)

    folder_name = ''
    dep_file_urls = []

    # iterate the file line by line
    for line in file:
        line = line.decode("utf-8").strip()

        # flush the previously cached dependency files
        if line != "" and line[0] == '[':
            if folder_name != '':
                sync_files(dep_file_urls, folder_name)
            
            s = 1
            e = line.rfind(']')
            folder_name = line[s:e]
        else:
            # push it in the dependency list
            if len(line) > 0:
                dep_file_urls.append(line)

    # see if we have any left-over dependency
    if dep_file_urls:
        sync_files(dep_file_urls, folder_name)
        pass

# main function
if __name__ == "__main__":
    main()