# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
import json

# Create your views here.

from django.http import HttpResponse
from django.http import Http404

import redis, time, random
import numpy as np
import scipy.sparse as sp
import sklearn.preprocessing as pp

def find_group(redis_conn, uid, radius=10, n_top=100, wd=True, wc=False):
	'''given a user id finds group of people nearby

	input:
	uid: user ID
	radius: radius of search from user's geolocation
	n_top: return top x closest

	output:
	group: list of people near uid, sorted by distance where uid is the first member of the list  
	'''
	group = redis_conn.georadiusbymember('location', uid, radius, 'm', withdist=wd, withcoord=wc, sort='ASC', count=200)
	if group[0][0]!=uid:
		for i in range(1, len(group)):
			if group[i][1]>0:
				break
			if group[i][0]==uid:
				t=group[i]
				group[i]=group[0]
				group[0]=t
				break
	return group

def generate_matrix(redis_conn, group, compression=None):
	''' given a group of people retrieves list of interests for each member '''

	mat = []
	# print len(group)
	for u in group:
		# TODO: consider storing interests in other datatypes
		# TODO: consider using connection to avoid TCP handshake overhead
		mat += [redis_conn.lrange('interests:'+u[0], 0, -1)]
	
	# can use sparse matrix for bigger scales
	if compression=='csr':
		return sp.csr_matrix(mat)
	elif compression=='csc':
		return sp.csc_matrix(mat)
	return np.array(mat, dtype='float')

def jaccard_first_member(mat):
	''' calculates the jaccard similarity of 
	the first user (row) in the matrix with other users (rows)
	
	mat: matrix of user interests 
	(keep your groups of users less than 1000 for better performance)
	'''
	user1 = mat[0,:].reshape((1,mat.shape[1]))
	aat = np.dot(user1 , mat.T)
	rows_sum = mat.sum(axis=1)
	aat /= (rows_sum+rows_sum[0]-aat)
	return aat.tolist()

def generate_interest(r, n_user=100, n_interest=100):
	'''' generate sample interests '''
	for i in range(n_user):
		r.delete('interests:user_'+str(i))
		ins = np.random.randint(2, size=n_interest).tolist()
		r.lpush('interests:user_'+str(i),  *ins)


def slides(request):
	return redirect("https://docs.google.com/presentation/d/11_fOv9bDV4DHhoHI7ZA2kljsHNaaE-diLzAFMTXxtp4/edit?usp=sharing")

def index(request):
	return render(request, 'user/index.html', None)
	# return HttpResponse("Hello, world. You're at the mysite index.")

def get_user_info(request):
	if not(request.is_ajax() and request.POST):
		raise Http404

	similarity_thresh = 0.3
	result = []
	uid = request.POST.get('uid')

	print 'uid:', uid
	r = redis.StrictRedis(
		host='10.0.0.12',
		port=6379, 
		password='')

	try:
		g = find_group(r, uid, 10)
		g2 = find_group(r, uid, 200, wd=False, wc=True)
		m = generate_matrix(r, g)
		group_interests = jaccard_first_member(m)[0]
		for i, u in enumerate(g[1:]):
			if group_interests[i+1]>=similarity_thresh:
				result += [(u[0], u[1],group_interests[i+1])]
		f = {'uid': uid, 'result':result[:5], 'group':g,'more_people':g2}
	except:
		f = f = {'uid': uid, 'result':[], 'group':[],'more_people':[]}
	data = json.dumps(f)
	return HttpResponse(data, content_type='application/json')
