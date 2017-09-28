#!/usr/bin/env python
# coding: utf-8

# ---
# --- IMPORTS
# ---

import xml.etree.ElementTree as ET
from optparse import OptionParser
import shutil
import time
import sys
import os

# ---
# --- FUNCTIONS
# ---

# Returns the content of the file f
def readAllFile(f):
	fd = open(f, "r")
	data = ""

	for line in fd.readlines():
		data += line

	fd.close()
	return data

# Correct the specials characters inside content
def correctSpecialCharacters(content):
	new = content

	new = new.replace('\\n', '\n')
	new = new.replace('\\t', '	')

	new = new.replace("$€n€$".decode('utf-8'), '\\n')
	new = new.replace("$€t€$".decode('utf-8'), '\\t')

	return new

# ---
# --- CLASSES
# ---

class Files():

	# List of all files alreayd opened and its contents
	def __init__(self):
		self.files = []

	# Insert text after position in project/name
	def insert(self, project, name, text, position):
		for f in self.files:
			if f['project'] == project and f['name'] == name:

				f['content'] = f['content'][:position] + text + f['content'][position:]

				return True

		return False

	# Remove all characters between start and end
	def remove(self, project, name, start, end):
		for f in self.files:
			if f['project'] == project and f['name'] == name:

				f['content'] = f['content'][:start] + f['content'][end:]

				return True

		return False

	# Returns True if the file is already opened
	def isOpened(self, project, name):
		for f in self.files:
			if f['project'] == project and f['name'] == name:
				return True
		return False

	# Opens the file (Warning: only saved when the file is closed)
	def open(self, project, name):
		if not self.isOpened(project, name):
			self.files.append({'project': project, 'name': name, 'content': ""})

	# Delete a project
	def deleteProject(self, project):
		self.files[:] = [element for element in self.files if element.get('project') != project]

	# Delete a file
	def deleteFile(self, project, name):
		self.files[:] = [element for element in self.files if element.get('project') != project or element.get('name') != name]


	# Close all files (Warning: this opens the file, write all contents on it, and close it)
	def closeAll(self):
		global globalPath

		while len(self.files) > 0:
			f = self.files.pop(0)

			fileName = globalPath + f['project'] + "/" + f['name']

			# Check if folder exists, and create it if necessary
			if not os.path.exists(os.path.dirname(fileName)):
				os.makedirs(os.path.dirname(fileName))

			fd = open(fileName, "w+");
			fd.write(f['content'].encode('utf-8','ignore'))
			fd.close()


	# Print all datas of all files
	def printAll(self):
		print self.files


# ---
# --- MAIN PROGRAM
# ---

# How long the build took
startTime = time.clock()

# Checks if we have an argument (ie: a xml file)

parser = OptionParser(usage="usage: %prog [options] <XML file>", version="%prog 1.1")

parser.add_option(
	"-f",
	"--force",
	action="store_true",
	dest="force_flag",
	default=False,
	help="force to rebuild all output folder"
)

(options, args) = parser.parse_args()

if len(args) != 1:
	parser.error("wrong number of arguments")

xmlFile = args.pop()

# Checks if the xml file exists and is xml
if not os.path.isfile(xmlFile):
	parser.error("File `" + xmlFile + "` doesn't exist...")
elif os.path.splitext(xmlFile)[1] != '.xml':
	parser.error("File `" + xmlFile + "` isn't xml...")

# We close the xml tag because it's still open
data = readAllFile(xmlFile) + "</TRACE>"
root = ET.fromstring(data)

maximum = len(root)

# Default location where projects and files will be located:
globalPath = "output/"

# We remove the output folder and it's content:	
if options.force_flag and os.path.exists(os.path.dirname(globalPath)):
	shutil.rmtree(globalPath)

# List of all files
files = Files()

# We loop through all the xml file
for i in range(0, maximum):

	attrib = root[i].attrib.get('K')

	# Insertion
	if attrib == "IT":

		currentProject  = root[i][0].text
		currentFile     = root[i][2].text
		currentPosition = int(root[i][3].text)

		content = correctSpecialCharacters(root[i][1].text)

		if not files.isOpened(currentProject, currentFile):
			files.open(currentProject, currentFile)

		files.insert(currentProject, currentFile, content, currentPosition)

	# Deletion
	elif attrib == "ST":

		currentProject  = root[i][0].text
		currentFile     = root[i][3].text
		cursorStart     = int(root[i][1].text)
		cursorEnd       = int(root[i][4].text)

		if not files.isOpened(currentProject, currentFile):
			files.open(currentProject, currentFile)

		files.remove(currentProject, currentFile, cursorStart, cursorEnd)

	# Delete a project
	elif attrib == "SP":

		currentProject  = root[i][0].text

		files.deleteProject(currentProject)

	# Delete a file
	elif attrib == "SF":

		currentProject  = root[i][0].text
		currentFile     = root[i][2].text

		files.deleteFile(currentProject, currentFile)


# We close the files (and save them)
files.closeAll()

# How long the build took
endTime = time.clock()
print "Done (in " + str(endTime - startTime) + "s)."
