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


def find_parameters(file):
    parameters = {}

    file = open(xml_file, "r")
    lines = file.readlines()

    number_of_lines = len(lines)
    for i in range(0, number_of_lines):
        line = lines[i]
        if "parameter" in line:
            # find the parameter
            parameter_elements = line.split("=")
            parameter = elements[1].replace(">", "")
            
            # go to next line to find the type
            i++
            line = lines[i]
            type_elements = line.split(">")
            type = elements[1].replace("</type", "")
            
            # add parameter to dictionary
            parameters.add(parameter, type)
            
    file.close()
    print(parameters)
    return parameters