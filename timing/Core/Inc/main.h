/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define LED_R_Pin GPIO_PIN_13
#define LED_R_GPIO_Port GPIOC
#define LED_Y_Pin GPIO_PIN_14
#define LED_Y_GPIO_Port GPIOC
#define LED_G_Pin GPIO_PIN_15
#define LED_G_GPIO_Port GPIOC
#define GEN_1kHz_Pin GPIO_PIN_7
#define GEN_1kHz_GPIO_Port GPIOA
#define GEN_1kHz_EXTI_IRQn EXTI9_5_IRQn
#define ENABLE_1kHz_Pin GPIO_PIN_4
#define ENABLE_1kHz_GPIO_Port GPIOC
#define MID_IO1_Pin GPIO_PIN_13
#define MID_IO1_GPIO_Port GPIOB
#define MID_IO2_Pin GPIO_PIN_14
#define MID_IO2_GPIO_Port GPIOB
#define CAM_Trig2_Pin GPIO_PIN_8
#define CAM_Trig2_GPIO_Port GPIOC
#define CAM_Trig_Pin GPIO_PIN_9
#define CAM_Trig_GPIO_Port GPIOC
#define PPS_Pin GPIO_PIN_8
#define PPS_GPIO_Port GPIOA
#define WCH_CHG0_Pin GPIO_PIN_11
#define WCH_CHG0_GPIO_Port GPIOC
#define WCH_RESET_Pin GPIO_PIN_12
#define WCH_RESET_GPIO_Port GPIOC
#define WCH_RUN_Pin GPIO_PIN_2
#define WCH_RUN_GPIO_Port GPIOD
#define WCH_TCPCS_Pin GPIO_PIN_3
#define WCH_TCPCS_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
