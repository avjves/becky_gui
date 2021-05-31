for f in $(find . -type f);
do
    sed -i 's/"\/api\//"http:\/\/localhost:6701\/api\//g' $f
done
