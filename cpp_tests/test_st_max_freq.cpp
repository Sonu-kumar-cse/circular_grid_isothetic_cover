#include<iostream>
#include<algorithm>
using namespace std;


void construct_St(int st[],int arr[],int low,int high,int curr)
{
    if(low==high)
    {
        st[curr]=arr[low];
        return;
    }
    int mid=(low+high)/2;
    construct_St(st,arr,low,mid,curr*2+1);
    construct_St(st,arr,mid+1,high,curr*2+2);
    st[curr]=st[curr*2+1]+st[curr*2+2];
}


int get_min_index(int st[],int low,int high,int x,int index)
{
    if(st[index]<x) return -1;
    if(low==high) return low;
    int mid=(low+high)/2;

    if(st[index*2+1]>=x)
        return get_min_index(st,low,mid,x,index*2+1);
    return get_min_index(st,mid+1,high,x-st[index*2+1],index*2+2);


}



int main()
{
    int arr[]={15, 22, 8, 45, 11, 60, 33, 71, 99, 10};
    int n=10;
    int sum=0;
    cout<<"prefix sum"<<endl;
    for(int i=0;i<n;i++){
        sum+=arr[i];
        cout<<sum<<" ";
    }
    cout<<endl;

    int st[n*4];

    construct_St(st,arr,0,n-1,0);
    cout<<"for x=1 ans="<<get_min_index(st,0,n-1,1,0)<<endl;
    cout<<"for x=38 ans="<<get_min_index(st,0,n-1,38,0)<<endl;
    cout<<"for x=194 ans="<<get_min_index(st,0,n-1,194,0)<<endl;
    cout<<"for x=372 ans="<<get_min_index(st,0,n-1,372,0)<<endl;


    cout<<"hello"<<endl;
    return 0;
}