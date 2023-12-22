-include \
	helm/content-api/Makefile
.PHONY: all test clean

export MAKE_PATH ?= $(shell pwd)
export SELF ?= $(MAKE)

MAKE_FILES = \
	${MAKE_PATH}/Makefile \
	${MAKE_PATH}/helm/content-api/Makefile

name ?= content-api
image ?= $(name)
port ?= 5033
repo ?= jalgraves
tag ?= $(shell yq eval '.info.version' swagger.yaml)
hash = $(shell git rev-parse --short HEAD)

ifeq ($(env),dev)
	image_tag = $(tag)-$(hash)
	context = ${DEV_CONTEXT}
	namespace = ${DEV_NAMESPACE}
else ifeq ($(env),prod)
    image_tag = $(tag)
	context = ${PROD_CONTEXT}
	namespace = ${PROD_NAMESPACE}
else
	env := dev
endif

context:
	kubectl config use-context $(context)

## Run pip-compile
compile:
	cp requirements.txt prev-requirements.txt
	pip-compile requirements.in

build:
	@echo "\033[1;32m. . . Building Content API image . . .\033[1;37m\n"
	@echo "Wtf $(context)"
	docker build \
		--platform linux/x86_64 \
		-t $(image):$(image_tag) .

publish: build
	docker tag $(image):$(image_tag) $(repo)/$(image):$(image_tag)
	docker push $(repo)/$(image):$(image_tag)

test:
	python3 -m pytest test/

clean:
	rm -rf api/__pycache__ || true
	rm .DS_Store || true
	rm api/*.pyc

## Start docker container
docker/run:
	docker run \
		--rm \
		--name $(image) \
		-p $(port):$(port) \
		$(image):$(image_tag)

## Stop docker container
docker/stop:
	docker rm -f $(image)

kill_pod: context
	./scripts/kill_pod.sh $(env) $(name)

kill_port_forward: context
	./scripts/stop_port_forward.sh $(port)

redeploy: build restart

restart: kill_pod kill_port_forward

## Show available commands
help:
	@printf "Available targets:\n\n"
	@$(SELF) -s help/generate | grep -E "\w($(HELP_FILTER))"
	@printf "\n\n"

help/generate:
	@awk '/^[a-zA-Z\_0-9%:\\\/-]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub("\\\\", "", helpCommand); \
			gsub(":+$$", "", helpCommand); \
			printf "  \x1b[32;01m%-35s\x1b[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKE_FILES) | sort -u

# Silence make output
# MAKEFLAGS += -s
