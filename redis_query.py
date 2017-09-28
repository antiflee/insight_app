#!/bin/python
import redis, time, random
import numpy as np
import scipy.sparse as sp
import sklearn.preprocessing as pp

def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r %2.4f sec' % \
              (method.__name__, te-ts)
        return result

    return timed


class user():
	def __init__(self):
		self.uid = ''
		self.pos = (0,0)
		self.hash = ''
	def __repr__(self):
		return 'user(%s, pos(%.6f,%.6f))' %(self.uid, self.pos[0], self.pos[1])

###############################################
#### functions related to batch processing ####
###############################################

def find_all_groups():
	r = redis.Redis(
	    host='10.0.0.12',
	    port=6379, 
	    password='')

	t0=time.time()
	uid_list = r.zrange('location', 0, -1)
	t1=time.time()
	# pos_list = r.geopos('location', *uid_list)
	hash_list = r.geohash('location', *uid_list)
	print t1-t0

	t3=time.time()
	print t3-t1

	users = []
	groups = []
	my_list = []
	last_hash = ''
	hash_precision = 7
	min_group_size = 3

	for i,_ in enumerate(uid_list):
		x = user()
		x.uid = uid_list[i]
		# x.pos = pos_list[i]
		x.hash = hash_list[i]
		users += [x]

		if x.hash[:hash_precision] == last_hash[:hash_precision]:
			my_list += [x]
		else:
			if len(my_list)>min_group_size:
				groups += [my_list]
			my_list = [x]
		last_hash = x.hash
	if len(my_list)>min_group_size:
		groups += [my_list]

	t4=time.time()
	print len(users), len(groups), 'time:', t4-t3

	
	# for g in groups:
	# 	g_set = set([i.uid for i in g])
	# 	for u in g:
	# 		if u.uid == 'user_8':
	# 			print g
	# 		# match = r.smembers('match:'+u.uid)
	# 		match = r.zrevrange('match:'+u.uid, 0, -1)
	# 		res = g_set.intersection(match)
	# 		if len(res)>0:
	# 			suggestions[u.uid] = res
	# print time.time()-t4
	# print suggestions['user_8']


def jaccard_similarities(mat, u_ind=0):
    mat.data[:] = 1 # binarize
    print mat
    if u_ind>-100: ####################### change
    	print 'aaa', mat[u_ind,:]
    	aat = mat[u_ind,:] * mat.T
    else:
    	aat = mat * mat.T
    rows_sum = mat.getnnz(axis=1)
    a = np.repeat(rows_sum, aat.getnnz(axis=1))
    b = rows_sum[aat.indices]
    print 'r', rows_sum
    print 'a', a
    print 'b', b
    similarities = aat.copy()
    similarities.data /= (a+b-aat.data)

    print 'jaccard'
    return similarities


#################################################
#### functions related to request processing ####
#################################################

@timeit
def find_group(redis_conn, uid, radius=10, n_top=100):
	'''given a user id finds group of people nearby

	input:
	uid: user ID
	radius: radius of search from user's geolocation
	n_top: return top x closest

	output:
	group: list of people near uid, sorted by distance where uid is the first member of the list  
	'''
	group = redis_conn.georadiusbymember('location', uid, radius, 'm', withdist=True, sort='ASC', count=200)
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

@timeit
def generate_matrix(redis_conn, group, compression=None):
	''' given a group of people retrieves list of interests for each member '''

	mat = []
	print len(group)
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

@timeit
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

@timeit
def generate_interest(r, n_user=100, n_interest=100):
	'''' generate sample interests '''
	for i in range(n_user):
		r.delete('interests:user_'+str(i))
		ins = np.random.randint(2, size=n_interest).tolist()
		r.lpush('interests:user_'+str(i),  *ins)


if __name__ == '__main__':
	
	similarity_thresh = 0.2

	r = redis.StrictRedis(
	    host='10.0.0.12',
	    port=6379, 
	    password='')

	# generate_interest(r, 10**5)

	ids = ['user_'+str(i+1) for i in range(10)]

	while True:
		t0=time.time()
		result = []
		uid = random.choice(ids)

		g = find_group(r, uid, 10)
		m = generate_matrix(r, g)
		group_interests = jaccard_first_member(m)[0]
		for i, u in enumerate(g[1:]):
			if group_interests[i+1]>=similarity_thresh:
				result += [(u[0], u[1],group_interests[i+1])]

		print uid, result[:3], time.time()-t0
