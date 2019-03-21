IMAGE=kasterma/vip
TAG=$(shell cat VERSION)

build: files/get-pip.py
	docker build -t ${IMAGE}:${TAG} .

push:
	docker push ${IMAGE}:${TAG}

files/get-pip.py:
	cd files ; curl -O https://bootstrap.pypa.io/get-pip.py
