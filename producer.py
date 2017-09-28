#!/bin/python

import sys, random, datetime, time
from confluent_kafka import Producer

def produce_from_file(p,file_path):
	with open(file_path, 'r') as input_file:
		for i,line in enumerate(input_file):
			if i > 10**5:
				break
			if i % 1000 == 0:
				time.sleep(5)
			msg_items = line.strip().split(',')
			lat = msg_items[0]
			lon = msg_items[1]
			# time_stamp = msg_items[-1]
			uid = str(random.choice(range(10**5)))
			msg = '{"uid":"user_'+uid+'","long":"'+lon+'","lat":"'+lat+'","time":"'+str(datetime.datetime.now())+'"}'
			
			# if verbose:
			# 	print msg
			
			p.produce('topic1', msg)
	p.flush()


if __name__ == "__main__":
	file_path = 'Geolife/all_data.plt'
	try:
		file_path = sys.argv[1]
	except:
		pass
	p = Producer({'bootstrap.servers':'10.0.0.11:9092'})
	produce_from_file(p, file_path)