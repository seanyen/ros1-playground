import os

print('%s' % os.environ['PKG_NAME'].replace('ros-eloquent-', '').replace('-', '_'))
