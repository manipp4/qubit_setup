// acqiris_QuantroDLL2.h

#pragma once

#include "stdafx.h"

using namespace std;

void initacqiris_QuantroDLL2();

/*
The BifurcationMap class.
All the parameters have to be initialized by the client, usually with a ctypes pointer:

Example of a python client:

        bm = acqirislib.BifurcationMap()
        bm.activeChannels = 15

        bm.nLoops = 20
        trends = zeros((4,params["numberOfSegments"]*bm.nLoops))
        bm.trends = trends.ctypes.data

		#...

After initializing all the variables, call init() to initialize the data processing routine itself.
Then call add(waveform) to process a single waveform.
Call finish() to finish the data processing.
*/
class BifurcationMap
{
public:
	~BifurcationMap();
	BifurcationMap();

	double rotation[2];
	double costable[2],sintable[2];
	double* rotatedWaveform;
	double *means,*trends,*averages,*probabilities,*crossProbabilities;
	unsigned int nPoints,nSegments,activeChannels;
	int index,nLoops;


	void setRotation(double r1,double r2);
	void init();
	void add(double *matrix);
	void finish();
};


class Demodulator // Performs a digital demodulation on a single signal or on two signals in quadrature, taking into account several corrections on the measured signals
{
public:
	Demodulator();
	~Demodulator();

//	6 corrections coefficients (offsets, gains, and rotation angles for two channels in quadratures) for a set of discrete frequencies, are stored in 7 tables that are properties of the class

	int dimensionF; //size of all tables = number of frequencies for which the corrections are known

	vector <double> tableF;
	vector <double> tableOffsetI;
	vector <double> tableOffsetQ;
	vector <double> tableGainI;
	vector <double> tableGainQ;
	vector <double> tableAngleI;
	vector <double> tableAngleQ;

	double *frequencies;
	double *quadratures;
	double *quadraturesAverages;//

	// returns the table index of a given frequency in the correction table if it exists or -1 otherwise
	int indexCorrection(double f);
	//replace or add the offset, gain, and rotation angle corrections for I and Q, for a given frequency 
	void setCorrections(double f,double Io, double Qo, double Ig, double Qg,  double Ir, double Qr);
	//Demodulation functions  using one signal or two signal in quadratures and returning I and Q, or A and phi
	void demodulate1ChAPhi(double *ChA,double *horPos, int nbrSegments, int nbrSamplesPerSegment, double samplingTime, double frequency, double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayA,double *arrayPhi,double *arrayMeanA,double *arrayMeanPhi, bool extraFast, double* P_Time_us);
	void demodulate2ChAPhi(double *ChA,double *ChB,double *horPos,int nbrSegments,int nbrSamplesPerSegment,double samplingTime,double frequency,double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayA, double *arrayPhi,double *arrayMeanA, double *arrayMeanPhi,  bool extraFast, double* P_Time_us);
	void demodulate1ChIQ(double *ChA, double *horPos,int nbrSegments, int nbrSamplesPerSegment, double samplingTime, double frequency, double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayI,double *arrayQ,double *arrayMeanI,double *arrayMeanQ, bool extraFast, double* P_Time_us);
	void demodulate2ChIQ(double *ChA,double *ChB,double *horPos,int nbrSegments,int nbrSamplesPerSegment,double samplingTime,double frequency,double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayI, double *arrayQ,double *arrayMeanI, double *arrayMeanQ, bool extraFast, double* P_Time_us);
	void Demodulator::demodulate(bool twoCh,double *ChA, double *ChB, double *horPos, double nbrSegments,double nbrSamplesPerSegment,double samplingTime,double frequency,double phase,int intervalMode,bool tryCorrec,bool averageOnly,bool APhi,int *nbrIntervalsPerSegment,double *array1,double *array2,double *arrayMean1,double *arrayMean2)
	
};

class MultiplexedBifurcationMap // Performs a digital demodulation on a single signal or on two signals in quadrature, taking into account several corrections on the measured signals
{
public:
	int dimensionF; 
	vector <double> tableF;
	vector <double> tableIoffset;
	vector <double> tableQoffset;
	vector <double> tableAngle;
	
	MultiplexedBifurcationMap();
	~MultiplexedBifurcationMap();
	
	int indexCorrection(double f);
	void setRotation(double f,double offsetI, double offsetQ, double angle);
	void rotateAndClicks(double f, double *trends, int numberOfSegments,double *clicks);
	void convertToProbabilities(int nbQB, int nbSegments, double *r, double *proba);
};
