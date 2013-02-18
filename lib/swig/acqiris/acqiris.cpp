// This is the main DLL file.

#include "stdafx.h"
#include <iostream>
using namespace std;
#include <cmath>
#include "acqiris.h"


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
	dimensionF=0;			 // set table size tp zeo (no frequencies known)
}

Demodulator::~Demodulator() //destructor
{

}

// returns the table index of a given frequency in the correction table if it exists or -1 otherwise
int Demodulator::indexCorrection(double f)
{
	cout << "Demodulator::indexCorrection" << endl;
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
	cout << "Demodulator::setCorrections : ";
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
		cout << "adding new line" << endl;
		};
	cout << "f,Io,Qo,Ig,Qg,Ir,Qr" << f << ' ' << offsetI << ' ' << offsetQ << ' ' << gainI << ' ' << gainQ << ' ' << angleI<< ' '  << angleQ << endl<<endl;

}

//Demodulation using one signal (amplitude only)
void Demodulator::demodulate1(double *ChA, double nbrSegments, double nbrSamplesPerSegment, double samplingTime, double frequency, double phase, double *arrayI, double *arrayQ, double *Imean, double *Qmean)
{
	
}

//Demodulation using two signals in quadrature
void Demodulator::demodulate2(double *ChA, double *ChB, double nbrSegments, double nbrSamplesPerSegment, double samplingTime, double frequency, double phase, double *arrayI, double *arrayQ, double *Imean, double *Qmean)
{
	cout << "Demodulator::demodulate: ";
	int n, p;
	double arg;
	cout << " *" ;
	cout << *Imean << endl;
	*Imean=0.;
	*Qmean=0.;
	int index=indexCorrection(frequency);
	double resI,resQ,det;
	cout << "index: " << index << endl;
	if (index>=0) det=cos((double)tableAngleI[index]-(double)tableAngleQ[index]);
	//Loop over all segment
	for(n=0;n<nbrSegments;n++)
	{	cout << "n" << n << endl;
		arrayI[n]=0;
		arrayQ[n]=0;
		//Loop over all points
		for(p=0;p<nbrSamplesPerSegment;p++)
		{	cout << "p" << p << endl;
			arg = 2*PI*frequency*p*samplingTime+phase;
			arrayI[n]+=ChA[p]*cos(arg);
			arrayQ[n]+=ChB[p]*sin(arg);
		}
		arrayI[n]/=nbrSamplesPerSegment;
		arrayQ[n]/=nbrSamplesPerSegment;

		if(index>=0)
		{	cout << "appplying correction" << endl;
			//I'=((cos Ri)I+sin(Ri)Q)/Gi
			//Q'=((cos Rq)Q-sin(Rq)I)/Gq
			//I=[((cos Rq)Gi I' -(sin Rq)Gq Q']/det
			//Q=[((sin Ri)Gi I' +cos(Ri)Gq Q']/det
			//det=cos(Ri-Rq)
			resI=(cos(tableAngleQ[index])*tableGainI[index]*arrayI[n]-sin(tableAngleQ[index])*tableGainQ[index]*arrayQ[n])/det;
			resQ=(sin(tableAngleI[index])*tableGainI[index]*arrayI[n]+cos(tableAngleI[index])*tableGainQ[index]*arrayQ[n])/det;
			arrayI[n]=resI;
			arrayQ[n]=resQ;
		}
		*Imean+=arrayI[n];
		*Qmean+=arrayQ[n];
		cout << "calculating averages" << endl;
	}
	*Imean/=nbrSegments;
	*Qmean/=nbrSegments;
	cout << "ok" << endl<<endl;
}

/*



multiplexed bifurcation map


 MultiplexedBifurcationMap::MultiplexedBifurcationMap()
{
	int dimensionF=1;
}

MultiplexedBifurcationMap::~MultiplexedBifurcationMap()
{
}

//This finishes the data treatment.
void MultiplexedBifurcationMap::finish()
{
	//Finish the data processing by normalizing the probabilities and averages.
	probabilities[0]/=(double)index;
	probabilities[1]/=(double)index;

	for(int i = 0;i++;i< 4)
		crossProbabilities[i]/=(double)index;

	for(int k = 0;k< 4;k++)
	{
		for(int i=0;i<nPoints;i++)
		{
			averages[i+k*nPoints]/=(double)index;
		}
	}
}

void MultiplexedBifurcationMap::add(double *f, double *trends, int numberOfFrequencies, int numberOfSegments,double *results)
{
	double Io,Qo,c,s;
	int nf, i, ns;
	int indexTrends;
	double point;
	// for each frequencie sent
	for(nf=0; nf<numberOfFrequencies; nf++)
	{
		// find the good parameters for this frequency
		int found = 0;
		for (i=0;i<dimensionF;i++)
		{
			if (fTable[i] == f[nf])
			{
				Io=Ioffset[i];
				Qo=Qoffset[i];
				c=CosTable[i];
				s=SinTable[i];
				found = 1;
				cout << "frequency found : " << "Io : " << Io << " Qo : " << Qo << " cos : " << c << " sin : " << s << endl;
			}
		}
		if (found == 1)
		{
			//loop over all segments
			for(ns=0; ns<numberOfSegments;ns++)
			{
				int ch=0;
				indexTrends=nf+numberOfFrequencies*(ns+numberOfSegments*ch);
				point = (trends[indexTrends]-Io)*c+(trends[indexTrends+numberOfFrequencies*numberOfSegments]-Qo)*s;
				if (point>0)
					results[indexTrends]=1;
				else results[indexTrends]=0;
			}

		}

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
			value+=pow(2,(nbQB-qb))*r[qb+i*nbQB];
		}
		proba[value]+=1./nSegments;
	}
}
*/