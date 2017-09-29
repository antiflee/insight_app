#!/bin/bash

# for i in Geolife/Data/* ; do
#   if [ -d "$i" ]; then
#     sed -e '1d' $i/Trajectory/*.plt > $i/Trajectory/all.plt
#   fi
# done


for i in Geolife/Data/* ; do
  if [ -d "$i" ]; then
    python producer_single.py $i/Trajectory/all.plt
  fi
done