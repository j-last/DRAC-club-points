import os
from functions.functions import getAgeCat

for name in os.listdir("People Files"):
    file_name = os.path.join("People Files", name)
    age_cat = getAgeCat(name[:-4])
    with open(file_name, "w") as f:
        f.writelines([
            "-----------\n",
            age_cat + "\n",
            "TOTAL: 0\n",
            "-----------\n",
            "RACES:\n"
            ])
