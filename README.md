# misp-quality-gate

# MISP Quality Gate will publish only unpublished events if it meets the required tags criteria.
# It will notify via command line of what tags passed and also write to a log file.

# A cronjob.sh is available to update to periodically run the script.

# Instructions:
# Setup virtualenv called venv in the root of the path: e.g. python3 -m venv /path/to/new/virtual/environment
#  cd /opt/misp-quality-gate
#  python3 -m venv /opt/misp-quality-gate/venv
# pip3 install requests
  
#  cronjob.sh - can be setup to run periodically
