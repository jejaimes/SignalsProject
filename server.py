from flask import Flask, json, request
from scipy.misc import electrocardiogram
import numpy as np
from f_SignalFunctions import PanTompkins, filtMediaMovil
from flask_cors import CORS, cross_origin

api = Flask(__name__)
cors = CORS(api)
api.config['CORS_HEADERS'] = 'Content-Type'

ecg = electrocardiogram()
taco = np.array([])
x_ecg = []
y_ecg = []
hr = 70
i = 0

@api.route('/taco',methods = ['POST', 'GET'])
@cross_origin()
def tacoAPI():
   global x_ecg, y_ecg, hr, taco
   if request.method == 'POST':
      d = np.array(json.loads(request.data))
      if not np.size(d):
         return ""
      x_ecg = np.concatenate((x_ecg,d[0]))
      y_ecg = np.concatenate((y_ecg,d[1]))
      v_ECGFilt = filtMediaMovil(y_ecg, 100, 50)
      v_Taco, v_Taco_Time, v_PeaksInd = PanTompkins(y_ecg, 100, v_ECGFilt, x_ecg)
      taco = np.concatenate((v_Taco_Time.reshape((len(v_Taco_Time), 1)), v_Taco.reshape((len(v_Taco),1))), axis=1)
      hr = int(len(v_PeaksInd)/((len(x_ecg)/(100*60))))
      print(hr)
      return ""
   else:
      d = {
         "hr": hr,
         "taco": taco.tolist()
      }
      return json.dumps(d)

@api.route('/ECG', methods=['GET'])
@cross_origin()
def get_ECG():
    global i
    i += 1
    return json.dumps(ecg[i])

if __name__ == '__main__':
    api.run() 