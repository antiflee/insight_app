#!/bin/bash


sed -i -e '1,6d' Data/*/Trajectory/*.plt

for folders in (ls Data); do
	UID = folders
	find Trajectory/*.plt -type f -exec sed -e '1,6d' {} \; > $UID.txt # s/$/{$UID}/
done

# python producer.py ${FILE}