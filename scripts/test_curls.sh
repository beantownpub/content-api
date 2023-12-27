#!/bin/bash

AUTH=$(echo -e "${API_USER}:${API_PASS}" | base64)
AUTH_HEADER="Authorization: Basic ${AUTH}"

function getPosts {
    echo "Getting Posts"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:${API_PORT}/v1/content/blog" | jq .
}

function getPost {
    echo "Getting Post ${1}"
    curl \
        -s \
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:${API_PORT}/v1/content/posts/${1}" | jq .
}

function createPost {
    echo "Creating Post"
    curl \
        -s \
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        -d @data.json \
        "localhost:${API_PORT}/v1/content/posts"
}

function deletePost {
    echo "Deleting Post"
    curl \
        -s \
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        -X DELETE \
        "localhost:${API_PORT}/v1/content/posts/${1}"
}

ARGS=("$@")
ARG_INDEX=0
for arg in "${ARGS[@]}"; do
    value=$((ARG_INDEX+1))
    case $arg in
        -c|--command)
            COMMAND="${ARGS[$value]}"
        ;;
        -p|--post)
            POST="${ARGS[$value]}"
        ;;
    esac
    ((ARG_INDEX=ARG_INDEX+1))
done

if [[ "${COMMAND}" = "create" ]]; then
    createPost
fi

if [[ "${COMMAND}" = "delete" ]]; then
    deletePost "${POST}"
fi

if [[ "${COMMAND}" = "get-all" ]]; then
    getPosts
fi

if [[ "${COMMAND}" = "get" ]]; then
    getPost "${POST}"
fi
