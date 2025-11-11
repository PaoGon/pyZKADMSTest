from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/iclock/getrequest', methods=['GET'])
def handle_ping():
    print("Device Ping Received")
    print(request.args)
    return Response("OK", content_type='text/plain')

@app.route('/iclock/cdata', methods=['POST'])
def handle_data():
    print("Data Received from Device")
    print(request.args)
    print(request.data.decode('utf-8'))
    return Response("OK", content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
