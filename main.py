from PIL import Image
import os
import glob
import argparse
import exifread

# get all files in the path
def GetFileList(path):
    fileList = []
	
	#scan all folders/files
    for filename in glob.iglob(path, recursive=True):
        img = Image.open(filename)
        width, height = img.size
        size = os.path.getsize(filename)

        f = open(filename, 'rb')
        tags = exifread.process_file(f)

        if tags.__contains__('Image DateTime'):
            fileList.append([filename, width, height, size,
                             False, tags['Image DateTime']])
        else:
            fileList.append([filename, width, height, size, False, ''])

        # print every file add in this list
        #print(filename, " >", width, height, size)

    return fileList


def CheckSameFile(file1, file2):
    if (file1[1] == file2[1] and  # heigth
        file1[2] == file2[2] and  # width
        file1[3] == file2[3] and  # size
        file1[5] == file2[5] and  # dateTime
            file1[0] != file2[0]):  # path
        return True
    return False


# program parameters
parser = argparse.ArgumentParser()
parser.add_argument('-same', action='store_true')
parser.add_argument('-iteractive', action='store_true')
parser.add_argument('-recursive', action='store_true')
parser.add_argument('-path', type=str)
args = parser.parse_args()

SAME_FOLDER = False
ITERACTIVE = False

if (args.same):
    SAME_FOLDER = True
if (args.iteractive):
    ITERACTIVE = True


# set folder path to search files
if (args.path):
    if(args.recursive):
        path = args.path + "/**/*.jpg"
    else:
        path = args.path + "/*.jpg"
#path = "C:/Users/thomas/Pictures/**/*.jpg"


# get the file list, containing: path, height, width, size(bytes), occurence, Image DateTime metadata, of each image file
fileList = GetFileList(path)
listLen = len(fileList)

#debug log
streamFile = open("duplicatedFiles.txt", "w")
countDuplicated = 0
duplicadedSize = 0


for file in fileList:
    added = False
    tmpString = ""
    sameFolder = False
    folderPath1 = file[0][:file[0].rfind('\\')]
    if (not file[4]):
        for cFile in fileList:
            if (CheckSameFile(file, cFile)):
                sameFolder = False
                folderPath2 = cFile[0][:cFile[0].rfind('\\')]

                tmpString += "\t" + cFile[0] + "\n"

                if(folderPath1 == folderPath2):
                    sameFolder = True

				#TODO: create a single window for both images
				#TODO: create a UI Button instead of a console
                if not(not sameFolder and SAME_FOLDER):
                    cFile[4] = True
                    added = True
                    countDuplicated += 1
                    duplicadedSize += cFile[3]

					
                    if ITERACTIVE:
						#show the two duplicated images
						#to guarantee that both images are equal
                        img = Image.open(file[0])
                        img.show()
                        img2 = Image.open(cFile[0])
                        img2.show()
						
						#print the path of both images
						#used to help user to determine which file will be deleted
                        print("[1] " + file[0][:file[0].rfind('\\')] +
                              "\t" + file[0][file[0].rfind('\\'):])
                        print("[2] " + cFile[0][:cFile[0].rfind('\\')] +
                              "\t" + cFile[0][cFile[0].rfind('\\'):])

						#input
                        keyPressed = input(
                            "Action to do: [1 or 2] Remove; [any] Nothing.\n")

                        if(keyPressed == '1'):                        
                            os.remove(file[0])
							print('Deleted first file\n', file[0])
                        elif(keyPressed == '2'):
                            os.remove(cFile[0])
							print('Deleted second file\n', cFile[0])
                        else:
                            print("Nothing done!\n")

		#if some file was deleted, add the file's name to output log
        if added:
            streamFile.write(file[0] + "\n")
            streamFile.write(tmpString)
			
streamFile.close()

#report of deleted files
print(listLen, " files checked! With ", countDuplicated,
      " files duplicaded (", duplicadedSize/(1024*1024), "MB)\n")
