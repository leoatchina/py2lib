python py2so.py -l ~/anaconda3/include/python3.6m -d ~/Downloads/Gastroscope/Server -o ~/Server -m ManageServer.py -D ui,proto
python py2so.py -l ~/anaconda3/include/python3.6m -d ~/Downloads/Gastroscope/Client -o ~/Client -m ManageClient.py -D ui,proto
rm -rf ~/Gastroscope/Client
rm -rf ~/Gastroscope/Server
mv ~/Client ~/Gastroscope
mv ~/Server ~/Gastroscope
