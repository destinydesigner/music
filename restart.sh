source activate
pid=`ps -ef | grep 'python main.py hackathon' | grep -v 'grep' | awk '{print $2}'`
kill $pid

python main.py hackathon &
