from xml.etree import ElementTree


class XMLReader:
    @staticmethod
    def get_isis_command(xml_file: str) -> dict:
        xml_tree = ElementTree.parse(xml_file)
        command_name = xml_tree.getroot().get("name")
        param_groups = xml_tree.find("groups").findall("group")

        params = dict()
        for group in list(param_groups):
            group_params = XMLReader._param_group_to_dict(group)
            params.update(group_params)

        return {
            "name": command_name,
            "parameters": params
        }

    @staticmethod
    def _param_group_to_dict(param_group: ElementTree.Element) -> dict:
        current_group = {}
        for param in param_group.findall("parameter"):
            default = param.find("default")
            type = param.find("type").text

            if default is None:
                default = ""
            else:
                default = default.find("item").text
                if type.lower() == "boolean":
                    default = default == "TRUE"
                elif type.lower() == "integer":
                    default = int(default)
                elif type.lower() == "double":
                    default = float(default)

            current_group[param.get("name")] = {
                "type": type,
                "default": default
            }

        return current_group
