import yaml
import sys

with open('tutorials/results.yaml') as f:
    config = yaml.full_load(f)

passed = True

for hardware in config.keys():
    hw = config[hardware]
    for notebook in hw.keys():
        nb = hw[notebook]
        if nb['passed']== False:
            passed = False
            print("{} (hw {}) failed with error {}".format(nb, hardware, nb['errors']))

if passed:
    sys.exit(0)
else:
    sys.exit(1)
