import inspect
import sys
import yaml
import re
import os
import traceback
from functools import reduce
import operator
from inspect import getframeinfo, stack

DEBUG = True
GENERATION_MARKER = True
imported = {}
ALIGN = None
format_name = ""
EMPTY_STRUCT_FILLER = {}
EMPTY_STRUCT_FILLER_FLAG = True


class Converter(object):
    # TODO CHECK IF DO WHILE ALWAYS WORKS IN CASE OF NO OBJECT GENERATED AT ALL

    def __init__(self, input_js, is_master=False, parent=None, root=None, name=None, preprocessor=None):
        self.output_instance = []
        self.enum_size = {}
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
            self.preprocessor = preprocessor

            self.endian = ""

            self.parse_subtree()
        else:
            self.parent = parent
            self.root = root

    # TODO MAYBE ADD MORE TABLES HERE FOR MORE DYNAMIC CODE GENERATION

    # registers instance in "global" table during parsing time
    def register_instance(self, name, value, containing_type):
        # print_debug(f"registering Instance {name} in {containing_type} with {value}")
        try:
            self.root.global_instance_table[str(containing_type)][str(name)] = {"VALUE": value, "IMPLEMENTED": False}
        except:
            self.root.global_instance_table[str(containing_type)] = {str(name): {"VALUE": value, "IMPLEMENTED": False}}
        return

    # registers type in "global" table during parsing time
    def register_type(self, name, value=None,
                      size_param_needed=False,
                      custom_param_needed=False):

        if value is not None:
            self.root.global_type_table[str(name)] = {"VALUE": value, "IMPLEMENTED": False, "PARAM": size_param_needed,
                                                      "PARAM_CUSTOM": custom_param_needed}
        elif size_param_needed:
            self.root.global_type_table[str(name)]["PARAM"] = True
        elif custom_param_needed:
            self.root.global_type_table[str(name)]["PARAM_CUSTOM"] = custom_param_needed

    # registers enum in "global" table during parsing time
    def register_enum(self, name, value, size):
        self.root.global_enum_table[str(name)] = {"VALUE": value, "IMPLEMENTED": False, "SIZE": size}

    # returns dict of value and possible doc/doc-ref as keys
    def lookup_instance(self, name, containing_type,
                        check_if_implemented=False):
        if check_if_implemented:
            getter = "IMPLEMENTED"
        else:
            getter = "VALUE"
        try:
            return self.root.global_instance_table[str(containing_type)][str(name)][getter]
        except:
            # print_debug("\nERROR INSTANCE " + str(name) + " NOT FOUND\nCan safely be ignored just for testing if expr_resolve works!\n")
            return False if check_if_implemented else None

    # returns dict of value and possible doc/doc-ref as keys
    def lookup_type(self, name, check_if_implemented=False,
                    check_if_size_param_needed=False,
                    check_if_custom_param_needed=False):
        if check_if_implemented:
            getter = "IMPLEMENTED"
        elif check_if_size_param_needed:
            getter = "PARAM"
        elif check_if_custom_param_needed:
            getter = "PARAM_CUSTOM"
        else:
            getter = "VALUE"
        if name and "(" in name:
            name = name.split("(")[0]

        try:
            return self.root.global_type_table[str(name)][getter]
        except:
            # print_debug(traceback.format_exc())
            # print_debug("ERROR TYPE " + str(name) + " NOT FOUND \n")
            return None

    # returns dict of value and possible doc/doc-ref as keys
    def lookup_enum(self, name, check_if_implemented=False,
                    error_suppresion=False):
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

            getter = self.root.global_instance_table[str(containing_type)]
        else:
            print_debug(str(type) + " TABLE NOT IMPLEMENTED\n")
            exit(-1)
        getter[str(name)]["IMPLEMENTED"] = value

    def parse_subtree(self, name=None):
        self.name = name
        # print_debug(self.input)
        # print_debug(type(self.this_level_keys))

        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                # print_debug(local_key)
                # print_debug(name)
                self.__dict__[local_key] = self.input[this_level_key]
                self.subtrees[local_key] = globals()[local_key](self.input[this_level_key], self, self.root, name=name)
                self.subtrees[local_key].parse_subtree(name=name)

    def generate_code_toplevel(self):
        # print_debug(self.root.global_instance_table, True)
        # print_debug(self.subtrees.keys())
        self.root.global_type_table[f'{format_name}_CONVERTER']["PARAM"] = True
        self.output_types.extend(self.subtrees["types"].generate_code(called_lowlevel=False))

        self.output_seqs.extend(self.subtrees["seq"].generate_code(called_lowlevel=False))

        # if "instances" in self.subtrees.keys():
        #     # print_debug(f'FOUND INSTANCES {self.subtrees["instances"]}' )
        #     self.output_instance.extend(self.subtrees["instances"].generate_code(called_lowlevel=False))

        if "enums" in self.subtrees.keys():
            self.output_enums.extend(self.subtrees["enums"].generate_code(called_lowlevel=False))

        if self.endian == "be":
            self.output.append(f"BigEndian();{gen_marker()}")
        elif self.endian == "le":
            self.output.append(f"LittleEndian();{gen_marker()}")
        else:
            print_debug("NO ENDIAN")
        self.output.append('Printf("SIZE %d\\n",FileSize());')

        # self.output.append("SetEvilBit(false);")
        self.output.extend(self.output_enums)
        self.output.extend(self.output_types)
        self.output.extend(self.output_seqs)
        self.output.extend(self.output_instance)
        #####GARBAGE COLLECTION####
        self.output.append("    if(FTell()<(FileSize()-1)){")
        self.output.append("        ubyte garbage_after_end_of_parsed_file_CONVERTER[(FileSize())-FTell()];")
        self.output.append('        Warning("Found possible Garbage-Data!");')
        self.output.append("    }")

        return self.output

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        if "instances" in self.this_level_keys:
            for x in self.input["instances"].keys():
                self.mark_as_implemented("instance", x, value=False, containing_type=self.name)

        gen_list = []
        if "doc-ref" in self.this_level_keys:
            gen_list.append("doc-ref")
        if "doc" in self.this_level_keys:
            gen_list.append("doc")
        if "seq" in self.this_level_keys:
            gen_list.append("seq")
        if "instances" in self.this_level_keys:
            gen_list.append("instances")

        # print_debug(gen_list)
        # print_debug(list(self.this_level_keys))
        # for this_level_key in list(self.this_level_keys)[::-1]:
        for this_level_key in gen_list:
            local_key = remap_keys(this_level_key)

            if local_key is not None:
                if True:  # SWITCH BETWEEN SUPPRESSION OF "UNIMPLEMENTED" ERRORS
                    try:
                        # print_debug(f"Calling {local_key} with size {size}")
                        self.output.extend(self.subtrees[local_key].generate_code(size, called_lowlevel))
                    except Exception:
                        print("\n++++++START Converter codeGEN exception START +++++")
                        print_debug(traceback.format_exc())
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
        for e in self.input["enums"]:
            enum_name = e
            enum_content = self.input["enums"][enum_name]
            local_values = list(enum_content.keys())
            last = local_values[-1]
            bit_len = len(hex(last)[2::]) * 4
            if bit_len <= 8:
                self.enum_size[enum_name] = f"ubyte"
            elif bit_len <= 16:
                self.enum_size[enum_name] = f"uint16"
            elif bit_len <= 32:
                self.enum_size[enum_name] = f"uint32"
            elif bit_len <= 64:
                self.enum_size[enum_name] = f"uint64"
            else:

                print_debug(f"UNHANDLED ENUM SIZE {bit_len} OF ENUM {enum_name}")

    def double_check_enum_size(self, enum_name, actual_size):
        actual_size = self.resolve_datatype(actual_size)
        # print_debug(actual_size)
        if self.enum_size[enum_name] != actual_size:
            self.enum_size[enum_name] = actual_size
            self.root.global_enum_table[enum_name]["SIZE"] = actual_size

    def lookup_enum_size(self, enum):
        return self.enum_size[enum]

    def lookup_enum_val_2_key(self, enum, key):  # UNUSED

        inv_map = {v: k for k, v in self.enums[enum].items()}
        return inv_map[key]

    def resolve_switch(self, switch_dict):
        if "switch-on" in switch_dict.keys():
            cases = switch_dict["cases"]
        else:
            cases = switch_dict
        return list(cases.values())

    def expr_resolve(self, expr, translate_condition_2_c=False, repeat_condition=False, id_of_obj=None):
        # takes a string and depending on the flags returns a list of
        # either elements that could be an instance or
        # a string that works as condition in c

        operator_replacement_dict = {"not ": " ! ", " and ": " && ", " or ": " || ", "_parent.": ""}
        if "or " in str(expr) and not " or " in str(expr):
            operator_replacement_dict["or "] = "|| "
            print_debug(f"ADDED >or < to operator replacement cause{expr}")
        # condition_splitter_replacement = ["::", "."] #TODO CHECK IF REMOVAL OF "." IS CORRECT (needed for floats to prevent removal of the dot)
        condition_splitter_replacement = ["::"]
        string_splitter_replacement = ['"']
        # print_debug(expr)
        if expr is None:
            return None
        if type(expr) is bool:
            return expr
        if type(expr) is int:
            return expr
        for to_be_rep in operator_replacement_dict.keys():
            expr = expr.replace(to_be_rep, operator_replacement_dict[to_be_rep])

        # for element in re.split('(\W+)', expr):  # replacing f**kin 0xffff_ffff with 0xffffffff
        for element in re.split('[^a-zA-Z0-9_.]+', expr):
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
            if expr == "_root._io":
                return None

            try:
                if "Str(" in expr:
                    expr = expr.replace("Str(", "")
                    expr = expr.replace(")", "")
            except:
                pass

            try:
                expr = expr.replace("_io.eof", "FEof()")
            except:
                pass
            # TODO UNSURE ABOUT THIS ONE!!!! breaks if used with restricted io stream
            # maybe do something with length_CONVERTER
            try:
                expr = expr.replace("_io.size", "FileSize()-1")
            except:
                pass
            try:

                expr = expr.replace("_io.pos", "FTell()")
            except:
                pass

            try:
                if "._io" in expr:
                    expr = expr.replace("._io", "")
            except:
                pass
            pass
            if "::" in expr:
                for element in expr.split(" "):
                    if "::" in element:
                        expr = expr.replace(str(element), element.split("::")[1])
            # print_debug(expr)
            return expr
        elif False:
            pass
        else:  # no flag set
            for splitter in condition_splitter_replacement:
                expr = expr.replace(str(splitter), " ")  # TODO rep AAAA with " " maybe
            if " " in expr:
                # print_debug(expr)
                return expr.split(" ")
            elif "." in expr:
                # print_debug(f'FOUND >.< in {expr}!')
                return expr.split(".")
            else:
                return expr

    def infer_type_top(self, input_str, containing_type=None, check_if=False):
        # print_debug(f'Inferring Type of {input_str} in {containing_type}')
        type_ret = self.infer_type(input_str, containing_type, check_if)
        # print_debug(f'=> Inferred Type {type_ret}')
        if type_ret:
            return type_ret
        else:
            print_debug(f'Inferring Type of {input_str} in {containing_type}')
            print_debug(f'ERROR => Inferred Type {type_ret}')

    def infer_type(self, input_str, containing_type=None, check_if=False):
        # is_color_mask_given ? color_mask_given.red_mask : header.bits_per_pixel == 16 ? 0b11111_00000_00000 : header.bits_per_pixel == 24 or header.bits_per_pixel == 32 ? 0xff0000 : 0
        try:
            input_str = input_str.strip()
        except:
            pass
        if input_str is None or input_str == "":
            return None
        condition_list = ["and", "or", "&&", "||", "==", ">", "<", "<=", ">=", "!="]
        for cond in condition_list:
            if input_str == cond:
                # print_debug(f"returning int cause {input_str}")
                return "int"
        if type(input_str) is dict:
            # print_debug(f"IMPLEMENT TYPE SWITCHING!!!! {input_str}")
            return "TEST"

        if type(input_str) is not str:
            print_debug(f"TRYING TO INFER TYPE OF {input_str} WHICH HAS TYPE {type(input_str)}")

        known_replacements = {"_io.pos": "uint32", "to_s": "string", "Str": "string", "SPrintf": "string"}
        for element in known_replacements.keys():
            if input_str == element:
                return known_replacements[element]
            elif len(input_str.split(".")) == 2:
                if input_str.split(".")[1] == element:
                    return known_replacements[element]

        patter_brackets = r"^(?P<pre>[\w\W]*?)\((?P<content>[\w\W]*)\)(?P<back>[\w\W]*)$"
        match = re.match(patter_brackets, input_str)
        if match is not None:
            pre = match.group('pre')
            content = match.group('content')
            back = match.group('back')
            # print_debug(f" PRE {pre} CONT {content} back {back}")

            if pre and pre.strip() == "sizeof":
                return "int"

            pre_type = self.infer_type(pre, containing_type, check_if)
            content_type = self.infer_type(content, containing_type, check_if)
            back_type = self.infer_type(back, containing_type, check_if)
            present_types_pre = []
            present_types = []
            if pre_type:
                present_types_pre.append(pre_type)
            if content_type:
                present_types_pre.append(content_type)
            if back_type:
                present_types_pre.append(back_type)
            for x in present_types_pre:
                if x not in present_types:
                    present_types.append(x)

            if "string" in present_types:
                return "string"
            elif "double" in present_types:
                # print_debug(f"returning double cause {input_str}" + gen_marker())
                return "double"
            elif "int" in present_types:
                return "int"
            elif "int64" in present_types:
                return "int64"
            else:

                print_debug(f'OUUPSII got types | {pre_type} | {content_type} | {back_type} | in {input_str}')
                print_debug(f"PRESENT TYPES {present_types}")
        if "?" in input_str and ":" in input_str:
            if check_if:
                return True

            condition = input_str.split("?")[0]
            else_case = "".join(input_str.split(":")[-1])
            then_case = input_str.split(":" + else_case)[0].split("?")[1]
            condition_type = self.infer_type(condition, containing_type, check_if)
            then_case_type = self.infer_type(then_case, containing_type, check_if)
            else_case_type = self.infer_type(else_case, containing_type, check_if)
            if then_case_type == else_case_type and then_case_type:
                return then_case_type
            elif then_case_type and not else_case_type:
                return then_case_type
            elif else_case_type and not then_case_type:
                return else_case_type
            else:
                if then_case_type == "double" or else_case_type == "double":
                    # print_debug(f"ERROR then_type {then_case_type} else_type {else_case_type}!!!")
                    return "double"
            # print_debug(f"Parsing value with if {input_str}")
            # print_debug(f" IF {condition} THEN {then_case} ELSE {else_case} containing type {containing_type}")
        if check_if:
            return False
        arithmetic_ops = ["/"]
        for op in arithmetic_ops:
            if op in input_str:
                # print_debug(f"returning double cause {input_str}" + gen_marker())
                return "double"
        arithmetic_ops = ["/", "+", "-", "*", "|", "&"]
        for op in arithmetic_ops:
            if op in input_str:
                return "int64"

        condition_list = [" and ", " or ", " && ", " || ", " == ", " > ", " < ", " <= ", " >= ", " >> ", " << "]
        for cond in condition_list:
            if cond in input_str:
                # print_debug(f"returning int cause {input_str}" + gen_marker())
                return "int"

        if " " in input_str.strip():
            units = input_str.strip().split(" ")
            if len(units) > 2:
                pass
                # print_debug(f"EDGECASE {units}")
            first_type = self.infer_type(units[0], containing_type, check_if)
            second_type = self.infer_type(units[1], containing_type, check_if)
            if first_type == second_type and first_type:
                return first_type
            elif second_type and not first_type:
                return second_type
            elif first_type and not second_type:
                return first_type
            else:
                # print_debug(f" SPACE SEPERATED TYPES missmatch {first_type} {second_type}")
                if first_type == "int64" or second_type == "int64":
                    # print_debug(f"ERROR {input_str} first_type {first_type} second_type {second_type}!!!")
                    return "int64"
                if first_type == "double" or second_type == "double":
                    # print_debug(f"ERROR {input_str} first_type {first_type} second_type {second_type}!!!")
                    return "double"
        can_conv_int = False
        can_conv_float = False
        try:
            val = int(input_str)
            # print_debug(f"returning int64 cause {input_str}" + gen_marker())
            return "int64"
        except:
            try:
                val = float(input_str)
                # print_debug(f"returning double cause {input_str}" + gen_marker())
                return "double"
            except:
                pass

        if "." in input_str:
            # print_debug(f'A+Trying to get type of {input_str} in {containing_type}')
            next_container = self.find_type_off_id(input_str.split(".")[0], containing_type)
            if next_container:
                return self.infer_type(".".join(input_str.split(".")[1::]), next_container, check_if)
            else:
                # print_debug(f'Couldnt find type of {input_str.split(".")[0]}')
                return None
        else:
            # print_debug(f'B+Trying to get type of {input_str} in {containing_type}')
            pos_type = self.find_type_off_id(input_str, containing_type)
            if pos_type:
                return pos_type
            else:
                # print_debug(f'RETURNING DOUBLE {input_str}')
                return "double"

    def find_type_off_id(self, id_name, containing_type, get_whole_type=False):
        id_name = id_name.strip()
        if containing_type is None:
            this_type_objects = self.root.input
        else:
            this_type_objects = self.root.lookup_type(containing_type)
        # print_debug(type(this_type_objects))
        # print_debug(id_name)
        tt_instances = this_type_objects["instances"] if "instances" in this_type_objects.keys() else []
        tt_seqs = this_type_objects["seq"] if "seq" in this_type_objects.keys() else []
        # print_debug(tt_instances.keys())
        # print_debug(tt_seqs)

        for datapoint in tt_seqs:
            local_id = datapoint["id"]
            # print_debug(f'Comparing {local_id} and {id_name}')
            if datapoint["id"] == id_name:
                # print_debug(f'FOUND {id_name} OFF TYPE {datapoint["type"]}')
                if type(datapoint["type"]) is dict:
                    return self.infer_type_top(datapoint["type"], containing_type)
                if get_whole_type:
                    return datapoint["type"]
                else:
                    return datapoint["type"].split("(")[0]
        for inst_name in tt_instances.keys():
            if inst_name == id_name:
                # print_debug(f'FOUND {id_name} OFF TYPE {tt_instances[inst_name]}')
                if "type" in tt_instances[inst_name].keys():
                    return tt_instances[inst_name]["type"]
                elif "value" in tt_instances[inst_name].keys():
                    # print_debug(f"calling infer_type with {containing_type}")
                    return self.infer_type_top(tt_instances[inst_name]["value"], containing_type)
                else:
                    str_pattern = fr"{id_name}\.to_s"
                    # print_debug(str_pattern)
                    str_occurences = self.root.preprocessor.search_num_occurences(str_pattern, pattern_override=True)
                    if str_occurences:
                        # print_debug(f'FOUND {id_name} to be char')
                        return "char"

                    print_debug(f'FOUND {id_name} OFF TYPE {tt_instances[inst_name]} occuring {str_occurences}')
                    print_debug(f"returning ubyte")
                    return "ubyte"

        type_params = self.root.lookup_type(containing_type, check_if_custom_param_needed=True)
        if type_params:
            if id_name in type_params.keys():
                return type_params[id_name]
        # print_debug(f'DID NOT FIND {id_name} in TYPE {containing_type}')
        return None

    # recusively checks for flag or returns the value with optional exclusion list
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
            # print_debug(f"exception chck_flg {flag} excl {exclude} in {self.input}")
            print_debug(f"exception chck_flg {flag} excl {exclude}")
            print_debug(self.parent.subtrees)
            print_debug(self.subtrees)
            print_debug(self.this_level_keys)
            exit(-1)
            return False

    # Checks recursively if flag is present in type #UNUSED
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

    # resolves c-Type from kaitai-type
    def resolve_datatype(self, kaitype, getsize=False, getendian=False):
        # TODO do something about LE????
        if kaitype == "bool":
            return "int"
        elif kaitype == "int":
            return "int"
            # return kaitype
        elif kaitype == "str":
            return "char"
        elif kaitype == "double":
            return "double"
        elif kaitype == "strz":
            return "string"
        if type(kaitype) is not str:
            print_debug(f"Trying to Resolve Datatype of{kaitype} of type {type(kaitype)}")
            return None
        match = re.match(r'(?P<parsed_type>[a-zA-Z])(?P<parsed_size>[0-9])(?P<parsed_endian>[a-zA-Z]*)', kaitype)
        if match is None:
            if getendian:
                return self.root.endian
            else:
                return None
        parsed_type = match.group('parsed_type')
        parsed_size = match.group('parsed_size')
        parsed_endian = match.group('parsed_endian')
        if getsize:
            return parsed_size
        if getendian:
            if parsed_endian == "le" or parsed_endian == "be":
                return parsed_endian
            else:
                return self.root.endian

        type_table = {"u": "uint", "s": "int", "b": "byte", "f": "float"}
        endian_table = {"le": "", "be": "", "": ""}  # TODO No Clue how to handle right Now
        # endian_table = {"le": "/*LITTLE ENDIAN*/", "be": "/*BIG ENDIAN*/", "": ""}  # TODO No Clue how to handle right Now
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

    def chck_flg(self, flag, flag_to_val=False, exclude=None, excluded_values=None):

        # TODO THIS IS A DIRTY FIX FOR CASES WHERE SUBTYPES(usually imports like exif into jpeg)
        # HAVE THEIR OWN META SECTION DEFINIGN ENDIAN IN A SWITCH STRUCTURE.
        # THIS FUNCTIONS OVERRIDES THE CONVERTER LVL FUNCTION IN ORDER TO CIRCUMVENT
        # THE NEED FOR SOME SUBTREE STRUCTURE UNDER META
        # THIS MIGHT BE A PROBLEM IF ENDIANESS(JPEG) != ENDIANESS(exif)
        # IN ORDER TO FIX THIS SOME SORT OF ENDIAN FLIP IS NEEDED AND INFORMATION ROUTING TO THE CORRESPONDING
        # CODE GEN PARTS
        if flag_to_val:
            return None
        return False


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
                self.root.register_enum(local_key, self.input[local_key], self.root.lookup_enum_size(local_key))
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])
                # print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        self.output = []
        for enum in self.subtrees.keys():
            self.output.extend(
                self.gen_single_enum(enum, self.subtrees[enum], type=converter.lookup_enum_size(enum)))
            self.output.append("\n")

        if called_lowlevel:
            self.root.output_enums.extend(self.output)
            return [""]
        return self.output

    def gen_single_enum(self, key, enumerations, type="ubyte"):
        values = enumerations.get_value()
        lines = []
        type = f'<{type}>'

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
            if f'_{key}_ENUM' in addin:
                lines.append(f"    {addin} = {str(hex(k))},{addin_doc}")
            else:
                lines.append(f"    {addin}_{key}_ENUM = {str(hex(k))},{addin_doc}")
        try:
            addin = values[keys[-1]]["id"]
        except:
            addin = values[keys[-1]]
        try:
            addin_doc = "     // " + (values[keys[-1]]["doc"]).strip().replace("\n", "\n     //")
        except:
            addin_doc = ""
        if f'_{key}_ENUM' in addin:
            lines.append(f"    {addin} = {str(hex(keys[-1]))},{addin_doc}")
        else:
            lines.append(f"    {addin}_{key}_ENUM = {str(hex(keys[-1]))},{addin_doc}")
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

    def get_name(self):  # UNUSED
        return self.name


class data_point():
    # Things that start with getting an id assigned/elements of seq
    def __init__(self, input_js, name=None, parent=None, root: Converter = None, size_eos=False, containing_type=None,
                 parsed_toplevel=False):
        self.subtrees = dict()
        self.input = input_js
        self.id = name
        self.this_level_keys = self.input.keys()
        self.type = None
        self.size = None
        self.parent = parent
        self.root = root
        self.parsed_toplevel = parsed_toplevel
        self.called_lowlevel = True
        if "size-eos" in self.input.keys():
            self.size_eos = True
        else:
            self.size_eos = False
        self.output = []
        self.front = []
        self.back = []
        self.containing_type = containing_type

    def parse(self):
        # if "type" in self.input.keys(): self.type = self.input["type"]
        # print_debug(f"INPUT TYPE {type(self.input)} cont {self.input}")
        if "type" in self.input.keys():
            local_type = self.input["type"]
            if "(" in local_type and False:
                self.type = local_type.split("(")[0]
            elif "::" in local_type and not "(" in local_type:
                self.type = local_type.split("::")[-1]
            else:
                self.type = local_type

        if "size" in self.input.keys(): self.size = self.input["size"]
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.subtrees[local_key] = attribute(local_key, self.input[this_level_key])

            # print(str(self.subtrees[local_key].get_name()) + " : " + str(self.subtrees[local_key].get_value()))
        if self.id is None:
            self.id = str(self.subtrees["id"].get_value())

    def generate_code(self, size=None, ignore_if=False, called_lowlevel=True, containing_type=None):
        if not called_lowlevel:
            self.called_lowlevel = False
            self.output.append(f"    local uint32 struct_start_CONVERTER = FTell();{gen_marker()}")
            self.output.append(f"    local uint32 length_CONVERTER = FileSize() - 1;{gen_marker()}")

        if not self.called_lowlevel:
            while_content = "!FEof()"
        else:
            while_content = "FTell() < UNTIL_CONVERTER"

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
                print_debug(self.subtrees.keys())
                # self.front.append("    while(FTell() < UNTIL_CONVERTER){")
                self.front.append("    while(" + while_content + "){ " + gen_marker())
                self.gen_atomic(indents=2, forwarding=True)
                self.front.append("    }")
            else:
                self.gen_atomic()

        if not ignore_if:
            self.output.extend(self.front)
        self.output.extend(self.back)
        return self.output

    def get_biggest_from_str_list(self, input):
        biggest = 0
        for entry in input:
            if int(entry) > biggest:
                biggest = int(entry)
        return biggest

    def gen_switch(self, size=None, is_local=False):
        if is_local:
            prefix = "local "
            # print_debug(f'subtrees {self.subtrees} self.type {self.type} front {self.front}')
        else:
            prefix = ""

        switch = self.type["switch-on"]
        cases = self.type["cases"]
        default_needed = True
        switch_over_enum = False
        num_of_switch_cases = len(cases.keys())
        do_endian_switch = False

        switch_drop = ["_root", "_parent", "_io"]
        if switch.split(".")[0] in switch_drop:
            switch_term = ".".join(switch.split(".")[1:])
        else:
            switch_term = switch
        ###INJECTION LOCAL VAR FOR START
        switch_term_instances = self.root.expr_resolve(switch_term)
        switch_term = self.root.expr_resolve(switch_term, translate_condition_2_c=True)
        print_debug(f" INSTANCES {switch_term_instances} in {self.containing_type} or {self.id}")
        self.gen_instances(switch_term_instances, containing_type=self.containing_type, from_list=True)
        bitfield_primer = False
        sizes = []
        type_prefix = ""
        for case_key in cases.keys():
            case = self.root.expr_resolve(case_key)
            if self.root.resolve_datatype(cases[case_key]):
                local_size = self.root.resolve_datatype(cases[case_key], getsize=True)
                if "int" in self.root.resolve_datatype(cases[case_key]) and sizes == []:
                    sizes.append(self.root.resolve_datatype(cases[case_key], getsize=True))
                elif "int" in self.root.resolve_datatype(cases[case_key]) and local_size not in sizes:
                    sizes.append(local_size)
                    bitfield_primer = True
                else:
                    pass
        # print_debug(f'Bitfield {cases}')
        if self.get_biggest_from_str_list(sizes) != 0:
            size_biggest = str(self.get_biggest_from_str_list(sizes) * 8)
            # print_debug(f"HHHHHHHHAAAAAAAA {size_biggest}")
        if bitfield_primer:
            self.front.append("    BitfieldDisablePadding();" + gen_marker())

        # TODO CAST SWITCHTERM TO INT OR MAKE SURE ALL LOCALS USED IN SWITCHES ARE int

        self.front.append("    switch(" + str(switch_term) + ") {" + gen_marker())
        first_index_front = len(self.front)
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
            if type(case) is bool or case == "true" or case == "false":
                self.front[first_index_front - 1] = '    switch(' + str(switch_term) + ') {' + gen_marker()
                case = f'{case}'
                default_needed = False
            if case == ["_"] or case == "_":
                default_needed = False
                case_val = "default"  # TODO remove case from case default
            elif type(case) is list:
                case_val = case[1]
            else:
                case_val = case

            if "(" in cases[case_key]:
                type_param_list = cases[case_key].replace("(", " ").replace(")", " ").split()
                cases[case_key] = type_param_list[0]
                param_addon = str(type_param_list[1::]).replace("'", "")[1:-1]
                # print_debug(param_addon)

            size_param_needed = self.root.lookup_type(cases[case_key], check_if_size_param_needed=True)
            custom_param = self.root.lookup_type(cases[case_key], check_if_custom_param_needed=True)

            if custom_param:
                print_debug("#TODO IMPLEMENT CUSTOM PARAMS FOR SWITCH!")
                exit(-1)

            if size_param_needed:
                if "size" in self.input.keys():
                    paramfield = "(" + str(self.input["size"]) + ")"
                else:
                    # print_debug("ERROR NO SIZE GIVE FOR PARAMETERIZED STRUCT INSTANTIATION (1):\n"+str(self.input))
                    # print_debug(self.root.global_type_table,pretty=True)
                    # print_debug(self.root.lookup_type(cases[case_key], check_if_param_needed=True))
                    # exit(-1)
                    paramfield = "(length_CONVERTER -(FTell()-struct_start_CONVERTER))"
            else:
                paramfield = ""
            if case_val != "default":
                self.front.append("        case " + str(case_val) + ":")
            else:
                default_needed = False
                self.front.append("        default:")
            if self.root.resolve_datatype(cases[case_key]):  # BASIC TYPE
                type_name = self.root.resolve_datatype(cases[case_key])
                if self.root.endian != self.root.resolve_datatype(cases[case_key], getendian=True):
                    do_endian_switch = True
            else:  # CUSTOM TYPE
                type_name = str(cases[case_key]) + "_TYPE "

            bitfiel_pad = ""
            if bitfield_primer:
                if "u" in type_name:
                    bitfiel_pad = f' : {type_name.replace("uint", "")}'
                    type_name = f'uint{size_biggest}'
                else:
                    bitfiel_pad = f' : {type_name.replace("int", "")}'
                    type_name = f'int{size_biggest}'

            self.switch_endian(self.root.resolve_datatype(cases[case_key], getendian=True), do_endian_switch)

            if "_TYPE" in type_name:
                prefix = " "
                # print_debug(f'GOT {type_name}')
            self.front.append(
                "            " + prefix + type_name + " " + str(self.id) + paramfield + f"{bitfiel_pad};{gen_marker()}")

            self.switch_endian(self.root.endian, do_endian_switch)
            self.front.append("            break;")

        if default_needed and "size" in self.input.keys():
            self.front.append("        default:")
            # self.output.append(f'    Warning("LENGTH %hu %hx",{str(self.input["size"])},{str(self.input["size"])});')
            default_size = self.input["size"]

            self.front.append(
                f"            {prefix}ubyte raw_data_CONVERTER[{gen_aligned_size(default_size)}];{gen_marker()}")
            self.front.append("            break;")
        elif default_needed and not switch_over_enum and not size and size_param_needed:
            self.front.append("        default:")
            self.front.append(
                f"            {prefix}ubyte raw_data_CONVERTER[length_CONVERTER -(FTell()-struct_start_CONVERTER)];{gen_marker()}")
            self.front.append("            break;")
        elif default_needed and not switch_over_enum and size:
            self.front.append("        default:")
            self.front.append(f"            {prefix}ubyte raw_data_CONVERTER[{size}];{gen_marker()}")
            self.front.append("            break;")
        elif default_needed:
            self.front.append("        default:")
            self.front.append("            break;")
            self.front.append("            if(!FEof()){")
            self.front.append(
                f'                Warning("UNSUPPLIED DEFAULT CASE FOR SWITCH OVER {switch_term}");{gen_marker()}')
            self.front.append("                return -1;")
            self.front.append("            }")
        if bitfield_primer:
            self.front.append("    BitfieldEnablePadding();" + gen_marker())

        self.front.append("    }")

    def switch_endian(self, endian, do_switch_endian=False):
        if do_switch_endian and endian is not None:
            if endian == "be":
                self.front.append(f"    BigEndian();{gen_marker()}")
            else:
                self.front.append(f"    LittleEndian();{gen_marker()}")

    def gen_if(self, containing_type=None):
        condition = self.input["if"]
        if "instances" in self.parent.parent.input.keys():
            pass
        possible_instances = self.root.expr_resolve(condition)
        if type(possible_instances) is not list:
            possible_instances = [possible_instances]
        # print_debug(f'Found possible {possible_instances} in {containing_type}')
        self.gen_instances(possible_instances, from_list=True, containing_type=containing_type)

        self.front.append(
            "    if (" + self.root.expr_resolve(condition, translate_condition_2_c=True) + ") {" + gen_marker())

        self.generate_code(ignore_if=True, containing_type=containing_type)

        self.front.append("    }")

    def gen_repeat(self, size=None):
        if not self.called_lowlevel:
            while_content = "!FEof()"
        else:
            while_content = "FTell() < UNTIL_CONVERTER"

        if "repeat-until" in self.this_level_keys:
            condition_in = self.input["repeat-until"]
            condition = self.root.expr_resolve(condition_in, translate_condition_2_c=True, repeat_condition=True,
                                               id_of_obj=self.id)
            # print_debug(condition)
            self.gen_instances(condition)
            # self.gen_atomic()
            self.front.append("    do{")
            self.gen_atomic(indents=2)
            self.front.append("    }while (!(" + condition + ")); " + gen_marker())
            # TODO CHECK IF DONE

        elif "repeat-expr" in self.this_level_keys:
            expr_in = self.input["repeat-expr"]
            expr = self.root.expr_resolve(expr_in, translate_condition_2_c=True)
            self.gen_instances(expr)
            for_length_needed = self.root.lookup_type(self.type, check_if_size_param_needed=True)
            for_custom_needed = self.root.lookup_type(self.type, check_if_custom_param_needed=True)
            if for_custom_needed or for_length_needed:
                self.front.append(f'    local int TILL_CONVERTER = ({expr});')
                self.front.append(f'    local int x_CONVERTER = 0;')
                self.front.append(f'    for(;x_CONVERTER < TILL_CONVERTER ;x_CONVERTER++)' + "{")
                # self.front.append(f'    for(int x_CONVERTER = 0;x_CONVERTER < TILL_CONVERTER ;x_CONVERTER++)' + "{")
                self.gen_atomic(indents=2)
                self.front.append('    }')
            else:
                self.gen_atomic(size=expr)
            pass
        elif "eos" == self.input["repeat"]:
            # self.front.append("    local uint32 UNTIL_CONVERTER = length_CONVERTER;") #TODO THIS IS OPTION B FOR EOS
            self.front.append("    while(" + while_content + "){" + f"{gen_marker()}")
            # self.front.append("    while(FTell() < UNTIL_CONVERTER){")
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
        if not self.called_lowlevel:
            while_content = "!FEof()"
        else:
            while_content = "FTell() < UNTIL_CONVERTER"

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
        self

        if self.size_eos and not forwarding and "length_CONVERTER" == size:

            # self.front.append("    while(" + while_content + "){ //AC" + f"{gen_marker()}")
            self.front.append("    do{")  # OPTION B
            # self.front.append("    while(FTell() < UNTIL_CONVERTER){")  # OPTION B
            self.gen_atomic(indents=2, forwarding=True)
            self.front.append("    }while(" + while_content + ");" + f"{gen_marker()}")
            # self.front.append("    }")  # OPTION B



        # TODO SWITCH BACK IF IT BREAKS
        # elif self.type == "str":
        elif self.type == "char" or self.type == "str":
            if self.size is not None:
                # TODO Done? IMPLEMENT CASE FOR DIFFERENT THAN ZEROBYTE TERMINATOR
                self.front.append(
                    prepend + "char " + str(self.id) + "[" + str(self.size) + "]" + f";{gen_marker()}" + loc_doc)
            elif "size-eos" in self.input:
                self.front.append(
                    prepend + "char " + str(
                        self.id) + f"[length_CONVERTER -(FTell()-struct_start_CONVERTER)];{gen_marker()}" + loc_doc)
        elif self.type == "strz":
            self.front.append(prepend + "string " + str(self.id) + f";{gen_marker()}" + loc_doc)
        elif self.type is not None:
            param_addon = ""
            temp_type = self.root.resolve_datatype(self.type)
            local_endian = f"{self.root.resolve_datatype(self.type, getendian=True)}"
            self.switch_endian(local_endian, local_endian != self.root.endian)

            if (temp_type is not None):  # BASIC TYPES
                if temp_type != "byte":
                    # print_debug(self.type)
                    # print_debug(temp_type)
                    self.front.append(
                        prepend + str(self.root.resolve_datatype(self.type)) + " " + str(
                            self.id) + f";{gen_marker()}" + loc_doc)
                else:
                    self.front.append(
                        prepend + str(self.root.resolve_datatype(self.type)) + " " + str(self.id) + "[" + str(
                            self.root.resolve_datatype(self.type, getsize=True)) + "]" + f";{gen_marker()}" + loc_doc)
                self.switch_endian(self.root.endian, local_endian != self.root.endian)
            # elif " " in str(self.type):
            #     print_debug(f"WENT HERE WITH{self.type}")
            #     self.type = self.root.expr_resolve(self.type, translate_condition_2_c=True)
            #     self.front.append(prepend + str(self.type) + " " + str(self.id) + ";" + loc_doc)

            else:  # CUSTOM TYPES

                if "instances" in self.parent.parent.input.keys():
                    # print_debug(self.type)
                    if "(" in self.type:
                        child_type = self.type.split("(")[0]
                    else:
                        child_type = self.type
                    if "_ENUM" not in self.type:
                        # print_debug(f'container {self.containing_type} child {child_type}')
                        this_lvl_instances = self.parent.parent.input["instances"].keys()
                        # print_debug(child_type)
                        temp_child = self.root.expr_resolve(child_type)

                        if type(temp_child) is list:
                            child_type = temp_child[-1]
                        else:
                            child_type = temp_child
                        lower_lvl_instances = self.get_lower_lvl_instances(
                            child_name=self.sanitize_type_name(child_type),
                            parent_name=self.containing_type,
                            parent_instances=this_lvl_instances)
                        if lower_lvl_instances:
                            # print_debug(f'Lower Level instances {lower_lvl_instances}')
                            self.gen_instances(lower_lvl_instances, from_list=True)

                if type_override is None and "_TYPE" not in self.type:
                    if "(" in self.type:
                        type_param_list = self.type.replace("(", "AAACONVERTER").replace(")", "AAACONVERTER").split(
                            "AAACONVERTER")[:-1]
                        self.type = type_param_list[0]
                        for i in range(len(type_param_list)):
                            type_param_list[i] = self.root.expr_resolve(type_param_list[i],
                                                                        translate_condition_2_c=True)
                        # print_debug(type_param_list)
                        param_addon = str(type_param_list[1::]).replace("'", "")[1:-1]

                    self.type = self.type + "_TYPE"
                length_addon = ""

                # print_debug(f'{self.type}@AAB')

                if "_ENUM" not in self.type and self.root.lookup_type(name=self.type.split("_TYPE")[0],
                                                                      check_if_size_param_needed=True):

                    try:
                        self.gen_instances(self.input["size"])
                    except:
                        pass
                    try:
                        length_addon = f'{self.root.expr_resolve(self.input["size"], translate_condition_2_c=True)}'
                    except:
                        if self.called_lowlevel:

                            # if param_addon != "":
                            #     param_addon = "," + param_addon
                            # length_addon = f"length_CONVERTER -(FTell()-struct_start_CONVERTER){param_addon}"
                            length_addon = f"length_CONVERTER -(FTell()-struct_start_CONVERTER)"
                        else:
                            # if param_addon != "":
                            #     param_addon = "," + param_addon
                            # length_addon = f"FileSize()-FTell(){param_addon}"
                            length_addon = f"FileSize()-FTell()"
                            pass
                        # loc_doc = "//TESTING"
                if size and param_addon == "":
                    length_addon = f"[{size}]"
                elif length_addon != "" and param_addon != "":
                    # print_debug(f'LENGTH_ADDON {length_addon} PARAM_ADDON {param_addon}')
                    length_addon = f'({length_addon},{param_addon})'
                elif length_addon != "" or param_addon != "":
                    # print_debug(f'LENGTH_ADDON {length_addon} PARAM_ADDON {param_addon}')
                    length_addon = f'({length_addon}{param_addon})'

                # print_debug(f'{self.type}|{length_addon}|{param_addon}|{self.size}')
                if size and length_addon != "" and param_addon != "":
                    self.front.append("    do{" + f"{gen_marker()}")
                    # self.front.append("    while(" + size + "){ //AD" + f"{gen_marker()}")

                # if length_addon
                if "_ENUM" in self.type and "type" in self.input.keys():
                    enum_size_local = self.root.lookup_enum_size(self.type.split("_ENUM")[0])
                    enum_size_actual = self.root.resolve_datatype(self.input["type"])
                    self.root.double_check_enum_size(self.type.split("_ENUM")[0], self.input["type"])
                    # print_debug(f'Got some sweet {self.type} of size {enum_size_local} vs actual {enum_size_actual} here!')

                self.front.append(
                    prepend + str(self.type) + " " + str(self.id) + length_addon + f";{gen_marker()}" + loc_doc)

                sanitized_name = self.sanitize_type_name(self.type)
                if sanitized_name:
                    if "seq" in self.root.input["types"][sanitized_name].keys():
                        type_kaitai = self.root.input["types"][sanitized_name]["seq"]
                    else:
                        type_kaitai = {}
                if (self.size or (self.size_eos and False)) and type_kaitai == EMPTY_STRUCT_FILLER:
                    if self.size:
                        if EMPTY_STRUCT_FILLER_FLAG:
                            skipper = f'{self.size} - 1'
                        else:
                            skipper = f'{self.size}'
                    elif self.size_eos:
                        skipper = "length_CONVERTER -(FTell()-struct_start_CONVERTER)"

                    self.front.append(f'    FSkip({skipper});' + gen_marker())

                if size and length_addon != "" and param_addon != "":
                    self.front.append("    }while(" + size + ")" + f"{gen_marker()}")
                    # self.front.append("        }")


        elif self.size is not None:  # JUST BYTES
            self.front.append(
                prepend + "ubyte " + str(self.id) + "[" + str(self.size) + "]" + f";{gen_marker()}" + loc_doc)

        else:
            # self.front.append(prepend + "byte " + str(self.id) + "[UNTIL_CONVERTER - FTell()]" + ";" + loc_doc)#OPTION A
            self.front.append(prepend + "ubyte " + str(self.id) + f";{gen_marker()}" + loc_doc)  # OPTION B

            # self.gen_repeat()
            # self.front.append("    local int64 UNTIL_CONVERTER = FTell() + length_CONVERTER;")
            # self.front.append("    while(FTell() < UNTIL_CONVERTER){")
            # self.gen_atomic(indents=2,)
            # self.front.append("    }")
            # print_debug("ERROR NO SIZE OR TYPE GIVEN AND ITS NO MAGIC")
            # print_debug(self.input)
            # self.front.append("//STUFF MISSING HERE @ NO MAGIC " + str(self.id) + "----" + str(self.input))
            # print_debug(self.front)

    def sanitize_type_name(self, type_name):
        if "_TYPE" in type_name:
            return type_name.split("_TYPE")[0]
        elif "_ENUM" in type_name:
            return None
        return type_name

    def get_lower_lvl_instances(self, child_name="", parent_name="", parent_instances=[]):
        needed_instances = []
        for instance in parent_instances:
            child_type_str = str(self.root.input["types"][child_name])
            if f"_parent.{instance}" in child_type_str and not self.root.lookup_instance(instance, parent_name,
                                                                                         check_if_implemented=True):
                # print_debug(f'FOUND _parent.{instance} in {child_type_str}!')
                needed_instances.append(instance)
        return needed_instances

    # Generates Instances from a condition string or from a list of instance names
    def gen_instances(self, condition, from_list=False, containing_type=None):
        # TODO CHECK FOR SPECIAL POSITION DEPENDENT INSTANCES
        # condition_list = condition.split(".")
        # print_debug(f'Before {condition}')
        if from_list and type(condition) is not list:
            condition = [condition]
        if not from_list:
            condition_list = self.root.expr_resolve(condition)
        else:
            condition_list = condition
        if type(condition_list) is not list:
            condition_list = [condition_list]

        if containing_type:
            container = containing_type
        elif self.containing_type is None:
            container = self.id
        else:
            container = self.containing_type

        for element in condition_list:
            # print_debug(f'ELEMENT {element}')
            instance = self.root.lookup_instance(element, container)
            is_implemented = self.root.lookup_instance(element, container, check_if_implemented=True)
            # print_debug(f"Condition Instance {element} is implemented : {is_implemented} with {instance} in {self.id} or {container}")
            if instance is not None and not is_implemented:
                # print_debug(f"Generating Instance {element}")
                self.gen_instance_full(instance, element, containing_type=container)
                self.root.mark_as_implemented("instance", element, value=True, containing_type=container)

    def gen_instance_full(self, instance_dict, name, containing_type=None):

        num_occurences = self.root.preprocessor.search_num_occurences(f'{name}')
        if num_occurences <= 1:
            # print_debug(f"Instance {name} occurs {num_occurences} Times")
            return

        if not (instance_dict is not None and not self.root.lookup_instance(name, containing_type,
                                                                            check_if_implemented=True)):
            print_debug(f"{name} already done")
            return
        inst_keys = instance_dict.keys()
        # print_debug(inst_keys)
        inst_if = instance_dict["if"] if "if" in inst_keys else None
        inst_pos = instance_dict["pos"] if "pos" in inst_keys else None
        inst_io = instance_dict["io"] if "io" in inst_keys else None
        inst_type = instance_dict["type"] if "type" in inst_keys else None
        inst_value = instance_dict["value"] if "value" in inst_keys else None
        inst_doc = instance_dict["doc"] if "doc" in inst_keys else None
        inst_size = instance_dict["size"] if "size" in inst_keys else None
        type_field = "ubyte"
        size_field = ""
        prefix_field = ""
        doc_field = "\n   //".join(inst_doc.split("\n")) if "doc" in inst_keys else ""
        # type_field=""

        if inst_if is not None:
            condition = self.root.expr_resolve(inst_if)
            # print_debug(f"condition {condition}")
            self.gen_instances(condition, type(condition) is list)

            self.front.append(
                f'    if({self.root.expr_resolve(inst_if, True)})' + "{" + f"{gen_marker()}")
        if inst_type is not None:
            if type(inst_type) is dict:
                switch = inst_type["switch-on"]
                switch_drop = ["_root", "_parent", "_io"]
                if switch.split(".")[0] in switch_drop:
                    switch_term = ".".join(switch.split(".")[1:])
                else:
                    switch_term = switch
                ###INJECTION LOCAL VAR FOR START
                switch_term_instances = self.root.expr_resolve(switch_term)
                self.gen_instances(switch_term_instances, containing_type=self.containing_type, from_list=True)

        if inst_pos is not None:

            self.front.append(f'        local int64 temp_CONVERTER = FTell();{gen_marker()}')
            if inst_io is not None:
                # print_debug(inst_io)
                start_of = self.root.expr_resolve(inst_io, translate_condition_2_c=True)
                if start_of:
                    start_point = f'startof( {start_of}[0] ) + '
                else:
                    start_point = ""
            else:
                start_point = ""
            self.front.append(f'        FSeek({start_point}{inst_pos} );{gen_marker()}')
            # self.front.append(f'        FSeek({start_point}{inst_pos} +1 );{gen_marker()}')
        #     print_debug(f'Found {name}')
        # else:
        #     print_debug(f'Found not {name} {inst_pos}')
        if inst_type is not None:
            if type(inst_type) is dict:
                # print_debug(f"HELP Instance {name} has switch Type {inst_type}")
                # print_debug(f"My Subtree contains {self.subtrees.keys()}")
                # print_debug(f'Front Before{len(self.front)}')

                temp_front = self.subtrees[name].front
                self.subtrees[name].front = self.front
                self.subtrees[name].gen_switch(is_local=True)
                self.subtrees[name].front = temp_front
                # print_debug(f'Front After {len(self.front)}')


            else:
                temp_type = self.root.resolve_datatype(instance_dict["type"])
                type_field = temp_type if temp_type else f'{instance_dict["type"]}_TYPE'

        if inst_size is not None:
            if "_TYPE" in type_field:
                # print_debug(f'Setting SIZE FIELD to ({inst_size})')
                size_field = f"({inst_size})"
            else:
                # print_debug(f'Setting SIZE FIELD to [{inst_size}]')
                size_field = f"[{inst_size}]"
        elif inst_type and self.root.lookup_type(instance_dict["type"], check_if_size_param_needed=True):
            size_field = f"(length_CONVERTER -(FTell()-struct_start_CONVERTER))"

        if inst_value is not None:
            c_value = self.root.expr_resolve(str(inst_value), translate_condition_2_c=True)
            possible_instances_pre = self.root.expr_resolve(inst_value)
            possible_instances = []
            for x in possible_instances_pre:
                if x != name:
                    possible_instances.append(x)
            # print_debug(f"Possible Instances {possible_instances} in {name} of {instance_dict} in {containing_type}")
            self.gen_instances(possible_instances, type(possible_instances) is list, containing_type)
            prefix_field = "local "

            if not inst_type and not self.root.lookup_instance(name, containing_type, check_if_implemented=True):

                type_field = self.root.infer_type_top(inst_value, containing_type)
                resolved_datatype = self.root.resolve_datatype(type_field)
                if_switch = False
                #########BASIC#TYPES###############
                if resolved_datatype:
                    type_field = resolved_datatype
                #########CUSTOM#TYPES#############
                elif self.root.lookup_type(type_field):
                    prefix_field = ""
                    if self.root.infer_type_top(inst_value, containing_type, check_if=True):
                        if_switch = True
                        self.front.extend(self.gen_instance_value_if(name, type_field, inst_value, containing_type))
                    type_field = f'{type_field}_TYPE'

                # print_debug(f'Inferred Type {type_field} form {inst_value}')
                if not if_switch:
                    self.front.append(
                        f"    {prefix_field}{type_field} {name} = ({c_value});{gen_marker()}{doc_field}")
        elif type(inst_type) is not dict:
            str_pattern = fr"{name}\.to_s"
            str_occurences = self.root.preprocessor.search_num_occurences(str_pattern, pattern_override=True)
            if str_occurences:
                # print_debug(f'FOUND {name} to be char')
                type_field = "char"

            self.front.append(
                f"    {prefix_field}{type_field} {name}{size_field};{gen_marker()}{doc_field}")
        else:
            self.front.append(f"//PLACEHOLDER {gen_marker()}")  # TODO CHECK IF UNUSED ELSECASE

        if inst_pos is not None:
            self.front.append(f'        FSeek(temp_CONVERTER); {gen_marker()}')
        if inst_if is not None:
            self.front.append("    }")
        self.root.mark_as_implemented("instance", name, containing_type, True)
        return

    def gen_instance_value_if(self, name, inst_type, value, containing_type, indent_index=2):  # RETURNS A LIST OF LINES
        output = []
        indents = indent_index * "    "
        LL_postfix = indent_index * "_L"
        if "?" in value and ":" in value:
            condition = value.split("?")[0]
            else_case = "".join(value.split(":")[-1])
            then_case = value.split(":" + else_case)[0].split("?")[1]

            condition_str = "\n".join(
                self.gen_instance_value_if(name, inst_type, condition, containing_type, indent_index + 1))[:-3]
            # print_debug(condition_str)
            then_str = "\n".join(
                self.gen_instance_value_if(name, inst_type, then_case, containing_type, indent_index + 1))
            else_str = "\n".join(
                self.gen_instance_value_if(name, inst_type, else_case, containing_type, indent_index + 1))
            output.append(f'{indents}if({condition_str}) ' + "{")
            output.append(then_str)
            output.append(indents + "} else {")
            output.append(else_str)
            output.append(indents + "}")
        else:
            # print_debug(value)
            type_field = self.root.infer_type_top(value, containing_type)
            resolved_datatype = self.root.resolve_datatype(type_field)
            # print_debug(f'GOT RESOLVED DATATYPE {resolved_datatype} from {type_field}')
            if resolved_datatype:
                output.append(value)
            else:
                param_field = ""
                recursion_level_type = containing_type
                if "." in value:
                    for element in value.split(".")[:-1]:
                        # print_debug(f'AAAAA{recursion_level_type}')
                        recursion_level_type = self.root.find_type_off_id(element.strip(), recursion_level_type)

                    ###THIS WILL BREAK IF THE PARAMS INCLUDE _parent or
                    # the data should be something like _parent.bla.blub
                    full_type = self.root.find_type_off_id(value.split(".")[-1], recursion_level_type, True)
                else:
                    full_type = self.root.find_type_off_id(value.strip(), recursion_level_type, True)
                # print_debug(f'Full Type {full_type}')
                param_field = "(" + full_type.split("(", 1)[1] if full_type else ""

                output.append(f'{indents}local int64 temp_CONVERTER{LL_postfix} = FTell();{gen_marker()}')
                output.append(f'{indents}FSeek(startof({value.strip()}));')
                output.append(f'{indents}{inst_type}_TYPE {name}{param_field};{gen_marker()}')
                output.append(f'{indents}FSeek(temp_CONVERTER{LL_postfix});')

        return output

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
            self.front.append("    ubyte " + str(self.id) + "[" + str(self.magic_len) + f"];{gen_marker()}")
            self.front.append("    if (" + self.id + "[0] != " + self.magic[0] + f" ||{gen_marker()}")
            for x in range(1, self.magic_len - 1):
                self.front.append("        " + self.id + "[" + str(x) + "] != " + self.magic[x] + " ||")
            self.front.append(
                "        " + self.id + "[" + str(self.magic_len - 1) + "] != " + self.magic[self.magic_len - 1] + ") {")
        else:
            self.front.append("    ubyte " + str(self.id) + f";{gen_marker()}")
            self.front.append("    if (" + self.id + " != " + self.magic[0] + ") {")
        self.front.append('        Warning("Magic Bytes of ' + self.id + f' not matching!");{gen_marker()}')
        self.front.append("        return -1;\n    };")

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

    def parse_subtree(self, name=None, parsed_toplevel=False):
        self.this_level_keys = []
        for data_dict in self.input:
            # if this_level_key == "doc-ref":this_level_key="doc"
            self.subtrees[data_dict["id"]] = data_point(data_dict, containing_type=name, parent=self, root=self.root,
                                                        parsed_toplevel=parsed_toplevel)
            self.subtrees[data_dict["id"]].parse()
            self.this_level_keys.append(data_dict["id"])

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        sizer_present = self.root.lookup_type(self.name, check_if_size_param_needed=True)
        if sizer_present:
            # if "length_CONVERTER" == size:
            # self.output.append("    local uint32 UNTIL_CONVERTER = FTell() + length_CONVERTER;") #TODO THIS IS OPTION A FOR EOS
            self.output.append(
                f"    local uint32 UNTIL_CONVERTER = FTell() + length_CONVERTER;{gen_marker()}")  # TODO THIS IS OPTION B FOR EOS
            # self.output.append('    Warning("LENGTH %hu UNTIL %hu FTell %hu",length_CONVERTER,UNTIL_CONVERTER,FTell());')

        for this_level_key in self.this_level_keys:
            # print_debug(f'{self.name} Called LowLevel = {called_lowlevel}')
            self.output.extend(
                self.subtrees[this_level_key].generate_code(size, called_lowlevel=called_lowlevel,
                                                            containing_type=self.name))

        return self.output


class instances(data_point):

    def __init__(self, input_js, parent, root, name=None):
        data_point.__init__(self, input_js, parent=parent, root=root, name=name)
        self.output = []
        self.front = []
        self.back = []
        self.name = name

    def parse_subtree(self, name=None):
        # print_debug(self.this_level_keys)
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                self.root.register_instance(local_key, self.input[local_key], containing_type=name)
                self.subtrees[local_key] = data_point(self.input[local_key], name=local_key, parent=self,
                                                      root=self.root)
                self.subtrees[local_key].parse()

    # def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
    def generate_code(self, size=None, ignore_if=False, called_lowlevel=True, containing_type=None):

        # print_debug(f"Generating Instance {self.name}")
        # print_debug(self.this_level_keys)
        for this_level_key in self.this_level_keys:
            instance = self.root.lookup_instance(this_level_key, containing_type=self.name)
            # print_debug(f'instance {instance}')
            if instance is not None and not self.root.lookup_instance(this_level_key, containing_type=self.name,
                                                                      check_if_implemented=True):
                num_occurences = self.root.preprocessor.search_num_occurences(this_level_key)
                # print_debug(f"Instance {this_level_key} occurs {num_occurences} Times")
                if num_occurences > 1:
                    self.gen_instance_full(instance, this_level_key, self.name)
                else:
                    pass
                    # print_debug(f"Instance {this_level_key} occurs {num_occurences} Times")
        self.output.extend(self.front)
        self.output.extend(self.back)
        return self.output


class types(Converter):
    def __init__(self, input_js, parent, root, name=None):
        Converter.__init__(self, input_js, parent=parent, root=root, name=name)
        # self.pre = {}
        self.pre = []
        self.output = []

    def sanitize_custom_params(self, param_list):
        out = {}
        for param in param_list:
            if "type" in param.keys():
                param_type = param["type"]
                if param_type in ["struct", "io", "any"]:
                    print_debug(f'CUSTOM PARAM {param["id"]} TYPE {param_type} NOT SUPPORTED!')
                    exit(-1)
                else:
                    out[param["id"]] = self.root.resolve_datatype(param_type)
            else:
                print_debug(f'CUSTOM PARAM {param["id"]} WITHOUT TYPE NOT SUPPORTED!')
                exit(-1)
        return out

    def parse_subtree(self, name=None):
        global EMPTY_STRUCT_FILLER
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                sanitized_params = None
                ##### ADDING PLACEHOLDER TO EMPTY STRUCTS###############
                if "seq" not in self.input[this_level_key].keys() and EMPTY_STRUCT_FILLER_FLAG:
                    self.input[this_level_key]["seq"] = [{"id": "MISSING_SEQ_CONVERTER_BYTES", "type": "u1"}]
                    EMPTY_STRUCT_FILLER = [{"id": "MISSING_SEQ_CONVERTER_BYTES", "type": "u1"}]
                    # print_debug(f'GOTCHA {local_key} at {self.input[this_level_key]}')
                ########################################################

                if "params" in self.input[local_key]:
                    sanitized_params = self.sanitize_custom_params(self.input[local_key]["params"])
                # print_debug(f'NAME {local_key} VALUE {self.input[local_key]} ')
                self.root.register_type(name=local_key, value=self.input[local_key],
                                        custom_param_needed=sanitized_params)
                self.subtrees[local_key] = Converter(self.input[this_level_key], parent=self, root=self.root,
                                                     name=local_key)
                self.subtrees[local_key].parse_subtree(name=local_key)
        self.parse_arguments_main()

    def parse_arguments_main(self):
        for this_level_key in self.this_level_keys:
            local_key = remap_keys(this_level_key)
            if local_key is not None:
                # print_debug(f'>>>>Checking {local_key}')
                if self.parse_arguments_recursion(self.subtrees[local_key], origin_type=local_key, depth=0):
                    # print_debug(f'<<<<{local_key} got PARAM')
                    self.root.register_type(name=local_key, size_param_needed=True)

    def parse_arguments_recursion(self, item, origin_type=None, depth=0,
                                  exclusion_list=[]):  # returns True if param is needed in subtree
        # print_debug(f'ITEM {item.name} Origin Type {origin_type} Depth {depth}')
        if depth > 5:
            print_debug(f"Parse_args_rec ITEM {item.name} Origin Type {origin_type}")
            # print_debug(item.input)
            already_known = self.root.lookup_type(origin_type, check_if_size_param_needed=True)
            if already_known:
                print_debug(f'===={origin_type} already known to need SIZE')
            return True

        already_known = self.root.lookup_type(origin_type, check_if_size_param_needed=True)
        if already_known:
            return True
            # print_debug(f'====={origin_type} already known to need SIZE')

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
            # print_debug(f"THIS {item.name} needs param!")
            return param_needed
        primer = False
        # print_debug(f'Entering Recursion for item {item.input}')
        included_types = []
        exclusion_list = []
        hit = item.chck_flg("type", flag_to_val=True, excluded_values=exclusion_list)
        while hit is not None:
            # print_debug(f'Hit {hit} Exclude {exclusion_list}')
            exclusion_list.append(str(hit))
            if "(" in hit:
                hit = hit.split("(")[0]
                # print_debug(hit)
                # primer = True
            # print_debug(f'Hit {hit} Resolved Hits {hit_list} actl {item.chck_flg("type", flag_to_val=True)} from {self.this_level_keys}')
            if type(hit) is dict:
                hit_list = self.root.resolve_switch(hit)
            else:
                hit_list = [self.root.expr_resolve(hit)]
            for hitter in hit_list:
                if hitter in list(self.this_level_keys) and not hitter in included_types:
                    included_types.append(hitter)
            hit = item.chck_flg("type", flag_to_val=True, excluded_values=exclusion_list)

        order_switch = depth / 2 == 0  # IMPORTANT PERFORMANCE INCREASE

        if included_types == []:  # LOWEST LATER // No SUBTYPES
            return False
        else:
            for sub_type in (included_types if order_switch else included_types[::-1]):
                lower_level_type = self.subtrees[sub_type]
                # print_debug(f'LLTYPE {lower_level_type.name} orig {origin_type}')
                if self.root.lookup_type(sub_type, check_if_size_param_needed=True):
                    if not self.check_if_flag_present(sub_type, item.input["seq"]):
                        param_needed = True
                        # print_debug(f'Type {sub_type} needs {param_needed}')
                        break
                elif self.parse_arguments_recursion(lower_level_type, item.name, depth + 1):
                    if not self.check_if_flag_present(sub_type, item.input["seq"]):
                        param_needed = True
                        break
            return param_needed

    # RETURNS TRUE IF flag isnt within every occurrence of type
    def check_if_flag_present(self, type_name, kaitai):
        for id_obj in kaitai:
            if "type" in id_obj.keys():
                if id_obj["type"] == type_name:
                    if "size" in id_obj.keys():
                        if id_obj["size"] != "eos":
                            return True
                    elif "repeat" in id_obj.keys():
                        if id_obj["repeat"] != "eos":
                            return True
                    else:
                        return False
        return False

    def generate_code(self, size=None, called_lowlevel=True, containing_type=None):
        self.output.extend(self.gen_complete_types(size))
        self.pre.extend(self.output)
        return self.pre

    def gen_complete_types(self, size=None):
        output = []
        for this_level_key in self.this_level_keys:
            custom_local_params = []
            lenfield = ""
            lencontent = ""
            size_param_needed = self.root.lookup_type(this_level_key, check_if_size_param_needed=True)
            custom_param = self.root.lookup_type(this_level_key, check_if_custom_param_needed=True)
            # print_debug(f'{this_level_key}   {size_param_needed}  {custom_param}')
            if size_param_needed:
                lenfield = "("
                lencontent = "uint32 length_CONVERTER"
            if custom_param:
                cust_cont = ""
                for cust_name in custom_param.keys():
                    cust_type = custom_param[cust_name]
                    cust_cont += f'{cust_type} {cust_name}_CONVERTER,'
                    custom_local_params.append(
                        f'    local {cust_type} {cust_name} = ({cust_type}){cust_name}_CONVERTER;{gen_marker()}')
                    # f'    local {cust_type} {cust_name}_CONVERTER = ({cust_type}){cust_name};{gen_marker()}')
                    # custom_local_params.append(f'    local {cust_type} {cust_name}_CONVERTER = {cust_type}({cust_name});{gen_marker()}')
                cust_cont = cust_cont[0:-1]
                # print_debug(custom_local_params)

            if lenfield != "":
                lenfield += lencontent
                if custom_param:
                    lenfield += "," + cust_cont + ")"
                else:
                    lenfield += ")"
            elif custom_param:
                lenfield = f'({cust_cont})'

            item = self.subtrees[this_level_key]

            if lenfield != "":
                forward_lenfield = lenfield + "{}"
            else:
                forward_lenfield = ""


            ##############WIP FORWARD DECLARATION RESTRUCTURE################
            self.pre.append("struct " + str(this_level_key) + "_TYPE" + forward_lenfield + f";{gen_marker()}")
            ##############WIP FORWARD DECLARATION RESTRUCTURE################
            output.append("struct " + str(this_level_key) + "_TYPE" + lenfield + " {" + gen_marker())
            if lenfield != "" or True:
                output.append(f"    local uint32 struct_start_CONVERTER = FTell();{gen_marker()}")
            if lenfield != "":
                sizer = "length_CONVERTER"
            else:
                sizer = None
            for custom_local_param in custom_local_params:
                pass
                # TODO UNCOMMENT IN ORDER TO GENERATE local vars of parameters
                output.append(custom_local_param)

            # if "seq" not in item.input.keys():
            #     item.input["seq"]={"id":"MISSING_SEQ_CONVERTER_BYTES","type":"u1"}

            output.extend(item.generate_code(sizer, called_lowlevel=True))  # GOING TO CHILD ITEM
            output.append("};\n")
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


def insert_imports_top(kaitaijs_main, imports, filepath):
    out = insert_imports(kaitaijs_main, imports, filepath)
    return out


def insert_imports(main_input, imports, path):
    # TODO INCLUDE ENDIANESS IN IMPORTED TYPES
    Converter_Loc = os.path.dirname(os.path.abspath(__file__))
    kaitai_base = f'{Converter_Loc}/../kaitai_struct_formats'
    # print_debug(kaitai_base)
    out = main_input
    next_imports = []
    for imp in imports:
        if imp in imported.keys():
            continue
        imported_kaitai = None
        try:
            with open(f'{path}/{imp}.ksy', "r") as in_file:
                input_file = in_file.read()
                print_debug(f"imported {imp}")
            imported_kaitai = yaml.load(input_file)
        except:
            try:
                with open(f'{kaitai_base}/{imp}.ksy', "r") as in_file:
                    input_file = in_file.read()
                    print_debug(f"imported {imp}")

                imported_kaitai = yaml.load(input_file)
            except:
                print_debug(f'{imp} import not found @ {path}/{imp}.ksy')
                exit(-1)
        try:
            imported_types = imported_kaitai["types"]
            for imp_type in imported_types.keys():
                if imp_type in out["types"].keys():
                    print_debug(f'Not inserting Type {imp_type}')
                    pass
                    # print_debug("AHH FUCK")
                    # print_debug(out["types"][imp_type],True)
                    # print_debug(imported_types[imp_type],True)
                else:
                    out["types"][imp_type] = imported_types[imp_type]
        except:
            print_debug(traceback.format_exc())
            print_debug("types didnt work")
            pass

        try:
            import_dict = {}
            import_dict["seq"] = imported_kaitai["seq"]
            if "instances" in imported_kaitai.keys():
                import_dict["instances"] = imported_kaitai["instances"]
            # imported_main_seq = imported_kaitai["seq"]
            out["types"][imported_kaitai["meta"]["id"]] = import_dict
        except:
            # print_debug(traceback.format_exc())
            # print_debug("main seq didnt work")
            pass
        try:
            imported_main_params = imported_kaitai["params"]
            out["types"][imported_kaitai["meta"]["id"]]["params"] = imported_main_params
        except:
            # traceback.print_exc()
            # print_debug("no params")
            pass

        try:
            imported_enums = imported_kaitai["enums"]
            for imp_enum in imported_enums.keys():
                if imp_enum not in out["enums"].keys():
                    out["enums"][imp_enum] = imported_enums[imp_enum]
                elif len(imported_enums[imp_enum]) > len(out["enums"][imp_enum]):
                    out["enums"][imp_enum] = imported_enums[imp_enum]
                else:
                    print_debug(f'Not inserting ENUM {imp_enum}')
        except:
            # print_debug("No Enums Imported")
            pass
        if "imports" in imported_kaitai["meta"]:
            next_imports += imported_kaitai["meta"]["imports"]
        imported[imp] = True

    if next_imports != []:
        out = insert_imports(out, next_imports, path)

    return out


def kaitai_sorter_main(input_kaitai):
    top_level_types = list(input_kaitai["types"].keys())
    for top_level_type in top_level_types:
        kaitai_sorter_recursive(input_kaitai, ["types", top_level_type], [top_level_type])


def kaitai_sorter_recursive(input_kaitai, path_list, type_list):
    this_level_keys = list(get_by_path(input_kaitai, path_list).keys())

    if "enums" in this_level_keys:
        enum_list = list(get_by_path(input_kaitai, path_list + ["enums"]).keys())
        for enum_unit in enum_list:
            if "enums" not in input_kaitai.keys():
                input_kaitai["enums"] = {}
            if enum_unit not in get_by_path(input_kaitai, ["enums"]).keys():

                set_by_path(input_kaitai, ["enums", enum_unit],
                            get_by_path(input_kaitai, path_list + ["enums", enum_unit]))
                del_by_path(input_kaitai, path_list + ["enums", enum_unit])
            else:
                print_debug(f'ERROR DOUBLE ENUMS WITH SAME NAME')
                exit(-1)
    # print_debug(get_by_path(input_kaitai, path_list[:-2]), pretty=True)
    if "types" in this_level_keys:
        this_level_types = list(get_by_path(input_kaitai, path_list + ["types"]).keys())

        for this_level_type in this_level_types:
            new_type_name = "_".join(type_list + [this_level_type])

            if "seq" in this_level_keys:
                # set_by_path(input_kaitai, path_list + ["seq"],list_replace_value(get_by_path(input_kaitai, path_list + ["seq"]), this_level_type, new_type_name))
                lower_path = path_list + ["seq"]
                lower_list = get_by_path(input_kaitai, lower_path)
                replacement = list_replace_value(lower_list, this_level_type, new_type_name)
                set_by_path(input_kaitai, lower_path, replacement)

            if "instances" in this_level_keys:
                lower_path = path_list + ["instances"]
                lower_dict = get_by_path(input_kaitai, lower_path)
                replacement = dict_replace_value(lower_dict, this_level_type, new_type_name)
                set_by_path(input_kaitai, lower_path, replacement)

            for to_be_modded_type in this_level_types:

                lower_lvl_keys = list(get_by_path(input_kaitai, path_list + ["types", to_be_modded_type]).keys())
                # MODDING LOWER LEVEL SEQ
                if "seq" in lower_lvl_keys:
                    lower_path = path_list + ["types", to_be_modded_type, "seq"]
                    lower_list = get_by_path(input_kaitai, lower_path)
                    replacement = list_replace_value(lower_list, this_level_type, new_type_name)
                    set_by_path(input_kaitai, lower_path, replacement)

                # MODDING LOWER LEVEL INSTANCES
                if "instances" in lower_lvl_keys:
                    lower_path = path_list + ["types", to_be_modded_type, "instances"]
                    lower_dict = get_by_path(input_kaitai, lower_path)
                    replacement = dict_replace_value(lower_dict, this_level_type, new_type_name)
                    set_by_path(input_kaitai, lower_path, replacement)

        #############RECURSION############################
        for this_level_type in this_level_types:
            kaitai_sorter_recursive(input_kaitai, path_list + ["types", this_level_type], type_list + [this_level_type])
        ##################################################

        ###############PULL-UP###########################
        for this_level_type in this_level_types:
            new_type_name = "_".join(type_list + [this_level_type])
            if new_type_name not in get_by_path(input_kaitai, ["types"]).keys():
                set_by_path(input_kaitai, ["types", new_type_name],
                            get_by_path(input_kaitai, path_list + ["types", this_level_type]))
                del_by_path(input_kaitai, path_list + ["types", this_level_type])
            else:
                print_debug(f'NEW TYPE{new_type_name} ALREADY IN TOP LEVEL TYPES!')
                exit(-1)
        # print_debug(f'deleting {path_list + ["types"]}')
        del_by_path(input_kaitai, path_list + ["types"])
        ##################################################


############STACKOVERFLOW-SECTION##################
def dict_replace_value(d, old, new):
    x = {}
    for k, v in d.items():
        # print_debug(type(v))
        # print_debug(v)
        if isinstance(v, dict):
            v = dict_replace_value(v, old, new)
        elif isinstance(v, list):
            v = list_replace_value(v, old, new)
        elif isinstance(v, str):
            if v == old:
                # print_debug(f"REPLACING >{old}< with >{new}< in >{v}<")
                v = v.replace(old, new)
            elif f' {old} ' in v:
                # TODO ADD space|old|space and stringstart|old|space
                # print_debug(f"REPLACING > {old} < with > {new} < in >{v}<")
                v = v.replace(f' {old} ', f' {new} ')
            elif f'{old} ' in v:
                # print_debug(f"REPLACING >{old} < with >{new} < in >{v}<")
                v = v.replace(f'{old} ', f'{new} ')
            else:
                # print_debug(f"Nothing in >{v}< to be replaced with >{new}<")
                pass
        x[k] = v
    return x


def list_replace_value(l, old, new):
    x = []
    for e in l:
        # print_debug(type(e))
        # print_debug(e)
        if isinstance(e, list):
            e = list_replace_value(e, old, new)
        elif isinstance(e, dict):
            e = dict_replace_value(e, old, new)
        elif isinstance(e, str):
            if e == old:
                # print_debug(f"REPLACING >{old}< with >{new}< in >{e}<")
                e = e.replace(old, new)
            elif f' {old} ' in e:
                # TODO ADD space|old|space and stringstart|old|space
                # print_debug(f"REPLACING > {old} < with > {new} < in >{e}<")
                e = e.replace(f' {old} ', f' {new} ')
            elif f'{old} ' in e:
                # print_debug(f"REPLACING >{old} < with >{new} < in >{e}<")
                e = e.replace(f'{old} ', f'{new} ')
            else:
                # print_debug(f"Nothing in >{old}< to be replaced with >{new}<")
                pass
        x.append(e)
    return x


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


def del_by_path(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]


def gen_marker():
    if GENERATION_MARKER:
        caller = getframeinfo(stack()[1][0])
        return f'//{caller.lineno}'
    else:
        return ""


##########################################################################

def gen_aligned_size(size_var):
    if ALIGN is not None:
        return f"{size_var} + {size_var} % {ALIGN}"
    else:
        return f"{size_var}"


# TODO HANDLE 0b0012.... (bmp.ksy)

class Preprocessor():
    def __init__(self, input_string, kaitaijs):
        self.input = input_string
        self.kaitai = kaitaijs
        self.types = kaitaijs["types"].keys()
        self.enums = kaitaijs["enums"].keys()
        # self.types = kaitaijs["types"].keys()

    def search_num_occurences(self, target, area=None, pattern_override=False):
        if area is None:
            area = self.input
        if not pattern_override:
            pattern = fr'\W{target}'
        else:
            pattern = fr'{target}'
        times = len(re.findall(pattern, area))
        return times

    def get_ENUM_from_entry(self, entry):
        out = []
        for enum_name in self.enums:
            for key, value in self.kaitai["enums"][enum_name].items():
                if entry == value:
                    out.append(enum_name)
        return out

    def preproccess(self):
        pattern_types = r"(?=(" + '|'.join(self.types) + r"))"
        pattern_enums = r"(?=(" + '|'.join(self.enums) + r"))"
        pattern_enum_sub = r"(?P<parsed_enum>(" + '|'.join(self.enums) + r"))[:]{2}(?P<subenum>[\w]+)"
        pattern_enum_sub_stupid = r"[\W]+(?P<parsed_enum>(" + '|'.join(
            self.enums) + r"))[:]{2}(?P<subenum>[\w]+): (?P<subenum2>[\w]+)"

        pattern_type_sub = r"(?P<parsed_type>(" + '|'.join(self.types) + r"))[:]{2}(?P<subtype>(" + '|'.join(
            self.types) + r"))"
        # pattern_enum_access=
        lines = self.input.split("\n")
        alpha_num_char = "[a-zA-Z0-9]"
        var_name = "^[_a-zA-Z0-9]\w+"
        var_name = "^(?![0-9]+)(?!0b[0-9]+)[_a-zA-Z0-9]\w+"
        pattern_to_s = r"(?P<object>((?![0-9]+)(?!0b[0-9]+)[_a-zA-Z0-9]\w+\.)*)to_s"
        pattern_sizeof = r"(?P<object>((?![0-9]+)(?!0b[0-9]+)[_a-zA-Z0-9]\w+\.)*)_sizeof"
        pattern_size = r"(?P<object>((?![0-9]+)(?!0b[0-9]+)[_a-zA-Z0-9]\w+\.)+)size"
        pattern_bitstring = "(?P<bitstring>0b[01_]+)"
        # var_name=fr'[a-zA-Z0-9]+|\w+'

        # REPLACEMENT PREROLLER
        replacement_dict = {}
        for enum_name in self.enums:
            for key, entry in self.kaitai["enums"][enum_name].items():
                if type(entry) == dict:
                    entry = entry["id"]
                    # print_debug(f'{entry}')
                    # exit(-1)
                if entry not in replacement_dict.keys():
                    replacement_dict[entry] = f'{entry}_{enum_name}_ENUM'
                else:
                    if type(replacement_dict[entry]) is list:
                        replacement_dict[entry].append(f'{entry}_{enum_name}_ENUM')
                    else:
                        replacement_dict[entry] = [replacement_dict[entry], f'{entry}_{enum_name}_ENUM']
                    # print_debug(f'AAAHHHHH {entry} in {enum_name} but already {replacement_dict[entry]}')

        # REPLACEMENT PHASE
        for index_l in range(len(lines)):
            line = lines[index_l]
            words = line.split()
            words_before = line.split()
            # print_debug(f'Proc LINE >{line}<')
            for index in range(len(words)):
                # for word in words:
                word = words[index]
                # print(word)

                # HANDLING enum_ENUM::monday
                match = re.match(pattern_enum_sub, word)
                if match is not None:
                    subenum = match.group('subenum')
                    parsed_enum = match.group('parsed_enum')
                    words[index] = words[index].replace(f'{parsed_enum}::{subenum}',
                                                        f'{subenum}_{parsed_enum}_ENUM')  # ENUM REPLACEMENT
                    # lines[index] = lines[index].replace(f'{parsed_enum}::{subenum}', f'{subenum}')
                    # print(f'Found ENUM {parsed_enum} with {subenum} in {word}')
                elif word in replacement_dict.keys() and "doc:" not in line and "doc-ref:" not in line and "id:" not in line:
                    rep = replacement_dict[word]
                    if type(rep) is list:
                        pass
                        # TODO CHECK IF BROKEN
                        # WHAT THIS CASE SHOULD CATCH :
                        # Enum entries of the same name in different ENUMS
                        # EXPECTED BEHAVIOUR : NO ISSUE CAUSE NAMES ARE CHANGED LATER TOO (here and in gen)

                        # print_debug(f"OH No")
                        # print_debug(f'Found possible enum {word} in line {line}')
                    else:
                        # Handling stupid cases of          block_type::extension: extension

                        match = re.match(pattern_enum_sub_stupid, line)
                        if match is not None:
                            subenum = match.group('subenum')
                            subenum2 = match.group('subenum2')
                            parsed_enum = match.group('parsed_enum')

                            if subenum == subenum2:
                                pass
                            else:
                                print_debug(f'Found possible enum {word} in line {line}')
                                words[index] = words[index].replace(f'{word}', f'{rep}')
                        else:
                            words[index] = words[index].replace(f'{word}', f'{rep}')

                # HANDLING imported_type::subtype
                match = re.match(pattern_type_sub, word)
                if match is not None:
                    subtype = match.group('subtype')
                    parsed_type = match.group('parsed_type')
                    # print(f'Found TYPE {parsed_type} with {subtype} in {word}')
                    words[index] = words[index].replace(f'{parsed_type}::{subtype}', f'{subtype}')

                # HANDLING .to_i
                if ".to_i" in word:
                    words[index] = words[index].replace(".to_i", "")

                # HANDLING .to_s
                match = re.match(pattern_to_s, word)
                if match is not None:
                    object_ = match.group('object')
                    # words[index] = words[index].replace(f'{object_}to_s', f'{object_[:-1]}')
                    words[index] = words[index].replace(f'{object_}to_s', f'Str( {object_[:-1]} )')

                # HANDLING _sizeof
                match = re.match(pattern_sizeof, word)
                if match is not None:
                    object_ = match.group('object')
                    words[index] = words[index].replace(f'{object_}_sizeof', f'sizeof( {object_[:-1]} )')

                # HANDLING size
                match = re.match(pattern_size, word)
                if match is not None:
                    object_ = match.group('object')
                    lines[index_l] = lines[index_l].replace(f'{object_}size ', f'{object_[:-1]}.array_size ')
                    # lines[index_l] = lines[index_l].replace(f'{object_}size ', f'sizeof({object_[:-1]}) ')
                    # words[index] = words[index].replace(f'{object_}size ', f'sizeof({object_[:-1]}) ')

                # HANDLING 0b0000...
                match = re.match(pattern_bitstring, word)
                if match is not None:
                    bitstring = match.group('bitstring')
                    bits = bitstring[2::].replace("_", "")
                    bit_len = len(bits)
                    bit_value = int(bits, 2)
                    words[index] = words[index].replace(bitstring, str(hex(bit_value)))
                    # print(f"changes to {lines[index]}")
            # print_debug(f'Replacing >{" ".join(words_before)}< with >{" ".join(words)}<')
            lines[index_l] = lines[index_l].replace(" ".join(words_before), " ".join(words))
            # print_debug(f'Changed To>{lines[index_l]}<')
        return "\n".join(lines)


def main():
    global converter, DEBUG, ALIGN, format_name

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("USAGE = python3 Converter.py <input file path> <output file path> [<alignment #byte>]")  # TODO
        exit(1)
    if len(sys.argv) == 4:
        ALIGN = sys.argv[3]
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    ########## MANUAL ALIGNEMENT OVERRIDE#################
    if len(sys.argv) != 4 and True:
        align_dict = {"avi": 2, "bmp": 4}
        format_name = os.path.basename(output_file_name).split(".")[0]
        if format_name in align_dict.keys():
            ALIGN = align_dict[format_name]

    #####################################################
    with open(input_file_name, "r") as in_file:
        input_file = in_file.read()

    kaitaijs_main = yaml.safe_load(input_file)

    try:
        imports = kaitaijs_main["meta"]["imports"]
        # print_debug(imports)
        # print_debug(input_file_name)
        filepath = os.path.dirname(os.path.abspath(input_file_name))
        # print_debug(filepath)
        out = insert_imports_top(kaitaijs_main, imports, filepath)
    except:
        # print_debug(traceback.format_exc())
        out = kaitaijs_main

    try:
        tl_keys = ["seq", "instances"]
        out["types"][f'{format_name}_CONVERTER'] = {}
        for key in tl_keys:
            if key in out.keys():
                out["types"][f'{format_name}_CONVERTER'][key] = out[key]
        # out["types"][f'{format_name}_CONVERTER']["params"] = [{"id": "length", "type": "u4"}]
        out["seq"] = [{"id": f"{format_name}", "type": f"{format_name}_CONVERTER"}]
        # out["seq"] = [{"id": f"{format_name}", "type": f"{format_name}_CONVERTER(length_CONVERTER)"}]
    except:
        print_debug(traceback.format_exc())

    kaitaijs = out
    # kaitaijs = kaitaijs_main
    kaitai_sorter_main(kaitaijs)

    sorted_string = yaml.dump(kaitaijs)
    preproc = Preprocessor(sorted_string, kaitaijs)
    kaitaijs_proc = yaml.safe_load(preproc.preproccess())
    # exit(-1)

    converter = Converter(kaitaijs_proc, True, preprocessor=preproc)
    # converter = Converter(kaitaijs, True,preprocessor = preproc)
    output = converter.generate_code_toplevel()
    outFolder = os.path.dirname(os.path.abspath(output_file_name))
    # print_debug(f'{outFolder}/intermediate_{os.path.basename(output_file_name).split(".")[0]}.ksy')
    with open(f'{outFolder}/intermediate_{os.path.basename(output_file_name).split(".")[0]}.ksy', "w+") as out_file:
        out_file.write(yaml.dump(kaitaijs_proc))

    with open(output_file_name, "w+") as out_file:
        out_file.write('\n'.join(output))

    # print('\n'.join(output))


if __name__ == "__main__":
    main()
