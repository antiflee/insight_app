from __future__ import print_function
import redis, math, datetime, yaml, json
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from elasticsearch import Elasticsearch
from elasticsearch import helpers


###################################################

APP_NAME = 'App1'
TOPIC = 'topic1'
KAFKA_BROKERS = ['10.0.0.8:9092', '10.0.0.9:9092', '10.0.0.11:9092']
REDIS_ADDR = '10.0.0.12'

###################################################

"""Processes the streaming data"""

def consume(kafka_addr):
	pass

def process(data):
	pass

def get_coord(line):
	return None 

def push_to_redis(data):
	redis_session = redis.Redis(host='10.0.0.12', port=6379, db=0)
	with redis_session.pipeline() as pipe:
		for d in data:
			pipe.geoadd('location', float(d[1]['long']), float(d[1]['lat']), d[1]['uid'])
		try:
			pipe.execute()
		except RedisError:
			print('Redis error!')

def push_to_batch(batch_addr, data):
	pass


if __name__=="__main__":
	sc = SparkContext(appName=APP_NAME)
	sc.setLogLevel("WARN")
	ssc = StreamingContext(sc, 5) # batch duration = 5 seconds

	my_topic = TOPIC
	brokers = ','.join(KAFKA_BROKERS)

	directKafkaStream = KafkaUtils.createDirectStream(ssc,	[my_topic], {"metadata.broker.list": brokers})
	# http://spark.apache.org/docs/latest/api/python/pyspark.streaming.html#pyspark.streaming.kafka.KafkaUtils
								# window(windowDuration, slideDuration=None)
	lines = directKafkaStream.map(lambda v: json.loads(v[1]))
	my_window = lines.window(10, 5).map(lambda x: (x['uid'], x))\
				.reduceByKey(lambda a, b: a if (a['time']>=b['time']) else b)
	my_window.pprint()
	w2 = my_window.foreachRDD(lambda rdd: rdd.foreachPartition(push_to_redis))
	# w2.pprint()
	# lines.pprint()

	# for i in my_window.collect():
	# 	print(i)

	# try:
	# 	conn = redis.StrictRedis(host="10.0.0.12", port=6379, db=0)
	# 	# locs = [12.97, 77.59'Bangalore', 13,77,'Baku']
	# 	lo = []
	# 	for i in range(100000):
	# 		lo+=[12.97+(i*0.00001), 77.59+(i*0.00001), str(i)]

	# 	# locs = sum([[12.97+(i*0.00001), 77.59+(i*0.00001), str(i)] for i in range(100000)], [])
	# 	conn.geoadd('location', *lo) 
	# 	print ('geoadd done')
	# except redis.exceptions.ResponseError:
	# 	print ("got response error!")

	# window_s = directKafkaStream.window(300, 150).map(getLLW)\
	# 			.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + \
	# 											b[1], a[2] + b[2]))\
	# 			.map(getSTD)
	# winmr2 = window_s.foreachRDD(lambda rdd: rdd\
	# 									.foreachPartition(send2redis))

	# stream = directKafkaStream.window(3600, 3600).map(getFormat)\
	# 			.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))\
	# 			.map(getAvg)
	# stream.foreachRDD(lambda rdd: rdd.foreachPartition(send2Es))

	ssc.start()
	ssc.awaitTermination()