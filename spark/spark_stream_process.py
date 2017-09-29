from __future__ import print_function
import redis, math, datetime, yaml, json
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from config import *

"""Processes the streaming data"""

def push_to_redis(data):
	redis_session = redis.Redis(host=REDIS_ADDR, port=6379, db=0)
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
	ssc = StreamingContext(sc, 5)

	my_topic = TOPIC
	brokers = ','.join(KAFKA_BROKERS)

	directKafkaStream = KafkaUtils.createDirectStream(ssc,	[my_topic], {"metadata.broker.list": brokers})
	lines = directKafkaStream.map(lambda v: json.loads(v[1]))
	my_window = lines.window(5, 5).map(lambda x: (x['uid'], x))\
				.reduceByKey(lambda a, b: a if (a['time']>=b['time']) else b)
	
	my_window.pprint()
	w2 = my_window.foreachRDD(lambda rdd: rdd.foreachPartition(push_to_redis))

	ssc.start()
	ssc.awaitTermination()