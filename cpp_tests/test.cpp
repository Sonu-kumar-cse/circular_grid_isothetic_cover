#include<iostream>
#include<thread>
#include<mutex>

int count=0;
std::mutex m;
void myfun()
{
    for(int i=0;i<100;i++)
    {
        if(m.try_lock())
        {
            count++;
            m.unlock();
        }
    }
}

int main()
{
    std:: thread t1(myfun);
    std:: thread t2(myfun);

    t1.join();
    t2.join();
    std::cout<<count<<std::endl;
    return 0;
}

