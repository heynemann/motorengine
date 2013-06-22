test: mongo_test
	@coverage run --branch `which nosetests` -vv --with-yanc -s tests/
	@coverage report -m --fail-under=80

tox:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox

setup:
	@pip install -e .\[tests\]

kill_mongo_test:
	@ps aux | awk '(/mongod.+test/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'
	@rm -rf /tmp/motorengine_test/mongodata

mongo_test: kill_mongo_test
	@rm -rf /tmp/motorengine_test/mongotestdata && mkdir -p /tmp/motorengine_test/mongotestdata
	@mongod --dbpath /tmp/motorengine_test/mongotestdata --logpath /tmp/motorengine_test/mongotestlog --port 6667 --quiet &
	@sleep 3
