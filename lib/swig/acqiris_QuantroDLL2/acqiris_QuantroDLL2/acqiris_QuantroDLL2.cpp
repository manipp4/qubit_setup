// This is the main DLL file.

#include "stdafx.h"
using namespace std;

#include "acqiris_QuantroDLL2.h"

const double PI = std::atan(1.0)*4;

void initacqiris_QuantroDLL2(){};

BifurcationMap::BifurcationMap() //creator
{
	setRotation(0,0);
}

BifurcationMap::~BifurcationMap() //destructor
{
}

//This initializes the bifurcation class...
void BifurcationMap::init()
{
	index = 0;
	//Set all the averages to 0
	for(int k=0;k<4;k++)
		for(int i = 0;i<nPoints;i++)
			averages[i+k*nPoints]=0;
	
	probabilities[0]=0;
	probabilities[1]=0;

	for(int i = 0;i< 4;i++)
		crossProbabilities[i]=0;
}

//This processes "waveform" and calculates probabilities, averages, etc...
void BifurcationMap::add(double *matrix)
{
	//Loop over all segments
	for(int j=0;j<nSegments;j++)
	{
		//Loop over all channels
		for(int k=0;k<4;k++)
		{
			int trendind = index+k*nSegments*nLoops;
			trends[trendind]= 0;
			for(int i=0;i<nPoints;i++)
			{
				int ind = i+j*nPoints+k*nPoints*nSegments;
				trends[trendind]+=matrix[ind];
				averages[i+k*nPoints]+=matrix[ind];
			}
			trends[trendind]/=(double)nPoints;
		}
		bool switched1 = false;
		bool switched2 = false;
		if ((activeChannels & 3) == 3)
		{
			//Rotate the trend information to obtain the bifurcation criterion.
			double c = trends[index+0*nSegments*nLoops]*costable[0]+trends[index+1*nSegments*nLoops]*sintable[0];
			//Check the bifurcation criterion for channels 1 & 2.
			if (c>0)
			{
				switched1 = true;
				probabilities[0]+=1.0;
			}
		}
		if ((activeChannels & 12) == 12)
		{
			//Rotate the trend information to obtain the bifurcation criterion.
			double c = trends[index+2*nSegments*nLoops]*costable[1]+trends[index+3*nSegments*nLoops]*sintable[1];
			//Check the bifurcation criterion for channels 3 & 4.
			if (c>0)
			{
				switched2 = true;
				probabilities[1]+=1.0;
			}
		}
		//Add the switching event to the joint probability table containing P(00),P(10),P(01),P(11)
		if (activeChannels == 15)
			crossProbabilities[(switched1 == true ? 2:0)+(switched2 == true ? 1:0)]+=1.0;
		index++;
	}
}

//Sets the rotation angles for the bifurcation map procedure.
void BifurcationMap::setRotation(double r1,double r2)
{
	rotation[0] = r1;
	rotation[1] = r2;
	costable[0] = cos(r1);
	sintable[0] = sin(r1);
	costable[1] = cos(r2);
	sintable[1] = sin(r2);
}

//This finishes the data treatment.
void BifurcationMap::finish()
{
	//Finish the data processing by normalizing the probabilities and averages.
	probabilities[0]/=(double)index;
	probabilities[1]/=(double)index;

	for(int i = 0;i< 4;i++)
		crossProbabilities[i]/=(double)index;

	for(int k = 0;k< 4;k++)
	{
		for(int i=0;i<nPoints;i++)
		{
			averages[i+k*nPoints]/=(double)index;
		}
	}
}

Demodulator::Demodulator()	  // creator
{
	dimensionF=0;			 // set table size to zero (no frequencies known)
}

Demodulator::~Demodulator() //destructor
{

}

// returns the table index of a given frequency in the correction table if it exists or -1 otherwise
int Demodulator::indexCorrection(double f)
{
	// cout << "Demodulator::indexCorrection" << endl;
	int index = -1;
	if (dimensionF>0)
		{
			for (int i=0;i<dimensionF;i++)
			{
				if (tableF[i] == f) index = i;
			};
		}
	return index;
}

//replace or add the offset, gain, and rotation angle corrections for I and Q, for a given frequency 
void Demodulator::setCorrections(double f,double offsetI, double offsetQ, double gainI, double gainQ,  double angleI, double angleQ)
{
	// cout << "Demodulator::setCorrections : ";
	int index=indexCorrection(f);
	if (index >=0 )
		{
			tableOffsetI[index] = offsetI;
			tableOffsetQ[index] = offsetQ;
			tableGainI[index] = gainI;
			tableGainQ[index] = gainQ;
			tableAngleI[index] = angleI;
			tableAngleQ[index] = angleQ;
		}
	else
		{
		dimensionF++;
		tableF.push_back(f);
		tableOffsetI.push_back(offsetI);
		tableOffsetQ.push_back(offsetQ);
		tableGainI.push_back(gainI);
		tableGainQ.push_back(gainQ);
		tableAngleI.push_back(angleI);
		tableAngleQ.push_back(angleQ);
		// cout << "adding new line" << endl;
		};
	// cout << "f,Io,Qo,Ig,Qg,Ir,Qr" << f << ' ' << offsetI << ' ' << offsetQ << ' ' << gainI << ' ' << gainQ << ' ' << angleI<< ' '  << angleQ << endl<<endl;

}

//// This function is for internal use only and should not be called by the client of the present DLL.
//// Use demodulate1ChIQ and demodulate2ChIQ or demodulate1ChAPhi and demodulate2ChAPhi  instead.
void Demodulator::demodulate(bool twoCh,double *ChA, double *ChB, double *horPos, double nbrSegments,double nbrSamplesPerSegment,double samplingTime,double frequency,double phase,int intervalMode,bool tryCorrec,bool averageOnly,bool APhi,int *nbrIntervalsPerSegment,double *array1,double *array2,double *arrayMean1,double *arrayMean2, bool extraFast)
{//	// cout << "PI = " << PI << endl;
	int i,j,p,q,r,nbrSamplesPerInterval,index=-1;
	double arg,deltaArg,I,Q,x,y,det;
	if (tryCorrec)									// Try to access corrections for the given frequency possibly stored in the demodulator class
	{	index=indexCorrection(frequency);
		if (index>=0) det=cos((double)tableAngleI[index]-(double)tableAngleQ[index]); //precomputes det (to be used for correcting I and Q)
	};
	double nbrSamplesPerHalfPeriod=1/(2*samplingTime*frequency); // precomputes number of samples per half-period
	// Define the numbers of demodulation intervals per segments and of samples per demodulation interval
	if(intervalMode>0)								//p demodulations over given integer number of half-period if possible, otherwise case below
	{	nbrSamplesPerInterval=nbrSamplesPerHalfPeriod*abs(intervalMode);
		*nbrIntervalsPerSegment=floor(nbrSamplesPerSegment/nbrSamplesPerInterval);
	};
	if((*nbrIntervalsPerSegment==0) || intervalMode==0)	//1 demodulation over maximum integer number of half-period if possible, otherwise case below
	{
		*nbrIntervalsPerSegment=1;
		nbrSamplesPerInterval=int(nbrSamplesPerHalfPeriod*(int)(nbrSamplesPerSegment/nbrSamplesPerHalfPeriod)+0.5);
	};
	if(nbrSamplesPerInterval==0 || intervalMode==-1)	//1 demodulation over full segment
	{	*nbrIntervalsPerSegment=1;
		nbrSamplesPerInterval=nbrSamplesPerSegment;
	};
	//precomputes argument increments of sin and cos functions and starts demodulation
	deltaArg=2*PI*frequency*samplingTime;
//	// cout << "frequency = " << frequency << " samplingTime = " << samplingTime << endl; 
	i=0;											//i index of arrayI and arrayQ (0 to nbrSegments*nbrIntervalsPerSegment-1)
	for(q=0;q<*nbrIntervalsPerSegment;q++)			//q index of demodulation interval (0 to nbrIntervalsPerSegment-1)
	{	arrayMean1[q]=0;							//initialize Imean and Qmean to zero for all intervals
		arrayMean2[q]=0;
	};
	for(p=0;p<nbrSegments;p++)						//Loop over all segments. p index of segment (0 to nbrSegments-1)
	{//	// cout << "segment = "<< p << endl;
		I=0;										//initialize quadratures capital I and capital Q to zero
		Q=0;
		j=p*nbrSamplesPerSegment;					// j sample index in ChA and ChB (0 to nbrSegments*nbrSamplesPerSegment-1)
		arg = phase+2*PI*frequency*horPos[p];								// initialise argument to phase+offsettime
		for(q=0;q<*nbrIntervalsPerSegment;q++)		//Loop over all demodulation intervals of a segment
		{//	// cout << "interval = "<< q << endl;
			for(r=0;r<nbrSamplesPerInterval;r++)	//Loop over all samples of a demodulation interval
			{//	// cout << "arg = " << arg << endl;
			//	// cout << "sample "<< j << " = " << ChA[j] << endl;
			//	// cout << "cos = " << cos(arg) << endl;
			//	// cout << "sin = " << sin(arg) << endl;
			//	// cout << "cos*ChA = " << ChA[j]*cos(arg) << endl;
				I+=ChA[j]*cos(arg);					//accumulate chA*Cos in I
				if(twoCh)	Q+=ChB[j]*cos(arg); else Q+=ChB[j]*sin(arg); //accumulate chB*Cos or chB*Sin in Q depending on 1 or two channels
				arg += deltaArg;					//increment argument
				j++;								// increment ChA and ChB index j (j=p*nbrSamplesPerSegment+q*nbrSamplesPerInterval+r)
			}; 
			//// cout << "I = " << I << " Q = " << Q << endl;
			I=2*I/nbrSamplesPerInterval;			//finish I and Q calculation;
			Q=2*Q/nbrSamplesPerInterval;
			//// cout << "I = " << I << " Q = " << Q << endl;
			if(index>=0)							//apply available and requested corrections
			{	// cout << "appplying corrections" << endl;
				if(twoCh)							// corrections when working on 2 channels I and Q
				{									//I'=((cos Ri)I+sin(Ri)Q)/Gi
													//Q'=((cos Rq)Q-sin(Rq)I)/Gq
													//I=[((cos Rq)Gi I' -(sin Rq)Gq Q']/det
													//Q=[((sin Ri)Gi I' +cos(Ri)Gq Q']/det
													//det=cos(Ri-Rq)
					x=(cos(tableAngleQ[index])*tableGainI[index]*I-sin(tableAngleQ[index])*tableGainQ[index]*Q)/det;
					y=(sin(tableAngleI[index])*tableGainI[index]*I+cos(tableAngleI[index])*tableGainQ[index]*Q)/det;
				}
				else								// corrections when working on 1 channels I
				{	x=(cos(tableAngleI[index])*I-sin(tableAngleI[index])*Q)*tableGainI[index];
					y=(sin(tableAngleI[index])*I+cos(tableAngleI[index])*Q)*tableGainI[index];
				};
				I=x;
				Q=y;
			};
			if(APhi) 
			{	x=sqrt(I*I+Q*Q);
				y=atan2(Q,I);
			}
			else
			{	x=I;y=Q;
			};
			if (! averageOnly)						//store I and Q in arrayI and arrayQ in case user asked for all segments
			{	array1[i]=x;
				array2[i]=y;
				i++;								//increment arrayI and arrayQ index
			};			
			arrayMean1[q]+=x;arrayMean2[q]+=y;		//accumulate for I and Q averaging
		};
	};
	for(q=0;q<*nbrIntervalsPerSegment;q++)			//complete I and Q averaging over all segments
	{	arrayMean1[q]/=nbrSegments;
		arrayMean2[q]/=nbrSegments;
	};
};

// Use demodulate1ChIQ to demodulate one channel I and return the demodulated quadratures
//	Digital demodulation by direct multiplication with cos and sin functions (no fourier transform). 
//	This function operates on one segment or a sequence of several segments
//	It demodulates over one or several sub-intervals of a segment (see intervalMode below)
//
// Input parameters:
//	ChA: pointer to the array in which the first quadrature (I) is stored (channel A)
//	nbrSegments: number of segments stored in ChA
//	nbrSamplesPerSegment: number of samples in each segment
//	samplingTime: time interval between two consecutive samples of a segment (in any units provided it is inverse from the frequency unit)
//	frequency: demodulation frequency (in any units provided it is inverse from the samplingTime unit)
//	phase: phase reference at the time of the first sample. Enters the (omega t + phase) argument of the cos and sin multiplicators
//	intervalMode: interval code used for demodulation:
//		intervalMode>0 means intervalMode half-periods if possible (otherwise try case below)
//		0 means 1 interval with length equal to the maximum integer number of half-periods in the segment length (otherwise do case below)
//		-1 means 1 interval with full segment length (allways possible)
//	tryCorrec: boolean telling wether gain, offset and IQ rotation corrections at the given frequency are to be performed (if present in memory)
//	averageOnly: boolean telling wether I and Q for all segments are to be returned (false) or only the average over all segments is to be returned (true).
// Output parameters
//	nbrIntervalsPerSegment: number of demodulation intervals per segment: 1 for intervalMode<=0 and max(1,floor(nbrSamplesPerSegment/nbrSamplesPerPeriod/abs(intervalMode)*2) for intervalMode>0;
//	arrayI,arrayQ: arrays of the nbrSegments*nbrIntervalsPerSegment I and Q quadratures when averageOnly is false (otherwise the two arrays are left empty) 
//	arrayMeanI,arrayMeanQ: arrays of the nbrIntervalsPerSegment I and Q values averaged over the nbrSegments segments
//	* P_Time_us: pointer to the evaluation duration of the function in 탎
//
void Demodulator::demodulate1ChIQ(double *ChA, double *horPos,int nbrSegments,int nbrSamplesPerSegment,double samplingTime, double frequency, double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayI,double *arrayQ,double *arrayMeanI,double *arrayMeanQ, bool extraFast, double *P_Time_us)
{
	// cout << "Demodulator::demodulate1ChIQ: "<<endl;
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut); //start the timer
	demodulate(false,ChA,ChA,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec,averageOnly,false,nbrIntervalsPerSegment,arrayI,arrayQ,arrayMeanI,arrayMeanQ,extraFast);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in 탎
	// cout<<"OK - duration = "<<*P_Time_us<< " microsec." <<endl;
};

// Use demodulate2ChIQ to demodulate 2 channels I and Q and return the demodulated quadratures
//	Digital demodulation by direct multiplication of I and Q with cos functions (no fourier transform). 
//	This function operates on one segment or a sequence of several segments
//	It demodulates over one or several sub-intervals of a segment (see intervalMode below)
//
// Input parameters:
//	ChA,ChB: pointers to the arrays in which the two quadratures (I and Q) are stored (channel A and B)
//	nbrSegments: number of segments stored in ChA and ChB
//	nbrSamplesPerSegment: number of samples in each segment
//	samplingTime: time interval between two consecutive samples of a segment (in any units provided it is inverse from the frequency unit)
//	frequency: demodulation frequency (in any units provided it is inverse from the samplingTime unit)
//	phase: phase reference at the time of the first sample. Enters the (omega t + phase) argument of the cos and sin multiplicators
//	intervalMode: interval code used for demodulation:
//		intervalMode>0 means intervalMode half-periods if possible (otherwise try case below)
//		0 means 1 interval with length equal to the maximum integer number of half-periods in the segment length (otherwise do case below)
//		-1 means 1 interval with full segment length (allways possible)
//	tryCorrec: boolean telling wether gain, offset and IQ rotation corrections at the given frequency are to be performed 
//	averageOnly: boolean telling wether I and Q for all segments are to be returned (false) or only the average over all segments is to be returned (true).
// Output parameters
//	nbrIntervalsPerSegment: number of demodulation intervals per segment: 1 for intervalMode<=0 and max(1,floor(nbrSamplesPerSegment/nbrSamplesPerPeriod/abs(intervalMode)*2) for intervalMode>0;
//	arrayI,arrayQ: arrays of the nbrSegments*nbrIntervalsPerSegment I and Q quadratures when averageOnly is false (otherwise the two arrays are left empty) 
//	arrayMeanI,arrayMeanQ: arrays of the nbrIntervalsPerSegment I and Q values averaged over the nbrSegments segments
//	* P_Time_us: pointer to the evaluation duration of the function in 탎
//
void Demodulator::demodulate2ChIQ(double *ChA,double *ChB, double *horPos, int nbrSegments, int nbrSamplesPerSegment,double samplingTime,double frequency,double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayI,double *arrayQ,double *arrayMeanI,double *arrayMeanQ, bool extraFast, double *P_Time_us)
{ 	// cout << "Demodulator::demodulate2ChIQ: "<<endl;
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut); //start the timer
	demodulate(true,ChA,ChB,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec,averageOnly,false,nbrIntervalsPerSegment,arrayI,arrayQ,arrayMeanI,arrayMeanQ,extraFast);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in 탎
	// cout<<"OK - duration = " <<*P_Time_us<< " microsec." <<endl;
};

// Use demodulate1ChAPhi to demodulate one channel I and return the demodulated amplitude A and phase Phi
//	Digital demodulation by direct multiplication with cos and sin functions (no fourier transform). 
//	This function operates on one segment or a sequence of several segments
//	It demodulates over one or several sub-intervals of a segment (see intervalMode below)
//
// Input parameters:
//	ChA: pointer to the array in which the first quadrature (I) is stored (channel A)
//	nbrSegments: number of segments stored in ChA
//	nbrSamplesPerSegment: number of samples in each segment
//	samplingTime: time interval between two consecutive samples of a segment (in any units provided it is inverse from the frequency unit)
//	frequency: demodulation frequency (in any units provided it is inverse from the samplingTime unit)
//	phase: phase reference at the time of the first sample. Enters the (omega t + phase) argument of the cos and sin multiplicators
//	intervalMode: interval code used for demodulation:
//		intervalMode>0 means intervalMode half-periods if possible (otherwise try case below)
//		0 means 1 interval with length equal to the maximum integer number of half-periods in the segment length (otherwise do case below)
//		-1 means 1 interval with full segment length (allways possible)
//	tryCorrec: boolean telling wether gain, offset and IQ rotation corrections at the given frequency are to be performed (if present in memory)
//	averageOnly: boolean telling wether I and Q for all segments are to be returned (false) or only the average over all segments is to be returned (true).
// Output parameters
//	nbrIntervalsPerSegment: number of demodulation intervals per segment: 1 for intervalMode<=0 and max(1,floor(nbrSamplesPerSegment/nbrSamplesPerPeriod/abs(intervalMode)*2) for intervalMode>0;
//	arrayA,arrayPhi: arrays of the nbrSegments*nbrIntervalsPerSegment amplitudes A and phase phi when averageOnly is false (otherwise the two arrays are left empty) 
//	arrayMeanA,arrayMeanPhi: arrays of the nbrIntervalsPerSegment A and Phi values averaged over the nbrSegments segments
//	* P_Time_us: pointer to the evaluation duration of the function in 탎
//
void Demodulator::demodulate1ChAPhi(double *ChA, double *horPos,int nbrSegments,int nbrSamplesPerSegment,double samplingTime, double frequency, double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayA,double *arrayPhi,double *arrayMeanA,double *arrayMeanPhi, bool extraFast, double *P_Time_us)
{ 	// cout << "Demodulator::demodulate1ChAPhi: ";
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut);			//start the timer
	demodulate(false,ChA,ChA,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec,averageOnly,true,nbrIntervalsPerSegment,arrayA,arrayPhi,arrayMeanA,arrayMeanPhi,extraFast);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in 탎
	// cout<<"OK - duration = " <<*P_Time_us<< " microsec." <<endl;
};

// Use demodulate2ChIQ to demodulate 2 channels I and Q and return the demodulated quadratures
//	Digital demodulation by direct multiplication of I and Q with cos functions (no fourier transform). 
//	This function operates on one segment or a sequence of several segments
//	It demodulates over one or several sub-intervals of a segment (see intervalMode below)
//
// Input parameters:
//	ChA,ChB: pointers to the arrays in which the two quadratures (I and Q) are stored (channel A and B)
//	nbrSegments: number of segments stored in ChA and ChB
//	nbrSamplesPerSegment: number of samples in each segment
//	samplingTime: time interval between two consecutive samples of a segment (in any units provided it is inverse from the frequency unit)
//	frequency: demodulation frequency (in any units provided it is inverse from the samplingTime unit)
//	phase: phase reference at the time of the first sample. Enters the (omega t + phase) argument of the cos and sin multiplicators
//	intervalMode: interval code used for demodulation:
//		intervalMode>0 means intervalMode half-periods if possible (otherwise try case below)
//		0 means 1 interval with length equal to the maximum integer number of half-periods in the segment length (otherwise do case below)
//		-1 means 1 interval with full segment length (allways possible)
//	tryCorrec: boolean telling wether gain, offset and IQ rotation corrections at the given frequency are to be performed 
//	averageOnly: boolean telling wether I and Q for all segments are to be returned (false) or only the average over all segments is to be returned (true).
// Output parameters
//	nbrIntervalsPerSegment: number of demodulation intervals per segment: 1 for intervalMode<=0 and max(1,floor(nbrSamplesPerSegment/nbrSamplesPerPeriod/abs(intervalMode)*2) for intervalMode>0;
//	arrayI,arrayQ: arrays of the nbrSegments*nbrIntervalsPerSegment I and Q quadratures when averageOnly is false (otherwise the two arrays are left empty) 
//	arrayMeanA,arrayMeanPhi: arrays of the nbrIntervalsPerSegment I and Q values averaged over the nbrSegments segments
//	* P_Time_us: pointer to the evaluation duration of the function in 탎
//
void Demodulator::demodulate2ChAPhi(double *ChA, double *horPos,double *ChB, int nbrSegments, int nbrSamplesPerSegment,double samplingTime,double frequency,double phase,int intervalMode,bool tryCorrec,bool averageOnly,int *nbrIntervalsPerSegment,double *arrayA,double *arrayPhi,double *arrayMeanA,double *arrayMeanPhi, bool extraFast, double *P_Time_us)
{	// cout << "Demodulator::demodulate2ChAPhi: ";
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut);			//start the timer
	demodulate(true,ChA,ChB,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec,averageOnly,true,nbrIntervalsPerSegment,arrayA,arrayPhi,arrayMeanA,arrayMeanPhi,extraFast);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in 탎
	// cout<<"OK - duration = " <<*P_Time_us<< " microsec." <<endl;
};

MultiplexedBifurcationMap::MultiplexedBifurcationMap()
{
	dimensionF=0;
}


MultiplexedBifurcationMap::~MultiplexedBifurcationMap()
{
}


int MultiplexedBifurcationMap::indexCorrection(double f)
{
	// cout << "MultiplexedBifurcationMap::indexCorrection" << endl;
	// cout << "dimensionF = " << dimensionF << endl;
	int index = -1;
	if (dimensionF>0)
		{
			for (int i=0;i<dimensionF;i++)
			{
				if (tableF[i] == f) index = i;
			};
		}
	return index;
}

void MultiplexedBifurcationMap::setRotation(double f, double offsetI, double offsetQ, double angle)
{
	// cout << "MultiplexedBifurcationMap::setRotation : " << endl;
	int index=indexCorrection(f);
	if (index >=0 )
		{
			tableIoffset[index] = offsetI;
			tableQoffset[index] = offsetQ;
			tableAngle[index] = angle;
		}
	else
		{
		dimensionF++;
		tableF.push_back(f);
		tableIoffset.push_back(offsetI);
		tableQoffset.push_back(offsetQ);
		tableAngle.push_back(angle);
		// cout << "adding new line" << endl;
		};
}

void MultiplexedBifurcationMap::rotateAndClicks(double f, double *trends, int numberOfSegments,double *clicks)
{
	double angle,Io,Qo,c,s;
	double I,Q;
	int nf, i, ns;
	int indexTrends;
	int index=indexCorrection(f);
	if (index>=0)
	{
		angle=tableAngle[index];
		Io=tableIoffset[index];
		Qo=tableQoffset[index];
		c=cos(angle);
		s=sin(angle);
	}
	else
	{
		angle=0;
		Io=0;
		Qo=0;
		c=1;
		s=0;
	}
	//loop over all segments
	for(ns=0; ns<numberOfSegments;ns++)
	{
		indexTrends=ns;
		I = (trends[indexTrends]-Io)*c+(trends[indexTrends+numberOfSegments]-Qo)*s;
		Q = -(trends[indexTrends]-Io)*s+(trends[indexTrends+numberOfSegments]-Qo)*c;
		trends[indexTrends]=I;
		trends[indexTrends+numberOfSegments]=Q;
		if (I>0)
			clicks[indexTrends]=1;
		else clicks[indexTrends]=0;
	}
}

void MultiplexedBifurcationMap::convertToProbabilities(int nbQB, int nbSegments, double *r, double *proba)
{
	int i;
	int qb;
	int value;
	for(i =0; i<nbSegments; i++)
	{
		value=0;
		for(qb=0; qb<nbQB; qb++)
		{
			value+=pow((double)2,(double)(nbQB-qb))*r[nbSegments*qb+i];
		}
		proba[value]+=1./nbSegments;
	}
}