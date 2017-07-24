import os
import re

folder = "google_trends"

def write_pop(day, pop):
    pop = pop.replace("類別：所有類別\nTOP\n","")
    pop_re = ""
    for c in pop.split("\n"):
        pop_re += day + "," + c + "\n"
    with open("pop_save.csv", "a") as f:
        f.write(pop_re)

def write_up(day, up):
    up = up.replace("RISING\n", "")
    up = up.replace("%", "")
    up = up.replace("\"", "")
    up_re = ""
    for c in up.split("\n"):
        match = re.match("(.*),飆升", c)
        match2 = re.match("(.*),\+(\d+),(\d{3})", c)
        if match:
            up_re += day + "," + match.group(1) + ",5000" + "\n"
        elif match2:
            up_re += day + "," + match2.group(1) + "," + match2.group(2) + match2.group(3) + "\n"
        else:
            match3 = re.match("(.*),\+(\d{3})", c)
            if match3:
                up_re += day + "," + match3.group(1) + "," + match3.group(2) + "\n"
    with open("up_save.csv", "a") as f:
        f.write(up_re)

def filenames():
    filenames = []
    for filename in os.listdir(folder):
        filenames.append(filename)
    filenames.sort()
    return filenames

def transform_file(filename):
    file_path = folder + "/" + filename
    with open(file_path, "r") as f:
        day = filename.split(".csv")[0]
        csvs = f.read().split("\n\n")
        pop = csvs[0]
        up = csvs[1]
        write_pop(day,pop)
        write_up(day,up)

def main():
    for filename in filenames():
        transform_file(filename)

main()