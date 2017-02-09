# Test tool
client.py make requests to the webmvc API by multiple user session.
"credential" file contains login:password pairs line by line

### How to run
```bash
cat credentials | python client.py -c --host=<server-host> --port=<server-port> --task-plan=<task_plan_json_file>
// ex: cat credentials | python client.py -c --host=172.17.0.2 --port=8330 --task-plan=task_plan.json
```

Minimal python version is 3.5

### Task plan examples

Task plan entry that contains "params" key or "files" key will be executed by POST HTTP request.
Task plan without "params" key will be executed by GET HTTP request.

#### Call pageflow API
```json
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

#### Call task plan with multiple requests (step by step)
```json
[
        "sync", // it's important! need for executing task plan step by step (synchronously)
        {
                "url" : "/webmvc/api/pageflow/myproject/testflow",
                "params" : {
                        "operation" : "START",
                        "pfParams" : {
                                "param1" : 9472,
                                "param2" : "test string param",
                                "param3" : {
                                        "key1" : "val1",
                                        "key2" : "val2"
                                }
                        }
                }
        },
        {
                "url" : "/webmvc/api/pageflow/myproject/testflow",
                "params": {
                        "operation": "RESUME",
                        "instanceId": "$_previous_response.content['instanceId']$",
                }
        }
]
```
**sync** keyword before requests entries is important, it's necessary to make requests from the task plan synchronously 
(step by step). Note the value of the parameter 'instanceId' from the second request entry. It contains string enclosed
in the '$' character.  This string will be compiled to appropriate value by the following algorithm:
* **_previoud_response** substring references to the last response from the previous request
* **content** substring references to the **[content](http://docs.python-requests.org/en/master/api/#requests.Response.content)** 
property of the response object (byte object will be converted to dict)
* **['instanceId']** references to the dict item that was parsed from the previous response content. 
Eg. the previous response content looks like that 
```json
{
  "instanceId":"9b2af428-873a-4096-9439-3673fb07ac66",
  "item":{
    "inputParams":{
      "TheThirdParam":{"key1":"val1","key2":"val2"},
      "theSecondParam":"test string param",
      "theFirstParam":9472
    },
    "type":"THTMLFormItem",
    "body":{
      "viewName":"[fabulous]testflow1",
      "js":null,
      "html":"<fab-form>\\n    the first form\\n</fab-form>                                                           ",
      "hash":"a3e2e8d2b8df9ac3"
    }
  }
}
```
, string **"$_previous_response.content['instanceId']$"** will be compiled to **9b2af428-873a-4096-9439-3673fb07ac66**


Also it's possible to use value from the previous response in the url string, eg. to download file after it has uploaded
(we need tempKey value from the file upload response)
```json
[
        "sync",
        {
                "url": "/webmvc/_upload?storage=FILE",
                "files": ["/paht/to/file/with.extension"]

        },
        {
                "url": "/webmvc/_download?key=$_previous_response.content['tempKey']$"
        }
]
```