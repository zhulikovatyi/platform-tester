# Test tool
api_report.py make requests to the pageflow (hardcoded) API by multiple user session.
"credential" file contains login:password pairs line by line

### How to run
```bash
cat credentials | python api_report.py -c --host=<server-host> --port=<server-port>
// ex: cat credentials | python api_report.py -c --host=172.17.0.2 --port=8330
```

Minimal python version is 3.5