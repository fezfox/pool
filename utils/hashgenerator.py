import hashlib
myPassword=b"splishsplosh"
print(hashlib.sha256(myPassword).hexdigest())