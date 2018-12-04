#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/prctl.h>
#include <dirent.h>
#include<string.h>
#define BUF_SIZE 1024
main()
{
    long d = 0;
    long pid = getpid();
    long id =-1;
    DIR  *dir;
    struct dirent *ptr;
    FILE *fp;
    char filepath[150];//大小随意，能装下cmdline文件的路径即可
    char buf[BUF_SIZE];
    char cur_task_name[50];//大小随意，能装下要识别的命令行文本即可
    char cur_task_id[50];//大小随意，能装下要识别的命令行文本即可
    char exe_name[50];//大小随意，能装下要识别的命令行文本即可
    for(;d<2000;d++)
    {
      id = fork(); 
      if(id ==0){
           prctl(PR_SET_PDEATHSIG, SIGHUP);
      }else if(id==-1)
      {
        break;
      }
    }
    if(pid == getpid()){
        for(int i=0;i<15;i++)
        {
           dir = opendir("/proc");
           if (NULL != dir)
           {
             while ((ptr = readdir(dir)) != NULL)
             {
                if ((strcmp(ptr->d_name, ".") == 0) || (strcmp(ptr->d_name, "..") == 0)) continue;
                if (DT_DIR != ptr->d_type) continue; 
           		  sprintf(filepath, "/proc/%s/status", ptr->d_name);//生成要读取的文件的路径
                fp = fopen(filepath, "r");//打开文件
                if (NULL != fp)
                {
                  for(int j=0;j<15;j++)
                  {
                    if( fgets(buf, BUF_SIZE-1, fp)== NULL ){
                        fclose(fp);
                        break;
                     }
                     sscanf(buf, "%s %s %*s", cur_task_name,cur_task_id);
                     if (!strcmp("Name:", cur_task_name) ){
                         //printf("%s  %s\n", cur_task_name,cur_task_id);
                        if (!strcmp("a.out", cur_task_id)){
                            memcpy(exe_name,cur_task_id,(strlen(cur_task_id)+1));
                            continue;
                         }
                     }
                    if (!strcmp("Uid:", cur_task_name)){
                         if( !strcmp("1000", cur_task_id)){
                           //printf("%s  %s\n", cur_task_name,cur_task_id);
                           long k =str2int(ptr->d_name);
                           if(k==pid) continue;
			   if (!strcmp("a.out", exe_name))continue;
                           kill(k,SIGKILL);
                           printf("kill -9 %d run: %d ,for %d ,path %s,filename:%s\n",k,d,i,filepath,exe_name);
                          // memcpy(exe_name,cur_task_name,(strlen(cur_task_name)+1));
                           int id1 = fork(); 
                           if(id1 ==0){
                               prctl(PR_SET_PDEATHSIG, SIGHUP);
                           }else if(id1==-1)
                           {
                               fclose(fp);
                               break;
                           }
                            
                         }
                         fclose(fp);
                         break;
                         }
                  }
               }
             }
           }else{
              printf('can\'t read /proc\n');
              exit(0);
             }
        }
        exit(0);
    }
    sleep(30);
}

int str2int(const char* str)
{
      long temp = 0;
    const char* p = str;
    if(str == NULL) return 0;
    while( *str != 0)
    {
        if( *str < '0' || *str > '9')
        {
            break;
        }
        temp = temp*10 +(*str -'0');
        str ++;
    }
    return temp;
}
