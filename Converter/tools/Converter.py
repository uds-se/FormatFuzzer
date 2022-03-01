import inspect
import sys
import yaml
import re
import os
import traceback

DEBUG = True


class Converter(object):
    # TODO implement kaitai imports
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

            self.endian = ""

            self.parse_subtree()
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

    def lookup_enum(self, name, check_if_implemented=False,
                    error_suppresion=False):  # returns dict of value and possible doc/doc-ref as keys
        if check_if_implemented:
            getter = "IMPLEMENTED"
        else:
            getter = "VALUE"
        try:
            return self.root.global_enum_table[str(name)][getter]
        except:
            if not error_suppresion:
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
            exit(-1)
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
        # print_debug(self.root.global_type_table,True)
        if "enums" in self.subtrees.keys():
            self.output_enums.extend(self.subtrees["enums"].generate_code(called_lowlevel=False))
        self.output_types.extend(self.subtrees["types"].generate_code(called_lowlevel=False))
        self.output_seqs.extend(self.subtrees["seq"].generate_code(called_lowlevel=False))

        if self.endian == "be":
            self.output.append("BigEndian();")
        #  print_debug("BigENDIAN")
        elif self.endian == "le":
            #   print_debug("LittleENDIAN")
            self.output.append("LittleEndian();")
        else:
            print_debug("NO ENDIAN")
        # self.output.append("SetEvilBit(false);")
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
                        self.output.extend(self.subtrees[local_key].generate_code(size, called_lowlevel))
                    except Exception as err:
                        print("\n++++++START Converter codeGEN exception START +++++")
                        traceback.print_exc()
                        print_debug(err.args)
                        print_debug(self.this_level_keys)
                        print_debug(self.subtrees.keys())
                        print_debug(self.input)
                        print_debug(self.subtrees[local_key].input)
                        print("\n++++++END Converter codeGEN exception END +++++\n")
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

    def resolve_switch(self, switch_dict):
        type_list = []
        if "switch-on" in switch_dict.keys():
            cases = switch_dict["cases"]
        else:
            cases = switch_dict
        return list(cases.values())

    def expr_resolve(self, expr, translate_condition_2_c=False, repeat_condition=False, id_of_obj=None):
        # takes a string and depending on the flags returns a list of
        # either elements that could be an instance or
        # a string that works as condition in c
        # TODO add CALL to this when implementig
        operator_replacement_dict = {"not ": " ! ", " and ": " && ", " or ": " || "}
        # condition_splitter_replacement = ["::", "."] #TODO CHECK IF REMOVAL OF "." IS CORRECT (needed for floats to prevent removal of the dot)
        condition_splitter_replacement = ["::"]
        string_splitter_replacement = ['"']
        if expr is None:
            return None
        for to_be_rep in operator_replacement_dict.keys():
            expr = expr.replace(to_be_rep, operator_replacement_dict[to_be_rep])
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
                    expr = expr.replace("_io.eof", "FEof()")
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
            for splitter in condition_splitter_replacement:
                expr = expr.replace(str(splitter), " ")
            # for splitter in string_splitter_replacement:  # TODO UNSURE ABOUT THIS
            #     expr = expr.replace(str(splitter), "")

            if " " in expr:
                return expr.split(" ")
            else:
                return expr

    def chck_flg(self, flag, flag_to_val=False, exclude=None, excluded_values=None):
        if excluded_values is None:
            excluded_values = []
        if self.this_level_keys is None:
            if flag_to_val:
                return None
            else:
                return False
        try:
            # print_debug(f'Checking for {flag} in {self.this_level_keys}')
            if not flag_to_val and flag in self.this_level_keys and (
                    exclude is None or (exclude not in self.this_level_keys)):
                return True
            else:
                # print_debug(self.subtrees)
                for this_level_key in self.this_level_keys:
                    local_key = remap_keys(this_level_key)
                    if local_key is not None:
                        # print_debug(f'check key {local_key} for {flag} in recursion {self.subtrees[local_key].input}')
                        hit = self.subtrees[local_key].chck_flg(flag, flag_to_val, exclude=exclude,
                                                                excluded_values=excluded_values)
                        if hit:
                            # print_debug(f'Found {hit} for {flag} in recursion {self.subtrees[local_key].input}')
                            return hit
                        else:
                            pass
                if flag_to_val:

                    return None
                else:
                    # print_debug(f"returning None on {flag} in {local_key}")
                    return False
        except:
            traceback.print_exc()
            print_debug(f"exception chck_flg {flag} excl {exclude} in {self.input}")
            exit(-1)
            return False

    def lookup_f_in_typ_pres(self, type, flag, id=None, flag_to_val=False, exclude=None):
        # print_debug(type)
        # print_debug(flag)
        # print_debug(str(id))

        if id is None:
            temp = self.subtrees["types"].subtrees[type].chck_flg(flag, flag_to_val, exclude=exclude)
            # print_debug(str(temp)+"\n")
            return temp
        temp = self.subtrees["types"].subtrees[type].subtrees[id].chck_flg(flag, flag_to_val, exclude=exclude)
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
        if self.root.endian == "":
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
            try:
                addin = values[k]["id"]
            except:
                addin = values[k]
            try:
                addin_doc = "     // " + (values[k]["doc"]).strip().replace("\n", "\n     //")
            except:
                addin_doc = ""
            lines.append("  " + addin + " = " + str(hex(k)) + "," + addin_doc)
        try:
            addin = values[keys[-1]]["id"]
        except:
            addin = values[keys[-1]]
        try:
            addin_doc = "     // " + (values[keys[-1]]["doc"]).strip().replace("\n", "\n     //")
        except:
            addin_doc = ""
        lines.append("  " + addin + " = " + str(hex(keys[-1])) + "" + addin_doc)
        lines.append("};")
        return lines


class attribute():
    # A data_point is composed of mutiple attributes/they are the atomic informations
    # TODO CHECK IF CLASS IS ACTUALLY NEEDED
    def __init__(self, name, value):
        self.value = value
        self.name = name

    def chck_flg(self, flag, flag_to_val=False, exclude=None, excluded_values=None):
        if flag_to_val:
            if flag == self.name:
                return self.value
            else:
                return None
        else:
            return flag == self.name

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
        if ("size-eos" in self.input.keys()):
            self.size_eos = True
        else:
            self.size_eos = False
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
        if "if" in self.this_level_keys and not ignore_if:
            self.gen_if(self.containing_type)

        elif "process" in self.this_level_keys:
            self.gen_atomic(docu="IMPLEMENT" + str(self.input["process"]), size=size)
            self.output.extend(self.front)
            self.output.extend(self.back)
            return self.output
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
            elif "size-eos" in self.input.keys():

                self.front.append("    while(FTell() < UNTIL_CONVERTER){")
                self.gen_atomic(indents=2, forwarding=True)
                self.front.append("    }")
            else:
                self.gen_atomic()

        if not ignore_if:
            self.output.extend(self.front)
        self.output.extend(self.back)
        return self.output

    def gen_switch(self, size=None):
        switch = self.type["switch-on"]
        cases = self.type["cases"]
        default_needed = True
        switch_over_enum = False
        num_of_enum_cases = 0
        num_of_switch_cases = len(cases.keys())
        switch_drop = ["_root", "_parent", "_io"]
        if switch.split(".")[0] in switch_drop:
            switch_term = ".".join(switch.split(".")[1:])
        else:
            switch_term = switch
        ###INJECTION LOCAL VAR FOR START

        self.front.append("     switch(" + str(switch_term) + ") {")

        # print_debug(self.input)
        if type(switch_term.split(".")) is list:
            poss_enum_dict = self.root.lookup_enum(switch_term.split(".")[::-1][0], error_suppresion=True)
            # print_debug(poss_enum_dict)
            if type(poss_enum_dict) is dict:
                switch_over_enum = True
                num_of_enum_cases = len(poss_enum_dict.keys())
                default_needed = (num_of_switch_cases < num_of_enum_cases)

        for case_key in cases.keys():
            case = self.root.expr_resolve(case_key)
            if case == ["_"] or case == "_":
                default_needed = False
                case_val = "default"  # TODO remove case from case default
            elif type(case) is list:

                case_val = case[1]
                # case_val = str(hex(self.root.lookup_enum_val_2_key(case[0], case[1])))

            else:
                case_val = case
            # sizeos = self.root.lookup_f_in_typ_pres(cases[case_key], "size-eos", exclude="encoding")
            sizeos = self.root.lookup_f_in_typ_pres(cases[case_key], "size-eos")
            repeat = self.root.lookup_f_in_typ_pres(cases[case_key], "repeat")
            # encoding = self.root.lookup_f_in_typ_pres(cases[case_key], "encoding")
            if (sizeos or repeat or self.root.lookup_type(cases[case_key], check_if_param_needed=True)):
                if "size" in self.input.keys():
                    paramfield = "(" + str(self.input["size"]) + ")"
                else:
                    # print_debug("ERROR NO SIZE GIVE FOR PARAMETERIZED STRUCT INSTANTIATION (1):\n"+str(self.input))
                    paramfield = ""
            else:
                paramfield = ""
            if case_val != "default":
                self.front.append("         case " + str(case_val) + ":")
            else:
                default_needed = False
                self.front.append("         default:")
            self.front.append("             " + str(cases[case_key]) + "_TYPE " + str(self.id) + paramfield + ";")
            self.front.append("             break;")

        if default_needed and "size" in self.input.keys():
            self.front.append("         default:")
            # self.output.append(f'    Warning("LENGTH %hu %hx",{str(self.input["size"])},{str(self.input["size"])});')
            self.front.append("             ubyte raw_data_CONVERTER[" + str(self.input["size"]) + "];")
            self.front.append("             break;")
        elif default_needed and not switch_over_enum:
            self.front.append("         default:")
            self.front.append("             ubyte raw_data_CONVERTER[LENGHT MISSING];")
            self.front.append("             break;")
            print_debug("LENGHT NOT FOUND FOR DEFAULT SWITCH CASE")
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
            # self.front.append("    local uint32 UNTIL_CONVERTER = length_CONVERTER;") #TODO THIS IS OPTION B FOR EOS
            self.front.append("    while(FTell() < UNTIL_CONVERTER){")
            self.gen_atomic(indents=2)
            self.front.append("    }")
            # self.front.append("    ")

            # self.front.append("//     repeat: eos PLACEHOLDER<=======")
            # TODO INSERT NEXT WHILE CONSTRUCTION
            pass
        else:
            print_debug("REPEAT MISSING" + str(self.input["repeat"]))
        # TODO implement

        pass

    def gen_atomic(self, docu="", size=None, type_override=None, indents=1, forwarding=False):

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

        if self.size_eos and not forwarding and "length_CONVERTER" == size:
            self.front.append("    while(FTell() < UNTIL_CONVERTER){")  # OPTION B
            self.gen_atomic(indents=2, forwarding=True)
            self.front.append("    }")  # OPTION B

        elif self.type == "str":
            if self.size is not None:
                # TODO Done? IMPLEMENT CASE FOR DIFFERENT THAN ZEROBYTE TERMINATOR
                self.front.append(prepend + "char " + str(self.id) + "[" + str(self.size) + "]" + ";" + loc_doc)
            elif "size-eos" in self.input:
                self.front.append(
                    prepend + "char " + str(
                        self.id) + "[length_CONVERTER -(FTell()-struct_start_CONVERTER)];" + loc_doc)
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
                    try:
                        self.gen_instances(self.input["size"])
                    except:
                        pass
                    try:
                        length_addon = "(" + self.root.expr_resolve(self.input["size"],
                                                                    translate_condition_2_c=True) + ")"
                    except:
                        length_addon = "(length_CONVERTER -(FTell()-struct_start_CONVERTER))"
                        loc_doc = "//TESTING"
                if size:
                    length_addon = "[" + size + "]"
                self.front.append(prepend + str(self.type) + " " + str(self.id) + length_addon + ";" + loc_doc)
        elif self.size is not None:  # JUST BYTES
            self.front.append(prepend + "ubyte " + str(self.id) + "[" + str(self.size) + "]" + ";" + loc_doc)
        else:
            # self.front.append(prepend + "byte " + str(self.id) + "[UNTIL_CONVERTER - FTell()]" + ";" + loc_doc)#OPTION A
            self.front.append(prepend + "ubyte " + str(self.id) + ";" + loc_doc)  # OPTION B

            # self.gen_repeat()
            # self.front.append("    local int64 UNTIL_CONVERTER = FTell() + length_CONVERTER;")
            # self.front.append("    while(FTell() < UNTIL_CONVERTER){")
            # self.gen_atomic(indents=2,)
            # self.front.append("    }")
            # print_debug("ERROR NO SIZE OR TYPE GIVEN AND ITS NO MAGIC")
            # print_debug(self.input)
            # self.front.append("//STUFF MISSING HERE @ NO MAGIC " + str(self.id) + "----" + str(self.input))
            # print_debug(self.front)

    def gen_instances(self, condition):
        # TODO CHECK FOR SPECIAL POSITION DEPENDENT INSTANCES
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
        # self.front.append("    ubyte " + str(self.id) + "[" + str(self.magic_len) + "];")
        # TODO HERE POSSIBLE SET_EVIL_BIT
        if self.magic_len > 1:
            self.front.append("    ubyte " + str(self.id) + "[" + str(self.magic_len) + "];")
            self.front.append("    if (" + self.id + "[0] != " + self.magic[0] + " ||")
            for x in range(1, self.magic_len - 1):
                self.front.append("        " + self.id + "[" + str(x) + "] != " + self.magic[x] + " ||")
            self.front.append(
                "        " + self.id + "[" + str(self.magic_len - 1) + "] != " + self.magic[self.magic_len - 1] + ") {")
        else:
            self.front.append("    ubyte " + str(self.id) + ";")
            self.front.append("    if (" + self.id + " != " + self.magic[0] + ") {")
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

    def chck_flg(self, flag, flag_to_val=False, exclude=None, excluded_values=None):
        if excluded_values is None:
            excluded_values = []
        if flag_to_val:
            if flag in self.this_level_keys and (exclude is None or exclude not in self.this_level_keys):

                if str(self.input[flag]) not in excluded_values:
                    # print_debug(f"Flag {flag} found : {self.input[flag]} Exclude : {excluded_values}")
                    return self.input[flag]
                else:
                    return None
            else:
                return None
        return flag in self.this_level_keys and (exclude is None or exclude not in self.this_level_keys)


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
        if "length_CONVERTER" == size:
            # self.output.append("    local uint32 UNTIL_CONVERTER = FTell() + length_CONVERTER;") #TODO THIS IS OPTION A FOR EOS
            self.output.append(
                "    local uint32 UNTIL_CONVERTER = FTell() + length_CONVERTER;//A")  # TODO THIS IS OPTION B FOR EOS
            # self.output.append('    Warning("LENGTH %hu UNTIL %hu FTell %hu",length_CONVERTER,UNTIL_CONVERTER,FTell());')

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
        # self.pre = {}
        self.pre = []
        self.output = []

    def parse_subtree(self, name=None):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.root.register_type(local_key, self.input[local_key])
                self.subtrees[local_key] = Converter(self.input[this_level_key], parent=self, root=self.root)
                self.subtrees[local_key].parse_subtree(name=local_key)
        self.parse_arguments_main()

    def parse_arguments_main(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                if self.parse_arguments_recursion(self.subtrees[local_key], origin_type=local_key):
                    self.root.register_type(name=local_key, param_needed=True)

    def parse_arguments_recursion(self, item, origin_type=None):  # returns True if param is needed in subtree
        # print_debug(item.this_level_keys)
        # print_debug(item.subtrees)
        # print_debug(item.input)
        param_needed = False
        for this_level_key in item.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                if item.chck_flg("size-eos"):
                    param_needed = True
                if item.chck_flg("repeat", flag_to_val=True) == "eos":
                    param_needed = True
                if item.chck_flg("process"):
                    param_needed = True
            if param_needed:
                # print_debug(item.name)
                return param_needed

        # print_debug(f'Entering Recursion for item {item.input}')
        included_types = []
        exclusion_list = []
        hit = item.chck_flg("type", flag_to_val=True, excluded_values=exclusion_list)
        while hit is not None:
            # print_debug(f'Hit {hit} Resolved Hits {hit_list} actl {item.chck_flg("type", flag_to_val=True)} from {self.this_level_keys}')
            exclusion_list.append(str(hit))
            if type(hit) is dict:
                hit_list = self.root.resolve_switch(hit)
            else:
                hit_list = [self.root.expr_resolve(hit)]
            for hitter in hit_list:
                if hitter in self.this_level_keys and not hitter in included_types:
                    included_types.append(hitter)
            hit = item.chck_flg("type", flag_to_val=True, excluded_values=exclusion_list)

        # print_debug("Final included types "+str(included_types))
        # print_debug(item.name)
        if included_types == []:  # LOWEST LATER // No SUBTYPES
            return False
        else:
            for sub_type in included_types:
                lower_level_type = self.subtrees[sub_type]
                # print_debug(lower_level_type)
                if self.parse_arguments_recursion(lower_level_type, origin_type=origin_type):
                    param_needed = True
            # print_debug(param_needed)
            return param_needed and not item.chck_flg("size")

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):

        # self.output.extend(self.gen_forward_types())
        self.output.extend(self.gen_complete_types(size))
        self.pre.extend(self.output)
        return self.pre

    def gen_complete_types(self, size=None):
        output = []
        # if "process" in self.input["seq"]:
        #     print_debug(self.input)
        #     print_debug(self.input)
        for this_level_key in self.this_level_keys:

            lenfield = ""
            if self.root.lookup_type(this_level_key, check_if_param_needed=True):
                lenfield = "(uint32 length_CONVERTER)"

            item = self.subtrees[this_level_key]
            #
            # # if item.chck_flg("size-eos") and not item.chck_flg("encoding"):
            # if item.chck_flg("size-eos"):
            #     lenfield = "(uint32 length_CONVERTER)"
            # if item.chck_flg("repeat", flag_to_val=True) == "eos":
            #     lenfield = "(uint32 length_CONVERTER)"
            # if item.chck_flg("process"):
            #     lenfield = "(uint32 length_CONVERTER)"
            # if lenfield != "":
            #     self.root.register_type(name=this_level_key, param_needed=True)
            if lenfield != "":
                forward_lenfield = lenfield + "{}"
            else:
                forward_lenfield = ""
            ##############WIP FORWARD DECLARATION RESTRUCTURE################
            self.pre.append("struct " + str(this_level_key) + "_TYPE" + forward_lenfield + ";")

            # self.pre[str(this_level_key)]=("struct " + str(this_level_key) + "_TYPE" + forward_lenfield + ";")

            ##############WIP FORWARD DECLARATION RESTRUCTURE################

            output.append("struct " + str(this_level_key) + "_TYPE" + lenfield + " {")
            if lenfield != "":
                output.append("    local uint32 struct_start_CONVERTER = FTell();")

            # TODO IMPLEMENT size Calc locals
            if lenfield != "":
                sizer = "length_CONVERTER"
            else:
                sizer = None
            output.extend(item.generate_code(sizer, called_lowlevel=True))  # GOING TO CHILD ITEM
            output.append("};\n")

        # TODO IMPLEMENT PARAMETERS FOR FUNCTIONS THAT HAVE A CHILD THAT NEED THE PARAMETER AND GET IT FROM PARENT
        return output

    def gen_forward_types(self):  # DEPRECATED
        output = []
        for this_level_key in self.this_level_keys:
            output.append("struct " + str(this_level_key) + "_TYPE ;")
        return output


def print_debug(string, pretty=False):
    if DEBUG:
        if type(string) is dict and pretty:
            print("\nDEBUG: " + str(yaml.dump(string, default_flow_style=False)).replace("\n", "\n     "))
        else:
            print("\nDEBUG: " + str(string).replace("\n", "\n     "))


def remap_keys(key):
    remap = {"doc-ref": "doc_ref"}
    blocklist = ["-webide-representation", "-orig-id", "params"]
    # TODO EXTEND TO SUPPORT MORE THINGS ESPECIALLY PARAMS
    if key in blocklist: return None
    if key in remap.keys(): return remap[key]
    return key


def insert_imports(main_input, imports, path):
    out = main_input
    for imp in imports:
        imported_kaitai = None
        try:
            with open(f'{path}/{imp}.ksy', "r") as in_file:
                input_file = in_file.read()
            imported_kaitai = yaml.load(input_file)
        except:
            print_debug(f'{imp} import not found @ {path}/{imp}.ksy')
            exit(-1)
        try:
            imported_types = imported_kaitai["types"]
            for imp_type in imported_types.keys():
                out["types"][imp_type] = imported_types[imp_type]
        except:
            pass

        try:
            imported_main_seq = imported_kaitai["seq"]
            out["types"][imported_kaitai["meta"]["id"]] = imported_main_seq
        except:
            pass

        try:
            imported_enums = imported_kaitai["enums"]
            for imp_enum in imported_enums.keys():
                out["enums"][imp_enum] = imported_enums[imp_enum]
        except:
            pass
    return out


def kaitai_sorter(input_kaitai, subtree):
    this_level_keys = subtree.keys()
    if "types" in this_level_keys:
        pass
    if "enums" in this_level_keys:
        pass


def main():
    global converter, DEBUG

    if len(sys.argv) != 3:
        print("USAGE = python3 Converter.py <input file path> <output file path>")  # TODO
        exit(1)
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    with open(input_file_name, "r") as in_file:
        input_file = in_file.read()
    kaitaijs_main = yaml.load(input_file)

    try:
        imports = kaitaijs_main["meta"]["imports"]
        # print_debug(imports)
        # print_debug(input_file_name)
        filepath = os.path.dirname(os.path.abspath(input_file_name))
        # print_debug(filepath)
        kaitaijs = insert_imports(kaitaijs_main, imports, filepath)
    except:
        kaitaijs = kaitaijs_main
    # kaitai_sorter(kaitaijs,kaitaijs)
    # print_debug(kaitaijs, pretty=True)

    converter = Converter(kaitaijs, True)
    output = converter.generate_code_toplevel()
    with open(output_file_name, "w+") as out_file:
        out_file.write('\n'.join(output))

    # print('\n'.join(output))


if __name__ == "__main__":
    main()
