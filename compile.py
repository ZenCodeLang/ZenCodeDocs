# Requires commonmark (pip install CommonMark)

from os import listdir
from os.path import isfile, isdir, join
import commonmark
import shutil
from distutils.dir_util import copy_tree
from railroad_diagrams import Diagram

with open("template.html", "r") as templateFile:
	template = templateFile.read()

def compileFile(inputFilename, outputFilename, up):
	with open(inputFilename, "r") as myfile:
		contentLines = myfile.readlines()
		content = "".join(contentLines)
	
	title = contentLines[0][1:].strip()
	html = commonmark.commonmark(content)
	result = template.replace("{content}", html).replace("{up}", up).replace("{title}", title)
	with open(outputFilename, "w") as myfile:
		myfile.write(result)
	

def compileDir(inputDir, outputDir, up):
	for f in listdir(inputDir):
		input = join(inputDir, f)
		output = join(outputDir, f)
		
		if isfile(input) and input[-3:] == ".md":
			compileFile(input, output.replace(".md", ".html"), up)
		elif isdir(input):
			compileDir(input, output, "../" + up)

shutil.rmtree("html", True)
copy_tree("template", "html")
compileDir("src", "html", "")
