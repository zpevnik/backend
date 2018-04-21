#! /bin/bash

_TIMESTAMP=`date +%Y%m%d-%H%M%S`
_COLLECTIONS=('songs' 'variants' 'users' 'authors' 'interpreters' 'songbooks')

for i in ${_COLLECTIONS[@]}; do
	mongoexport -h localhost:27017 --username={} --password={} --authenticationDatabase={} -d zpevnik -c ${i} -o ~/backup/$_TIMESTAMP-${i}.json
done
