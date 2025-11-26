from flask import Flask, request, Response, jsonify
from attendance_queue_processor import AttendanceQueueProcessor
from dotenv import load_dotenv
import os
from datetime import datetime

from SaveDTRLog import SaveDTRLog
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Global queue processor instance (will be initialized in main)
queue_processor : AttendanceQueueProcessor | None = None

@app.route('/iclock/getrequest', methods=['GET'])
def handle_ping():
    print("Device Ping Received")
    print(request.args)
    return Response("OK", content_type='text/plain')


@app.route('/iclock/cdata', methods=['POST'])
def handle_data():
    if queue_processor is None:
        return Response("Service not ready", content_type='text/plain'), 503

    print("Data Received from Device")
    print("args:")
    print(request.args)
    print("data:")
    print(request.data.decode('utf-8'))

    # Check if table is ATTLOG
    table = request.args.get('table')

    if table != 'ATTLOG':
        return Response("OK", content_type='text/plain')

    try:
        # Get the raw data and decode it
        raw_data = request.data.decode('utf-8')

        # Split by whitespace
        parts = raw_data.split()

        if len(parts) >= 2:
            # Get scanning number (index 0)
            scanning_no = parts[0]
            action_type: int = int(parts[3])

            # Get date and time (index 1 and 2)
            log_date_str = f"{parts[1]} {parts[2]}"
            log_date = datetime.strptime(log_date_str, "%Y-%m-%d %H:%M:%S")

            # Create DTO (you'll need to provide the ouid value)
            dto = SaveDTRLog(
                ouid= int(os.getenv('OUID', 0)),  # Set this based on your logic
                scanning_no=scanning_no,
                log_date=log_date
            )

            # Add to queue
            queue_processor.add_task(dto)

            print(f"Queued task: {scanning_no} at {log_date}")

    except Exception as e:
        print(f"Error processing ATTLOG data: {e}")

    return Response("OK", content_type='text/plain')


@app.route('/api/submit', methods=['POST'])
def submit_task():
    """API endpoint to receive and queue tasks"""
    try:
        data = request.get_json()
        if queue_processor is None:
            return jsonify({
                'status': 'error',
                'message': 'Queue processor not initialized'
            }), 503
        
        # Add task to queue
        queue_processor.add_task(data)
        
        return jsonify({
            'status': 'success',
            'message': 'Task queued successfully',
            'queue_size': queue_processor.get_queue_size()
        }), 202
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/queue/status', methods=['GET'])
def queue_status():

    if queue_processor is None:
        return jsonify({
            'status': 'error',
            'message': 'Queue processor not initialized'
        }), 503

    return jsonify({
        'queue_size': queue_processor.get_queue_size()
    })


def main():
    """Main function to initialize and run the application"""
    global queue_processor
    
    # Load configuration from environment variables
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Initialize the task queue processor
    queue_processor = AttendanceQueueProcessor()
    
    # Start the background worker
    queue_processor.start()
    
    try:
        # Run Flask app
        print(f"Starting Flask app on {HOST}:{PORT}")
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        # Cleanup
        queue_processor.stop()


if __name__ == '__main__':
    main()
