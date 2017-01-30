# Test tool
client.py make requests to the webmvc API by multiple user session.
"credential" file contains login:password pairs line by line

### How to run
```bash
cat credentials | python client.py -c --host=<server-host> --port=<server-port>
// ex: cat credentials | python client.py -c --host=172.17.0.2 --port=8330
```

Minimal python version is 3.5

### Task plan examples

Task plan entry that contains "params" key or "files" key will be executed by POST HTTP request.
Task plan without "params" key will be executed by GET HTTP request.

#### Call pageflow API
```json
// task plan to call pageflow API
[
  {
    "url": "/webmvc/api/pageflow/myMetadataProject/testInputParametersPageflow",
    "params": {"operation":"START", "params": {"pfParams": {"inputParam1": "inputValue1"}}},
    "requestCount": 1
  }
]
```

#### Call file upload API
```json
[
  {
    "url": "/webmvc/_upload?storage=DB",
    "files":["/path/to/file/with.extension"],
    "requestCount": 1
  }
]
```

#### Call file download API
```json
[
  {
    "url": "/webmvc/_download&key=2c4ed01e-75fb-4c8d-ad61-7e30153b0be7",
    "requestCount": 1
  }
]
```