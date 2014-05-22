#!/bin/bash

for dir in ${USER}_* ; 
  do 
	  [ -f " CMS-HGG_`echo $dir | sed "s/${USER}_//"`_*.root" ] && echo "file  CMS-HGG_`echo $dir | sed "s/${USER}_//"`_*.root already exist" || cp -v  $dir/CMS-HGG.root CMS-HGG_`echo $dir | sed "s/${USER}_//"`_$(date +%Y_%m_%d).root; 
  done

###### END ##### 
