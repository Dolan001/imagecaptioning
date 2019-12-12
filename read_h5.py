import h5py
filename = './models/model-ep010-loss5.640-val_loss5.951.h5'

with h5py.File(filename, 'r') as f:
    # List all groups
    print("Keys: %s" % f.keys())
    print(f.values())
    a_group_key = list(f.keys())[0]
    print(a_group_key)

    # Get the data
    data = list(f[a_group_key])
    print(data)
