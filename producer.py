#!/bin/python

import sys, random
from confluent_kafka import Producer

def produce_from_file(p,file_path):
	with open(file_path, 'r') as input_file:
		for i,line in enumerate(input_file):
			msg_items = line.strip().split(',')
			if i>6 and len(msg_items)>2:
				lat = msg_items[0]
				lon = msg_items[1]
				time_stamp = msg_items[-1]
				uid = str(random.choice([1,2,3,4,5,6,7,8,9,10]))
				msg = '{"uid":"user_'+uid+'","long":"'+lon+'","lat":"'+lat+'","time":"'+time_stamp+'"}'
				print msg
				p.produce('topic1', msg) #, str(i))
	p.flush()


if __name__ == "__main__":
	file_path = 'Geolife/Data/103/Trajectory/20080917135224.plt'
	try:
		file_path = sys.argv[1]
	except:
		pass
	p = Producer({'bootstrap.servers':'10.0.0.11:9092'})
	produce_from_file(p, file_path)