.PHONY: clean kill run run2 all
.IGNORE: kill

all:
run:
	nohup ./env/bin/gunicorn --worker-class eventlet -w 1 -b 127.0.0.1:9696 server:app --reload &

run2:
	nohup ./env/bin/gunicorn --worker-class eventlet -w 1 -b 127.0.0.1:9696 server:app --reload >/dev/null 2>&1 &

kill:
	pkill -f "127.0.0.1:7676 xmp:app"

clean:
	@echo "clean is None"
