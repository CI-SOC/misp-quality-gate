
#!/bin/bash

SRC_FOLDER=/opt/misp-quality-gate/src
VENV_FOLDER=/opt/misp-quality-gate/venv

# activate python virtual environment
source $VENV_FOLDER/bin/activate

# execute check
python3 $SRC_FOLDER/run.py

echo 'Done'


