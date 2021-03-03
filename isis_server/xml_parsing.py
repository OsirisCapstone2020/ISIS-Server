# turn dictionary into json
    #  need to make json folder
    # make sure there isn't duplicate files/already existing files when this is run
    # make json per file
    # make json overall
# validate file inputs from n8n server (make another file for this)
    # look at function name given, pull parameters and types from json
    # compare file name (.cub, etc)
    # make sure strings, ints, are used (how do you do this when python doesn't have types?????)



# read line
# if parameter in line
	# split on =
	# remove >
		# replace(>,'')
	# get stuff from array based on position
	# next line
		# split on >
        # remove word for third element with type
            # so remove </type>
		
		
		
# to remove items, make a variable with all characters being removed, then put
# this as the first parameter of replace

import glob

def find_files():
    files = glob.glob('../xml/*.xml')
    print(files)
    
    for file in files:
        print(find_parameters(file))


def find_parameters(file):
    parameters = {}

    file = open(file, "r")
    lines = file.readlines()

    number_of_lines = len(lines)
    for i in range(0, number_of_lines):
        #elements = []
        line = lines[i]
        if "parameter name" in line:
            # find the parameter
            parameter_elements = line.split("=")
            print(parameter_elements)
            parameter_with_new_line = parameter_elements[1].replace(">", "")
            parameter = parameter_with_new_line.replace("\n", "")
            
            # go to next line to find the type
            i += 1
            line = lines[i]
            type_elements = line.split(">")
            print(type_elements)
            type = type_elements[1].replace("</type", "")
            
            # add parameter to dictionary
            parameters[parameter] = type
            
    file.close()
    print(parameters)
    print(len(parameters))
    return parameters
    
#find_files()
find_parameters("../xml/caminfo.xml")