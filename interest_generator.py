#!/bin/python
import random

n_user = 1000
m_interest = 100

with open('interests.csv', 'w') as f:
	for i in range(n_user):
		if i == 0:
			f.write('uid')
			for j in range(m_interest):
				f.write(',i'+str(j))
			f.write('\n')
		else:
			f.write('user_'+str(i))
			for j in range(m_interest):
				f.write(','+random.choice(['0','1']))
			f.write('\n')