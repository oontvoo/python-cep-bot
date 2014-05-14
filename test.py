# RUN these before running this script
# export PYTHONPATH=/opt/streambase/lib64/python2.6
# export STREAMBASE_HOME=/opt/streambase

import streambase as sb
import os

DEFAULT_TIMEOUT = 500 #ms

client = sb.Client("sb://localhost")

streams = client.listEntities(sb.EntityType.INPUT_STREAMS)
for stream in streams:
    print(stream + ":")
    print(client.describe(stream))

props = client.getStreamProperties("InputStream")
schema = props.getSchema()
print(schema)

tuple = sb.Tuple(schema)
tuple.setString("sender", "secondSender")
tuple.setString("msg", "secondMsg")

print("Enqueing " + str(tuple))
client.enqueue("InputStream", tuple)



### deq
print "PID: " + str(os.getpid())
client2 = sb.Client("sb://localhost")
client2.subscribe("OutputStream")
try:
    while True:
        result = sb.DequeueResult()
        while result.getStatus() != sb.DequeueResult.GOOD:
            result = client2.dequeue(DEFAULT_TIMEOUT)
        tuples = result.getTuples()
        print("len: " + str(len(tuples)))
        for tuple in tuples:
            print("Dequeued tuple: " + str(tuple))

except KeyboardInterrupt, e:
    client2.close()


client2.close()
client.close()
