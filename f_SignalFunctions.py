import numpy as np
import scipy.signal as sig # Análisis de señal


def filtMediaMovil(v_ECGSig, s_FsHz, s_ElectricNoiseHz):
    s_ElectricNoiseAveSam = int(np.ceil(s_FsHz / s_ElectricNoiseHz))
    v_ECGFilt = np.zeros(np.size(v_ECGSig))
    for s_Ind in range(np.size(v_ECGFilt)):
        s_FirstInd = s_Ind - (s_ElectricNoiseAveSam - 1)
        if s_FirstInd < 0:
            s_FirstInd = 0
        v_ECGFilt[s_Ind] = np.mean(v_ECGSig[s_FirstInd:s_Ind + 1])
    return v_ECGFilt


def PanTompkins(v_ECGSig, s_FsHz, v_ECGFilt, v_Time):
    # Obtención primera derivada, filtro pasa altas - QRS
    v_ECGFiltDiff = np.zeros(np.size(v_ECGSig))
    v_ECGFiltDiff[1:] = np.diff(v_ECGSig)
    v_ECGFiltDiff[0] = v_ECGFiltDiff[1]
    
    # Atenuar lo pequeña y ampliar lo que es grande, acumula los dos picos anteriores en uno solo
    v_ECGFiltDiffSqrt = v_ECGFiltDiff**2
    s_AccSumWinSizeSec = 0.03 # Ventana de 30 ms
    s_AccSumWinHalfSizeSec = s_AccSumWinSizeSec / 2.0 # Toma la mitad del intervalo
    s_AccSumWinHalfSizeSam = \
        int(np.round(s_AccSumWinHalfSizeSec * s_FsHz)) # Nos da el núnmero de puntos de la ventana
    v_ECGFiltDiffSqrtSum = \
        np.zeros(np.size(v_ECGFiltDiffSqrt))
    for s_Count in range(np.size(v_ECGFiltDiffSqrtSum)):
        s_FirstInd = s_Count - s_AccSumWinHalfSizeSam
        s_LastInd = s_Count + s_AccSumWinHalfSizeSam
        if s_FirstInd < 0:
            s_FirstInd = 0
        if s_LastInd >= np.size(v_ECGFiltDiffSqrtSum):
            s_LastInd = np.size(v_ECGFiltDiffSqrtSum)
        v_ECGFiltDiffSqrtSum[s_Count] = \
            np.mean(
                v_ECGFiltDiffSqrt[s_FirstInd:s_LastInd + 1])
            
    
    v_PeaksInd = sig.find_peaks(v_ECGFiltDiffSqrtSum)
    v_Peaks = v_ECGFiltDiffSqrtSum[v_PeaksInd[0]]
    s_PeaksMean = np.mean(v_Peaks)
    s_PeaksStd = np.std(v_Peaks)
    s_MinTresh = s_PeaksMean + 1 * s_PeaksStd
    s_MaxTresh = s_PeaksMean + 8 * s_PeaksStd
    s_QRSInterDurSec = 0.2
    s_MinDurSam = np.round(s_QRSInterDurSec * s_FsHz)
    v_PeaksInd = sig.find_peaks(v_ECGFiltDiffSqrtSum,
                                height=[s_MinTresh, s_MaxTresh],
                                distance=s_MinDurSam)
    v_PeaksInd = v_PeaksInd[0]
    # Corregir esa identificación de picos corridos
    s_QRSPeakAdjustHalfWinSec = 0.05
    s_QRSPeakAdjustHalfWinSam = \
        int(np.round(s_QRSPeakAdjustHalfWinSec * s_FsHz))
    for s_Count in range(np.size(v_PeaksInd)):
        s_Ind = v_PeaksInd[s_Count]
        s_FirstInd = s_Ind - s_QRSPeakAdjustHalfWinSam
        s_LastInd = s_Ind + s_QRSPeakAdjustHalfWinSam
        if s_FirstInd < 0:
            s_FirstInd = 0
        if s_LastInd >= np.size(v_ECGSig):
            s_LastInd = np.size(v_ECGSig)
        v_Aux = v_ECGFilt[s_FirstInd:s_LastInd + 1]
        v_Ind1 = sig.find_peaks(v_Aux)
        if np.size(v_Ind1[0]) == 0:
            continue
        s_Ind2 = np.argmax(v_Aux[v_Ind1[0]])
        s_Ind = int(v_Ind1[0][s_Ind2])
        v_PeaksInd[s_Count] = s_FirstInd + s_Ind
        
    # Tacograma 
    v_Taco = np.diff(v_PeaksInd) / s_FsHz
    v_Time_Taco = v_Time[v_PeaksInd[1:]]
    
    return v_Taco, v_Time_Taco, v_PeaksInd