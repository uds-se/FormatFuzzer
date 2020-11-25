import os
from subprocess import Popen, PIPE, STDOUT
from PIL import Image
from natsort import natsorted, ns

folderToCheck = 'mp4/examples_2'
fileExtension = '.mp4'

def checkImageDetailed(directory, fn):

    #command = ['ffmpeg', '-i',  str(fn), '-c:v', 'libx264', '-y', '-c:a', 'libmp3lame', '-b:a', '384K', 'output.avi']
    command = ['ffmpeg', '-v',  'error','-i',str(fn), '-y','-f','null','-', 'output.avi']

    ffmpeg = Popen(command, stderr=PIPE ,stdout = PIPE )
    out, err = ffmpeg.communicate()
    exitcode = ffmpeg.returncode
    return exitcode, err

processedFilesList = []
errorDict = {}
errorDict["Correct files"] = 0;
def addToList(bucket, element):
    while(len(processedFilesList) <= bucket):
        newList = []
        processedFilesList.append(newList)
    processedFilesList[bucket].append(element)

def addToErrorList(error, element):
    errorMsgs = str(error).split("\\n")
    errorMsgs = [i for i in errorMsgs if len(i)>1]
    
    for errorMsg in errorMsgs:
        if(errorMsg not in errorDict):    
            errorDict[errorMsg] = len(errorDict)
    for errorMsg in errorMsgs:
        addToList(errorDict[errorMsg], element)

    
def iterateImages():
    for directory, subdirectories, files, in os.walk(folderToCheck):
        
        i = 1;
        for file in files:
            if file.endswith(fileExtension):
                filePath = os.path.join(directory, file)
                
                code, err = checkImageDetailed(directory, filePath)
                if str(code) !="0":
                    addToErrorList(err, file)
                else:
                    addToList(0, file)
                print("process file "+str(i)+"/"+str(len(files)))
                i = i+1

def summary():
    print("Summary folder "+folderToCheck+": ")  
    print("checked format "+fileExtension)        
    for errorCode in errorDict:
        print("     Category "+errorCode+" --> Ammount: "+str(len(processedFilesList[errorDict[errorCode]])))    
    
    
    
import os
from shutil import copyfile
 
 
os.system("make mp4_videoOnly-fuzzer")
i = 1;
while i < 10:
    os.system("./mp4_videoOnly-fuzzer fuzz mp4/examples_2/example.mp4")
       
    src = os.path.join("mp4/examples_2", "example.mp4")
    dst = os.path.join("mp4/examples_2", str(i)+".mp4")
    copyfile(src, dst)    
    i = i+1;
os.remove(os.path.join("mp4/examples_2", "example.mp4"))

    
iterateImages()
print("-------------- DONE --------------");
summary()