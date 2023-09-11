from flask import Flask, render_template, request, url_for, flash, redirect
import CRP_Stage2
import CRP_Stage2_SQA
from werkzeug.exceptions import abort

app = Flask(import_name=__name__)
app.config['SECRET_KEY'] = '565656'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list")
def list_devices():
    return render_template("list.html", CP_LIST=CRP_Stage2_SQA.SQAListAllObjects(output=False))

@app.route("/SystemWideAllTimeStats")
def all_time_stats():
    number_of_days = CRP_Stage2_SQA.SQATotalDays()
    #print(f'number_of_days = {number_of_days}')
    total_data_used = CRP_Stage2_SQA.WebSQLAllTimeSystemDataUsage()
    #print(f'total_data_used = {total_data_used}')
    last_100_total_data_used = CRP_Stage2_SQA.WebSQALastXTotalUsage(day_limit = 100)
    #print(f'Last 100 total data = {last_100_total_data_used}')
    last_100_moving_average = last_100_total_data_used / 100
    #print(f'100 day moving avg = {last_100_moving_average}')
    return render_template("systemwidealltime.html", TOTAL_DAYS=number_of_days,
                           TOTAL_DATA = total_data_used,
                           MOVING_AVG = last_100_moving_average)

@app.route("/SystemWideDailyUsage")
def system_wide_daily_usage():
    #returns a list of lists like: [(datetime.date(2023, 9, 5), 56513.85054016113), (datetime.date(2023, 9, 4), 51803.09237766266), (datetime.date(2023, 9, 3), 55848.53785228729)]
    return render_template("systemwidedailyusage.html", CP_LIST=CRP_Stage2_SQA.WebSQASystemDailyUsage())

@app.route("/top20day")
def top_20day():
    return render_template("top20day.html", CP_DICT=CRP_Stage2_SQA.SQAFindTopXHighestDays(top_x=20))

@app.route("/top20alltime")
def top_20alltime():
    return render_template("top20alltime.html", CP_DICT=CRP_Stage2_SQA.SQAFindTopXDeviceUsage(top_x=20))

#This route pulls the device summary info and pushes it back to the table
@app.route("/device_info")
def get_device_info():
    return render_template("device_info.html", CP_DICT=CRP_Stage2_SQA.WebSQLOutputObjectInfoByName(cp_name=request.args["cp"]))

#This route loads the device summary page and populates the device drop down list
@app.route("/show_device_summary")
def show_device_summary():
    return render_template("show_device_summary.html", CP_LIST=CRP_Stage2_SQA.SQAListAllObjects(output=False))

#This route pulls the device usage info and pushes it back to the table
@app.route("/device_usage")
def get_device_usage():
    #Data from the web page selection is returned as 
    #ImmutableMultiDict([('cp', 'BAW-CP1'), ('sort_by_value', 'Usage'), ('sort_order_value', 'Asc')])
    #print(f'Requested CP is: {request.args}')
    '''
    if request.args["min_data_usage"] != 0:
        #print(f'min_data_request = {request.args["min_data_usage"]}')
        cp_dict = CRP_Stage2.WebSQLShowUsageByName(cp_name=request.args["cp"], 
                                                sort_order_value=request.args["sort_order_value"], 
                                                sort_by_value=request.args["sort_by_value"], 
                                                response_limit=request.args["response_limit"],
                                                min_data_usage=request.args["min_data_usage"])
        return render_template("device_usage.html", CP_DICT=cp_dict)
    elif request.args["min_data_usage"] == 0:
        cp_dict = CRP_Stage2.WebSQLShowUsageByName(cp_name=request.args["cp"], 
                                                sort_order_value=request.args["sort_order_value"], 
                                                sort_by_value=request.args["sort_by_value"], 
                                                response_limit=request.args["response_limit"])
        return render_template("device_usage.html", CP_DICT=cp_dict)
    '''
    cp_dict = CRP_Stage2.WebSQLShowUsageByName(cp_name=request.args["cp"], 
                                                sort_order_value=request.args["sort_order_value"], 
                                                sort_by_value=request.args["sort_by_value"], 
                                                response_limit=request.args["response_limit"],
                                                min_data_usage=request.args["min_data_usage"])
    return render_template("device_usage.html", CP_DICT=cp_dict)
#This route loads the device summary page and populates the device drop down list
@app.route("/show_device_usage")
def show_device_usage():
    return render_template("show_device_usage.html", CP_LIST=CRP_Stage2_SQA.SQAListAllObjects(output=False))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

