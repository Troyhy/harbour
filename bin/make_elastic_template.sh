#!/usr/bin/env bash
# TODO: This has to be added to ES
docker run -it --link harbour_elasticsearch_1:es --entrypoint="/usr/bin/curl" harbour_fluentd:latest -XPOST 'http://es:9200/_template/nginx_access' -d \
'{
  "mappings": {
    "_default_": {
      "_all": { "enabled": false },
      "_source": { "compress": true },
      "properties":{
        "@timestamp":{"type":"date","format":"dateOptionalTime"},
        "agent":{"type":"string"},
        "code":{"type":"string"},
        "host":    {"type":"string"},
        "message":{"type":"string"},
        "method":{"type":"string"},
        "path":{"type":"string"},
        "referer":{"type":"string"},
        "remote":{"type":"string"},
        "size":{"type":"integer"},
        "tag":{"type":"string"},
        "user":{"type":"string"}
      }
    }
  },
  "template": "nginx-*"
}'
