.PHONY: all test clean

name ?= content-api
image ?= content-api
env ?= dev
tag ?= $(shell grep 'appVersion:' Chart.yaml | cut -f 2 -d' ')
port ?= ${BEANTOWN_PORT}

ifeq ($(env),dev)
	context = ${DEV_CONTEXT}
	namespace = ${DEV_NAMESPACE}
	square_url = ${SQUARE_URL_DEV}
	logLevel = tiny
else ifeq ($(env), prod)
	context = ${PROD_CONTEXT}
	namespace = ${PROD_NAMESPACE}
	square_url = ${SQUARE_URL_PROD}
	logLevel = tiny
endif

## Publish content-api Helm chart
helm/publish:
	cd helm/content-api/ && helm package . && \
		cd - && \
		helm repo index . --url https://beantownpub.github.io/helm/ && \
		git add admin/

## Create app-creds
helm/creds/app: context
	@echo "\033[1;32m. . . Installing creds $(env) secret . . .\033[1;37m\n"
	kubectl create secret generic app-creds \
		--namespace $(namespace) \
		--from-literal=api_user="${API_USER}" \
		--from-literal=api_pass="${API_PASS}" \
		--from-literal=db_host="${DB_HOST}" \
		--from-literal=db_pass="${DB_PASS}" \
		--from-literal=db_port="${DB_PORT}" \
		--from-literal=db_user="${DB_USER}"

## Create common apps secret
helm/creds/services: context
	@echo "\033[1;32m. . . Installing external services secret . . .\033[1;37m\n"
	kubectl create secret generic services \
		--namespace $(namespace) \
		--from-literal=contact_api_host="${CONTACT_API_HOST}" \
		--from-literal=contact_api_port="${CONTACT_API_PORT}" \
		--from-literal=contact_api_protocol="${CONTACT_API_PROTOCOL}" \
		--from-literal=menu_api_host="${MENU_API_HOST}" \
		--from-literal=menu_api_port="${MENU_API_PORT}" \
		--from-literal=menu_api_protocol="${MENU_API_PROTOCOL}" \
		--from-literal=merch_api_host="${MERCH_API_HOST}" \
		--from-literal=merch_api_port="${MERCH_API_PORT}" \
		--from-literal=merch_api_protocol="${MERCH_API_PROTOCOL}" \
		--from-literal=users_api_host="${USERS_API_HOST}" \
		--from-literal=users_api_port="${USERS_API_PORT}" \
		--from-literal=users_api_protocol="${USERS_API_PROTOCOL}"

## install content-api frontend in K8s cluster
install:
	kubectl config use-context $(context)
	helm upgrade --install content-api helm/content-api/ \
		--namespace $(namespace) \
		--set image.tag=$(tag) \
		--set global.env=$(env) \
		--set logLevel=$(logLevel) \
		--debug

delete:
	kubectl config use-context $(context)
	helm uninstall $(name) -n $(namespace)

## run helm template
template:
	helm template helm/content-api/ \
		--namespace $(namespace) \
		--name-template=$(name) \
		--set global.env=$(env) \
		--debug

.ONESHELL: port_forward
