#!/bin/bash
# Run the ETL script and save its logs
cd /DWH/Scripts
python /DWH/Scripts/ETL_script.py > /DWH/Logs/etl_$(date +\%Y-\%m-\%d).log 2>&1

echo "ETL script has finished."
# To Keep the container running
tail -f /dev/null
