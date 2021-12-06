import cfile as C
import sys
import yaml



def main():
    if len(sys.argv)!=3:
        print("USAGE = python3 Converter.py <input file path> <output file path>")#TODO
        exit(1)
    input_file_name=sys.argv[1]
    output_file_name=sys.argv[2]
    with open(input_file_name,"r") as in_file:
        input_file=in_file.read()
    kaitaijs=yaml.load(input_file)
    types=kaitaijs["types"].keys()
    print(types)







if __name__ == "__main__":
    main()