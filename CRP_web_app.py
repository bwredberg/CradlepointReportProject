from flask import Flask, render_template, request, url_for, flash, redirect
import CRP_Stage2
from werkzeug.exceptions import abort

app = Flask(import_name=__name__)
app.config['SECRET_KEY'] = '565656'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list")
def list_devices():
    return render_template("list.html", CP_LIST=CRP_Stage2.SQLListAllObjects(output=False))

#This route pulls the device summary info and pushes it back to the table
@app.route("/device_info")
def get_device_info():
    return render_template("device_info.html", CP_DICT=CRP_Stage2.WebSQLOutputObjectInfoByName(cp_name=request.args["cp"]))

#This route loads the device summary page and populates the device drop down list
@app.route("/show_device_summary")
def show_device_summary():
    return render_template("show_device_summary.html", CP_LIST=CRP_Stage2.SQLListAllObjects(output=False))

#This route pulls the device usage info and pushes it back to the table
@app.route("/device_usage")
def get_device_usage():
    #ImmutableMultiDict([('cp', 'BAW-CP1'), ('sort_by_value', 'Usage'), ('sort_order_value', 'Asc')])
    #print(f'Requested CP is: {request.args}')
    cp_tuple = CRP_Stage2.WebSQLShowUsageByName(cp_name=request.args["cp"], sort_order_value=request.args["sort_order_value"], sort_by_value=request.args["sort_by_value"])
    return render_template("device_usage.html", CP_LIST=cp_tuple)

#This route loads the device summary page and populates the device drop down list
@app.route("/show_device_usage")
def show_device_usage():
    return render_template("show_device_usage.html", CP_LIST=CRP_Stage2.SQLListAllObjects(output=False))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

