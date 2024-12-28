import os
from functions.functions import getAgeCat

for name in os.listdir("People Files"):
    name_file = os.path.join("People Files", name)
    age_cat = getAgeCat(name[:-4])
    with open(name_file, "w") as f:
        f.writelines([
            "-----------\n",
            "WU40" + "\n",
            "TOTAL: 0\n",
            "-----------\n",
            "RACES:\n"
            ])