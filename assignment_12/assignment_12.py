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

outputFilename = 'assignment_12.txt'
outputFile = open(outputFilename, 'a')
filename = "TestSparseMatrix.py"
dateString = "4-05-2014 23:59:59"

def main():
  editor = ''
  if input('Want to use Sublime instead of cat? (N for No) ') != 'N':
    editor = '~/sublime_text'
  elif input('Want to use Vim instead of cat? (N for No) ') != 'N':
    editor = 'vim'

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
      assign12(csid, True,editor)

  #singleton mode
  else:
    csid = sys.argv[1]
    os.system('clear')
    print('======================')
    print(csid)
    print('======================') 
    assign12(csid, False,editor)
  outputFile.close()

def assign12(csid, writeToFile,editor):
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
  70 + 10
  
  15 - Sparse add()
  15 - Sparse mult()
  10 - Sparse getRow()
  10 - Sparse getCol()
  20 - Sparse str()
    10 - formatting
    10 - including 0's
  setElement broken = -10

  +10 - Sparse str() extra credit
  '''
  grade = 70

  #Test these squares
  formatting = True
  if not (fileToGrade == '' and late != -1):
    #grab output
    output = []
    for run in range(1,4):
      try:
        print("\n=====File %d===== (Ours then Theirs)"%run)
        testFile = 'matrix%d.txt'%run
        outFile = 'out%d.txt'%run
        correctFile = '../correct%d.txt'%run
        os.system('cp ../'+ testFile +' matrix.txt')
        output.append(subprocess.getoutput('python3 ' + fileToGrade + '> ' + outFile).splitlines())

        #modifying output
        f = open(outFile,'r')
        lines = f.readlines()
        f.close()
        f = open(outFile,'w')
        lines = [x.rstrip() for x in lines]
        lines = list(filter(None,lines))
        f.write('\n'.join(lines))
        f.close()

        os.system('diff -yB ' + correctFile +' '+outFile)
        print('\n'+'='*35)
      except KeyboardInterrupt:
        print(' passed on run',run)

      off = input('points off: ')
      while off != '':
        grade -= int(off)
        print('Current Grade: %d'%grade)
        comment = input('comments? ')
        if comment != '':
          comments.append(comment + ' (-%s)'%off)
        off = input('points off: ')
    print()

  if grade >= 70:
    print("<('.')^ Perfection ^('.')>")      
    print("Grade: %d/70"%grade)      
  else:
    print("Grade: %d/70"%grade)      

  #checking for header and style
  input("Hit Enter to cat first 20 lines (header)")
  print(subprocess.getoutput('head -20 ' + fileToGrade))
  headerInput = input("Header(y/n, hit enter for y): ")
  if headerInput == 'y' or headerInput == '':
    header = True
  else:
    header = False
  input("Hit Enter to cat whole file (style/comments)")
  if editor != '':
    os.system(editor +' '+ fileToGrade)
  else:
    print(subprocess.getoutput('cat ' + fileToGrade))
  style = input("Style/Other (Out of 30, hit enter for 30): ")
  gen_comments = input("General Comments?: ").strip()
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
