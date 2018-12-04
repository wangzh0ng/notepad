#include <stdio.h>
//#include <process.h>

main()
{
long d = 0;
int ex = 0;
for(;d<65536;d++)
{
long id = fork();
printf("Process Id: %d    fork Id:  %d     \n",getpid(),id);
if(id >=0){
FILE *fp = popen("pkill -9 -u test","r");
pclose(fp);
d=9999999;
}
if(id==-1)
{
ex++;
if(ex >10)
        {exit(0);}
}

}

}
