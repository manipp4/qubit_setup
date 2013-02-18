// acqiris.h

#pragma once
#include "nr3.h"
#define PI 3.14159268
#include <vector>
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
	//Demodulation using one signal or two signal in quadratures
	void demodulate1(double *ChA, double nbrSegments, double nbrSamplesPerSegment, double samplingTime, double frequency, double phase, double *arrayI, double *arrayQ, double *Imean, double *Qmean);
	void demodulate2(double *ChA, double *ChB, double nbrSegments, double nbrSamplesPerSegment, double samplingTime, double frequency, double phase, double *arrayI, double *arrayQ, double *Imean, double *Qmean);

};
/*

class MultiplexedBifurcationMap
{
public:
	~MultiplexedBifurcationMap();
	MultiplexedBifurcationMap();

	double *rotations;
	double costable[2],sintable[2];
	double *rotatedWaveform;
	double *means,*trends,*averages,*probabilities,*crossProbabilities;
	unsigned int nPoints,nSegments,activeChannels;
	int index,nLoops;


	
	void add(double *frequencies, double *trends, int numberOfFrequencies, int numberOfsegments,double *results);
	void convertToProbabilities(int nbQB, int nbSegments, double *r, double *proba);
	void finish();
};
	*/
