import cfile as C
import sys
import yaml



datatypes={"u4":"uint32","u1":"ubyte","u2":"uint16"} #TODO implement all types


def main():
    if len(sys.argv)!=3:
        print("USAGE = python3 Converter.py <input file path> <output file path>")#TODO
        exit(1)
    input_file_name=sys.argv[1]
    output_file_name=sys.argv[2]
    with open(input_file_name,"r") as in_file:
        input_file=in_file.read()
    kaitaijs=yaml.load(input_file)
    types=kaitaijs["types"]
    enums=kaitaijs["enums"]
    print(kaitaijs)
    lines=[]
    lines.extend(gen_enums(enums))
    lines.extend(gen_types(types))
    with open(output_file_name,"w") as out_file:
        out_file.write('\n'.join(lines))

    print('\n'.join(lines))


def gen_enums(enums):
    lines=[]
    for enum_key in enums.keys():
        lines.extend(gen_single_enum(enum_key,enums[enum_key]))
        lines.append("\n")
    return lines

def gen_single_enum(key, values):
    lines = []
    #TODO FIND CORRECT TYPE? defaulting to <byte> for now
    size = "<byte>"
    lines.append("typedef enum " + size +" " + key + " {")
    keys = list(values.keys())
    for k in keys[0:-1]:
        lines.append("  " + (values[k] if "id" not in values[k] else values[k]["id"]) + " = " + str(k) + "," + ("" if "doc" not in values[k] else "  // " + (values[k]["doc"]).replace("\n", " ")))
    lines.append("  " + (values[keys[-1]] if "id" not in values[keys[-1]] else values[keys[-1]]["id"]) + " = " + str(keys[-1]) + "" + ("" if "doc" not in values[keys[-1]] else "  // " + (values[keys[-1]]["doc"]).replace("\n", " ")))
    lines.append("} " + str(key).upper() + ";")
    return lines

def gen_types(types):
    lines = []
    #TODO implement dependency aware type generation
    for key in types.keys():
        lines.extend(gen_single_simple_type(key,types[key]))
        lines.append("\n")
    return lines

def gen_single_simple_type(key, values):
    #TODO only doing simple structs for now
    lines = []
    lines.append("typedef struct {")
    keys = list(values.keys())
    #print(keys)
    for k in keys:
        if "doc" in k:
            lines.append("  // "+values[k].replace("\n", " "))
    for item in values["seq"]:
        #print(item)
        if "type" not in item.keys():
            if "size" not in item.keys():
                print("FAILURE AT FINDING TYPE\nKEYS = "+str(item.keys()))
                continue
            local_type="size"
        else:
            local_type="type"
        if type(item[local_type]) is str or type(item[local_type]) is int:
            lines.append("  "+gen_simple_var_creation(item[local_type],item["id"])+(""if "doc" not in item.keys() else"     //"+item["doc"]).replace("\n", " "))
        else:
            print("type not supported yet,skipping @ "+str(item[local_type].keys()))



    lines.append("} "+str(key).upper()+";")
    return lines
def gen_simple_var_creation(typ,name,content=None):  #TODO Refactor name
    type = typ if typ not in datatypes.keys() else datatypes[typ]
    lines=("  "+(str(type).upper() if type==typ else str(type))+" "+str(name).lower())
    if content is None:
        pass
    else:
        print("COMPLEX VARS not YET supported!\n") #TODO implement
    lines+=";"
    return lines

def gen_switch():
    lines=[]
    return lines
if __name__ == "__main__":
    main()