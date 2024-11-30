import json
import os
import ast
import pandas as pd

directory = "data"

# sample data to store
main = []

# full set alteryx data to store as list
full_main = []

# current working directory
cwd = os.getcwd()

# directories to scan for .py file to get data.
actuall_dirs = ["core", 'lib']

# change this path based on your framework repo location. path to python modules for search.
fw_path = ""


def get_avail_funcs_from_dirs():
    total = 0
    for ddir in actuall_dirs:

        fw_root = os.path.join(os.path.dirname(ayx_fw_path), ddir)
        fw_abs_root = os.path.abspath(fw_root)

        count = 0
        for root, dirs, files in os.walk(fw_abs_root):

            for file in files:
                if file.endswith(".py"):
                    count += 1
                    # print(count, file)
                    path = f"{root}" + f"\\{file}"

                    with open(path, 'r', errors='ignore') as file:
                        code = file.read()
                        node = ast.parse(code)
                        doc_string = lambda fun: ast.get_docstring(fun)

                        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
                        for class_ in classes:
                            # print("Class_name=", class_.name)
                            method_objs = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
                            methods = [(obj.name, tuple(a.arg for a in obj.args.args), doc_string(obj)) for obj in
                                       method_objs]
                            # print(methods)
                            full_main.append([class_.name, methods])

        total += count
    print(f"{total} files found in codebase to process.")


def get_available_methods():
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):

                print(file)
                path = cwd + f"\\{directory}" + f"\\{file}"

                with open(path, 'r') as file:
                    code = file.read()
                    node = ast.parse(code)
                    doc_string = lambda fun: ast.get_docstring(fun)

                    classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
                    for class_ in classes:
                        # print("Class_name=", class_.name)
                        method_objs = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
                        methods = [(obj.name, tuple(a.arg for a in obj.args.args), doc_string(obj)) for obj in
                                   method_objs]
                        # print(methods)
                        main.append([class_.name, methods])


def create_write_json(lst):
    main_list = {}
    for class_info in lst:
        class_name, methods = class_info[0], class_info[1]
        for fun in methods:
            dictionary = {
                "Methods": fun[0] + str(fun[1]),
                "Info": fun[2],
            }
            if class_name not in main_list.keys():
                main_list[class_name] = [dictionary]

            else:
                main_list[class_name].append(dictionary)

    # Serializing json
    json_object = json.dumps(main_list, indent=4)

    # Writing to sample.json
    with open("data.json", "w+") as outfile:
        outfile.write(json_object)


def create_write_csv(lst):
    classess = []
    methodss = []
    infos = []

    for class_info in lst:
        class_name, methods = class_info[0], class_info[1]
        for fun in methods:

            classess.append(class_name)
            methodss.append(fun[0] + str(fun[1]))
            if fun[2]:
                docstring = fun[2].replace('\n', '-')
            else:
                docstring = ''
            infos.append(docstring)

    main_list = {'Class': classess, 'Method': methodss, 'Doc_string': infos}

    # # Writing to
    df = pd.DataFrame(main_list)
    # print(df)
    # saving the dataframe
    file = 'sampledata.csv'
    directory = "docs"
    path = cwd + f"\\{directory}" + f"\\{file}"
    df.to_csv(path, index=False,)


def create_write_data_to_csv(lst, name):
    classess = []
    methodss = []
    infos = []

    for class_info in lst:
        class_name, methods = class_info[0], class_info[1]
        for fun in methods:

            classess.append(class_name)
            methodss.append(fun[0] + str(fun[1]))
            if fun[2]:
                docstring = fun[2].replace('\n', '-')
            else:
                docstring = ''
            infos.append(docstring)

    main_list = {'Class': classess, 'Method': methodss, 'Doc_string': infos}

    # Writing to csv.
    df = pd.DataFrame(main_list)
    # print(df)
    # saving the dataframe
    file = name
    directory = "docs"
    path = cwd + f"\\{directory}" + f"\\{file}"
    delimiter = ';'
    line_terminator = f'{delimiter}\n'
    df.to_csv(path, index=False, lineterminator=line_terminator)


if __name__ == "__main__":
    # get_available_methods()
    # print(main)
    # # create_write_json(main)
    # create_write_csv(main)

    get_avail_funcs_from_dirs()
    create_write_data_to_csv(full_main, "fullayxdata.csv")
