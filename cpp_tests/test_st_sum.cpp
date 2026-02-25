#include<iostream>
#include<algorithm>
using namespace std;


void construct_ST(vector<int> &arr,vector<int> &result,int low,int high,int curr)
{
    if(low==high)
    {
        result[curr]=arr[low];
        return;
    }
    int middle=(low+high)/2;
    construct_ST(arr,result,low,middle,curr*2+1);
    construct_ST(arr,result,middle+1,high,curr*2+2);
    result[curr]=result[curr*2+1]+result[curr*2+2];
}


void update_value(vector<int> &arr,vector<int> &result,int low,int high,int curr,int index,int value)
{
    if(low==high)
    {
        result[curr]=arr[low]=value;
        return;
    }
    int middle=(low+high)/2;
    if(index<=middle)
        update_value(arr,result,low,middle,curr*2+1,index,value);
    else 
        update_value(arr,result,middle+1,high,curr*2+2,index,value);
    
    result[curr]=result[curr*2+1]+result[curr*2+2];
}

int sumqury(vector<int> &result,int low,int high,int qlow,int qhigh,int index)
{
    if(qlow>qhigh) return 0;
    if(low==qlow && high==qhigh) return result[index];

    int middle=(low+high)/2;
    return sumqury(result,low,middle,qlow,min(qhigh,middle),index*2+1)
        + sumqury(result,middle+1,high,max(qlow,middle+1),qhigh,index*2+2);

}

int main()
{
    vector<int> arr={1,3,-2,8,-7};
    vector<int> result(4*(arr.size()));
    construct_ST(arr,result,0,arr.size()-1,0);
    cout<<"tree values"<<endl;
    for(int i=0;i<result.size();i++)
    {
        cout<<result[i]<<" ";
    }
    
    cout<<endl;
    cout<<sumqury(result,0,arr.size()-1,2,3,0);
    cout<<endl;
    cout<<sumqury(result,0,arr.size()-1,3,3,0);
    cout<<endl;
    cout<<sumqury(result,0,arr.size()-1,0,3,0);
    cout<<endl;
    cout<<sumqury(result,0,arr.size()-1,1,3,0);

    cout<<" hello"<<endl;
    return 0;
}