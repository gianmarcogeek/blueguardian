/* Usage example of the JETGPIO library
 * Compile with: gcc -Wall -o jetgpio_example jetgpio_example.c -ljetgpio
 * Execute with: sudo ./jetgpio_example
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <jetgpio.h>

int main(int argc, char *argv[])
{
  int Init;

  Init = gpioInitialise();
  if (Init < 0)
    {
      /* jetgpio initialisation failed */
      printf("Jetgpio initialisation failed. Error code:  %d\n", Init);
      exit(Init);
    }
  else
    {
      /* jetgpio initialised okay*/
      printf("Jetgpio initialisation OK. Return code:  %d\n", Init);
    }	

  // Setting up pin 3 as OUTPUT and 7 as INPUT

  int blue = gpioSetMode(31, JET_OUTPUT);
  if (blue < 0)
    {
      /* gpio setting up failed */
      printf("gpio setting up failed. Error code:  %d\n", blue);
      exit(Init);
    }
  else
    {
      /* gpio setting up okay*/
      printf("gpio setting up okay. Return code:  %d\n", blue);
    }

  int red = gpioSetMode(32, JET_OUTPUT);
  if (red < 0)
    {
      /* gpio setting up failed */
      printf("gpio setting up failed. Error code:  %d\n", red);
      exit(Init);
    }
  else
    {
      /* gpio setting up okay*/
      printf("gpio setting up okay. Return code:  %d\n", red);
    }
  while(1)
  {
    gpioWrite(31, 0);
    gpioWrite(32, 0);
	exit(0);
  }
  
  // Terminating library 
  gpioTerminate();

  exit(0);
	
}

