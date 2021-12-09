import cfile as C
import sys
import yaml

datatypes = {"u4": "uint32", "u1": "ubyte", "u2": "uint16"}  # TODO implement all types


class Converter(object):

    # TODO implement size lookup funtion

    def __init__(self, input_js, is_master=False):
        print(self.__class__.__name__)
        self.output = []
        self.subtrees = {}
        self.this_level_keys = []
        self.input = input_js
        try:
            self.this_level_keys = self.input.keys()
            print(self.this_level_keys)
        except:
            self.this_level_keys = None
        if is_master:
            self.global_init()
            self.parse_subtree()

    def parse_subtree(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.__dict__[local_key] = self.input[this_level_key]
                self.subtrees[local_key] = globals()[local_key](self.input[this_level_key])
                self.subtrees[local_key].parse_subtree()

    def generate_code_toplevel(self):
        self.output.extend(self.subtrees["enums"].generate_code())
        self.output.extend(self.subtrees["types"].generate_code())
        print("AAAAAAAAAAAAAAAAAAAAAAA")
        self.output.extend(self.subtrees["seq"].generate_code())
        print("AAAAAAAAAAAAAAAAAAAAAAA")

        return self.output

    def generate_code(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                try:
                    self.output.extend(self.subtrees[local_key].generate_code())
                except:
                    pass
        return self.output

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

    def global_init(self):
        self.resolve_enum_sizes()

    def resolve_enum_sizes(self):
        self.enum_size = {"standard": "<byte>"}

    def lookup_enum_size(self, enum):
        return self.enum_size[enum]


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

    def generate_code(self):
        return [self.output]


class enums(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])
                print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))

    def generate_code(self):
        self.output = []
        for enum in self.subtrees.keys():
            self.output.extend(self.gen_single_enum(enum, self.subtrees[enum], converter.lookup_enum_size("standard")))
            self.output.append("\n")
        return self.output

    def gen_single_enum(self, key, enumerations, size="<byte>"):
        values = enumerations.get_value()
        lines = []
        # TODO FIND CORRECT TYPE? defaulting to <byte> for now
        lines.append("enum " + size + " {")
        keys = list(values.keys())
        for k in keys[0:-1]:
            lines.append("  " + (values[k] if "id" not in values[k] else values[k]["id"]) + " = " + str(k) + "," + (
                "" if "doc" not in values[k] else "  // " + (values[k]["doc"]).replace("\n", "\n     //")))
        lines.append(
            "  " + (values[keys[-1]] if "id" not in values[keys[-1]] else values[keys[-1]]["id"]) + " = " + str(
                keys[-1]) + "" + (
                "" if "doc" not in values[keys[-1]] else "  // " + (values[keys[-1]]["doc"]).replace("\n",
                                                                                                     "\n     //")))
        lines.append("} " + str(key) + ";")
        return lines


class attribute():
    def __init__(self, name, value):
        self.value = value
        self.name = name

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name


class data_point():
    def __init__(self, input_js, name=None):
        self.subtrees = dict()
        self.input = input_js
        self.id = name

    def parse(self):
        for this_level_key in self.input.keys():
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])

            print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))
        if self.id is None:
            self.id = self.subtrees["id"].get_value()

    def generate_code(self):
        self.output = []
        print(self.subtrees.keys())
        if (len(self.subtrees.keys()) == 2) and ("type" in self.subtrees.keys()):
            self.output.append(self.gen_atomic_variable(self.id, self.subtrees["type"].get_value()))
            print(self.output)
        return self.output

    def gen_atomic_variable(self, name, type, size=None):
        output = ""
        print(name)
        if size is not None:
            print("AAA")
            pass
        if str(type) in datatypes.keys():
            return "    " + str(datatypes[type]) + " " + str(name) + ";"
        return "    " + str(type) + " " + str(name) + ";"


class seq(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        self.this_level_keys = []
        for data_dict in self.input:
            # if this_level_key == "doc-ref":this_level_key="doc"
            self.subtrees[data_dict["id"]] = data_point(data_dict)
            self.subtrees[data_dict["id"]].parse()
            self.this_level_keys.append(data_dict["id"])

    def generate_code(self):
        for this_level_key in self.this_level_keys:
            self.output.extend(self.subtrees[this_level_key].generate_code())
        return self.output


class instances(seq):

    def __init__(self, input_js):
        seq.__init__(self, input_js)

    def parse_subtree(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = data_point(self.input[local_key], local_key)
                self.subtrees[local_key].parse()

    def generate_code(self):
        # TODO understand what these are exactly supposed to do as the are not parsed
        pass


class types(Converter):
    def __init__(self, input_js):
        Converter.__init__(self, input_js)

    def parse_subtree(self):
        print(self.input)
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = Converter(self.input[this_level_key])
                self.subtrees[local_key].parse_subtree()

    def generate_code(self):
        self.output.extend(self.gen_forward_types())
        self.output.extend(self.gen_complete_types())
        return self.output

    def gen_complete_types(self):
        output = []
        for this_level_key in self.this_level_keys:
            output.extend(self.subtrees[this_level_key].generate_code())
        return output
        # TODO IMPLEMENT THIS IS JUST A PLACEHOLDER

    def gen_forward_types(self):
        output = []
        for this_level_key in self.this_level_keys:
            output.append("struct " + str(this_level_key) + ";")
        return output


def remap_keys(key):
    remap = {"doc-ref": "doc"}
    blocklist = ["-webide-representation"]
    if key in blocklist: return None
    if key in remap.keys(): return remap[key]
    return key


def main():
    global converter

    if len(sys.argv) != 3:
        print("USAGE = python3 Converter.py <input file path> <output file path>")  # TODO
        exit(1)
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    with open(input_file_name, "r") as in_file:
        input_file = in_file.read()
    kaitaijs = yaml.load(input_file)

    converter = Converter(kaitaijs, True)

    # output = converter.generate_code_toplevel()
    output = converter.generate_code()
    print('\n'.join(output))
    # converter.print_input()
    exit(0)

    with open(output_file_name, "w") as out_file:
        out_file.write('\n'.join(output))

    print('\n'.join(output))


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


if __name__ == "__main__":
    main()
