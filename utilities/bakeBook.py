#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bake book6 into a single markdown file"""

# Version: 2024-01-14 - original


########################################################
# Copyright (C) 2022-2023 Brian E. Carpenter.                  
# All rights reserved.
#
# Redistribution and use in source and binary forms, with
# or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above
# copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials
# provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of
# its contributors may be used to endorse or promote products
# derived from this software without specific prior written
# permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS  
# AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED 
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A     
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)    
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING   
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE        
# POSSIBILITY OF SUCH DAMAGE.                         
#                                                     
########################################################

from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askokcancel, askyesno, showinfo

import time
import os

def logit(msg):
    """Add a message to the log file"""
    global flog, printing
    flog.write(msg+"\n")
    if printing:
        print(msg)
        
def logitw(msg):
    """Add a warning message to the log file"""
    global warnings
    logit("WARNING: "+msg)
    warnings += 1

def dprint(*msg):
    """ Diagnostic print """
    global printing
    if printing:
        print(*msg)

def crash(msg):
    """Log and crash"""
    printing = True
    logit("CRASH "+msg)
    flog.close()
    exit()    

def rf(f):
    """Return a file as a list of lower case strings"""
    file = open(f, "r",encoding='utf-8', errors='replace')
    l = file.readlines()
    file.close()
    return l

def file_ok(fn):
    """Check if a local file is OK"""
    if fn.startswith("../"):
        fn = fn.replace("../","")
    fn = fn.replace("%20"," ")
    return os.path.exists(fn)


def wf(f,l):
    """Write list of strings to file"""
    global written
    file = open(f, "w",encoding='utf-8')
    for line in l:
        file.write(line)
    file.close()
    logit("'"+f+"' written")
 

def uncase(l):
    """Return lower case version of a list of strings"""
    u = []
    for s in l:
        u.append(s.lower())
    return u

def fix_section(raw):
    """Change citations throughout a section"""
    new = []
    for line in raw:
        if "](" in line:
            outline = ""
            while "](" in line:
                head, line = line.split("](", maxsplit=1)
                if line.startswith("https:") or line.startswith("http:"):
                    outline += head + "](" 
                    continue # Web reference, nothing to change
                target, line = line.split(")", maxsplit=1)
                if "/" in target:
                    _, target = target.rsplit("/", maxsplit=1)
                if target[0].isdigit():
                    #Chapter number will not be in anchor
                    _, target = target.split("%20", maxsplit=1)
                if target.endswith(".md"):
                    target = target.replace(".md","")
                target = target.replace("%20","-").replace(".","").lower() 
                if target == "contents":
                    #Special case
                    target = "list-of-contents"
                outline += head + "](#" + target +")"
            outline += line
        else:
            outline = line
        #Avoid unwanted anchors
        if outline.startswith("## ["):
            #Assume this is a chapter contents item
            outline = outline[3:]
        new.append(outline)
    new.append(page_break)
    return(new)



page_break = '<!-- page break -->\n'

######### Startup

#Define some globals

printing = False # True for extra diagnostic prints
warnings = 0

#Announce

Tk().withdraw() # we don't want a full GUI

T = "Book baker."

printing = askyesno(title=T,
                    message = "Diagnostic printing?")

where = askdirectory(title = "Select main book directory")
                   
os.chdir(where)

#Open log file

flog = open("bakeBook.log", "w",encoding='utf-8')
timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC%z",time.localtime())
logit("bakeBook run at "+timestamp)

logit("Running in directory "+ os.getcwd())


showinfo(title=T,
         message = "Will read current book6 text.\nTouch no files until done!")


######### Create empty output

baked = []

######### Title page

title = rf("title.md")
title.append("\nVersion captured at "+timestamp+"\n")
title.append(page_break)
baked += title
del title

######### Contents

# Read raw contents

contents = rf("Contents.md")

# Make list of section files to be baked

preamble = True
fns = []
for line in contents:
    if line.startswith("[1. Introduction]"):
        preamble = False
    if preamble:
        continue #ignore preamble
    if not line.strip():
        continue #ignore blank
    if line.startswith("["):
        # directory name
        _, tail = line.split("](")
        dirname, filename = tail.split("/")
        dirname = dirname.replace("%20", " ")
        filename = filename.replace("%20", " ").replace(")", "").replace("\n", "")
    elif line.startswith("*"):
        filename = line.replace("* ", "").replace("%20", " ").replace("\n", "") + ".md"
    fns.append(dirname+"/"+filename)
        
# Pre-bake contents

contents = fix_section(contents)

# Special case for links to indexes

for i in range(len(contents)):
    line = contents[i]
    if "(#index)" in line:
        contents[i] = line.replace("(#index)", "(#book6-Main-Index)")
    elif "(#citex)" in line:
        contents[i] = line.replace("(#citex)", "(#book6-Citation-Index)")
        
baked += contents

######### Main text

for fn in fns:
    baked += fix_section(rf(fn))


######### Indexes

baked += fix_section(rf("Index.md"))
baked += fix_section(rf("Citex.md"))

######### Write the baked file

wf("baked.md", baked)

######### Close log and exit
    
flog.close()

if warnings:
    warn = str(warnings)+" warning(s)\n"
else:
    warn = ""

showinfo(title=T,
         message = warn+"Check bakeBook.log.")

             


