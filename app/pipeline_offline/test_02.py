import numpy as np, pickle
E  = np.load("indices/text_emb.npz")
mp = pickle.load(open("indices/pid2idx.pkl","rb"))
sample_pid = list(E.files)[0]
print(sample_pid, E[sample_pid][:5])      # 길이 384 벡터 확인
print("pid2idx size =", len(mp))


