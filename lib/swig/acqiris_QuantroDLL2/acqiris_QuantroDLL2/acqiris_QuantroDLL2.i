/* File : acqiris_QuantroDLL2.i */
%module acqiris_QuantroDLL2

%{
#include "acqiris_QuantroDLL2.h"
%}

/*added by denis*/
%include "std_vector.i"
// Instantiate templates used by DLL
namespace std {
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
}


/*Yippie!!! This typemap converts any incoming variable (that is supposed to be a long integer pointing to some memory location) to a double pointer... */
%typemap (in) double*
{
	$1 = (double *)PyInt_AsLong($input);
}
%typemap (in) unsigned int*
{
	$1 = (unsigned int *)PyInt_AsLong($input);
}
%typemap (in) int*
{
	$1 =  (int *)PyInt_AsLong($input);
}

/* Let's just grab the original header file here */
%include "acqiris_QuantroDLL2.h"
