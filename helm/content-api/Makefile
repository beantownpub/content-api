.PHONY: all test clean

name ?= content-api
image ?= content-api
env ?= dev
helm_tag ?= $(shell grep 'appVersion:' Chart.yaml | cut -f 2 -d' ')
port ?= ${CONTENT_API_PORT}

ifeq ($(env),dev)
	context = ${DEV_CONTEXT}
	namespace = ${DEV_NAMESPACE}
	logLevel = INFO
else ifeq ($(env), prod)
	context = ${PROD_CONTEXT}
	namespace = ${PROD_NAMESPACE}
	logLevel = INFO
endif

helm/context:
	kubectl config use-context $(context)

## Publish content-api Helm chart
helm/publish:
	cd helm/content-api && helm package . && \
		cd - && \
		helm repo index . --url https://beantownpub.github.io/helm/ && \
		git add content-api/

## Helm dependencies update
helm/du:
	cd helm/content-api && \
		helm dependencies update

## Deploy content-api to cluster
helm/install: helm/context
	cd helm/content-api && \
	helm upgrade --install content-api . \
		--namespace $(namespace) \
		--set global.env=$(env) \
		--set logLevel=$(logLevel) \
		--set aws.accessKeyId="${AWS_ACCESS_KEY_ID}" \
		--set aws.secretAccessKey="${AWS_SECRET_ACCESS_KEY}" \
		--set aws.secretName="${AWS_SECRET_NAME}" \
		--set aws.region="${AWS_DEFAULT_REGION}" \
		--debug
	@echo $(name)

## Create db secret
helm/db_secret: helm/context
	kubectl create secret generic db-creds \
		--namespace "${NAMESPACE}" \
		--from-literal=db_admin_user="${DB_ADMIN_USER}" \
		--from-literal=db_admin_pass="${DB_ADMIN_PASS}" \
		--from-literal=db_user="${DB_USER}" \
		--from-literal=db_pass="${DB_PASS}" \
		--from-literal=contact_db_name="${CONTACT_DB_NAME}" \
		--from-literal=menu_db_name="${MENU_DB_NAME}" \
		--from-literal=merch_db_name="${MERCH_DB_NAME}" \
		--from-literal=users_db_name="${USERS_DB_NAME}"

## Create common apps secret
helm/creds/services: context
	@echo "\033[1;32m. . . Installing external services secret . . .\033[1;37m\n"
	kubectl create secret generic services \
		--namespace $(namespace) \
		--from-literal=CONTENT_API_host="${CONTACT_API_HOST}" \
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


## Forward menu-api port
helm/port_forward: context
	kubectl port-forward --namespace $(namespace) svc/$(name) $(port):$(port)

## Stop port-forwarding
helm/stop_pf: context
	./scripts/stop_port_forward.sh $(port) || true

## Uninstall deployment
helm/uninstall:
	kubectl config use-context $(context)
	helm uninstall $(name) -n $(namespace)

## run helm template
helm/template:
	helm template helm/content-api/ \
		--namespace $(namespace) \
		--name-template=$(name) \
		--set global.env=$(env) \
		--debug

.ONESHELL: port_forward
