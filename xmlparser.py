import re,os.path,xmltodict,json,argparse,xml.etree.ElementTree as ET,sys
from os import path

def xmltojson(file):                         
    """ function to parse and convert xml file to json
    with xml.etree module
    """
    
    try:
        text = open(file,'r')
        filetext = text.read()
        text.close()

        d1 = re.search(r"^\S+xml version=",filetext,flags=re.MULTILINE) ##checks if the first line of file starts with "xml version=" text

        if d1:
            with open(file,'r') as rfile:
                rdata = rfile.read().splitlines(True)
            with open('updated.xml','w') as wfile:
                wfile.writelines(rdata[1:])

            if path.isfile('updated.xml'):

                with open('updated.xml','r') as ufile:
                    udata = ufile.read().replace("\n","").replace("\t","")

                udict = xmltodict.parse(udata)    ##xmltodict module converts xmldata to dictionary
                jsondata = json.dumps(udict)
                return(jsondata)

        else:
            print("Incorrect XML file format.. please check the xml file version.")

    except Exception as error:
        print(error)
        
def iterparent(val,cnt):
    ""function to recursively call and get the child elements of parent/grand parent 
    elements
    """
    
    try:
        finaldict = {}
        finaldict[val.tag] = {}
        mainkey = val.tag
        if len(val.attrib):                    ## check if the element has attribute data
            for k,v in val.attrib.items():
                k = '@' + k
                finaldict[mainkey][k] = v

        for child in val:
            childdict = {}
            if len(child):
                cnt = cnt + 1
                iterparent(child,cnt)
            else:
                finaldict[mainkey][child.tag] = child.text
        jsondata = json.dumps(finaldict)
        return(jsondata)

    except Exception as error:
        print(error)        

def getelemval(file,elem):
    """function to parse xml file and get the required 
    element data and convert it into json
    """
    
    try:
        parser = ET.XMLParser(encoding="utf-8")  ##xml.etree.ElementTree(ET) module to parse the xml data
        tree = ET.parse(file,parser=parser)
        root = tree.getroot()                   ## Get the root element of the xml file
        elmlist = []
        dictdata = {}
        cnt = 0
        keyt = "#text"
        for val in root.iter():                 ## loop on each element of the xml file starting from the root
            elmlist.append(val.tag)
            if val.attrib:                       ## if the element has attribute
                dict = val.attrib
                for k in dict.keys():
                    if not dict[k]:              ## skip the loop if the element value is null	
                        continue
						
                    if dict[k].upper() == elem.upper():    ## check if the search value is matching with the attribute value
                        if len(val):                       ## if the element has sub elements/children call iterparent() function
                            cnt = 1
                            jsondata = iterparent(val,cnt)  
                            return(jsondata)
                        else:
                            childattrib = val.attrib        ##if element has no children then get the element details
                            dictdata[val.tag] = {}
                            for k,v in childattrib.items():
                                k = '@' + k
                                dictdata[val.tag][k] = v
                            dictdata[val.tag][keyt] = val.text
                            jsondata = json.dumps(dictdata)
                            return(jsondata)
            if not val.text:    
                continue
				
            if val.text.upper() == elem.upper():            ## if the search value is matching with element value
                cnt = cnt + 1
                elemdict = {}
                keyt = "#text"
                parntag = val.tag
                prt = root.findall('.//{value}/..'.format(value=parntag))  ## get the parent of the element
                for i in prt:                                            ## get the siblings of the element
                    elm = i.find('./{value}'.format(value=val.tag))       
                    if elm.text.upper() == elem.upper():
                        parnattrib = i.attrib
                        parntag = i.tag
                elemdict[parntag] = {}
                if parnattrib:                                  ## get the attribute details if the parent of the element has
                    for k,v in parnattrib.items():
                        k = '@' + k
                        elemdict[parntag][k] = v
                elemdict[parntag][val.tag] = {}

                if len(val.attrib):                         ## if the element has attribute data get it 
                    dict = val.attrib
                    for k,v in dict.items():
                        k = '@' + k
                        elemdict[parntag][val.tag][k] = v

                elemdict[parntag][val.tag][keyt] = val.text
                jsondata = json.dumps(elemdict)
                return(jsondata)

        if cnt == 0:                                         
            print("The requested value not available in xml file")

    except Exception as error:
        print(error)             


def main():
    """ Gets the arguments from the command line and 
    save it to file and elem variables
    """
    
    parser = argparse.ArgumentParser()                 
    parser.add_argument("-f", dest="file", required=True)    
    parser.add_argument("-e", dest="elem", nargs='?',default="test")  ## if the search value is not provided set the elem variable to "test"
    args = parser.parse_args() 

    text = open(args.file,'r')
    filetext = text.read()
    text.close()

    d1 = re.search(r"^\S+xml version=",filetext,flags=re.MULTILINE)  ##check if xml file first line is xml version
    
    if d1:
    
        if args.elem == "test":
            jsondata = xmltojson(args.file)                     ##function call xmltojson()
            print(jsondata)
        else:
            searchelem = getelemval(args.file,args.elem)        ##function call getelemval() to get element value in json
            print(searchelem)

    else:
        print("Incorrect XML file format.. please check the xml file version.")
	
if __name__ == "__main__":
    main()

