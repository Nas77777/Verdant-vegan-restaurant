from flask import Flask, render_template, request, jsonify, session


app = Flask(__name__)

app.secret_key = 'your_secret_key'


available_times = {
    "2025-03-04": ["10:00 AM", "11:00 AM", "2:00 PM"],
    "2025-03-02": ["9:00 AM", "1:00 PM"],
    "2025-03-03": ["8:00 AM", "12:00 PM", "4:00 PM"]
}

reservations = {}

@app.route('/')
def index():
    return render_template('date&time-3.html')


@app.route('/get-available-times')
def get_available_times():
    date = request.args.get('date') 

    times = available_times.get(date, [])
    booked_times = reservations.get(date, [])
    available_slots = [time for time in times if time not in booked_times]

    return jsonify({"times": available_slots})

@app.route('/select-time', methods=['POST'])
def select_time():
    data = request.get_json()
    date = data.get('formattedDate')
    time = data.get('time')

    session['formattedDate'] = date
    session['selectedTime'] = time

    if not date or not time:
        return jsonify({"message": "Invalid input"}), 400

    
    print(f"Picked Date: {date}, Picked Time: {time}")

    if date not in reservations:
        reservations[date] = []
    reservations[date].append(time)

    return jsonify({"message": f"Reservation confirmed for {date} at {time}!"})

if __name__ == '__main__':
    app.run(debug=True)
