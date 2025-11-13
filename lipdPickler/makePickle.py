import lipd
import pickle
import os

print(os.getcwd())
print(os.path.isfile('/lipd.pkl'))

D = lipd.readLipd("/output/")
TS = lipd.extractTs(D)
all_data = {}
all_data['D'] = D

filetosave = open('/lipd.pkl','wb')

pickle.dump(all_data, filetosave, protocol = 2)

filetosave.close()
