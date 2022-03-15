#!/usr/bin/env bash

largest=0
smallest=10000000
sum=0
counter=0

for folder in $(ls $1); do
   RES=$(for file in $(find "$1/$folder"); do if [ -f "$file" ]; then cat $file; fi; done | wc -l)
   echo $folder: $RES
   if [ $RES -lt $smallest ]; then
      smallest=$RES;
   fi
   if [ $RES -gt $largest ]; then
      largest=$RES;
   fi
   sum=$(($sum + $RES))
   counter=$(($counter+1))
done

echo "==============="
echo "smallest: $smallest"
echo "largest: $largest"
echo "sum: $sum"
echo "avg: $(($sum/$counter))"