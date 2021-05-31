for f in $(find . -type f);
do
    sed -i 's/http:\/\/localhost:6701\/api/\/api/g' $f
done
