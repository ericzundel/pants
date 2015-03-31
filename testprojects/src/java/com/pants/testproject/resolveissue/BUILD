
java_library(
  name="foo",
  sources = ["Foo.java"],
  dependencies = [
    ':qux-jars',
    ':baz-jars',
    ':foo-jars',
    ':bar-jars',
  ]
)

java_library(
  name="bar",
  sources = ["Bar.java"],
  dependencies = [
    ':baz-jars',
    ':foo-jars',
    ':bar-jars',
    ':qux-jars',
  ]
)

java_library(
  name="baz",
  sources = ["Baz.java"],
  dependencies = [
    ':baz-jars',
    ':bar-jars',
    ':foo-jars',
    ':qux-jars',    
  ]
)

java_library(
  name="qux",
  sources = ["Qux.java"],
  dependencies = [
    ':foo-jars',
    ':bar-jars',
    ':qux-jars',    
    ':baz-jars',
  ],
) 

java_library(
  name="foobar",
  dependencies=[
    ':qux',
  ]
)

java_library(
  name="foobaz",
  dependencies=[
    ':baz',
  ]
)

jar_library(
  name = 'foo-jars',
  jars = [
    jar(org='net.java.dev.jna',
           name='jna',
           rev='4.0.0'),
  ],
)

jar_library(
  name = 'bar-jars',
  jars = [
    jar(org='org.apache.sshd',
           name='sshd-core',
           rev='0.13.0'),
  ],
)

jar_library(
  name = 'baz-jars',
  jars = [
   jar(org='com.maxmind.geoip2',
           name='geoip2',
           rev='2.1.0',), 
  ],
)

jar_library(
  name = 'qux-jars',
  jars = [
    jar(org='com.bugsnag',
           name='bugsnag',
           rev='1.2.8',),
  ],
)



jar_library(
  name = 'foobar-jars',
  jars= [
   jar(org='com.maxmind.geoip2',
           name='geoip2',
           rev='2.1.0',), 
    jar(org='com.bugsnag',
           name='bugsnag',
           rev='1.2.8',),
    jar(org='net.java.dev.jna',
           name='jna',
           rev='4.0.0'),
    jar(org='org.apache.sshd',
           name='sshd-core',
           rev='0.13.0'),
  ],
)

jar_library(
  name = 'foobaz-jars',
  jars = [
    jar(org='net.java.dev.jna',
           name='jna',
           rev='4.0.0'),
    jar(org='org.apache.sshd',
           name='sshd-core',
           rev='0.13.0'),
    jar(org='com.bugsnag',
           name='bugsnag',
           rev='1.2.8',),
   jar(org='com.maxmind.geoip2',
           name='geoip2',
           rev='2.1.0',), 
  ],
)
