#!/bin/bash

for dir in ${USER}_* ; 
  do 
	  FILE2=$( echo "CMS-HGG_`echo $dir | sed "s/${USER}_//"`_*.root" )
	  FILE=$( echo $FILE2 )
	  [ -f "${FILE}" ] && 
	  	{ echo "file ${FILE} already exist" ; } || 
		{ cp -v  $dir/CMS-HGG.root CMS-HGG_`echo $dir | sed "s/${USER}_//"`_$(date +%Y_%m_%d).root  ; }
  done

###### END ##### 
