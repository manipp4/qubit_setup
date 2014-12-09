// demodulation.cpp : dfinit les fonctions exportes pour l'application DLL.
//
#include "stdafx.h"
#include <iostream>
#include <math.h>
#include <typeinfo> 
#define PI 3.14159265359	

double precalculatedFrequencies[8];
int precalculatedLastUsedTime[8];
const int precalculatedArraysSize = 262144;
double * precalculatedArrays[8];
double precalculatedArray0[precalculatedArraysSize];
double precalculatedArray1[precalculatedArraysSize];
double precalculatedArray2[precalculatedArraysSize];
double precalculatedArray3[precalculatedArraysSize];
double precalculatedArray4[precalculatedArraysSize];
double precalculatedArray5[precalculatedArraysSize];
double precalculatedArray6[precalculatedArraysSize];
double precalculatedArray7[precalculatedArraysSize];
double precalculatedArray8[precalculatedArraysSize];
double testArray[30000000];

void printAll()
{
	std::cout << &precalculatedArray0 << std::endl;
	std::cout << &precalculatedArray0 << std::endl;
}
int oldest(){
	//look for the oldest frequency unused
	int index = 0;
	int age = 0;
	for (int i = 0; i < 8; ++i){
		if (precalculatedLastUsedTime[i] > age)
		{
			age = precalculatedLastUsedTime[i];
			index = i;
		}
	}
	return index;
}

int generatePrecalculatedArray(double freq){
	precalculatedArrays[0] = precalculatedArray0;
	precalculatedArrays[1] = precalculatedArray1;
	precalculatedArrays[2] = precalculatedArray2;
	precalculatedArrays[3] = precalculatedArray3;
	precalculatedArrays[4] = precalculatedArray4;
	precalculatedArrays[5] = precalculatedArray5;
	precalculatedArrays[6] = precalculatedArray6;
	precalculatedArrays[7] = precalculatedArray7;
	// generate the array for given frequency
	int index = oldest();
	precalculatedFrequencies[index] = freq;
	for (int i = 0; i < precalculatedArraysSize; ++i)
	{ 
		precalculatedArrays[index][i] = cos(2 * PI*freq*double(i));
	}
	std::cout << "new one generated" << std::endl;
	return index;
}
int searchInPrecalculatedArrays(double freq){
//Look in precalculatedFrequencies to find index corresponding to give frequency
	for (int i = 0; i < 8; ++i){ if (abs(precalculatedFrequencies[i] - freq) < 0.00001) {return i; } }
	return generatePrecalculatedArray(freq);
}




void ageOtherArrays(int index){
	for (int i = 0; i < 8; ++i){ precalculatedLastUsedTime[i] += 1;}
	precalculatedLastUsedTime[index] = 0;
}



extern "C" __declspec( dllexport ) void WINAPI demodulate(bool twoCh,double *ChA, double *ChB, double *horPos, int nbrSegments,int nbrSamplesPerSegment,float samplingTime,float frequency,float phase,int intervalMode,bool tryCorrec, float *corrections, bool extraFast, bool averageOnly,bool APhi,int *nbrIntervalsPerSegment,double *array1,double *array2,double *arrayMean1,double *arrayMean2)
{	
	printAll();
	bool printDebug = true;
	if (printDebug) std::cout << "demodulating" << std::endl;
	float cosValues [1025] = {1.,0.999981,0.999925,0.999831,0.999699,0.999529,0.999322,0.999078,0.998795,0.998476,0.998118,0.997723,0.99729,0.99682,0.996313,0.995767,0.995185,0.994565,0.993907,0.993212,0.99248,0.99171,0.990903,0.990058,0.989177,0.988258,0.987301,0.986308,0.985278,0.98421,0.983105,0.981964,0.980785,0.97957,0.978317,0.977028,0.975702,0.974339,0.97294,0.971504,0.970031,0.968522,0.966976,0.965394,0.963776,0.962121,0.960431,0.958703,0.95694,0.955141,0.953306,0.951435,0.949528,0.947586,0.945607,0.943593,0.941544,0.939459,0.937339,0.935184,0.932993,0.930767,0.928506,0.92621,0.92388,0.921514,0.919114,0.916679,0.91421,0.911706,0.909168,0.906596,0.903989,0.901349,0.898674,0.895966,0.893224,0.890449,0.88764,0.884797,0.881921,0.879012,0.87607,0.873095,0.870087,0.867046,0.863973,0.860867,0.857729,0.854558,0.851355,0.84812,0.844854,0.841555,0.838225,0.834863,0.83147,0.828045,0.824589,0.821103,0.817585,0.814036,0.810457,0.806848,0.803208,0.799537,0.795837,0.792107,0.788346,0.784557,0.780737,0.776888,0.77301,0.769103,0.765167,0.761202,0.757209,0.753187,0.749136,0.745058,0.740951,0.736817,0.732654,0.728464,0.724247,0.720003,0.715731,0.711432,0.707107,0.702755,0.698376,0.693971,0.689541,0.685084,0.680601,0.676093,0.671559,0.667,0.662416,0.657807,0.653173,0.648514,0.643832,0.639124,0.634393,0.629638,0.624859,0.620057,0.615232,0.610383,0.605511,0.600616,0.595699,0.59076,0.585798,0.580814,0.575808,0.570781,0.565732,0.560662,0.55557,0.550458,0.545325,0.540171,0.534998,0.529804,0.52459,0.519356,0.514103,0.50883,0.503538,0.498228,0.492898,0.48755,0.482184,0.476799,0.471397,0.465976,0.460539,0.455084,0.449611,0.444122,0.438616,0.433094,0.427555,0.422,0.41643,0.410843,0.405241,0.399624,0.393992,0.388345,0.382683,0.377007,0.371317,0.365613,0.359895,0.354164,0.348419,0.342661,0.33689,0.331106,0.32531,0.319502,0.313682,0.30785,0.302006,0.296151,0.290285,0.284408,0.27852,0.272621,0.266713,0.260794,0.254866,0.248928,0.24298,0.237024,0.231058,0.225084,0.219101,0.21311,0.207111,0.201105,0.19509,0.189069,0.18304,0.177004,0.170962,0.164913,0.158858,0.152797,0.14673,0.140658,0.134581,0.128498,0.122411,0.116319,0.110222,0.104122,0.0980171,0.091909,0.0857973,0.0796824,0.0735646,0.0674439,0.0613207,0.0551952,0.0490677,0.0429383,0.0368072,0.0306748,0.0245412,0.0184067,0.0122715,0.00613588,0.,-0.00613588,-0.0122715,-0.0184067,-0.0245412,-0.0306748,-0.0368072,-0.0429383,-0.0490677,-0.0551952,-0.0613207,-0.0674439,-0.0735646,-0.0796824,-0.0857973,-0.091909,-0.0980171,-0.104122,-0.110222,-0.116319,-0.122411,-0.128498,-0.134581,-0.140658,-0.14673,-0.152797,-0.158858,-0.164913,-0.170962,-0.177004,-0.18304,-0.189069,-0.19509,-0.201105,-0.207111,-0.21311,-0.219101,-0.225084,-0.231058,-0.237024,-0.24298,-0.248928,-0.254866,-0.260794,-0.266713,-0.272621,-0.27852,-0.284408,-0.290285,-0.296151,-0.302006,-0.30785,-0.313682,-0.319502,-0.32531,-0.331106,-0.33689,-0.342661,-0.348419,-0.354164,-0.359895,-0.365613,-0.371317,-0.377007,-0.382683,-0.388345,-0.393992,-0.399624,-0.405241,-0.410843,-0.41643,-0.422,-0.427555,-0.433094,-0.438616,-0.444122,-0.449611,-0.455084,-0.460539,-0.465976,-0.471397,-0.476799,-0.482184,-0.48755,-0.492898,-0.498228,-0.503538,-0.50883,-0.514103,-0.519356,-0.52459,-0.529804,-0.534998,-0.540171,-0.545325,-0.550458,-0.55557,-0.560662,-0.565732,-0.570781,-0.575808,-0.580814,-0.585798,-0.59076,-0.595699,-0.600616,-0.605511,-0.610383,-0.615232,-0.620057,-0.624859,-0.629638,-0.634393,-0.639124,-0.643832,-0.648514,-0.653173,-0.657807,-0.662416,-0.667,-0.671559,-0.676093,-0.680601,-0.685084,-0.689541,-0.693971,-0.698376,-0.702755,-0.707107,-0.711432,-0.715731,-0.720003,-0.724247,-0.728464,-0.732654,-0.736817,-0.740951,-0.745058,-0.749136,-0.753187,-0.757209,-0.761202,-0.765167,-0.769103,-0.77301,-0.776888,-0.780737,-0.784557,-0.788346,-0.792107,-0.795837,-0.799537,-0.803208,-0.806848,-0.810457,-0.814036,-0.817585,-0.821103,-0.824589,-0.828045,-0.83147,-0.834863,-0.838225,-0.841555,-0.844854,-0.84812,-0.851355,-0.854558,-0.857729,-0.860867,-0.863973,-0.867046,-0.870087,-0.873095,-0.87607,-0.879012,-0.881921,-0.884797,-0.88764,-0.890449,-0.893224,-0.895966,-0.898674,-0.901349,-0.903989,-0.906596,-0.909168,-0.911706,-0.91421,-0.916679,-0.919114,-0.921514,-0.92388,-0.92621,-0.928506,-0.930767,-0.932993,-0.935184,-0.937339,-0.939459,-0.941544,-0.943593,-0.945607,-0.947586,-0.949528,-0.951435,-0.953306,-0.955141,-0.95694,-0.958703,-0.960431,-0.962121,-0.963776,-0.965394,-0.966976,-0.968522,-0.970031,-0.971504,-0.97294,-0.974339,-0.975702,-0.977028,-0.978317,-0.97957,-0.980785,-0.981964,-0.983105,-0.98421,-0.985278,-0.986308,-0.987301,-0.988258,-0.989177,-0.990058,-0.990903,-0.99171,-0.99248,-0.993212,-0.993907,-0.994565,-0.995185,-0.995767,-0.996313,-0.99682,-0.99729,-0.997723,-0.998118,-0.998476,-0.998795,-0.999078,-0.999322,-0.999529,-0.999699,-0.999831,-0.999925,-0.999981,-1.,-0.999981,-0.999925,-0.999831,-0.999699,-0.999529,-0.999322,-0.999078,-0.998795,-0.998476,-0.998118,-0.997723,-0.99729,-0.99682,-0.996313,-0.995767,-0.995185,-0.994565,-0.993907,-0.993212,-0.99248,-0.99171,-0.990903,-0.990058,-0.989177,-0.988258,-0.987301,-0.986308,-0.985278,-0.98421,-0.983105,-0.981964,-0.980785,-0.97957,-0.978317,-0.977028,-0.975702,-0.974339,-0.97294,-0.971504,-0.970031,-0.968522,-0.966976,-0.965394,-0.963776,-0.962121,-0.960431,-0.958703,-0.95694,-0.955141,-0.953306,-0.951435,-0.949528,-0.947586,-0.945607,-0.943593,-0.941544,-0.939459,-0.937339,-0.935184,-0.932993,-0.930767,-0.928506,-0.92621,-0.92388,-0.921514,-0.919114,-0.916679,-0.91421,-0.911706,-0.909168,-0.906596,-0.903989,-0.901349,-0.898674,-0.895966,-0.893224,-0.890449,-0.88764,-0.884797,-0.881921,-0.879012,-0.87607,-0.873095,-0.870087,-0.867046,-0.863973,-0.860867,-0.857729,-0.854558,-0.851355,-0.84812,-0.844854,-0.841555,-0.838225,-0.834863,-0.83147,-0.828045,-0.824589,-0.821103,-0.817585,-0.814036,-0.810457,-0.806848,-0.803208,-0.799537,-0.795837,-0.792107,-0.788346,-0.784557,-0.780737,-0.776888,-0.77301,-0.769103,-0.765167,-0.761202,-0.757209,-0.753187,-0.749136,-0.745058,-0.740951,-0.736817,-0.732654,-0.728464,-0.724247,-0.720003,-0.715731,-0.711432,-0.707107,-0.702755,-0.698376,-0.693971,-0.689541,-0.685084,-0.680601,-0.676093,-0.671559,-0.667,-0.662416,-0.657807,-0.653173,-0.648514,-0.643832,-0.639124,-0.634393,-0.629638,-0.624859,-0.620057,-0.615232,-0.610383,-0.605511,-0.600616,-0.595699,-0.59076,-0.585798,-0.580814,-0.575808,-0.570781,-0.565732,-0.560662,-0.55557,-0.550458,-0.545325,-0.540171,-0.534998,-0.529804,-0.52459,-0.519356,-0.514103,-0.50883,-0.503538,-0.498228,-0.492898,-0.48755,-0.482184,-0.476799,-0.471397,-0.465976,-0.460539,-0.455084,-0.449611,-0.444122,-0.438616,-0.433094,-0.427555,-0.422,-0.41643,-0.410843,-0.405241,-0.399624,-0.393992,-0.388345,-0.382683,-0.377007,-0.371317,-0.365613,-0.359895,-0.354164,-0.348419,-0.342661,-0.33689,-0.331106,-0.32531,-0.319502,-0.313682,-0.30785,-0.302006,-0.296151,-0.290285,-0.284408,-0.27852,-0.272621,-0.266713,-0.260794,-0.254866,-0.248928,-0.24298,-0.237024,-0.231058,-0.225084,-0.219101,-0.21311,-0.207111,-0.201105,-0.19509,-0.189069,-0.18304,-0.177004,-0.170962,-0.164913,-0.158858,-0.152797,-0.14673,-0.140658,-0.134581,-0.128498,-0.122411,-0.116319,-0.110222,-0.104122,-0.0980171,-0.091909,-0.0857973,-0.0796824,-0.0735646,-0.0674439,-0.0613207,-0.0551952,-0.0490677,-0.0429383,-0.0368072,-0.0306748,-0.0245412,-0.0184067,-0.0122715,-0.00613588,0.,0.00613588,0.0122715,0.0184067,0.0245412,0.0306748,0.0368072,0.0429383,0.0490677,0.0551952,0.0613207,0.0674439,0.0735646,0.0796824,0.0857973,0.091909,0.0980171,0.104122,0.110222,0.116319,0.122411,0.128498,0.134581,0.140658,0.14673,0.152797,0.158858,0.164913,0.170962,0.177004,0.18304,0.189069,0.19509,0.201105,0.207111,0.21311,0.219101,0.225084,0.231058,0.237024,0.24298,0.248928,0.254866,0.260794,0.266713,0.272621,0.27852,0.284408,0.290285,0.296151,0.302006,0.30785,0.313682,0.319502,0.32531,0.331106,0.33689,0.342661,0.348419,0.354164,0.359895,0.365613,0.371317,0.377007,0.382683,0.388345,0.393992,0.399624,0.405241,0.410843,0.41643,0.422,0.427555,0.433094,0.438616,0.444122,0.449611,0.455084,0.460539,0.465976,0.471397,0.476799,0.482184,0.48755,0.492898,0.498228,0.503538,0.50883,0.514103,0.519356,0.52459,0.529804,0.534998,0.540171,0.545325,0.550458,0.55557,0.560662,0.565732,0.570781,0.575808,0.580814,0.585798,0.59076,0.595699,0.600616,0.605511,0.610383,0.615232,0.620057,0.624859,0.629638,0.634393,0.639124,0.643832,0.648514,0.653173,0.657807,0.662416,0.667,0.671559,0.676093,0.680601,0.685084,0.689541,0.693971,0.698376,0.702755,0.707107,0.711432,0.715731,0.720003,0.724247,0.728464,0.732654,0.736817,0.740951,0.745058,0.749136,0.753187,0.757209,0.761202,0.765167,0.769103,0.77301,0.776888,0.780737,0.784557,0.788346,0.792107,0.795837,0.799537,0.803208,0.806848,0.810457,0.814036,0.817585,0.821103,0.824589,0.828045,0.83147,0.834863,0.838225,0.841555,0.844854,0.84812,0.851355,0.854558,0.857729,0.860867,0.863973,0.867046,0.870087,0.873095,0.87607,0.879012,0.881921,0.884797,0.88764,0.890449,0.893224,0.895966,0.898674,0.901349,0.903989,0.906596,0.909168,0.911706,0.91421,0.916679,0.919114,0.921514,0.92388,0.92621,0.928506,0.930767,0.932993,0.935184,0.937339,0.939459,0.941544,0.943593,0.945607,0.947586,0.949528,0.951435,0.953306,0.955141,0.95694,0.958703,0.960431,0.962121,0.963776,0.965394,0.966976,0.968522,0.970031,0.971504,0.97294,0.974339,0.975702,0.977028,0.978317,0.97957,0.980785,0.981964,0.983105,0.98421,0.985278,0.986308,0.987301,0.988258,0.989177,0.990058,0.990903,0.99171,0.99248,0.993212,0.993907,0.994565,0.995185,0.995767,0.996313,0.99682,0.99729,0.997723,0.998118,0.998476,0.998795,0.999078,0.999322,0.999529,0.999699,0.999831,0.999925,0.999981,1.};
	float sinValues [1025] = {0.,0.00613588,0.0122715,0.0184067,0.0245412,0.0306748,0.0368072,0.0429383,0.0490677,0.0551952,0.0613207,0.0674439,0.0735646,0.0796824,0.0857973,0.091909,0.0980171,0.104122,0.110222,0.116319,0.122411,0.128498,0.134581,0.140658,0.14673,0.152797,0.158858,0.164913,0.170962,0.177004,0.18304,0.189069,0.19509,0.201105,0.207111,0.21311,0.219101,0.225084,0.231058,0.237024,0.24298,0.248928,0.254866,0.260794,0.266713,0.272621,0.27852,0.284408,0.290285,0.296151,0.302006,0.30785,0.313682,0.319502,0.32531,0.331106,0.33689,0.342661,0.348419,0.354164,0.359895,0.365613,0.371317,0.377007,0.382683,0.388345,0.393992,0.399624,0.405241,0.410843,0.41643,0.422,0.427555,0.433094,0.438616,0.444122,0.449611,0.455084,0.460539,0.465976,0.471397,0.476799,0.482184,0.48755,0.492898,0.498228,0.503538,0.50883,0.514103,0.519356,0.52459,0.529804,0.534998,0.540171,0.545325,0.550458,0.55557,0.560662,0.565732,0.570781,0.575808,0.580814,0.585798,0.59076,0.595699,0.600616,0.605511,0.610383,0.615232,0.620057,0.624859,0.629638,0.634393,0.639124,0.643832,0.648514,0.653173,0.657807,0.662416,0.667,0.671559,0.676093,0.680601,0.685084,0.689541,0.693971,0.698376,0.702755,0.707107,0.711432,0.715731,0.720003,0.724247,0.728464,0.732654,0.736817,0.740951,0.745058,0.749136,0.753187,0.757209,0.761202,0.765167,0.769103,0.77301,0.776888,0.780737,0.784557,0.788346,0.792107,0.795837,0.799537,0.803208,0.806848,0.810457,0.814036,0.817585,0.821103,0.824589,0.828045,0.83147,0.834863,0.838225,0.841555,0.844854,0.84812,0.851355,0.854558,0.857729,0.860867,0.863973,0.867046,0.870087,0.873095,0.87607,0.879012,0.881921,0.884797,0.88764,0.890449,0.893224,0.895966,0.898674,0.901349,0.903989,0.906596,0.909168,0.911706,0.91421,0.916679,0.919114,0.921514,0.92388,0.92621,0.928506,0.930767,0.932993,0.935184,0.937339,0.939459,0.941544,0.943593,0.945607,0.947586,0.949528,0.951435,0.953306,0.955141,0.95694,0.958703,0.960431,0.962121,0.963776,0.965394,0.966976,0.968522,0.970031,0.971504,0.97294,0.974339,0.975702,0.977028,0.978317,0.97957,0.980785,0.981964,0.983105,0.98421,0.985278,0.986308,0.987301,0.988258,0.989177,0.990058,0.990903,0.99171,0.99248,0.993212,0.993907,0.994565,0.995185,0.995767,0.996313,0.99682,0.99729,0.997723,0.998118,0.998476,0.998795,0.999078,0.999322,0.999529,0.999699,0.999831,0.999925,0.999981,1.,0.999981,0.999925,0.999831,0.999699,0.999529,0.999322,0.999078,0.998795,0.998476,0.998118,0.997723,0.99729,0.99682,0.996313,0.995767,0.995185,0.994565,0.993907,0.993212,0.99248,0.99171,0.990903,0.990058,0.989177,0.988258,0.987301,0.986308,0.985278,0.98421,0.983105,0.981964,0.980785,0.97957,0.978317,0.977028,0.975702,0.974339,0.97294,0.971504,0.970031,0.968522,0.966976,0.965394,0.963776,0.962121,0.960431,0.958703,0.95694,0.955141,0.953306,0.951435,0.949528,0.947586,0.945607,0.943593,0.941544,0.939459,0.937339,0.935184,0.932993,0.930767,0.928506,0.92621,0.92388,0.921514,0.919114,0.916679,0.91421,0.911706,0.909168,0.906596,0.903989,0.901349,0.898674,0.895966,0.893224,0.890449,0.88764,0.884797,0.881921,0.879012,0.87607,0.873095,0.870087,0.867046,0.863973,0.860867,0.857729,0.854558,0.851355,0.84812,0.844854,0.841555,0.838225,0.834863,0.83147,0.828045,0.824589,0.821103,0.817585,0.814036,0.810457,0.806848,0.803208,0.799537,0.795837,0.792107,0.788346,0.784557,0.780737,0.776888,0.77301,0.769103,0.765167,0.761202,0.757209,0.753187,0.749136,0.745058,0.740951,0.736817,0.732654,0.728464,0.724247,0.720003,0.715731,0.711432,0.707107,0.702755,0.698376,0.693971,0.689541,0.685084,0.680601,0.676093,0.671559,0.667,0.662416,0.657807,0.653173,0.648514,0.643832,0.639124,0.634393,0.629638,0.624859,0.620057,0.615232,0.610383,0.605511,0.600616,0.595699,0.59076,0.585798,0.580814,0.575808,0.570781,0.565732,0.560662,0.55557,0.550458,0.545325,0.540171,0.534998,0.529804,0.52459,0.519356,0.514103,0.50883,0.503538,0.498228,0.492898,0.48755,0.482184,0.476799,0.471397,0.465976,0.460539,0.455084,0.449611,0.444122,0.438616,0.433094,0.427555,0.422,0.41643,0.410843,0.405241,0.399624,0.393992,0.388345,0.382683,0.377007,0.371317,0.365613,0.359895,0.354164,0.348419,0.342661,0.33689,0.331106,0.32531,0.319502,0.313682,0.30785,0.302006,0.296151,0.290285,0.284408,0.27852,0.272621,0.266713,0.260794,0.254866,0.248928,0.24298,0.237024,0.231058,0.225084,0.219101,0.21311,0.207111,0.201105,0.19509,0.189069,0.18304,0.177004,0.170962,0.164913,0.158858,0.152797,0.14673,0.140658,0.134581,0.128498,0.122411,0.116319,0.110222,0.104122,0.0980171,0.091909,0.0857973,0.0796824,0.0735646,0.0674439,0.0613207,0.0551952,0.0490677,0.0429383,0.0368072,0.0306748,0.0245412,0.0184067,0.0122715,0.00613588,0.,-0.00613588,-0.0122715,-0.0184067,-0.0245412,-0.0306748,-0.0368072,-0.0429383,-0.0490677,-0.0551952,-0.0613207,-0.0674439,-0.0735646,-0.0796824,-0.0857973,-0.091909,-0.0980171,-0.104122,-0.110222,-0.116319,-0.122411,-0.128498,-0.134581,-0.140658,-0.14673,-0.152797,-0.158858,-0.164913,-0.170962,-0.177004,-0.18304,-0.189069,-0.19509,-0.201105,-0.207111,-0.21311,-0.219101,-0.225084,-0.231058,-0.237024,-0.24298,-0.248928,-0.254866,-0.260794,-0.266713,-0.272621,-0.27852,-0.284408,-0.290285,-0.296151,-0.302006,-0.30785,-0.313682,-0.319502,-0.32531,-0.331106,-0.33689,-0.342661,-0.348419,-0.354164,-0.359895,-0.365613,-0.371317,-0.377007,-0.382683,-0.388345,-0.393992,-0.399624,-0.405241,-0.410843,-0.41643,-0.422,-0.427555,-0.433094,-0.438616,-0.444122,-0.449611,-0.455084,-0.460539,-0.465976,-0.471397,-0.476799,-0.482184,-0.48755,-0.492898,-0.498228,-0.503538,-0.50883,-0.514103,-0.519356,-0.52459,-0.529804,-0.534998,-0.540171,-0.545325,-0.550458,-0.55557,-0.560662,-0.565732,-0.570781,-0.575808,-0.580814,-0.585798,-0.59076,-0.595699,-0.600616,-0.605511,-0.610383,-0.615232,-0.620057,-0.624859,-0.629638,-0.634393,-0.639124,-0.643832,-0.648514,-0.653173,-0.657807,-0.662416,-0.667,-0.671559,-0.676093,-0.680601,-0.685084,-0.689541,-0.693971,-0.698376,-0.702755,-0.707107,-0.711432,-0.715731,-0.720003,-0.724247,-0.728464,-0.732654,-0.736817,-0.740951,-0.745058,-0.749136,-0.753187,-0.757209,-0.761202,-0.765167,-0.769103,-0.77301,-0.776888,-0.780737,-0.784557,-0.788346,-0.792107,-0.795837,-0.799537,-0.803208,-0.806848,-0.810457,-0.814036,-0.817585,-0.821103,-0.824589,-0.828045,-0.83147,-0.834863,-0.838225,-0.841555,-0.844854,-0.84812,-0.851355,-0.854558,-0.857729,-0.860867,-0.863973,-0.867046,-0.870087,-0.873095,-0.87607,-0.879012,-0.881921,-0.884797,-0.88764,-0.890449,-0.893224,-0.895966,-0.898674,-0.901349,-0.903989,-0.906596,-0.909168,-0.911706,-0.91421,-0.916679,-0.919114,-0.921514,-0.92388,-0.92621,-0.928506,-0.930767,-0.932993,-0.935184,-0.937339,-0.939459,-0.941544,-0.943593,-0.945607,-0.947586,-0.949528,-0.951435,-0.953306,-0.955141,-0.95694,-0.958703,-0.960431,-0.962121,-0.963776,-0.965394,-0.966976,-0.968522,-0.970031,-0.971504,-0.97294,-0.974339,-0.975702,-0.977028,-0.978317,-0.97957,-0.980785,-0.981964,-0.983105,-0.98421,-0.985278,-0.986308,-0.987301,-0.988258,-0.989177,-0.990058,-0.990903,-0.99171,-0.99248,-0.993212,-0.993907,-0.994565,-0.995185,-0.995767,-0.996313,-0.99682,-0.99729,-0.997723,-0.998118,-0.998476,-0.998795,-0.999078,-0.999322,-0.999529,-0.999699,-0.999831,-0.999925,-0.999981,-1.,-0.999981,-0.999925,-0.999831,-0.999699,-0.999529,-0.999322,-0.999078,-0.998795,-0.998476,-0.998118,-0.997723,-0.99729,-0.99682,-0.996313,-0.995767,-0.995185,-0.994565,-0.993907,-0.993212,-0.99248,-0.99171,-0.990903,-0.990058,-0.989177,-0.988258,-0.987301,-0.986308,-0.985278,-0.98421,-0.983105,-0.981964,-0.980785,-0.97957,-0.978317,-0.977028,-0.975702,-0.974339,-0.97294,-0.971504,-0.970031,-0.968522,-0.966976,-0.965394,-0.963776,-0.962121,-0.960431,-0.958703,-0.95694,-0.955141,-0.953306,-0.951435,-0.949528,-0.947586,-0.945607,-0.943593,-0.941544,-0.939459,-0.937339,-0.935184,-0.932993,-0.930767,-0.928506,-0.92621,-0.92388,-0.921514,-0.919114,-0.916679,-0.91421,-0.911706,-0.909168,-0.906596,-0.903989,-0.901349,-0.898674,-0.895966,-0.893224,-0.890449,-0.88764,-0.884797,-0.881921,-0.879012,-0.87607,-0.873095,-0.870087,-0.867046,-0.863973,-0.860867,-0.857729,-0.854558,-0.851355,-0.84812,-0.844854,-0.841555,-0.838225,-0.834863,-0.83147,-0.828045,-0.824589,-0.821103,-0.817585,-0.814036,-0.810457,-0.806848,-0.803208,-0.799537,-0.795837,-0.792107,-0.788346,-0.784557,-0.780737,-0.776888,-0.77301,-0.769103,-0.765167,-0.761202,-0.757209,-0.753187,-0.749136,-0.745058,-0.740951,-0.736817,-0.732654,-0.728464,-0.724247,-0.720003,-0.715731,-0.711432,-0.707107,-0.702755,-0.698376,-0.693971,-0.689541,-0.685084,-0.680601,-0.676093,-0.671559,-0.667,-0.662416,-0.657807,-0.653173,-0.648514,-0.643832,-0.639124,-0.634393,-0.629638,-0.624859,-0.620057,-0.615232,-0.610383,-0.605511,-0.600616,-0.595699,-0.59076,-0.585798,-0.580814,-0.575808,-0.570781,-0.565732,-0.560662,-0.55557,-0.550458,-0.545325,-0.540171,-0.534998,-0.529804,-0.52459,-0.519356,-0.514103,-0.50883,-0.503538,-0.498228,-0.492898,-0.48755,-0.482184,-0.476799,-0.471397,-0.465976,-0.460539,-0.455084,-0.449611,-0.444122,-0.438616,-0.433094,-0.427555,-0.422,-0.41643,-0.410843,-0.405241,-0.399624,-0.393992,-0.388345,-0.382683,-0.377007,-0.371317,-0.365613,-0.359895,-0.354164,-0.348419,-0.342661,-0.33689,-0.331106,-0.32531,-0.319502,-0.313682,-0.30785,-0.302006,-0.296151,-0.290285,-0.284408,-0.27852,-0.272621,-0.266713,-0.260794,-0.254866,-0.248928,-0.24298,-0.237024,-0.231058,-0.225084,-0.219101,-0.21311,-0.207111,-0.201105,-0.19509,-0.189069,-0.18304,-0.177004,-0.170962,-0.164913,-0.158858,-0.152797,-0.14673,-0.140658,-0.134581,-0.128498,-0.122411,-0.116319,-0.110222,-0.104122,-0.0980171,-0.091909,-0.0857973,-0.0796824,-0.0735646,-0.0674439,-0.0613207,-0.0551952,-0.0490677,-0.0429383,-0.0368072,-0.0306748,-0.0245412,-0.0184067,-0.0122715,-0.00613588,0.};
	// corrections : angleI, angleQ, offset I, offsetQ, gainI, gainQ
	//	// cout << "PI = " << PI << endl;
	int i,j,p,q,r,nbrSamplesPerInterval,index=-1;
	double arg,deltaArg,I,Q,x,y,det;
	double angleI	=0;
	double angleQ	=0;
	double offsetI	=0;
	double offsetQ	=0;
	double gainI	=0;
	double gainQ	=0;	
	double reducedFrequency; //used in extraFastLoop
	int arrayIndex;
	double * thisPrecalculatedArray[8];
	float c, s; // temporaties values for sine and cos
	int tempIndex;


	//std::cout<< "frequency "<< frequency << std::endl;
	//std::cout<< "samplingTime "<< samplingTime << std::endl;
	//std::cout<< "horPos[0] "<< horPos[0]  << std::endl;
	std::cout << "freq " << 1000* (samplingTime*frequency) << std::endl;
	det=1;	
	if (tryCorrec)									// Try to access corrections for the given frequency possibly stored in the demodulator class
	{	
		angleI	=corrections[0];
		angleQ	=corrections[1];
		offsetI	=corrections[2];
		offsetQ	=corrections[3];
		gainI	=corrections[4];
		gainQ	=corrections[5];
		if (index>=0) det=cos((double)angleI-(double)angleQ); //precomputes det (to be used for correcting I and Q)
	}
	double nbrSamplesPerHalfPeriod=1/(2*samplingTime*frequency); // precomputes number of samples per half-period
	// Define the numbers of demodulation intervals per segments and of samples per demodulation interval
	if(intervalMode>0)								//p demodulations over given integer number of half-period if possible, otherwise case below
	{	nbrSamplesPerInterval=nbrSamplesPerHalfPeriod*abs(intervalMode);
		*nbrIntervalsPerSegment=floor(float(nbrSamplesPerSegment/nbrSamplesPerInterval));
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
	deltaArg=abs(2*PI*frequency*samplingTime);
	//std::cout<< "deltaArg " << deltaArg << std::endl;
	//std::cout << "frequency = " << frequency << " samplingTime = " << samplingTime << endl; 
	i=0;											//i index of arrayI and arrayQ (0 to nbrSegments*nbrIntervalsPerSegment-1)
	for(q=0;q<*nbrIntervalsPerSegment;q++)			//q index of demodulation interval (0 to nbrIntervalsPerSegment-1)
	{	arrayMean1[q]=0;							//initialize Imean and Qmean to zero for all intervals
		arrayMean2[q]=0;
	};
	reducedFrequency = frequency*samplingTime;
	arrayIndex = searchInPrecalculatedArrays(reducedFrequency);
	ageOtherArrays(arrayIndex);
	double Id = 0.;										//initialize quadratures capital I and capital Q to zero
	double Qd = 0.;
	double* thisArray = precalculatedArrays[arrayIndex];
	std::cout << "extra fast: " << extraFast << std::endl;
	for(p=0;p<nbrSegments;p++)						//Loop over all segments. p index of segment (0 to nbrSegments-1)
	{//	// cout << "segment = "<< p << endl;
		j=p*nbrSamplesPerSegment;					// j sample index in ChA and ChB (0 to nbrSegments*nbrSamplesPerSegment-1)
		arg = phase+2*PI*frequency*horPos[p];								// initialise argument to phase+offsettime
		for(q=0;q<*nbrIntervalsPerSegment;q++)		//Loop over all demodulation intervals of a segment
		{//	// cout << "interval = "<< q << endl;
			Id = 0.;										//initialize quadratures capital I and capital Q to zero
			Qd = 0.;
			//std::cout << "I init:" << Id << std::endl;
			if (extraFast)
				{
					//std::cout << "in extraFast" << std::endl;
					for (r = 0; r<nbrSamplesPerInterval; r++)	//Loop over all samples of a demodulation interval
					{
						//std::cout << "ChA << precalculatedArrays[arrayIndex][r]:" << ChA[j] << " " << precalculatedArrays[arrayIndex][r] << std::endl;
						//std::cout << "I: " << Id << std::endl;
						Id += ChA[j] * thisArray[r];
						Qd += ChB[j] * thisArray[r];
						//std::cout << "I: " << Id << std::endl;
						j++;
					}
					Id = 2 * Id / double(nbrSamplesPerInterval);			//finish I and Q calculation;
					Qd = 2 * Qd / double(nbrSamplesPerInterval);
					//std::cout << "Id:" << Id << " Qd:" << Qd << std::endl;
					arg = phase - 2 * PI*frequency*horPos[p];
					double c = cos(arg);
					double s = sin(arg);
					x = c*Id - s*Qd;
					y = c*Qd + s*Id;
					Id = x;
					Qd = y;

				}
				else
				{
					//std::cout << "slow demod : p,q=" << p << ' ' << q << std::endl;
					for (r = 0; r<nbrSamplesPerInterval; r++)	//Loop over all samples of a demodulation interval
					{
						if (printDebug) 	std::cout << "p " << p << " q " << q << " r " << r << std::endl;
						c = float(cos(abs(arg)));
						s = float(sin(abs(arg)));
						Id += ChA[j] * c;					//accumulate chA*Cos in I
						if (twoCh)	Qd += ChB[j] * c; else Qd += ChB[j] * s; //accumulate chB*Cos or chB*Sin in Q depending on 1 or two channels
						arg += deltaArg;					//increment argument
						if (arg > 2 * PI) arg -= 2 * PI;
						j++;
					}
					Id = 2 * Id / nbrSamplesPerInterval;			//finish I and Q calculation;
					Qd = 2 * Qd / nbrSamplesPerInterval;
				}

			if(index>=0)							//apply available and requested corrections
			{
				std::cout << "apply corrections" << std::endl;
				// cout << "appplying corrections" << endl;
				if(twoCh)							// corrections when working on 2 channels I and Q
				{									//I'=((cos Ri)I+sin(Ri)Q)/Gi
													//Q'=((cos Rq)Q-sin(Rq)I)/Gq
													//I=[((cos Rq)Gi I' -(sin Rq)Gq Q']/det
													//Q=[((sin Ri)Gi I' +cos(Ri)Gq Q']/det
													//det=cos(Ri-Rq)
					x=(cos(angleI)*gainI*Id-sin(angleQ)*gainQ*Qd)/det;
					y=(sin(angleI)*gainI*Id+cos(angleQ)*gainQ*Qd)/det;
				}
				else								// corrections when working on 1 channels I
				{	x=(cos(angleI)*Id-sin(angleQ)*Qd)*gainI;
					y=(sin(angleQ)*Id+cos(angleI)*Qd)*gainI;
				};
				Id=x;
				Qd=y;
			};
			if(APhi) 
			{	x=sqrt(Id*Id+Qd*Qd);
				y=atan2(Qd,Id);
			}
			else
			{	x=Id;y=Qd;
			};
			if (printDebug) std::cout << "storing in dest array" << std::endl;
			if (! averageOnly)						//store I and Q in arrayI and arrayQ in case user asked for all segments
			{	
				//std::cout << "i:" << i << std::endl;
				//std::cout << "x:" << x << " y:" << y << std::endl;
				array1[i]=double(x);
				array2[i]=double(y);
				//std::cout << "array1[i]:" << array1[i] << " array2[i]:" << array2[i] << std::endl;
				i++;								//increment arrayI and arrayQ index
				//std::cout << "i:" << i << std::endl;
			};
			arrayMean1[q]+=x;arrayMean2[q]+=y;		//accumulate for I and Q averaging
			if (printDebug) std::cout << "stored" << std::endl;
		};
	};
//	if (printDebug) std::cout << "averaging" << std::endl;
//	for(q=0;q<*nbrIntervalsPerSegment;q++)			//complete I and Q averaging over all segments
//	{	arrayMean1[q]/=nbrSegments;
//		arrayMean2[q]/=nbrSegments;
//	};
//	if (printDebug) std::cout << "averaging done" << std::endl;
//	if (printDebug) std::cout << "deleting" << std::endl;
//	//delete[] & cosValues;
//	//delete[] & sinValues;
//	if (printDebug) std::cout << "deleting done" << std::endl;
	//std::cout << array1 << ' ' << &(array1[9]) << std::endl;
	//std::cout << "typeid " << typeid(array1).name() << std::endl;
	//cout << "array1[0]:" << array1[0] << " array2[0]:" << array2[0] << std::endl;
};

extern "C" __declspec( dllexport ) int WINAPI version()
{
	return 1;
}

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
//	* P_Time_us: pointer to the evaluation duration of the function in µs
//
extern "C" __declspec( dllexport ) void WINAPI demodulate1ChIQ(double *ChA, double *horPos,int nbrSegments,int nbrSamplesPerSegment,float samplingTime, float frequency, float phase,int intervalMode,bool tryCorrec, float *corrections, bool extraFast, bool averageOnly,int *nbrIntervalsPerSegment,double *arrayI,double *arrayQ,double *arrayMeanI,double *arrayMeanQ,double *P_Time_us)
{
	// cout << "Demodulator::demodulate1ChIQ: "<<endl;
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut); //start the timer
	demodulate(false,ChA,ChA,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec, corrections, extraFast,averageOnly,false,nbrIntervalsPerSegment,arrayI,arrayQ,arrayMeanI,arrayMeanQ);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in µs
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
//	* P_Time_us: pointer to the evaluation duration of the function in µs
//
extern "C" __declspec( dllexport ) void WINAPI demodulate2ChIQ(double *ChA,double *ChB, double *horPos, int nbrSegments, int nbrSamplesPerSegment,float samplingTime,float frequency,float phase,int intervalMode,bool tryCorrec, float *corrections, bool extraFast, bool averageOnly,int *nbrIntervalsPerSegment,double *arrayI,double *arrayQ,double *arrayMeanI,double *arrayMeanQ, double *P_Time_us)
{ 	
	std::cout<<" in demodulate " << std::endl;
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut); //start the timer
	std::cout<<"start demodulate" << std::endl;
	demodulate(true,ChA,ChB,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec, corrections, extraFast,averageOnly,false,nbrIntervalsPerSegment,arrayI,arrayQ,arrayMeanI,arrayMeanQ);
	std::cout<<"demodulation over" << std::endl;
//	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
//	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in µs
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
//	* P_Time_us: pointer to the evaluation duration of the function in µs
//
extern "C" __declspec( dllexport ) void WINAPI demodulate1ChAPhi(double *ChA, double *horPos,int nbrSegments,int nbrSamplesPerSegment,float samplingTime, float frequency, float phase,int intervalMode,bool tryCorrec, float *corrections, bool extraFast, bool averageOnly,int *nbrIntervalsPerSegment,double *arrayA,double *arrayPhi,double *arrayMeanA,double *arrayMeanPhi, double *P_Time_us)
{ 	// cout << "Demodulator::demodulate1ChAPhi: ";
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut);			//start the timer
	demodulate(false,ChA,ChA,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec, corrections, extraFast,averageOnly,true,nbrIntervalsPerSegment,arrayA,arrayPhi,arrayMeanA,arrayMeanPhi);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in µs
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
//	* P_Time_us: pointer to the evaluation duration of the function in µs
//
extern "C" __declspec( dllexport ) void WINAPI demodulate2ChAPhi(double *ChA, double *horPos,double *ChB, int nbrSegments, int nbrSamplesPerSegment,float samplingTime,float frequency,float phase,int intervalMode,bool tryCorrec, float *corrections, bool extraFast, bool averageOnly,int *nbrIntervalsPerSegment,double *arrayA,double *arrayPhi,double *arrayMeanA,double *arrayMeanPhi, double *P_Time_us)
{	// cout << "Demodulator::demodulate2ChAPhi: ";
	LARGE_INTEGER L_Frequency,L_TmpDebut,L_TmpFin;
	QueryPerformanceFrequency(&L_Frequency);
	QueryPerformanceCounter(&L_TmpDebut);			//start the timer
	demodulate(true,ChA,ChB,horPos,nbrSegments,nbrSamplesPerSegment,samplingTime,frequency,phase,intervalMode,tryCorrec, corrections, extraFast,averageOnly,true,nbrIntervalsPerSegment,arrayA,arrayPhi,arrayMeanA,arrayMeanPhi);
	QueryPerformanceCounter(&L_TmpFin);				//stop the timer...
	*P_Time_us = 1000000.0 *(L_TmpFin.QuadPart - L_TmpDebut.QuadPart) / L_Frequency.QuadPart;//...and calculate elapsed time in µs
	// cout<<"OK - duration = " <<*P_Time_us<< " microsec." <<endl;
};



extern "C" __declspec(dllexport) void WINAPI gen()
{
	for (int i = 0; i < 1000000; ++i)
	{
		testArray[i] = sin(double(i));
	}
}
extern "C" __declspec(dllexport) double WINAPI testSpeed1()
{
	int k = 0;
	double h = 0;
	for (int j = 0; j < 10000; ++j)
	{
		//		std::cout << "j:" << j << std::endl;
		for (int i = 0; i < 3000; ++i)
		{
			//std::cout << i << " " << j << std::endl;
			h += testArray[k] * precalculatedArrays[0][i];
			k++;
		}
	}
	return h;
}

extern "C" __declspec(dllexport) double WINAPI testSpeed2()
{
	int k = 0;
	double h = 0;
	for (int j = 0; j < 10000; ++j)
	{
//		std::cout << "j:" << j << std::endl;
		for (int i = 0; i < 3000; ++i)
		{
			//std::cout << i << " " << j << std::endl;
			h += testArray[k] * cos(double(i));
			k++;
		}
	}
	return h;
}
