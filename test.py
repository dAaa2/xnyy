import os
test = "1\\2\\3"
print(os.sep.join(test.rsplit("\\", 2)[1:]))