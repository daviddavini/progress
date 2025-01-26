import argparse
import os
import re
import sys
import glob

class Section:
    def __init__(self, indent: int, done: bool, title: str):
        self.parent = None
        self.subs = []
        self.indent = indent
        self.done = done
        self.title = title
    def __str__(self):
        return self.title
    def __repr__(self):
        return f'Section({self.indent},{self.done},"{self.title}")'

    def descendants(self):
        descs = [self]
        for sub in self.subs:
            descs.append(sub)
            descs.extend(sub.descendants())
        return descs

    def completion(self):
        descs = self.descendants()
        done = [x for x in descs if x.done]
        return len(done), len(descs)

def to_section_tree(f):
    prev = None
    for line in lines:
        if line.isspace():
            continue
        m = re.match(r"(x* *)(.*)", line)
        spaces = m.group(1)
        title = m.group(2)
        indent = len(spaces)
        done = False if indent == 0 else spaces[0] == 'x'
        section = Section(indent, done, title)
        if prev is None:
            assert indent == 0
            root = section
        else:
            if indent == prev.indent:
                section.parent = prev.parent 
                prev.parent.subs.append(section)
            elif indent > prev.indent:
                assert indent == prev.indent+4
                section.parent = prev
                prev.subs.append(section)
            else:
                while indent < prev.indent:
                    prev = prev.parent
                assert indent == prev.indent
                section.parent = prev.parent
                prev.parent.subs.append(section)
            assert section.parent is not None 
        prev = section
    return root

def percent_str(x,y):
    return f"{x/y:.0%}"
    # return ' ' if x==0 else f"{x/y:.0%}"

def fraction_str(x,y):
    return f"{x}/{y}"
def progress_str(x,y):
    return f"{percent_str(x,y):>4} {fraction_str(x,y):<8}"

def print_completion(root: Section):
    print(f"Title:\t{root.title}")
    for sub in root.subs:
        done, descs = sub.completion()
        print(f"{progress_str(done,descs)} {sub.title}")
    done, descs = root.completion()
    print(f"Total completion: {progress_str(done,descs)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser('progress')
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-o', '--output', choices=['text','html'], default='text')
    args = parser.parse_args()
    if not args.filename:
        for category in os.listdir('library'):
            for tech in os.listdir(os.path.join('library',category)):
                print(tech.upper())
                for level in ['spec','docs','guides']:
                    print(f'    {level}')
                    for book in glob.glob(os.path.join('library',category,tech,level,'*.progress')):
                        with open(book) as f:
                            lines = f.readlines()
                            root = to_section_tree(f)
                        done, descs = root.completion()
                        print(f"        {progress_str(done,descs)} {root.title}")
    else:
        with open(args.filename) as f:
            lines = f.readlines()
            root = to_section_tree(f)
        print_completion(root)
