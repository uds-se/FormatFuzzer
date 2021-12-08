import cfile as C
import sys
import yaml

datatypes = {"u4": "uint32", "u1": "ubyte", "u2": "uint16"}  # TODO implement all types


class Converter(object):
    def __init__(self, input_js):
        print(self.__class__.__name__)
        # self.input = {}
        self.subtrees = {}
        self.this_level_keys = []
        self.input = input_js
        try:
            self.this_level_keys = self.input.keys()
            print(self.this_level_keys)
        except:
            self.this_level_keys = None

    def parse_subtree(self):
        for this_level_key in self.this_level_keys:
            local_key = this_level_key
            if str(this_level_key) == "doc-ref": local_key = 'doc'
            self.__dict__[local_key] = self.input[this_level_key]
            self.subtrees[local_key] = globals()[local_key](self.input[this_level_key])
            self.subtrees[local_key].parse_subtree()

    def print_input(self):
        print("+++++++++++++")
        print(self.input)
        print("+++++++++++++")
        for this_level_key in self.this_level_keys:
            print("=============")
            print(this_level_key)
            print(self.subtrees[this_level_key].input)
            print("=============")

    def print_recursive_input(self):
        # TODO sense-full way of getting back json for checking
        for this_level_key in self.this_level_keys:
            print("=============")
            print(this_level_key)
            self.subtrees[this_level_key].print_recursive_input()
            print("=============")


class attribute():
    def __init__(self, input_js, name=None):
        self.input = input_js
        if name is None:
            self.id = self.input["id"]
        else:
            self.id = name

    def parse(self):
        print(self.input)


class meta(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        print(self.input)


class doc(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        self.output = "//     " + str(self.input).replace("\n", "\n//    ")
        print(self.output)


class enums(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        print(self.input)


class seq(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        for attribute_dict in self.input:
            # if this_level_key == "doc-ref":this_level_key="doc"
            self.subtrees[attribute_dict["id"]] = attribute(attribute_dict)
            self.subtrees[attribute_dict["id"]].parse()


class instances(seq):

    def __init__(self, input_js):
        seq.__init__(self, input_js)

    def parse_subtree(self):
        for this_level_key in self.this_level_keys:
            local_key = this_level_key
            if this_level_key == "doc-ref": local_key = "doc"

            self.subtrees[local_key] = attribute(self.input[local_key], local_key)
            self.subtrees[local_key].parse()


class types(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        print(self.input)

        for this_level_key in self.this_level_keys:
            local_key = this_level_key
            if str(this_level_key) == "doc-ref": local_key = 'doc'
            self.subtrees[local_key] = Converter(self.input[this_level_key])
            self.subtrees[local_key].parse_subtree()


def main():
    if len(sys.argv) != 3:
        print("USAGE = python3 Converter.py <input file path> <output file path>")  # TODO
        exit(1)
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    with open(input_file_name, "r") as in_file:
        input_file = in_file.read()
    kaitaijs = yaml.load(input_file)

    converter = Converter(kaitaijs)
    converter.parse_subtree()
    # converter.print_input()
    exit(0)

    types = kaitaijs["types"]
    enums = kaitaijs["enums"]
    print(kaitaijs)
    lines = []
    lines.extend(gen_enums(enums))
    lines.extend(gen_types(types))
    with open(output_file_name, "w") as out_file:
        out_file.write('\n'.join(lines))

    print('\n'.join(lines))


def gen_enums(enums):
    lines = []
    for enum_key in enums.keys():
        lines.extend(gen_single_enum(enum_key, enums[enum_key]))
        lines.append("\n")
    return lines


def gen_single_enum(key, values):
    lines = []
    # TODO FIND CORRECT TYPE? defaulting to <byte> for now
    size = "<byte>"
    lines.append("enum " + size + " {")
    keys = list(values.keys())
    for k in keys[0:-1]:
        lines.append("  " + (values[k] if "id" not in values[k] else values[k]["id"]) + " = " + str(k) + "," + (
            "" if "doc" not in values[k] else "  // " + (values[k]["doc"]).replace("\n", "\n     //")))
    lines.append("  " + (values[keys[-1]] if "id" not in values[keys[-1]] else values[keys[-1]]["id"]) + " = " + str(
        keys[-1]) + "" + ("" if "doc" not in values[keys[-1]] else "  // " + (values[keys[-1]]["doc"]).replace("\n",
                                                                                                               "\n     //")))
    lines.append("} " + str(key) + ";")
    return lines


def gen_types(types):
    lines = []
    # TODO implement dependency aware type generation
    for key in types.keys():
        lines.extend(gen_single_simple_type(key, types[key]))
        lines.append("\n")
    return lines


def gen_single_simple_type(key, values):
    # TODO only doing simple structs for now
    lines = []
    lines.append("struct " + str(key) + "{")
    keys = list(values.keys())
    # print(keys)
    for k in keys:
        if "doc" in k:
            lines.append("  // " + values[k].replace("\n", "\n     //"))
    for item in values["seq"]:
        # print(item)
        if "type" not in item.keys():
            if "size" not in item.keys():
                print("FAILURE AT FINDING TYPE\nKEYS = " + str(item.keys()))
                continue
            local_type = "size"
        else:
            local_type = "type"
        if type(item[local_type]) is str or type(item[local_type]) is int:
            lines.append("  " + gen_simple_var_creation(item[local_type], item["id"]) + (
                "" if "doc" not in item.keys() else "     //" + item["doc"]).replace("\n", "\n     //"))
        else:
            print("type not supported yet,skipping @ " + str(item[local_type].keys()))

    lines.append("};")
    return lines


def gen_simple_var_creation(typ, name, content=None):  # TODO Refactor name
    type = typ if typ not in datatypes.keys() else datatypes[typ]
    lines = ("  " + (str(type) if type == typ else str(type)) + " " + str(name))
    if content is None:
        pass
    else:
        print("COMPLEX VARS not YET supported!\n")  # TODO implement
    lines += ";"
    return lines


def gen_switch():
    lines = []
    return lines


if __name__ == "__main__":
    main()
