# Requires commonmark (pip install CommonMark)

from os import listdir
from os.path import isfile, isdir, join
import commonmark
import shutil
import re
from distutils.dir_util import copy_tree
from railroad_diagrams import parseDiagram
import io

railroadPattern = re.compile('```Railroad:(.*)```', re.MULTILINE)

with open("template.html", "r") as templateFile:
    template = templateFile.read()

def diagramProcessor(match):
    diagram = parseDiagram(match.group(1))
    output = io.StringIO()
    diagram.writeSvg(output.write)
    return output.getvalue()


def processRailroadPatterns(content):
    current = 0
    fromIndex = content.find('```Railroad')
    fileOutput = io.StringIO()
    while fromIndex >= 0:
        toIndex = content.find('```', fromIndex + 11)
        diagramContent = content[fromIndex + 11:toIndex]
        diagram = parseDiagram(diagramContent)
        output = io.StringIO()
        diagram.writeSvg(output.write)
        fileOutput.write(content[current:fromIndex])
        fileOutput.write(output.getvalue())
        current = toIndex + 3
        fromIndex = content.find('```Railroad', current)
    fileOutput.write(content[current:])
    return fileOutput.getvalue()


def compileFile(inputFilename, outputFilename, up):
    with open(inputFilename, "r") as myfile:
        contentLines = myfile.readlines()
        content = "".join(contentLines)

    #content = railroadPattern.sub(diagramProcessor, content)
    content = processRailroadPatterns(content)
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
