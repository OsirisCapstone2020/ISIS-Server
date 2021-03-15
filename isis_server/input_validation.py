# validate file inputs from n8n server (make another file for this)
    # look at function name given, pull parameters and types from json
    # compare file name (.cub, etc)
    # make sure strings, ints, are used (how do you do this when python doesn't have types?????)
    
import json
from copy import deepcopy

_DEFAULT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {"type": "string"},
        "args": {
            "type": "object",
            "properties": dict(),
            "required": list(),
            "additionalProperties": False
        },
    },
    "required": ["args", "from"],
    "additionalProperties": False
}


def get_json_schema(**kwargs):
    schema = deepcopy(_DEFAULT_JSON_SCHEMA)

    for k, v in kwargs.items():
        schema["properties"]["args"]["properties"][k] = v
        schema["properties"]["args"]["required"].append(k)

    return schema


def read_json(json_file):
    json_dictionary = json.loads(json_file)
    for parameter in json_file:
        check_type(parameter, json_dictionary[parameter])


def check_type(parameter, type):
    if type == "cube":
        parameter_elements = parameter.split(".")
        if parameter_elements[1] == ".cub" \
            or parameter_elements[1] == ".CUB" \
            or parameter_elements[1] == ".lbl" \
            or parameter_elements[1] == ".pvl" \
            or parameter_elements[1] == ".bds":
                return True
        else:
            return False
    
    elif type == "filename":
        parameter_elements = parameter.split(".")
        if parameter_elements[1] == ".txt" \
            or parameter_elements[1] == ".lis" \
            or parameter_elements[1] == ".lst" \
            or parameter_elements[1] == ".img" \
            or parameter_elements[1] == ".IMG" \
            or parameter_elements[1] == ".PNG" \
            or parameter_elements[1] == ".JPG" \
            or parameter_elements[1] == ".JPEG" \
            or parameter_elements[1] == ".BMP" \
            or parameter_elements[1] == ".TIF" \
            or parameter_elements[1] == ".TIFF" \
            or parameter_elements[1] == ".GIF" \
            or parameter_elements[1] == ".JP2" \
            or parameter_elements[1] == ".vic" \
            or parameter_elements[1] == ".map" \
            or parameter_elements[1] == ".cub" \
            or parameter_elements[1] == ".pvl" \
            or parameter_elements[1] == ".bsp" \
            or parameter_elements[1] == ".dat" \
            or parameter_elements[1] == ".db" \
            or parameter_elements[1] == ".tls" \
            or parameter_elements[1] == ".tpc" \
            or parameter_elements[1] == ".tsc" \
            or parameter_elements[1] == ".prt" \
            or parameter_elements[1] == ".bc" \
            or parameter_elements[1] == ".csv" \
            or parameter_elements[1] == ".tf" \
            or parameter_elements[1] == ".ddd" \
            or parameter_elements[1] == ".bds" \
            or parameter_elements[1] == ".def" \
            or parameter_elements[1] == ".net" \
            or parameter_elements[1] == ".fits" \
            or parameter_elements[1] == ".raw" \
            or parameter_elements[1] == ".gml" \
            or parameter_elements[1] == ".GML" \
            or parameter_elements[1] == ".conf" \
            or parameter_elements[1] == ".qub" \
            or parameter_elements[1] == ".lbl":
                return True
        else:
            return False
            
    # filename   .pvl.DIFF
    # current method will work with this, but this doesn't stop
    # files that have multiple .
    
    # overlap stats
        # filename   *
        # this will accept everything??????????
            
            
    # double
    # strings
    # cube
    # integer
    # boolean
    # image