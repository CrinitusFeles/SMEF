from filehash.filehash import FileHash
hasher = FileHash('sha1')
hash = hasher.cathash_dir("/home/astraadmin/.local/lib/python3.9/site-packages/smef", "*.py")
#hash = checksumdir.dirhash("./smef")
print((hash))
if str(hash) != 'b9d4c17ce8454eae0b134b0b196a33591daef7ce':
    print("Hash sum is incorrect")
else:
    print("Hash sum OK")
