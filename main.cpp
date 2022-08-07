// The MIT License (MIT)
//
// Copyright (c) 2015 THINGER LTD
// Author: alvarolb@gmail.com (Alvaro Luis Bustamante)
//
// Permission is hereby granted, free of charge, to any person obtaining a cop
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software i
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.


#include "thinger/thinger.h"
#include <wiringPi.h>
#include <wiringSerial.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <sstream>


#define USER_ID             "Will"
#define DEVICE_ID           "CWM_TP5"
#define DEVICE_CREDENTIAL   "T123TP5a!"

#define LED_PIN 0
#define PAINT_EN_PIN 1

#define RTD_A 3.9083e-3
#define RTD_B -5.775e-7

#define OUR_INPUT_FIFO_NAME "/tmp/my_fifo"
#define OUR_INPUT_FIFO_NAME1 "/tmp/my_fifo1"
#define OUR_INPUT_FIFO_NAME2 "/tmp/my_fifo2"

float        Voltage = 3.14;  
float        Z1,Z2,Z3,Z4,Rt;
float        tempx = 76;
float        tempy;
float        tempx_last = 76;
float        datatemp;
float        phase_a_comm,phase_b_comm,phase_c_comm;
float        avg_current;
float        drive_vibration_abs_comm;

float        drive_vibration_comm;
float        drive_vibration_comm_last
;
float        drive_vibration_peak_comm;

float        vibration_alarm_setpoint = 500;
float        vibration_alarm_resetpoint = 50;

float        current_alarm_setpoint = 3.0;
float        current_alarm_resetpoint = 1.0;

float        temperature_alarm_setpoint = 140;
float        temperature_alarm_resetpoint = 75;

float       variablea;
float       variableb;


bool         current_alarm=0;
bool         temperature_alarm=0;
bool         vibration_alarm=0;
bool         request_null = 0;
bool         reset_null = 0;
bool         request_frc_temp = 0;
bool         request_frc_curr = 0;
bool         request_frc_vib = 0;
bool         request_frc_survey = 0;
bool         paint_enable_local = 0;
bool         paint_enable_local_last = 0;

unsigned int bucket_time_counter = 421;
unsigned int loop_counter;
unsigned int calcval,calcval1;
unsigned int rxbuffer[128];
unsigned int indexx = 0;
unsigned int indexx1 = 0;
unsigned int drv_mon_state = 0;
int          usbserial,retval,in_char;
char         first = 0x01;
unsigned char out_char,zxy;
unsigned char request_reset = 0;
unsigned int  temptst = 0;
unsigned int  startup = 0;

char pipe2_snd[] = "ABCD/n";

using namespace std;

using std::cout; using std::cerr;
using std::endl; using std::string;


int resultzed;
int our_input_fifo_filestream = -1;
int our_input_fifo1_filestream = -1;
int our_input_fifo2_filestream = -1;

unsigned int x13;
unsigned int blc = 0;

//chain_metrics
unsigned int current_link = 0;
unsigned int off_cycles = 0;

unsigned int chain_length_1 = 0;
unsigned int chain_length_2 = 0;
unsigned int chain_length_3 = 0;
unsigned int chain_length_4 = 0;
unsigned int chain_length_5 = 0;
unsigned int chain_speed  = 0;





char               tmps[32] = {"empty\0"}; 
char               tmps1[32] = {"empty\0"}; 
char               tmps2[32] = {"empty\0"}; 
char               tmps3[32] = {"empty\0"}; 
char               tmps4[32] = {"empty\0"};
char               tmps5[32] = {"empty\0"};

char               S_State[32] = {"idle\0"};
char               P_State[32] = {"disabled\0"};

unsigned int number_links = 0; 
unsigned int number_ooc_links = 0;
float        tolerance_threshold = 275.125;




int main(int argc, char *argv[])
{
	//tmps[1] = 'm'; 
	
//***********************************************************************************************************************	
        resultzed = mkfifo(OUR_INPUT_FIFO_NAME, 0666);             //
        if (resultzed == 0)
        {
                //FIFO CREATED
        }

        printf("Process %d opening FIFO %s\n", getpid(), OUR_INPUT_FIFO_NAME);
	our_input_fifo_filestream = open(OUR_INPUT_FIFO_NAME, (O_RDONLY | O_NONBLOCK));
					//Possible flags:
					//	O_RDONLY - Open for reading only.
					//	O_WRONLY - Open for writing only.
					//	O_NDELAY / O_NONBLOCK (same function) - Enables nonblocking mode. When set read requests on the file can return immediately with a failure status
					//											if there is no input immediately available (instead of blocking). Likewise, write requests can also return
					//											immediately with a failure status if the output can't be written immediately.
	if (our_input_fifo_filestream != -1)
		printf("Opened FIFO: %i\n", our_input_fifo_filestream);

//***********************************************************************************************************************
        resultzed = mkfifo(OUR_INPUT_FIFO_NAME1, 0666);             //(This will fail if the fifo already ex$
        if (resultzed == 0)
        {
                //FIFO CREATED
        }

        printf("Process %d opening FIFO1 %s\n", getpid(), OUR_INPUT_FIFO_NAME1);
        our_input_fifo1_filestream = open(OUR_INPUT_FIFO_NAME1, (O_RDONLY |  O_NONBLOCK));
                                        //Possible flags:
                                        //      O_RDONLY - Open for reading only.
                                        //      O_WRONLY - Open for writing only.
                                        //      O_NDELAY / O_NONBLOCK (same function) - Enables nonblocking$
                                        //                                                                 $
                                        //                                                                 $
        if (our_input_fifo1_filestream != -1)
        {
                printf("Opened FIFO1: %i\n", our_input_fifo1_filestream);
        }
//***********************************************************************************************************************
	resultzed = mkfifo(OUR_INPUT_FIFO_NAME2, 0666);             //(This will fail if the fifo already ex$
        if (resultzed == 0)
        {
                //FIFO CREATED
        }

        printf("Process %d opening FIFO2 %s\n", getpid(), OUR_INPUT_FIFO_NAME2);
        our_input_fifo2_filestream = open(OUR_INPUT_FIFO_NAME2, (O_WRONLY |  O_NONBLOCK));
                                        //Possible flags:
                                        //      O_RDONLY - Open for reading only.
                                        //      O_WRONLY - Open for writing only.
                                        //      O_NDELAY / O_NONBLOCK (same function) - Enables nonblocking$
                                        //                                                                 $
                                        //                                                                 $
        if (our_input_fifo2_filestream != -1)
        {
		printf("Opened FIFO2: %i\n", our_input_fifo2_filestream);
        }
          
        temptst = 0;

    	thinger_device thing(USER_ID, DEVICE_ID, DEVICE_CREDENTIAL);

    	wiringPiSetup();
    	pinMode(LED_PIN, OUTPUT);
    	digitalWrite(LED_PIN, LOW);
	pinMode(PAINT_EN_PIN, OUTPUT);
        digitalWrite(PAINT_EN_PIN, LOW);	
	
	printf("before usbserial open\n");
        usbserial = ( serialOpen("/dev/ttyUSB_FTDI_RS485",19200));
        //usbserial = ( serialOpen("/dev/ttyUSB4",19200));
	printf("after usbserial open\n");
	printf("userserial = %d",usbserial);


         thing["chain_curr_link"] >> [](pson &out){ 
         out["current_link"] = current_link;  
	 out["off_cycles"] = off_cycles; 
         }; 


       


         thing["chain_metrics"] >> [](pson &out){ 
         out["chain_length_1"] = chain_length_1;
         out["chain_length_2"] = chain_length_2;
	 out["chain_length_3"] = chain_length_3;
	 out["chain_length_4"] = chain_length_4;
	 out["chain_length_5"] = chain_length_5;
         out["chain_speed"] = chain_speed;
         }; 
	 
	 
	 

	 
         thing["time_stamps"] >> [](pson &out){ 
	 out["time_stamp_0"] = (const char*) tmps;         	 
         out["time_stamp_1"] = (const char*) tmps1; 
         out["time_stamp_2"] = (const char*) tmps2; 
	 out["time_stamp_3"] = (const char*) tmps3; 
	 out["time_stamp_4"] = (const char*) tmps4; 
	 out["time_stamp_5"] = (const char*) tmps5; 
         }; 	 


         thing["survey_results"] >> [](pson &out){ 
         out["number_links"] = number_links;  
         out["number_ooc_links"] = number_ooc_links;
         out["tolerance_threshold"] = tolerance_threshold;
        // out["time_stamp"] = time_stamp;
         }; 


         thing["survey_metrics"] >> [](pson &out){ 
         out["S_State"] = (const char*) S_State;  
         }; 
	 
         thing["paint_metrics"] >> [](pson &out){ 
         out["P_State"] = (const char*) P_State;  
         };

	 thing["tmp"] >> [](pson &out){ 
         out["test1"] = tempx;   // tempx;
	 out["test2"] = phase_a_comm;
	 out["test3"] = phase_b_comm;
	 out["test4"] = phase_c_comm;
         out["test5"] = drive_vibration_comm;
         out["test6"] = drive_vibration_peak_comm;
         }; 
 
	thing["reset_peak"] << [](pson& in){
    		if(in.is_empty()){
        		// in = (bool) digitalRead(LED_PIN);
    		}
    		else{
                        request_reset=in;
    		}
	};
	
	
	thing["frc_survey"] << [](pson& in){
		
                if(in.is_empty()){
                        in = (bool) request_frc_survey;
                }
                else{   
			request_frc_survey = in;
                        if (request_frc_survey)
			{
				digitalWrite(LED_PIN, in ? HIGH : LOW);
			}
                }
        };

	thing["paint_enable"] << [](pson& in){
		
                if(in.is_empty()){
                        in = (bool) paint_enable_local_last;
                }
                else{
                        paint_enable_local = in;
			if((paint_enable_local_last == 0)&&(paint_enable_local==1))
			{
				if (digitalRead(PAINT_EN_PIN))
				{
					digitalWrite(PAINT_EN_PIN, LOW);
				}
				else
                                {
                                        digitalWrite(PAINT_EN_PIN, HIGH);
                                }
			}
                        paint_enable_local_last  = paint_enable_local;
                }
        };
	
	
	thing["frc_reset_temp_alarm"] << [](pson& in){
		
		temperature_alarm = 0;
                if(in.is_empty()){
                        in = (bool) request_frc_temp;
                }
                else{
                        request_frc_temp = in;
                }
        };
	
	
	thing["frc_reset_current_alarm"] << [](pson& in){
		
		current_alarm = 0;
                if(in.is_empty()){
                        in = (bool) request_frc_curr;
                }
                else{
                        request_frc_curr = in;
                }
        };		

	thing["frc_reset_vib_alarm"] << [](pson& in){
		
		vibration_alarm = 0;
                if(in.is_empty()){
                        in = (bool) request_frc_vib;
                }
                else{
                        request_frc_vib = in;
                }
        };
	
	
        thing["set_current_nulls"] << [](pson& in){
		
		temperature_alarm = 0;
                if(in.is_empty()){
                        in = (bool) request_null;
                }
                else{
                        request_null = in;
                }
        };

        thing["reset_current_nulls"] << [](pson& in){
                if(in.is_empty()){
                        in = (bool) reset_null;
                }
                else{
                        reset_null = in;
                }
        };


        thing["tmpset"] << [](pson& in){
                if(in.is_empty()){
                        in = (float)temperature_alarm_setpoint;
                }
                else{
                        temperature_alarm_setpoint = in;
                }
        };


        thing["tmpreset"] << [](pson& in){
                if(in.is_empty()){
                        in = (float)temperature_alarm_resetpoint;
                }
                else{
                        temperature_alarm_resetpoint = in;
                }
        };

        thing["currset"] << [](pson& in){
                if(in.is_empty()){
                        in = (float)current_alarm_setpoint;
                }
                else{
                        current_alarm_setpoint  = in;
                }
        };


        thing["currreset"] << [](pson& in){
                if(in.is_empty()){
                        in = (float)current_alarm_resetpoint;
                }
                else{
                        current_alarm_resetpoint  = in;
                }
        };
        thing["vibset"] << [](pson& in){
                if(in.is_empty()){
                        in = (float)vibration_alarm_setpoint;
                }
                else{
                        vibration_alarm_setpoint  = in;
                }
        };


        thing["vibreset"] << [](pson& in){
                if(in.is_empty()){
                        in = (float)vibration_alarm_resetpoint;
                }
                else{
                       vibration_alarm_resetpoint  = in;
                }
        };



        thing["alarm_rd_bck"] >> [](pson &out){ 
        out["temperature_setpoint"]   = (float)temperature_alarm_setpoint;
        out["temperature_resetpoint"] = (float)temperature_alarm_resetpoint;
        out["current_setpoint"]       = (float)current_alarm_setpoint;
        out["current_resetpoint"]     = (float)current_alarm_resetpoint;
        out["vibration_setpoint"]     = (float)vibration_alarm_setpoint;
        out["vibration_resetpoint"]   = (float)vibration_alarm_resetpoint;
        };

        thing["alarm_state"] >> [](pson &out){ 
        out["current_alarmx"]   = (bool)current_alarm;
        out["temp_alarmx"]      = (bool)temperature_alarm;
        out["vibration_alarmx"] = (bool)vibration_alarm;

        };
	



//         thing["alarm_setpoints"] <<  [](pson& in){ 
//         in["vibset"]   = vibration_alarm_setpoint;
//         in["vibreset"] = vibration_alarm_resetpoint;
//         in["currset"]  = current_alarm_setpoint;
//         in["currreset"]= current_alarm_resetpoint;
//           temperature_alarm_setpoint = in["tmpset"];
//         in["tmpreset"] = temperature_alarm_resetpoint;
//         }; 




//      drv_mon_state = 0      rxing temperature packet          123456 /n/d    ( 0x20,0x0a,0x0d )
//                             txing "2"                         requesting avg current packet
//
//      drv_mon_state = 1      rxing avg current packet          123456 123456 123456 /n/d    ( 0x20,0x0a,0x0d )
//                             txing "4"                         requesting vibration metrics packet
//
//      drv_mon_state = 2      rxingvibration metrics packet     123456 123456 123456 /n/d    ( 0x20,0x0a,0x0d )  
//                             txing "5"                         requesting vibration peak reset ( if set )
//
//      drv_mon_state = 3      rxingvibration OK from peak reset OK /n/d    ( 0x20,0x0a,0x0d )   
//                             txing "3"                        requesting temperature packet
//





	while(1==1)    // this "main_loop seemd to occur about once / second
	{
		//printf("the big loop %d\n",blc);
		//blc++;
		
		thing.handle();
		if ((off_cycles==0)||(off_cycles==99999)||(off_cycles==777777))
		{
			S_State[0] = 'i';
                        S_State[1] = 'n';
                        S_State[2] = ' ';
                        S_State[3] = 'p';
			S_State[4] = 'r';
                        S_State[5] = 'o';
                        S_State[6] = 'g';
                        S_State[7] = 'r';
			S_State[8] = 'e';
                        S_State[9] = 's';
                        S_State[10] = 's';
                        S_State[11] = 0x00;
		}
		else
		{
		
                	if (digitalRead(LED_PIN)==0)
			{
				S_State[0] = 'I';
				S_State[1] = 'd';
				S_State[2] = 'l';
				S_State[3] = 'e';
				S_State[4] = 0x00;
			}
                	else
			{
				S_State[0] = 'a';
				S_State[1] = 'r';
				S_State[2] = 'm';
				S_State[3] = 'e';
				S_State[4] = 'd';			
				S_State[5] = 0x00;
			}
		}
	
                if (digitalRead(PAINT_EN_PIN)==0)            
                {
                        P_State[0] = 'd';
                        P_State[1] = 'i';
                        P_State[2] = 's';
                        P_State[3] = 'a';
                        P_State[4] = 'b';
                        P_State[5] = 'l';
                        P_State[6] = 'e';
                        P_State[7] = 'd';
                        P_State[8] = 0x00;
                }
                else
                {
                        P_State[0] = 'e';
                        P_State[1] = 'n';
                        P_State[2] = 'a';
                        P_State[3] = 'b';
                        P_State[4] = 'l';
                        P_State[5] = 'e';
                        P_State[6] = 'd';
                        P_State[7] = 0x00;
                }

		if ((our_input_fifo1_filestream != -1)&&(1))
                {
                        char rx_buffer1[256];
                        unsigned int    zed1;
			//printf("got something on fifo1");

                        int rx_length1 = read(our_input_fifo1_filestream, (void*)rx_buffer1, 255);         //F$
                        if (rx_length1 < 0)
                        {
                                //An error occured (this can happen)
                                //printf("FIFO Read error\n");
                        }
                        else if (rx_length1 == 0)
                        {
                                //No data waiting
                        }
                        else
                        { 

				for (zxy=0; zxy<20; zxy++)
				{
					tmps5[zxy] = tmps4[zxy];
				}
				
				
				for (zxy=0; zxy<20; zxy++)
				{
					tmps4[zxy] = tmps3[zxy];
				}
				
				
				for (zxy=0; zxy<20; zxy++)
				{
					tmps3[zxy] = tmps2[zxy];
				}
				
				
				for (zxy=0; zxy<20; zxy++)
				{
					tmps2[zxy] = tmps1[zxy];
				}
				
				
				for (zxy=0; zxy<20; zxy++)
				{
					tmps1[zxy] = tmps[zxy];
				}
				
																				
				printf("rx_length1: %d\n", rx_length1);								
				printf("rx_buffer1: %s\n", rx_buffer1);
				
				rx_buffer1[21] = 0;
				
				//strcpy(rx_buffer1, tmps);
				
				for (zxy=2; zxy<22; zxy++)
				{
					tmps[zxy-2] = rx_buffer1[zxy];
				}
				
			
				thing.stream("time_stamps");

                        }
		}

		//thing.handle();

		if ((our_input_fifo_filestream != -1)&&(1))
		{
			unsigned char rx_buffer[256];
                        unsigned int 	zed;
                       
			//printf("got something on fifo");
			int rx_length = read(our_input_fifo_filestream, (void*)rx_buffer, 255);		//Filestream, buffer to store in, number of bytes to read (max)
			if (rx_length < 0)
			{
				//An error occured (this can happen)
				//printf("FIFO Read error\n");
			}
			else if (rx_length == 0)
			{
				//No data waiting
			}
			else
			{ 
				//Bytes received
                                rx_buffer[rx_length] = '\0';
                                
                                while (rx_length)
                                {
					printf("FIFO %i bytes read : %s\n", rx_length, rx_buffer);
                                	x13 = (rx_buffer[2] & 0x0f)  * 100000;
					x13 += (rx_buffer[3] & 0x0f) * 10000;
					x13 += (rx_buffer[4] & 0x0f) * 1000;
					x13 += (rx_buffer[5] & 0x0f) * 100;
					x13 += (rx_buffer[6] & 0x0f) * 10;
					x13 +=  rx_buffer[7] & 0x0f;
    					//printf("The value of x13 : %d\n", x13);

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'a'))
                                	{ 
                                 	current_link = x13;
                                        thing.stream("chain_curr_link");
                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'b'))
                                	{ 
                                        chain_length_1 = x13;
					thing.stream("chain_metrics");

                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'c'))
                                	{ 
                                        chain_length_2 = x13;
                                        thing.stream("chain_metrics");

                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'd'))
                                	{ 
                                        chain_length_3 = x13;
                                        thing.stream("chain_metrics");

                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'e'))
                                	{ 
                                        chain_length_4 = x13;
                                        thing.stream("chain_metrics");

                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'f'))
                                	{ 
                                        chain_length_5  = x13;
                                        thing.stream("chain_metrics");

                                	}


                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'g'))
                                	{ 
                                        off_cycles = x13;
                                        //thing.stream("chain_metrics");
                                	}




  					if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'm'))
                                	{ 
                                        number_links = x13;
                                        thing.stream("survey_results");
                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'n'))
                                	{ 
                                        number_ooc_links = x13;
                                        thing.stream("survey_results");
                                	}

                                	if ((rx_buffer[0] == '*')&&(rx_buffer[1] == 'o'))
                                	{ 
                                        tolerance_threshold  = x13;
                                        thing.stream("survey_results");
                                	}
                                        if (rx_length > 7)
                                        {
                                                for (zed=0; zed < (rx_length-8); zed++)
						{
                                                	rx_buffer[zed] = rx_buffer[zed+8];
						}
						rx_length = rx_length - 8;
					}
					else
					{
						rx_length = 0;
					}
 				}


			}
		}




		//thing.handle();           
		printf("userserial = %d\n",usbserial);
		
		if(usbserial != -1)
		{		
			indexx = 0;	 		
			switch(drv_mon_state) 
			{	 
					case 0:    //  rx temperature      xxx.xx  lf

							rxbuffer[0] = 0x00;	                                                        printf(" %d ",rxbuffer[0]);
                                                        rxbuffer[1] = 0x00;
                                                        rxbuffer[2] = 0x00;
                                                        rxbuffer[3] = 0x00;
                                                        rxbuffer[4] = 0x00;
							rxbuffer[5] = 0x00;
							rxbuffer[6] = 0x00;
							while (serialDataAvail(usbserial) )
							{
							  in_char = serialGetchar (usbserial) ;
							  rxbuffer[indexx] = in_char;
							  if (in_char == 0x0a) break;
							  if (indexx  < 10) indexx++;
							} 


							if ((rxbuffer[indexx-3] == 0x2e)&&(indexx==6))
							{
								  calcval =  (rxbuffer[(indexx -6)] & 0x0f)*10000;
								  calcval += (rxbuffer[indexx -5] & 0x0f)*1000;
								  calcval += (rxbuffer[indexx -4] & 0x0f)*100;
								  calcval += (rxbuffer[indexx -2] & 0x0f)*10;
								  calcval += (rxbuffer[indexx -1] & 0x0f);
								  tempx = calcval;
								  tempx = tempx/100;


								  // convert to F for now 
								  tempx *= 1.8;
								  tempx += 32;
								  printf("%f deg f\n",tempx);
								  if ((tempx < 30) || (tempx > 180))
								  {
									   tempx = tempx_last;
								  }
								  else
								  {
									  tempx_last = tempx;
								  }
								  
								  if ((tempx > temperature_alarm_setpoint)&&(temperature_alarm == 0))
								  {
									temperature_alarm = 1;
									tempy = tempx;
									pson datatemp = tempy;
									thing.call_endpoint("TP5_overtemp_email", datatemp); 
								  }


								  if ((tempx <  temperature_alarm_resetpoint)&&(temperature_alarm == 1))
								  {
									temperature_alarm = 0;
								  }

							}
							serialFlush (usbserial);
							serialPutchar(usbserial, '2') ;  //  '2' request current avgs
							printf("sending a 2 \n");
							drv_mon_state = 2;               //   1

					break;
				
					case 1:     //  rx current avgs
							
							
							while (serialDataAvail(usbserial) )
							{
								in_char = serialGetchar (usbserial) ;
								rxbuffer[indexx] = in_char;
								if (in_char == 0x0a) break;
								if (indexx  < 10) indexx++;
							}

                                                        //printf(" %d ",rxbuffer[0]);
                                                        //printf(" %d ",rxbuffer[1]);
                                                        //printf(" %d ",rxbuffer[2]);
                                                        //printf(" %d ",rxbuffer[3]);
                                                        //printf(" %d ",rxbuffer[4]);
                                                        //printf(" %d \n",rxbuffer[5]);
							
							
							
							if ((rxbuffer[indexx-3] == 0x2e)&&(indexx==5))
							{
								calcval = (rxbuffer[indexx -5] & 0x0f)*1000;
								calcval += (rxbuffer[indexx -4] & 0x0f)*100;
								calcval += (rxbuffer[indexx -2] & 0x0f)*10;
								calcval += (rxbuffer[indexx -1] & 0x0f);
								
								phase_c_comm = calcval;
								phase_c_comm = phase_c_comm/100;
								
								avg_current = phase_a_comm = phase_b_comm = phase_c_comm;
								if (avg_current > 25) avg_current = 0;

								if ((avg_current > current_alarm_setpoint)&&(current_alarm == 0))
								{
									current_alarm = 1;
									tempy = avg_current;
									pson datacurr = tempy;
									thing.call_endpoint("OverCurrentEmail", datacurr); 
								}


								if ((avg_current <  current_alarm_resetpoint)&&(current_alarm == 1))
								{
								      current_alarm = 0;
								}
							      

							}
							serialFlush (usbserial);
							serialPutchar(usbserial, '3');
							printf("sending a 3\n");   
							drv_mon_state = 3;                

					break;		
					case 2:
							drv_mon_state = 1;
					break;
					case 3:
							drv_mon_state = 0;
                                        break;
							
			
				
				default :
				break;
			}
	 				
		}

	}
    	return 0;
}

