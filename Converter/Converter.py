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
        self.output.extend(self.subtrees["seq"].generate_code())


        return self.output

    def generate_code(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                try:
                    self.output.extend(self.subtrees[local_key].generate_code())
                except Exception as err:
                    print("++++++START Converter codeGEN exception START +++++")
                    print(err)
                    print(self.subtrees[local_key].input)
                    print(self.this_level_keys)
                    print("++++++END Converter codeGEN exception END +++++")
                    pass
        return self.output


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
        self.output = "     //     " + str(self.input).replace("\n", "\n//    ")

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
                # print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))

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
                "" if "doc" not in values[k] else "     // " + (values[k]["doc"]).strip().replace("\n", "\n     //")))
        lines.append(
            "  " + (values[keys[-1]] if "id" not in values[keys[-1]] else values[keys[-1]]["id"]) + " = " + str(
                keys[-1]) + "" + (
                "" if "doc" not in values[keys[-1]] else "      // " + (values[keys[-1]]["doc"]).strip().replace("\n",
                                                                                                                 "\n     //")))
        lines.append("} " + str(key) + ";")
        return lines


class attribute():
    # A data_point is composed of mutiple attributes/they are the atomic informations
    # TODO CHECK IF CLASS IS ACTUALLY NEEDED
    def __init__(self, name, value):
        self.value = value
        self.name = name

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name


class data_point():
    #Things that start with getting an id assigned/elements of seq
    def __init__(self, input_js, name=None):
        self.subtrees = dict()
        self.input = input_js
        self.id = name
        self.this_level_keys = self.input.keys()
        self.type = None
        self.size = None

    def parse(self):
        if "type" in self.input.keys(): self.type = self.input["type"]
        if "size" in self.input.keys(): self.size = self.input["size"]
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])

            # print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))
        if self.id is None:
            self.id = self.subtrees["id"].get_value()

    def generate_code(self):
        # TODO EXTEND TO ALL VARIATIONS
        self.output = []
        self.front = []
        self.back = []

        if "process" in self.this_level_keys:
            self.gen_atomic(docu="IMPLEMENT" + str(self.input["process"]))
            print("PROCESS NOT IMPLEMENTED YET\n")
            # TODO IMPLEMENT
            self.output.extend(self.front)
            self.output.extend(self.back)
            return self.output
        elif "if" in self.this_level_keys:
            self.gen_if()
        elif "repeat" in self.this_level_keys:
            self.gen_repeat()

        if "encoding" in self.this_level_keys:
            self.gen_str()
        elif "contents" in self.this_level_keys:
            self.gen_contents()
        elif type(self.type) is dict:
            self.gen_switch()
        else:
            self.gen_atomic()

        self.output.extend(self.front)
        self.output.extend(self.back)
        return self.output

    def gen_switch(self):
        # TODO implement
        pass

    def gen_if(self):
        # TODO implement
        pass

    def gen_repeat(self):
        # TODO implement
        pass

    def gen_str(self):
        self.gen_atomic()
        # TODO THIS METHOD ONLY EXISTS IN CASE ENCODING NEEDS SPECIAL TREATMENT

    def gen_contents(self):
        # TODO implement
        pass

    def gen_atomic(self, docu=""):
        if docu != "":
            loc_doc = "     //" + str(docu)
        else:
            loc_doc = ""
        if self.type == "str" and self.size is not None:
            # TODO IMPLEMENT CASE FOR DIFFERENT THAN ZEROBYTE TERMINATOR
            self.front.append("    char " + str(self.id) + "[" + str(self.size) + "]" + ";" + loc_doc)
        elif self.type == "strz":
            self.front.append("    string " + str(self.id) + ";" + loc_doc)
        elif self.type is not None:
            if self.type in datatypes.keys():
                self.front.append("    " + str(datatypes[self.type]) + " " + str(self.id) + ";" + loc_doc)
            else:
                self.front.append("    " + str(self.type) + " " + str(self.id) + ";" + loc_doc)
        elif self.size is not None:
            self.front.append("    byte " + str(self.id) + "[" + str(self.size) + "]" + ";" + loc_doc)
        else:
            print("ERROR NO SIZE OR TYPE GIVEN AND ITS NO MAGIC\n")
            self.front.append("//STUFF MISSING HERE @ NO MAGIC " + str(self.id) + " " + str(self.input))

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
        #print("SEQ"+str(self.output)+str(self.input))
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

    # output = converter.generate_code()
    output = converter.generate_code_toplevel()
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
