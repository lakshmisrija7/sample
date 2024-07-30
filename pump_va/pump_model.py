from flask import Flask, render_template, request, send_from_directory, make_response,jsonify
import json

from static.spectrum_model import pump_equipment
app = Flask(__name__)
fault_type = None
spectrum_analysis_model = pump_equipment()
@app.route("/")
def home():
    return render_template("pump_main.html")
    
@app.route('/vibrationData', methods=["GET", "POST"])
def vibration_data():
    global fault_type
    fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z,time_x,time_y,time_z = spectrum_analysis_model.get_frequency_domain_data(fault_type)
    x_time_graph_data =  {"timestamp": list(time_x),  "amplitude": list(ts_amp_x)  }
    updated_x_graphdata = [{"Time": tstamp, "Amplitude": amp} for tstamp, amp in zip( x_time_graph_data["timestamp"],  x_time_graph_data["amplitude"])]
    
    y_time_graph_data =  {"timestamp": list(time_y),  "amplitude": list(ts_amp_y)  }
    updated_y_graphdata = [{"Time": tstamp, "Amplitude": amp} for tstamp, amp in zip( y_time_graph_data["timestamp"],  y_time_graph_data["amplitude"])]
    
    z_time_graph_data =  {"timestamp": list(time_z),  "amplitude": list(ts_amp_z)  }
    updated_z_graphdata = [{"Time": tstamp, "Amplitude": amp} for tstamp, amp in zip( z_time_graph_data["timestamp"],  z_time_graph_data["amplitude"])]
    
    # x_freq,x_amp,y_freq,y_amp,z_freq,z_amp = spectrum_analysis_model.get_freq_domain_data(fault_type,rotation_speed,sampling_rate,duration,no_of_balls)
    x_data = {
    "frequency": list(fft_freq_x),  
    "amplitude": list(fft_amp_x)  
}
    updated_xdata = [{"frequency": freq, "amplitude": amp} for freq, amp in zip(x_data["frequency"], x_data["amplitude"])]
    
    y_data = {
    "frequency": list(fft_freq_y),  
    "amplitude": list(fft_amp_y)  
}
    updated_ydata = [{"frequency": freq, "amplitude": amp} for freq, amp in zip(y_data["frequency"], y_data["amplitude"])]
    z_data = {
    "frequency": list(fft_freq_z),  
    "amplitude": list(fft_amp_z)  
}
    updated_zdata = [{"frequency": freq, "amplitude": amp} for freq, amp in zip(z_data["frequency"], z_data["amplitude"])]
    
    data = {
        "x_data": updated_xdata,
        "y_data": updated_ydata,
        "z_data": updated_zdata,
        "time_x_data":  updated_x_graphdata,
        "time_y_data":  updated_y_graphdata,
        "time_z_data":  updated_z_graphdata,
        
    }
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response
    # return data



@app.route("/NormalDataRoute", methods=["GET"])
def getNormalData():
    global fault_type
    fault_type = None
    return "Generating Normal Data"

@app.route("/unbalanceDataRoute", methods=["GET"])
def unbalance_fault_Data():
    global fault_type
    fault_type = "unbalance"
    return "Fault Induced: unbalance"

@app.route("/misalignmentDataRoute", methods=["GET"])
def misalignmnet_fault_Data():
    global fault_type
    fault_type = "misalignment"
    return "Fault Induced: misalignment"

@app.route("/eccentricityDataRoute", methods=["GET"])
def eccentricity_fault_tData():
    global fault_type
    fault_type = "eccentricity"
    return "Fault Induced: eccentricity"

@app.route("/bent_shaftDataRoute", methods=["GET"])
def bent_shaft_fault_tData():
    global fault_type
    fault_type = "bent_shaft"
    return "Fault Induced: bent_shaft"

@app.route("/starvationDataRoute", methods=["GET"])
def starvation_fault_tData():
    global fault_type
    fault_type = "starvation"
    return "Fault Induced: starvation"

@app.route("/broken_impellerDataRoute", methods=["GET"])
def broken_impeller_fault_tData():
    global fault_type
    fault_type = "broken_impeller"
    return "Fault Induced: broken_impeller"

@app.route("/cavitationDataRoute", methods=["GET"])
def cavitation_fault_tData():
    global fault_type
    fault_type = "cavitation"
    return "Fault Induced: cavitation"

@app.route("/innerracefaultDataRoute", methods=["GET"])
def innerrace_fault_Data():
    global fault_type
    fault_type = "innerrace_fault"
    return "Fault Induced: innerrace"

@app.route("/outerracefaultDataRoute", methods=["GET"])
def outerrace_fault_Data():
    global fault_type
    fault_type = "outerrace_fault"
    return "Fault Induced: outerrace"

@app.route("/cagefaultDataRoute", methods=["GET"])
def cage_fault_Data():
    global fault_type
    fault_type = "cage_fault"
    return "Fault Induced: cage fault"

@app.route("/rollingelementfaultfaultDataRoute", methods=["GET"])
def rolling_element_fault_Data():
    global fault_type
    fault_type = "rolling_element_fault"
    return "Fault Induced: rolling element"

if __name__=="__main__":
    app.run(debug=True, port=2001)