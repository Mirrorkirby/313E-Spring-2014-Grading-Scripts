from os.path import os, exists
from datetime import datetime, timedelta
from functools import *
import math
import subprocess
import sys
import re
import difflib
import time

pipes = {'stdout':subprocess.PIPE, 'stdin':subprocess.PIPE, 'stderr':subprocess.PIPE}

outputFilename = 'assignment_08.txt'
outputFile = open(outputFilename, 'a')
filename = "Mondrian.py"
dateString = "3-7-2014 23:00:00"

def main():
  out = subprocess.getoutput('ls ./')
  CSIDS = out.split("\n")
  if len(sys.argv) == 3:
    outputFile.write('CSID\tGrade\tComments\n')
    lowerBound = sys.argv[1]
    upperBound = sys.argv[2] + '~';
    myList = []
    count = 0
    for item in CSIDS:
      if lowerBound <= item <= upperBound:
        if "." not in item :
          myList.append(item)
    for csid in myList :
      count += 1
      os.system('clear')
      print('======================')
      print(csid + " " + str(count) + " out of " + str(len(myList)))
      print('======================')
      assign08(csid, True)
  #singleton mode
  else:
    csid = sys.argv[1]
    os.system('clear')
    print('======================')
    print(csid)
    print('======================')
    assign05(csid, False)
  outputFile.close()

def assign08(csid, writeToFile) :
  fileToGrade = ""
  late = 0
  grade = 70
  style = 30
  wrongFileName = False
  header = True
  comments = []

  os.chdir(csid)
  if writeToFile: outputFile.write(csid + "\t")
  files = os.listdir('.')

  #filename checking
  for f in files :
    splitted = subprocess.getoutput('ls -l ' + f).split()
    if f == filename :
      fileToGrade = filename
      late = isLate(splitted)
      break
    elif f == filename.lower() :
      fileToGrade = filename.lower()
      late = isLate(splitted)
      wrongFileName = True
      break

  #really odd filename
  if fileToGrade == "" :
    print(subprocess.getoutput('ls -l'))
    fileToGrade = input("Which file should I grade? ")
    if fileToGrade == "" :
      if writeToFile:
        outputFile.write("0\tno file\n")
      os.chdir("..")
      return
    else :
      splitted = subprocess.getoutput('ls -l ' + fileToGrade.replace(' ','\ ')).split()
      late = isLate(splitted)
      wrongFileName = True

  #grading time!
  '''
  10 for output to file (.eps)
  10 for range (1-6)
  25 for "recursiveness"
  25 for randomness
  '''
  grade = 0

  #Test these recursive levels
  inputText = [1,3,4,4]
  second = False #used to determine if it's the second time we're doing 4
  if not (fileToGrade == '' and late != -1):
    # See if they output to an eps file
    if 'Mondrian.eps' in open(fileToGrade).read():
      grade += 10 #Get 10 pts for following instructions
      for reclevel in inputText:
        try:
          print("Using recursion level: ", str(reclevel))
          process = subprocess.Popen(['python3', fileToGrade], **pipes)
          out = process.communicate(bytes(str(reclevel), 'UTF-8'))[0]
          #rename the file to the adecuate one
          if not second:
            if reclevel == 4:
              second = True
              print("REPEATING")
            newFile = "Mondrian" + str(reclevel) + ".eps"
            print("Finished working on: ", newFile)
            process = subprocess.Popen(['cp', "Mondrian.eps", newFile], **pipes)
          else:
            #We're running recursive level 4 again to test for randomness
            newFile = "Mondrian" + str(reclevel) + "Random.eps"
            print("Finished working on: ", newFile)
            process = subprocess.Popen(['cp', "Mondrian.eps", newFile], **pipes)

        except KeyboardInterrupt:
          print(' passed ^C')

        #TODO: Check if I can create turtle object to close the window

    else:
      print("They didn't output to file!!!")
      print("We'll do it manually")
      for reclevel in inputText:
        try:
          print("Using recursion level: ", str(reclevel))
          process = subprocess.Popen(['python3', fileToGrade], **pipes)
          out = process.communicate(bytes(str(reclevel), 'UTF-8'))[0]
          #TODO: Add to the grade (check if it's fine)
          input()

          
        except KeyboardInterrupt:
          print(' passed ^C')

  

  #checking for header and style
  input("Hit Enter to cat first 20 lines (header)")
  print(subprocess.getoutput('head -20 ' + fileToGrade))
  headerInput = input("Header(y/n, hit enter for y): ")
  if headerInput == 'y' or headerInput == '':
    header = True
  else :
    header = False
  input("Hit Enter to cat whole file (style/comments)")
  print(subprocess.getoutput('cat ' + fileToGrade))
  style = input("Style/Other (Out of 30, hit enter for 30): ")
  gen_comments = input("General Comments?: ").rstrip().lstrip()
  gen_comments = gen_comments if len(gen_comments) is not 0 else "style"
  if not style.isdigit():
    style = 30
  else :
    style = int(style)
  if (gen_comments != "style" or style != 30):
    gen_comments += " (%+d)" % (style - 30)
    comments.append("%s" % gen_comments)

  #writing grade time!
  if late == -1:
    if writeToFile: outputFile.write('0\t More than 7 days late')
    print('Late more than 7 days!')
  else :
    if late == 3:
      comments.append("3-7 days late (-30)")
      grade -= 30
    elif late == 2:
      comments.append("2 days late (-20)")
      grade -= 20
    elif late == 1:
      comments.append("1 day late (-10)")
      grade -= 10

    if wrongFileName or not header:
      grade -= 5
      if wrongFileName and header:
        comments.append("wrong filename (-5)")
      elif header and not wrongFileName:
        comments.append("malformed header (-5)")
      else:
        comments.append("wrong filename and malformed header (-5)")

    if writeToFile: outputFile.write(str(grade+style) + "\t" + ', '.join(comments))

  if writeToFile: outputFile.write('\n')
  os.chdir("..")

#returns the number of days late an assignment is
def isLate(splitted):
  dueDate = datetime.strptime(dateString,"%m-%d-%Y %H:%M:%S")
  lateOne = dueDate + timedelta(days=1)
  lateTwo = lateOne + timedelta(days=1)
  lateSev = dueDate + timedelta(days=7)
  turninDate = datetime.strptime(splitted[5] + " " +(("0" + splitted[6]) if len(splitted[6]) == 1 else splitted[6])+ " " + splitted[7] +" 2014", "%b %d %H:%M %Y")
  if turninDate <= dueDate:
    return 0
  elif turninDate <= lateOne:
    return 1
  elif turninDate <= lateTwo:
    return 2
  elif turninDate <= lateSev:
    return 3
  else :
    return -1

main()
