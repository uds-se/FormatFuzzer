import inspect
import sys
import yaml
import re
import traceback

DEBUG = True


class Converter(object):

    # TODO implement size lookup funtion

    def __init__(self, input_js, is_master=False, parent=None, root=None, name=None):
        self.output_enums = []
        self.output_types = []
        self.output_seqs = []
        self.output = []
        self.subtrees = {}
        self.this_level_keys = []
        self.input = input_js
        self.name = name

        try:
            self.this_level_keys = self.input.keys()
        except:
            self.this_level_keys = None
        if is_master:
            self.root = self
            self.global_instance_table = {}
            self.global_type_table = {}
            self.global_enum_table = {}
            self.global_init()
            self.parse_subtree()
            self.endian = ""
        else:
            self.parent = parent
            self.root = root

    # TODO MAYBE ADD MORE TABLES HERE FOR MORE DYNAMIC CODE GENERATION
    def register_instance(self, name, value,
                          containing_type):  # registers instance in "global" table during parsing time
        try:
            self.root.global_instance_table[str(containing_type)][str(name)] = {"VALUE": value, "IMPLEMENTED": False}
        except:
            self.root.global_instance_table[str(containing_type)] = {str(name): {"VALUE": value, "IMPLEMENTED": False}}
        return

    def register_type(self, name, value=None,
                      param_needed=False):  # registers type in "global" table during parsing time
        if not param_needed:
            self.root.global_type_table[str(name)] = {"VALUE": value, "IMPLEMENTED": False, "PARAM": param_needed}
        else:
            self.root.global_type_table[str(name)]["PARAM"] = True

    def register_enum(self, name, value):  # registers enum in "global" table during parsing time
        self.root.global_enum_table[str(name)] = {"VALUE": value, "IMPLEMENTED": False}

    def lookup_instance(self, name, containing_type,
                        check_if_implemented=False):  # returns dict of value and possible doc/doc-ref as keys
        if check_if_implemented:
            getter = "IMPLEMENTED"
        else:
            getter = "VALUE"
        try:
            return self.root.global_instance_table[str(containing_type)][str(name)][getter]
        except:
            # print_debug("\nERROR INSTANCE " + str(name) + " NOT FOUND\nCan safely be ignored just for testing if expr_resolve works!\n")
            return None

    def lookup_type(self, name, check_if_implemented=False,
                    check_if_param_needed=False):  # returns dict of value and possible doc/doc-ref as keys
        if check_if_implemented:
            getter = "IMPLEMENTED"
        elif check_if_param_needed:
            getter = "PARAM"
        else:
            getter = "VALUE"
        try:
            return self.root.global_type_table[str(name)][getter]
        except:
            # traceback.print_exc()
            print_debug("ERROR TYPE " + str(name) + " NOT FOUND\n")
            return None

    def lookup_enum(self, name, check_if_implemented=False):  # returns dict of value and possible doc/doc-ref as keys
        if check_if_implemented:
            getter = "IMPLEMENTED"
        else:
            getter = "VALUE"
        try:
            return self.root.global_enum_table[str(name)][getter]
        except:
            print_debug("ERROR ENUM " + str(name) + " NOT FOUND\n")
            return None

    def mark_as_implemented(self, type, name, containing_type=None, value=True):

        if type == "type":
            getter = self.root.global_type_table
        elif type == "enum":
            getter = self.root.global_enum_table
        elif type == "instance":

            getter = self.root.global_instance_table[containing_type]
        else:
            print_debug(str(type) + " TABLE NOT IMPLEMENTED\n")
            exit(0)
        getter[str(name)]["IMPLEMENTED"] = value

    def parse_subtree(self, name=None):
        self.name = name

        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                # print_debug(local_key)
                # print_debug(name)
                self.__dict__[local_key] = self.input[this_level_key]
                self.subtrees[local_key] = globals()[local_key](self.input[this_level_key], self, self.root, name=name)
                self.subtrees[local_key].parse_subtree(name=name)

    def generate_code_toplevel(self):
        if "enums" in self.subtrees.keys():
            self.output_enums.extend(self.subtrees["enums"].generate_code(called_lowlevel=False))
        self.output_types.extend(self.subtrees["types"].generate_code(called_lowlevel=False))
        self.output_seqs.extend(self.subtrees["seq"].generate_code(called_lowlevel=False))
        self.output.extend(self.output_enums)
        self.output.extend(self.output_types)
        self.output.extend(self.output_seqs)

        return self.output

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):

        if "instances" in self.this_level_keys:
            for x in self.input["instances"].keys():
                self.mark_as_implemented("instance", x, value=False, containing_type=self.name)
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                if True:  # SWITCH BETWEEN SUPPRESSION OF "UNIMPLEMENTED" ERRORS
                    try:
                        # if local_key =="seq":print("AAAAAAAAAAAAA")
                        # if local_key =="instances":print("BBBBBBBBBBBBB")

                        self.output.extend(self.subtrees[local_key].generate_code(size, called_lowlevel))
                    except Exception as err:
                        print("\n++++++START Converter codeGEN exception START +++++")
                        traceback.print_exc()
                        print(self.subtrees.keys())
                        print(self.subtrees[local_key].input)
                        print(self.this_level_keys)
                        print("++++++END Converter codeGEN exception END +++++\n")
                        pass
                else:
                    self.output.extend(self.subtrees[local_key].generate_code(size, called_lowlevel))

        return self.output

    def global_init(self):
        self.resolve_enum_sizes()

    def resolve_enum_sizes(self):
        self.enum_size = {"standard": "<ubyte>"}

    def lookup_enum_size(self, enum):
        return self.enum_size[enum]

    def lookup_enum_val_2_key(self, enum, key):

        inv_map = {v: k for k, v in self.enums[enum].items()}
        return inv_map[key]

    def expr_resolve(self, expr, translate_condition_2_c=False, repeat_condition=False, id_of_obj=None):
        # takes a string and depending on the flags returns a list of
        # either elements that could be an instance or
        # a string that works as condition in c
        # TODO add CALL to this when implementig
        operator_replacement_dict = {"not ": " ! ", " and ": " && ", " or ": " || "}
        # condition_splitter_replacement = ["::", "."] #TODO CHECK IF REMOVAL OF "." IS CORRECT (needed for floats to prevent removal of the dot)
        condition_splitter_replacement = ["::"]
        string_splitter_replacement = ['"']
        for to_be_rep in operator_replacement_dict.keys():
            expr = expr.replace(to_be_rep, operator_replacement_dict[to_be_rep])
        # print_debug(expr)
        # print_debug(re.findall('[^a-zA-Z0-9_]+', expr))
        # print_debug(re.findall('(\W+)', expr))
        # print_debug(re.split('(\W+)', expr))
        # print_debug(re.split('[^a-zA-Z0-9_.]+', expr))
        # FLOAT REGEX "[-+]?\d*\.\d+|\d+"        '[^a-zA-Z0-9_.]+'
        # for element in re.split('(\W+)', expr):  # replacing f**kin 0xffff_ffff with 0xffffffff
        for element in re.split('[^a-zA-Z0-9_.]+', expr):  # replacing f**kin 0xffff_ffff with 0xffffffff
            try:
                try:
                    temp = str(int(element))
                    expr = expr.replace(element, temp)
                    continue
                except:
                    temp = str(float(element))
                    expr = expr.replace(element, temp)
                    continue
            except:
                # print_debug("Failed to IntConvert : >"+str(element)+"< in "+str(expr))
                # traceback.print_exc()
                pass
            try:
                temp = hex(int(element, 2))
                expr = expr.replace(element, temp)
            except:
                # print_debug("Failed to HexConvert : >"+str(element)+"< in "+str(expr))
                # traceback.print_exc()
                pass

        if translate_condition_2_c:
            if repeat_condition:
                try:
                    expr = expr.replace("_.", "" + str(id_of_obj) + ".")
                except:
                    pass
                try:
                    expr = expr.replace("_io.eof", "FTell()==FileSize()")
                except:
                    pass

            pass
            if "::" in expr:
                for element in expr.split(" "):
                    if "::" in element:
                        expr = expr.replace(str(element), element.split("::")[1])

            return expr
        elif False:
            pass
        else:  # no flag set
            print_debug(expr)
            for splitter in condition_splitter_replacement:
                expr = expr.replace(str(splitter), " ")
            print_debug(expr)
            # for splitter in string_splitter_replacement:  # TODO UNSURE ABOUT THIS
            #     expr = expr.replace(str(splitter), "")

            if " " in expr:
                return expr.split(" ")
            else:
                return expr

    def chck_flg(self, flag, flag_to_val=False):
        try:
            if flag in self.this_level_keys:
                return True
            else:
                for this_level_key in self.this_level_keys:
                    local_key = remap_keys(this_level_key)
                    if local_key is not None:
                        if self.subtrees[local_key].chck_flg(flag, flag_to_val):
                            return self.subtrees[local_key].chck_flg(flag, flag_to_val)
                        else:
                            pass
                if flag_to_val:
                    return None
                else:
                    return False
        except:
            return False

    def lookup_f_in_typ_pres(self, type, flag, id=None, flag_to_val=False):
        # print_debug(type)
        # print_debug(flag)
        # print_debug(str(id))

        if id is None:
            temp = self.subtrees["types"].subtrees[type].chck_flg(flag, flag_to_val)
            # print_debug(str(temp)+"\n")
            return temp
        temp = self.subtrees["types"].subtrees[type].subtrees[id].chck_flg(flag, flag_to_val)
        # print_debug(str(temp)+"\n")
        return temp

    def resolve_datatype(self, kaitype, getsize=False, getendian=False):
        # TODO do something about LE????
        match = re.match(r'(?P<parsed_type>[a-zA-Z])(?P<parsed_size>[0-9])(?P<parsed_endian>[a-zA-Z]*)', kaitype)
        if match is None:
            return None
        parsed_type = match.group('parsed_type')
        parsed_size = match.group('parsed_size')
        parsed_endian = match.group('parsed_endian')
        if getsize:
            return parsed_size
        if getendian:
            return parsed_endian

        type_table = {"u": "uint", "s": "int", "b": "byte", "f": "float"}
        endian_table = {"le": "/*LITTLE ENDIAN*/", "be": "/*BIG ENDIAN*/",
                        "": ""}  # TODO No Clue how to handle right Now
        to_be_size = int(parsed_size) * 8
        if parsed_endian == self.root.endian:
            to_be_endian = ""
        else:
            to_be_endian = endian_table[parsed_endian]
        if int(parsed_size) == 1 and type_table[parsed_type] != "float":
            result = "ubyte"
        elif int(parsed_size) == 8 and type_table[parsed_type] == "float":
            result = to_be_endian + "double"
        elif type_table[parsed_type] == "float":
            result = to_be_endian + "float"
        elif type_table[parsed_type] == "byte":
            result = to_be_endian + "byte"
        else:
            result = to_be_endian + type_table[parsed_type] + str(to_be_size)
        return result


class meta(Converter):
    def __init__(self, input_js, parent, root: Converter, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)

    def parse_subtree(self, name=None):
        self.root.endian = self.input["endian"]

        pass


class doc(Converter):
    def __init__(self, input_js, parent, root: Converter, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)

    def parse_subtree(self, name=None):
        self.output = "    //     " + str(self.input).replace("\n", "\n    //    ")

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        return [self.output]


class doc_ref(Converter):
    def __init__(self, input_js, parent, root: Converter, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)

    def parse_subtree(self, name=None):
        self.output = "    //     " + str(self.input).replace("\n", "\n    //    ")

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        return [self.output]


class enums(Converter):
    def __init__(self, input_js, parent, root: Converter, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)

    def parse_subtree(self, name=None):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.root.register_enum(local_key, self.input[local_key])
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])
                # print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        self.output = []
        for enum in self.subtrees.keys():
            self.output.extend(
                self.gen_single_enum(enum, self.subtrees[enum], type=converter.lookup_enum_size("standard")))
            self.output.append("\n")

        if called_lowlevel:
            self.root.output_enums.extend(self.output)
            return [""]
        return self.output

    def gen_single_enum(self, key, enumerations, type="<ubyte>"):
        values = enumerations.get_value()
        lines = []
        # TODO FIND CORRECT TYPE? defaulting to <byte> for now
        lines.append("enum " + type + " " + str(key) + "_ENUM{")
        keys = list(values.keys())
        for k in keys[0:-1]:
            lines.append(
                "  " + (values[k] if "id" not in values[k] else values[k]["id"]) + " = " + str(hex(k)) + "," + (
                    "" if "doc" not in values[k] else "     // " + (values[k]["doc"]).strip().replace("\n",
                                                                                                      "\n     //")))
        lines.append(
            "  " + (values[keys[-1]] if "id" not in values[keys[-1]] else values[keys[-1]]["id"]) + " = " + str(hex(
                keys[-1])) + "" + (
                "" if "doc" not in values[keys[-1]] else "      // " + (values[keys[-1]]["doc"]).strip().replace("\n",
                                                                                                                 "\n     //")))
        lines.append("};")
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
    # Things that start with getting an id assigned/elements of seq
    def __init__(self, input_js, name=None, parent=None, root: Converter = None, size_eos=False, containing_type=None):
        self.subtrees = dict()
        self.input = input_js
        self.id = name
        self.this_level_keys = self.input.keys()
        self.type = None
        self.size = None
        self.parent = parent
        self.root = root
        self.size_eos = size_eos
        self.output = []
        self.front = []
        self.back = []
        self.containing_type = containing_type

    def parse(self):
        if "type" in self.input.keys(): self.type = self.input["type"]
        if "size" in self.input.keys(): self.size = self.input["size"]
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])

            # print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))
        if self.id is None:
            self.id = str(self.subtrees["id"].get_value())

    def generate_code(self, size=None, ignore_if=False, called_lowlevel=True, containing_type=None):
        # TODO EXTEND TO ALL VARIATIONS
        if size:
            print_debug(size)
        pass
        if "process" in self.this_level_keys:
            self.gen_atomic(docu="IMPLEMENT" + str(self.input["process"]), size=size)
            print("PROCESS NOT IMPLEMENTED YET\n")
            # TODO IMPLEMENT
            self.output.extend(self.front)
            self.output.extend(self.back)
            return self.output
        elif "if" in self.this_level_keys and not ignore_if:
            self.gen_if(self.containing_type)
        elif "repeat" in self.this_level_keys:
            self.gen_repeat()
        elif "encoding" in self.this_level_keys:
            self.gen_str()
        elif "contents" in self.this_level_keys:
            self.gen_contents()

        elif type(self.type) is dict:
            self.gen_switch(self.size)
        else:
            if "enum" in self.input.keys():
                self.gen_atomic(type_override=self.input["enum"])
            else:
                self.gen_atomic()

        if not ignore_if:
            self.output.extend(self.front)
        self.output.extend(self.back)
        return self.output

    def gen_switch(self, size=None):
        switch = self.type["switch-on"]
        cases = self.type["cases"]

        switch_drop = ["_root", "_parent", "_io"]
        if switch.split(".")[0] in switch_drop:
            switch_term = ".".join(switch.split(".")[1:])
        else:
            switch_term = switch
        self.front.append("     switch(" + str(switch_term) + ") {")
        for case_key in cases.keys():
            case = self.root.expr_resolve(case_key)
            if case == ["_"] or case == "_":
                case_val = "default"  # TODO remove case from case default
            elif type(case) is list:

                case_val = case[1]
                # case_val = str(hex(self.root.lookup_enum_val_2_key(case[0], case[1])))

            else:
                case_val = case
            sizeos = self.root.lookup_f_in_typ_pres(cases[case_key], "size-eos")
            repeat = self.root.lookup_f_in_typ_pres(cases[case_key], "repeat")
            encoding = self.root.lookup_f_in_typ_pres(cases[case_key], "encoding")
            if (sizeos or repeat) and not encoding:
                if self.root.lookup_f_in_typ_pres(cases[case_key], "repeat", flag_to_val=True) == "eos":
                    paramfield = "(lenght_CONVERTER)"
                else:
                    paramfield = ""
            else:
                paramfield = ""
            if case_val != "default":
                self.front.append("         case " + str(case_val) + ":")
            else:
                self.front.append("         default:")
            self.front.append("             " + str(cases[case_key]) + "_TYPE " + str(self.id) + paramfield + ";")
            self.front.append("             break;")
        self.front.append("    }")

    def gen_if(self, containing_type=None):
        condition = self.input["if"]
        if "instances" in self.parent.parent.input.keys():
            pass

        self.gen_instances(condition)

        self.front.append("    if (" + self.root.expr_resolve(condition, translate_condition_2_c=True) + ") {")

        self.generate_code(ignore_if=True, containing_type=containing_type)

        self.front.append("     }")

        # TODO implement

    def gen_repeat(self, size=None):
        if "repeat-until" in self.this_level_keys:
            condition_in = self.input["repeat-until"]
            condition = self.root.expr_resolve(condition_in, translate_condition_2_c=True, repeat_condition=True,
                                               id_of_obj=self.id)
            # print_debug(condition)
            self.gen_instances(condition)
            self.gen_atomic()
            self.front.append("    while (!(" + condition + ")) {")
            self.gen_atomic(indents=2)
            self.front.append("    }")
            # TODO CHECK IF DONE

        elif "repeat-expr" in self.this_level_keys:
            expr_in = self.input["repeat-expr"]
            expr = self.root.expr_resolve(expr_in, translate_condition_2_c=True)
            self.gen_instances(expr)
            self.gen_atomic(size=expr)
            pass
        elif "eos" == self.input["repeat"]:

            self.front.append("//     repeat: eos PLACEHOLDER<=======")
            # TODO INSERT NEXT WHILE CONSTRUCTION
            pass
        else:
            print_debug("REPEAT MISSING" + str(self.input["repeat"]))
        # TODO implement
        pass

    def gen_atomic(self, docu="", size=None, type_override=None, indents=1):

        # elif "size" in self.this_level_keys and self.root.lookup_type(name=self.type, check_if_param_needed=True):
        #     print_debug(self.type)
        #     print_debug(self.id)
        prepend = "    " * indents
        if type_override:
            self.type = type_override + "_ENUM"
        if docu != "":
            loc_doc = "     //" + str(docu)
        else:
            loc_doc = ""

        if self.size_eos:
            print_debug("size-EOS found here")
            pass
        if self.type == "str":
            if self.size is not None:
                # TODO IMPLEMENT CASE FOR DIFFERENT THAN ZEROBYTE TERMINATOR
                self.front.append(prepend + "char " + str(self.id) + "[" + str(self.size) + "]" + ";" + loc_doc)
            elif "size-eos" in self.input:
                self.front.append(prepend + "string " + str(self.id) + ";" + loc_doc)
        elif self.type == "strz":
            self.front.append(prepend + "string " + str(self.id) + ";" + loc_doc)
        elif self.type is not None:

            temp_type = self.root.resolve_datatype(self.type)

            if (temp_type is not None):  # BASIC TYPES
                if temp_type != "byte":
                    # print_debug(self.type)
                    # print_debug(temp_type)
                    self.front.append(
                        prepend + str(self.root.resolve_datatype(self.type)) + " " + str(self.id) + ";" + loc_doc)
                else:
                    self.front.append(
                        prepend + str(self.root.resolve_datatype(self.type)) + " " + str(self.id) + "[" + str(
                            self.root.resolve_datatype(self.type, getsize=True)) + "]" + ";" + loc_doc)

            elif " " in str(self.type):
                self.type = self.root.expr_resolve(self.type, translate_condition_2_c=True)
                self.front.append(prepend + str(self.type) + " " + str(self.id) + ";" + loc_doc)


            else:  # CUSTOM TYPES

                if type_override is None and "_TYPE" not in self.type:
                    self.type = self.type + "_TYPE"
                length_addon = ""
                if "_ENUM" not in self.type and self.root.lookup_type(name=self.type.split("_TYPE")[0],
                                                                      check_if_param_needed=True):
                    # print_debug(self.input["size"])
                    length_addon = "(" + self.root.expr_resolve(self.input["size"], translate_condition_2_c=True) + ")"
                if size:
                    length_addon = "[" + size + "]"
                self.front.append(prepend + str(self.type) + " " + str(self.id) + length_addon + ";" + loc_doc)
        elif self.size is not None:  # JUST BYTES
            self.front.append(prepend + "byte " + str(self.id) + "[" + str(self.size) + "]" + ";" + loc_doc)
        else:

            # self.gen_repeat()
            print_debug("ERROR NO SIZE OR TYPE GIVEN AND ITS NO MAGIC\n")
            print_debug(self.input)
            self.front.append("//STUFF MISSING HERE @ NO MAGIC " + str(self.id) + "----" + str(self.input))

    def gen_instances(self, condition):
        # condition_list = condition.split(".")
        condition_list = self.root.expr_resolve(condition)
        if type(condition_list) is not type([]):
            condition_list = [condition_list]
        for element in condition_list:
            instance = self.root.lookup_instance(element, self.containing_type)
            if instance is not None and not self.root.lookup_instance(element, self.id, check_if_implemented=True):
                self.root.mark_as_implemented("instance", element, value=True, containing_type=self.containing_type)
                temp = " ".join(self.root.expr_resolve(str(instance["value"])))
                self.front.append("    local int64 " + str(element) + " = " + str(temp) + ";" + (
                    ("   //" + str(instance["doc"])) if "doc" in instance.keys() else ""))

    def gen_str(self):
        self.gen_atomic()
        # TODO THIS METHOD ONLY EXISTS IN CASE ENCODING NEEDS SPECIAL TREATMENT

    def gen_contents(self):
        self.contents = self.input["contents"]
        self.magic = self.to_hex_list(self.contents)
        self.magic_len = len(self.magic)
        self.front.append("    byte " + str(self.id) + "[" + str(self.magic_len) + "];")
        # TODO HERE POSSIBLE SET_EVIL_BIT
        self.front.append("    if (" + self.id + "[0] != " + self.magic[0] + " ||")
        for x in range(1, self.magic_len - 1):
            self.front.append("        " + self.id + "[" + str(x) + "] != " + self.magic[x] + " ||")
        self.front.append(
            "        " + self.id + "[" + str(self.magic_len - 1) + "] != " + self.magic[self.magic_len - 1] + ") {")
        self.front.append('         Warning("Magic Bytes of ' + self.id + ' not matching!");')
        self.front.append("         return -1;\n    };")

    def to_hex_list(self, input):
        if type(input) is list:
            is_str = False
            for x in input:
                if type(x) is str:
                    is_str = True
            if not is_str:
                return [hex(no) for no in input]
            else:
                out = []
                for x in input:
                    line = self.to_hex_list(x)
                    if type(line) is list:
                        out.extend(line)
                    else:
                        out.append(line)
                return out
        elif type(input) is str:
            return list(map(lambda c: hex(ord(c)), input))
        elif type(input) is int:
            return hex(input)
        else:
            print_debug("to_hex_list FAILURE\n")
            exit(-1)

    def chck_flg(self, flag, flag_to_val=False):
        if flag_to_val:
            if flag in self.this_level_keys:
                return self.input[flag]
            else:
                return None
        return flag in self.this_level_keys


class seq(Converter):
    def __init__(self, input_js, parent, root, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)

    def parse_subtree(self, name=None):
        self.this_level_keys = []
        for data_dict in self.input:
            # if this_level_key == "doc-ref":this_level_key="doc"
            self.subtrees[data_dict["id"]] = data_point(data_dict, containing_type=name, parent=self, root=self.root)
            self.subtrees[data_dict["id"]].parse()
            self.this_level_keys.append(data_dict["id"])

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        for this_level_key in self.this_level_keys:
            self.output.extend(
                self.subtrees[this_level_key].generate_code(size, called_lowlevel=True, containing_type=self.name))
        # print("SEQ"+"\n".join(self.output)+str(self.input))
        return self.output


class instances(seq):

    def __init__(self, input_js, parent, root, name=None):
        seq.__init__(self, input_js, parent=parent, root=root, name=name)
        self.output = []
        self.front = []
        self.back = []

    def parse_subtree(self, name=None):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.root.register_instance(local_key, self.input[local_key], containing_type=name)
                self.subtrees[local_key] = data_point(self.input[local_key], name=local_key, parent=self,
                                                      root=self.root)
                self.subtrees[local_key].parse()

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        for this_level_key in self.this_level_keys:
            instance = self.root.lookup_instance(this_level_key, containing_type=self.name)
            if instance is not None and not self.root.lookup_instance(this_level_key, containing_type=self.name,
                                                                      check_if_implemented=True):
                temp = " ".join(self.root.expr_resolve(str(instance["value"])))
                self.front.append("    local double " + str(this_level_key) + " = " + str(temp) + ";" + (
                    ("   //" + str(instance["doc"])) if "doc" in instance.keys() else ""))
        self.output.extend(self.front)
        self.output.extend(self.back)
        return self.output
        # TODO IMPLEMENT instances as local vars just before they are used
        # TODO If they are not yet implemented
        pass


class types(Converter):
    def __init__(self, input_js, parent, root, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)

    def parse_subtree(self, name=None):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.root.register_type(local_key, self.input[local_key])
                self.subtrees[local_key] = Converter(self.input[this_level_key], parent=self, root=self.root)
                self.subtrees[local_key].parse_subtree(name=local_key)

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        self.output.extend(self.gen_forward_types())
        self.output.extend(self.gen_complete_types(size))
        return self.output

    def gen_complete_types(self, size=None):
        output = []
        if size is not None:
            lenfield = "(int32 lenght)"
        else:
            lenfield = ""
        for this_level_key in self.this_level_keys:
            lenfield = ""
            item = self.subtrees[this_level_key]
            if item.chck_flg("size-eos") and not item.chck_flg("encoding"):
                lenfield = "(int32 lenght_CONVERTER)"
            if item.chck_flg("repeat", flag_to_val=True) == "eos":
                lenfield = "(int32 lenght_CONVERTER)"
            if lenfield != "":
                self.root.register_type(name=this_level_key, param_needed=True)
            output.append("struct " + str(this_level_key) + "_TYPE" + lenfield + " {")
            # TODO IMPLEMENT size Calc locals
            output.extend(item.generate_code(size, called_lowlevel=True))  # GOING TO CHILD ITEM
            output.append("};\n")
        return output
        # TODO IMPLEMENT THIS IS JUST A PLACEHOLDER

    def gen_forward_types(self):
        output = []
        for this_level_key in self.this_level_keys:
            output.append("struct " + str(this_level_key) + "_TYPE ;")
        return output


def print_debug(string):
    if DEBUG:
        print("\nDEBUG: " + str(string).replace("\n", "\n     "))


def remap_keys(key):
    remap = {"doc-ref": "doc_ref"}
    blocklist = ["-webide-representation", "-orig-id", "params"]
    # TODO EXTEND TO SUPPORT MORE THINGS ESPECIALLY PARAMS
    if key in blocklist: return None
    if key in remap.keys(): return remap[key]
    return key


def main():
    global converter, DEBUG

    if len(sys.argv) != 3:
        print("USAGE = python3 Converter.py <input file path> <output file path>")  # TODO
        exit(1)
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    with open(input_file_name, "r") as in_file:
        input_file = in_file.read()
    kaitaijs = yaml.load(input_file)
    converter = Converter(kaitaijs, True)
    output = converter.generate_code_toplevel()
    with open(output_file_name, "w+") as out_file:
        out_file.write('\n'.join(output))
    print('\n'.join(output))


if __name__ == "__main__":
    main()
