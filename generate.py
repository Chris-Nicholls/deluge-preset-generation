from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

import random

onlyfiles = [f for f in listdir("./") if  isfile(f)]
xmlfiles = [f for f in onlyfiles if f.endswith(".XML")]


class AttribCount:                     # The target object of the parser
     current = []

     attrib_count = 0
     def start(self, tag, attrib):   # Called for each opening tag.
         self.attrib_count += len(attrib)
             
         
     def end(self, tag):             # Called for each closing tag.
         pass
     def data(self, data):
         pass
     def close(self):    # Called when all data has been parsed.
         pass

def count_attrs_string(s):
    count = AttribCount()
    parser = XMLParser(target=count)
    parser.feed(s)
    parser.close()
    return count.attrib_count

def count_attrs_file(f):
    return count_attrs_string(open(f).read())

def count_attrs(e):
    total = len(e.attrib)
    for c in e.getchildren():
        total += count_attrs(c)
    return total

def coin_flip():
    return random.choice([True, False])

def merge_dict(d1, d2):
    result = {}
    keys = list(d1.keys()) + list(d2.keys())

    for k in keys:
        if k in d1 and k in d2:
            result[k] = random.choice([d1[k], d2[k]])
        elif k in d1 and coin_flip():
            result[k] = d1[k]
        elif k in d2 and coin_flip():
            result[k] = d2[k]
    return result

basic_nodes = ["lfo1","modulator1", "modulator2", "lfo2", "unison", "delay", "compressor", "arpeggiator"]
default_param_nodes = ["envelope1","envelope2","equalizer"]
class Patch:
    
    def __init__(self, file=None, patch1=None, patch2=None):
        self.top_level = {}
        self.nodes = {}
        self.mod_knobs = []
        self.patch_cables = {}
        self.default_param_nodes = {}
        self.default_params = {}
        self.osc1 = {}
        self.osc2 = {}

        if file != None: 
            self.init_from_file(file)
        
        elif patch1 != None and patch2 != None:
            self.init_from_patches(patch1, patch2)

    def init_from_patches(self, patch1, patch2):
        self.filename = "z" + str(i) + " " + patch1.filename[:-4][:10] + " + " + patch2.filename[:-4][:10] +  ".XML"

        self.top_level = merge_dict(patch1.top_level, patch2.top_level)
        self.nodes = merge_dict(patch1.nodes, patch2.nodes)
        self.default_params =  merge_dict(patch1.default_params, patch2.default_params)
        self.default_param_nodes = merge_dict(patch1.default_param_nodes, patch2.default_param_nodes)
        self.osc1 = random.choice([patch1.osc1, patch2.osc1])
        self.osc2 = random.choice([patch1.osc2, patch2.osc2])
        self.patch_cables = merge_dict(patch1.patch_cables, patch2.patch_cables)

        for n in range(16):
            self.mod_knobs += [random.choice([patch1.mod_knobs[n], patch2.mod_knobs[n]])]

    
    def init_from_file(self, file):
        self.filename=file

        xml_elem = ET.parse(file)

        self.osc1 = xml_elem.findall("osc1")[0]
        self.osc2 = xml_elem.findall("osc2")[0]
 
        for n in basic_nodes:
            es = xml_elem.findall(n)
            if (len(es) == 1):
                self.nodes[n]= es[0].attrib

        for n in default_param_nodes:
            es = xml_elem.findall("defaultParams/" + n)
            if (len(es) == 1):
                self.default_param_nodes[n]= es[0].attrib

        for n in default_param_nodes:
            es = xml_elem.findall("defaultParams")
            if (len(es) == 1):
                self.default_params= es[0].attrib

        for n in xml_elem.findall("modKnobs/modKnob"):
            self.mod_knobs += [n.attrib]
        for n in xml_elem.findall("defaultParams/patchCables/patchCable"):
            self.patch_cables[(n.attrib["source"], n.attrib["destination"])] = n.attrib
        self.top_level = xml_elem.getroot().attrib

    def count_attrs(self):
        total = 0
        for n in self.nodes:
            total += len(self.nodes[n])
        for n in self.default_param_nodes:
            total += len(self.default_param_nodes[n])
        for n in self.mod_knobs:
            total += len(n)
        for p in self.patch_cables:
            total += len(p)
        total += len(self.default_params)
        total += count_attrs(self.osc1)
        total += count_attrs(self.osc2)
        total += len(self.top_level)
        return total
    
    def to_xml(self):
        root = ET.Element('sound', attrib=self.top_level)
        root.extend([self.osc1])
        root.extend([self.osc2])
        for n in self.nodes:
            ET.SubElement(root, n, attrib=self.nodes[n])
            
        default_params = ET.SubElement(root, "defaultParams", attrib=self.default_params)

        for n in self.default_param_nodes:
            ET.SubElement(default_params, n, attrib=self.default_param_nodes[n])


        patch_cables = ET.SubElement(default_params, "patchCables")
        for p in self.patch_cables:
            ET.SubElement(patch_cables, "patchCable", attrib=self.patch_cables[p])

        mod_knobs = ET.SubElement(root, "modKnobs")
        for n in self.mod_knobs:
            ET.SubElement(mod_knobs, "modKnob", attrib=n)
        return ET.ElementTree(root)


def check_file(f):  
    patch = Patch(f)
    a = patch.count_attrs()
    b = count_attrs_file(f)
    c = count_attrs(patch.to_xml())
    if (a != b != c):
        print("Bad file: ", f, a, b, c)


for f in xmlfiles: check_file(f)


for i in range(50):
    patch0 = Patch(file=random.choice(xmlfiles))
    patch1 = Patch(file=random.choice(xmlfiles)) 
    child = Patch(patch1=patch0, patch2=patch1)
    child.to_xml().write(child.filename)

    










    