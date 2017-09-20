# coding: utf-8

import xml.etree.ElementTree as ET


tree = ET.parse('data.xml')
root = tree.getroot()


#maximum = len(root)
maximum = 20
for i in range(0, maximum):
	if root[i].attrib.get('K') == "IT":

		currentProject  = root[i][0].text
		currentFile     = root[i][2].text
		currentPosition = int(root[i][3].text)

		content = root[i][1].text.replace('\\n', '\n').replace('\\t', '	')

		#print currentPosition, content

		f = open(currentFile, "r+b")

		everything = f.read()
		everything = everything[:currentPosition] + content + everything[currentPosition + 1:]
		f.seek(0)
		f.truncate()

		f.write(everything)

		f.close()
