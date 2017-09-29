#!/bin/python

import sys, random, datetime, time
from confluent_kafka import Producer
from config import *

def produce_from_file(p,file_path):
	uid = int(file_path.split('/')[-3])
	with open(file_path, 'r') as input_file:
		for i,line in enumerate(input_file):
			time.sleep(2)
			msg_items = line.strip().split(',')
			lat = msg_items[0]
			lon = msg_items[1]
			msg = '{"uid":"user_'+str(uid)+'","long":"'+lon+'","lat":"'+lat+'","time":"'+str(datetime.datetime.now())+'"}'
			
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
	p = Producer({'bootstrap.servers':','.join(KAFKA_BROKERS)})
	produce_from_file(p, file_path)