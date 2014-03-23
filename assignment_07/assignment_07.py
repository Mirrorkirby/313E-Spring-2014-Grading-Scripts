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

outputFilename = 'assignment_07.txt'
filename = "Boxes.py"
dateString = "2-28-2014 23:00:00"

outputFile = open(outputFilename, 'a')

def execute(cmd, timeout=15):
    sub = subprocess.Popen(cmd, **pipes)
    curr = 0
    while curr < timeout and sub.poll() is None:
        time.sleep(1)
        curr += 1
    if sub.poll() is None:
        sub.terminate()
        return -1, ''
    else:
        return sub.poll(), sub.communicate()[0].decode('utf-8')

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
      assign07(csid, True)
  #singleton mode
  else:
    csid = sys.argv[1]
    os.system('clear')
    print('======================')
    print(csid)
    print('======================')
    assign07(csid, False)
  outputFile.close()

def assign07(csid, writeToFile) :
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
  7 test cases (10 pts each) = 70 pts
  '''
  grade = 0
  inFiles = ['test1.in', 'test2.in', 'test3.in', 'test4.in', 'test5.in', 'test6.in', 'test7.in']
  outFiles = ['test1.out', 'test2.out', 'test3.out', 'test4.out', 'test5.out', 'test6.out', 'test7.out']

  for idx in range(len(inFiles)):
    print('Test ' + str(idx + 1) + ':')

    os.system('cp ../' + inFiles[idx] + ' Boxes.txt')
    os.system('cp ../' + inFiles[idx] + ' boxes.txt')
    # output = subprocess.getoutput('python3 ' + fileToGrade).split('\n\n')
    signal, output = execute(['python3', fileToGrade], 15)
    output = output.split('\n\n')
    correct = open('../' + outFiles[idx]).read().split('\n\n')

    subsets = set()
    correctSubsets = set()

    if signal != -1:
      for out in output:
        boxes = set()
        for line in out.split('\n'):
          box = set()
          for d in re.sub('[^\d]', ' ', line).split(' '):
            if d.isdigit():
              box.add(int(d))
          if len(box) == 3:
            boxes.add(frozenset(box))
        if len(boxes) > 0:
          subsets.add(frozenset(boxes))

      for cor in correct:
        boxes = set()
        for line in cor.split('\n'):
          box = set()
          for d in re.sub('[^\d]', ' ', line).split(' '):
            if d.isdigit():
              box.add(int(d))
          if len(box) == 3:
            boxes.add(frozenset(box))
        if len(boxes) > 0:
          correctSubsets.add(frozenset(boxes))

      if (subsets == correctSubsets):
        print('\tPassed')
        grade += 10
      else:
        print('\tFailed (-10)')
        comments.append('Failed Test ' + str(idx + 1))
    else:
      print('\tTimed Out (-10)')
      comments.append('Failed Test ' + str(idx + 1) + ' (Timed Out)')

  if grade == 70:
    print('Perfection =D')
  else:
    print('Grade: ' + str(grade) + '/70')

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
      elif not header and not wrongFileName:
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