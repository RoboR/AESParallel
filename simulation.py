import numpy as np
import datetime
from SEFPS import SEFPS

NUM_FILES = 100
KEY_SIZES = [16, 24, 32]
KEYS = []

for size in KEY_SIZES:
	key = np.random.choice(256, size).astype(np.uint8)
	KEYS.append([size, key])

NUM_CORES = [1, 2, 4, 8]
NUM_USERS = [5, 10, 15]
FILE_VARIANCE = [3, 9, 16]
FILE_ASSIGNS = dict()
FILE_SIZE = 1024

for num in NUM_USERS:
	file_assign = dict()

	for variance in FILE_VARIANCE:
		temp = np.arange(num)
		mean = temp.mean()
		temp = ((1/np.sqrt(2 * np.pi * variance)) * np.exp(-((temp - mean)**2)/(2*variance))) * NUM_FILES
		temp = temp.astype(int)
		temp2 = NUM_FILES - temp.sum()
		if temp2:
			for i in range(temp2):
				temp[i % temp.size] += 1

		count = 0
		for i in range(temp.size):
			if temp[i] == 0:
				count += 1
				temp[i] += 1

		for i in range(count):
			temp[temp.argmax()] -= 1

		file_assign[variance] = temp

	FILE_ASSIGNS[num] = file_assign


fp = open("result.txt", 'a')

for key in KEYS:
	for num_cores in NUM_CORES:
		for user in FILE_ASSIGNS:
			for variance in FILE_ASSIGNS[user]:
				key_bytes = key[1]
				condition = "Key size = " + str(key[0]) \
							+ " ; Number of cores = " + str(num_cores) \
							+ " ; Number of user = " + str(user) \
							+ " ; File distribution variance = " + str(variance) \
							+ " ; files assigned = " + str(FILE_ASSIGNS[user][variance])
				print(condition)
				fp.write(condition)
				fp.write("\n")

				# AES algorithm here
				start_time = datetime.datetime.now()

				# SEFPS
				for file_by_user in FILE_ASSIGNS[user][variance]:
					for file in range(0, file_by_user):
						sefps = SEFPS(num_cores, key_bytes)
						file_bytes = np.random.choice(256, FILE_SIZE).astype(np.uint8)
						cipher = sefps.encrypt(file_bytes)

				end_time = datetime.datetime.now()

				delta_time = end_time - start_time
				delta_microseconds = delta_time.total_seconds() * 1000

				time_res = "Total time spend " + str(delta_microseconds)
				print(time_res)
				print("\n")
				fp.write(time_res)
				fp.write("\n\n")
