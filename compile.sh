if [ $# -gt 0 ]; then
    KEEP="$1"
else
    KEEP="0"
fi

rm -rf ~/Gastroscope/Server
python py2so.py -l ~/anaconda3/include/python3.6m -d ~/Downloads/Gastroscope/Server -o ~/Gastroscope/Server -m ManageServer.py,__init__.py -D ui,proto -k $KEEP 


rm -rf ~/Gastroscope/Client
python py2so.py -l ~/anaconda3/include/python3.6m -d ~/Downloads/Gastroscope/Client -o ~/Gastroscope/Client -m ManageClient.py,__init__.py -D ui,proto -k $KEEP
