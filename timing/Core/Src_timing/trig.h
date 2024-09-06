/*
 * trig.h
 *
 *  Created on: Feb 28, 2024
 *      Author: 9d3efbc78886
 */

#ifndef TRIG_H_
#define TRIG_H_


#include "stm32f4xx_hal.h"
#include "../Inc/main.h"
#include "imu.h"
void foreverLoop(void);

#define LED_RED_ON()    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_13,GPIO_PIN_RESET)
#define LED_RED_OFF()    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_13,GPIO_PIN_SET)
#define LED_YELLOW_ON()    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_14,GPIO_PIN_RESET)
#define LED_YELLOW_OFF()    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_14,GPIO_PIN_SET)
#define LED_GREEN_ON()    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_15,GPIO_PIN_RESET)
#define LED_GREEN_OFF()    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_15,GPIO_PIN_SET)

#define PPS_SET()   HAL_GPIO_WritePin(PPS_GPIO_Port,PPS_Pin,GPIO_PIN_SET)
#define PPS_RESET()   HAL_GPIO_WritePin(PPS_GPIO_Port,PPS_Pin,GPIO_PIN_RESET)

//#define PPS_TO_X86_SET()   HAL_GPIO_WritePin(GPIOA,GPIO_PIN_0,GPIO_PIN_SET)
//#define PPS_TO_X86_RESET()   HAL_GPIO_WritePin(GPIOA,GPIO_PIN_0,GPIO_PIN_RESET)

#define CAM_TRIG_SET()   HAL_GPIO_WritePin(CAM_Trig_GPIO_Port,CAM_Trig_Pin,GPIO_PIN_SET)
#define CAM_TRIG_RESET()   HAL_GPIO_WritePin(CAM_Trig_GPIO_Port,CAM_Trig_Pin,GPIO_PIN_RESET)

#define kHz_CLK_EN()   HAL_GPIO_WritePin(ENABLE_1kHz_GPIO_Port,ENABLE_1kHz_Pin,GPIO_PIN_SET)
#define kHz_CLK_DIS()   HAL_GPIO_WritePin(ENABLE_1kHz_GPIO_Port,ENABLE_1kHz_Pin,GPIO_PIN_RESET)

#endif /* TRIG_H_ */
