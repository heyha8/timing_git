//trig task

//#include "stm32f1xx_hal.h"
#include "trig.h"
#include "string.h"

#define X86_RX_LEN    21
#define IMU_RX_LEN    12

extern UART_HandleTypeDef huart1;
extern UART_HandleTypeDef huart2;
extern UART_HandleTypeDef huart3;
extern UART_HandleTypeDef huart4;
extern UART_HandleTypeDef huart6;


static int ppsSet = 0;
static int camTrigSet = 0;
static int ppsToX86Set = 0;
static int imudata_freq = 0;
static int camflag = 0;

static int systickByKhzClk = 0;

uint8_t x86_rx_buffer[X86_RX_LEN];
uint8_t imu_rx_buffer[IMU_RX_LEN];
uint8_t x86_rx_byte;
uint8_t imu_rx_byte;
uint8_t ssStartFrame[X86_RX_LEN] = "#ss:start************";
uint8_t ssStopFrame[X86_RX_LEN] = "#ss:stop*************";
uint8_t ssStartCamera[X86_RX_LEN] = "#ss:camstart*********";
uint8_t ssStopCamera[X86_RX_LEN] = "#ss:camstop**********";
uint8_t stFrme[4] = "#st:";
//setting date and time: '#st:240224151955.00**' 0204-feb-22th, 15:19:55s
//start pps and counting:'#ss:start************'
//stop  pps and counting:'#ss:stop*************'

uint8_t year = 24;
uint8_t month = 02;
uint8_t day = 24;
uint8_t hour = 00;
uint8_t minute = 00;
uint32_t sec_x1000 = 00000;


uint32_t imuTimeStamp = 0;

unsigned char gprmc_frame[68]        = "$GPRMC,111109.00,A,6018.29807,N,18103.66588,E,0.058,,240224,,,A*7x";//plus 0x0d 0x0a
unsigned char gprmc_frame_con[68]        = "$GPRMC,111109.00,A,6018.29807,N,18103.66588,E,0.058,,240224,,,A*7x";//plus 0x0d 0x0a
unsigned char timeStamp2x86_frame[41]= "$MCU_T,111109.00,240224,123456.123,A*7x";//plus 0x0d 0x0a
uint8_t hex2char[16] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
uint8_t ppsEnable = 0;
uint8_t receivedFromX86 = 0;
uint8_t receivedFromIMU = 0;

extern ParseUnion   rxdata_union;
unsigned char imu_data[50] = "";
static uint8_t RxBuffer=0;  //串口接收缓存
uint8_t ReceiveFlag=0;//解析成功标志位 1解析成功 0未解析成功

//
// uint8_t cmd[34]={0x55,0xaa,0x03,0x00,0x18,0x00,0x00,0x00,0xbe,0x42,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xc6,0x88,0x48,0x82};
uint8_t cmd[34]={0x55,0xaa,0x03,0x00,0x18,0x00,0x00,0x00,0x80,0x3f,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x52,0xd8,0x8e,0xe8};


uint8_t ascii2dec(char x)
{
	return x-48;
}
char dec2ascii(uint8_t x)
{
	return x+48;
}


uint8_t reorderX86RxBuffer(void)
{
  uint8_t sharpPos = 0;
  uint8_t inn[X86_RX_LEN];
  uint8_t i;
  for(i=0;i<X86_RX_LEN;++i)
  {
	  if(x86_rx_buffer[i] == '#')
	  {
		  if(i==0)
		  {
			  return 1;
		  }
		  else
		  {
			  sharpPos = i;
			  for(i = sharpPos;i<X86_RX_LEN;++i)
			  {
				  inn[i-sharpPos] = x86_rx_buffer[i];
			  }
			  for(i = 0;i<sharpPos;++i)
			  {
				  inn[X86_RX_LEN-sharpPos+i] = x86_rx_buffer[i];
			  }
			  memcpy(x86_rx_buffer,inn,X86_RX_LEN);
			  return 1;
		  }
	  }
  }
  return 0;
}

void sysStop(void)
{
	kHz_CLK_DIS();
	LED_YELLOW_ON();
	ppsEnable = 0;
}

void sysRun(void)
{
	kHz_CLK_EN();
	LED_YELLOW_OFF();
	ppsEnable = 1;
}

void sysCameraStop(void)
{
	camflag = 0;
}

void sysCameraRun(void)
{
	camflag = 1;
}

void foreverLoop(void)
{

  HAL_Delay(150);
  LED_RED_OFF();
  LED_YELLOW_OFF();
  LED_GREEN_OFF();
  PPS_RESET();
//  HAL_UART_Transmit_IT(&huart6, timeStamp2x86_frame, sizeof(timeStamp2x86_frame)); //to x86
//  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  HAL_UART_Receive_IT(&huart2, &RxBuffer, 1);/* 使能串口2接收中断 */
  HAL_UART_Transmit(&huart2, (uint8_t *)&cmd, sizeof(cmd), 0xffff);//开启数据流模式
 // SendCommands();
  sysStop();


  /* Infinite loop */
  for(;;)
  {

//	  if(HAL_UART_GetState(&huart4) == HAL_UART_STATE_READY)
//	  {
//		  HAL_UART_Receive_IT(&huart4, &imu_rx_byte, 1);//start receive from imu
//		  LED_YELLOW_ON();
//	  }
	  if(HAL_UART_GetState(&huart6) == HAL_UART_STATE_READY)
	  {
		  HAL_UART_Receive_IT(&huart6, &x86_rx_byte, 1);//start receive from PC
	  }


//	  LED_GREEN_ON();
//	  osDelay(200);
	  LED_GREEN_OFF();
//	  osDelay(800);
    if (ppsSet || ppsToX86Set || camTrigSet || imudata_freq)
    {

    	//prepare PPS Frame, but wait PPS pulse finish then send frame
    	if((ppsSet||ppsToX86Set) && ppsEnable)
    	{
    		gprmc_frame[sizeof(gprmc_frame)-1] = timeStamp2x86_frame[sizeof(timeStamp2x86_frame)-1] = 0x0A;
    		gprmc_frame[sizeof(gprmc_frame)-2] = timeStamp2x86_frame[sizeof(timeStamp2x86_frame)-2] = 0x0D;

    		gprmc_frame[7] = timeStamp2x86_frame[7] = dec2ascii(hour/10);
    		gprmc_frame[8] = timeStamp2x86_frame[8] = dec2ascii(hour%10);
    		gprmc_frame[9] = timeStamp2x86_frame[9] = dec2ascii(minute/10);
    		gprmc_frame[10] = timeStamp2x86_frame[10] = dec2ascii(minute%10);
    		gprmc_frame[11] = timeStamp2x86_frame[11] = dec2ascii(sec_x1000/10000);
    		gprmc_frame[12] = timeStamp2x86_frame[12] = dec2ascii((sec_x1000%10000)/1000);
    		gprmc_frame[14] = timeStamp2x86_frame[14] = dec2ascii((sec_x1000%1000)/100);
    		gprmc_frame[15] = timeStamp2x86_frame[15] = dec2ascii((sec_x1000%100)/10);

    		gprmc_frame[53] = timeStamp2x86_frame[17] = dec2ascii(year/10);
    		gprmc_frame[54] = timeStamp2x86_frame[18] = dec2ascii(year%10);
    		gprmc_frame[55] = timeStamp2x86_frame[19] = dec2ascii(month/10);
    		gprmc_frame[56] = timeStamp2x86_frame[20] = dec2ascii(month%10);
    		gprmc_frame[57] = timeStamp2x86_frame[21] = dec2ascii(day/10);
    		gprmc_frame[58] = timeStamp2x86_frame[22] = dec2ascii(day%10);

    		uint32_t imuTimeStampSec = (imuTimeStamp<<1) / 1000;
    		if(receivedFromIMU)
    		{
    			receivedFromIMU = 0;
    			timeStamp2x86_frame[24] = dec2ascii( imuTimeStampSec/100000);
    			timeStamp2x86_frame[25] = dec2ascii((imuTimeStampSec%100000)/10000);
    			timeStamp2x86_frame[26] = dec2ascii((imuTimeStampSec%10000)/1000);
    			timeStamp2x86_frame[27] = dec2ascii((imuTimeStampSec%1000)/100);
    			timeStamp2x86_frame[28] = dec2ascii((imuTimeStampSec%100)/10);
    			timeStamp2x86_frame[29] = dec2ascii((imuTimeStampSec%10));
    			timeStamp2x86_frame[31] = dec2ascii(((imuTimeStamp<<1)%1000)/100);
    			timeStamp2x86_frame[32] = dec2ascii(((imuTimeStamp<<1)%100)/10);
    			timeStamp2x86_frame[33] = dec2ascii(((imuTimeStamp<<1)%10));
    		}
    		else
    		{
    			timeStamp2x86_frame[24] = 48;
    			timeStamp2x86_frame[25] = 48;
    			timeStamp2x86_frame[26] = 48;
    			timeStamp2x86_frame[27] = 48;
    			timeStamp2x86_frame[28] = 48;
    			timeStamp2x86_frame[29] = 48;
    			timeStamp2x86_frame[31] = 48;
    			timeStamp2x86_frame[32] = 48;
    			timeStamp2x86_frame[33] = 48;
    		}


    		uint8_t checkSum = 0;
    		for(uint8_t i=1;i<sizeof(gprmc_frame)-5;++i)
    		{
    			checkSum ^= gprmc_frame[i];
    		}
    		gprmc_frame[sizeof(gprmc_frame)-4] = hex2char[checkSum>>4];
    		gprmc_frame[sizeof(gprmc_frame)-3] = hex2char[checkSum&0x0f];

    		checkSum = 0;
    		for(uint8_t i=1;i<sizeof(timeStamp2x86_frame)-5;++i)
    		{
    			checkSum ^= timeStamp2x86_frame[i];
    		}
    		timeStamp2x86_frame[sizeof(timeStamp2x86_frame)-4] = hex2char[checkSum>>4];
    		timeStamp2x86_frame[sizeof(timeStamp2x86_frame)-3] = hex2char[checkSum&0x0f];
    	}

    	//finish pps pulse
    	HAL_Delay(10);
    	LED_YELLOW_OFF();
    	PPS_RESET();
    	//PPS_TO_X86_RESET();
    	CAM_TRIG_RESET();

    	//send
    	if((ppsSet||ppsToX86Set||imudata_freq) && ppsEnable)
    	{

    		if(ppsToX86Set)//10Hz
    		{
    			//HAL_UART_Transmit_IT(&huart6, timeStamp2x86_frame, sizeof(timeStamp2x86_frame)); //to x86
//    			memcpy(imu_data, rxdata_union.payload, 60);
//    			HAL_UART_Transmit_IT(&huart6, imu_data, sizeof(imu_data));
    			HAL_UART_Transmit_IT(&huart3, gprmc_frame, sizeof(gprmc_frame));
    		}
    		if(ppsSet)//1Hz
    		{	HAL_UART_Transmit_IT(&huart1, gprmc_frame, sizeof(gprmc_frame)); // to lidar

    			//HAL_UART_Transmit_IT(&huart6, timeStamp2x86_frame, sizeof(timeStamp2x86_frame)); //to x86
    		}
    		if(imudata_freq)//50Hz
			{
				memcpy(imu_data, rxdata_union.payload, 50);
				HAL_UART_Transmit_IT(&huart6, imu_data, sizeof(imu_data));
			}
    			//HAL_UART_Transmit_IT(&huart6, gprmc_frame, sizeof(gprmc_frame));
    	}

    	ppsSet = 0;
    	ppsToX86Set = 0;
    	camTrigSet = 0;
    	imudata_freq = 0;

    }

    if(receivedFromX86)
    {
    	receivedFromX86 = 0;
    	if(reorderX86RxBuffer())
    	{
    		//setting date and time: '#st:240224151955.00**' 0204-feb-22th, 15:19:55s
    		//start pps and counting:'#ss:start************'
    		//stop  pps and counting:'#ss:stop*************'
    		//start camera and counting:'#ss:camstart************'
    		//stop  camera and counting:'#ss:camstop*************'
    		if(memcmp(x86_rx_buffer,ssStartFrame,8) == 0)
    		{
    			sysRun();
    		}
    		else if(memcmp(x86_rx_buffer,ssStopFrame,8) == 0)
    		{
    			sysStop();
    		}
    		else if(memcmp(x86_rx_buffer,ssStopCamera,11) == 0)
			{
				sysCameraStop();
			}
    		else if(memcmp(x86_rx_buffer,ssStartCamera,11) == 0)
			{
				sysCameraRun();
			}
    		else if(memcmp(x86_rx_buffer,stFrme,4) == 0)
    		{
    			year = ascii2dec(x86_rx_buffer[4])*10+ascii2dec(x86_rx_buffer[5]);
    			month = ascii2dec(x86_rx_buffer[6])*10+ascii2dec(x86_rx_buffer[7]);
    			day = ascii2dec(x86_rx_buffer[8])*10+ascii2dec(x86_rx_buffer[9]);
    			hour = ascii2dec(x86_rx_buffer[10])*10+ascii2dec(x86_rx_buffer[11]);
    			minute = ascii2dec(x86_rx_buffer[12])*10+ascii2dec(x86_rx_buffer[13]);
    			sec_x1000 = ascii2dec(x86_rx_buffer[14])*10000+ascii2dec(x86_rx_buffer[15])*1000;
    			sec_x1000 += ascii2dec(x86_rx_buffer[17])*100+ascii2dec(x86_rx_buffer[18])*10;
    		}


    	}

    }

//    if(receivedFromIMU)
//    {
//    	receivedFromIMU = 0;
//
//    	if(imu_rx_buffer[0] == 0x3A)
//    	{
//    	    imuTimeStamp = (((uint32_t)imu_rx_buffer[10])<<24) + (((uint32_t)imu_rx_buffer[9])<<16) + (((uint32_t)imu_rx_buffer[8])<<8) + imu_rx_buffer[7];
//
//    	}
//
//    }


  }

}


void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	if(GPIO_Pin != GPIO_PIN_7)
	{
		return;
	}
	//add time
	sec_x1000 += 1;
	if(sec_x1000 >= 60000)
	{
		sec_x1000 = 0;
		minute ++;
		if(minute >= 60)
		{
			minute = 0;
			hour ++;
			if(hour >= 24)
			{
				hour = 0;
				day ++;
				if(month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
				{
					if(day >= 32)
					{
						day = 1;
						month ++;
					}
				}
				else if(month == 4 || month == 6 || month == 9 || month == 11)
				{
					if(day >= 31)
					{
						day = 1;
						month ++;
					}
				}
				else
				{
					if(year%4 == 0)
					{
						if(day >= 30)
						{
							day = 1;
							month ++;
						}
					}
					else
					{
						if(day >= 29)
						{
							day = 1;
							month ++;
						}
					}
				}
				if(month >= 13)
				{
					month = 1;
					year ++;
				}
			}
		}
	}

   	systickByKhzClk ++;

   	if (sec_x1000 % 1000 == 0) // 1Hz
   	    {
   	    		PPS_SET();
   	    		//PPS_TO_X86_SET();
   	    		ppsToX86Set = 1;
   	    		ppsSet = 1;
   	    		imudata_freq = 1;
   	    		if (camflag == 1)
   	    		{
   	    			CAM_TRIG_SET();
   	    			camTrigSet = 1;
   	    		}
   	    		return;
   	    }
   	    if (sec_x1000 % 100 == 0) // 10Hz
   	    {
   	    		//PPS_TO_X86_SET();
   	    		ppsToX86Set = 1;
   	    		if (camflag == 1)
   				{
   					CAM_TRIG_SET();
   					camTrigSet = 1;
   				}
				if (sec_x1000 % 20 == 0){
					imudata_freq = 1;
				}
   	    		return;
   	    }
   	     if (sec_x1000 % 20 == 0) // 50Hz
   	 	{
   	     	imudata_freq = 1;
   	 		return;
   	 	}
//    if (sec_x1000 % 1000 == 0) // 1Hz
//    {
//    		PPS_SET();
//    		//PPS_TO_X86_SET();
//    		ppsToX86Set = 1;
//    		ppsSet = 1;
//    		imudata_freq = 1;
//    		if (camflag == 1)
//    		{
//    			CAM_TRIG_SET();
//    			camTrigSet = 1;
//    		}
//    		return;
//    }
//    if (sec_x1000 % 50 == 0) // 10Hz
//    {
//    		//PPS_TO_X86_SET();
//    		ppsToX86Set = 1;
//    		if (camflag == 1)
//			{
//				CAM_TRIG_SET();
//				camTrigSet = 1;
//			}
//    		if (sec_x1000 % 20 == 0){
//    			imudata_freq = 1;
//    		}
//    		return;
//    }
//    if (sec_x1000 % 20 == 0) // 50Hz
//	{
//    	imudata_freq = 1;
//		return;
//	}
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	static uint32_t uart6LastRxTime = 0;
	static uint32_t uart1LastRxTime = 0;
	static uint8_t uart6PenPos = 0;
	static uint8_t uart1PenPos = 0;
	if(huart == &huart6) // receive from x86
	{
		HAL_UART_Receive_IT(&huart6, &x86_rx_byte, 1);//go on receive from PC
		//judge if too long
		if(HAL_GetTick() - uart6LastRxTime > 5)
		{
			uart6PenPos = 0;
		}
		uart6LastRxTime = HAL_GetTick();
		x86_rx_buffer[uart6PenPos] = x86_rx_byte;
		uart6PenPos ++;

		if(uart6PenPos >= sizeof(x86_rx_buffer))
		{
			receivedFromX86 = 1;
			uart6PenPos = 0;
		}
//		LED_YELLOW_ON();
		LED_GREEN_ON();
	}
	else if(huart==&huart2) //判断是否为串口2
	{
	      imu_rx(RxBuffer);//收到串口2数据进行解析
		  while(HAL_UART_Receive_IT(&huart2, &RxBuffer, 1) != HAL_OK);//开启下一次中断

	}
//	else if(huart == &huart3) // receive from imu
//	{
//		HAL_UART_Receive_IT(&huart3, &imu_rx_byte, 1);//go on receive from IMU
//		//judge if too long
//		if(HAL_GetTick() - uart1LastRxTime > 2)
//		{
//			uart1PenPos = 0;
//		}
//		uart1LastRxTime = HAL_GetTick();
//		imu_rx_buffer[uart1PenPos] = imu_rx_byte;
//		uart1PenPos ++;
//
//		if(uart1PenPos == sizeof(imu_rx_buffer))
//		{
//			receivedFromIMU = 1;
//			uart1PenPos --;
//			if(imu_rx_buffer[0] == 0x3A)
//			{
//				imuTimeStamp = (((uint32_t)imu_rx_buffer[10])<<24) + (((uint32_t)imu_rx_buffer[9])<<16) + (((uint32_t)imu_rx_buffer[8])<<8) + imu_rx_buffer[7];
//			}
////			LED_YELLOW_ON();
//		}
////		LED_YELLOW_ON();
//	}
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
	if(HAL_UART_GetError(huart) & HAL_UART_ERROR_ORE)
	{
		__HAL_UART_FLUSH_DRREGISTER(huart);  //读DR寄存器，就可以清除ORE错误标志位
	}
	else
	{
		return;
	}
	if(huart == &huart1) // receive from imu
	{
		HAL_UART_Receive_IT(&huart1, &imu_rx_byte, 1);//go on receive from IMU
	}
	else if(huart == &huart2) // receive from x86
	{
		HAL_UART_Receive_IT(&huart2, &x86_rx_byte, 1);//go on receive from PC
	}
}
