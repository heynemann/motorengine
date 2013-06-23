test:
	@PYTHONPATH=.:$$PYTHONPATH python setup.py test

tox: mongo_test
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox

setup:
	@pip install -e .\[tests\]

kill_mongo_test:
	@ps aux | awk '(/mongod.+test/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'
	@rm -rf /tmp/motorengine_test/mongodata
	@rm -rf /tmp/motorengine_test_2/mongodata
	@rm -rf /tmp/motorengine_test_3/mongodata

mongo_test: kill_mongo_test
	@rm -rf /tmp/motorengine_test/mongotestdata && mkdir -p /tmp/motorengine_test/mongotestdata
	@rm -rf /tmp/motorengine_test_2/mongotestdata && mkdir -p /tmp/motorengine_test_2/mongotestdata
	@rm -rf /tmp/motorengine_test_3/mongotestdata && mkdir -p /tmp/motorengine_test_3/mongotestdata
	@mongod --dbpath /tmp/motorengine_test/mongotestdata --logpath /tmp/motorengine_test/mongotestlog --port 4445 --quiet --smallfiles --oplogSize 128 &
	@mongod --dbpath /tmp/motorengine_test_2/mongotestdata --logpath /tmp/motorengine_test_2/mongotestlog --replSet rs0 --port 27017 --quiet --smallfiles --oplogSize 128 &
	@mongod --dbpath /tmp/motorengine_test_3/mongotestdata --logpath /tmp/motorengine_test_3/mongotestlog --replSet rs0 --port 27018 --quiet --smallfiles --oplogSize 128 &
	@sleep 3
	@mongo --host localhost --port 27017 --eval 'rs.initiate({_id: "rs0", members: [{ _id: 0, host: "localhost:27017" }]});rs.conf();while(!rs.add("localhost:27018")["ok"]){};quit()'

