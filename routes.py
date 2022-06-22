import datetime
from flask import Blueprint, current_app, redirect, render_template, request, url_for
import uuid

pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")

@pages.context_processor
def make_date_range_global():
    def date_range(start_date):
        date_arr = [ start_date + datetime.timedelta(days=day) for day in range(-3, 4)]
        return date_arr
    return {'date_range': date_range}

@pages.route("/")
def index():
    if request.args.get('date'):
        selected_date = datetime.datetime.fromisoformat(request.args.get('date'))
    else:
        selected_date = datetime.datetime.today()
    
    habits_on_date = current_app.db.habits.find({"added":{"$lte": selected_date}})

    completed = [
        habit["habit"]
        for habit in current_app.db.completions.find({"date": selected_date})
    ]
    return render_template(
        "index.html",
        title="Habit Tracker - HOME",
        habits=habits_on_date,
        completed=completed,
        selected_date=selected_date
        )


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    selected_date = today_at_midnight()
    if request.method == "POST":
        current_app.db.habits.insert_one({
            "_id": uuid.uuid4().hex,
            "name": request.form.get("habits"),
            "added": selected_date
        })

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=selected_date)


@pages.route('/complete', methods=['POST'])
def complete():

    date_str = request.form.get('date')
    habit_marked = request.form.get('habitId')
    date = datetime.datetime.fromisoformat(date_str)
    current_app.db.completions.insert_one({"date": date, "habit":habit_marked})

    return redirect(url_for('habits.index', date=date_str))

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)
