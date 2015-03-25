#!/usr/bin/env bash
# TODO: This has to be added to ES
curl - XPOST http://172.17.0.190:9200/nginx* -d '\
{
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
}
'
